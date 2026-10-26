# Engineering review

## Baseline and confirmed findings

The requested repository was clean when inspected. Its requirements pinned Django 3.2, Stripe 5.0.0, allauth 0.52.0 and Pillow 9.4.0. Python 3.12.3 was available; Django was not installed in the base environment. No applicable AGENTS.md was found in the repository or its accessible parent paths. The existing test files contained scaffolds. A working original deployment or original dependency environment was not available, so no baseline runtime pass is claimed.

| Finding | Impact | Resolution |
| --- | --- | --- |
| POST edit form omitted `instance` | Could create a second row or fail on unique slug rather than update | Bind the selected product; regression tests preserve related reviews/wishlist and reject invalid edits |
| Rating checked an unrelated `None` variable | Always displayed zero stars | Aggregate mean, explicit no-review case, half-up integer star rounding |
| Checkout checked the `is_valid` method object | Invalid data could reach save and cause failure | Save profile only after calling validation in the authenticated checkout POST |
| Confirmation assigned current profile to any order number | Could transfer ownership and expose addresses | Assign ownership only during trusted checkout preparation; authorization on every order read |
| History endpoint lacked access checks | Anonymous/cross-account access to order details | Require login and filter by current profile |
| Anonymous review POST used AnonymousUser as a foreign key | Could crash rather than handle unauthenticated submission | Redirect to login before form save; ignore client-supplied user identity |
| Delete/wishlist/cart actions used GET | Accidental or forged navigation could change state | POST-only mutations with CSRF forms; logout still uses allauth confirmation |
| Cart quantity conversion lacked bounds | Invalid input could crash, permit negative totals or excessive quantities | Strict integer 1–99 additions; documented decrement/removal behavior |
| Cart and model delivery rules differed | Charged total and saved order could disagree | One decimal-money delivery rule |
| Webhook matched mutable customer fields then rebuilt orders | Duplicate/partial orders, ambiguous ownership and repeated emails | Pre-save one atomic snapshot; bind intent uniquely; verified, locked state transitions |
| Current catalogue price used for historical item display | Old orders could display changed prices or lose lines on product deletion | Store unit prices, protect product references and make order admin read-only |

A legacy telemetry credential was found in `.vscode/uptime.sh` and appeared in tool output during inspection. Treat it as exposed: its owner should revoke or rotate it. The prepared changes replace that script with a no-op and stop Gitpod from launching telemetry. Git history is preserved and may still contain the old credential. This review is not an exhaustive secret scan of Git history. No customer or payment records were printed.

## Upgrade decisions

Django 5.2 LTS was selected over a newer feature series for its support period through April 2028 and compatibility with Python 3.12. The resolved patch is 5.2.18. The Stripe SDK stays in the 12.x series; allauth stays in 65.x. The dependency file pins the complete resolved environment rather than floating every install to the newest release.

Compatibility changes include allauth AccountMiddleware and current signup/login settings, `crispy_bootstrap4`, `STORAGES` backend configuration, the current S3 backend import and psycopg 3. The S3 provider and migration history remain intact. Python's installed 3.12.3 patch is old and should be updated separately.

The obsolete Gitpod image (Python 3.8, PostgreSQL 12, unrelated MongoDB and automatic telemetry) is replaced with a Python 3.12 development configuration using SQLite by default. Its image build and hosted preview have not been run here; set `ALLOWED_HOSTS` to the workspace preview hostname when using it. Local PowerShell setup and PostgreSQL CI are the verified paths.

Official guidance reviewed:

- [Django upgrade process](https://docs.djangoproject.com/en/5.2/howto/upgrade-version/)
- [Django 5.2 LTS and Python compatibility](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [Django 5.0 compatibility changes](https://docs.djangoproject.com/en/5.2/releases/5.0/)
- [Django 4.0](https://docs.djangoproject.com/en/5.2/releases/4.0/), [4.1](https://docs.djangoproject.com/en/5.2/releases/4.1/), [4.2](https://docs.djangoproject.com/en/5.2/releases/4.2/) and [5.1](https://docs.djangoproject.com/en/5.2/releases/5.1/) intervening release notes
- [Allauth release notes](https://docs.allauth.org/en/latest/release-notes/recent.html)
- [Allauth installation](https://docs.allauth.org/en/latest/installation/quickstart.html), [S3 storage configuration](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html) and [crispy template packs](https://django-crispy-forms.readthedocs.io/en/latest/install.html)
- [Stripe webhook verification, retries and duplicate delivery](https://docs.stripe.com/webhooks)

## Payment reasoning for interviews

The database owns the intended order, not the browser. Prices and delivery are computed once for a validated checkout and saved with line items in a transaction. The external API call occurs after that transaction, so network latency does not hold database locks. Stripe idempotency recovers intent creation retries; a stored intent ID is reused on later retries. If Stripe wins the race to webhook delivery before that ID is saved, the endpoint asks Stripe to retry.

The webhook's signature proves the event origin. Intent ID, order key, amount and currency checks prove it applies to the saved purchase. A row lock serializes state changes; unique event IDs deduplicate repeated deliveries. `paid` is terminal within the implemented success/failure lifecycle, so late failure events cannot undo successful payment. Refund/dispute handling requires a separate future state model rather than repurposing payment failure.

Order reads never mutate ownership. Authenticated access uses the saved profile relationship. Guest access uses a random session capability and does not infer ownership from an email address. A signed-in user can revisit a guest order from that same session but cannot turn it into their profile order merely by viewing it.

The old webhook sent email during every processing attempt. Automatic order emails have been removed pending a durable outbox/worker design. There is no exactly-once email-delivery claim. The application records payment state and event history without synchronous mail or external API calls inside webhook transactions.

## Validation boundaries

The suite exercises application authorization and money rules, Stripe API responses are mocked, and the real Stripe HMAC verifier is tested with a locally signed event plus invalid/missing signatures. PostgreSQL tests cover duplicate webhook concurrency, simultaneous checkout preparation and schema constraints. A migration test seeds old-schema orders, migrates forward and verifies preserved identities/totals, independent random keys and prices derived from stored line totals.

No live charge, real email, S3 upload, public deployment or customer database migration was performed. Hosted CI and the browser/Stripe.js integration still need manual test-mode verification. See README for the demonstration steps and remaining limitations.

## CV wording after verification

- Modernized a Django e-commerce portfolio application to Django 5.2 LTS with pinned dependencies, PostgreSQL CI and regression coverage for authorization, checkout and cart behavior.
- Implemented server-priced order snapshots and signature-verified Stripe payment transitions, using database uniqueness constraints and row locks to handle duplicate and concurrent webhook delivery.
- Secured order confirmation/history with profile ownership and session-bound guest access, and added regression tests for product identity, profile validation and payment ordering.

These bullets describe implementation and local test verification; they do not imply production deployment, measured performance or a coverage percentage.
