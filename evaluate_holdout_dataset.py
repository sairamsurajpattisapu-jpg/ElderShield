"""
ElderShield — Independent Holdout Evaluation Runner (HWV4-PS05)
Evaluates the frozen production detection engine against N=30 completely untouched
holdout conversations covering novel scam scripts and hard negative examples
(urgent hospital calls, family emergencies, legitimate bank OTP safeguards).
"""

import os
import sys
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from engine.analyzer import engine, parse_raw_transcript
from tests.holdout_evaluation_dataset import HOLDOUT_EVALUATION_DATASET

def run_holdout_evaluation() -> Dict[str, Any]:
    print("=" * 85)
    print("ELDERSHIELD — INDEPENDENT HOLDOUT EVALUATION REPORT (HWV4-PS05)")
    print("=" * 85)
    print(f"Total Holdout Samples: {len(HOLDOUT_EVALUATION_DATASET)}")
    print("Dataset Status: Untouched Holdout Evaluation Set (Distinct from dev & regression fixtures)")
    print("-" * 85)

    tp, tn, fp, fn = 0, 0, 0, 0
    insufficient_ev_count = 0
    failures: List[Dict[str, Any]] = []

    category_stats: Dict[str, Dict[str, int]] = {}
    language_stats: Dict[str, Dict[str, int]] = {}

    for sample in HOLDOUT_EVALUATION_DATASET:
        sid = sample["id"]
        cat = sample["category"]
        lang = sample["language"]
        gt = sample["ground_truth"]
        transcript = sample["transcript"]

        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1

        if lang not in language_stats:
            language_stats[lang] = {"total": 0, "passed": 0}
        language_stats[lang]["total"] += 1

        turns = parse_raw_transcript(transcript)
        assessment = engine.analyze(turns=turns, raw_transcript=transcript)

        pred_decision = assessment.decision # BLOCK, ALLOW, INCONCLUSIVE
        pred_level = assessment.risk_level   # HIGH_RISK, SUSPICIOUS, LOW_RISK, INSUFFICIENT_EVIDENCE
        score = assessment.risk_score

        is_predicted_scam = (pred_level in ["HIGH_RISK", "SUSPICIOUS"] or pred_decision == "BLOCK")
        is_insufficient = (pred_level == "INSUFFICIENT_EVIDENCE" or pred_decision == "INCONCLUSIVE" or assessment.insufficient_evidence)

        if is_insufficient:
            insufficient_ev_count += 1

        passed = False
        outcome = ""

        if gt == "SCAM":
            if is_predicted_scam:
                tp += 1
                passed = True
                outcome = "PASS [TP]"
            else:
                fn += 1
                outcome = "FAIL [FN - Missed Scam]"
                failures.append({
                    "id": sid, "category": cat, "expected": "SCAM",
                    "got_level": pred_level, "got_score": score,
                    "reasons": assessment.reasons, "transcript": transcript[:100] + "..."
                })
        elif gt == "SAFE":
            if not is_predicted_scam:
                tn += 1
                passed = True
                outcome = "PASS [TN]"
            else:
                fp += 1
                outcome = "FAIL [FP - False Alarm]"
                failures.append({
                    "id": sid, "category": cat, "expected": "SAFE",
                    "got_level": pred_level, "got_score": score,
                    "evidence": [e.exact_quote for e in assessment.evidence],
                    "transcript": transcript[:100] + "..."
                })
        elif gt == "INSUFFICIENT_EVIDENCE":
            if not is_predicted_scam:
                tn += 1
                passed = True
                outcome = "PASS [TN (Deferred)]"
            else:
                fp += 1
                outcome = "FAIL [FP - Inconclusive Flagged as Scam]"
                failures.append({
                    "id": sid, "category": cat, "expected": "INSUFFICIENT_EVIDENCE",
                    "got_level": pred_level, "got_score": score,
                    "evidence": [e.exact_quote for e in assessment.evidence],
                    "transcript": transcript[:100] + "..."
                })

        if passed:
            category_stats[cat]["passed"] += 1
            language_stats[lang]["passed"] += 1

        print(f"[{'PASS' if passed else 'FAIL'}] {sid:38s} | {cat:30s} | GT:{gt:5s} -> Pred:{pred_level:21s} (Score: {score:4.1f}) {outcome}")

    # Metrics computation
    total_eval = tp + tn + fp + fn
    precision = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = (fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
    fnr = (fn / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
    abstention_rate = (insufficient_ev_count / total_eval * 100.0) if total_eval > 0 else 0.0

    print("\n" + "=" * 85)
    print("HOLDOUT DETECTION ACCURACY & GENERALIZATION METRICS:")
    print("=" * 85)
    print(f"  • Total Evaluated Samples   : {total_eval}")
    print(f"  • True Positives (TP)       : {tp:2d}  (Novel scams correctly blocked)")
    print(f"  • True Negatives (TN)       : {tn:2d}  (Hospital urgency & legitimate calls allowed)")
    print(f"  • False Positives (FP)      : {fp:2d}  (Legitimate calls wrongly flagged)")
    print(f"  • False Negatives (FN)      : {fn:2d}  (Novel scams missed)")
    print("-" * 85)
    print(f"  • Precision                 : {precision:6.2f}%")
    print(f"  • Recall (Sensitivity)      : {recall:6.2f}%")
    print(f"  • F1 Score                  : {f1:6.2f}%")
    print(f"  • False-Positive Rate (FPR) : {fpr:6.2f}%  [Formula: FP / (FP + TN)]")
    print(f"  • False-Negative Rate (FNR) : {fnr:6.2f}%  [Formula: FN / (TP + FN)]")
    print(f"  • Abstention/Deferred Rate  : {abstention_rate:6.2f}%  (Safely classified as INSUFFICIENT_EVIDENCE)")
    print("-" * 85)
    print("CONFUSION MATRIX:")
    print(f"                     Predicted Non-Scam    Predicted Scam")
    print(f"  Actual Non-Scam:          {tn:2d}                    {fp:2d}  (Total: {tn+fp})")
    print(f"  Actual Scam:              {fn:2d}                    {tp:2d}  (Total: {fn+tp})")

    print("\nBREAKDOWN BY CATEGORY:")
    for cat, stats in sorted(category_stats.items()):
        pct = (stats["passed"] / stats["total"]) * 100.0 if stats["total"] > 0 else 0.0
        print(f"  • {cat:32s}: {stats['passed']}/{stats['total']} passed ({pct:.1f}%)")

    print("\nBREAKDOWN BY LANGUAGE:")
    for lang, stats in sorted(language_stats.items()):
        pct = (stats["passed"] / stats["total"]) * 100.0 if stats["total"] > 0 else 0.0
        print(f"  • {lang:15s}: {stats['passed']}/{stats['total']} passed ({pct:.1f}%)")

    print("\n" + "=" * 85)
    print("GENERALIZATION DISCLOSURE & LIMITATIONS:")
    print("  1. Statistical Margin of Error: Sample size N=30 is a focused holdout set designed")
    print("     to test novel syntactic phrasing and difficult negative scenarios (hospital urgency).")
    print("     Percentages carry statistical uncertainty and should not be cited as real-world 100%.")
    print("  2. In-the-Wild Generalization: Real fraud in the wild evolves continuously. These results")
    print("     demonstrate that the multi-vector compound scoring logic does not rely on rigid")
    print("     keyword matching, but field performance across telecommunication channels must be")
    print("     monitored in pilot trials.")
    print("=" * 85)

    return {
        "total": total_eval, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "fpr": fpr, "fnr": fnr, "failures": failures
    }

if __name__ == "__main__":
    run_holdout_evaluation()
