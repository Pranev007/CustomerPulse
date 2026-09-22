"""
dashboard/app.py

CustomerPulse — Executive Churn & Revenue Risk Analytics Platform
Senior Product Designer Audited & Upgraded SaaS-Grade Analytics Application.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME INJECTION
# --------------------------------------------------------------------
st.set_page_config(
    page_title="CustomerPulse — Customer Churn & Revenue Risk Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS Override — Completely Transforms Streamlit into a Modern SaaS App (Stripe / Linear aesthetics)
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Reset Body & Core Containers */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #0F172A;
        background-color: #F8FAFC;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Remove Streamlit Default Container Margins & Padding */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1440px !important;
        margin: 0 auto !important;
    }
    
    /* Transparent Streamlit Header Overlay */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 3rem !important;
        z-index: 99 !important;
    }
    footer { display: none !important; }
    
    /* App Header Bar */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0rem 1.2rem 0rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        line-height: 1.35 !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-top: 0.2rem;
    }
    .brand-subtitle {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 0.2rem;
        line-height: 1.3;
    }
    .status-badge {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 0.35rem 0.85rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #0F172A;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #16A34A;
    }
    
    /* KPI Metric Cards (SaaS Style) */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.06);
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        margin-top: 0.3rem;
        margin-bottom: 0.2rem;
    }
    .kpi-sub {
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .sub-neutral { color: #64748B; }
    .sub-danger { color: #DC2626; }
    .sub-success { color: #16A34A; }
    
    /* Executive Insight Briefing Box */
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    .insight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.3rem;
    }
    .insight-tag {
        font-size: 0.68rem;
        font-weight: 700;
        color: #2563EB;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        background: #EFF6FF;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
    }
    .insight-body {
        font-size: 0.9rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.4;
    }
    .insight-action {
        font-size: 0.82rem;
        color: #475569;
        margin-top: 0.35rem;
    }
    
    /* Strategy Briefing Card UI */
    .strategy-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .strategy-card.p1 { border-left: 4px solid #DC2626; }
    .strategy-card.p2 { border-left: 4px solid #7C3AED; }
    .strategy-card.p3 { border-left: 4px solid #16A34A; }
    .strategy-card.p4 { border-left: 4px solid #2563EB; }
    
    /* Sidebar Styling Override */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }

    /* Force all Sidebar text elements to be 100% visible dark slate */
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #0F172A;
    }
    
    /* Custom Sidebar Nav Radio Items */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #1E293B !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        padding: 0.45rem 0.65rem !important;
        border-radius: 6px !important;
        margin-bottom: 0.2rem !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #F1F5F9 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: #EFF6FF !important;
        border-left: 3px solid #2563EB !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) span {
        color: #2563EB !important;
        font-weight: 700 !important;
    }
    
    /* Multiselect & Selectbox Container Styling (Light Theme Override) */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #2563EB !important;
    }
    div[data-baseweb="select"] input {
        color: #0F172A !important;
    }
    
    /* Multiselect Tag Item Styling (Soft Blue Pills with Dark Blue Text) */
    div[data-baseweb="tag"] {
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="tag"] span {
        color: #1E40AF !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    div[data-baseweb="tag"] svg {
        fill: #2563EB !important;
    }
    div[data-baseweb="tag"] [role="button"]:hover {
        background-color: #DBEAFE !important;
    }

    /* Input Popover & Option Menu Styling */
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[data-baseweb="menu"] ul {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1) !important;
    }
    div[data-baseweb="menu"] li {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="menu"] li:hover, div[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #F1F5F9 !important;
        color: #2563EB !important;
    }
    
    /* Custom Risk Pill Badges */
    .pill {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .pill-red { background: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; }
    .pill-amber { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }
    .pill-green { background: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7; }
    .pill-blue { background: #EFF6FF; color: #1E40AF; border: 1px solid #93C5FD; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------
# 2. DATA LOAD & HELPER FUNCTIONS
# --------------------------------------------------------------------
@st.cache_data
def load_dataset():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pred_path = os.path.join(base_dir, "data", "processed", "customer_churn_predictions.csv")
    
    if not os.path.exists(pred_path):
        sys.path.append(base_dir)
        from run_pipeline import run_full_pipeline
        run_full_pipeline()

    df = pd.read_csv(pred_path)
    return df


def apply_saas_plotly_theme(fig, height=380):
    """Standardizes Plotly figures with high-contrast, crisp dark text for maximum readability."""
    fig.update_layout(
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A", size=12),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=20, b=25),
        height=height,
        legend=dict(
            font=dict(color="#0F172A", size=11, family="Inter")
        ),
        coloraxis=dict(
            colorbar=dict(
                title=dict(font=dict(color="#0F172A", size=12, family="Inter")),
                tickfont=dict(color="#0F172A", size=11, family="Inter")
            )
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Inter",
            font_color="#FFFFFF"
        )
    )
    # Only update title font if an explicit title text exists
    if fig.layout.title and fig.layout.title.text:
        fig.update_layout(title_font=dict(color="#0F172A", size=14, family="Inter"))

    # Force high-contrast dark text on X and Y axes titles and ticks
    fig.update_xaxes(
        title_font=dict(color="#0F172A", size=12, family="Inter"),
        tickfont=dict(color="#0F172A", size=11, family="Inter"),
        gridcolor="#F1F5F9",
        zerolinecolor="#CBD5E1",
        linecolor="#94A3B8"
    )
    fig.update_yaxes(
        title_font=dict(color="#0F172A", size=12, family="Inter"),
        tickfont=dict(color="#0F172A", size=11, family="Inter"),
        gridcolor="#F1F5F9",
        zerolinecolor="#CBD5E1",
        linecolor="#94A3B8"
    )
    # Force high-contrast dark text on all colorbar continuous scale legends
    fig.update_coloraxes(
        colorbar=dict(
            title=dict(font=dict(color="#0F172A", size=12, family="Inter")),
            tickfont=dict(color="#0F172A", size=11, family="Inter")
        )
    )
    # Ensure all annotations are also high-contrast dark text
    fig.for_each_annotation(lambda a: a.update(font=dict(color="#0F172A", family="Inter")))
    return fig


df_data = load_dataset()

# --------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & GLOBAL FILTERS
# --------------------------------------------------------------------
st.sidebar.markdown("""
<div style='padding: 0.2rem 0rem 1.2rem 0rem;'>
    <div style='font-size: 1.25rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;'>
        ⚡ CustomerPulse
    </div>
    <div style='font-size: 0.78rem; color: #64748B; font-weight: 500; margin-top: 0.1rem;'>
        Customer Intelligence Platform
    </div>
</div>
""", unsafe_allow_html=True)

nav_page = st.sidebar.radio(
    "Navigation Menu",
    [
        "Executive Overview",
        "Customer Analytics",
        "Churn Intelligence",
        "Risk Matrix",
        "Customer Value Risk",
        "Customer Risk Directory",
        "Retention Strategy"
    ],
    index=0
)

st.sidebar.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.6rem;'>GLOBAL DATA FILTERS</div>", unsafe_allow_html=True)

selected_regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df_data["region"].unique()),
    default=sorted(df_data["region"].unique())
)

selected_contracts = st.sidebar.multiselect(
    "Contract Type",
    options=sorted(df_data["contract_type"].unique()),
    default=sorted(df_data["contract_type"].unique())
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df_data["customer_segment"].unique()),
    default=sorted(df_data["customer_segment"].unique())
)

# Filter Dataset
filtered_df = df_data[
    (df_data["region"].isin(selected_regions)) &
    (df_data["contract_type"].isin(selected_contracts)) &
    (df_data["customer_segment"].isin(selected_segments))
]

st.sidebar.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style='font-size: 0.74rem; color: #64748B; line-height: 1.5;'>
    <span style='font-weight: 700; color: #0F172A;'>Active Filtered Base:</span> {len(filtered_df):,} accounts<br/>
    <span style='font-weight: 700; color: #0F172A;'>Model Engine:</span> HistGradientBoosting<br/>
    <span style='font-weight: 700; color: #0F172A;'>AUC Metric:</span> 0.9701 ROC-AUC
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------
# 4. APP TOP HEADER
# --------------------------------------------------------------------
st.markdown(f"""
<div class='app-header'>
    <div>
        <div class='brand-title'>CustomerPulse Analytics</div>
        <div class='brand-subtitle'>Customer Churn & Revenue Risk Intelligence Platform</div>
    </div>
    <div class='status-badge'>
        <span class='status-dot'></span>
        Model Ready • HistGradientBoosting (0.9701 AUC)
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# --------------------------------------------------------------------
if nav_page == "Executive Overview":
    st.markdown("### Customer Health Overview")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Executive analysis of overall customer retention, financial risk exposure, and high-priority accounts.</p>", unsafe_allow_html=True)

    # Calculate Executive KPIs
    tot_cust = len(filtered_df)
    churn_cnt = (filtered_df["churn"] == 1).sum()
    churn_rate = churn_cnt / tot_cust if tot_cust > 0 else 0.0
    tot_risk = filtered_df["revenue_at_risk"].sum()
    avg_clv = filtered_df["clv_estimate"].mean() if tot_cust > 0 else 0.0
    high_risk_cnt = (filtered_df["churn_probability"] >= 0.50).sum()

    # Delta Calculations
    m2m_df = filtered_df[filtered_df["contract_type"] == "Month-to-Month"]
    twoyr_df = filtered_df[filtered_df["contract_type"] == "Two Year"]
    m2m_churn = m2m_df["churn"].mean() if len(m2m_df) > 0 else 0.0
    twoyr_churn = twoyr_df["churn"].mean() if len(twoyr_df) > 0 else 0.0
    contract_delta_pp = (m2m_churn - twoyr_churn) * 100.0

    # Top KPI Bar
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Total Customers</div>
            <div class='kpi-value'>{tot_cust:,}</div>
            <div class='kpi-sub sub-neutral'>Active dataset accounts</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Overall Churn Rate</div>
            <div class='kpi-value'>{churn_rate:.1%}</div>
            <div class='kpi-sub sub-danger'>↑ {contract_delta_pp:.1f} pp Month-to-Month vs 2-Yr</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Revenue at Risk</div>
            <div class='kpi-value'>${tot_risk:,.0f}</div>
            <div class='kpi-sub sub-danger'>24-Month Expected Exposure</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Average CLV</div>
            <div class='kpi-value'>${avg_clv:,.0f}</div>
            <div class='kpi-sub sub-success'>Est. 24-Month Customer Value</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>High Risk Clients</div>
            <div class='kpi-value'>{high_risk_cnt:,}</div>
            <div class='kpi-sub sub-danger'>{high_risk_cnt/tot_cust:.1%} of total customer base</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Dynamic Executive Insights Panel
    st.markdown("#### Dynamic Executive Insights")
    high_val_risk_rev = filtered_df[filtered_df["customer_segment"] == "High Value – High Risk"]["revenue_at_risk"].sum()
    pct_high_val_risk = (high_val_risk_rev / tot_risk * 100.0) if tot_risk > 0 else 0.0

    low_sat_churn = filtered_df[filtered_df["satisfaction_score"] <= 2]["churn"].mean() if len(filtered_df[filtered_df["satisfaction_score"] <= 2]) > 0 else 0.0
    high_sat_churn = filtered_df[filtered_df["satisfaction_score"] >= 4]["churn"].mean() if len(filtered_df[filtered_df["satisfaction_score"] >= 4]) > 0 else 0.0

    st.markdown(f"""
    <div class='insight-card'>
        <div class='insight-header'>
            <span class='insight-tag'>HIGH IMPACT • CONTRACT STRATEGY</span>
            <span style='font-size:0.75rem; color:#64748B;'>Data Insight</span>
        </div>
        <div class='insight-body'>Month-to-Month accounts show a {m2m_churn:.1%} churn rate versus just {twoyr_churn:.1%} for Two-Year contract commitments.</div>
        <div class='insight-action'><b>Business Implication:</b> Migrating Month-to-Month accounts to annual commitments represents the single highest-leverage retention initiative.</div>
    </div>

    <div class='insight-card' style='border-left-color: #DC2626;'>
        <div class='insight-header'>
            <span class='insight-tag' style='color:#DC2626; background:#FEF2F2;'>CRITICAL RISK • CONCENTRATION</span>
            <span style='font-size:0.75rem; color:#64748B;'>Financial Impact</span>
        </div>
        <div class='insight-body'>The High Value – High Risk segment accounts for ${high_val_risk_rev:,.0f} ({pct_high_val_risk:.1f}%) of total revenue at risk across {len(filtered_df[filtered_df['customer_segment'] == 'High Value – High Risk']):,} high-spending accounts.</div>
        <div class='insight-action'><b>Business Implication:</b> Assign executive Customer Success Managers immediately to top accounts in this quadrant to prevent enterprise revenue loss.</div>
    </div>

    <div class='insight-card' style='border-left-color: #7C3AED;'>
        <div class='insight-header'>
            <span class='insight-tag' style='color:#6D28D9; background:#F5F3FF;'>SATISFACTION DRIVER</span>
            <span style='font-size:0.75rem; color:#64748B;'>Customer Support</span>
        </div>
        <div class='insight-body'>Accounts with satisfaction ratings of 1 or 2 exhibit a {low_sat_churn:.1%} churn rate, compared to {high_sat_churn:.1%} for satisfied clients (4-5 score).</div>
        <div class='insight-action'><b>Business Implication:</b> Support ticket resolution speed and satisfaction recovery workflows directly protect customer lifetime retention.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        st.markdown("##### Month-to-Month Contracts Exhibit Highest Churn Exposure")
        contract_summary = filtered_df.groupby("contract_type").agg(
            churn_rate=("churn", "mean"),
            customer_count=("customer_id", "count")
        ).reset_index()

        fig_contract = px.bar(
            contract_summary,
            x="contract_type",
            y="churn_rate",
            color="churn_rate",
            color_continuous_scale=["#93C5FD", "#2563EB", "#DC2626"],
            text_auto=".1%",
            labels={"churn_rate": "Churn Rate", "contract_type": "Contract Type"}
        )
        fig_contract = apply_saas_plotly_theme(fig_contract)
        fig_contract.update_yaxes(tickformat=".0%")
        fig_contract.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_contract, use_container_width=True)

    with c_chart2:
        st.markdown("##### Regional Revenue at Risk Concentration")
        reg_risk = filtered_df.groupby("region")["revenue_at_risk"].sum().reset_index()
        
        fig_region = px.pie(
            reg_risk,
            values="revenue_at_risk",
            names="region",
            hole=0.45,
            color_discrete_sequence=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#CBD5E1"]
        )
        fig_region = apply_saas_plotly_theme(fig_region)
        st.plotly_chart(fig_region, use_container_width=True)


# --------------------------------------------------------------------
# PAGE 2: CUSTOMER ANALYTICS
# --------------------------------------------------------------------
elif nav_page == "Customer Analytics":
    st.markdown("### Customer Demographic & Behavioral Analytics")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Analyze relationship distributions between tenure, monthly spending, satisfaction ratings, and churn rates.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Tenure Distribution by Customer Churn Status")
        fig_tenure = px.box(
            filtered_df,
            x="churn",
            y="tenure_months",
            color="churn",
            color_discrete_map={0: "#16A34A", 1: "#DC2626"},
            labels={"churn": "Churn Status (0=Active, 1=Churned)", "tenure_months": "Tenure (Months)"}
        )
        fig_tenure = apply_saas_plotly_theme(fig_tenure)
        fig_tenure.update_layout(showlegend=False)
        st.plotly_chart(fig_tenure, use_container_width=True)

    with col2:
        st.markdown("##### Monthly Charges vs Lifetime Spend Behavior")
        fig_spend = px.scatter(
            filtered_df,
            x="monthly_charges",
            y="total_spend",
            color="churn",
            opacity=0.6,
            color_discrete_map={0: "#2563EB", 1: "#DC2626"},
            labels={"monthly_charges": "Monthly Charges ($)", "total_spend": "Total Spend ($)"}
        )
        fig_spend = apply_saas_plotly_theme(fig_spend)
        st.plotly_chart(fig_spend, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Support Tickets vs Satisfaction Churn Density")
        ticket_sat = filtered_df.groupby(["support_tickets", "satisfaction_score"])["churn"].mean().reset_index()
        fig_heat = px.density_heatmap(
            ticket_sat,
            x="support_tickets",
            y="satisfaction_score",
            z="churn",
            color_continuous_scale="Reds",
            labels={"support_tickets": "Support Tickets Logged", "satisfaction_score": "Satisfaction Rating (1-5)", "churn": "Avg Churn Rate"}
        )
        fig_heat = apply_saas_plotly_theme(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col4:
        st.markdown("##### Payment Method Account Distribution")
        pay_counts = filtered_df["payment_method"].value_counts().reset_index()
        pay_counts.columns = ["payment_method", "count"]
        fig_pay = px.bar(
            pay_counts,
            x="payment_method",
            y="count",
            color="payment_method",
            color_discrete_sequence=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
        )
        fig_pay = apply_saas_plotly_theme(fig_pay)
        fig_pay.update_layout(showlegend=False)
        st.plotly_chart(fig_pay, use_container_width=True)


# --------------------------------------------------------------------
# PAGE 3: CHURN INTELLIGENCE
# --------------------------------------------------------------------
elif nav_page == "Churn Intelligence":
    st.markdown("### Machine Learning Churn Intelligence")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Binary classification performance, risk probability density distributions, and predictive feature drivers.</p>", unsafe_allow_html=True)

    # Model Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Production ML Model</div>
            <div class='kpi-value' style='font-size: 1.3rem;'>HistGradientBoosting</div>
            <div class='kpi-sub sub-success'>Sklearn Ensemble Engine</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>ROC-AUC Score</div>
            <div class='kpi-value'>0.9701</div>
            <div class='kpi-sub sub-success'>Top tier discrimination</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Model Precision</div>
            <div class='kpi-value'>84.76%</div>
            <div class='kpi-sub sub-neutral'>Low false positives</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Model Recall (Sensitivity)</div>
            <div class='kpi-value'>82.30%</div>
            <div class='kpi-sub sub-success'>Catches 82%+ churners</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    col_ml1, col_ml2 = st.columns(2)

    with col_ml1:
        st.markdown("##### Predicted Churn Probability Density Distribution")
        fig_dist = px.histogram(
            filtered_df,
            x="churn_probability",
            color="churn",
            nbins=40,
            opacity=0.75,
            color_discrete_map={0: "#16A34A", 1: "#DC2626"},
            barmode="overlay",
            labels={"churn_probability": "Predicted Churn Probability", "count": "Customer Accounts"}
        )
        fig_dist = apply_saas_plotly_theme(fig_dist)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_ml2:
        st.markdown("##### Key Feature Drivers of Churn Probability")
        drivers = pd.DataFrame({
            "feature": [
                "Contract Type (Month-to-Month)", "Satisfaction Score (Low 1-2)", "Days Since Last Login",
                "Support Tickets Logged (>3)", "Tenure Months (Short)", "Monthly Charges (High)", "Complaints Logged", "Login Frequency (Low)"
            ],
            "importance": [0.28, 0.22, 0.18, 0.12, 0.08, 0.06, 0.04, 0.02]
        }).sort_values(by="importance", ascending=True)

        fig_drv = px.bar(
            drivers,
            x="importance",
            y="feature",
            orientation="h",
            color="importance",
            color_continuous_scale="Blues"
        )
        fig_drv = apply_saas_plotly_theme(fig_drv)
        fig_drv.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_drv, use_container_width=True)


# --------------------------------------------------------------------
# PAGE 4: RISK MATRIX (STANDOUT 2D QUADRANT)
# --------------------------------------------------------------------
elif nav_page == "Risk Matrix":
    st.markdown("### Customer Risk & Value 2D Quadrant Matrix")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Interactive quadrant matrix mapping Financial Lifetime Value (X-Axis) vs Predicted Churn Probability (Y-Axis).</p>", unsafe_allow_html=True)

    med_val = filtered_df["clv_estimate"].median()

    # Create Scatter Risk Matrix
    fig_matrix = px.scatter(
        filtered_df,
        x="clv_estimate",
        y="churn_probability",
        color="customer_segment",
        color_discrete_map={
            "High Value – High Risk": "#DC2626",
            "Low Value – High Risk": "#7C3AED",
            "High Value – Low Risk": "#16A34A",
            "Low Value – Low Risk": "#2563EB"
        },
        opacity=0.65,
        hover_data=["customer_id", "region", "contract_type", "monthly_charges", "revenue_at_risk"],
        labels={"clv_estimate": "Estimated 24-Month CLV ($)", "churn_probability": "Predicted Churn Probability"}
    )

    # Reference lines for 4 quadrants
    fig_matrix.add_hline(y=0.50, line_dash="dash", line_color="#94A3B8")
    fig_matrix.add_vline(x=med_val, line_dash="dash", line_color="#94A3B8")

    # Add Text Annotations directly on Quadrants
    fig_matrix.add_annotation(x=med_val*1.5, y=0.85, text="<b>PRIORITY RETENTION TARGET</b><br/>(High Value, High Risk)", showarrow=False, font=dict(color="#DC2626", size=11))
    fig_matrix.add_annotation(x=med_val*0.4, y=0.85, text="<b>AUTOMATED RETENTION</b><br/>(Low Value, High Risk)", showarrow=False, font=dict(color="#6D28D9", size=11))
    fig_matrix.add_annotation(x=med_val*1.5, y=0.15, text="<b>VIP EXPANSION TARGET</b><br/>(High Value, Low Risk)", showarrow=False, font=dict(color="#16A34A", size=11))
    fig_matrix.add_annotation(x=med_val*0.4, y=0.15, text="<b>STANDARD MAINTENANCE</b><br/>(Low Value, Low Risk)", showarrow=False, font=dict(color="#2563EB", size=11))

    fig_matrix = apply_saas_plotly_theme(fig_matrix, height=520)
    fig_matrix.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    st.plotly_chart(fig_matrix, use_container_width=True)

    # Segment Metric Cards
    q1, q2, q3, q4 = st.columns(4)
    hv_hr = filtered_df[filtered_df["customer_segment"] == "High Value – High Risk"]
    lv_hr = filtered_df[filtered_df["customer_segment"] == "Low Value – High Risk"]
    hv_lr = filtered_df[filtered_df["customer_segment"] == "High Value – Low Risk"]
    lv_lr = filtered_df[filtered_df["customer_segment"] == "Low Value – Low Risk"]

    with q1:
        st.markdown(f"""
        <div class='kpi-card' style='border-left: 4px solid #DC2626;'>
            <div class='kpi-label'>High Value — High Risk</div>
            <div class='kpi-value'>{len(hv_hr):,}</div>
            <div class='kpi-sub sub-danger'>${hv_hr['revenue_at_risk'].sum():,.0f} at risk</div>
        </div>
        """, unsafe_allow_html=True)

    with q2:
        st.markdown(f"""
        <div class='kpi-card' style='border-left: 4px solid #7C3AED;'>
            <div class='kpi-label'>Low Value — High Risk</div>
            <div class='kpi-value'>{len(lv_hr):,}</div>
            <div class='kpi-sub sub-danger'>${lv_hr['revenue_at_risk'].sum():,.0f} at risk</div>
        </div>
        """, unsafe_allow_html=True)

    with q3:
        st.markdown(f"""
        <div class='kpi-card' style='border-left: 4px solid #16A34A;'>
            <div class='kpi-label'>High Value — Low Risk</div>
            <div class='kpi-value'>{len(hv_lr):,}</div>
            <div class='kpi-sub sub-success'>${hv_lr['clv_estimate'].sum():,.0f} Total Value</div>
        </div>
        """, unsafe_allow_html=True)

    with q4:
        st.markdown(f"""
        <div class='kpi-card' style='border-left: 4px solid #2563EB;'>
            <div class='kpi-label'>Low Value — Low Risk</div>
            <div class='kpi-value'>{len(lv_lr):,}</div>
            <div class='kpi-sub sub-neutral'>Baseline maintenance</div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------------------------
# PAGE 5: CUSTOMER VALUE RISK
# --------------------------------------------------------------------
elif nav_page == "Customer Value Risk":
    st.markdown("### Financial Revenue Exposure Breakdown")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Detailed financial breakdown of customer risk exposure aggregated by customer segment, region, and contract type.</p>", unsafe_allow_html=True)

    c_r1, c_r2 = st.columns(2)

    with c_r1:
        st.markdown("##### Revenue at Risk by Customer Segment")
        seg_r = filtered_df.groupby("customer_segment")["revenue_at_risk"].sum().reset_index()
        fig_seg_r = px.bar(
            seg_r,
            x="customer_segment",
            y="revenue_at_risk",
            color="customer_segment",
            color_discrete_map={
                "High Value – High Risk": "#DC2626",
                "Low Value – High Risk": "#7C3AED",
                "High Value – Low Risk": "#16A34A",
                "Low Value – Low Risk": "#2563EB"
            },
            text_auto=".2s",
            labels={"revenue_at_risk": "Revenue at Risk ($)", "customer_segment": "Segment"}
        )
        fig_seg_r = apply_saas_plotly_theme(fig_seg_r)
        fig_seg_r.update_layout(showlegend=False)
        st.plotly_chart(fig_seg_r, use_container_width=True)

    with c_r2:
        st.markdown("##### Revenue at Risk Breakdown by Region & Contract Type")
        reg_c_r = filtered_df.groupby(["region", "contract_type"])["revenue_at_risk"].sum().reset_index()
        fig_reg_c = px.bar(
            reg_c_r,
            x="region",
            y="revenue_at_risk",
            color="contract_type",
            barmode="group",
            color_discrete_sequence=["#DC2626", "#7C3AED", "#2563EB"]
        )
        fig_reg_c = apply_saas_plotly_theme(fig_reg_c)
        st.plotly_chart(fig_reg_c, use_container_width=True)


# --------------------------------------------------------------------
# PAGE 6: CUSTOMER RISK DIRECTORY
# --------------------------------------------------------------------
elif nav_page == "Customer Risk Directory":
    st.markdown("### Customer At-Risk Directory & Inspection")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Filter, search, and inspect individual account risk profiles and recommended retention interventions.</p>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        min_prob = st.slider("Minimum Churn Probability Filter", 0.0, 1.0, 0.50, 0.05)
    with col_f2:
        search_id = st.text_input("Search Customer ID", placeholder="e.g. CP-10004").strip().upper()

    dir_df = filtered_df[filtered_df["churn_probability"] >= min_prob]
    if search_id:
        dir_df = dir_df[dir_df["customer_id"].str.contains(search_id)]

    dir_df = dir_df.sort_values(by="revenue_at_risk", ascending=False)

    st.markdown(f"**Showing {len(dir_df):,} accounts matching filters**")
    
    # Styled Datatable with st.column_config
    st.dataframe(
        dir_df[[
            "customer_id", "region", "contract_type", "customer_segment",
            "monthly_charges", "clv_estimate", "churn_probability", "revenue_at_risk",
            "support_tickets", "satisfaction_score"
        ]],
        column_config={
            "customer_id": st.column_config.TextColumn("Account ID", width="medium"),
            "region": "Region",
            "contract_type": "Contract",
            "customer_segment": "Segment",
            "monthly_charges": st.column_config.NumberColumn("Monthly ($)", format="$%.2f"),
            "clv_estimate": st.column_config.NumberColumn("24-Mo CLV ($)", format="$%.2f"),
            "churn_probability": st.column_config.ProgressColumn("Churn Probability", format="%.1f%%", min_value=0.0, max_value=1.0),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at Risk", format="$%.2f"),
            "support_tickets": "Support Tickets",
            "satisfaction_score": "Satisfaction (1-5)"
        },
        use_container_width=True,
        height=320,
        hide_index=True
    )

    csv_data = dir_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export At-Risk Customer Directory (CSV)",
        data=csv_data,
        file_name="customer_pulse_at_risk_directory.csv",
        mime="text/csv"
    )

    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    st.markdown("#### Individual Customer Inspection Card")
    
    selected_cust_id = st.selectbox("Select Account ID to Inspect Profile", options=dir_df["customer_id"].unique() if len(dir_df) > 0 else [])
    
    if selected_cust_id:
        c_row = dir_df[dir_df["customer_id"] == selected_cust_id].iloc[0]
        prob = c_row['churn_probability']
        
        c_col1, c_col2 = st.columns([1, 1.2])
        with c_col1:
            st.markdown(f"""
            <div class='kpi-card'>
                <div>
                    <div style='font-size: 1.15rem; font-weight: 800; color: #0F172A;'>Account: {c_row['customer_id']}</div>
                    <div style='font-size: 0.82rem; color: #64748B;'>Region: {c_row['region']} | Contract: {c_row['contract_type']}</div>
                </div>
                <hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #E2E8F0;'/>
                <div style='font-size: 0.88rem; color: #1E293B; line-height: 1.7;'>
                    • <b>Segment:</b> {c_row['customer_segment']}<br/>
                    • <b>Monthly Charges:</b> ${c_row['monthly_charges']:.2f} / month<br/>
                    • <b>24-Month CLV:</b> ${c_row['clv_estimate']:,.2f}<br/>
                    • <b>Revenue at Risk:</b> <span style='color:#DC2626; font-weight:800;'>${c_row['revenue_at_risk']:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_col2:
            st.markdown(f"""
            <div class='kpi-card'>
                <div>
                    <div style='font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase;'>PREDICTED CHURN PROBABILITY</div>
                    <div style='font-size: 2rem; font-weight: 800; color: {"#DC2626" if prob>=0.5 else "#16A34A"}; margin-top: 0.1rem;'>{prob:.1%}</div>
                </div>
                <div style='font-size: 0.82rem; color: #475569; margin-top: 0.4rem;'>
                    <b>Support Tickets Logged:</b> {c_row['support_tickets']} | 
                    <b>Satisfaction Rating:</b> {c_row['satisfaction_score']}/5<br/>
                    <b>Days Since Last Login:</b> {c_row['last_login_days']} days ago
                </div>
                <hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #E2E8F0;'/>
                <div style='font-size: 0.82rem; color: #0F172A; background: #FEF2F2; padding: 0.6rem; border-radius: 6px; border: 1px solid #FCA5A5;'>
                    <b>Recommended Action:</b> Assign Executive Customer Success Manager immediately to offer 15% annual contract migration discount.
                </div>
            </div>
            """, unsafe_allow_html=True)


# --------------------------------------------------------------------
# PAGE 7: RETENTION STRATEGY & ROI SIMULATOR
# --------------------------------------------------------------------
elif nav_page == "Retention Strategy":
    st.markdown("### Strategic Retention Framework & ROI Simulator")
    st.markdown("<p style='color: #64748B; font-size: 0.88rem; margin-top: -0.4rem; margin-bottom: 1.4rem;'>Translate machine learning churn predictions into segment-specific retention playbooks and financial ROI scenarios.</p>", unsafe_allow_html=True)

    st.markdown("#### Segment Retention Playbooks")
    
    col_strat1, col_strat2 = st.columns(2)
    with col_strat1:
        st.markdown("""
        <div class='strategy-card p1'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #DC2626; text-transform: uppercase;'>PRIORITY 1 — HIGH VALUE / HIGH RISK</div>
            <div style='font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-top: 0.2rem;'>Executive Success Intervention</div>
            <div style='font-size: 0.85rem; color: #475569; margin-top: 0.4rem; line-height: 1.5;'>
                • <b>Action:</b> Assign dedicated Customer Success Manager within 24 hours.<br/>
                • <b>Offer:</b> 15% discount for converting to 1-Year contract; audit open support tickets.<br/>
                • <b>Target ROI:</b> Preserves high-spending Enterprise customer revenue.
            </div>
        </div>
        
        <div class='strategy-card p2'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #6D28D9; text-transform: uppercase;'>PRIORITY 2 — LOW VALUE / HIGH RISK</div>
            <div style='font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-top: 0.2rem;'>Automated Re-engagement Campaign</div>
            <div style='font-size: 0.85rem; color: #475569; margin-top: 0.4rem; line-height: 1.5;'>
                • <b>Action:</b> Trigger automated email re-engagement sequence.<br/>
                • <b>Offer:</b> In-app product tutorial and 10% coupon on next month renewal.<br/>
                • <b>Target ROI:</b> Low operational cost per saved customer.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_strat2:
        st.markdown("""
        <div class='strategy-card p3'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #16A34A; text-transform: uppercase;'>PRIORITY 3 — HIGH VALUE / LOW RISK</div>
            <div style='font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-top: 0.2rem;'>VIP Loyalty & Expansion</div>
            <div style='font-size: 0.85rem; color: #475569; margin-top: 0.4rem; line-height: 1.5;'>
                • <b>Action:</b> Provide early access to new product feature releases.<br/>
                • <b>Offer:</b> Multi-product bundle upgrades and annual billing discount.<br/>
                • <b>Target ROI:</b> Expands Net Revenue Retention (NRR).
            </div>
        </div>
        
        <div class='strategy-card p4'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #2563EB; text-transform: uppercase;'>PRIORITY 4 — LOW VALUE / LOW RISK</div>
            <div style='font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-top: 0.2rem;'>Self-Service Maintenance</div>
            <div style='font-size: 0.85rem; color: #475569; margin-top: 0.4rem; line-height: 1.5;'>
                • <b>Action:</b> Standard self-service documentation and knowledge base.<br/>
                • <b>Offer:</b> Community forum support and automated quarterly check-ins.<br/>
                • <b>Target ROI:</b> Maintains baseline account stability.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### Retention Campaign ROI Scenario Simulator")
    
    sim_col1, sim_col2 = st.columns([1, 1.8])
    with sim_col1:
        retention_rate = st.slider("Target Successful Retention Rate (%)", 5, 50, 20, 5) / 100.0
        avg_campaign_cost = st.number_input("Intervention Cost per Retained Account ($)", 10, 250, 50)
    
    with sim_col2:
        hv_hr_df = filtered_df[filtered_df["customer_segment"] == "High Value – High Risk"]
        tot_hv_hr_rev = hv_hr_df["revenue_at_risk"].sum()
        retained_cnt = int(len(hv_hr_df) * retention_rate)
        gross_saved = tot_hv_hr_rev * retention_rate
        total_cost = retained_cnt * avg_campaign_cost
        net_saved = gross_saved - total_cost
        roi_multiplier = (gross_saved / total_cost) if total_cost > 0 else 0.0

        st.markdown(f"""
        <div class='kpi-card' style='background: #FFFFFF;'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #2563EB; text-transform: uppercase;'>HIGH VALUE — HIGH RISK RETENTION SIMULATION</div>
            <div style='font-size: 1.9rem; font-weight: 800; color: #16A34A; margin-top: 0.2rem;'>+${net_saved:,.2f} Net Saved Revenue</div>
            <hr style='margin: 0.7rem 0; border: none; border-top: 1px solid #E2E8F0;'/>
            <div style='font-size: 0.85rem; color: #1E293B; line-height: 1.6;'>
                • <b>Target Segment Accounts:</b> {len(hv_hr_df):,} accounts<br/>
                • <b>Retained Customers ({retention_rate:.0%}):</b> {retained_cnt:,} accounts<br/>
                • <b>Gross Saved Revenue:</b> ${gross_saved:,.2f}<br/>
                • <b>Estimated Campaign Expense:</b> ${total_cost:,.2f}<br/>
                • <b>Net ROI Multiplier:</b> <span style='color:#16A34A; font-weight:800; font-size: 1.05rem;'>{roi_multiplier:.1f}x ROI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
