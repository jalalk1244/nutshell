# Nutshell

A Django e-commerce portfolio project for a nuts and dried-fruit store. It includes a product catalogue, filters, reviews, wishlists, a session cart, customer profiles, order history and Stripe card payments. This modernization focuses on authorization, correct totals, a verifiable payment lifecycle and regression tests.

![Original responsive design](static/media/am-i-responsive.png)

The storefront uses a warm botanical design with cream backgrounds, forest-green accents, editorial headings and responsive layouts. The S3 storage provider is retained. [Historical design notes, screenshots and credits](docs/legacy-readme.md) are preserved separately; their deployment and testing claims are historical. See the [UI refresh notes](docs/ui-refresh.md) for the latest presentation changes and verification.

## Runtime and local setup

Use Python 3.12 with the latest available security patch. `requirements.txt` pins the resolved dependencies, including Django 5.2.18 LTS, allauth 65.20.1, Stripe SDK 12.5.1, psycopg 3 and Bootstrap 4 crispy templates. Django 5.2 supports Python 3.12 and receives security support until April 2028. The local checks used the installed Python 3.12.3; update its patch version before hosting.

PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DEVELOPMENT = '1'
$env:SECRET_KEY = 'replace-with-a-random-local-secret'
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

With `DEVELOPMENT=1` and no `DATABASE_URL`, local development uses SQLite. PostgreSQL 17 is the verified database for constraints and concurrency. To use your own empty local PostgreSQL database instead:

```powershell
$env:DATABASE_URL = 'postgres://USER:PASSWORD@localhost:5432/nutshell'
python manage.py migrate
```

Create categories and products in Django admin or use the owner product forms. The project does not ship customer data or a seeded production database. Superusers can manage products through storefront forms; ordinary customers and staff without superuser status cannot. Django admin additionally respects its own staff/model permissions.

## Configuration

[.env.example](.env.example) lists variable names and safe placeholders. It is a reference: Django does not automatically load `.env`. Set variables in your shell or deployment environment. A legacy, untracked `env.py` is still supported but should not be committed.

| Variable | Purpose |
| --- | --- |
| `DEVELOPMENT` | Set only for local development; its presence enables DEBUG and local HTTP cookies |
| `SECRET_KEY` | Required random secret outside development |
| `DATABASE_URL` | PostgreSQL connection string; required outside development |
| `ALLOWED_HOSTS` | Comma-separated hostnames; defaults to localhost and 127.0.0.1 |
| `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY` | Test-mode publishable and secret keys for local payments |
| `STRIPE_WH_SECRET` | Signing secret from your local Stripe listener or configured webhook |
| `USE_AWS` | Set to enable the existing S3 backend |
| `AWS_STORAGE_BUCKET_NAME` / `AWS_S3_REGION_NAME` | Your bucket and region; existing region defaults to eu-north-1 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Optional explicit S3 credentials; prefer the SDK credential chain when available |
| `EMAIL_BACKEND` | Defaults to the in-memory backend, which sends no email |

Allauth retains username/email login and mandatory email verification. Local `createsuperuser` supports admin access. To manually exercise signup without sending real mail, explicitly set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` and read the verification link privately in your terminal. Do not publish that output. GET logout shows a confirmation; POST performs logout.

Production requires HTTPS, proxy configuration appropriate to your host and a static-file server or configured S3 storage. Secure session/CSRF cookies are enabled outside development. No public deployment is claimed here. Gunicorn remains the Linux deployment entrypoint from `Procfile`; the Windows development server is local only.

The legacy Gitpod configuration now selects Python 3.12 and no longer starts external telemetry or unrelated databases. Its hosted image build is unverified. Set `ALLOWED_HOSTS` to your workspace preview hostname before using its preview. An old telemetry credential was removed from `.vscode/uptime.sh`; its owner should revoke/rotate it because existing Git history can retain it.

## Money and cart rules

Prices always come from the database. Money uses `Decimal` with two decimal places and round-half-up. USD is the supported currency. Delivery costs $3 below a $25 product subtotal, is free at $25 or above, and is zero for an empty bag. The same rule is used by checkout and stored orders.

Adding requires an integer quantity from 1 to 99, with a maximum of 99 per product. Non-integer, zero, negative and excessive additions return HTTP 400. Decrementing one item to zero removes it. Removal is idempotent and also works for a product that has disappeared from the catalogue. Invalid product references are rejected. Cart, wishlist and delete actions require POST and CSRF tokens.

Checkout records the prices shown when the form loads. If catalogue prices change before submission, payment preparation returns 409 and asks the customer to reload and review the new amount. Saved orders retain unit prices and totals even when catalogue prices change. Products referenced by orders cannot be deleted.

Reviews take their identity from the authenticated user; anonymous submissions redirect to login. The numeric mean is displayed to one decimal place. Filled stars use the exact mean rounded to the nearest integer, with halves rounded upward: 4.5 displays five filled stars. Products without reviews show zero. Multiple reviews by one user remain allowed.

## Stripe test mode

Use only test keys and a Stripe test environment. Never enter real card information during a demonstration. After configuring test keys, forward local events with the Stripe CLI:

```sh
stripe listen --forward-to localhost:8000/checkout/wh/
```

Set `STRIPE_WH_SECRET` to that listener's signing secret and restart Django. Complete an actual Nutshell checkout with a Stripe test card such as `4242 4242 4242 4242`, a future expiry and any test CVC. Generic `stripe trigger` events do not contain Nutshell's order binding and intentionally cannot mark an order paid. No live Stripe requests or real emails are part of the automated suite.

## Order and payment lifecycle

1. GET checkout displays the server-calculated total and a session checkout key; it does not create a payment intent.
2. POST payment preparation validates the address and cart, then atomically creates one `pending` order and its price snapshots. Authenticated ownership is assigned here. A unique checkout key makes repeated/concurrent submissions reuse that order.
3. After the database transaction, the server creates a Stripe PaymentIntent for the saved total and currency, with an idempotency key derived from the order key. Existing intents are retrieved on retries. The server binds the intent ID uniquely to the order before returning its client secret to that checkout session.
4. Stripe.js confirms the card payment. A browser redirect displays the order but cannot mark it paid.
5. Only a signature-verified `payment_intent.succeeded` webhook with the correct intent ID, order key, amount, amount received, currency and successful intent status marks the order `paid`. Failure events mark it `failed`; a later success can recover it, while a delayed failure cannot regress `paid`.
6. A row lock serializes competing events; a unique Stripe event ID records processing. Duplicate deliveries acknowledge success without creating orders or repeating transitions. If an event arrives before intent binding, HTTP 503 requests a retry.

Confirmation GETs have no business side effects. They do not clear the bag, save profile data, transfer ownership or send email. A paid order offers an explicit POST button to clear its purchased bag; it leaves a newer bag intact. Saved profile data is updated only from a validated, authenticated checkout POST when opted in. Failed payments offer a return to checkout. Unavailable payment services return a retryable customer message.

Contact and delivery details can be corrected on a pending or failed checkout without creating another order or PaymentIntent. Corrections are validated and serialized with payment confirmation; they cannot alter ownership, the saved prices or a paid order's details.

Orders created before this change are labelled `legacy` (unverified), rather than presumed paid. Their existing identities, ownership and totals remain intact. See [engineering review](docs/engineering-review.md) for migration details and tradeoffs.

Legacy guest orders have no trusted session capability from the old flow and require operator assistance; migration does not make their references publicly accessible.

## Order privacy

Signed-in customers may view only orders linked to their profile. Confirmation and history endpoints enforce that rule on the server. Neither order numbers nor matching email addresses prove ownership. Profile history filters by the current user.

Guest orders use a random server-issued checkout key stored in the Django session as an access capability. Knowing the displayed order number does not provide access. The same guest session can revisit its order; logging in does not claim it. Losing the session loses guest access, and no email-based recovery is implemented. Keep Django's database-backed session engine; do not switch to a cookie-only engine without reviewing guest capability confidentiality.

## Tests and CI

```powershell
python -m pip check
python manage.py check --settings=nutshell.test_settings
python manage.py makemigrations --check --dry-run --settings=nutshell.test_settings
python -Wd manage.py test --settings=nutshell.test_settings --noinput
```

Set `DATABASE_URL` to an isolated PostgreSQL test database connection before running concurrency/constraint verification. The database role must be permitted to create Django's temporary test database. Never point tests at production. Without that variable, SQLite provides a quick local run and skips row-lock concurrency tests. The test settings use mocked Stripe responses and in-memory email.

GitHub Actions runs the suite against PostgreSQL 17 and Python 3.12, checks migration drift and validates dependencies. The workflow is provided; a hosted Actions run has not been observed in this session.

## Existing database upgrade

Back up your database and media, install the pinned dependencies, stop checkout traffic, and run `python manage.py migrate` in a staging environment first. Keep all existing migration history. No database was reset during this review.

The new migrations add payment state, per-order random keys, unique payment intent/event constraints, line-item price snapshots, protected product references, quantity bounds and unique wishlist entries. Keys are generated separately for each existing order. Historical unit prices are derived from stored line totals divided by quantity, never from current catalogue prices. Existing totals are not recalculated.

If duplicate order references, duplicate non-empty intent IDs, invalid quantities or duplicate wishlist entries exist, migration stops with a reconciliation message and does not silently delete them. Resolve those records with an operator who can inspect the relevant test/payment history before retrying. Existing unknown legacy ownership is not reassigned.

## Demonstration and limitations

- Edit an existing product as the owner and verify its URL, review and wishlist still refer to the same product.
- Submit an invalid edit, try management as a customer, and show that GET deletion is refused.
- Add reviews rated four and five to show a 4.5 mean and five rounded stars.
- Show correct cart delivery boundaries and rejected invalid quantities.
- Complete a Stripe test checkout, observe pending/paid status, replay its webhook, and show that another browser/user cannot read the order.
- Run the PostgreSQL suite and inspect the tests for duplicate events, concurrent checkout and migration preservation.

Automatic order confirmation emails are intentionally disabled: the previous webhook could resend them for every delivery. A durable email outbox/worker would be the next step before reintroducing delivery guarantees. Account verification remains an allauth feature with a safe local email backend. Refunds, disputes, cancellation reconciliation, inventory reservations, expired pending-order cleanup and guest access recovery are not implemented. An operator must reconcile prolonged pending payments using Stripe before fulfilling orders. Concurrent cart edits in multiple tabs can still follow Django session last-write behavior.

Stripe's browser flow, S3 credentials and hosted deployment need manual integration verification with your own test configuration. The automated suite verifies the application rules and real webhook signature verification without contacting Stripe. Original screenshots illustrate the existing design, not a claim of a new browser audit or current public deployment.
