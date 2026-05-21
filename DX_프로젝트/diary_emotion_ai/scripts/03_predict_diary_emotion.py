from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "diary_emotion_nb_model.json"
LABEL_MAP_PATH = ROOT / "data" / "processed" / "label_map.json"


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


def predict(model: dict, text: str) -> tuple[str, dict[str, float]]:
    vocabulary = set(model["vocabulary"])
    features = extract_features(text)
    scores = {}

    for label in model["labels"]:
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


def main() -> None:
    if len(sys.argv) < 2:
        diary_text = input("다이어리 문장을 입력하세요: ").strip()
        if not diary_text:
            print("입력된 문장이 없습니다.")
            raise SystemExit(1)
    else:
        diary_text = " ".join(sys.argv[1:])

    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    label_map = json.loads(LABEL_MAP_PATH.read_text(encoding="utf-8"))
    prediction, probabilities = predict(model, diary_text)
    sorted_probabilities = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)

    result = {
        "input": diary_text,
        "main_emotion": prediction,
        "confidence": round(probabilities[prediction], 4),
        "description": label_map["description"].get(prediction, ""),
        "ranking": [
            {"emotion": label, "probability": round(probability, 4)}
            for label, probability in sorted_probabilities
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
