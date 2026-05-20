import json
import os
import sys
from pathlib import Path

import django
import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "securedocs.settings")
django.setup()

from documents.services import extract_text  # noqa: E402



CLASSIFIER_DIR = Path(__file__).resolve().parent
DATASET_DIR = CLASSIFIER_DIR / "dataset"
SYNTHETIC_DIR = DATASET_DIR / "synthetic"
REAL_DIR = DATASET_DIR / "real"
OCR_CACHE = DATASET_DIR / "_ocr_cache.json"
MODEL_PATH = CLASSIFIER_DIR / "model.pkl"
REPORTS_DIR = CLASSIFIER_DIR / "reports"
REPORT_TXT = REPORTS_DIR / "classification_report.txt"
CONFUSION_PNG = REPORTS_DIR / "confusion_matrix.png"

CLASSES = ["contract", "id", "invoice", "other"]
RANDOM_STATE = 2023



def find_pdfs():
    samples = []
    for root in (SYNTHETIC_DIR, REAL_DIR):
        for class_name in CLASSES:
            class_dir = root / class_name
            if not class_dir.is_dir():
                continue
            for pdf in sorted(class_dir.glob("*.pdf")):
                samples.append((pdf, class_name))
    return samples


def load_ocr_cache():
    if OCR_CACHE.exists():
        with OCR_CACHE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_ocr_cache(cache):
    with OCR_CACHE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def ocr_all(samples):
    cache = load_ocr_cache()
    texts, labels = [], []
    new_count = 0

    for pdf_path, label in samples:
        key = str(pdf_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        if key in cache:
            text = cache[key]
        else:
            print(f"  OCR: {key}")
            text = extract_text(pdf_path)
            cache[key] = text
            new_count += 1

        texts.append(text)
        labels.append(label)

    if new_count > 0:
        save_ocr_cache(cache)
        print(f"OCR cache updated ({new_count} new files)")
    else:
        print(f"OCR cache hit for all {len(samples)} files")

    return texts, labels

def build_pipeline(classifier):
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )),
        ("clf", classifier),
    ])

def main():
    print("=" * 60)
    print("SecureDocs classifier training (SD-15)")
    print("=" * 60)

    samples = find_pdfs()
    print(f"\nFound {len(samples)} PDFs across {len(CLASSES)} classes")
    for cls in CLASSES:
        n = sum(1 for _, lbl in samples if lbl == cls)
        print(f"  {cls:10s}: {n}")

    if len(samples) == 0:
        print("ERROR: no PDFs found. Did you run generate_dataset.py?")
        return

    print("\nExtracting text via OCR...")
    texts, labels = ocr_all(samples)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels,
        test_size=0.20,
        stratify=labels,
        random_state=RANDOM_STATE,
    )
    print(f"\nTrain: {len(X_train)} docs | Test: {len(X_test)} docs")

    print("\n--- Baseline: Multinomial Naive Bayes ---")
    nb_pipeline = build_pipeline(MultinomialNB())
    nb_pipeline.fit(X_train, y_train)
    nb_pred = nb_pipeline.predict(X_test)
    nb_acc = accuracy_score(y_test, nb_pred)
    print(f"Accuracy: {nb_acc:.3f}")

    print("\n--- Main model: Logistic Regression ---")
    lr_pipeline = build_pipeline(LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ))
    lr_pipeline.fit(X_train, y_train)
    lr_pred = lr_pipeline.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)
    print(f"Accuracy: {lr_acc:.3f}")

    report = classification_report(
        y_test, lr_pred,
        labels=CLASSES,
        target_names=CLASSES,
        digits=3,
        zero_division=0,
    )
    print("\nPer-class metrics (Logistic Regression):")
    print(report)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_TXT.open("w", encoding="utf-8") as f:
        f.write("SecureDocs classifier — evaluation report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Dataset: {len(samples)} PDFs ({len(X_train)} train, {len(X_test)} test)\n")
        f.write(f"Random state: {RANDOM_STATE}\n\n")
        f.write(f"Baseline (Naive Bayes) accuracy:        {nb_acc:.3f}\n")
        f.write(f"Main model (Logistic Regression) acc:   {lr_acc:.3f}\n\n")
        f.write("Per-class metrics (Logistic Regression):\n")
        f.write(report)
    print(f"\nReport saved to {REPORT_TXT.relative_to(PROJECT_ROOT)}")

    cm = confusion_matrix(y_test, lr_pred, labels=CLASSES)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASSES)
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion matrix — Logistic Regression")
    plt.tight_layout()
    plt.savefig(CONFUSION_PNG, dpi=120)
    plt.close(fig)
    print(f"Confusion matrix saved to {CONFUSION_PNG.relative_to(PROJECT_ROOT)}")

    joblib.dump(lr_pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH.relative_to(PROJECT_ROOT)}")

    print("\n" + "=" * 60)
    print("SD-15 training complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()