"""
src/feature_engineering.py

Engineers business-relevant derived features, RFM scores, tenure bucketing,
and customer lifetime value estimates for CustomerPulse.
"""

import os
import pandas as pd
import numpy as np


class FeatureEngineer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def add_tenure_group(self) -> pd.DataFrame:
        bins = [0, 6, 12, 24, 48, 100]
        labels = ["0-6 Months", "7-12 Months", "13-24 Months", "25-48 Months", "49+ Months"]
        self.df["tenure_group"] = pd.cut(self.df["tenure_months"], bins=bins, labels=labels, include_lowest=True)
        return self.df

    def add_clv_estimate(self) -> pd.DataFrame:
        # Estimated 24-month CLV based on monthly charges & tenure scaling
        self.df["clv_estimate"] = np.round(self.df["monthly_charges"] * 24.0, 2)
        return self.df

    def add_engagement_score(self) -> pd.DataFrame:
        # Normalized score from 0 to 100
        norm_login = np.clip(self.df["login_frequency"] / 40.0, 0, 1)
        norm_orders = np.clip(self.df["monthly_orders"] / 10.0, 0, 1)
        norm_recency = np.clip(1.0 - (self.df["last_login_days"] / 60.0), 0, 1)
        
        score = (norm_login * 0.40 + norm_orders * 0.35 + norm_recency * 0.25) * 100.0
        self.df["engagement_score"] = np.round(score, 1)
        return self.df

    def add_rfm_metrics(self) -> pd.DataFrame:
        # Recency score (5 = most recent logins, 1 = inactive)
        self.df["recency_score"] = pd.qcut(self.df["last_login_days"].rank(method="first", ascending=False), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Frequency score (5 = highest login frequency)
        self.df["frequency_score"] = pd.qcut(self.df["login_frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Monetary score (5 = highest total spend / monthly charges)
        self.df["monetary_score"] = pd.qcut(self.df["total_spend"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Combined RFM Score
        self.df["rfm_combined"] = (
            self.df["recency_score"].astype(str) + 
            self.df["frequency_score"].astype(str) + 
            self.df["monetary_score"].astype(str)
        )
        return self.df

    def add_support_ticket_rate(self) -> pd.DataFrame:
        self.df["ticket_rate_per_month"] = np.round(self.df["support_tickets"] / (self.df["tenure_months"] + 1.0), 3)
        return self.df

    def transform_pipeline(self) -> pd.DataFrame:
        self.add_tenure_group()
        self.add_clv_estimate()
        self.add_engagement_score()
        self.add_rfm_metrics()
        self.add_support_ticket_rate()
        return self.df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    fe = FeatureEngineer(df)
    fe.add_tenure_group()
    fe.add_clv_estimate()
    fe.add_engagement_score()
    fe.add_rfm_metrics()
    fe.add_support_ticket_rate()
    return fe.df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    proc_path = os.path.join(base_dir, "data", "processed", "customer_churn_cleaned.csv")
    if os.path.exists(proc_path):
        df_clean = pd.read_csv(proc_path)
        df_fe = engineer_features(df_clean)
        print(f"[SUCCESS] Feature engineering complete. Total columns: {len(df_fe.columns)}")
        print("Derived columns added:", [c for c in df_fe.columns if c not in df_clean.columns])
