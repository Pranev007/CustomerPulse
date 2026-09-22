"""
build_notebooks.py

Generates the 3 structured Jupyter Notebooks for CustomerPulse:
1. 01_data_cleaning_eda.ipynb
2. 02_business_analysis.ipynb
3. 03_churn_model.ipynb
"""

import os
import nbformat as nbf


def make_nb_01():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 01 — CustomerPulse: Data Cleaning & Exploratory Data Analysis (EDA)

## Executive Summary
This notebook documents the data loading, data cleaning, validation, and exploratory visualization of 20,000 customer records from the CustomerPulse E-Commerce / Subscription Churn dataset.

### Objectives:
1. Detect & handle missing values, duplicates, and extreme outliers.
2. Validate feature data types and range boundaries.
3. Perform univariate and bivariate EDA to answer core business questions around churn drivers.
"""),
        nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 6)

# Load Raw Data
raw_path = "../data/raw/customer_churn_raw.csv"
df_raw = pd.read_csv(raw_path)
print(f"Raw Dataset Shape: {df_raw.shape}")
df_raw.head()
"""),
        nbf.v4.new_markdown_cell("""## 1. Data Cleaning & Missing Value Audit"""),
        nbf.v4.new_code_cell("""# Check missing values
missing = df_raw.isnull().sum()
print("Missing values count:")
print(missing[missing > 0])

# Perform cleaning using src/data_processing.py
import sys
sys.path.append("../")
from src.data_processing import DataCleaner

proc_path = "../data/processed/customer_churn_cleaned.csv"
cleaner = DataCleaner(raw_path)
df_clean = cleaner.clean_pipeline(proc_path)

print("\\nCleaned Dataset Shape:", df_clean.shape)
"""),
        nbf.v4.new_markdown_cell("""## 2. Exploratory Data Analysis (EDA)

### 2.1 Overall Churn Distribution"""),
        nbf.v4.new_code_cell("""plt.figure(figsize=(6, 4))
ax = sns.countplot(data=df_clean, x="churn", palette=["#2ecc71", "#e74c3c"])
plt.title("Overall Customer Churn Distribution (0 = Active, 1 = Churned)", fontsize=14, fontweight="bold")
plt.xlabel("Churn Status")
plt.ylabel("Customer Count")

for p in ax.patches:
    height = p.get_height()
    ax.annotate(f"{height:,} ({height/len(df_clean):.1%})",
                (p.get_x() + p.get_width() / 2., height / 2),
                ha='center', va='center', color='white', fontweight='bold', fontsize=12)

plt.show()
"""),
        nbf.v4.new_markdown_cell("""### 2.2 Churn by Contract Type & Payment Method"""),
        nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=df_clean, x="contract_type", y="churn", ax=axes[0], ci=None, palette="Blues_r")
axes[0].set_title("Churn Rate by Contract Type", fontsize=12, fontweight="bold")
axes[0].set_ylabel("Churn Rate")

sns.barplot(data=df_clean, x="payment_method", y="churn", ax=axes[1], ci=None, palette="Reds_r")
axes[1].set_title("Churn Rate by Payment Method", fontsize=12, fontweight="bold")
axes[1].set_ylabel("Churn Rate")
axes[1].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.show()
"""),
        nbf.v4.new_markdown_cell("""### 2.3 Impact of Support Tickets & Satisfaction Score"""),
        nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=df_clean, x="support_tickets", y="churn", ax=axes[0], ci=None, palette="magma")
axes[0].set_title("Churn Rate by Support Tickets Logged", fontsize=12, fontweight="bold")
axes[0].set_xlabel("Number of Support Tickets")

sns.barplot(data=df_clean, x="satisfaction_score", y="churn", ax=axes[1], ci=None, palette="viridis")
axes[1].set_title("Churn Rate by Customer Satisfaction Score", fontsize=12, fontweight="bold")
axes[1].set_xlabel("Satisfaction Score (1 to 5)")

plt.tight_layout()
plt.show()
""")
    ]
    return nb


def make_nb_02():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 02 — CustomerPulse: Executive Business KPI Analysis & RFM Customer Segmentation

## Executive Summary
This notebook calculates core financial Business Analyst KPIs, performs RFM (Recency, Frequency, Monetary) Customer Segmentation, and models $ / ₹ Revenue at Risk.
"""),
        nbf.v4.new_code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("../")
from src.feature_engineering import engineer_features
from src.business_analysis import BusinessAnalytics

proc_path = "../data/processed/customer_churn_cleaned.csv"
df_clean = pd.read_csv(proc_path)
df_fe = engineer_features(df_clean)

ba = BusinessAnalytics(df_fe)
kpis = ba.calculate_executive_kpis()

print("=========================================")
print("        BUSINESS ANALYTICS KPIS          ")
print("=========================================")
for k, v in kpis.items():
    print(f"• {k:<25}: {v:,.2f}" if isinstance(v, float) else f"• {k:<25}: {v:,}")
"""),
        nbf.v4.new_markdown_cell("""## 1. RFM Customer Segmentation & Risk Matrix"""),
        nbf.v4.new_code_cell("""df_risk = ba.calculate_revenue_at_risk()
df_seg = ba.assign_customer_segments()

segment_summary = df_seg.groupby("customer_segment").agg(
    customer_count=("customer_id", "count"),
    avg_churn_prob=("churn_probability", "mean"),
    total_revenue_at_risk=("revenue_at_risk", "sum")
).reset_index()

print("--- CUSTOMER SEGMENTATION SUMMARY ---")
print(segment_summary)

plt.figure(figsize=(9, 5))
sns.barplot(data=segment_summary, x="customer_segment", y="total_revenue_at_risk", palette="rocket")
plt.title("Total Revenue at Risk by Customer Segment ($)", fontsize=14, fontweight="bold")
plt.xlabel("Customer Segment")
plt.ylabel("Revenue at Risk ($)")
plt.xticks(rotation=15)
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 2. Top At-Risk High Value Customers"""),
        nbf.v4.new_code_cell("""top_at_risk = ba.get_top_at_risk_customers(10)
top_at_risk
""")
    ]
    return nb


def make_nb_03():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 03 — CustomerPulse: Machine Learning Churn Model & Driver Interpretability

## Executive Summary
This notebook trains, evaluates, and compares standard classification algorithms (Logistic Regression, Random Forest, Gradient Boosting) for churn prediction, prioritizes Precision/Recall trade-offs, and extracts feature importances.
"""),
        nbf.v4.new_code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("../")
from src.feature_engineering import engineer_features
from src.model import ChurnModelPipeline

proc_path = "../data/processed/customer_churn_cleaned.csv"
df_clean = pd.read_csv(proc_path)
df_fe = engineer_features(df_clean)

trainer = ChurnModelPipeline()
results = trainer.train_and_evaluate(df_fe)

# Display tabular performance summary
metrics_df = pd.DataFrame(results).T[["accuracy", "precision", "recall", "f1_score", "roc_auc"]]
metrics_df
"""),
        nbf.v4.new_markdown_cell("""## 1. Model Feature Importance Ranking"""),
        nbf.v4.new_code_cell("""df_imp = trainer.get_feature_importances(df_fe).head(12)

plt.figure(figsize=(10, 6))
sns.barplot(data=df_imp, x="importance", y="feature", palette="mako")
plt.title(f"Top 12 Churn Drivers — {trainer.best_model_name}", fontsize=14, fontweight="bold")
plt.xlabel("Relative Feature Importance")
plt.ylabel("Feature")
plt.show()
""")
    ]
    return nb


def build_all_notebooks():
    nb_dir = os.path.join(os.path.dirname(__file__), "notebooks")
    os.makedirs(nb_dir, exist_ok=True)

    nb1 = make_nb_01()
    with open(os.path.join(nb_dir, "01_data_cleaning_eda.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb1, f)

    nb2 = make_nb_02()
    with open(os.path.join(nb_dir, "02_business_analysis.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb2, f)

    nb3 = make_nb_03()
    with open(os.path.join(nb_dir, "03_churn_model.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb3, f)

    print("[SUCCESS] Successfully created 3 Jupyter Notebooks under notebooks/")


if __name__ == "__main__":
    build_all_notebooks()
