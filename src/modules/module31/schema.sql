-- ==========================================
-- 1. MAIN ENTITY: HistoricalCase
-- ==========================================
CREATE TABLE M31_HistoricalCase (
    CaseID SERIAL PRIMARY KEY,
    Diagnosis VARCHAR(100), -- ICD-10 or Text
    TreatmentProtocol VARCHAR(255),
    AdmissionDate DATE
);

-- ==========================================
-- 2. MULTI-VALUED ATTRIBUTES (Double Ellipses)
-- ==========================================
-- Implements "DemographicsData" from diagram
CREATE TABLE M31_DemographicsData (
    DemoID SERIAL PRIMARY KEY,
    CaseID INT REFERENCES M31_HistoricalCase(CaseID) ON DELETE CASCADE,
    AttributeName VARCHAR(50), -- e.g., 'Age', 'Gender', 'Ethnicity'
    AttributeValue VARCHAR(50)
);

-- Implements "ClinicalData" from diagram
CREATE TABLE M31_ClinicalData (
    ClinID SERIAL PRIMARY KEY,
    CaseID INT REFERENCES M31_HistoricalCase(CaseID) ON DELETE CASCADE,
    FeatureName VARCHAR(50), -- e.g., 'SystolicBP', 'HeartRate'
    FeatureValue DECIMAL(10,2)
);

-- ==========================================
-- 3. WEAK ENTITY: Outcome (Double Rectangle)
-- ==========================================
CREATE TABLE M31_Outcome (
    CaseID INT PRIMARY KEY REFERENCES M31_HistoricalCase(CaseID), -- Identifying Relationship
    SurvivalStatus VARCHAR(20), -- 'Alive', 'Deceased'
    RecoveryTime INT, -- Days
    ComplicationRate DECIMAL(5,2) -- Percentage
);

-- ==========================================
-- 4. ENTITY: SimilarityMetric
-- ==========================================
CREATE TABLE M31_SimilarityMetric (
    MetricID SERIAL PRIMARY KEY,
    AlgorithmName VARCHAR(50), -- e.g., 'WeightedEuclidean'
    WeightFactor JSONB -- Stores weights: {"Age": 0.3, "Diagnosis": 0.5}
);

-- ==========================================
-- 5. RELATIONSHIP ENTITY: TreatmentComparison
-- ==========================================
CREATE TABLE M31_TreatmentComparison (
    ComparisonID SERIAL PRIMARY KEY,
    TargetCaseID INT, -- The new patient (can be null if just comparing history)
    MatchedCaseID INT REFERENCES M31_HistoricalCase(CaseID),
    MetricID INT REFERENCES M31_SimilarityMetric(MetricID),
    SimilarityScore DECIMAL(10,2),
    EffectivenessDelta DECIMAL(10,2),
    ComparisonDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 6. SEED DATA (To make it work)
-- ==========================================
-- Case 1
INSERT INTO M31_HistoricalCase (Diagnosis, TreatmentProtocol) VALUES ('Pneumonia', 'Antibiotics-A');
INSERT INTO M31_DemographicsData (CaseID, AttributeName, AttributeValue) VALUES (1, 'Age', '55'), (1, 'Gender', 'Male');
INSERT INTO M31_ClinicalData (CaseID, FeatureName, FeatureValue) VALUES (1, 'SystolicBP', 140), (1, 'WBC', 12.5);
INSERT INTO M31_Outcome (CaseID, SurvivalStatus, RecoveryTime, ComplicationRate) VALUES (1, 'Alive', 7, 0.05);

-- Case 2
INSERT INTO M31_HistoricalCase (Diagnosis, TreatmentProtocol) VALUES ('Pneumonia', 'Antibiotics-B');
INSERT INTO M31_DemographicsData (CaseID, AttributeName, AttributeValue) VALUES (2, 'Age', '58'), (2, 'Gender', 'Male');
INSERT INTO M31_ClinicalData (CaseID, FeatureName, FeatureValue) VALUES (2, 'SystolicBP', 138), (2, 'WBC', 11.0);
INSERT INTO M31_Outcome (CaseID, SurvivalStatus, RecoveryTime, ComplicationRate) VALUES (2, 'Alive', 5, 0.02);

-- Metric
INSERT INTO M31_SimilarityMetric (AlgorithmName, WeightFactor) VALUES ('StandardWeighted', '{"Age": 30, "Diagnosis": 50, "BP": 20}');

-- ==========================================
-- 7. THE LOGIC (Stored Procedure)
-- ==========================================
CREATE OR REPLACE FUNCTION M31_FindSimilarCases(
    input_age INT, 
    input_diagnosis VARCHAR, 
    input_sbp INT
) 
RETURNS TABLE(
    MatchedCaseID INT, 
    SimilarityScore INT, 
    Protocol VARCHAR, 
    Survival VARCHAR, 
    RecoveryDays INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        hc.CaseID,
        (
            -- Score Calculation based on joined tables
            (CASE WHEN hc.Diagnosis = input_diagnosis THEN 50 ELSE 0 END) +
            (CASE WHEN ABS(d_age.AttributeValue::INT - input_age) <= 5 THEN 30 ELSE 0 END) +
            (CASE WHEN ABS(c_bp.FeatureValue - input_sbp) < 10 THEN 20 ELSE 0 END)
        )::INT as Score,
        hc.TreatmentProtocol,
        o.SurvivalStatus,
        o.RecoveryTime
    FROM M31_HistoricalCase hc
    -- Join Outcome (Weak Entity)
    JOIN M31_Outcome o ON hc.CaseID = o.CaseID
    -- Join Demographics (Multi-valued Attribute 1)
    LEFT JOIN M31_DemographicsData d_age ON hc.CaseID = d_age.CaseID AND d_age.AttributeName = 'Age'
    -- Join ClinicalData (Multi-valued Attribute 2)
    LEFT JOIN M31_ClinicalData c_bp ON hc.CaseID = c_bp.CaseID AND c_bp.FeatureName = 'SystolicBP'
    ORDER BY Score DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;