import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.modules.module31.database import get_db
from src.modules.module31.algorithms import calculate_similarity
from src.modules.module31.test.populate_dummy_data import populate_database

def render_module31_ui(name, desc, cat_key):
    # Breadcrumb
    st.markdown(f"Category {cat_key.split('-')[0].strip()} > {name}")
    st.markdown(f"# {name}")
    st.markdown(f"*{desc}*")
    
    # Tabs
    tab = st.radio("Navigation", ["🏠 Home", "🔗 ER Diagram", "📋 Collections", "🔍 View Logic", "⚡ DB Triggers (Simulation)", "📊 Output"], horizontal=True, label_visibility="collapsed")
    st.divider()
    
    db = get_db()
    
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
        st.markdown("### Manage Database")
        st.write("Click below to populate the MongoDB database with initial test data.")
        if st.button("Populate Dummy Data"):
            with st.spinner("Populating data..."):
                try:
                    populate_database()
                    st.success("Database populated successfully! Check 'Collections' tab for counts.")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.divider()
        st.markdown("### 🎛️ Adjust Similarity Metrics")
        st.write("Update the dynamic mathematical weights used by the algorithm. This inserts a new active configuration into the `similarity_metrics` collection.")
        
        # Fetch current active weights to use as default values
        current_weights = db.similarity_metrics.find_one({"active": True})
        if not current_weights:
             current_weights = db.similarity_metrics.find_one({"name": "default"}) or {"W_lab": 0.4, "W_clin": 0.4, "W_treat": 0.2}

        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
             w_lab = st.number_input("Weight: Lab Data (Euclidean)", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_lab", 0.4)), step=0.1)
        with col_w2:
             w_clin = st.number_input("Weight: Clinical (Jaccard)", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_clin", 0.4)), step=0.1)
        with col_w3:
             w_treat = st.number_input("Weight: Treatment (Exact Matches)", min_value=0.0, max_value=1.0, value=float(current_weights.get("W_treat", 0.2)), step=0.1)
             
        if st.button("Update Active Weights", type="secondary"):
             total_weight = w_lab + w_clin + w_treat
             if abs(total_weight - 1.0) > 0.01: # allow tiny floating point differences
                 st.warning("Warning: Weights should ideally sum to 1.0 for normalized scoring, but changes will still be saved.")
             
             try:
                 # Deactivate old weights
                 db.similarity_metrics.update_many({}, {"$set": {"active": False}})
                 # Insert new active weights
                 import datetime
                 new_metric = {
                     "name": f"Config_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                     "W_lab": w_lab,
                     "W_clin": w_clin,
                     "W_treat": w_treat,
                     "active": True,
                     "created_at": datetime.datetime.now()
                 }
                 db.similarity_metrics.insert_one(new_metric)
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
