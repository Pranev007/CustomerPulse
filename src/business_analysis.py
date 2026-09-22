"""
src/business_analysis.py

Calculates core Business Analytics KPIs, RFM Customer Segmentation,
Quantifies Revenue at Risk, and generates actionable Business Recommendations.
"""

import os
import pandas as pd
import numpy as np


class BusinessAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate_executive_kpis(self) -> dict:
        total_customers = int(len(self.df))
        churned_customers = int((self.df["churn"] == 1).sum())
        active_customers = total_customers - churned_customers
        churn_rate = float(churned_customers / total_customers) if total_customers > 0 else 0.0

        arpu = float(self.df["monthly_charges"].mean())
        avg_tenure = float(self.df["tenure_months"].mean())
        avg_clv = float(self.df["clv_estimate"].mean()) if "clv_estimate" in self.df.columns else float(self.df["total_spend"].mean())

        active_monthly_rev = float(self.df[self.df["churn"] == 0]["monthly_charges"].sum())
        churned_monthly_rev = float(self.df[self.df["churn"] == 1]["monthly_charges"].sum())
        total_historical_spend = float(self.df["total_spend"].sum())

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "churned_customers": churned_customers,
            "churn_rate": churn_rate,
            "arpu": arpu,
            "avg_tenure_months": avg_tenure,
            "avg_clv": avg_clv,
            "active_monthly_revenue": active_monthly_rev,
            "churned_monthly_revenue": churned_monthly_rev,
            "total_historical_spend": total_historical_spend
        }

    def assign_customer_segments(self, churn_prob_col: str = "churn_probability") -> pd.DataFrame:
        """
        Creates 4-quadrant Customer Segmentation based on Financial Value & Predicted Churn Probability:
        1. High Value - High Risk
        2. High Value - Low Risk
        3. Low Value - High Risk
        4. Low Value - Low Risk
        """
        prob = self.df[churn_prob_col] if churn_prob_col in self.df.columns else self.df["churn"].astype(float)
        val = self.df["monthly_charges"]

        val_threshold = self.df["monthly_charges"].median()
        risk_threshold = 0.50

        is_high_val = val >= val_threshold
        is_high_risk = prob >= risk_threshold

        conditions = [
            (is_high_val & is_high_risk),
            (is_high_val & ~is_high_risk),
            (~is_high_val & is_high_risk),
            (~is_high_val & ~is_high_risk)
        ]

        choices = [
            "High Value – High Risk",
            "High Value – Low Risk",
            "Low Value – High Risk",
            "Low Value – Low Risk"
        ]

        self.df["customer_segment"] = np.select(conditions, choices, default="Low Value – Low Risk")
        return self.df

    def calculate_revenue_at_risk(self, churn_prob_col: str = "churn_probability") -> pd.DataFrame:
        """
        Calculates expected Revenue at Risk per customer:
        revenue_at_risk = predicted_churn_probability * estimated_customer_value (24-month CLV)
        """
        prob = self.df[churn_prob_col] if churn_prob_col in self.df.columns else self.df["churn"].astype(float)
        clv = self.df["clv_estimate"] if "clv_estimate" in self.df.columns else self.df["monthly_charges"] * 24.0

        self.df["churn_probability"] = prob
        self.df["revenue_at_risk"] = np.round(prob * clv, 2)
        return self.df

    def get_top_at_risk_customers(self, top_n: int = 100) -> pd.DataFrame:
        if "revenue_at_risk" not in self.df.columns:
            self.calculate_revenue_at_risk()
        
        cols = [
            "customer_id", "region", "contract_type", "monthly_charges",
            "clv_estimate", "churn_probability", "revenue_at_risk",
            "customer_segment", "support_tickets", "satisfaction_score"
        ]
        available_cols = [c for c in cols if c in self.df.columns]
        
        return self.df.sort_values(by="revenue_at_risk", ascending=False).head(top_n)[available_cols]

    def summarize_risk_by_dimension(self, dimension: str) -> pd.DataFrame:
        if "revenue_at_risk" not in self.df.columns:
            self.calculate_revenue_at_risk()

        summary = self.df.groupby(dimension).agg(
            total_customers=("customer_id", "count"),
            avg_churn_prob=("churn_probability", "mean"),
            total_revenue_at_risk=("revenue_at_risk", "sum"),
            avg_revenue_at_risk=("revenue_at_risk", "mean")
        ).reset_index()

        summary["pct_of_total_risk"] = summary["total_revenue_at_risk"] / summary["total_revenue_at_risk"].sum()
        return summary.sort_values(by="total_revenue_at_risk", ascending=False)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    proc_path = os.path.join(base_dir, "data", "processed", "customer_churn_cleaned.csv")
    if os.path.exists(proc_path):
        df_clean = pd.read_csv(proc_path)
        from feature_engineering import engineer_features
        df_fe = engineer_features(df_clean)
        
        ba = BusinessAnalytics(df_fe)
        kpis = ba.calculate_executive_kpis()
        print("\n--- EXECUTIVE BUSINESS KPIS ---")
        for k, v in kpis.items():
            print(f"• {k}: {v:,.2f}" if isinstance(v, float) else f"• {k}: {v:,}")

        df_risk = ba.calculate_revenue_at_risk()
        df_segmented = ba.assign_customer_segments()
        
        print("\n--- REVENUE AT RISK BY REGION ---")
        print(ba.summarize_risk_by_dimension("region"))

        print("\n--- TOP 5 AT RISK CUSTOMERS ---")
        print(ba.get_top_at_risk_customers(5))
