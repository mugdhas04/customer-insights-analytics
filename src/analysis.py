"""
Analysis Module for Customer Insights Analytics

This module provides functions for analyzing cleaned e-commerce data
to generate actionable business insights. Functions are designed to
support both ad-hoc analysis and dashboard integration.

Author: Customer Insights Analytics Team
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_revenue_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate key revenue metrics from the dataset.
    
    Metrics calculated:
    - Total Revenue: Sum of all transaction values
    - Average Order Value (AOV): Average revenue per order
    - Average Revenue per Customer: Revenue divided by unique customers
    
    Args:
        df: Cleaned DataFrame with 'Revenue', 'InvoiceNo', and 'CustomerID' columns
    
    Returns:
        Dictionary containing revenue metrics
    
    Example:
        >>> metrics = calculate_revenue_metrics(clean_df)
        >>> print(f"Total Revenue: ${metrics['total_revenue']:,.2f}")
    """
    metrics = {}
    
    # Total Revenue
    if 'Revenue' in df.columns:
        metrics['total_revenue'] = df['Revenue'].sum()
    else:
        # Calculate if not present
        if 'Quantity' in df.columns and 'UnitPrice' in df.columns:
            metrics['total_revenue'] = (df['Quantity'] * df['UnitPrice']).sum()
        else:
            metrics['total_revenue'] = 0
    
    # Total Orders
    if 'InvoiceNo' in df.columns:
        metrics['total_orders'] = df['InvoiceNo'].nunique()
    else:
        metrics['total_orders'] = len(df)
    
    # Total Customers
    if 'CustomerID' in df.columns:
        metrics['total_customers'] = df['CustomerID'].nunique()
    else:
        metrics['total_customers'] = 0
    
    # Average Order Value (AOV)
    if metrics['total_orders'] > 0:
        metrics['avg_order_value'] = metrics['total_revenue'] / metrics['total_orders']
    else:
        metrics['avg_order_value'] = 0
    
    # Average Revenue per Customer
    if metrics['total_customers'] > 0:
        metrics['avg_revenue_per_customer'] = metrics['total_revenue'] / metrics['total_customers']
    else:
        metrics['avg_revenue_per_customer'] = 0
    
    return metrics


def calculate_monthly_sales_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly sales trends for time-series analysis.
    
    This function aggregates data by month to identify:
    - Revenue patterns over time
    - Seasonality in customer orders
    - Growth or decline trends
    
    Args:
        df: Cleaned DataFrame with 'InvoiceDate' (datetime) and 'Revenue' columns
    
    Returns:
        DataFrame with monthly aggregated metrics:
        - YearMonth: Period identifier
        - Revenue: Total revenue for the month
        - Orders: Number of unique orders
        - Customers: Number of unique customers
        - AvgOrderValue: Average order value for the month
    
    Example:
        >>> monthly_trends = calculate_monthly_sales_trends(clean_df)
        >>> monthly_trends.plot(x='YearMonth', y='Revenue', kind='line')
    """
    # Ensure we have the required columns
    if 'InvoiceDate' not in df.columns:
        raise ValueError("DataFrame must contain 'InvoiceDate' column")
    
    # Create a copy and ensure datetime
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['InvoiceDate']):
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Create YearMonth column if not present
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    
    # Calculate Revenue if not present
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Aggregate by month
    monthly_data = df.groupby('YearMonth').agg({
        'Revenue': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    monthly_data.columns = ['YearMonth', 'Revenue', 'Orders', 'Customers', 'UnitsSold']
    
    # Calculate Average Order Value
    monthly_data['AvgOrderValue'] = monthly_data['Revenue'] / monthly_data['Orders']
    
    # Convert YearMonth to string for better display
    monthly_data['YearMonth'] = monthly_data['YearMonth'].astype(str)
    
    # Sort by date
    monthly_data = monthly_data.sort_values('YearMonth').reset_index(drop=True)
    
    return monthly_data


def get_top_customers_by_revenue(
    df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Identify top customers by total monetary value.
    
    This analysis helps identify:
    - High-value customers for retention programs
    - VIP customer segments
    - Revenue concentration (Pareto principle)
    
    Args:
        df: Cleaned DataFrame with 'CustomerID' and 'Revenue' columns
        top_n: Number of top customers to return (default: 10)
    
    Returns:
        DataFrame with top customers ranked by revenue:
        - CustomerID: Unique customer identifier
        - TotalRevenue: Sum of all purchases
        - OrderCount: Number of orders placed
        - AvgOrderValue: Average order value
        - RevenueShare: Percentage of total revenue
    
    Example:
        >>> top_customers = get_top_customers_by_revenue(clean_df, top_n=20)
        >>> print(top_customers.head())
    """
    if 'CustomerID' not in df.columns:
        raise ValueError("DataFrame must contain 'CustomerID' column")
    
    df = df.copy()
    
    # Calculate Revenue if not present
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Aggregate by customer
    customer_data = df.groupby('CustomerID').agg({
        'Revenue': 'sum',
        'InvoiceNo': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    # Rename columns
    customer_data.columns = ['CustomerID', 'TotalRevenue', 'OrderCount', 'TotalUnits']
    
    # Calculate additional metrics
    customer_data['AvgOrderValue'] = customer_data['TotalRevenue'] / customer_data['OrderCount']
    
    # Calculate revenue share
    total_revenue = customer_data['TotalRevenue'].sum()
    customer_data['RevenueShare'] = (customer_data['TotalRevenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue and get top N
    top_customers = customer_data.nlargest(top_n, 'TotalRevenue').reset_index(drop=True)
    
    # Add rank
    top_customers.insert(0, 'Rank', range(1, len(top_customers) + 1))
    
    return top_customers


def get_top_products_by_revenue(
    df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Identify top-selling products by revenue.
    
    This analysis supports:
    - Inventory planning decisions
    - Product portfolio optimization
    - Marketing focus areas
    
    Args:
        df: Cleaned DataFrame with 'StockCode', 'Description', and 'Revenue' columns
        top_n: Number of top products to return (default: 10)
    
    Returns:
        DataFrame with top products ranked by revenue
    """
    df = df.copy()
    
    # Calculate Revenue if not present
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Group by product
    product_cols = ['StockCode']
    if 'Description' in df.columns:
        product_cols.append('Description')
    
    product_data = df.groupby(product_cols).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    
    # Rename columns
    rename_map = {'InvoiceNo': 'OrderCount', 'Quantity': 'UnitsSold'}
    product_data = product_data.rename(columns=rename_map)
    
    # Sort and get top N
    top_products = product_data.nlargest(top_n, 'Revenue').reset_index(drop=True)
    
    # Add rank
    top_products.insert(0, 'Rank', range(1, len(top_products) + 1))
    
    return top_products


def get_sales_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales metrics by country.
    
    This geographic analysis helps identify:
    - Key markets by revenue
    - Expansion opportunities
    - Regional performance patterns
    
    Args:
        df: Cleaned DataFrame with 'Country' and 'Revenue' columns
    
    Returns:
        DataFrame with sales metrics by country, sorted by revenue
    """
    if 'Country' not in df.columns:
        raise ValueError("DataFrame must contain 'Country' column")
    
    df = df.copy()
    
    # Calculate Revenue if not present
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Aggregate by country
    country_data = df.groupby('Country').agg({
        'Revenue': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    # Rename columns
    country_data.columns = ['Country', 'Revenue', 'Orders', 'Customers', 'UnitsSold']
    
    # Calculate revenue share
    total_revenue = country_data['Revenue'].sum()
    country_data['RevenueShare'] = (country_data['Revenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue
    country_data = country_data.sort_values('Revenue', ascending=False).reset_index(drop=True)
    
    return country_data


def calculate_customer_segments(
    df: pd.DataFrame,
    revenue_quantiles: Tuple[float, float] = (0.25, 0.75)
) -> pd.DataFrame:
    """
    Segment customers based on their monetary value.
    
    Segments:
    - High Value: Top 25% by revenue
    - Medium Value: Middle 50% by revenue
    - Low Value: Bottom 25% by revenue
    
    Args:
        df: Cleaned DataFrame with customer transaction data
        revenue_quantiles: Tuple of (low, high) quantile thresholds
    
    Returns:
        DataFrame with customer IDs and their segments
    """
    df = df.copy()
    
    # Calculate Revenue if not present
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Calculate customer revenue
    customer_revenue = df.groupby('CustomerID')['Revenue'].sum().reset_index()
    customer_revenue.columns = ['CustomerID', 'TotalRevenue']
    
    # Calculate quantile thresholds
    low_threshold = customer_revenue['TotalRevenue'].quantile(revenue_quantiles[0])
    high_threshold = customer_revenue['TotalRevenue'].quantile(revenue_quantiles[1])
    
    # Assign segments
    def assign_segment(revenue):
        if revenue >= high_threshold:
            return 'High Value'
        elif revenue >= low_threshold:
            return 'Medium Value'
        else:
            return 'Low Value'
    
    customer_revenue['Segment'] = customer_revenue['TotalRevenue'].apply(assign_segment)
    
    # Add segment statistics
    segment_stats = customer_revenue.groupby('Segment').agg({
        'CustomerID': 'count',
        'TotalRevenue': ['sum', 'mean']
    }).round(2)
    
    segment_stats.columns = ['CustomerCount', 'TotalRevenue', 'AvgRevenue']
    segment_stats = segment_stats.reset_index()
    
    return customer_revenue, segment_stats


def generate_summary_report(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive summary report of the dataset.
    
    This function combines multiple analyses into a single report
    suitable for executive dashboards or automated reporting.
    
    Args:
        df: Cleaned DataFrame with transaction data
    
    Returns:
        Dictionary containing:
        - kpis: Key performance indicators
        - monthly_trends: Monthly aggregated data
        - top_customers: Top 10 customers by revenue
        - top_products: Top 10 products by revenue
        - country_breakdown: Sales by country
    """
    report = {}
    
    # Calculate KPIs
    report['kpis'] = calculate_revenue_metrics(df)
    
    # Monthly trends
    try:
        report['monthly_trends'] = calculate_monthly_sales_trends(df)
    except Exception as e:
        report['monthly_trends'] = None
        print(f"Warning: Could not calculate monthly trends: {e}")
    
    # Top customers
    try:
        report['top_customers'] = get_top_customers_by_revenue(df, top_n=10)
    except Exception as e:
        report['top_customers'] = None
        print(f"Warning: Could not calculate top customers: {e}")
    
    # Top products
    try:
        report['top_products'] = get_top_products_by_revenue(df, top_n=10)
    except Exception as e:
        report['top_products'] = None
        print(f"Warning: Could not calculate top products: {e}")
    
    # Country breakdown
    try:
        report['country_breakdown'] = get_sales_by_country(df)
    except Exception as e:
        report['country_breakdown'] = None
        print(f"Warning: Could not calculate country breakdown: {e}")
    
    return report
