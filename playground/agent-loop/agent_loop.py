#!/usr/bin/env python3
"""
Agent loop prototype — Real or Replica One-Go Check v2 (playground only).

Loop: goal + state -> Spark-style decision -> tool -> observation -> repeat -> stop.
This file runs with MOCK tools by default, so it costs nothing and needs no key.
Swap a mock tool for a real one (SAM crop, pool compare, Spark explain) by
replacing its function — the loop itself does not change. That is the point:
the brain (Spark) decides, the code does, the state stays in code.

Stop conditions (hard, never optional):
  - verdict reached
  - same tool fails twice in a row
  - MAX_STEPS reached
  - user stop (KeyboardInterrupt)

Verdicts are always Likely Genuine / Likely Counterfeit / Inconclusive.
Never guaranteed, never official. No card photos, no keys in this file.
Built Oct 26, 2026 — hackathon period.
"""
import argparse
import json

MAX_STEPS = 5

# ---- Mock tools (stand-ins for SAM / pool / Spark, same shapes as real ones) ----
def tool_sam_crop(state):
    """Mock SAM crop: succeeds on first try for front, second try for back."""
    state["crop_attempts"] = state.get("crop_attempts", 0) + 1
    side = "back" if state.get("front_cropped") else "front"
    # Simulate one glare failure on the very first front crop, then success.
    if side == "front" and state["crop_attempts"] == 1:
        return {"ok": False, "error": "glare: no clean box"}
    state[side + "_cropped"] = True
    return {"ok": True, "box": [18, 16, 584, 813], "side": side}

def tool_compare_pool(state):
    """Mock pool comparison: front alone is inconclusive, front+back decides."""
    if state.get("front_cropped") and state.get("back_cropped"):
        return {"ok": True, "match": "Alakazam Base / BS 1", "score": 0.92}
    return {"ok": True, "match": None, "score": 0.45}

def tool_spark_explain(state, verdict):
    """Mock Spark plain-words explanation (real Spark call replaces this)."""
    if verdict == "Likely Genuine":
        return "Front and back both match the reference card, and the centering looks even. That points to Likely Genuine — an estimate, not an official grade."
    if verdict == "Likely Counterfeit":
        return "The front does not match the reference card on key details. That points to Likely Counterfeit — an estimate, not a guarantee."
    return "Front alone was not enough to decide, and no back photo was available in this run. That is Inconclusive — do not treat it as a pass or a fail."

# ---- Decision step (what Spark would do; here as a rule, so the loop is testable
#      without spending a Spark call — a real Spark call returns the same action JSON) ----
def decide(state):
    """Return (action, reason). Mirrors the action JSON Spark would return."""
    if not state.get("front_cropped"):
        return "sam_crop", "need a clean front crop first"
    cmp_ = state.get("last_compare")
    if cmp_ and cmp_.get("score", 0) >= 0.85:
        return "verdict_genuine", "front+back match is strong enough to stop"
    if state.get("front_cropped") and not state.get("back_cropped"):
        return "sam_crop", "front alone is inconclusive, get the back"
    if state.get("back_cropped"):
        return "verdict_inconclusive", "front+back still did not decide, stop honestly"
    return "compare_pool", "crop done, compare it"

def run_loop(verbose=True):
    state = {"goal": "verdict on one card", "front_cropped": False, "back_cropped": False}
    log = []
    verdict = None
    stop_reason = None
    consecutive_failures = 0

    for step in range(1, MAX_STEPS + 1):
        action, reason = decide(state)
        log.append({"step": step, "action": action, "reason": reason, "state_before": dict(state)})
        if verbose:
            print(f"Step {step}: {action} — {reason}")

        if action == "sam_crop":
            result = tool_sam_crop(state)
            if not result["ok"]:
                consecutive_failures += 1
                log[-1]["result"] = result
                if consecutive_failures >= 2:
                    verdict, stop_reason = "Inconclusive", "same tool failed twice, stop safely"
                    break
                continue
            consecutive_failures = 0
            log[-1]["result"] = result
            # After a crop, compare next step.
            state["last_compare"] = tool_compare_pool(state)
            log[-1]["compare"] = state["last_compare"]
            continue

        if action == "compare_pool":
            state["last_compare"] = tool_compare_pool(state)
            log[-1]["result"] = state["last_compare"]
            continue

        if action.startswith("verdict_"):
            verdict = {"verdict_genuine": "Likely Genuine",
                       "verdict_inconclusive": "Inconclusive"}.get(action, "Inconclusive")
            stop_reason = reason
            break

    if verdict is None:
        verdict, stop_reason = "Inconclusive", f"max steps ({MAX_STEPS}) reached, stop honestly"

    explanation = tool_spark_explain(state, verdict)
    out = {"verdict": verdict, "stop_reason": stop_reason, "explanation": explanation, "steps": log, "final_state": state}
    if verbose:
        print(f"\nVerdict: {verdict}")
        print(f"Stop: {stop_reason}")
        print(f"Explanation: {explanation}")
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    result = run_loop()
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Log written to {args.out}")
