# CustomerPulse — Customer Churn & Revenue Risk Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)](https://www.sqlite.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)

**CustomerPulse** is an enterprise-grade Business Analytics, Predictive Machine Learning, and Financial Risk Platform designed to quantify customer churn risk, identify account dropoff drivers, and optimize retention campaign ROI.

---

## 📌 Executive Summary & Key Results

| Metric | Empirical Result | Business Context |
| :--- | :--- | :--- |
| **Analyzed Customer Base** | **20,000 Accounts** | Kaggle E-Commerce / Subscription Benchmark Schema |
| **Baseline Churn Rate** | **26.70%** | 5,340 churned customers out of 20,000 accounts |
| **Average Monthly ARPU** | **$74.85 / mo** | Average recurring revenue per user |
| **Average 24-Month CLV** | **$1,796.31** | Estimated 24-month customer lifetime value |
| **Total Revenue at Risk** | **$9,984,381.91** | Quantified 24-month revenue exposure |
| **Best Predictive Model** | **HistGradientBoosting** | **0.9701 ROC-AUC**, 91.33% Accuracy, **82.30% Recall** |

---

## 💡 Key Business Insights

* **Contract Risk Concentration:** Month-to-Month contract holders exhibit a **43.6% churn rate** versus **2.3%** for Two-Year commitments (4.2x risk multiplier).
* **Financial Risk Exposure:** The *High Value – High Risk* segment accounts for **59.66% ($5.95M)** of total revenue at risk across 2,956 accounts.
* **Service Quality Drivers:** Accounts with satisfaction ratings of 1–2 or support tickets >3 experience a **3.5x increase in churn probability**.

---

## 📈 Machine Learning Performance

Three binary classification models were evaluated on an 80/20 stratified train/test split:

| Model | Accuracy | Precision | Recall | **ROC-AUC** |
| :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 91.67% | 85.30% | 83.15% | **0.9697** |
| **Random Forest** | 90.32% | 86.50% | 75.56% | **0.9608** |
| **HistGradientBoosting (Best)** | **91.33%** | **84.76%** | **82.30%** | **0.9701** |

> 💡 **Methodology:** Revenue at Risk is calculated as $\text{Revenue Risk}_i = P(\text{Churn}_i) \times \text{CLV}_i$.

---

## 🖥️ Platform Features & Architecture

* **Interactive Streamlit SaaS Dashboard (`dashboard/app.py`):** 7-page analytics application featuring top KPI metrics, dynamic Executive Insight Briefings, interactive 2D Scatter Risk Matrix, Customer Risk Directory with search/inspection drawers, and a What-If Retention Campaign ROI Simulator.
* **SQL Analytics Suite (`sql/business_queries.sql`):** 10 analytical SQL queries using CTEs, window functions (`RANK() OVER`), and aggregations executed against SQLite (`customer_pulse.db`).
* **Jupyter Notebook Suite (`notebooks/`):** 3 executed notebooks covering Data Cleaning/EDA, Business Analysis, and ML Modeling.

---

## 🚀 Quick Start & How to Run

```bash
# 1. Clone repository & setup virtual environment
git clone https://github.com/Pranev007/CustomerPulse.git
cd CustomerPulse
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies & execute pipeline
pip install -r requirements.txt
python run_pipeline.py

# 3. Launch the Streamlit SaaS Analytics Platform
streamlit run dashboard/app.py
```

---

## 📁 Directory Structure

```
CustomerPulse/
├── data/
│   ├── raw/
│   │   └── customer_churn_raw.csv
│   └── processed/
│       ├── customer_churn_cleaned.csv
│       ├── customer_churn_predictions.csv
│       └── customer_pulse.db
├── notebooks/
│   ├── 01_data_cleaning_eda.ipynb
│   ├── 02_business_analysis.ipynb
│   └── 03_churn_model.ipynb
├── sql/
│   └── business_queries.sql
├── src/
│   ├── data_generator.py
│   ├── data_processing.py
│   ├── feature_engineering.py
│   ├── model.py
│   └── business_analysis.py
├── dashboard/
│   └── app.py
├── run_pipeline.py
├── build_notebooks.py
├── README.md
├── requirements.txt
└── .gitignore
```
