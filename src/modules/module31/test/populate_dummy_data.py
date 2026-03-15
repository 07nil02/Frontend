import sys
import os

# Add the parent directory to sys.path so we can import 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db

def populate_database():
    db = get_db()
    
    print("Clearing existing data...")
    db.patients.delete_many({})
    db.historical_cases.delete_many({})
    db.outcomes.delete_many({})
    db.treatment_comparisons.delete_many({})
    db.similarity_metrics.delete_many({})

    # 1. Similarity Metrics
    print("Populating similarity_metrics...")
    import datetime
    db.similarity_metrics.insert_one({
        "name": "default",
        "W_lab": 0.4,
        "W_clin": 0.4,
        "W_treat": 0.2,
        "active": True,
        "created_at": datetime.datetime.now()
    })

    # 2. Target Patients
    print("Populating patients...")
    target_patients = [
        {
            "_id": "user123",
            "name": "Sarah Johnson",
            "age": 45,
            "sex": "F",
            "blood_group": "O+",
            "lab_values": { "heart_rate": 78, "systolic_bp": 120, "diastolic_bp": 80, "hba1c": 5.4 },
            "symptoms": ["fever", "cough", "fatigue", "muscle_pain"],
            "treatment_protocol": "Standard Care Protocol A"
        },
        {
            "_id": "user456",
            "name": "Michael Chen",
            "age": 58,
            "sex": "M",
            "blood_group": "A-",
            "lab_values": { "heart_rate": 92, "systolic_bp": 145, "diastolic_bp": 90, "hba1c": 6.8 },
            "symptoms": ["chest_pain", "shortness_of_breath", "nausea"],
            "treatment_protocol": "Emergency Cardiac Protocol"
        },
        {
            "_id": "user789",
            "name": "Emily Williams",
            "age": 32,
            "sex": "F",
            "blood_group": "B+",
            "lab_values": { "heart_rate": 65, "systolic_bp": 110, "diastolic_bp": 70, "hba1c": 5.1 },
            "symptoms": ["fatigue", "headache", "loss_of_taste"],
            "treatment_protocol": "Alternative Care Protocol B"
        }
    ]
    db.patients.insert_many(target_patients)

    # 3. Historical Cases & Outcomes
    print("Populating historical_cases and outcomes...")
    
    cases = [
