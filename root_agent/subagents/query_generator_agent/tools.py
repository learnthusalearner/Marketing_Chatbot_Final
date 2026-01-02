
import os
import psycopg2
import json
from typing import Dict, Any

# --- Supabase DB Connection ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")

def run_query(query: str, params: tuple = ()) -> Dict[str, Any]:
    conn = None
    try:
        conn = psycopg2.connect(
            host=SUPABASE_URL,
            database=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT
        )
        cur = conn.cursor()
        cur.execute(query, params)

        if cur.description:
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            result = [dict(zip(cols, row)) for row in rows]
        else:
            conn.commit()
            result = {"rows_affected": cur.rowcount}

        cur.close()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()

# ==============================
#  15 Core Dashboards
# ==============================

def impressions_reach_analysis(): ...
def ctr_tracker(): ...
def cpc_optimization(): ...
def spend_allocation_monitor(): ...
def sales_conversion_tracker(): ...
def acos_roas_analyzer(): ...
def asin_performance_split(): ...
def keyword_efficiency(): ...
def trend_time_analysis(): ...
def wasted_spend_detector(): ...
def high_roi_opportunities(): ...
def portfolio_currency_impact(): ...
def campaign_lifecycle_dashboard(): ...
def quality_of_engagement(): ...
def management_summary(): ...

# ==============================
#  Executive-Level Extras
# ==============================

def top_performing_campaigns():
    """Campaigns with best sales + ROAS"""
    query = """
        SELECT campaign_name,
               SUM(total_sales) AS sales,
               ROUND(SUM(total_sales)/NULLIF(SUM(spend),0), 2) AS roas
        FROM ads_performance
        GROUP BY campaign_name
        ORDER BY sales DESC, roas DESC
        LIMIT 10;
    """
    return run_query(query)

def worst_performing_campaigns():
    """High spend, low return campaigns"""
    query = """
        SELECT campaign_name,
               SUM(spend) AS spend,
               SUM(total_sales) AS sales,
               ROUND(100.0 * SUM(spend)/NULLIF(SUM(total_sales),0), 2) AS acos
        FROM ads_performance
        GROUP BY campaign_name
        HAVING SUM(spend) > 500 AND SUM(total_sales) < 100
        ORDER BY acos DESC
        LIMIT 10;
    """
    return run_query(query)

def daily_profitability_summary():
    """Profit = Sales – Spend by date"""
    query = """
        SELECT date,
               SUM(total_sales) AS sales,
               SUM(spend) AS spend,
               SUM(total_sales) - SUM(spend) AS profit
        FROM ads_performance
        GROUP BY date
        ORDER BY date ASC;
    """
    return run_query(query)

def portfolio_level_profitability():
    """Portfolio comparison of ACOS & ROAS"""
    query = """
        SELECT portfolio_name,
               SUM(spend) AS spend,
               SUM(total_sales) AS sales,
               ROUND(100.0 * SUM(spend)/NULLIF(SUM(total_sales),0), 2) AS acos,
               ROUND(SUM(total_sales)/NULLIF(SUM(spend),0), 2) AS roas
        FROM ads_performance
        GROUP BY portfolio_name
        ORDER BY roas DESC;
    """
    return run_query(query)

def asin_profitability_ranking():
    """Top profitable ASINs"""
    query = """
        SELECT advertised_asin,
               SUM(total_sales) AS sales,
               SUM(spend) AS spend,
               SUM(total_sales) - SUM(spend) AS profit
        FROM ads_performance
        GROUP BY advertised_asin
        ORDER BY profit DESC
        LIMIT 20;
    """
    return run_query(query)

def keyword_growth_trends():
    """Top growing keywords over time"""
    query = """
        SELECT customer_search_term, DATE_TRUNC('week', date) AS week,
               SUM(clicks) AS clicks, SUM(total_sales) AS sales
        FROM ads_performance
        GROUP BY customer_search_term, week
        ORDER BY week ASC, sales DESC;
    """
    return run_query(query)

def year_month_rollup():
    """Executive year-month summary"""
    query = """
        SELECT DATE_TRUNC('month', date) AS month,
               SUM(spend) AS spend,
               SUM(total_sales) AS sales,
               ROUND(SUM(total_sales)/NULLIF(SUM(spend),0), 2) AS roas,
               ROUND(100.0 * SUM(spend)/NULLIF(SUM(total_sales),0), 2) AS acos
        FROM ads_performance
        GROUP BY month
        ORDER BY month ASC;
    """
    return run_query(query)
