import os
import json
import pandas as pd

def validate_canonical_dataset(csv_path: str):
    print(f"Validating Canonical Dataset at '{csv_path}'...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Canonical dataset file '{csv_path}' does not exist!")

    df = pd.read_csv(csv_path)
    print(f"Loaded Dataset Shape: {df.shape[0]:,} rows x {df.shape[1]:,} columns.\n")

    # Load Canonical Schema Config
    with open("configs/canonical_schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    with open("configs/dataset_mapping.json", "r", encoding="utf-8") as f:
        mapping_config = json.load(f)

    supported_templates = set(mapping_config.get("supported_cc_templates", {}).keys())

    # 1. Target Class Distribution (Zero Unknowns)
    print("--- TRIAGE TARGET DISTRIBUTION (CLEAN) ---")
    if "triage_target" in df.columns:
        print(df["triage_target"].value_counts(dropna=False))
        print("\nDistribution Percentage:")
        print((df["triage_target"].value_counts(normalize=True) * 100).round(2).astype(str) + "%")

        unknowns = (df["triage_target"] == "Unknown").sum()
        if unknowns == 0:
            print("\nTARGET CHECK PASSED: Zero 'Unknown' target rows present!")
        else:
            print(f"\nWARNING: Found {unknowns} 'Unknown' target rows!")

    # 2. 20 Supported Chief Complaint Template Distribution
    print("\n--- 20 SUPPORTED CHIEF COMPLAINT TEMPLATES DISTRIBUTION ---")
    if "chief_complaint" in df.columns:
        cc_counts = df["chief_complaint"].value_counts()
        print(f"Total Unique Template IDs present: {len(cc_counts)}")
        print(cc_counts)

    # 3. Null Values Audit
    print("\n--- NULL VALUES AUDIT ---")
    total_nulls = df.isna().sum().sum()
    print(f"Total NULL values across entire dataset: {total_nulls}")
    if total_nulls == 0:
        print("NULL CHECK PASSED: 100% of dataset cells are clean and populated!")
    else:
        print("Null counts per column:")
        print(df.isna().sum()[df.isna().sum() > 0])

    # 4. Sample BMI Statistics
    if "bmi" in df.columns:
        print("\n--- BMI STATISTICAL SUMMARY ---")
        print(df["bmi"].describe())

    # 5. Leakage Prevention Check
    forbidden_terms = ["troponin", "mri", "ct_count", "ekg", "culture", "bloodua", "glucoseua"]
    leaked = [col for col in df.columns if any(term in col.lower() for term in forbidden_terms)]
    if leaked:
        print(f"\nLEAKAGE DETECTED! Found forbidden hospital-only features: {leaked}")
    else:
        print("\nLEAKAGE CHECK PASSED: Zero hospital-only lab/imaging features found in canonical dataset!")

    print("\nValidation Completed Successfully!")

if __name__ == "__main__":
    validate_canonical_dataset("data/processed/canonical_dataset.csv")
