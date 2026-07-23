import json
import os
import logging
import numpy as np
import joblib

logger = logging.getLogger("efficiency_v.ml.predictor")

class TriagePredictor:
    LABEL_MAP = {0: "Home Care", 1: "Consult", 2: "Immediate"}
    LABEL_COLORS = {0: "green", 1: "yellow", 2: "red"}

    # Human-readable display names for features
    FEATURE_DISPLAY = {
        "chief_complaint": "Chief Complaint",
        "age": "Age",
        "gender": "Gender",
        "race": "Race",
        "lang": "Language",
        "insurance_status": "Insurance Status",
        "bmi": "BMI",
        "previous_ed_visits": "Previous ED Visits",
        "previous_admissions": "Previous Admissions",
        "asthma": "Asthma",
        "copd": "COPD",
        "diabetes": "Diabetes",
        "hypertension": "Hypertension",
        "heart_disease": "Heart Disease",
        "chf": "Congestive Heart Failure",
        "kidney_disease": "Kidney Disease",
        "epilepsy": "Epilepsy",
        "anemia": "Anemia",
        "influenza": "Influenza",
        "uti": "UTI",
        "dizziness": "Dizziness",
        "fatigue": "Fatigue",
        "allergy": "Allergy",
        "takes_antihypertensive": "On Antihypertensive Medication",
        "takes_diabetes_medicine": "On Diabetes Medication",
        "takes_inhaler": "Uses Inhaler",
        "takes_blood_thinner": "On Blood Thinner",
        "heart_rate": "Heart Rate",
        "systolic_bp": "Systolic Blood Pressure",
        "diastolic_bp": "Diastolic Blood Pressure",
        "respiratory_rate": "Respiratory Rate",
        "spo2": "Oxygen Saturation (SpO2)",
        "body_temperature": "Body Temperature",
        "symptom_duration": "Symptom Duration (hours)",
        "symptom_severity": "Symptom Severity",
        "pain_score": "Pain Score (0-10)",
        "pain_type": "Type of Pain",
        "symptom_onset": "Symptom Onset",
        "progression": "Symptom Progression",
        "intermittent": "Intermittent Symptoms",
        "relieved_by_rest": "Relieved by Rest",
        "radiating_pain": "Radiating Pain",
        "chest_tightness": "Chest Tightness",
        "neck_stiffness": "Neck Stiffness",
        "light_sensitivity": "Light Sensitivity",
        "persistent_cough": "Persistent Cough",
        "bloody_cough": "Coughing Blood",
        "body_aches": "Body Aches",
        "abdominal_tenderness": "Abdominal Tenderness",
        "diarrhea": "Diarrhea",
        "burning_urination": "Burning Urination",
        "urinary_frequency": "Increased Urinary Frequency",
        "leg_swelling": "Leg Swelling",
        "palpitations": "Palpitations",
        "vision_changes": "Vision Changes",
        "recent_injury": "Recent Injury",
        "unconscious": "Unconscious/Unresponsive",
        "unable_to_speak": "Unable to Speak",
        "severe_bleeding": "Severe Bleeding",
        "seizure_active": "Active Seizure",
        "cyanosis": "Cyanosis (Blue Skin)",
        "severe_shortness_of_breath": "Severe Shortness of Breath",
    }
    
    # Reverse map for CC
    CC_REVERSE = {
        0: "abdominal_pain", 1: "allergic_reaction", 2: "back_pain", 3: "chest_pain",
        4: "cough", 5: "diarrhea", 6: "dizziness", 7: "fall_trauma", 8: "fever",
        9: "headache", 10: "leg_swelling", 11: "palpitations", 12: "rash",
        13: "seizure", 14: "shortness_of_breath", 15: "sore_throat",
        16: "stroke_symptoms", 17: "syncope", 18: "urinary_symptoms", 19: "vomiting"
    }

    def __init__(self):
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "triage_model.joblib")
        features_path = os.path.join(base_dir, "feature_names.json")

        logger.info(f"Loading XGBoost model from: {model_path}")
        self.model = joblib.load(model_path)

        with open(features_path, "r") as f:
            self.feature_names = json.load(f)

        self.feature_importances = dict(
            zip(self.feature_names, self.model.feature_importances_.tolist())
        )
        logger.info(f"Predictor ready. Features: {len(self.feature_names)}")

    def predict(self, vector: list, top_n: int = 5):
        """
        Run prediction and return structured result with top contributing features.
        """
        if len(vector) != len(self.feature_names):
            raise ValueError(
                f"Vector length mismatch: got {len(vector)}, expected {len(self.feature_names)}"
            )

        arr = np.array(vector, dtype=float).reshape(1, -1)

        # Prediction
        label_int = int(self.model.predict(arr)[0])
        proba = self.model.predict_proba(arr)[0]
        confidence = float(proba[label_int])
        prediction = self.LABEL_MAP[label_int]

        # Top features: weight global importance by the actual value in the vector
        feature_scores = {}
        for i, feat in enumerate(self.feature_names):
            val = float(vector[i])
            importance = self.feature_importances.get(feat, 0.0)
            # Active features (non-zero) with high importance are most relevant
            score = importance * (1.0 + abs(val))
            feature_scores[feat] = score

        top_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Build human-readable output
        top_features_detail = []
        for feat, score in top_features:
            val = vector[self.feature_names.index(feat)]
            # Human-readable value for chief_complaint
            if feat == "chief_complaint":
                display_val = self.CC_REVERSE.get(int(val), str(int(val)))
            else:
                display_val = val

            top_features_detail.append({
                "feature": feat,
                "display_name": self.FEATURE_DISPLAY.get(feat, feat),
                "value": display_val,
                "global_importance": round(self.feature_importances.get(feat, 0.0), 4),
            })

        return {
            "label": label_int,
            "prediction": prediction,
            "color": self.LABEL_COLORS[label_int],
            "confidence": round(confidence, 4),
            "top_features": top_features_detail,
        }


# Singleton
triage_predictor = TriagePredictor()
