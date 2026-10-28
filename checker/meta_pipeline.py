#!/usr/bin/env python3
"""
Meta / Baseten / SAM implementation, PLAYGROUND ONLY, Oct 27, 2026.
Implements every use in ~/workspace/fake-check/meta-baseten-sam-uses-2026-10-27.md
(A1-A8, B9-B10, C11-C12, D13-D17, E18-E24, F25-F27) as functions, NOT as a
release. No live demo change, no Play submission, no publishing, no sending.

Guardrails, enforced in code, not just comments:
- SAM segments only. It NEVER authenticates, grades, or identifies a card.
  authenticate_card() and grade_card() refuse, by design.
- A verdict is NEVER changed by a model explanation. Verdict comes from
  Tells v2 measurements (local, $0) or stays Inconclusive. Spark/Baseten
  text is explanation only, and must trace to supplied measurements.
- Identity: the printed card number wins over any model suggestion.
  identity_check() returns the printed number, with the suggestion recorded.
- No sensitive material is sent in these tests: test inputs are measurements,
  anonymised comments, and playground card crops already on file. No names,
  addresses, keys, payment data, or other people's cards.
- No ML training on model outputs. Using SAM crops to calibrate local
  thresholds in test is calibration, not training a model on outputs.
- Every paid call is appended to call_log.jsonl with model, use, tokens
  or images, and a cost estimate. Meta $150 credits and Baseten $100 are
  already granted; SAM is $0.0025/call on record. A use with no log entry
  is not counted as tested.

Cost estimates are LOG ESTIMATES, not billing dashboards:
- Baseten: input $1.25/1M tokens, output $4.25/1M tokens (plan, Oct 27).
- Muse Image: ~$0.01/image on record (Meta credits, not cash here).
- SAM: $0.0025/call on record.
- Meta Spark: Meta $150 free credits; token usage recorded if returned,
  cash cost recorded as 0.0 with source "meta-free-credit" (billing is on
  dev.meta.ai/billing, not in the API response).

Verified request forms (Oct 26, connector docs):
- Meta Spark: POST https://api.meta.ai/v1/messages, model muse-spark-1.3,
  max_tokens 4000 (a 20-token limit returned no visible text in Oct 26).
- Baseten: POST https://inference.baseten.co/v1/chat/completions,
  model meta-models/muse-spark-open-1026, OpenAI-compatible.
- Muse Image: POST https://api.meta.ai/v1/images/generations,
  model muse-image-1.0, b64_json PNG, checked for PNG header.
- SAM: POST https://api.meta.ai/v1/responses, model sam-3.1, short noun
  phrase "trading card" (a long instructional prompt returned empty
  output in Oct 26, so long prompts are NOT used).
- Muse Voice Transcribe: model muse-voice-transcribe-1.0 is listed in
  the model list, but its audio endpoint was NOT verified before this
  job. transcribe_note() probes ONE endpoint form and, if it fails,
  falls back to a $0 text-note path and records the probe as BLOCKED.
  It does not grind retries.
- Muse Wonder: model muse-wonder-1.0 is listed; wonder_audit() tries
  it via the messages endpoint once and records success or failure.
"""
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)
LOG_PATH = os.path.join(OUT, "call_log.jsonl")

DISCLAIMER = ("Estimate only, never official, never guaranteed. "
              "SAM segments only; it does not authenticate or grade a card.")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused")


def _log(model, use, cost, source, detail=None):
    entry = {"model": model, "use": use, "cost_usd_estimate": round(float(cost), 6),
             "source": source, "detail": detail or {}}
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def _meta_request(url, body):
    """Meta API via stored connection (surrogate), redirects disabled."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
    from dynamic_credentials import add_surrogate_to_request
    add_surrogate_to_request(req, "custom.meta-model-api", allowed_hosts=["api.meta.ai"])
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def _collect_text(obj, out):
    if isinstance(obj, dict):
        if obj.get("type") in ("thinking", "redacted_thinking"):
            return
        for k in ("output_text", "text"):
            if isinstance(obj.get(k), str) and obj[k].strip():
                out.append(obj[k])
        for v in obj.values():
            _collect_text(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_text(v, out)


def _parse_box(text, img_w, img_h):
    m = re.search(r"<\|box;(\d+),(\d+),(\d+),(\d+)\|>", text)
    if not m:
        m = re.search(r"x1\s*=\s*(\d+).*?y1\s*=\s*(\d+).*?x2\s*=\s*(\d+).*?y2\s*=\s*(\d+)", text, re.S)
    if not m:
        return None
    x1, y1, x2, y2 = (int(v) for v in m.groups())
    x1, y1 = max(0, min(x1, img_w - 1)), max(0, min(y1, img_h - 1))
    x2, y2 = max(x1 + 1, min(x2, img_w)), max(y1 + 1, min(y2, img_h))
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": img_w, "h": img_h}


def meta_spark(prompt, use):
    """A1-A8 Meta path. Returns (text, usage_dict) or ('', error)."""
    try:
        resp = _meta_request("https://api.meta.ai/v1/messages", {
            "model": "muse-spark-1.3",
            "messages": [{"role": "user", "content": prompt}], "max_tokens": 4000})
        texts = []
        _collect_text(resp, texts)
        text = "\n".join(texts).strip()
        usage = resp.get("usage", {}) if isinstance(resp, dict) else {}
        _log("muse-spark-1.3", use, 0.0, "meta-free-credit",
             {"chars": len(text), "usage": usage})
        return text, usage
    except Exception as e:
        _log("muse-spark-1.3", use + ":FAILED", 0.0, "meta-free-credit",
             {"error": str(e)[:300]})
        return "", {"error": str(e)[:300]}


def baseten_chat(prompt, use, max_tokens=1000):
    """D13 draft-first path. Returns (text, usage) or ('', error)."""
    try:
        body = json.dumps({"model": "meta-models/muse-spark-open-1026",
                           "messages": [{"role": "user", "content": prompt}],
                           "max_tokens": max_tokens}).encode()
        req = urllib.request.Request("https://inference.baseten.co/v1/chat/completions",
                                     data=body, headers={"Content-Type": "application/json"}, method="POST")
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import add_surrogate_to_request, read_json_response
        add_surrogate_to_request(req, "custom.baseten", allowed_hosts=["inference.baseten.co"])
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=120) as resp:
            data = read_json_response(resp)
        text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {}) or {}
        inp = usage.get("prompt_tokens", 0) or 0
        outp = usage.get("completion_tokens", 0) or 0
        cost = inp * 1.25 / 1_000_000 + outp * 4.25 / 1_000_000
        _log("meta-models/muse-spark-open-1026", use, cost, "baseten-granted",
             {"chars": len(text), "usage": usage})
        return text, usage
    except Exception as e:
        _log("meta-models/muse-spark-open-1026", use + ":FAILED", 0.0, "baseten-granted",
             {"error": str(e)[:300]})
        return "", {"error": str(e)[:300]}


def draft_first(prompt, use, max_tokens=1000):
    """D13/D16: Baseten draft first; Meta Spark only if Baseten is empty.
    Fix 2026-10-27: Baseten intermittently returns content=None (see
    run_demo log); an empty draft must fall back, never an empty verdict
    explanation. Triage prompts use max_tokens=2000 (1000 truncated A8)."""
    text, usage = baseten_chat(prompt, use + ":baseten-draft", max_tokens=max_tokens)
    if text:
        return text, "baseten-spark-open"
    text2, _ = meta_spark(prompt, use + ":meta-fallback")
    return text2, "meta-spark-1.3-fallback" if text2 else "none"


# ---- A. Meta Spark uses (all via draft_first unless noted) ----
def verdict_reasoning(tells, verdict, identity):
    """A1: structured tells-by-tell reasoning, measurements only."""
    prompt = ("Explain this card-check result in plain words for a collector, "
              "using ONLY these supplied facts. Do not invent tells, measurements, "
              "or a card identity not in the facts. Say plainly if the verdict is "
              f"Inconclusive and what would help next. Facts: identity={identity}, "
              f"verdict={verdict}, tells={json.dumps(tells)}. "
              "Format: one line per tell measured, then one verdict line.")
    text, source = draft_first(prompt, "A1-verdict-reasoning")
    return {"use": "A1", "verdict_unchanged": verdict, "source": source,
            "text": text, "disclaimer": DISCLAIMER}


def second_opinion(tells, verdict):
    """A2: Spark second opinion; code NEVER changes the verdict."""
    prompt = ("Second opinion only, on supplied Tells v2 measurements. Do not "
              "change the verdict, do not authenticate the card, do not invent "
              f"tells. Measurements: {json.dumps(tells)}. Current verdict: {verdict}. "
              "List any measurement that looks inconsistent, or say none.")
    text, source = draft_first(prompt, "A2-second-opinion")
    return {"use": "A2", "verdict_unchanged": verdict, "source": source, "text": text}


def tester_feedback_summary(comments):
    """A3/D15: anonymised comments only; no names, no photos in input."""
    prompt = ("Summarise these ANONYMISED tester comments in three groups: "
              "what confused testers, what broke, what to cut. Do not invent "
              f"comments. Comments: {json.dumps(comments)}")
    text, source = draft_first(prompt, "A3-tester-feedback-summary")
    return {"use": "A3", "source": source, "text": text}


def photo_quality_coach(measurements):
    """A4: one short retake line from measurements; local template if model fails."""
    prompt = ("Write ONE short retake line for a card photo, from these "
              "measurements only. Do not invent a verdict. "
              f"Measurements: {json.dumps(measurements)}")
    text, source = draft_first(prompt, "A4-photo-quality-coach")
    if not text:
        text = ("Retake flat, card filling the frame, even light, portrait "
                "for a portrait card, no fingers or carpet in frame.")
        source = "local-template-$0"
    return {"use": "A4", "source": source, "text": text}


def back_consistency_note(front_meas, back_meas):
    """A5: if no back, the honest line, no model call needed for that line."""
    if back_meas is None:
        return {"use": "A5", "source": "local-$0",
                "text": "No back photo supplied — front-only verdict. A back photo would "
                        "have helped if it disagreed with the front."}
    prompt = ("Write a one-line front-vs-back consistency note from these "
              "measurements only. Say plainly if they disagree. "
              f"Front: {json.dumps(front_meas)}. Back: {json.dumps(back_meas)}.")
    text, source = draft_first(prompt, "A5-back-consistency")
    return {"use": "A5", "source": source, "text": text}


def community_post_draft(facts):
    """A6/D15: DRAFT only; human approval required before any post."""
    prompt = ("Draft one short, varied, rules-first community post from these "
              "facts only. No links, no app pitch unless the facts say so, "
              "no invented claims. Facts: " + json.dumps(facts))
    text, source = draft_first(prompt, "A6-community-post-draft")
    return {"use": "A6", "status": "DRAFT-ONLY-human-approval-required",
            "source": source, "text": text}


def identity_check(printed_number, model_suggestion):
    """A7: printed number wins, always. Suggestion is recorded, never used."""
    return {"use": "A7", "identity_used": printed_number,
            "model_suggestion_recorded_only": model_suggestion,
            "rule": "printed card number beats model suggestion"}


def identity_suggestion(crop_note):
    """A7 helper: Spark suggestion, to be checked against the printed number."""
    prompt = ("Suggest a card identity from this note only, as a SUGGESTION. "
              "Do not authenticate. Note: " + crop_note)
    text, source = draft_first(prompt, "A7-identity-suggestion")
    return {"use": "A7-suggestion", "source": source, "text": text}


def edge_case_triage(inconclusive_list):
    """A8: group Inconclusive checks by reason, internal tool."""
    prompt = ("Group these Inconclusive checks by reason (bad photo, no "
              "reference, back missing, slab glare, other) and say which "
              f"group to fix first. Checks: {json.dumps(inconclusive_list)}")
    text, source = draft_first(prompt, "A8-edge-case-triage", max_tokens=2000)
    return {"use": "A8", "source": source, "text": text}


def demo_script_beats(measurements, verdict):
    """A2/demo: Spark writes 20-40s plain-words script per beat, measurements only."""
    prompt = ("Write a short demo-video script beat (20-40 seconds spoken) "
              "from these measurements only. Do not invent tells. "
              f"Measurements: {json.dumps(measurements)}. Verdict: {verdict}.")
    text, source = draft_first(prompt, "demo-script-beat")
    return {"use": "demo-script", "source": source, "text": text}


# ---- B. Muse Image ----
def muse_image(prompt, out_name, use):
    """B9/B10: art only, never a card photo, never a real/fake card."""
    try:
        resp = _meta_request("https://api.meta.ai/v1/images/generations", {
            "model": "muse-image-1.0", "prompt": prompt, "n": 1,
            "size": "1024x1024", "output_format": "png", "response_format": "b64_json"})
        items = resp.get("data", [])
        if items and items[0].get("b64_json"):
            data = base64.b64decode(items[0]["b64_json"])
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                path = os.path.join(OUT, out_name)
                with open(path, "wb") as f:
                    f.write(data)
                _log("muse-image-1.0", use, 0.01, "meta-free-credit",
                     {"bytes": len(data), "file": out_name})
                return {"use": use, "file": out_name, "bytes": len(data), "ok": True}
        _log("muse-image-1.0", use + ":FAILED", 0.01, "meta-free-credit",
             {"error": "no usable PNG returned"})
        return {"use": use, "ok": False, "error": "no usable PNG returned"}
    except Exception as e:
        _log("muse-image-1.0", use + ":FAILED", 0.0, "meta-free-credit",
             {"error": str(e)[:300]})
        return {"use": use, "ok": False, "error": str(e)[:300]}


# ---- C. Voice + Wonder ----
def transcribe_note(text_note):
    """C11: $0 text-note path (works), plus ONE probe of the audio endpoint.
    The probe is recorded honestly; if it fails, the use is BLOCKED for audio
    and the text path is the implemented path. No real user audio is used."""
    result = {"use": "C11", "text_note_path": text_note, "text_path_ok": True}
    # One probe only, silent WAV, multipart guess at an OpenAI-style endpoint.
    try:
        import wave, io
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 1600)
        boundary = "----musepipeline"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n"
                "muse-voice-transcribe-1.0\r\n"
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"note.wav\"\r\n"
                "Content-Type: audio/wav\r\n\r\n").encode() + buf.getvalue() + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request("https://api.meta.ai/v1/audio/transcriptions",
                                     data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                                     method="POST")
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import add_surrogate_to_request
        add_surrogate_to_request(req, "custom.meta-model-api", allowed_hosts=["api.meta.ai"])
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        result["audio_probe"] = {"ok": True, "response": str(data)[:300]}
        _log("muse-voice-transcribe-1.0", "C11-audio-probe", 0.0, "meta-free-credit",
             {"ok": True})
    except Exception as e:
        result["audio_probe"] = {"ok": False, "error": str(e)[:300],
                                 "status": "BLOCKED-audio-endpoint-not-verified"}
        _log("muse-voice-transcribe-1.0", "C11-audio-probe:FAILED", 0.0,
             "meta-free-credit", {"error": str(e)[:300]})
    return result


def wonder_audit(trace_text):
    """C12: Wonder audits a Spark trace for invented tells. One attempt."""
    try:
        resp = _meta_request("https://api.meta.ai/v1/messages", {
            "model": "muse-wonder-1.0",
            "messages": [{"role": "user", "content": (
                "Audit this reasoning trace. Flag any tell, measurement, or "
                "identity that is NOT in the supplied facts. Do not add new "
                f"tells. Trace: {trace_text}")}], "max_tokens": 4000})
        texts = []
        _collect_text(resp, texts)
        text = "\n".join(texts).strip()
        _log("muse-wonder-1.0", "C12-wonder-audit", 0.0, "meta-free-credit",
             {"chars": len(text)})
        return {"use": "C12", "ok": bool(text), "text": text}
    except Exception as e:
        _log("muse-wonder-1.0", "C12-wonder-audit:FAILED", 0.0, "meta-free-credit",
             {"error": str(e)[:300]})
        return {"use": "C12", "ok": False, "error": str(e)[:300]}


# ---- D. Baseten batch ----
def batch_calibration_narration(tells_results):
    """D14/D17: Baseten per card, templated, Meta fallback on empty draft.
    Fix 2026-10-27: the first run left one card's narration empty on a
    Baseten content=None failure, with no fallback. That must not happen
    in a batch summary."""
    out = []
    for r in tells_results:
        prompt = ("Write one short summary for this card's Tells v2 scores, "
                  "in the same template: strong mismatches, matches, verdict. "
                  "Do not invent tells. Scores: " + json.dumps(r))
        text, source = draft_first(prompt, "D14-batch-calibration-narration")
        out.append({"card": r.get("card"), "narration": text, "source": source})
    return {"use": "D14", "n": len(out), "results": out}


# ---- E. SAM ----
def sam_box(image_path, phrase="trading card"):
    """E18-E21 core: one SAM call, verified short-phrase form. $0.0025/call."""
    from PIL import Image
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    with Image.open(image_path) as im:
        img_w, img_h = im.size
    try:
        resp = _meta_request("https://api.meta.ai/v1/responses", {
            "model": "sam-3.1",
            "input": [{"role": "user", "content": [
                {"type": "input_text", "text": phrase},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"}]}]})
        texts = []
        _collect_text(resp, texts)
        box = _parse_box("\n".join(texts), img_w, img_h)
        _log("sam-3.1", "SAM-box", 0.0025, "meta-sam-per-call",
             {"image": os.path.basename(image_path), "box": box})
        return box
    except Exception as e:
        _log("sam-3.1", "SAM-box:FAILED", 0.0025, "meta-sam-per-call",
             {"error": str(e)[:300]})
        return None


def crop_to(image_path, box, out_name):
    from PIL import Image
    with Image.open(image_path) as im:
        im.crop((box["x1"], box["y1"], box["x2"], box["y2"])).save(os.path.join(OUT, out_name))
    return out_name


def region_split(crop_path):
    """E21 region prep, $0 Pillow: art window = top portion, textbox = rest.
    This is a HEURISTIC split by proportion, not a measured ground-truth
    layout. It is labelled as such wherever it is used."""
    from PIL import Image
    with Image.open(crop_path) as im:
        w, h = im.size
        im.crop((0, 0, w, int(h * 0.48))).save(os.path.join(OUT, "art-window.png"))
        im.crop((0, int(h * 0.48), w, h)).save(os.path.join(OUT, "textbox.png"))
    return {"use": "E21-region-split", "method": "heuristic-proportion-48pct",
            "note": "Not a measured layout; art/textbox boundary varies by set.",
            "files": ["art-window.png", "textbox.png"]}


def photo_quality_from_box(box, ref_aspect):
    """E23: box aspect vs reference aspect, $0. Bad crop is a photo signal,
    never a Counterfeit verdict on its own."""
    if not box:
        return {"use": "E23", "signal": "no-box-photo-rejected"}
    aspect = (box["x2"] - box["x1"]) / max(1, (box["y2"] - box["y1"]))
    ok = abs(aspect - ref_aspect) <= 0.15
    return {"use": "E23", "box_aspect": round(aspect, 3), "ref_aspect": round(ref_aspect, 3),
            "aspect_ok": ok, "signal": "ok" if ok else "retake-bad-crop-aspect"}


def authenticate_card(*_a, **_k):
    """E24: REFUSED, by design. SAM segments; it does not authenticate."""
    raise NotImplementedError("SAM must not be asked to authenticate a card.")


def grade_card(*_a, **_k):
    """E24: REFUSED, by design. No grade guarantee, ever."""
    raise NotImplementedError("SAM must not be asked to grade a card.")


# ---- F. Combined pipelines ----
def cheap_check(tells, verdict, identity):
    """F25: local tells ($0) -> Baseten draft -> Meta only if Baseten fails.
    Verdict is the tells verdict, unchanged."""
    exp = verdict_reasoning(tells, verdict, identity)
    return {"pipeline": "F25-cheap-check", "verdict": verdict, "verdict_source": "tells-v2-local",
            "explanation_source": exp["source"], "explanation": exp["text"],
            "sam_calls": 0, "disclaimer": DISCLAIMER}


def test_check(sam_crop_path, tells, verdict, identity):
    """F26: SAM-heavy TEST pipeline only. NOT the final-app cost model."""
    exp = verdict_reasoning(tells, verdict, identity)
    script = demo_script_beats(tells, verdict)
    return {"pipeline": "F26-test-check", "verdict": verdict, "sam_crop": sam_crop_path,
            "explanation_source": exp["source"], "demo_script": script["text"],
            "note": "Test-only SAM-heavy pipeline; do not quote as final-app cost."}


def demo_check(sam_crop_path, tells, verdict, identity):
    """F27: one SAM crop -> tells on screen -> Spark verdict -> Image title card."""
    exp = verdict_reasoning(tells, verdict, identity)
    art = muse_image("A simple Pokemon card checker demo title card, flat illustration, "
                     "a gold cauldron and a magnifier, plain background, no real card, no text",
                     "demo-title-card.png", "F27-demo-title-card")
    return {"pipeline": "F27-demo-check", "verdict": verdict, "sam_crop": sam_crop_path,
            "explanation": exp["text"], "title_card": art,
            "disclaimer": DISCLAIMER}
