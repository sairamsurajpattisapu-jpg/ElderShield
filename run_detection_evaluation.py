"""
ElderShield — Scam Detection Evaluation Runner
Executes rule engine evaluation across all 12 standardized categories and computes:
  - Precision, Recall, F1 Score
  - False-Positive Rate (FP / (FP + TN))
  - False-Negative Rate (FN / (TP + FN))
  - Confusion Matrix
  - Accuracy breakdown by category
  - Accuracy breakdown by language
  - Performance under insufficient/ambiguous evidence
"""

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from engine.analyzer import engine, parse_raw_transcript
from tests.evaluation_dataset import EVALUATION_SAMPLES

def run_evaluation():
    total_samples = len(EVALUATION_SAMPLES)
    tp = 0 # True Positives: Ground Truth SCAM -> Detected HIGH_RISK / BLOCK
    fp = 0 # False Positives: Ground Truth SAFE/INSUFFICIENT -> Detected HIGH_RISK / BLOCK
    tn = 0 # True Negatives: Ground Truth SAFE/INSUFFICIENT -> Detected LOW_RISK or INSUFFICIENT_EVIDENCE
    fn = 0 # False Negatives: Ground Truth SCAM -> Detected SAFE / failed to block

    category_results = defaultdict(lambda: {"total": 0, "correct": 0})
    language_results = defaultdict(lambda: {"total": 0, "correct": 0})
    insufficient_evidence_results = {"total": 0, "correct": 0}

    print("=" * 85)
    print("ELDERSHIELD — SYSTEMATIC DETECTION & FALSE-ALARM EVALUATION REPORT")
    print("=" * 85)
    print(f"Total Evaluation Samples: {total_samples}")
    print("Fixture Type: Curated Synthetic & Multi-Turn Benchmark (Distinct from Dev Fixtures)")
    print("-" * 85)

    for sample in EVALUATION_SAMPLES:
        sid = sample["id"]
        cat = sample["category"]
        lang = sample["language"]
        ground_truth = sample["ground_truth"]
        transcript = sample["transcript"]

        turns = parse_raw_transcript(transcript)
        assessment = engine.analyze(turns=turns, raw_transcript=transcript)

        predicted_level = assessment.risk_level
        predicted_decision = assessment.decision
        predicted_class = "SCAM" if predicted_decision == "BLOCK" or predicted_level == "HIGH_RISK" else (
            "INSUFFICIENT_EVIDENCE" if assessment.insufficient_evidence or predicted_level == "INSUFFICIENT_EVIDENCE" else "SAFE"
        )

        category_results[cat]["total"] += 1
        language_results[lang]["total"] += 1

        is_correct = False
        if ground_truth == "SCAM":
            if predicted_class == "SCAM":
                tp += 1
                is_correct = True
            else:
                fn += 1
        elif ground_truth == "SAFE":
            if predicted_class == "SCAM":
                fp += 1
            else:
                tn += 1
                is_correct = True
        elif ground_truth == "INSUFFICIENT_EVIDENCE":
            insufficient_evidence_results["total"] += 1
            if predicted_class == "SCAM":
                fp += 1
            else:
                tn += 1
                if predicted_level == "INSUFFICIENT_EVIDENCE" or predicted_decision == "INCONCLUSIVE":
                    insufficient_evidence_results["correct"] += 1
                is_correct = True

        if is_correct:
            category_results[cat]["correct"] += 1
            language_results[lang]["correct"] += 1

        status_str = "PASS" if is_correct else "FAIL"
        print(f"[{status_str}] {sid:30s} | Cat: {cat:25s} | GT: {ground_truth:10s} -> Pred: {predicted_level:15s} (Score: {assessment.risk_score:4.1f})")

    # Metrics calculation
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = (fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = (fn / (tp + fn)) if (tp + fn) > 0 else 0.0

    print("\n" + "=" * 85)
    print("DETECTION ACCURACY & SAFETY METRICS:")
    print("=" * 85)
    print(f"  • True Positives (TP) : {tp:2d}  (Scams correctly blocked)")
    print(f"  • True Negatives (TN) : {tn:2d}  (Safe & ambiguous dialogues allowed/deferred)")
    print(f"  • False Positives (FP): {fp:2d}  (Safe calls wrongly blocked as scams)")
    print(f"  • False Negatives (FN): {fn:2d}  (Scams missed)")
    print("-" * 85)
    print(f"  • Precision           : {precision * 100:6.2f}%")
    print(f"  • Recall (Sensitivity): {recall * 100:6.2f}%")
    print(f"  • F1 Score            : {f1 * 100:6.2f}%")
    print(f"  • False-Positive Rate : {fpr * 100:6.2f}%  [Formula: FP / (FP + TN)]")
    print(f"  • False-Negative Rate : {fnr * 100:6.2f}%  [Formula: FN / (TP + FN)]")

    print("\nCONFUSION MATRIX:")
    print("               Predicted Non-Scam    Predicted Scam")
    print(f"Actual Non-Scam:     {tn:4d}                {fp:4d}  (Total: {tn+fp})")
    print(f"Actual Scam:         {fn:4d}                {tp:4d}  (Total: {fn+tp})")

    print("\nBREAKDOWN BY SCENARIO CATEGORY:")
    for cat, data in sorted(category_results.items()):
        acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0.0
        print(f"  • {cat:30s}: {data['correct']}/{data['total']} passed ({acc:5.1f}%)")

    print("\nBREAKDOWN BY LANGUAGE / SCRIPT:")
    for lang, data in sorted(language_results.items()):
        acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0.0
        print(f"  • {lang:30s}: {data['correct']}/{data['total']} passed ({acc:5.1f}%)")

    if insufficient_evidence_results["total"] > 0:
        ie_acc = (insufficient_evidence_results["correct"] / insufficient_evidence_results["total"]) * 100
        print(f"\nINSUFFICIENT EVIDENCE PERFORMANCE:")
        print(f"  • Correctly flagged as INSUFFICIENT_EVIDENCE: {insufficient_evidence_results['correct']}/{insufficient_evidence_results['total']} ({ie_acc:5.1f}%)")

    print("\n" + "=" * 85)
    print("LIMITATIONS AND EVALUATION DISCLOSURE:")
    print("  1. Dataset Size: N=24 labeled samples. This benchmark demonstrates rule correctness")
    print("     and false-positive resistance on curated test patterns; it is NOT an in-the-wild")
    print("     epidemiological prevalence study.")
    print("  2. Rule Scores vs Probabilities: ElderShield risk scores (0-100) represent rule-based")
    print("     compound threat indices, NOT calibrated statistical probabilities.")
    print("  3. Acoustic Limitation: Testing evaluated conversational text transcripts. Prosody")
    print("     and acoustic background cues were not evaluated by the rule analyzer.")
    print("=" * 85)

    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "fpr": fpr, "fnr": fnr
    }

if __name__ == "__main__":
    run_evaluation()
