from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

TRAIN_CSV = PROCESSED_DIR / "diary_emotion_train.csv"
VALIDATION_CSV = PROCESSED_DIR / "diary_emotion_validation.csv"
MODEL_PATH = MODEL_DIR / "diary_emotion_nb_model.json"
EVALUATION_PATH = REPORT_DIR / "evaluation.json"

MIN_FEATURE_COUNT = 3
MAX_VOCABULARY_SIZE = 25000


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def extract_features(text: str) -> Counter:
    text = normalize(text)
    compact = text.replace(" ", "")
    features = Counter()

    for token in text.split():
        if len(token) >= 2:
            features[f"w:{token}"] += 1

    for n in (2, 3):
        if len(compact) >= n:
            for i in range(len(compact) - n + 1):
                features[f"c{n}:{compact[i:i+n]}"] += 1

    return features


def train(records: list[dict[str, str]]) -> dict:
    labels = sorted({row["main_emotion"] for row in records})
    doc_counts = Counter(row["main_emotion"] for row in records)
    raw_feature_counts = Counter()
    label_feature_counts: dict[str, Counter] = defaultdict(Counter)

    for row in records:
        label = row["main_emotion"]
        features = extract_features(row["text"])
        raw_feature_counts.update(features)
        label_feature_counts[label].update(features)

    vocabulary = [
        feature
        for feature, count in raw_feature_counts.most_common()
        if count >= MIN_FEATURE_COUNT
    ][:MAX_VOCABULARY_SIZE]
    vocabulary_set = set(vocabulary)
    vocab_size = len(vocabulary)

    priors = {
        label: math.log(doc_counts[label] / len(records))
        for label in labels
    }

    totals = {}
    feature_counts = {}
    for label in labels:
        filtered_counts = {
            feature: count
            for feature, count in label_feature_counts[label].items()
            if feature in vocabulary_set
        }
        total = sum(filtered_counts.values())
        totals[label] = total
        feature_counts[label] = filtered_counts

    return {
        "model_type": "multinomial_naive_bayes",
        "labels": labels,
        "vocabulary": vocabulary,
        "priors": priors,
        "feature_counts": feature_counts,
        "feature_totals": totals,
        "min_feature_count": MIN_FEATURE_COUNT,
        "max_vocabulary_size": MAX_VOCABULARY_SIZE,
    }


def predict(model: dict, text: str) -> tuple[str, dict[str, float]]:
    vocabulary = set(model["vocabulary"])
    features = extract_features(text)
    labels = model["labels"]
    scores = {}

    for label in labels:
        score = model["priors"][label]
        evidence = 0.0
        evidence_count = 0
        feature_counts = model["feature_counts"][label]
        denominator = model["feature_totals"][label] + len(vocabulary)
        for feature, count in features.items():
            if feature in vocabulary:
                evidence += math.log((feature_counts.get(feature, 0) + 1) / denominator) * count
                evidence_count += count
        if evidence_count:
            score += evidence / evidence_count
        scores[label] = score

    max_score = max(scores.values())
    exp_scores = {label: math.exp(score - max_score) for label, score in scores.items()}
    total = sum(exp_scores.values())
    probabilities = {label: value / total for label, value in exp_scores.items()}
    prediction = max(probabilities, key=probabilities.get)
    return prediction, probabilities


def evaluate(model: dict, records: list[dict[str, str]]) -> dict:
    labels = model["labels"]
    confusion = {label: Counter() for label in labels}
    correct = 0

    for row in records:
        truth = row["main_emotion"]
        prediction, _ = predict(model, row["text"])
        confusion[truth][prediction] += 1
        if truth == prediction:
            correct += 1

    per_label = {}
    for label in labels:
        tp = confusion[label][label]
        predicted_as_label = sum(confusion[truth][label] for truth in labels)
        actual_label = sum(confusion[label].values())
        precision = tp / predicted_as_label if predicted_as_label else 0
        recall = tp / actual_label if actual_label else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": actual_label,
        }

    return {
        "accuracy": round(correct / len(records), 4),
        "total": len(records),
        "per_label": per_label,
        "confusion_matrix": {
            truth: {pred: confusion[truth][pred] for pred in labels}
            for truth in labels
        },
    }


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    train_records = read_csv(TRAIN_CSV)
    validation_records = read_csv(VALIDATION_CSV)
    model = train(train_records)
    evaluation = evaluate(model, validation_records)

    MODEL_PATH.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
    EVALUATION_PATH.write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(evaluation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
