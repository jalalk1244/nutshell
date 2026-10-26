# Local verification — 26 October 2026

The final source was checked in the chat's writable verification copy using the isolated virtual environment created for the requested Nutshell project. Python was 3.12.3, Django 5.2.18 and PostgreSQL 17. The local Python patch should be updated before hosting.

| Check | Observed result |
| --- | --- |
| PostgreSQL test suite, `python -Wd manage.py test --settings=nutshell.test_settings --noinput` | 56 tests passed, no skips |
| SQLite test suite with the same command and no DATABASE_URL | 56 discovered; 54 passed, two row-lock concurrency tests skipped as expected |
| Django system checks | No issues |
| `makemigrations --check --dry-run` | No changes detected |
| `pip check` | No broken requirements |
| `collectstatic --noinput --settings=nutshell.test_settings --verbosity 0` | Completed successfully using local filesystem storage |
| `node --check checkout/static/checkout/js/stripe_elements.js` | Completed successfully |
| Django system check with USE_AWS and a placeholder bucket | No issues; no live S3 request performed |

PostgreSQL used a separate temporary cluster bound to loopback on port 55439, containing only synthetic test data. The existing project database was not migrated or reset. The suite creates and destroys its own temporary test database.

Meaningful regressions include existing-row editing, failed validation, owner permissions, ratings and rounding, review identity, wishlist ownership, CSRF/method requirements, profile updates, guest and account order privacy, decimal totals, quantity bounds, price changes, immutable order snapshots, signature verification, payment mismatch rejection, duplicate/out-of-order events, concurrent webhook and checkout submissions, and forward migration of seeded legacy records.

Stripe API calls were mocked. A separate test exercises the real Stripe webhook signature verifier with a locally generated valid HMAC; invalid and missing signatures are also tested. Email uses Django's in-memory backend. No live charge, real email, public deployment, paid resource, customer data mutation or S3 upload was performed.

The hosted GitHub Actions workflow, Gitpod image build, Stripe.js browser flow and live storage configuration remain unverified. Automatic order confirmation email is disabled pending a durable delivery design. A removed legacy telemetry credential appeared during inspection; its owner should rotate/revoke it, and its old Git history has not been rewritten.
