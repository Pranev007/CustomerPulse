"""
src/model.py

Machine Learning modeling engine for CustomerPulse.
Trains Logistic Regression, Random Forest, and Gradient Boosting / XGBoost models.
Evaluates Precision, Recall, F1, ROC-AUC, extracts feature importances,
and exports predictions and trained pipelines.
"""

import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)


class ChurnModelPipeline:
    def __init__(self, target_col: str = "churn"):
        self.target_col = target_col
        self.feature_cols = None
        self.preprocessor = None
        self.models = {}
        self.results = {}
        self.best_model_name = None
        self.best_pipeline = None

    def prepare_data(self, df: pd.DataFrame):
        # Exclude ID and target column
        exclude_cols = [self.target_col, "customer_id", "churn_probability", "revenue_at_risk", "customer_segment", "rfm_combined"]
        X = df.drop(columns=[c for c in exclude_cols if c in df.columns])
        y = df[self.target_col]

        num_cols = X.select_dtypes(include=["int64", "float64", "int32"]).columns.tolist()
        cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
            ]
        )

        return X, y, num_cols, cat_cols

    def train_and_evaluate(self, df: pd.DataFrame, test_size: float = 0.20, seed: int = 42):
        X, y, num_cols, cat_cols = self.prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=y
        )

        # 1. Logistic Regression
        lr_pipe = Pipeline([
            ("preprocessor", self.preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=seed))
        ])
        lr_pipe.fit(X_train, y_train)

        # 2. Random Forest
        rf_pipe = Pipeline([
            ("preprocessor", self.preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=150, max_depth=12, random_state=seed, n_jobs=-1))
        ])
        rf_pipe.fit(X_train, y_train)

        # 3. Gradient Boosting (HistGradientBoosting)
        gb_pipe = Pipeline([
            ("preprocessor", self.preprocessor),
            ("classifier", HistGradientBoostingClassifier(max_iter=150, random_state=seed))
        ])
        gb_pipe.fit(X_train, y_train)

        self.models = {
            "Logistic Regression": lr_pipe,
            "Random Forest": rf_pipe,
            "Gradient Boosting": gb_pipe
        }

        best_auc = 0.0
        for name, pipe in self.models.items():
            y_pred = pipe.predict(X_test)
            y_prob = pipe.predict_proba(X_test)[:, 1]

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred)
            rec = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_prob)
            cm = confusion_matrix(y_test, y_pred)

            self.results[name] = {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "roc_auc": auc,
                "confusion_matrix": cm,
                "y_test": y_test,
                "y_prob": y_prob,
                "y_pred": y_pred
            }

            if auc > best_auc:
                best_auc = auc
                self.best_model_name = name
                self.best_pipeline = pipe

        print(f"[MODEL PIPELINE] Best Model Selected: {self.best_model_name} (ROC-AUC: {best_auc:.4f})")
        return self.results

    def get_feature_importances(self, X_sample: pd.DataFrame) -> pd.DataFrame:
        if self.best_pipeline is None:
            raise ValueError("Model pipeline must be trained first.")

        preprocessor = self.best_pipeline.named_steps["preprocessor"]
        classifier = self.best_pipeline.named_steps["classifier"]

        cat_encoder = preprocessor.named_transformers_["cat"]
        num_cols = preprocessor.transformers_[0][2]
        cat_cols = preprocessor.transformers_[1][2]
        
        cat_feature_names = cat_encoder.get_feature_names_out(cat_cols).tolist()
        feature_names = num_cols + cat_feature_names

        if hasattr(classifier, "feature_importances_"):
            importances = classifier.feature_importances_
        elif hasattr(classifier, "coef_"):
            importances = np.abs(classifier.coef_[0])
        else:
            # Fallback for HistGradientBoosting
            from sklearn.inspection import permutation_importance
            X_trans = preprocessor.transform(X_sample)
            r = permutation_importance(classifier, X_trans, X_sample["churn"] if "churn" in X_sample else np.zeros(len(X_sample)), n_repeats=5, random_state=42)
            importances = r.importances_mean

        df_imp = pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        }).sort_values(by="importance", ascending=False)

        return df_imp

    def predict_full_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.best_pipeline is None:
            raise ValueError("Model pipeline must be trained before predicting.")

        exclude_cols = [self.target_col, "customer_id", "churn_probability", "revenue_at_risk", "customer_segment", "rfm_combined"]
        X = df.drop(columns=[c for c in exclude_cols if c in df.columns])

        probs = self.best_pipeline.predict_proba(X)[:, 1]
        preds = self.best_pipeline.predict(X)

        df_out = df.copy()
        df_out["churn_probability"] = np.round(probs, 4)
        df_out["predicted_churn"] = preds
        return df_out

    def save_artifacts(self, models_dir: str):
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, "best_churn_model.pkl")
        joblib.dump(self.best_pipeline, model_path)
        print(f"[SUCCESS] Saved best trained model artifact ({self.best_model_name}) to: {model_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    proc_path = os.path.join(base_dir, "data", "processed", "customer_churn_cleaned.csv")
    
    if os.path.exists(proc_path):
        df_clean = pd.read_csv(proc_path)
        from feature_engineering import engineer_features
        df_fe = engineer_features(df_clean)

        trainer = ChurnModelPipeline()
        results = trainer.train_and_evaluate(df_fe)

        print("\n--- MODEL PERFORMANCE COMPARISON ---")
        for model_name, metrics in results.items():
            print(f"\n[{model_name}]")
            print(f" • Accuracy:  {metrics['accuracy']:.4f}")
            print(f" • Precision: {metrics['precision']:.4f}")
            print(f" • Recall:    {metrics['recall']:.4f}")
            print(f" • F1 Score:  {metrics['f1_score']:.4f}")
            print(f" • ROC-AUC:   {metrics['roc_auc']:.4f}")

        df_preds = trainer.predict_full_dataset(df_fe)
        trainer.save_artifacts(os.path.join(base_dir, "models"))
