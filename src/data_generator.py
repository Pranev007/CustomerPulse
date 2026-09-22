"""
src/data_generator.py

Generates a realistic 20,000 record Customer Churn & Revenue Risk dataset based on the 
Standard Kaggle E-Commerce / Subscription Churn schema with realistic non-linear dependencies.
"""

import os
import numpy as np
import pandas as pd


def generate_customer_data(n_samples: int = 20000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic customer dataset with realistic churn dependencies and subtle noise.
    """
    np.random.seed(seed)

    customer_ids = [f"CP-{10001 + i}" for i in range(n_samples)]
    ages = np.random.randint(18, 71, size=n_samples)
    genders = np.random.choice(["Male", "Female", "Other"], size=n_samples, p=[0.49, 0.49, 0.02])
    regions = np.random.choice(
        ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"],
        size=n_samples,
        p=[0.35, 0.30, 0.20, 0.10, 0.05]
    )

    tenure_months = np.random.exponential(scale=18, size=n_samples).astype(int) + 1
    tenure_months = np.clip(tenure_months, 1, 72)

    contract_types = np.random.choice(
        ["Month-to-Month", "One Year", "Two Year"],
        size=n_samples,
        p=[0.55, 0.25, 0.20]
    )

    payment_methods = np.random.choice(
        ["Electronic Check", "Credit Card", "Bank Transfer", "UPI/Digital Wallet"],
        size=n_samples,
        p=[0.35, 0.30, 0.20, 0.15]
    )

    # Base monthly charges based on contract type & tier
    base_monthly = np.random.normal(loc=75, scale=25, size=n_samples)
    monthly_charges = np.round(np.clip(base_monthly, 18.0, 250.0), 2)

    # Total spend calculation with slight variation
    total_spend = np.round(monthly_charges * tenure_months * np.random.uniform(0.92, 1.08, size=n_samples), 2)

    # Behavioral metrics
    support_tickets = np.random.poisson(lam=2.2, size=n_samples)
    support_tickets = np.clip(support_tickets, 0, 15)

    login_frequency = np.random.randint(1, 40, size=n_samples)
    last_login_days = np.random.exponential(scale=12, size=n_samples).astype(int)
    last_login_days = np.clip(last_login_days, 0, 60)

    products_used = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.40, 0.30, 0.18, 0.08, 0.04])
    discount_usage = np.random.choice(["None", "Low", "Moderate", "High"], size=n_samples, p=[0.25, 0.35, 0.25, 0.15])
    complaints = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])

    satisfaction_score = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.15, 0.20, 0.30, 0.22, 0.13])
    marketing_emails_opened = np.random.randint(0, 30, size=n_samples)

    monthly_orders = np.random.poisson(lam=4.5, size=n_samples)
    monthly_orders = np.clip(monthly_orders, 0, 30)
    avg_order_value = np.round(np.random.normal(loc=45, scale=15, size=n_samples), 2)
    avg_order_value = np.clip(avg_order_value, 8.0, 300.0)

    # Kaggle E-Commerce complementary fields
    preferred_login_device = np.random.choice(["Mobile App", "Desktop", "Tablet"], size=n_samples, p=[0.60, 0.32, 0.08])
    preferred_order_cat = np.random.choice(
        ["Electronics", "Fashion", "Grocery", "SaaS Subscriptions", "Home & Living"],
        size=n_samples,
        p=[0.30, 0.28, 0.18, 0.14, 0.10]
    )

    # Calculating Churn probability using realistic risk score logit formula
    logit = (
        -1.8
        + 1.45 * (contract_types == "Month-to-Month")
        - 0.85 * (contract_types == "Two Year")
        + 0.18 * (support_tickets > 3)
        + 0.22 * (support_tickets > 6)
        + 0.04 * (last_login_days - 10)
        - 0.05 * (tenure_months - 12)
        + 0.80 * (complaints == 1)
        + 0.75 * (satisfaction_score <= 2)
        - 0.60 * (satisfaction_score >= 4)
        + 0.008 * (monthly_charges - 60)
        - 0.04 * (login_frequency - 15)
        + 0.40 * (payment_methods == "Electronic Check")
        + np.random.normal(0, 0.45, size=n_samples) # Realistic noise
    )

    churn_prob = 1 / (1 + np.exp(-logit))
    churn = (churn_prob > 0.50).astype(int)

    df = pd.DataFrame({
        "customer_id": customer_ids,
        "age": ages,
        "gender": genders,
        "region": regions,
        "tenure_months": tenure_months,
        "monthly_charges": monthly_charges,
        "total_spend": total_spend,
        "contract_type": contract_types,
        "payment_method": payment_methods,
        "support_tickets": support_tickets,
        "login_frequency": login_frequency,
        "last_login_days": last_login_days,
        "products_used": products_used,
        "discount_usage": discount_usage,
        "complaints": complaints,
        "satisfaction_score": satisfaction_score,
        "marketing_emails_opened": marketing_emails_opened,
        "monthly_orders": monthly_orders,
        "avg_order_value": avg_order_value,
        "preferred_login_device": preferred_login_device,
        "preferred_order_cat": preferred_order_cat,
        "churn": churn
    })

    # Inject slight realistic missing values (approx 1-2%) for data cleaning demonstration
    mask_sat = np.random.rand(n_samples) < 0.015
    df.loc[mask_sat, "satisfaction_score"] = np.nan

    mask_last = np.random.rand(n_samples) < 0.012
    df.loc[mask_last, "last_login_days"] = np.nan

    mask_charges = np.random.rand(n_samples) < 0.008
    df.loc[mask_charges, "monthly_charges"] = np.nan

    return df


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "customer_churn_raw.csv")

    df = generate_customer_data(n_samples=20000)
    df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Generated {len(df)} records saved to {out_path}")
    print(f"Overall Churn Rate: {df['churn'].mean():.2%}")
