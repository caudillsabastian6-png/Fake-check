"""Test the matcher against pool v2 — PLAYGROUND, Oct 28, 2026.

Test sets (all from verification_pool_v2.csv, files on disk):
  A. Sanity: same file vs itself -> distance must be 0 on every hash.
  B. Robustness: same file resized to 50% and re-encoded JPEG q70 ->
     distance should stay small (perceptual hashes must survive this).
  C. Same-identity: A1 identities with 2 distinct front files
     (Yveltal 019/025, Switch 183/202, Hop 165/202) -> 3 pairs.
     NOTE: these are distinct photos of the same identity, NOT proven
     re-photographs of the same physical card, so this is an upper
     bound on "same card" distance, not a clean same-card measure.
  D. Impostors: random cross-identity A1 front pairs (different cards).
  E. Fake vs genuine: each B fake front (40) vs its nearest A1 genuine
     front by centre-pHash, and vs a random A1 front.
  F. Backs: A1 genuine back vs genuine back (uniform design — expect
     very low distances, which PROVES a back alone cannot prove identity).
  G. Nearest-neighbour separation: each A1 front vs its nearest OTHER
     A1 front (excluding its same-identity twin).

Output: JSON summary + CSV of pair distances, printed honestly.
Nothing here approves a threshold; see THRESHOLD_PROPOSAL.md.
"""

import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matcher import (  # noqa: E402
    compare, hash_image, hamming, resolve_path,
)

from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.expanduser(
    "~/workspace/fake-check/playground/verification-pool-2026-10-28"
    "/verification_pool_v2.csv"
)
TMP = os.path.join(HERE, "tmp")
os.makedirs(TMP, exist_ok=True)


def load():
    rows = list(csv.DictReader(open(POOL)))
    a1 = [r for r in rows if r["tier"] == "A1-verified-identity-confirmed"]
    fake = [r for r in rows if r["tier"] in (
        "B-fake-owner-confirmed", "B-fake-anchor")]
    return a1, fake


def stats(vals):
    if not vals:
        return {}
    s = sorted(vals)
    n = len(s)
    return {
        "n": n,
        "min": s[0],
        "p25": s[n // 4],
        "median": s[n // 2],
        "p75": s[(3 * n) // 4],
        "max": s[-1],
        "mean": round(sum(s) / n, 2),
    }


def main():
    a1, fake = load()
    a1_fronts = []
    for r in a1:
        p = resolve_path(r["front_file"])
        if p:
            a1_fronts.append((r, p))
    a1_backs = []
    for r in a1:
        p = resolve_path(r["back_file"])
        if p:
            a1_backs.append((r, p))
    fake_fronts = []
    for r in fake:
        p = resolve_path(r["front_file"])
        if p:
            fake_fronts.append((r, p))

    print("A1 fronts hashed:", len(a1_fronts), "| A1 backs:", len(a1_backs),
          "| fake fronts:", len(fake_fronts))

    hashes_front = {r["front_file"]: hash_image(p) for r, p in a1_fronts}
    hashes_back = {r["back_file"]: hash_image(p) for r, p in a1_backs}
    hashes_fake = {r["front_file"]: hash_image(p) for r, p in fake_fronts}

    out = {}

    # A. Sanity
    r0, p0 = a1_fronts[0]
    h0 = hashes_front[r0["front_file"]]
    out["A_sanity_same_file"] = compare(h0, h0)

    # B. Robustness: resize + re-encode
    im = Image.open(p0)
    small = os.path.join(TMP, "robust.jpg")
    im.resize((im.width // 2, im.height // 2)).save(small, "JPEG", quality=70)
    out["B_robust_resize_reencode"] = compare(h0, hash_image(small))

    # C. Same-identity pairs
    from collections import defaultdict
    by_id = defaultdict(list)
    for r, p in a1_fronts:
        by_id[(r["card_name"], r["number"])].append(r)
    same_pairs = []
    for key, rs in by_id.items():
        if len(rs) == 2:
            h1 = hashes_front[rs[0]["front_file"]]
            h2 = hashes_front[rs[1]["front_file"]]
            same_pairs.append({"identity": "%s %s" % key,
                               **compare(h1, h2)})
    out["C_same_identity_pairs"] = same_pairs

    # D. Impostors: fixed-seed random cross-identity pairs
    random.seed(28)
    impostor = []
    for _ in range(60):
        r1, r2 = random.sample(a1_fronts, 2)
        if (r1[0]["card_name"], r1[0]["number"]) == (
                r2[0]["card_name"], r2[0]["number"]):
            continue
        impostor.append(compare(hashes_front[r1[0]["front_file"]],
                                hashes_front[r2[0]["front_file"]]))
    out["D_impostor_stats"] = {
        k: stats([d[k] for d in impostor]) for k in impostor[0]
    }

    # E. Fake vs genuine
    fake_nearest, fake_random = [], []
    rng = random.Random(29)
    for r, p in fake_fronts:
        hf = hashes_fake[r["front_file"]]
        dists = [compare(hf, hashes_front[fr["front_file"]])["centre_phash"]
                 for fr, _ in a1_fronts]
        fake_nearest.append(min(dists))
        fake_random.append(rng.choice(dists))
    out["E_fake_vs_genuine_nearest_centre_phash"] = stats(fake_nearest)
    out["E_fake_vs_genuine_random_centre_phash"] = stats(fake_random)

    # F. Backs vs backs
    back_pairs = []
    for i in range(0, min(40, len(a1_backs) - 1), 2):
        h1 = hashes_back[a1_backs[i][0]["back_file"]]
        h2 = hashes_back[a1_backs[i + 1][0]["back_file"]]
        back_pairs.append(compare(h1, h2))
    out["F_genuine_back_vs_back_stats"] = {
        k: stats([d[k] for d in back_pairs]) for k in back_pairs[0]
    }

    # G. Nearest-neighbour separation (centre pHash)
    nn = []
    for r, p in a1_fronts:
        h = hashes_front[r["front_file"]]
        best = None
        for r2, p2 in a1_fronts:
            if r2["front_file"] == r["front_file"]:
                continue
            d = hamming(h["centre"]["phash"],
                        hashes_front[r2["front_file"]]["centre"]["phash"])
            if best is None or d < best:
                best = d
        nn.append(best)
    out["G_nearest_other_A1_centre_phash"] = stats(nn)

    with open(os.path.join(HERE, "test_results.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
