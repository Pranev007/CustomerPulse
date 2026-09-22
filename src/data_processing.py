"""
src/data_processing.py

Data cleaning pipeline for CustomerPulse.
Handles missing values, duplicates, outliers, inconsistent categories,
and type conversions with full logging and explanation.
"""

import os
import pandas as pd
import numpy as np


class DataCleaner:
    def __init__(self, raw_filepath: str):
        self.raw_filepath = raw_filepath
        self.df = None
        self.cleaning_log = []

    def load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.raw_filepath):
            raise FileNotFoundError(f"Raw data file not found at: {self.raw_filepath}")
        self.df = pd.read_csv(self.raw_filepath)
        self.cleaning_log.append(f"Loaded raw dataset with {len(self.df)} rows and {len(self.df.columns)} columns.")
        return self.df

    def remove_duplicates(self) -> pd.DataFrame:
        initial_len = len(self.df)
        self.df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)
        dropped = initial_len - len(self.df)
        self.cleaning_log.append(f"Checked duplicates: Removed {dropped} duplicate customer records.")
        return self.df

    def handle_missing_values(self) -> pd.DataFrame:
        missing = self.df.isnull().sum()
        self.cleaning_log.append(f"Missing values detected prior to imputation:\n{missing[missing > 0].to_dict()}")

        # 1. Satisfaction score: Impute using median by churn status
        if "satisfaction_score" in self.df.columns and self.df["satisfaction_score"].isnull().sum() > 0:
            sat_median = self.df.groupby("churn")["satisfaction_score"].transform("median")
            self.df["satisfaction_score"] = self.df["satisfaction_score"].fillna(sat_median)
            self.cleaning_log.append("Imputed missing 'satisfaction_score' with median satisfaction grouped by churn status.")

        # 2. Last login days: Impute with median
        if "last_login_days" in self.df.columns and self.df["last_login_days"].isnull().sum() > 0:
            last_login_med = self.df["last_login_days"].median()
            self.df["last_login_days"] = self.df["last_login_days"].fillna(last_login_med)
            self.cleaning_log.append(f"Imputed missing 'last_login_days' with overall median ({last_login_med:.1f} days).")

        # 3. Monthly charges: Impute with median grouped by contract type
        if "monthly_charges" in self.df.columns and self.df["monthly_charges"].isnull().sum() > 0:
            charges_med = self.df.groupby("contract_type")["monthly_charges"].transform("median")
            self.df["monthly_charges"] = self.df["monthly_charges"].fillna(charges_med)
            self.cleaning_log.append("Imputed missing 'monthly_charges' with median charges by contract type.")

        return self.df

    def enforce_data_types_and_ranges(self) -> pd.DataFrame:
        # Enforce integer types
        int_cols = ["age", "tenure_months", "support_tickets", "login_frequency", 
                    "last_login_days", "products_used", "satisfaction_score", 
                    "marketing_emails_opened", "monthly_orders", "complaints", "churn"]
        
        for col in int_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(int)

        # Enforce non-negative numeric boundaries
        numeric_cols = ["tenure_months", "monthly_charges", "total_spend", "avg_order_value"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = np.maximum(self.df[col], 0.0)

        # Re-verify total_spend internal consistency
        self.df["total_spend"] = np.where(
            self.df["total_spend"] < self.df["monthly_charges"],
            self.df["monthly_charges"] * self.df["tenure_months"],
            self.df["total_spend"]
        )

        self.cleaning_log.append("Converted numeric categories to strict integer/float types and enforced range boundaries.")
        return self.df

    def handle_outliers(self) -> pd.DataFrame:
        # Cap extreme monthly charges & total spend at 99.5th percentile to handle skew without data loss
        for col in ["monthly_charges", "total_spend", "avg_order_value"]:
            if col in self.df.columns:
                cap_val = self.df[col].quantile(0.995)
                self.df[col] = np.minimum(self.df[col], cap_val)
        self.cleaning_log.append("Capped upper 0.5% extreme outliers for financial metrics (monthly_charges, total_spend, avg_order_value).")
        return self.df

    def clean_pipeline(self, output_filepath: str) -> pd.DataFrame:
        self.load_data()
        self.remove_duplicates()
        self.handle_missing_values()
        self.enforce_data_types_and_ranges()
        self.handle_outliers()

        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        self.df.to_csv(output_filepath, index=False)
        self.cleaning_log.append(f"Successfully saved cleaned dataset to: {output_filepath}")
        return self.df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_path = os.path.join(base_dir, "data", "raw", "customer_churn_raw.csv")
    proc_path = os.path.join(base_dir, "data", "processed", "customer_churn_cleaned.csv")

    cleaner = DataCleaner(raw_path)
    df_clean = cleaner.clean_pipeline(proc_path)
    print("\n--- DATA CLEANING SUMMARY LOG ---")
    for log_item in cleaner.cleaning_log:
        print(f"• {log_item}")
