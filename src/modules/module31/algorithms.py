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
            
        lab_distance = euclidean_distance(target_lab_vector, case_lab_vector)
        score_lab = 1 / (1 + lab_distance) # Normalization

        # 2. Clinical Score (Jaccard Similarity)
        # Assuming 'symptoms' is a list of strings
        target_symptoms = set(target_patient.get("symptoms", []))
        case_symptoms = set(case.get("symptoms", []))
        score_clin = jaccard_similarity(target_symptoms, case_symptoms)

        # 3. Treatment Score (Exact/Fuzzy Match)
        # Assuming 'treatment_protocol' is a string
        target_treatment = target_patient.get("treatment_protocol", "")
        case_treatment = case.get("treatment_protocol", "")
        score_treat = exact_or_fuzzy_match(target_treatment, case_treatment, method='exact')

        # Final Weighted Score
        final_similarity = (W_lab * score_lab) + (W_clin * score_clin) + (W_treat * score_treat)
        
        results.append({
            "case_id": case["_id"],
            "final_similarity": final_similarity,
            "outcome": case.get("outcome") 
        })

    # Rank and insert into treatment_comparisons
    sorted_results = sorted(results, key=lambda x: x["final_similarity"], reverse=True)
    
    # Clear previous comparisons for the target patient
    treatment_comparisons.delete_many({"target_patient_id": target_patient_id})
    
    # Insert new matches
    for result in sorted_results: # Insert all matches
        treatment_comparisons.insert_one({
            "target_patient_id": target_patient_id,
            "matched_case_id": result["case_id"],
            "SimilarityScore": result["final_similarity"],
            # EffectivenessDelta would be calculated based on outcomes
            "EffectivenessDelta": "calculation_pending" 
        })
        
    print(f"Inserted {len(sorted_results)} treatment comparisons for patient {target_patient_id}.")
    return sorted_results[:10]

if __name__ == '__main__':
    # This is an example of how you might run this.
    # You would need to have data in your DB first.
    # from bson.objectid import ObjectId
    # calculate_similarity(ObjectId("some_patient_id_here"))
    print("Algorithm module ready.")

