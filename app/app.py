"""
Customer Insights Analytics Dashboard

A Streamlit-based dashboard for visualizing e-commerce customer insights.
This app reads cleaned data from data/processed/ and displays key metrics
and trends for business stakeholders.

Run with: streamlit run app/app.py

Author: Customer Insights Analytics Team
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analysis import (
    calculate_revenue_metrics,
    calculate_monthly_sales_trends,
    get_top_customers_by_revenue
)


# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Insights Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_processed_data():
    """
    Load cleaned data from the processed data directory.
    
    Returns:
        DataFrame or None if file not found
    """
    data_path = Path(__file__).parent.parent / 'data' / 'processed' / 'cleaned_data.csv'
    
    if not data_path.exists():
        return None
    
    df = pd.read_csv(data_path)
    
    # Convert date column if present
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    return df


# -----------------------------------------------------------------------------
# Dashboard Components
# -----------------------------------------------------------------------------
def display_header():
    """Display the dashboard header and description."""
    st.title("📊 Customer Insights Analytics")
    st.markdown("""
    **Real-time insights into customer behavior and business performance.**
    
    This dashboard provides key metrics and visualizations to help stakeholders 
    understand customer purchasing patterns, revenue trends, and high-value segments.
    """)
    st.divider()


def display_kpi_metrics(metrics: dict):
    """
    Display key performance indicators in a metric card layout.
    
    Args:
        metrics: Dictionary containing calculated KPIs
    """
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${metrics.get('total_revenue', 0):,.2f}",
            help="Sum of all transaction values"
        )
    
    with col2:
        st.metric(
            label="Total Orders",
            value=f"{metrics.get('total_orders', 0):,}",
            help="Number of unique invoices"
        )
    
    with col3:
        st.metric(
            label="Total Customers",
            value=f"{metrics.get('total_customers', 0):,}",
            help="Number of unique customers"
        )
    
    with col4:
        st.metric(
            label="Avg Order Value",
            value=f"${metrics.get('avg_order_value', 0):,.2f}",
            help="Average revenue per order"
        )


def display_revenue_trend(monthly_data: pd.DataFrame):
    """
    Display a revenue trend chart.
    
    Args:
        monthly_data: DataFrame with monthly aggregated revenue data
    """
    st.subheader("📅 Monthly Revenue Trend")
    
    fig = px.line(
        monthly_data,
        x='YearMonth',
        y='Revenue',
        markers=True,
        title='Revenue Over Time'
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8)
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)


def display_orders_customers_trend(monthly_data: pd.DataFrame):
    """
    Display orders and customers trend on dual axis.
    
    Args:
        monthly_data: DataFrame with monthly aggregated data
    """
    st.subheader("👥 Orders & Customers Trend")
    
    fig = go.Figure()
    
    # Add Orders trace
    fig.add_trace(go.Bar(
        x=monthly_data['YearMonth'],
        y=monthly_data['Orders'],
        name='Orders',
        marker_color='#2ecc71'
    ))
    
    # Add Customers trace on secondary axis
    fig.add_trace(go.Scatter(
        x=monthly_data['YearMonth'],
        y=monthly_data['Customers'],
        name='Unique Customers',
        yaxis='y2',
        line=dict(color='#e74c3c', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis=dict(title='Number of Orders', side='left'),
        yaxis2=dict(title='Unique Customers', side='right', overlaying='y'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_top_customers(top_customers: pd.DataFrame):
    """
    Display top customers table.
    
    Args:
        top_customers: DataFrame with top customers by revenue
    """
    st.subheader("🏆 Top 10 Customers by Revenue")
    
    # Format for display
    display_df = top_customers[['Rank', 'CustomerID', 'TotalRevenue', 'OrderCount', 'RevenueShare']].copy()
    display_df['TotalRevenue'] = display_df['TotalRevenue'].apply(lambda x: f"${x:,.2f}")
    display_df['RevenueShare'] = display_df['RevenueShare'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def display_data_not_found():
    """Display message when processed data is not found."""
    st.warning("⚠️ Processed data not found!")
    st.markdown("""
    **To get started:**
    
    1. Place your raw e-commerce dataset in `data/raw/ecommerce_data.csv`
    2. Run the data cleaning pipeline:
    
    ```python
    from src.data_cleaning import clean_data_pipeline, save_cleaned_data
    
    # Clean the data
    clean_df = clean_data_pipeline(
        filepath='data/raw/ecommerce_data.csv',
        drop_missing_cols=['CustomerID'],
        date_columns=['InvoiceDate']
    )
    
    # Save to processed folder
    save_cleaned_data(clean_df, 'data/processed/cleaned_data.csv')
    ```
    
    3. Refresh this dashboard.
    
    **Expected CSV columns:** InvoiceNo, StockCode, Description, Quantity, 
    InvoiceDate, UnitPrice, CustomerID, Country
    """)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
def display_sidebar(df: pd.DataFrame):
    """
    Display sidebar with filters and information.
    
    Args:
        df: The loaded DataFrame
    """
    with st.sidebar:
        st.header("🔧 Dashboard Info")
        
        if df is not None:
            st.success("✅ Data loaded successfully")
            st.metric("Total Records", f"{len(df):,}")
            
            if 'InvoiceDate' in df.columns:
                min_date = df['InvoiceDate'].min()
                max_date = df['InvoiceDate'].max()
                st.write(f"**Date Range:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        
        st.divider()
        
        st.markdown("""
        ### About This Dashboard
        
        This analytics dashboard provides insights into:
        - Revenue performance
        - Customer purchasing trends
        - High-value customer identification
        
        **Data Source:** Processed e-commerce transactions
        
        **Last Updated:** Real-time on page load
        """)
        
        st.divider()
        
        st.markdown("""
        ### Contact
        
        For questions or support, please reach out to the Analytics Team.
        """)


# -----------------------------------------------------------------------------
# Main Application
# -----------------------------------------------------------------------------
def main():
    """Main application entry point."""
    # Display header
    display_header()
    
    # Load data
    df = load_processed_data()
    
    # Display sidebar
    display_sidebar(df)
    
    # Check if data exists
    if df is None:
        display_data_not_found()
        return
    
    # Calculate metrics
    metrics = calculate_revenue_metrics(df)
    
    # Display KPIs
    display_kpi_metrics(metrics)
    
    st.divider()
    
    # Display charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            monthly_data = calculate_monthly_sales_trends(df)
            display_revenue_trend(monthly_data)
        except Exception as e:
            st.error(f"Could not generate revenue trend: {e}")
    
    with col2:
        try:
            monthly_data = calculate_monthly_sales_trends(df)
            display_orders_customers_trend(monthly_data)
        except Exception as e:
            st.error(f"Could not generate orders/customers trend: {e}")
    
    st.divider()
    
    # Display top customers
    try:
        top_customers = get_top_customers_by_revenue(df, top_n=10)
        display_top_customers(top_customers)
    except Exception as e:
        st.error(f"Could not generate top customers: {e}")
    
    # Footer
    st.divider()
    st.caption("Customer Insights Analytics Dashboard | Built with Streamlit")


if __name__ == "__main__":
    main()
