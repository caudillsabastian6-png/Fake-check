"""Image matcher prototype — PLAYGROUND / TEST ONLY, Oct 28, 2026.

$0, Pillow + numpy only, no cv2, no model calls, no live deployment.
This is a perceptual-hash matcher, NOT a card recogniser: it measures
how similar two photos look, it does not name a card from pixels alone
and it never decides a verdict by itself.

Hashes implemented:
  - aHash: 8x8 mean threshold (64 bits).
  - dHash: 9x8 horizontal-gradient threshold (64 bits).
  - pHash: 32x32 greyscale -> 2-D DCT (numpy, separable cosine matrix)
    -> top-left 8x8 low frequencies, median threshold (64 bits).
    DCT is implemented here in ~30 lines; it is not a library call.

Preprocessing (deliberate, and a known limitation):
  - Two variants are hashed for every image: FULL (whole photo as
    supplied) and CENTRE (centre crop forced to the 5:7 card ratio,
    80% of the shorter side's span). Pool photos are hand photos of a
    card on a surface, NOT card-only crops, so a full-photo hash is
    dominated by background (leather, rug, hand). The centre crop is
    an approximation, not a card detector — it does not find the card,
    it assumes the card is roughly centred. A production matcher
    needs a real card crop (SAM or equivalent) before hashing.
  - Images are converted to greyscale; colour is deliberately ignored
    by all three hashes (a known weakness for colour tells).

Comparison: Hamming distance (bit differences) between 64-bit hashes.
Lower = more similar. pHash is the primary score; dHash is reported
alongside as a second opinion. A match is NEVER declared on one hash
alone in the threshold proposal — see THRESHOLD_PROPOSAL.md.

Penguin deployment warning (do not ignore): the live backend host is
stdlib-only Python with no pip, no Pillow and no numpy. This file
CANNOT run there as-is. Deployment options are in MULTIBACKEND_ROLES.md
(G1 after Oct 30, or a JS/WASM Worker, or a separate VM service).
Prototyping here does not make the live backend capable of matching.
"""

import os

import numpy as np
from PIL import Image

# Standalone fix (Oct 29, 2026): pool photos are card photos and are never
# shipped in this pack. Look in backend-matcher/fixtures/ first, then any
# dirs named in $FAKECHECK_POOL_DIRS (os.pathsep-separated), then the
# builder's workspace dirs (absent on a clean machine -> resolve_path
# returns None and the test SKIPs with the reason).
BASE_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"),
] + [d for d in os.environ.get("FAKECHECK_POOL_DIRS", "").split(os.pathsep) if d] + [
    os.path.expanduser("~/workspace/user/files"),
    os.path.expanduser("~/workspace/fake-check/fake-samples"),
]


def resolve_path(filename):
    """Find a pool file by basename across the known pool directories."""
    if not filename:
        return None
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename
    for d in BASE_DIRS:
        p = os.path.join(d, os.path.basename(filename))
        if os.path.exists(p):
            return p
    return None


def _grey_array(path, size, centre_crop=False):
    im = Image.open(path).convert("L")
    if centre_crop:
        w, h = im.size
        # Card ratio 5:7 (portrait). Take a centred window 80% of the
        # width and the matching height; clamp to the image bounds.
        cw = int(w * 0.80)
        ch = int(cw * 7 / 5)
        if ch > h:
            ch = h
            cw = int(ch * 5 / 7)
        left = (w - cw) // 2
        top = (h - ch) // 2
        im = im.crop((left, top, left + cw, top + ch))
    return np.asarray(im.resize(size, Image.LANCZOS), dtype=np.float64)


def ahash(path, centre_crop=False):
    a = _grey_array(path, (8, 8), centre_crop)
    bits = (a > a.mean()).flatten()
    return bits_to_int(bits)


def dhash(path, centre_crop=False):
    a = _grey_array(path, (9, 8), centre_crop)
    bits = (a[:, :-1] > a[:, 1:]).flatten()
    return bits_to_int(bits)


_DCT_CACHE = {}


def _dct_matrix(n):
    """Orthonormal DCT-II matrix (n x n), numpy only, cached."""
    if n in _DCT_CACHE:
        return _DCT_CACHE[n]
    m = np.zeros((n, n))
    for k in range(n):
        for i in range(n):
            m[k, i] = np.cos((2 * i + 1) * k * np.pi / (2 * n))
        m[k] *= np.sqrt(2.0 / n)
    m[0] *= 1.0 / np.sqrt(2.0)
    _DCT_CACHE[n] = m
    return m


def phash(path, centre_crop=False):
    a = _grey_array(path, (32, 32), centre_crop)
    d = _dct_matrix(32)
    coeffs = d @ a @ d.T
    low = coeffs[:8, :8].flatten()
    # Median excluding the DC term (index 0), standard pHash practice.
    med = np.median(np.delete(low, 0))
    bits = low > med
    return bits_to_int(bits)


def bits_to_int(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return v


def hamming(a, b):
    """Hamming distance between two 64-bit hash ints."""
    return bin(a ^ b).count("1")


def hash_image(path):
    """All three hashes, both variants, for one image path."""
    return {
        "full": {
            "ahash": ahash(path),
            "dhash": dhash(path),
            "phash": phash(path),
        },
        "centre": {
            "ahash": ahash(path, centre_crop=True),
            "dhash": dhash(path, centre_crop=True),
            "phash": phash(path, centre_crop=True),
        },
    }


def compare(h1, h2):
    """Distance dict between two hash_image() results."""
    out = {}
    for variant in ("full", "centre"):
        for kind in ("ahash", "dhash", "phash"):
            out["%s_%s" % (variant, kind)] = hamming(
                h1[variant][kind], h2[variant][kind]
            )
    return out


def rank_candidates(query_hashes, pool_hashes, top_n=5, variant="centre",
                    kind="phash"):
    """Rank pool entries by Hamming distance to the query.

    pool_hashes: list of (label, hash_image() result).
    Returns [(label, distance, dhash_distance), ...] sorted ascending.
    Ranking is a candidate list, NOT an identification: the caller must
    still check set + printed number first (see THRESHOLD_PROPOSAL.md).
    """
    scored = []
    for label, h in pool_hashes:
        d = hamming(query_hashes[variant][kind], h[variant][kind])
        d2 = hamming(query_hashes[variant]["dhash"], h[variant]["dhash"])
        scored.append((label, d, d2))
    scored.sort(key=lambda t: (t[1], t[2]))
    return scored[:top_n]
