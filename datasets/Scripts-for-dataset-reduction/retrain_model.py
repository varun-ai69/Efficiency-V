"""
Retrain triage_model.joblib with proper conversation feature signal.

CONTRACT (must stay identical to current backend):
  - Input:  62 features in exact order from feature_names.json
  - Output: label 0 (Home Care), 1 (Consult), 2 (Immediate)
  - File:   backend/app/ai/ml/triage_model.joblib  (drop-in replacement)
  - feature_names.json is NOT changed.
"""

import json
import os
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_sample_weight

CANONICAL_CSV   = "c:/Users/Asus f15/Efficiency-V/datasets/processed/canonical_dataset.csv"
FEATURE_NAMES_F = "c:/Users/Asus f15/Efficiency-V/backend/app/ai/ml/feature_names.json"
MODEL_OUT       = "c:/Users/Asus f15/Efficiency-V/backend/app/ai/ml/triage_model.joblib"

# ── Exact same mappings as triage.py / predictor.py ───────────────────────────
CC_LIST = sorted([
    "fall_trauma", "abdominal_pain", "chest_pain", "shortness_of_breath",
    "back_pain", "stroke_symptoms", "urinary_symptoms", "headache",
    "dizziness", "fever", "cough", "rash", "vomiting", "leg_swelling",
    "sore_throat", "syncope", "palpitations", "seizure", "diarrhea",
    "allergic_reaction"
])
CC_MAP = {cc: idx for idx, cc in enumerate(CC_LIST)}

ONSET_MAP       = {"not_specified": 0, "gradual": 1, "acute": 2, "sudden": 3}
PROGRESSION_MAP = {"not_specified": 0, "better": 1, "same": 2, "worse": 3}
PAIN_MAP        = {"not_specified": 0, "sharp": 1, "burning": 2, "crushing": 3,
                   "stabbing": 4, "pressure": 5}
LABEL_MAP       = {"Home Care": 0, "Consult": 1, "Immediate": 2}

GENDER_MAP      = {"female": 0, "male": 1, "other": 2, "unknown": 0}
RACE_MAP        = {str(i): i for i in range(10)}
LANG_MAP        = {str(i): i for i in range(10)}
INS_MAP         = {str(i): i for i in range(5)}

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading canonical dataset ...")
df = pd.read_csv(CANONICAL_CSV)
print(f"  Loaded {len(df):,} rows x {df.shape[1]} cols")
print(f"  Label distribution:\n{df['triage_target'].value_counts()}\n")

df = df[df["triage_target"].isin(LABEL_MAP)].copy()
df["y"] = df["triage_target"].map(LABEL_MAP).astype(int)

with open(FEATURE_NAMES_F) as f:
    FEATURES = json.load(f)          # the canonical 62-feature list

# ── Encode static categorical columns ────────────────────────────────────────
def safe_int(val, mapping, default=0):
    return mapping.get(str(val).strip().lower(), default)

df["chief_complaint"] = df["chief_complaint"].apply(
    lambda x: CC_MAP.get(str(x).strip().lower(), 0)
).astype(float)

for col, mp in [("gender", GENDER_MAP), ("race", RACE_MAP),
                ("lang", LANG_MAP), ("insurance_status", INS_MAP)]:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: safe_int(x, mp)).astype(float)

# ── Synthetic conversation-feature augmentation ───────────────────────────────
# The original CSV has ALL conv features fixed to 0 (dataset_mapper.py lines 156-165).
# We generate clinically plausible values tied to triage class so the model
# actually learns their signal. Seed fixed for reproducibility.
rng = np.random.default_rng(42)
n   = len(df)
y   = df["y"].values

def class_noise(arr_base, noise_std):
    return np.clip(arr_base + rng.normal(0, noise_std, n), 0, None)

# pain_score [0-10]: Home Care ~2, Consult ~5, Immediate ~8.5
pain_base = np.where(y == 0, 2.0, np.where(y == 1, 5.0, 8.5))
df["pain_score"] = class_noise(pain_base, 1.5).clip(0, 10).round(1)

# symptom_severity [0-10]
sev_base = np.where(y == 0, 2.0, np.where(y == 1, 5.0, 8.0))
df["symptom_severity"] = class_noise(sev_base, 1.5).clip(0, 10).round(1)

# symptom_duration [hours] Home Care ~48h, Consult ~24h, Immediate ~4h
dur_base = np.where(y == 0, 48.0, np.where(y == 1, 24.0, 4.0))
df["symptom_duration"] = class_noise(dur_base, 12.0).clip(0, None).round(1)

# symptom_onset 0=not_specified, 1=gradual, 2=acute, 3=sudden
onset_vals = np.where(y == 2,
                rng.choice([2, 3], n, p=[0.3, 0.7]),
                np.where(y == 1,
                    rng.choice([1, 2], n, p=[0.5, 0.5]),
                    rng.choice([0, 1], n, p=[0.3, 0.7])
                ))
df["symptom_onset"] = onset_vals.astype(float)

# progression 0=not_specified, 1=better, 2=same, 3=worse
prog_vals = np.where(y == 2,
                rng.choice([2, 3], n, p=[0.2, 0.8]),
                np.where(y == 1,
                    rng.choice([1, 2, 3], n, p=[0.3, 0.4, 0.3]),
                    rng.choice([0, 1, 2], n, p=[0.2, 0.5, 0.3])
                ))
df["progression"] = prog_vals.astype(float)

# pain_type 0=not_specified, 1=sharp, 2=burning, 3=crushing, 4=stabbing, 5=pressure
pain_type_vals = np.where(y == 2,
                     rng.choice([1, 3, 4, 5], n, p=[0.1, 0.4, 0.3, 0.2]),
                     np.where(y == 1,
                         rng.choice([0, 1, 2, 5], n, p=[0.2, 0.3, 0.3, 0.2]),
                         rng.choice([0, 1], n, p=[0.6, 0.4])
                     ))
df["pain_type"] = pain_type_vals.astype(float)

# Red-flag binary features: very correlated with Immediate
FLAG_PROBS = {
    "unconscious":               [0.00, 0.01, 0.25],
    "unable_to_speak":           [0.00, 0.01, 0.20],
    "severe_bleeding":           [0.00, 0.02, 0.30],
    "seizure_active":            [0.00, 0.02, 0.22],
    "cyanosis":                  [0.00, 0.01, 0.18],
    "severe_shortness_of_breath":[0.01, 0.05, 0.60],
    "chest_tightness":           [0.02, 0.15, 0.55],
    "radiating_pain":            [0.02, 0.12, 0.45],
}
for feat, probs in FLAG_PROBS.items():
    p_arr = np.where(y == 0, probs[0], np.where(y == 1, probs[1], probs[2]))
    df[feat] = (rng.uniform(0, 1, n) < p_arr).astype(float)

# Moderate probability symptoms
MODERATE_FLAGS = {
    "body_aches":           [0.10, 0.30, 0.50],
    "abdominal_tenderness": [0.05, 0.20, 0.40],
    "diarrhea":             [0.10, 0.20, 0.25],
    "burning_urination":    [0.10, 0.20, 0.15],
    "urinary_frequency":    [0.10, 0.20, 0.15],
    "leg_swelling":         [0.05, 0.15, 0.30],
    "palpitations":         [0.03, 0.12, 0.35],
    "vision_changes":       [0.02, 0.10, 0.28],
    "recent_injury":        [0.10, 0.15, 0.20],
    "neck_stiffness":       [0.02, 0.08, 0.22],
    "light_sensitivity":    [0.03, 0.10, 0.18],
    "persistent_cough":     [0.10, 0.25, 0.20],
    "bloody_cough":         [0.01, 0.05, 0.20],
    "intermittent":         [0.40, 0.30, 0.10],
    "relieved_by_rest":     [0.50, 0.30, 0.05],
}
for feat, probs in MODERATE_FLAGS.items():
    p_arr = np.where(y == 0, probs[0], np.where(y == 1, probs[1], probs[2]))
    df[feat] = (rng.uniform(0, 1, n) < p_arr).astype(float)

# ── Build X in exact feature order ───────────────────────────────────────────
print("Building feature matrix in canonical order ...")
for feat in FEATURES:
    if feat not in df.columns:
        print(f"  [WARN] Missing feature '{feat}' -- filling 0.0")
        df[feat] = 0.0
    else:
        df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)

X = df[FEATURES].values.astype(float)
y_arr = df["y"].values.astype(int)
print(f"  X shape: {X.shape}   y distribution: {dict(zip(*np.unique(y_arr, return_counts=True)))}")

# ── Train / Test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_arr, test_size=0.15, random_state=42, stratify=y_arr
)
print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")

# ── Train XGBoost ─────────────────────────────────────────────────────────────
print("\nTraining XGBoost ...")
clf = XGBClassifier(
    n_estimators=400,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1,
)

sw = compute_sample_weight("balanced", y_train)
clf.fit(X_train, y_train, sample_weight=sw,
        eval_set=[(X_test, y_test)], verbose=50)

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
print("\n=== Test Set Performance ===")
print(classification_report(y_test, y_pred,
      target_names=["Home Care", "Consult", "Immediate"]))

# Sanity checks
LMAP = {0: "Home Care", 1: "Consult", 2: "Immediate"}

zero_vec = np.zeros((1, len(FEATURES)))
z_pred   = clf.predict(zero_vec)
z_proba  = clf.predict_proba(zero_vec)
print(f"\nSanity -- all-zeros -> {LMAP[int(z_pred[0])]}  proba={[round(p,3) for p in z_proba[0]]}")

mild_vec = zero_vec.copy()
mild_vec[0][FEATURES.index("pain_score")] = 2.0
mild_vec[0][FEATURES.index("symptom_duration")] = 48.0
mild_vec[0][FEATURES.index("intermittent")] = 1.0
mild_vec[0][FEATURES.index("relieved_by_rest")] = 1.0
m_pred = clf.predict(mild_vec)
m_prob = clf.predict_proba(mild_vec)
print(f"Sanity -- mild/stable -> {LMAP[int(m_pred[0])]}  proba={[round(p,3) for p in m_prob[0]]}")

sev_vec = zero_vec.copy()
sev_vec[0][FEATURES.index("pain_score")] = 9.0
sev_vec[0][FEATURES.index("symptom_severity")] = 9.0
sev_vec[0][FEATURES.index("severe_shortness_of_breath")] = 1.0
sev_vec[0][FEATURES.index("chest_tightness")] = 1.0
sev_vec[0][FEATURES.index("symptom_onset")] = 3.0   # sudden
sev_vec[0][FEATURES.index("progression")] = 3.0     # worse
s_pred = clf.predict(sev_vec)
s_prob = clf.predict_proba(sev_vec)
print(f"Sanity -- severe SOB + chest -> {LMAP[int(s_pred[0])]}  proba={[round(p,3) for p in s_prob[0]]}")

# ── Save (drop-in replacement) ────────────────────────────────────────────────
joblib.dump(clf, MODEL_OUT)
print(f"\nModel saved -> {MODEL_OUT}")
print(f"Feature count: {len(FEATURES)} (unchanged, no backend code changes needed)")
