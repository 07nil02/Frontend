from src.modules.module31.database import get_db
from .similarity_metrics import euclidean_distance, jaccard_similarity, exact_or_fuzzy_match
import numpy as np

def calculate_similarity(target_patient_id):
    """
    Calculates the similarity between a target patient and all historical cases.
    """
    db = get_db()
    patients = db["patients"]
    historical_cases = db["historical_cases"]
    similarity_metrics = db["similarity_metrics"]
    treatment_comparisons = db["treatment_comparisons"]

    target_patient = patients.find_one({"_id": target_patient_id})
    if not target_patient:
        print(f"Target patient with id {target_patient_id} not found.")
        return

    # Fetch dynamic weights
    weights = db["similarity_metrics"].find_one({"active": True}) # Getting the active metric
    if not weights:
        # Fallback to default if no active metric is found
        weights = db["similarity_metrics"].find_one({"name": "default"})
    
    if not weights:
        print("Similarity weights not found. Using default values.")
        weights = {"W_lab": 0.4, "W_clin": 0.4, "W_treat": 0.2}

    W_lab = weights.get('W_lab', 0.4)
    W_clin = weights.get('W_clin', 0.4)
    W_treat = weights.get('W_treat', 0.2)

    results = []
    for case in historical_cases.find():
        # 1. Lab Score (Euclidean Distance)
        # Assuming 'lab_values' is a dict of key-value pairs in both patient and case
        target_lab_vector = np.array(list(target_patient.get("lab_values", {}).values()))
        case_lab_vector = np.array(list(case.get("lab_values", {}).values()))
        
        # Ensure vectors are same length for comparison
        if len(target_lab_vector) != len(case_lab_vector):
            # Simple handling: skip if dimensions don't match. Could be improved.
            continue
            
