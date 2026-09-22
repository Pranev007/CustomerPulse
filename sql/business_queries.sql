-- ====================================================================
-- CUSTOMER PULSE — BUSINESS ANALYST SQL QUERY SUITE
-- Database: SQLite (data/processed/customer_pulse.db)
-- Table Analyzed: customer_predictions
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: EXECUTIVE CHURN SUMMARY & OVERALL METRICS
-- Demonstrates: AGGREGATION, COUNT DISTINCT, ROUND, CASE WHEN
-- --------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(CASE WHEN churn = 0 THEN 1 ELSE 0 END) AS active_customers,
    SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_arpu,
    ROUND(AVG(total_spend), 2) AS avg_total_spend,
    ROUND(SUM(revenue_at_risk), 2) AS total_revenue_at_risk
FROM customer_predictions;


-- --------------------------------------------------------------------
-- QUERY 2: REGIONAL CHURN RATE & REVENUE LOSS BREAKDOWN
-- Demonstrates: GROUP BY, AGGREGATION, PERCENTAGE CALCULATION
-- --------------------------------------------------------------------
SELECT 
    region,
    COUNT(customer_id) AS customer_count,
    SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) / COUNT(customer_id), 2) AS regional_churn_rate_pct,
    ROUND(SUM(CASE WHEN churn = 0 THEN monthly_charges ELSE 0 END), 2) AS active_monthly_revenue,
    ROUND(SUM(CASE WHEN churn = 1 THEN monthly_charges ELSE 0 END), 2) AS lost_monthly_revenue,
    ROUND(SUM(revenue_at_risk), 2) AS regional_revenue_at_risk
FROM customer_predictions
GROUP BY region
ORDER BY regional_revenue_at_risk DESC;


-- --------------------------------------------------------------------
-- QUERY 3: CHURN BY CONTRACT TYPE & PAYMENT METHOD
-- Demonstrates: MULTI-COLUMN GROUP BY, CONDITIONAL AGGREGATION
-- --------------------------------------------------------------------
SELECT 
    contract_type,
    payment_method,
    COUNT(customer_id) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(100.0 * AVG(churn), 2) AS churn_rate_pct,
    ROUND(AVG(tenure_months), 1) AS avg_tenure_months,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customer_predictions
GROUP BY contract_type, payment_method
ORDER BY churn_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 4: AVERAGE CUSTOMER VALUE & SPEND BY RFM CUSTOMER SEGMENT
-- Demonstrates: SEGMENTATION ANALYSIS, AGGREGATION
-- --------------------------------------------------------------------
SELECT 
    customer_segment,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_spend,
    ROUND(AVG(clv_estimate), 2) AS avg_estimated_clv,
    ROUND(AVG(churn_probability), 4) AS avg_churn_probability,
    ROUND(SUM(revenue_at_risk), 2) AS segment_revenue_at_risk
FROM customer_predictions
GROUP BY customer_segment
ORDER BY segment_revenue_at_risk DESC;


-- --------------------------------------------------------------------
-- QUERY 5: REVENUE AT RISK BY SEGMENT (WITH RISK SHARE %)
-- Demonstrates: CTE (Common Table Expression), WINDOW AGGREGATION
-- --------------------------------------------------------------------
WITH SegmentRisk AS (
    SELECT 
        customer_segment,
        COUNT(customer_id) AS customer_count,
        SUM(revenue_at_risk) AS segment_risk
    FROM customer_predictions
    GROUP BY customer_segment
)
SELECT 
    customer_segment,
    customer_count,
    ROUND(segment_risk, 2) AS total_revenue_at_risk,
    ROUND(100.0 * segment_risk / (SELECT SUM(segment_risk) FROM SegmentRisk), 2) AS risk_share_pct
FROM SegmentRisk
ORDER BY total_revenue_at_risk DESC;


-- --------------------------------------------------------------------
-- QUERY 6: TOP 20 HIGH-VALUE CUSTOMERS MOST LIKELY TO CHURN
-- Demonstrates: CTE, FILTERING, SORTING, LIMIT
-- --------------------------------------------------------------------
WITH HighRiskHighValue AS (
    SELECT 
        customer_id,
        region,
        contract_type,
        monthly_charges,
        clv_estimate,
        churn_probability,
        revenue_at_risk,
        support_tickets,
        satisfaction_score
    FROM customer_predictions
    WHERE churn_probability >= 0.50
)
SELECT 
    customer_id,
    region,
    contract_type,
    monthly_charges,
    clv_estimate,
    ROUND(churn_probability, 4) AS churn_probability,
    ROUND(revenue_at_risk, 2) AS revenue_at_risk,
    support_tickets,
    satisfaction_score
FROM HighRiskHighValue
ORDER BY revenue_at_risk DESC
LIMIT 20;


-- --------------------------------------------------------------------
-- QUERY 7: SUPPORT TICKET INTENSITY VS CHURN RATE
-- Demonstrates: CASE WHEN BUCKETING, GROUP BY
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN support_tickets = 0 THEN '0 Tickets'
        WHEN support_tickets BETWEEN 1 AND 2 THEN '1-2 Tickets'
        WHEN support_tickets BETWEEN 3 AND 5 THEN '3-5 Tickets'
        ELSE '6+ Tickets (High Ticket Intensity)'
    END AS ticket_bucket,
    COUNT(customer_id) AS customer_count,
    SUM(churn) AS churned_count,
    ROUND(100.0 * AVG(churn), 2) AS churn_rate_pct,
    ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction_score
FROM customer_predictions
GROUP BY ticket_bucket
ORDER BY churn_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 8: UNCHURNED HIGH-VALUE CUSTOMERS AT IMMEDIATE ATTRITION RISK
-- Demonstrates: MULTI-CONDITION WHERE CLAUSE, BUSINESS PRIORITIZATION
-- --------------------------------------------------------------------
SELECT 
    customer_id,
    region,
    contract_type,
    monthly_charges,
    support_tickets,
    satisfaction_score,
    last_login_days,
    ROUND(churn_probability, 4) AS churn_probability,
    ROUND(revenue_at_risk, 2) AS revenue_at_risk
FROM customer_predictions
WHERE churn = 0 
  AND monthly_charges >= 75.0
  AND (satisfaction_score <= 2 OR support_tickets >= 4 OR last_login_days >= 20)
ORDER BY revenue_at_risk DESC
LIMIT 25;


-- --------------------------------------------------------------------
-- QUERY 9: REGIONAL REVENUE AT RISK RANKING USING WINDOW FUNCTIONS
-- Demonstrates: WINDOW FUNCTION RANK() OVER ()
-- --------------------------------------------------------------------
SELECT 
    region,
    COUNT(customer_id) AS total_customers,
    ROUND(SUM(revenue_at_risk), 2) AS total_revenue_at_risk,
    RANK() OVER (ORDER BY SUM(revenue_at_risk) DESC) AS risk_rank
FROM customer_predictions
GROUP BY region;


-- --------------------------------------------------------------------
-- QUERY 10: TENURE COHORT ANALYSIS & CHURN EVOLUTION
-- Demonstrates: COHORT BUCKETING, MULTI-METRIC AGGREGATION
-- --------------------------------------------------------------------
SELECT 
    tenure_group,
    COUNT(customer_id) AS cohort_size,
    SUM(churn) AS churned_count,
    ROUND(100.0 * AVG(churn), 2) AS cohort_churn_rate_pct,
    ROUND(AVG(engagement_score), 1) AS avg_engagement_score,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(revenue_at_risk), 2) AS cohort_revenue_at_risk
FROM customer_predictions
GROUP BY tenure_group
ORDER BY cohort_churn_rate_pct DESC;
