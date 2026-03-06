from src.modules.module31.database import get_db

def setup_collections():
    """
    Creates the necessary collections in the database as described in the schema.
    """
    db = get_db()
    
    collections = [
        "patients", 
        "historical_cases", 
        "similarity_metrics", 
        "treatment_comparisons", 
        "outcomes"
    ]
    
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Created '{collection_name}' collection.")
        else:
            print(f"'{collection_name}' collection already exists.")
            
    # Optional: Insert a default similarity metric
    metrics_collection = db["similarity_metrics"]
    if metrics_collection.count_documents({}) == 0:
        default_metric = {
            "name": "default",
            "W_lab": 0.4,
            "W_clin": 0.4,
            "W_treat": 0.2
        }
        metrics_collection.insert_one(default_metric)
        print("Inserted default similarity metric.")


if __name__ == '__main__':
    setup_collections()
    print("MongoDB database setup for Module 31 complete.")
