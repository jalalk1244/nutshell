# Catalogue image provenance

Created on 26 October 2026 using Codex's built-in ImageGen tool. These are newly generated illustrative food images for the portfolio demo, not photographs documenting actual goods for sale. No stock photo was supplied as an edit target and no watermark was removed from an existing photo.

| Project asset | Dimensions | File size | Used for |
| --- | --- | --- | --- |
| `static/media/catalogue/dried-fruit-mix.webp` | 1254 × 1254 | 250,454 bytes | Dried-fruit category and identified legacy dried-fruit product imagery |
| `static/media/catalogue/seed-mix.webp` | 1254 × 1254 | 232,930 bytes | Seed category and identified legacy seed product imagery |

Generated PNG originals were retained in Codex's generated-image directory. The project files are WebP encodings of those originals with no resizing, cropping or scene edits. These filenames are new URLs, avoiding the stale-image cache problem that overwriting an old stock-photo URL could cause. Both assets are included by normal `collectstatic`.

## Integration

Homepage category images reference the assets directly. The shared `product_image_url` template filter substitutes them only for these identified legacy image-field values:

- `dry_fruits.jpg` → `media/catalogue/dried-fruit-mix.webp`
- `seeds.jpg` and `seeds_EO8exKU.jpg` → `media/catalogue/seed-mix.webp`

Catalogue cards, wishlist cards, product details, bag and checkout use the same filter. Other uploaded images retain their configured media-storage URL. Database records, existing media files, the storage provider and historical screenshots were preserved. When hosting with S3 static storage, publish the new static assets through the normal deployment process; no upload or public deployment was performed in this pass.

This replaces the two visibly watermarked stock images in the active storefront. Other existing imagery and historical screenshots were not replaced; this record does not claim a complete rights audit of earlier assets.

## Final generation prompts

### Dried fruit

Use case: product-mockup. Asset type: square ecommerce product photograph for Nutshell, a warm botanical nuts-and-dried-fruit portfolio store. Generate a brand-new photorealistic food photograph, not an edit of any existing photo. Subject: an appetizing dried-fruit mix containing golden-orange dried apricots, wrinkled dark raisins, golden raisins and a few rich brown dates in a shallow matte ivory ceramic bowl, with a few loose pieces beside the bowl. No nuts or fresh fruit. Scene: pale warm cream limestone surface, subtle natural linen near the edge. Composition: square 1:1, gently elevated three-quarter view, bowl centered, generous clean margin on every side so it remains visible when cropped to a portrait product card. Lighting: soft natural side daylight, restrained soft shadows, realistic fine surface texture, sophisticated understated food editorial photography. Palette: warm cream, amber, deep brown, very subtle sage linen. No text, letters, labels, logos, watermark, packaging, people, hands, graphic frames or collage. The output is the photograph only.

### Seeds

Use case: product-mockup. Asset type: square ecommerce product photograph for Nutshell, a warm botanical nuts-and-seeds portfolio store. Generate a brand-new photorealistic food photograph, not an edit of any existing photo. Subject: a natural seed mix of green pumpkin seed kernels, ivory hulled sunflower kernels, golden flax seeds and a small quantity of sesame seeds in a shallow matte ivory ceramic bowl; a few seeds scattered next to it. No nuts, fruit, leaves, shells, sprouts or packaging. Scene: pale warm cream limestone surface, subtle sage natural linen near the edge. Composition: square 1:1, gently elevated three-quarter view, bowl centered, generous clean margins so it works cropped into a portrait product card. Lighting: soft natural side daylight, restrained soft shadows, realistic seed texture and natural irregularity, sophisticated understated food editorial photography. Palette: warm cream, muted pumpkin-seed green, ivory, gold and subtle sage. No text, letters, labels, logos, watermark, people, hands, graphic frames or collage. Photograph only.

## Original generated PNG fingerprints

- Dried fruit SHA-256: `9aac19b46497dd2db580986f997c593b5e4f3c11a42dc4d654f0051e443ac788`
- Seeds SHA-256: `55833db6675690cac7d5109859332988935dbccbfbaf9505f6c0040dbaa9caac`
