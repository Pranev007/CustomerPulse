"""
run_pipeline.py

End-to-End Orchestrator for CustomerPulse:
1. Generates synthetic customer dataset based on Kaggle E-Commerce schema.
2. Cleans raw data and handles missing values / outliers.
3. Engineers RFM metrics, engagement score, and CLV estimates.
4. Trains ML models (Logistic Regression, Random Forest, Gradient Boosting).
5. Predicts churn probabilities and quantifies Revenue at Risk.
6. Populates SQLite database (data/processed/customer_pulse.db) for SQL querying.
"""

import os
import sqlite3
import pandas as pd

from src.data_generator import generate_customer_data
from src.data_processing import DataCleaner
from src.feature_engineering import engineer_features
from src.model import ChurnModelPipeline
from src.business_analysis import BusinessAnalytics


def run_full_pipeline():
    print("==================================================")
    print("   CUSTOMER PULSE — END-TO-END ANALYTICS PIPELINE  ")
    print("==================================================")

    base_dir = os.path.dirname(__file__)
    raw_dir = os.path.join(base_dir, "data", "raw")
    proc_dir = os.path.join(base_dir, "data", "processed")
    models_dir = os.path.join(base_dir, "models")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    raw_path = os.path.join(raw_dir, "customer_churn_raw.csv")
    proc_path = os.path.join(proc_dir, "customer_churn_cleaned.csv")
    final_pred_path = os.path.join(proc_dir, "customer_churn_predictions.csv")
    db_path = os.path.join(proc_dir, "customer_pulse.db")

    # STEP 1: DATA GENERATION
    print("\n[STEP 1/6] Generating 20,000 raw customer records...")
    df_raw = generate_customer_data(n_samples=20000)
    df_raw.to_csv(raw_path, index=False)
    print(f" -> Raw data saved to {raw_path}")

    # STEP 2: DATA CLEANING
    print("\n[STEP 2/6] Executing data cleaning and validation pipeline...")
    cleaner = DataCleaner(raw_path)
    df_clean = cleaner.clean_pipeline(proc_path)
    print(f" -> Cleaned data saved to {proc_path}")

    # STEP 3: FEATURE ENGINEERING
    print("\n[STEP 3/6] Engineering RFM metrics, CLV, and engagement scores...")
    df_fe = engineer_features(df_clean)
    print(f" -> Engineered {len(df_fe.columns)} feature columns.")

    # STEP 4: ML MODEL TRAINING & PREDICTION
    print("\n[STEP 4/6] Training machine learning classification models...")
    trainer = ChurnModelPipeline()
    trainer.train_and_evaluate(df_fe)
    df_preds = trainer.predict_full_dataset(df_fe)
    trainer.save_artifacts(models_dir)

    # STEP 5: BUSINESS ANALYTICS & REVENUE RISK
    print("\n[STEP 5/6] Calculating Business KPIs & Quantifying Revenue at Risk...")
    ba = BusinessAnalytics(df_preds)
    df_risk = ba.calculate_revenue_at_risk(churn_prob_col="churn_probability")
    df_final = ba.assign_customer_segments(churn_prob_col="churn_probability")
    
    # Save final enriched CSV
    df_final.to_csv(final_pred_path, index=False)
    print(f" -> Final enriched predictions saved to {final_pred_path}")

    # STEP 6: SQL DATABASE POPULATION
    print("\n[STEP 6/6] Populating SQLite Database (customer_pulse.db)...")
    conn = sqlite3.connect(db_path)
    
    df_raw.to_sql("raw_customers", conn, if_exists="replace", index=False)
    df_clean.to_sql("cleaned_customers", conn, if_exists="replace", index=False)
    df_final.to_sql("customer_predictions", conn, if_exists="replace", index=False)

    # Summary tables for fast dashboard/SQL queries
    regional_summary = ba.summarize_risk_by_dimension("region")
    regional_summary.to_sql("risk_by_region", conn, if_exists="replace", index=False)

    segment_summary = ba.summarize_risk_by_dimension("customer_segment")
    segment_summary.to_sql("risk_by_segment", conn, if_exists="replace", index=False)

    conn.close()
    print(f" -> Database populated successfully at {db_path}")

    kpis = ba.calculate_executive_kpis()
    print("\n==================================================")
    print("            PIPELINE EXECUTION SUMMARY            ")
    print("==================================================")
    print(f" Total Customers Analyzed: {kpis['total_customers']:,}")
    print(f" Overall Churn Rate:       {kpis['churn_rate']:.2%}")
    print(f" ARPU (Monthly):           ${kpis['arpu']:.2f}")
    print(f" Avg Customer CLV:         ${kpis['avg_clv']:,.2f}")
    print(f" Total Revenue at Risk:    ${df_final['revenue_at_risk'].sum():,.2f}")
    print("==================================================")


if __name__ == "__main__":
    run_full_pipeline()
