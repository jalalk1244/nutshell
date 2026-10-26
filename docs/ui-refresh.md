# Warm botanical UI refresh

The storefront now uses cream, forest green, sage and a restrained terracotta accent, with serif headings and a shared set of spacing, colour and component styles in `static/css/base.css`. Existing product images are retained; catalogue photography remains dependent on the supplied media.

Updated screens: home, catalogue, product details/reviews, wishlist, shopping bag, checkout, customer profile and order confirmation. The shared header/footer carry the style into existing authentication and product-management pages. No new payment or shopping feature was added.

The header uses native search/account disclosure menus, local SVG icons, a mobile hamburger menu and bag count. The hamburger reveals category links below 801px while desktop navigation stays visible on larger screens. Header menus close with Escape or an outside click; Escape restores focus to the toggle. Opening another header menu closes the previous one. The basic disclosure works without JavaScript. Pages include a skip link, visible keyboard focus, named quantity/removal controls, labelled checkout inputs and reduced-motion styling. Messages stay visible until dismissed rather than disappearing automatically.

Catalogue categories come from the database. Search, category, subcategory and sorting now compose correctly; previously some of those query branches discarded earlier filters. A regression test covers category/search/sort composition and mismatched category/subcategory results. Empty searches, wishlists and bags have useful next actions. The wishlist product link now goes to the actual product instead of an empty fragment.

Checkout preserves the existing field names, CSRF token, checkout key and Stripe element IDs. Product management, reviews, wishlist and cart mutations retain their server authorization and POST forms. Confirmation has distinct pending, failed, paid and unverified messages; viewing it still cannot confirm payment or change ownership. Profile field labels are now visible alongside placeholders.

The old newsletter integration is retained with the same provider endpoint, but the misleading immediate success modal is removed. Newsletter submission was not exercised. Stripe.js loads only on checkout, and the global Mailchimp validation script is no longer needed for its native email field.

## Verification

- SQLite suite: 57 tests discovered, 55 passed, two PostgreSQL row-lock tests skipped. The earlier payment implementation had already passed its full PostgreSQL suite; payment transitions were not changed in this UI pass.
- Native browser checks at 1440px and 390px: home, catalogue, bag, checkout, profile and all four order-payment states fit the viewport without horizontal overflow. The product screen was also checked at 390px. Home, catalogue, product and profile also passed a 768px tablet overflow check.
- Browser interaction: add two sample products through the actual product form, navigate to bag and checkout, open search and close it with Escape. The sample bag displayed $9.98 subtotal, $3 delivery and $12.98 total.
- JavaScript syntax and Django system checks passed. No schema change or new migration is required for the UI refresh.

The live preview uses an isolated demo SQLite database. No real payment, email or newsletter submission was made. These checks are not a complete accessibility audit or a verification of live Stripe/S3 configuration. The GitHub Actions workflow continues to provide PostgreSQL validation when pushed.
