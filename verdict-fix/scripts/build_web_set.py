#!/usr/bin/env python3
"""build_web_set.py - outside TEST set of real-vs-fake card photos from public web pages.

NEVER mix into house training data, labels, weights or thresholds. Images are not
committed (copyright): only this script, manifest.csv/json and URLs are. Re-run to
re-download into web-set/raw/ and re-cut crops into web-set/crops/.

Labels: only what the source page states (quote kept in label_basis). Anything the
page does not state = UNKNOWN. px/mm values are ESTIMATES (method column).
"""
import os, sys, csv, json, hashlib, subprocess
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import cardfeat as cf

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web-set")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
S3 = "https://s3.amazonaws.com/ccg-corporate-production/news-images/"
CF = "https://images.ctfassets.net/t8bripszr2o9/"
P = {  # source pages
 "ef17741": "https://www.elitefourum.com/t/identifying-fake-cards-from-the-newer-sets/17741",
 "ef13268": "https://www.elitefourum.com/t/is-my-pokemon-card-a-misprint-or-fake-guide-to-fake-cards/13268",
 "ef23015": "https://www.elitefourum.com/t/microscope-resource-thread-update-video-9-on-page-4/23015",
 "ef64743": "https://www.elitefourum.com/t/why-most-international-holos-are-printed-without-rosettes-am-vs-fm-offset-printing/64743",
 "cgcl": "https://www.cgccomics.com/news/article/8648/counterfeit-pokemon-cards/",
 "cgcd": "https://www.cgccards.hk/news/article/14311/",
 "cgcu": "https://www.cgccards.hk/news/article/15008/counterfeit-card-sm-umbreon/",
 "tci": "https://tcgcardinvestor.com/articles/how-to-spot-fake-pokemon-cards",
 "collw": "https://www.collectiwiz.com/knowledgebase/is-my-pokemon-card-or-magic-the-gathering-card-real-or-fake-a-step-by-step-illustrated-guide-to-identifying-authentic-vs-fake-aka-counterfeit-trading-cards-for-popular-tcgs",
 "flip": "https://flipsidegaming.com/blogs/pokemon-blog/identifying-fake-pokemon-cards",
 "poki": "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/",
}
Q17741 = "post #10 (Quuador): 'I took some pictures of real cards on the left, and fake cards on the right.'"
# raw images: id, url, page, photo_type, est_px_mm (None = measure card), px_mm_method, side, note
RAW = [
 ("ef17741_3270", "https://i.postimg.cc/k5yGPsPR/DSCN3270.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", Q17741),
 ("ef17741_3275", "https://s26.postimg.cc/jcl5an7x5/DSCN3275.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", Q17741 + " + 'It's name is Raikou EX instead of Pikachu EX'"),
 ("ef17741_3277", "https://i.postimg.cc/0NC4GM7q/DSCN3277.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'Both at the left are real (regular & miscut version), the three at the right are fake.'"),
 ("ef17741_3279", "https://i.postimg.cc/0NCYX7tc/DSCN3279.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'The left one is real, the three right ones are fake.'"),
 ("ef17741_3280", "https://i.postimg.cc/8C4gwnLc/DSCN3280.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'Left one is real, other two are fake.'"),
 ("ef17741_3283", "https://i.postimg.cc/QMmV5mtk/DSCN3283.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'Both left are real, both right are fake.'"),
 ("ef17741_3286", "https://i.postimg.cc/1zK1JRLD/DSCN3286.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'Left one is real, other two are fake.'"),
 ("ef17741_3288", "https://i.postimg.cc/SKG7sHMy/DSCN3288.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'The two on the left are real ...' (rest fake)"),
 ("ef17741_3292", "https://i.postimg.cc/JhxcnbCS/DSCN3292.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", Q17741 + " + 'This one actually looks very close to the real one ... proved it was fake'"),
 ("ef17741_3296", "https://i.postimg.cc/XvgWDd2Y/DSCN3296.jpg", "ef17741", "phone_photo_scene", None, "card quad", "front", "'Both on the left are real, right one is fake.'"),
 ("ef13268_a", "https://i.imgur.com/DDcSIxF.jpg", "ef13268", "composite_graphic", None, "card quad", "front", "'Below is an image of a fake Pokemon card (right) and a real one (left)'"),
 ("ef13268_d", "https://i.imgur.com/CimJHsr.jpg", "ef13268", "phone_photo_scene", None, "card quad", "back", "post #10 (aetsen): 'The real card is on the right and the fake is on the left.'"),
 ("ef23015_68c", "https://i.imgur.com/68cciST.jpg", "ef23015", "phone_photo_scene", None, "card quad", "front", "post #9: 'the real unlimited dragonair' vs 'the fake 1st shadowed dragonair' (fake = the one with the 1st Edition stamp, middle)"),
 ("ef23015_realstamp", "https://i.imgur.com/x48rjVA.jpg", "ef23015", "microscope", 190.0, "on-image mm annotation on sibling fake-stamp shot at same 20X (approx)", "front", "'Real stamp on Pidgey(20X)'"),
 ("ef23015_fakestamp", "https://i.imgur.com/8sl4udT.jpg", "ef23015", "microscope", 190.0, "on-image mm annotation 4.31 mm ~ 830 px (approx)", "front", "'Fake stamp on fake dragonair(20X)'"),
 ("ef23015_phonefake", "https://i.imgur.com/Rrbjexz.jpg", "ef23015", "phone_closeup", 60.0, "text size guess (approx, low confidence)", "front", "post #17: 'Phone picture of fake dragonair'"),
 ("ef64743_b01", "https://efour.b-cdn.net/uploads/default/original/4X/3/7/6/37672bc7cdedbee2c27ec26509e074022e0aa6a8.jpeg", "ef64743", "microscope", 615.0, "on-image 1000 um scale bar ~615 px", "back", "@hian_43: 'I imaged 12 cards ... Base Set Unlimited to 30th Celebrations' / 'all my samples consist of authentic cards'"),
 ("ef64743_b02", "https://efour.b-cdn.net/uploads/default/original/4X/e/e/b/eeb8088a7064b9d9cc767efbd096a32218dfbaca.jpeg", "ef64743", "microscope", 615.0, "scale bar (same rig as b01)", "back", "same as b01"),
 ("ef64743_b03", "https://efour.b-cdn.net/uploads/default/original/4X/0/f/f/0ff9cdc7dd4b896c4df91c18825b622a1374c4ae.jpeg", "ef64743", "microscope", 615.0, "scale bar (same rig as b01)", "back", "same as b01"),
 ("ef64743_b04", "https://efour.b-cdn.net/uploads/default/original/4X/4/7/0/4709f98bd3c15dc80b10c118e07ea058fc977d0e.jpeg", "ef64743", "microscope", 615.0, "scale bar (same rig as b01)", "back", "same as b01"),
 ("ef64743_b05", "https://efour.b-cdn.net/uploads/default/original/4X/a/b/6/ab65a5303ee8acea402dee6864699fd05e33798b.jpeg", "ef64743", "microscope", 615.0, "scale bar (same rig as b01)", "back", "same as b01"),
 ("ef64743_b06", "https://efour.b-cdn.net/uploads/default/original/4X/e/3/5/e3505f7a726f5ace5618e9d8c91df9cb622f2059.jpeg", "ef64743", "microscope", 615.0, "scale bar (same rig as b01)", "back", "same as b01"),
 ("cgcl_edge", CF + "newsimg-8c59a5c6f50b904823d36566a5f5671c/3564b42ef6cc0cbc0edda4b8b7828898/_DSC0629_-_Copy_-_Copy__2_20201023165918045.JPG", "cgcl", "edge_macro", None, "n/a", "edge", "'Edges of the fake Lucky Stadium (left) and a genuine card (right)'"),
 ("cgcl_starng", CF + "newsimg-9173ebc5f5914911c127ba0010cc8a14/16d7ee79dd698cfa721550fbea454501/Star_NG_DSC0626_-_Copy20201023162138168.JPG", "cgcl", "lab_macro", 100.0, "Black Star symbol size guess (approx, low confidence)", "front", "'close-up photos of the Black Star' on the counterfeits ('NG' file); 'poorly reproduced it using a consumer printer'"),
 ("cgcl_star1", CF + "newsimg-444d752ee04b85652d1bde4212551229/199e51027dcc67943eb27fd7e816ecd5/Star_DSC0658_-_Copy_-_Copy20201023162152298.JPG", "cgcl", "lab_macro", 100.0, "same framing as starng (approx)", "front", "genuine close-up ('first O in PROMO on a genuine card' is a crop of this same DSC0658 frame)"),
 ("cgcl_star2", CF + "newsimg-bca378746d614f6fda46cb381228c761/f33ec822621040c54be3885addf11f45/Star_DSC0658_-_Copy20201023162205409.JPG", "cgcl", "lab_macro", 300.0, "letter O size guess (approx, low confidence)", "front", "'the four different colored dots are easily seen in the first O in PROMO on a genuine card'"),
 ("cgcd_machreal", S3 + "Machamp%20Real_FR_lg20250805122147194.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "front", "caption: 'genuine 1st Edition Base Set Machamp (left image) vs counterfeit'"),
 ("cgcd_machfake", S3 + "Machamp%20Fake_FR_lg20250805121754606.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "front", "same caption (right image = counterfeit)"),
 ("cgcd_backreal", S3 + "Charizard%20Back_lg20250801133159366.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "back", "caption: 'genuine Pokemon card back (left image) vs counterfeit'"),
 ("cgcd_backfake", S3 + "Fake%20Charizard_BK_lg20250801133302689.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "back", "same caption (right = counterfeit Disco Charizard back)"),
 ("cgcd_taxireal", S3 + "Taxi%20Pattern%20Genuine_lg20250801133818125.jpg", "cgcd", "lab_macro", 60.0, "logo letter height guess (approx)", "back", "caption: 'genuine card back (left) vs counterfeit, close-up' (file 'Genuine')"),
 ("cgcd_taxifake", S3 + "Taxi%20Pattern%20Fake_lg20250801133911380.jpg", "cgcd", "lab_macro", 60.0, "same framing as taxireal (approx)", "back", "same caption (file 'Fake')"),
 ("cgcd_czfake", S3 + "Fake%20Charizard_FR_lg20250801124917686.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "front", "counterfeit 'Disco' test print Charizard (page: 'none of these cards were genuine')"),
 ("cgcd_czreal", S3 + "1_Real20250805153133679.jpg", "cgcd", "lab_scan_or_photo", None, "card quad", "front", "caption: 'genuine Disco test print Charizard (left), genuine shadowless Charizard (middle), counterfeit (right)' - this is the left (file '1_Real')"),
 ("cgcu_obvreal", S3 + "Obv_real_lg20260306144716962.jpg", "cgcu", "lab_scan_or_photo", None, "card quad", "front", "caption: 'counterfeit (left) vs genuine' - genuine (file 'Obv_real'); Simplified Chinese card"),
 ("cgcu_obvfake", S3 + "Obv_fake_lg20260306144852637.jpg", "cgcu", "lab_scan_or_photo", None, "card quad", "front", "same caption - counterfeit (file 'Obv_fake')"),
 ("tci_rip", "https://tcgcardinvestor.com/articles/img/how-to-spot-fake-pokemon-cards/rip-test-fake-vs-real.webp", "tci", "composite_graphic", None, "n/a", "edge", "'The counterfeit Black Kyurem EX, left ... The genuine Blaziken EX, right' (two photos side by side)"),
 ("tci_phole", "https://tcgcardinvestor.com/articles/img/how-to-spot-fake-pokemon-cards/p-hole-chessboard-real-vs-fake.webp", "tci", "composite_graphic", 100.0, "P-hole size guess (approx, low confidence)", "back", "'Left: a genuine card ... Right: a fake' (two macros side by side)"),
 ("collw_backs", "https://images.squarespace-cdn.com/content/v1/67fecc9ef0cec617cb14ac37/5e456b37-c545-4544-993a-2ccb5958b293/Fake_vs_Real_Pokemon_Cards_2_backs.png?format=2500w", "collw", "composite_graphic", None, "n/a", "back", "graphic labelled 'Real' (left photo) / 'Fake' (right photo), same table"),
 ("flip_regreal", "https://cdn.shopify.com/s/files/1/0128/0782/files/regice_real_a06fef48-8b42-4161-b061-f1b3f8e7057b.jpg", "flip", "phone_photo_scene", None, "card quad", "front", "'[Fake on the left, real on the right]' - file 'regice_real'"),
 ("flip_regfake", "https://cdn.shopify.com/s/files/1/0128/0782/files/regice_fake_b1f9e4f2-4b6f-40bc-952b-ab3ddb15e5f8.jpg", "flip", "phone_photo_scene", None, "card quad", "front", "same caption - file 'regice_fake'"),
 ("flip_backreal", "https://cdn.shopify.com/s/files/1/0128/0782/files/real_pokemon_back.jpg", "flip", "phone_photo_scene", None, "card quad", "back", "file 'real_pokemon_back' under '[Fake on the left, real on the right]'"),
 ("flip_backfake", "https://cdn.shopify.com/s/files/1/0128/0782/files/pokemon_fake_back.jpg", "flip", "phone_photo_scene", None, "card quad", "back", "file 'pokemon_fake_back'"),
 ("poki_c1", "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/c1.webp", "poki", "loupe_phone", 230.0, "1st Edition stamp width ~4.3 mm (approx)", "front", "article on counterfeit 1st Edition cards the author bought: 'close-up shots taken through a loupe' of the fakes"),
 ("poki_c2", "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/c2.webp", "poki", "loupe_phone", 230.0, "same loupe as c1 (approx)", "front", "same as c1"),
 ("poki_c3", "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/c3.webp", "poki", "loupe_phone", 230.0, "same loupe as c1 (approx)", "front", "same as c1"),
 ("poki_c4", "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/c4.webp", "poki", "loupe_phone", 230.0, "same loupe as c1 (approx)", "front", "same as c1"),
 ("poki_04", "https://pokiplanet.com/blog/posts/1st-edition-base-set-fakes/04.webp", "poki", "scan_or_flat_photo", None, "card quad", "front", "cards from the counterfeit packs the author bought ('The non-holo cards are decent fakes')"),
]
# crops from multi-card / same-photo images: crop_id, raw_id, (x0,y0,x1,y1) fractions, label, pair_id
CROPS = [
 ("ef17741_3270_L", "ef17741_3270", (0.02, 0.10, 0.53, 0.97), "GENUINE", "SP01"), ("ef17741_3270_R", "ef17741_3270", (0.52, 0.10, 0.99, 0.97), "FAKE", "SP01"),
 ("ef17741_3275_L", "ef17741_3275", (0.07, 0.08, 0.55, 0.97), "GENUINE", "SP02"), ("ef17741_3275_R", "ef17741_3275", (0.52, 0.08, 0.98, 0.97), "FAKE", "SP02"),
 ("ef17741_3277_L", "ef17741_3277", (0.10, 0.56, 0.42, 1.00), "GENUINE", "SP03"), ("ef17741_3277_R", "ef17741_3277", (0.43, 0.56, 0.76, 1.00), "FAKE", "SP03"),
 ("ef17741_3279_L", "ef17741_3279", (0.08, 0.26, 0.39, 0.86), "GENUINE", "SP04"), ("ef17741_3279_R", "ef17741_3279", (0.40, 0.46, 0.68, 1.00), "FAKE", "SP04"),
 ("ef17741_3280_L", "ef17741_3280", (0.03, 0.14, 0.37, 0.84), "GENUINE", "SP05"), ("ef17741_3280_R", "ef17741_3280", (0.36, 0.16, 0.68, 0.84), "FAKE", "SP05"),
 ("ef17741_3283_L", "ef17741_3283", (0.00, 0.03, 0.51, 0.56), "GENUINE", "SP06"), ("ef17741_3283_R", "ef17741_3283", (0.49, 0.03, 1.00, 0.56), "FAKE", "SP06"),
 ("ef17741_3286_L", "ef17741_3286", (0.02, 0.18, 0.38, 0.85), "GENUINE", "SP07"), ("ef17741_3286_R", "ef17741_3286", (0.36, 0.18, 0.71, 0.85), "FAKE", "SP07"),
 ("ef17741_3288_L", "ef17741_3288", (0.11, 0.00, 0.40, 0.53), "GENUINE", "SP08"), ("ef17741_3288_R", "ef17741_3288", (0.43, 0.00, 0.71, 0.53), "FAKE", "SP08"),
 ("ef17741_3292_L", "ef17741_3292", (0.05, 0.06, 0.51, 0.99), "GENUINE", "SP09"), ("ef17741_3292_R", "ef17741_3292", (0.50, 0.06, 0.97, 0.99), "FAKE", "SP09"),
 ("ef17741_3296_L", "ef17741_3296", (0.01, 0.03, 0.53, 0.55), "GENUINE", "SP10"), ("ef17741_3296_R", "ef17741_3296", (0.48, 0.24, 1.00, 0.86), "FAKE", "SP10"),
 ("ef13268_a_L", "ef13268_a", (0.00, 0.00, 0.42, 1.00), "GENUINE", "SP11"), ("ef13268_a_R", "ef13268_a", (0.58, 0.00, 1.00, 1.00), "FAKE", "SP11"),
 ("ef13268_d_R", "ef13268_d", (0.45, 0.16, 0.88, 0.82), "GENUINE", "SP12"), ("ef13268_d_L", "ef13268_d", (0.10, 0.25, 0.50, 0.84), "FAKE", "SP12"),
 ("ef23015_68c_L", "ef23015_68c", (0.00, 0.00, 0.335, 1.00), "GENUINE", "SP13"), ("ef23015_68c_M", "ef23015_68c", (0.325, 0.00, 0.665, 1.00), "FAKE", "SP13"),
 # genuine-vs-genuine CONTROLS from the same photos (two real copies stated in the caption)
 ("ef17741_3283_LB", "ef17741_3283", (0.00, 0.50, 0.51, 1.00), "GENUINE", "GG01"),  # + ef17741_3283_L
 ("ef17741_3288_LB", "ef17741_3288", (0.11, 0.47, 0.40, 1.00), "GENUINE", "GG02"),  # + ef17741_3288_L
 ("ef17741_3296_LB", "ef17741_3296", (0.01, 0.50, 0.53, 1.00), "GENUINE", "GG03"),  # + ef17741_3296_L
 ("ef17741_3277_LT", "ef17741_3277", (0.10, 0.00, 0.42, 0.52), "GENUINE", "GG04"),  # + ef17741_3277_L (caption: regular & miscut)
 ("tci_phole_L", "tci_phole", (0.00, 0.00, 0.50, 1.00), "GENUINE", "CP01"), ("tci_phole_R", "tci_phole", (0.50, 0.00, 1.00, 1.00), "FAKE", "CP01"),
]
# whole-image labels for raws that are a single card or single macro (not cropped)
SINGLE = {"ef23015_realstamp": "GENUINE", "ef23015_fakestamp": "FAKE", "ef23015_phonefake": "FAKE",
          **{f"ef64743_b0{i}": "GENUINE" for i in range(1, 7)},
          "cgcl_starng": "FAKE", "cgcl_star1": "GENUINE", "cgcl_star2": "GENUINE",
          "cgcd_machreal": "GENUINE", "cgcd_machfake": "FAKE", "cgcd_backreal": "GENUINE", "cgcd_backfake": "FAKE",
          "cgcd_taxireal": "GENUINE", "cgcd_taxifake": "FAKE", "cgcd_czfake": "FAKE", "cgcd_czreal": "GENUINE",
          "cgcu_obvreal": "GENUINE", "cgcu_obvfake": "FAKE",
          "flip_regreal": "GENUINE", "flip_regfake": "FAKE", "flip_backreal": "GENUINE", "flip_backfake": "FAKE",
          "poki_c1": "FAKE", "poki_c2": "FAKE", "poki_c3": "FAKE", "poki_c4": "FAKE",
          # images holding BOTH a real and a fake, kept whole only as the source of a pair (label MIXED)
          "cgcl_edge": "MIXED", "tci_rip": "MIXED", "collw_backs": "MIXED", "poki_04": "FAKE"}
# same-session (not same-photo) pairs, for reporting only
SESSION_PAIRS = [("SS01", "cgcd_machreal", "cgcd_machfake"), ("SS02", "cgcd_backreal", "cgcd_backfake"),
                 ("SS03", "cgcd_taxireal", "cgcd_taxifake"), ("SS04", "cgcd_czreal", "cgcd_czfake"),
                 ("SS05", "cgcu_obvreal", "cgcu_obvfake"), ("SS06", "flip_regreal", "flip_regfake"),
                 ("SS07", "flip_backreal", "flip_backfake"), ("SS08", "ef23015_realstamp", "ef23015_fakestamp"),
                 ("SS09", "cgcl_star1", "cgcl_starng")]


def main():
    raw_dir, crop_dir = os.path.join(OUT, "raw"), os.path.join(OUT, "crops")
    os.makedirs(raw_dir, exist_ok=True); os.makedirs(crop_dir, exist_ok=True)
    with open(os.path.join(OUT, ".gitignore"), "w") as g:
        g.write("# images are third-party, not committed\nraw/\ncrops/\n*.jpg\n*.png\n*.webp\n")
    rows, rawmeta = [], {}
    for rid, url, page, ptype, ppm, how, side, basis in RAW:
        ext = ".webp" if ".webp" in url else (".png" if ".png" in url else ".jpg")
        path = os.path.join(raw_dir, rid + ext)
        if not os.path.exists(path) or os.path.getsize(path) < 5000:
            subprocess.run(["curl", "-sL", "-A", UA, "-m", "60", "-o", path, url], check=False)
        ok = os.path.exists(path) and os.path.getsize(path) > 5000
        rawmeta[rid] = dict(path=path, url=url, page=P[page], ptype=ptype, ppm=ppm, how=how, side=side, basis=basis, ok=ok)
        if rid in SINGLE:
            img = cf.load(path) if ok else None
            est = ppm
            if ok and est is None and ptype not in ("edge_macro", "composite_graphic"):
                q, _ = cf.find_card(img, side); est = round(cf.px_per_mm(q), 1)
            pair = next((p for p, a, b in SESSION_PAIRS if rid in (a, b)), "")
            rows.append(dict(image_id=rid, file=os.path.relpath(path, OUT), label=SINGLE[rid], label_basis=basis,
                             same_photo_pair="no", pair_id=pair, pair_kind="same_session_not_same_photo" if pair else "",
                             photo_type=ptype, side=side, est_px_per_mm=est, px_mm_method=how if ppm else "card quad (find_card)",
                             image_url=url, page_url=P[page], crop_of="", sha256=hashlib.sha256(open(path, "rb").read()).hexdigest() if ok else "", downloaded=ok))
    for cid, rid, (x0, y0, x1, y1), lab, pair in CROPS:
        m = rawmeta[rid]
        if not m["ok"]:
            continue
        img = cf.load(m["path"]); h, w = img.shape[:2]
        crop = img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
        cp = os.path.join(crop_dir, cid + ".png"); cv2.imwrite(cp, crop)
        if m["ppm"]:
            est, how = m["ppm"], m["how"]
        else:
            q, _ = cf.find_card(crop, m["side"]); est, how = round(cf.px_per_mm(q), 1), "card quad (find_card on crop)"
        rows.append(dict(image_id=cid, file=os.path.relpath(cp, OUT), label=lab, label_basis=m["basis"],
                         same_photo_pair="no" if pair.startswith("CP") else "yes", pair_id=pair,
                         pair_kind="composite_two_photos" if pair.startswith("CP") else ("same_photo_genuine_control" if pair.startswith("GG") else "same_photo"),
                         photo_type=m["ptype"], side=m["side"], est_px_per_mm=est, px_mm_method=how,
                         image_url=m["url"], page_url=m["page"], crop_of=rid,
                         sha256=hashlib.sha256(open(cp, "rb").read()).hexdigest(), downloaded=True))
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, keys); wr.writeheader(); wr.writerows(rows)
    json.dump({"note": "OUTSIDE TEST SET ONLY - never train/tune on it. Labels as stated by source pages. px/mm are estimates.",
               "pages": P, "rows": rows}, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    lab = [r for r in rows if r["label"] in ("GENUINE", "FAKE")]
    sp = sorted({r["pair_id"] for r in rows if r["pair_kind"] == "same_photo"})
    print(f"raw downloaded {sum(m['ok'] for m in rawmeta.values())}/{len(rawmeta)}; manifest rows {len(rows)}; "
          f"labelled GENUINE/FAKE {len(lab)} (G {sum(r['label']=='GENUINE' for r in lab)} / F {sum(r['label']=='FAKE' for r in lab)}); "
          f"same-photo pairs {len(sp)}; same-session pairs {len(SESSION_PAIRS)}")


if __name__ == "__main__":
    main()
