import os
import pickle
import random
import csv
import sys
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
try:
    from feature_extractors import extract_features, get_feature_names
except ImportError:
    from .feature_extractors import extract_features, get_feature_names

DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
DATASET_PATH = os.path.join(DATASETS_DIR, 'asap_aes.csv')
SYNTHETIC_DATASET_PATH = os.path.join(DATASETS_DIR, 'synthetic_essays_DO_NOT_USE_FOR_FINAL.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'trained_weights.pkl')

REQUIRED_TRAITS = ["organization", "conventions", "word_choice", "sentence_fluency", "voice", "content"]


def generate_synthetic_dataset():
    """
    Generates a synthetic dataset for offline training and smoke-testing.
    Zero external dependencies (uses standard library csv).
    """
    print("=" * 70)
    print("[WARNING] Generating SYNTHETIC dataset for smoke-testing only.")
    print("          This is NOT real human-labeled data.")
    print("          Do NOT use trained_weights.pkl from this run as your final model.")
    print("=" * 70)
    os.makedirs(DATASETS_DIR, exist_ok=True)

    templates = [
        "In this presentation, I am going to explain the design. Firstly, the architecture is modular. Secondly, the database runs on MongoDB. However, we found that scaling is hard. In conclusion, we succeeded.",
        "Um, like, basically, you know, we built this app and it's actually really cool. We did some things, kind of, and so it works. The end.",
        "We are absolutely delighted to welcome you to our corporate proposal. It is absolutely essential to join together to achieve our future plans. We appreciate your consideration.",
        "This project has several errors. The database fail. The API is wrong. Punctuation , is bad . Spelling errrors are present. Duplicate duplicate words here.",
        "Our scalable technical architecture leverages distributed microservices. To implement this, we vectorized all text features using an offline TF-IDF matrix. The results demonstrate high performance.",
        "To achieve clarity, we must keep sentences brief. Long sentences clutter the message. Focus on direct verbs. Avoid passive phrasing.",
        "We thank you, our esteemed panel, for your consideration. We want to align this lecture with your expectations.",
        "The architecture is very disorganized. No agenda is present. Slides are cluttered. There is no call to action at the end.",
    ]

    fieldnames = ["essay", "organization", "conventions", "word_choice", "sentence_fluency", "voice", "content"]
    rows = []
    for i in range(300):
        template = random.choice(templates)
        words = template.split()
        if len(words) > 10:
            if random.random() < 0.2:
                words = words + ["um", "basically", "actually", "like"]
            if random.random() < 0.15:
                words = [w for w in words if random.random() > 0.1]
        text = " ".join(words)

        feats = extract_features(text)

        org = 80.0
        if feats["transition_density"] == 0:
            org -= 25
        if feats["word_count"] < 30:
            org -= 20
        org = max(10.0, min(100.0, org + random.randint(-5, 5)))

        conv = max(10.0, min(100.0, 100.0 - (feats["error_density"] * 300.0) + random.randint(-5, 5)))

        word_choice = max(10.0, min(100.0, 50.0 + (feats["noun_chunks_ratio"] * 100.0) - (feats["filler_density"] * 100.0) + random.randint(-5, 5)))

        fluency = 80.0
        if feats["avg_sentence_len"] > 20:
            fluency -= 20
        if feats["passive_ratio"] > 0.3:
            fluency -= 15
        if feats["filler_density"] > 0.05:
            fluency -= 15
        fluency = max(10.0, min(100.0, fluency + random.randint(-5, 5)))

        voice = max(10.0, min(100.0, 50.0 + (feats["audience_pronoun_ratio"] * 300.0) + (feats["sentiment_score"] * 30.0) + random.randint(-5, 5)))

        content = max(10.0, min(100.0, (org + conv + word_choice + fluency + voice) / 5.0 + random.randint(-4, 4)))

        rows.append({
            "essay": text,
            "organization": org,
            "conventions": conv,
            "word_choice": word_choice,
            "sentence_fluency": fluency,
            "voice": voice,
            "content": content
        })

    with open(SYNTHETIC_DATASET_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] Synthetic smoke-test dataset saved to {SYNTHETIC_DATASET_PATH}")
    return SYNTHETIC_DATASET_PATH


def _map_real_labels(rows, columns):
    """
    Maps dataset rows to required trait columns using standard list/dict manipulation.
    """
    print(f"[INFO] Columns found in dataset: {columns}")

    # Priority 1: exact trait columns already present
    if all(t in columns for t in REQUIRED_TRAITS):
        print("[INFO] Using exact trait columns found directly in the dataset. (REAL per-trait data)")
        return rows

    # Priority 2: real ASAP multi-trait rater columns (essay sets 7 & 8)
    trait_cols = [f"rater1_trait{i}" for i in range(1, 7)]
    if all(c in columns for c in trait_cols):
        print("[INFO] Mapping rater1_trait1..6 columns to our 6 traits. (REAL per-trait rater data)")
        for r in rows:
            for target, source in zip(REQUIRED_TRAITS, trait_cols):
                r[target] = float(r[source])
        return rows

    # Priority 3: holistic domain1_score as a real proxy
    if "domain1_score" in columns:
        print("[WARNING] Per-trait columns not found. Falling back to domain1_score as proxy for ALL 6 traits.")
        scores = [float(r["domain1_score"]) for r in rows if r.get("domain1_score")]
        mn, mx = min(scores), max(scores)
        for r in rows:
            raw = float(r.get("domain1_score", 0))
            scaled = ((raw - mn) / (mx - mn) * 90.0 + 10.0) if mx > mn else 70.0
            for target in REQUIRED_TRAITS:
                r[target] = scaled
        return rows

    # Priority 4: nothing usable found
    raise ValueError(
        f"Could not find usable label columns in the dataset. Columns: {columns}"
    )


def train_model(use_synthetic_if_missing=True):
    if not os.path.exists(DATASET_PATH):
        print(f"[WARN] Real dataset '{DATASET_PATH}' not found.")
        if not use_synthetic_if_missing:
            raise FileNotFoundError(
                f"'{DATASET_PATH}' not found and synthetic fallback disabled."
            )
        dataset_path = generate_synthetic_dataset()
        is_real_data = False
    else:
        dataset_path = DATASET_PATH
        is_real_data = True
        print(f"[INFO] Found real dataset at {os.path.abspath(dataset_path)}")

    print(f"[INFO] Loading dataset from {dataset_path}...")
    rows = []
    with open(dataset_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        for r in reader:
            rows.append(r)

    print(f"[INFO] Loaded {len(rows)} rows.")

    # Normalize essay column name
    if "essay" not in columns:
        if "essay_text" in columns:
            for r in rows:
                r["essay"] = r.pop("essay_text", "")
        else:
            found_col = None
            for c in columns:
                if rows and len(str(rows[0].get(c, ''))) > 50:
                    found_col = c
                    break
            if found_col:
                for r in rows:
                    r["essay"] = r.get(found_col, "")
            else:
                raise ValueError(f"Could not identify an essay text column. Columns: {columns}")

    if is_real_data:
        rows = _map_real_labels(rows, columns)

    print(f"[INFO] Extracting features for {len(rows)} documents. This may take a moment...")
    X_list = []
    feature_names = get_feature_names()
    for r in rows:
        feats = extract_features(str(r["essay"]))
        X_list.append([feats[name] for name in feature_names])
    X = np.array(X_list)

    models = {}
    print("[INFO] Training Random Forest Regressors (80/20 train/test split per trait)...")
    for trait in REQUIRED_TRAITS:
        y = np.array([float(r[trait]) for r in rows])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        score = r2_score(y_test, preds)
        pred_std = np.std(preds)
        print(f"   '{trait}': R² = {score:.3f} | prediction std = {pred_std:.2f}")

        # Refit on full data for the final saved model
        model.fit(X, y)
        models[trait] = model

    checkpoint = {
        "models": models,
        "feature_names": feature_names,
        "trained_on_real_data": is_real_data,
    }

    print(f"[INFO] Saving trained models to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(checkpoint, f)

    print("[SUCCESS] Offline NLP models successfully trained and serialized!")


if __name__ == '__main__':
    train_model()