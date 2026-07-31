import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def train_and_save_model():
    dataset_path = os.path.join("datasets", "student_academic_dataset.csv")
    models_dir = os.path.join("ml_models", "models")
    model_output_path = os.path.join(models_dir, "performance_predictor.pkl")

    os.makedirs(models_dir, exist_ok=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} records.")

    features = [
        "hsc_perc", "sem1_sgpa", "sem2_sgpa", "sem3_sgpa",
        "sem4_sgpa", "sem5_sgpa", "sem6_sgpa", "attendance_perc",
        "certifications_count", "project_score", "dsa_score",
        "dbms_score", "ml_score", "cn_score"
    ]
    target = "predicted_sem7_sgpa"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print(f"Model Training Completed:")
    print(f"  - RMSE: {rmse:.4f}")
    print(f"  - R² Score: {r2:.4f}")

    model_data = {
        "model": model,
        "features": features,
        "target": target,
        "metrics": {"rmse": float(rmse), "r2": float(r2)}
    }

    with open(model_output_path, "wb") as f:
        pickle.dump(model_data, f)

    print(f"Model successfully saved to: {model_output_path}")

if __name__ == "__main__":
    train_and_save_model()
