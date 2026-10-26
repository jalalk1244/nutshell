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

## Remaining acceptance steps

- Step 2: browser walkthrough of signup, login, profile, wishlist and owner product management — pending.
- Step 3: observe GitHub Actions passing after push — pending.
- Step 4: review and replace watermarked product imagery — pending.
- Step 5: verify deployment/storage if a public demo is desired — pending; public deployment requires explicit authorization.

Automatic order email delivery, guest order recovery and refunds/disputes remain documented project limitations.
