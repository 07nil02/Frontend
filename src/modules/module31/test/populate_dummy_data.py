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
        {
            "_id": "HC-001", "age": 47, "sex": "F", "blood_group": "O+",
            "lab_values": {"heart_rate": 80, "systolic_bp": 122, "diastolic_bp": 82, "hba1c": 5.5},
            "symptoms": ["fever", "cough", "fatigue"], "treatment_protocol": "Standard Care Protocol A",
            "outcome": "Fully Recovered"
        },
        {
            "_id": "HC-002", "age": 52, "sex": "M", "blood_group": "A-",
            "lab_values": {"heart_rate": 85, "systolic_bp": 130, "diastolic_bp": 85, "hba1c": 6.1},
            "symptoms": ["fever", "headache", "nausea"], "treatment_protocol": "Aggressive Antiviral Protocol",
            "outcome": "Recovered with Minor Complications"
        },
        {
            "_id": "HC-003", "age": 44, "sex": "F", "blood_group": "B+",
            "lab_values": {"heart_rate": 76, "systolic_bp": 118, "diastolic_bp": 78, "hba1c": 5.3},
            "symptoms": ["fever", "cough", "muscle_pain"], "treatment_protocol": "Standard Care Protocol A",
            "outcome": "Fully Recovered"
        },
        {
            "_id": "HC-004", "age": 60, "sex": "M", "blood_group": "O-",
            "lab_values": {"heart_rate": 100, "systolic_bp": 150, "diastolic_bp": 95, "hba1c": 7.2},
            "symptoms": ["chest_pain", "shortness_of_breath", "dizziness"], "treatment_protocol": "Emergency Cardiac Protocol",
            "outcome": "Deceased"
        },
        {
            "_id": "HC-005", "age": 45, "sex": "F", "blood_group": "AB+",
            "lab_values": {"heart_rate": 79, "systolic_bp": 120, "diastolic_bp": 81, "hba1c": 5.6},
            "symptoms": ["fever", "cough", "fatigue", "loss_of_taste"], "treatment_protocol": "Alternative Care Protocol B",
            "outcome": "Recovered Slowly"
        },
        {
            "_id": "HC-006", "age": 55, "sex": "M", "blood_group": "A-",
            "lab_values": {"heart_rate": 88, "systolic_bp": 140, "diastolic_bp": 88, "hba1c": 6.5},
            "symptoms": ["chest_pain", "shortness_of_breath"], "treatment_protocol": "Emergency Cardiac Protocol",
            "outcome": "Fully Recovered"
        },
        {
            "_id": "HC-007", "age": 35, "sex": "F", "blood_group": "B+",
            "lab_values": {"heart_rate": 68, "systolic_bp": 115, "diastolic_bp": 75, "hba1c": 5.2},
            "symptoms": ["headache", "fatigue"], "treatment_protocol": "Alternative Care Protocol B",
            "outcome": "Fully Recovered"
        },
        {
            "_id": "HC-008", "age": 62, "sex": "M", "blood_group": "O+",
            "lab_values": {"heart_rate": 95, "systolic_bp": 155, "diastolic_bp": 98, "hba1c": 7.5},
            "symptoms": ["chest_pain", "nausea", "dizziness"], "treatment_protocol": "Aggressive Antiviral Protocol",
            "outcome": "Deceased"
        }
    ]
    
    db.historical_cases.insert_many(cases)
    
    # Optional: Detailed Outcomes matching the LaTeX doc
    outcomes = [
        {"case_id": "HC-001", "survival_status": "Survived", "recovery_time_days": 5, "complication_rates": 0.0},
        {"case_id": "HC-002", "survival_status": "Survived", "recovery_time_days": 14, "complication_rates": 0.15},
        {"case_id": "HC-003", "survival_status": "Survived", "recovery_time_days": 6, "complication_rates": 0.0},
        {"case_id": "HC-004", "survival_status": "Deceased", "recovery_time_days": 2, "complication_rates": 1.0},
        {"case_id": "HC-005", "survival_status": "Survived", "recovery_time_days": 10, "complication_rates": 0.05},
        {"case_id": "HC-006", "survival_status": "Survived", "recovery_time_days": 8, "complication_rates": 0.10},
        {"case_id": "HC-007", "survival_status": "Survived", "recovery_time_days": 4, "complication_rates": 0.0},
        {"case_id": "HC-008", "survival_status": "Deceased", "recovery_time_days": 1, "complication_rates": 1.0},
    ]
    
    db.outcomes.insert_many(outcomes)

    print("Dummy data successfully populated!")
    print(f"Total Patients: {db.patients.count_documents({})}")
    print(f"Total Historical Cases: {db.historical_cases.count_documents({})}")
    print(f"Total Outcomes: {db.outcomes.count_documents({})}")

if __name__ == "__main__":
    populate_database()
