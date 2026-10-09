"""
ElderShield — Unfamiliar Evaluation Runner (Independent Test Set)
Executes frozen production detector across the 112-sample unfamiliar evaluation set.
Records baseline metrics, confusion matrix, category/language breakdowns,
and details of every false positive and false negative.
"""

import os
import sys
import json
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from engine.analyzer import engine, parse_raw_transcript
from tests.unfamiliar_evaluation_dataset import UNFAMILIAR_EVALUATION_SAMPLES

def run_unfamiliar_evaluation(tag: str = "BASELINE"):
    total_samples = len(UNFAMILIAR_EVALUATION_SAMPLES)
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    category_results = defaultdict(lambda: {"total": 0, "correct": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0})
    language_results = defaultdict(lambda: {"total": 0, "correct": 0})
    failures = []

    print("=" * 88)
    print(f"ELDERSHIELD — UNFAMILIAR CONVERSATION EVALUATION [{tag}]")
    print("=" * 88)
    print(f"Total Evaluation Samples: {total_samples}")
    print("Provenance: Independent Synthetic Stress-Tests + Public Advisory Case Patterns")
    print("-" * 88)

    for sample in UNFAMILIAR_EVALUATION_SAMPLES:
        sid = sample["id"]
        cat = sample["category"]
        lang = sample["language"]
        ground_truth = sample["ground_truth"]
        transcript = sample["transcript"]

        turns = parse_raw_transcript(transcript)
        assessment = engine.analyze(turns=turns, raw_transcript=transcript)

        predicted_level = assessment.risk_level
        predicted_decision = assessment.decision
        
        # Predicted Class:
        # SCAM: decision is BLOCK or level is HIGH_RISK
        # SAFE: decision is ALLOW or level is LOW_RISK
        # INSUFFICIENT_EVIDENCE: insufficient_evidence is True or level is INSUFFICIENT_EVIDENCE or decision is INCONCLUSIVE
        if predicted_decision == "BLOCK" or predicted_level == "HIGH_RISK":
            predicted_class = "SCAM"
        elif assessment.insufficient_evidence or predicted_level == "INSUFFICIENT_EVIDENCE" or predicted_decision == "INCONCLUSIVE":
            predicted_class = "INSUFFICIENT_EVIDENCE"
        else:
            predicted_class = "SAFE"

        category_results[cat]["total"] += 1
        language_results[lang]["total"] += 1

        is_correct = False
        if ground_truth == "SCAM":
            if predicted_class == "SCAM":
                tp += 1
                category_results[cat]["tp"] += 1
                category_results[cat]["correct"] += 1
                language_results[lang]["correct"] += 1
                is_correct = True
            else:
                fn += 1
                category_results[cat]["fn"] += 1
                failures.append({
                    "id": sid,
                    "category": cat,
                    "language": lang,
                    "error_type": "FALSE_NEGATIVE (Missed Scam)",
                    "ground_truth": ground_truth,
                    "predicted_class": predicted_class,
                    "predicted_level": predicted_level,
                    "predicted_decision": predicted_decision,
                    "risk_score": assessment.risk_score,
                    "transcript": transcript,
                    "reasons": assessment.reasons
                })
        else:
            # Ground truth is SAFE or INSUFFICIENT_EVIDENCE (Non-Scam)
            if predicted_class == "SCAM":
                fp += 1
                category_results[cat]["fp"] += 1
                failures.append({
                    "id": sid,
                    "category": cat,
                    "language": lang,
                    "error_type": "FALSE_POSITIVE (Legitimate Flagged as Scam)",
                    "ground_truth": ground_truth,
                    "predicted_class": predicted_class,
                    "predicted_level": predicted_level,
                    "predicted_decision": predicted_decision,
                    "risk_score": assessment.risk_score,
                    "transcript": transcript,
                    "reasons": assessment.reasons
                })
            else:
                # Correct non-scam handling (either allowed or deferred as insufficient)
                tn += 1
                category_results[cat]["tn"] += 1
                category_results[cat]["correct"] += 1
                language_results[lang]["correct"] += 1
                is_correct = True

        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] {sid:30} | {cat:30} | GT: {ground_truth:10} -> Pred: {predicted_class:10} (Score: {assessment.risk_score:.1f}, {predicted_level})")

    # Metrics calculation
    precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = (fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0
    fnr = (fn / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0

    print("\n" + "=" * 88)
    print(f"DETECTION ACCURACY & SAFETY METRICS [{tag}]:")
    print("=" * 88)
    print(f"  • True Positives (TP) : {tp:3d}  (Scams correctly blocked)")
    print(f"  • True Negatives (TN) : {tn:3d}  (Safe & ambiguous dialogues allowed/deferred)")
    print(f"  • False Positives (FP): {fp:3d}  (Safe calls wrongly blocked as scams)")
    print(f"  • False Negatives (FN): {fn:3d}  (Scams missed)")
    print("-" * 88)
    print(f"  • Precision           : {precision:6.2f}%")
    print(f"  • Recall (Sensitivity): {recall:6.2f}%")
    print(f"  • F1 Score            : {f1:6.2f}%")
    print(f"  • False-Positive Rate : {fpr:6.2f}%  [Formula: FP / (FP + TN)]")
    print(f"  • False-Negative Rate : {fnr:6.2f}%  [Formula: FN / (TP + FN)]")

    print("\nCONFUSION MATRIX:")
    print("                      Predicted Non-Scam    Predicted Scam")
    print(f"Actual Non-Scam:            {tn:3d}                   {fp:3d}  (Total: {tn+fp})")
    print(f"Actual Scam:                {fn:3d}                   {tp:3d}  (Total: {fn+tp})")

    print("\nBREAKDOWN BY SCENARIO CATEGORY:")
    for cat, data in sorted(category_results.items()):
        pct = (data["correct"] / data["total"]) * 100.0 if data["total"] > 0 else 0.0
        print(f"  • {cat:32}: {data['correct']:2d}/{data['total']:2d} passed ({pct:5.1f}%) [TP:{data['tp']} TN:{data['tn']} FP:{data['fp']} FN:{data['fn']}]")

    print("\nBREAKDOWN BY LANGUAGE / SCRIPT:")
    for lang, data in sorted(language_results.items()):
        pct = (data["correct"] / data["total"]) * 100.0 if data["total"] > 0 else 0.0
        print(f"  • {lang:32}: {data['correct']:2d}/{data['total']:2d} passed ({pct:5.1f}%)")

    print(f"\nTOTAL DEFECTS (FAILURES): {len(failures)}")
    for f in failures:
        print(f"  - [{f['error_type']}] ID: {f['id']} ({f['category']}, {f['language']})")
        print(f"    GT: {f['ground_truth']} -> Pred: {f['predicted_class']} (Score: {f['risk_score']}, Level: {f['predicted_level']})")
        print(f"    Transcript: {repr(f['transcript'][:120])}...")
        print(f"    Reasons: {f['reasons']}")
        print()

    return {
        "tag": tag,
        "total": total_samples,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "fnr": fnr,
        "failures": failures,
        "category_results": dict(category_results),
        "language_results": dict(language_results)
    }

if __name__ == "__main__":
    run_unfamiliar_evaluation(tag="BASELINE_FROZEN_DETECTOR")
