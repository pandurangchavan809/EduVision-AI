import os
import pickle
import pandas as pd
import numpy as np

class AcademicPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join("ml_models", "models", "performance_predictor.pkl")
        
        self.model_path = model_path
        self.model = None
        self.features = [
            "hsc_perc", "sem1_sgpa", "sem2_sgpa", "sem3_sgpa",
            "sem4_sgpa", "sem5_sgpa", "sem6_sgpa", "attendance_perc",
            "certifications_count", "project_score", "dsa_score",
            "dbms_score", "ml_score", "cn_score"
        ]
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.model = data.get("model")
                    self.features = data.get("features", self.features)
                print(f"Successfully loaded ML model from {self.model_path}")
            except Exception as e:
                print(f"Warning: Could not load ML model pickle ({e}). Fallback to rule-based engine.")
        else:
            print(f"Model path {self.model_path} not found. Fallback to rule-based predictor.")

    def predict_performance(self, student_data):
        """
        Takes a dict or pandas Series of student attributes and returns:
        - predicted_sgpa
        - risk_status
        - strengths
        - weaknesses
        - recommendations
        """
        # Prepare feature vector
        feature_vector = []
        for feat in self.features:
            val = student_data.get(feat, 0.0)
            feature_vector.append(float(val))

        # Predict SGPA
        if self.model:
            df_in = pd.DataFrame([feature_vector], columns=self.features)
            predicted_sgpa = float(self.model.predict(df_in)[0])
            predicted_sgpa = round(min(10.0, max(4.0, predicted_sgpa)), 2)
        else:
            # Rule-based fallback
            sgpas = [float(student_data.get(f"sem{i}_sgpa", 7.0)) for i in range(1, 7)]
            avg_sgpa = sum(sgpas) / len(sgpas)
            attendance = float(student_data.get("attendance_perc", 80.0))
            predicted_sgpa = round(min(10.0, max(4.5, avg_sgpa * 0.85 + (attendance / 100) * 1.5)), 2)

        attendance = float(student_data.get("attendance_perc", 80.0))
        
        # Risk evaluation
        if predicted_sgpa < 6.5 or attendance < 72.0:
            risk_status = "High Academic Risk"
            risk_color = "red"
        elif predicted_sgpa < 7.8:
            risk_status = "Moderate Risk"
            risk_color = "amber"
        else:
            risk_status = "Low Risk / High Performer"
            risk_color = "emerald"

        # Identify strengths & weaknesses based on subject scores
        subjects = {
            "Data Structures & Algorithms": float(student_data.get("dsa_score", 75)),
            "Database Management (DBMS)": float(student_data.get("dbms_score", 75)),
            "Machine Learning & AI": float(student_data.get("ml_score", 75)),
            "Computer Networks": float(student_data.get("cn_score", 75))
        }

        sorted_subs = sorted(subjects.items(), key=lambda x: x[1], reverse=True)
        strengths = [f"{sub} ({score:.0f}%)" for sub, score in sorted_subs if score >= 75]
        weaknesses = [f"{sub} ({score:.0f}%)" for sub, score in sorted_subs if score < 75]

        if not strengths:
            strengths = [f"{sorted_subs[0][0]} ({sorted_subs[0][1]:.0f}%)"]
        if not weaknesses:
            weaknesses = ["No critical subject deficiencies detected."]

        # Recommendations
        recommendations = []
        if attendance < 75.0:
            recommendations.append("Mandatory attendance boost required to cross the institutional 75% threshold.")
        
        if any("Data Structures" in w for w in weaknesses):
            recommendations.append("Focus on algorithmic complexity and dynamic programming practice on LeetCode.")
        if any("Machine Learning" in w for w in weaknesses):
            recommendations.append("Review mathematical foundations of gradient descent and model evaluation metrics.")
        if any("DBMS" in w for w in weaknesses):
            recommendations.append("Practice advanced SQL joins, indexing techniques, and transaction management.")
            
        certs = int(student_data.get("certifications_count", 0))
        if certs < 2:
            recommendations.append("Complete industry certifications (e.g. AWS Cloud Practitioner, Kaggle ML) to boost profile.")
            
        proj = float(student_data.get("project_score", 70.0))
        if proj < 75.0:
            recommendations.append("Enhance practical project implementation and GitHub codebase documentation.")

        if not recommendations:
            recommendations.append("Maintain current academic consistency and mentor junior peers in lab assignments.")

        ai_summary = f"Student demonstrates strong technical aptitude in {sorted_subs[0][0]}. Based on historical SGPA momentum (Sem 6: {student_data.get('sem6_sgpa', 'N/A')}) and {attendance}% attendance, predicted Sem 7 target is {predicted_sgpa}/10.0."

        return {
            "predicted_sem7_sgpa": predicted_sgpa,
            "risk_status": risk_status,
            "risk_color": risk_color,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "ai_summary": ai_summary
        }
