# One-Go Check v1 — Oct 26, 2026

Hackathon-period wiring, built Oct 26, 2026. Earlier app and demo work is separate and is not claimed here.

## Flow
1. SAM 3.1 crops the card. Verified working form: short noun phrase "trading card" plus the image, via POST /v1/responses. A long instructional prompt returned empty output, so use the short form only.
2. Database comparison, v1: manifest lookup by filename only. If the input is not a known pool file, or no tells were measured, the result is honestly Inconclusive. v1 does NOT measure tells yet, so it must NOT return Likely Genuine or Likely Counterfeit from a crop alone.
3. Muse Spark 1.3 explains the result in plain words, via POST /v1/messages. Spark thinking can consume about 1,500 tokens before any visible text, so use max_tokens 4000. A 1,200 limit returned no text in the Oct 26 test. Parse the content array by type and skip redacted thinking items.
4. Muse Image 1.0 draws a cauldron illustration, via POST /v1/images/generations. Art only, never a fake card photo, never a replacement for a real card image.

## Test run, Oct 26, 2026
- Input: sr-0001-BS-1.png, 600x825, from the sourced-reals pool.
- SAM box: x1=18, y1=16, x2=584, y2=813.
- Cropped: 566x797.
- Manifest match: Alakazam, Base / BS, 1, Rare Holo, source pokemontcg.io.
- Spark text: 851 characters, plain-words explanation, verdict Inconclusive, with the reason that no tells were measured.
- Image: one cauldron illustration saved in the local test output, not committed here as a binary.
- Verdict disclaimer, always: photo-based opinion only, never a guarantee.

## Auth
The script reads META_MODEL_API_KEY from the environment in public use. In Muse's workspace it falls back to the stored Meta Model API connection. No key is logged, written to output, or committed to this repo.

## Next steps, in owner-approved order
1. Push this v1 (this commit).
2. Global top-bar and menu navigation fix, verified on a real phone.
3. Grade a Card SAM measurement flow: crop front and back, border and centering measure, edge and corner flags, Spark estimate explanation, estimate-only disclaimer.
4. Tells measurement for One-Go, so a future version can move past Inconclusive only when tells are actually measured.
