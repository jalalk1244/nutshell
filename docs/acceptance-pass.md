# Final acceptance pass

Date: 26 October 2026. Work is performed one step at a time; later steps remain pending until explicitly started.

## Step 1 — Stripe sandbox checkout: passed

- Successful payment: the user completed checkout with Stripe's successful test card. The database recorded a signature-verified success event and marked its bound order paid.
- Declined payment: the user submitted Stripe's generic-decline test card and saw a decline message. A failure webhook was recorded, the order remained failed rather than paid, and its checkout bag was retained. Earlier successful payments remained paid.
- Duplicate success: an already-recorded success event was retrieved read-only from the sandbox API and POSTed twice to the running local webhook endpoint with fresh local signatures. Both requests returned 200, without changes to orders, line items or processed-event records.
- Duplicate failure: an already-recorded failure event was retrieved and replayed through the same endpoint. It returned 200 without changing those records.
- Signature rejection: replaying the success payload with an invalid signature returned 400 and left database state unchanged.

Replay was local, using actual retrieved sandbox payloads and the local listener signing secret. It was not a Dashboard-initiated resend or a new payment. Payloads, secrets, customer details and payment references were not included in the report.

Two bugs were resolved during this step: correcting delivery details on a retry now reuses the saved order/intent, and the purchased cart now clears automatically through a CSRF-protected POST after verified payment. The cart implementation passed browser checks for successful clearing, delayed confirmation, failed-payment retention and preservation of a newer bag. The complete regression suite passed all 67 tests on isolated PostgreSQL.

The preview uses a separate demo database, test-only keys and an in-memory email backend. No live charge or real email was sent. Local test credentials, CLI tools and diagnostic scripts remain Git-ignored.

## Step 2 — Accounts and product management: passed

- Signup and verification: the user created a dedicated acceptance account, followed its locally captured email link and confirmed the address. The database verified the email and associated profile existed.
- Authentication/profile: the user signed in, opened the private profile, saved fictional delivery details and confirmed they persisted after refresh.
- Wishlist: adding, persistence after refresh, removal and persistence of removal passed the user's browser walkthrough.
- Customer permissions: the regular account was denied product management. Direct customer create/edit/delete requests returned 403, edit controls were hidden and product data stayed unchanged.
- Owner creation/editing: temporary owner privileges were granted only to the acceptance account in the isolated demo database. The user created a temporary product and edited its name/price. The edit template initially submitted to the add endpoint and contained nested forms; both defects were fixed. A new regression test reproduced the routing failure before the fix, all 13 product tests passed afterward, and a separate browser fixture confirmed submission updated the same row without duplicates.
- Owner deletion: the user deleted the temporary acceptance product. Its absence and restoration of the original product count were verified. The acceptance account's original customer permissions were restored afterward.

Verification emails were saved through Django's local file-based backend in a Git-ignored directory. No real email was sent, and no passwords or confirmation links were included in this record. Temporary browser owner/product fixtures were removed. The acceptance account remains a normal customer.

## Step 3 — GitHub Actions: passed

The remote `main` revision matched local commit `35478f88c150029ec049edfc7e700894ecbb1e5f`. GitHub's public Actions API reported the `Django checks` workflow completed successfully for that exact revision.

Verified run: [Django checks #40355672824](https://github.com/jalalk1244/nutshell/actions/runs/40355672824).

The committed workflow runs on Ubuntu with Python 3.12 and PostgreSQL 17. It installs the pinned dependencies, checks dependency consistency, runs Django system checks, checks migration drift and runs the Django test suite. This is a hosted CI result, separate from earlier local test runs. Subsequent commits will trigger their own checks.

## Step 4 — Watermarked storefront imagery: passed

Two visibly watermarked stock photos were identified: the old dried-fruit image and the old seed image. New illustrative food images were generated using the built-in ImageGen tool, visually inspected, and packaged as WebP files. The final prompts, asset paths, dimensions and provenance are recorded in [image assets](image-assets.md).

Homepage category tiles use the replacements directly. Catalogue/wishlist cards, product details, bag and checkout share a filename-specific URL filter. It replaces only identified legacy stock filenames and preserves custom upload/storage URLs and existing database records. No migration, media deletion, live storage upload or public deployment was performed.

All 18 relevant product/home tests passed, including regressions for replacement URLs in the storefront and preservation of custom uploads. Local static collection succeeded. Isolated desktop/mobile browser checks confirmed both new assets decoded correctly across home, catalogue, product details, bag and checkout, with no known legacy watermark URLs in those views and no catalogue horizontal overflow. New filenames avoid stale-image caching.

The hosted CI result above predates this image update. Push the completed image commit to trigger verification of the latest revision.

## Optional remaining step

Step 5: verify deployment/storage if a public demo is desired. It remains unstarted; public deployment requires explicit authorization.

Automatic order email delivery, guest order recovery and refunds/disputes remain documented project limitations. Earlier artwork and historical screenshots are outside the scope of this two-image replacement pass.
