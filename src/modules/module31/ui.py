import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.modules.module31.api import get_active_similarity_weights, update_active_similarity_weights, get_collection_counts, get_all_patients
from src.modules.module31.algorithms import calculate_similarity

def render_module31_ui(name, desc, cat_key):
    # Breadcrumb
    st.markdown(f"Category {cat_key.split('-')[0].strip()} > {name}")
    st.markdown(f"# {name}")
    st.markdown(f"*{desc}*")
    
    # Tabs
    tab = st.radio("Navigation", ["🏠 Home", "🔗 ER Diagram", "📋 Collections", "🔍 View Logic", "⚡ DB Triggers (Simulation)", "📊 Output"], horizontal=True, label_visibility="collapsed")
    st.divider()
    

    if tab == "🏠 Home":
        st.info(f"**{name}** - {desc}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Input Entities")
            st.success("1️⃣ Target Patient Data")
            st.success("2️⃣ Historical Cases Repository")
            st.success("3️⃣ Dynamic Similarity Metrics")
        
        with col2:
            st.markdown("### Output Entities")
            st.success("1️⃣ Matched Historical Cases")
            st.success("2️⃣ Similarity Scores")
            st.success("3️⃣ Treatment Effectiveness Delta")
            
        st.divider()
        st.markdown("### 🎛️ Adjust Similarity Metrics")
        st.write("Update the dynamic mathematical weights used by the algorithm. This inserts a new active configuration into the `similarity_metrics` collection.")
        
        # Fetch current active weights to use as default values
        current_weights = get_active_similarity_weights()

        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
             w_lab = st.number_input("Weight: Lab Data ", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_lab", 0.4)), step=0.1)
        with col_w2:
             w_clin = st.number_input("Weight: Clinical ", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_clin", 0.4)), step=0.1)
        with col_w3:
             w_treat = st.number_input("Weight: Treatment ", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_treat", 0.2)), step=0.1)
             
        if st.button("Update Active Weights", type="secondary"):
             total_weight = w_lab + w_clin + w_treat
             if abs(total_weight - 1.0) > 0.01: # allow tiny floating point differences
                 st.warning("Warning: Weights should ideally sum to 1.0 for normalized scoring, but changes will still be saved.")
             
             try:
                 import datetime
                 new_metric = {
                     "name": f"Config_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                     "W_lab": w_lab,
                     "W_clin": w_clin,
                     "W_treat": w_treat,
                     "active": True,
                     "created_at": datetime.datetime.now()
                 }
                 update_active_similarity_weights(new_metric)
                 st.success("Successfully updated active similarity weights in the database!")
             except Exception as e:
                 st.error(f"Error updating weights: {e}")
    elif tab == "🔗 ER Diagram":
        st.markdown("### Entity Relationship Diagram (MongoDB)")
        
        # Use st.markdown with raw HTML or a mermaid plugin to render Mermaid JS
        import streamlit.components.v1 as components
        
        # Mermaid JS markup
        mermaid_code = """
        <div class="mermaid" style="display: flex; justify-content: center; width: 100%;">
        erDiagram
    PATIENT ||--o{ TREATMENT-COMPARISON : "triggers"
    HISTORICAL-CASE ||--o{ TREATMENT-COMPARISON : "matched against"
    HISTORICAL-CASE ||--|| OUTCOME : "results in"
    SIMILARITY-METRIC ||--o{ TREATMENT-COMPARISON : "weighs"

    PATIENT {
        string PatientID PK
        string Name
        date DOB
        string Sex
        string BloodGroup
        dict lab_values
        array symptoms
        string treatment_protocol
    }

    HISTORICAL-CASE {
        string CaseID PK
        string Diagnosis
        string TreatmentProtocol
        string DemographicData
        string ClinicalData
    }

    OUTCOME {
        string OutcomeID PK
        string CaseID FK
        string SurvivalStatus
        string RecoveryTime
        string ComplicationRate
    }

    TREATMENT-COMPARISON {
        string ComparisonID PK
        string PatientID FK
        string CaseID FK
        string MetricID FK
        float SimilarityScore
        float EffectivenessDelta
    }

    SIMILARITY-METRIC {
        string MetricID PK
        string Algorithm
        float weight_lab
        float weight_clinical
        float wt_treatment
    }
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'loose' });
        </script>
        """
        components.html(mermaid_code, height=600, scrolling=True)

    elif tab == "📋 Collections":
        st.markdown("### Database Collections")
        
        try:
            counts = get_collection_counts()
            patients_count = counts["patients"]
            hist_count = counts["historical_cases"]
            sim_count = counts["similarity_metrics"]
            treat_count = counts["treatment_comparisons"]
            outcomes_count = counts["outcomes"]
            
            import pandas as pd
            df = pd.DataFrame({
                "Collection Name": ["patients", "historical_cases", "similarity_metrics", "treatment_comparisons", "outcomes"],
                "Records": [patients_count, hist_count, sim_count, treat_count, outcomes_count],
                "Status": ["✅ Active"] * 5
            })
            df.index = df.index + 1
            st.table(df)
        except Exception as e:
            st.error(f"Database Error: {e}. Please ensure MongoDB is running.")

    elif tab == "🔍 View Logic":
        st.markdown("### Pre-defined Processing Views & Queries")
        st.markdown("In compliance with the constraints, here is how the core processing simulates SQL logic inside MongoDB via aggregations and Python.")
        
        st.markdown("**1. Data Normalization View (Simulation)**")
        st.info("Normalizes raw vitals into a standardized 0-1 range for Euclidean comparison.")
        st.code("""
# MongoDB Aggregation Pipeline equivalent for View
pipeline = [
    {
        "$project": {
            "case_id": "$_id",
            "norm_heart_rate": { "$divide": ["$lab_values.heart_rate", 200] }, # Example max bound
            "norm_systolic_bp": { "$divide": ["$lab_values.systolic_bp", 250] },
            "norm_hba1c": { "$divide": ["$lab_values.hba1c", 15] }
        }
    }
]
        """, language="python")

        st.markdown("**2. Outcome Aggregation Query**")
        st.info("Joins the top similar cases with their historical outcomes to predict recovery.")
        st.code("""
# Execute after ranking top cases
db.treatment_comparisons.aggregate([
    { "$match": { "target_patient_id": target_patient_id } },
    { "$sort": { "SimilarityScore": -1 } },
    { "$limit": 10 },
    {
        "$lookup": {
            "from": "outcomes",
            "localField": "matched_case_id",
            "foreignField": "case_id",
            "as": "outcome_details"
        }
    }
])
        """, language="python")
        
    elif tab == "⚡ DB Triggers (Simulation)":
        st.markdown("### Database Triggers")
        st.markdown("These represent events that automatically fire when records are modified.")
        
        st.code("""
# Trigger: Update Treatment Effectiveness Delta
# Fired When: A new match is calculated and inserted into treatment_comparisons

def after_comparison_insert(target_id, matched_id):
    # Retrieve outcomes
    case_outcome = db.outcomes.find_one({"case_id": matched_id})
    target_current_status = get_target_status(target_id)
    
    # Calculate delta
    delta = case_outcome['recovery_time_days'] - target_current_status['days_ill']
    
    # Auto-update the comparison record
    db.treatment_comparisons.update_one(
        {"target_patient_id": target_id, "matched_case_id": matched_id},
        {"$set": {"EffectivenessDelta": f"{delta} days estimated"}}
    )
        """, language="python")

    elif tab == "📊 Output":
        st.markdown("### 🎯 Patient Case Similarity Analysis")
        
        # Fetch patients dynamically for dropdown
        try:
            patients_cursor = get_all_patients()
            if not patients_cursor:
                st.warning("No patients in the database.")
            else:
                patient_options = {str(p["_id"]): f"{p.get('name', 'Unknown User')} (ID: {p['_id']})" for p in patients_cursor}
                
                selected_patient_id = st.selectbox("Select Target Patient:", 
                                                   options=list(patient_options.keys()), 
                                                   format_func=lambda x: patient_options[x])

                if st.button("Run Similarity Search", type="primary"):
                    with st.spinner("Crunching historical metrics (Euclidean & Jaccard logic)..."):
                        try:
                            results = calculate_similarity(selected_patient_id)
                            if results:
                                st.success("Analysis Complete! Top matches found:")
                                import pandas as pd
                                df = pd.DataFrame(results)
                                df.index = df.index + 1
                                st.table(df)
                            else:
                                st.warning(f"No matched records found for patient: {selected_patient_id}")
                        except Exception as e:
                            st.error(f"Error during execution: {e}")
        except Exception as e:
            st.error(f"Could not connect to database: {e}")

    st.divider()
    if st.button("⬅ Back to Modules"):
        st.session_state.view = "category"
        st.rerun()
