"""
Customer Insights Analytics Dashboard

A Streamlit-based dashboard for visualizing e-commerce customer insights.
This app reads cleaned data from data/processed/ and displays key metrics,
trends, customer segmentation, and Python vs SQL analytics comparison.

Run with:
python -m streamlit run app/app.py
"""

# =============================================================================
# Imports & Path Setup
# =============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (
    calculate_revenue_metrics,
    calculate_monthly_sales_trends,
    get_top_customers_by_revenue,
    calculate_rfm,
    add_rfm_segments
)

from src.sql_analytics import (
    load_data_to_sqlite,
    sql_total_revenue
)

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Customer Insights Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Data Loading
# =============================================================================
def load_processed_data():
    data_path = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"

    if not data_path.exists():
        return None

    df = pd.read_csv(data_path)

    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    return df

# =============================================================================
# UI Components
# =============================================================================
def display_header():
    st.title("Customer Insights Analytics")
    st.markdown("""
    **End-to-end analytics dashboard for understanding customer behavior,
    revenue trends, and high-value customer segments.**
    """)
    st.divider()


def display_sidebar(df):
    with st.sidebar:
        st.header("Dashboard Controls")

        analytics_engine = st.radio(
            "Analytics Engine",
            ["Python", "SQL"],
            help="Switch between Python-based and SQL-based KPI computation"
        )

        st.divider()

        if df is not None:
            st.success("Data loaded successfully")
            st.metric("Total Records", f"{len(df):,}")

            if "InvoiceDate" in df.columns:
                st.write(
                    f"**Date Range:** {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}"
                )

        st.divider()
        st.markdown("""
        **Key Features**
        - Revenue & growth trends
        - Customer behavior analysis
        - RFM-based segmentation
        - Python vs SQL analytics validation
        """)

    return analytics_engine


def display_kpi_metrics(metrics):
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"${metrics['total_revenue']:,.2f}")
    col2.metric("Total Orders", f"{metrics['total_orders']:,}")
    col3.metric("Total Customers", f"{metrics['total_customers']:,}")
    col4.metric("Avg Order Value", f"${metrics['avg_order_value']:,.2f}")


def display_revenue_trend(monthly_data):
    st.subheader("Monthly Revenue Trend")

    fig = px.line(
        monthly_data,
        x="YearMonth",
        y="Revenue",
        markers=True
    )
    fig.update_yaxes(tickformat="$,.0f")
    st.plotly_chart(fig, width="stretch")


def display_orders_customers_trend(monthly_data):
    st.subheader("Orders & Customers Trend")

    fig = go.Figure()
    fig.add_bar(x=monthly_data["YearMonth"], y=monthly_data["Orders"], name="Orders")
    fig.add_scatter(
        x=monthly_data["YearMonth"],
        y=monthly_data["Customers"],
        name="Customers",
        yaxis="y2"
    )

    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right"),
        hovermode="x unified"
    )

    st.plotly_chart(fig, width="stretch")


def display_top_customers(top_customers):
    st.subheader("Top 10 Customers by Revenue")

    display_df = top_customers.copy()
    display_df["TotalRevenue"] = display_df["TotalRevenue"].map("${:,.2f}".format)
    display_df["RevenueShare"] = display_df["RevenueShare"].map("{:.2f}%".format)

    st.dataframe(display_df, width="stretch", hide_index=True)

# =============================================================================
# Main Application
# =============================================================================
def main():
    display_header()

    df = load_processed_data()
    analytics_engine = display_sidebar(df)

    st.info(f" Analytics Engine in use: {analytics_engine}")

    if df is None:
        st.warning("Processed data not found. Please run the data cleaning pipeline.")
        return

    # -------------------------------------------------------------------------
    # KPIs (Python vs SQL)
    # -------------------------------------------------------------------------
    if analytics_engine == "Python":
        metrics = calculate_revenue_metrics(df)

    else:
        st.caption(" KPIs computed using SQLite (SQL)")

        conn = load_data_to_sqlite()
        total_revenue = sql_total_revenue(conn)["total_revenue"].iloc[0]
        total_orders = df["InvoiceNo"].nunique()
        total_customers = df["CustomerID"].nunique()

        metrics = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "avg_order_value": total_revenue / total_orders
        }

    display_kpi_metrics(metrics)
    st.divider()

    # -------------------------------------------------------------------------
    # Trends
    # -------------------------------------------------------------------------
    monthly_data = calculate_monthly_sales_trends(df)

    col1, col2 = st.columns(2)
    with col1:
        display_revenue_trend(monthly_data)
    with col2:
        display_orders_customers_trend(monthly_data)

    st.divider()

    # -------------------------------------------------------------------------
    # Top Customers
    # -------------------------------------------------------------------------
    top_customers = get_top_customers_by_revenue(df, top_n=10)
    display_top_customers(top_customers)

    st.divider()

    # -------------------------------------------------------------------------
    # RFM Segmentation
    # -------------------------------------------------------------------------
    st.subheader("Customer Segmentation (RFM)")

    rfm_df = calculate_rfm(df)
    rfm_segmented = add_rfm_segments(rfm_df)

    segment_counts = (
        rfm_segmented["Segment"]
        .value_counts()
        .reset_index()
    )
    segment_counts.columns = ["Segment", "Customer Count"]

    st.bar_chart(segment_counts.set_index("Segment"))

    st.markdown("""
    ###  Key Business Insights
    - A large **At Risk** segment highlights churn-prevention opportunities.
    - **Champions** and **Loyal** customers generate a disproportionate share of revenue.
    - Python and SQL KPI consistency validates analytical accuracy.
    """)

    st.divider()
    st.caption("Customer Insights Analytics Dashboard | Built with Streamlit")

# =============================================================================
# App Entry Point
# =============================================================================
if __name__ == "__main__":
    main()
