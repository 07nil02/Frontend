from .database import get_db

def get_active_similarity_weights():
    db = get_db()
    current_weights = db.similarity_metrics.find_one({"active": True})
    if not current_weights:
        current_weights = db.similarity_metrics.find_one({"name": "default"}) or {"W_lab": 0.4, "W_clin": 0.4, "W_treat": 0.2}
    return current_weights

def update_active_similarity_weights(new_metric):
    db = get_db()
    db.similarity_metrics.update_many({}, {"$set": {"active": False}})
    db.similarity_metrics.insert_one(new_metric)

def get_collection_counts():
    db = get_db()
    return {
        "patients": db.patients.count_documents({}),
        "historical_cases": db.historical_cases.count_documents({}),
        "similarity_metrics": db.similarity_metrics.count_documents({}),
        "treatment_comparisons": db.treatment_comparisons.count_documents({}),
        "outcomes": db.outcomes.count_documents({})
    }

def get_all_patients():
    db = get_db()
    return list(db.patients.find({}, {"_id": 1, "name": 1}))
