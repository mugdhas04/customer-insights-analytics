"""
Data Cleaning Module for Customer Insights Analytics

This module provides reusable functions for cleaning and preprocessing
e-commerce transaction data. All functions are designed to be modular
and can be used independently or chained together in a pipeline.

Author: Customer Insights Analytics Team
"""

import pandas as pd
import numpy as np
from typing import Optional, List


def load_data(filepath: str, encoding: str = 'ISO-8859-1') -> pd.DataFrame:
    """
    Load CSV data from the specified filepath.
    
    Args:
        filepath: Path to the CSV file (relative or absolute)
        encoding: File encoding (default: ISO-8859-1 for e-commerce datasets)
    
    Returns:
        DataFrame containing the loaded data
    
    Raises:
        FileNotFoundError: If the specified file does not exist
    """
    df = pd.read_csv(filepath, encoding=encoding)
    print(f"Loaded {len(df):,} records from {filepath}")
    return df


def handle_missing_values(
    df: pd.DataFrame,
    drop_columns: Optional[List[str]] = None,
    fill_values: Optional[dict] = None
) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Strategy:
    - Drop rows where specified columns have missing values
    - Fill missing values with specified defaults
    - For CustomerID, rows with missing values are typically dropped
      as they cannot be attributed to customer-level analysis
    
    Args:
        df: Input DataFrame
        drop_columns: List of columns where rows with missing values should be dropped
        fill_values: Dictionary mapping column names to fill values
    
    Returns:
        DataFrame with missing values handled
    
    Example:
        >>> df = handle_missing_values(
        ...     df,
        ...     drop_columns=['CustomerID'],
        ...     fill_values={'Description': 'Unknown'}
        ... )
    """
    df = df.copy()
    initial_count = len(df)
    
    # Drop rows with missing values in specified columns
    if drop_columns:
        for col in drop_columns:
            if col in df.columns:
                df = df.dropna(subset=[col])
                
    # Fill missing values with specified defaults
    if fill_values:
        for col, value in fill_values.items():
            if col in df.columns:
                df[col] = df[col].fillna(value)
    
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        print(f"Removed {dropped_count:,} rows with missing values")
    
    return df


def convert_date_columns(
    df: pd.DataFrame,
    date_columns: List[str],
    date_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Convert string columns to datetime format.
    
    Proper datetime conversion enables:
    - Time-based filtering and aggregation
    - Extraction of date components (year, month, day, etc.)
    - Accurate date arithmetic for cohort analysis
    
    Args:
        df: Input DataFrame
        date_columns: List of column names to convert to datetime
        date_format: Optional format string (e.g., '%Y-%m-%d %H:%M:%S')
                    If None, pandas will infer the format
    
    Returns:
        DataFrame with converted date columns
    
    Example:
        >>> df = convert_date_columns(df, ['InvoiceDate'])
    """
    df = df.copy()
    
    for col in date_columns:
        if col in df.columns:
            try:
                if date_format:
                    df[col] = pd.to_datetime(df[col], format=date_format)
                else:
                    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                print(f"Converted '{col}' to datetime")
            except Exception as e:
                print(f"Warning: Could not convert '{col}' to datetime: {e}")
    
    return df


def remove_invalid_records(
    df: pd.DataFrame,
    quantity_col: str = 'Quantity',
    price_col: str = 'UnitPrice',
    remove_negative_quantity: bool = True,
    remove_zero_price: bool = True
) -> pd.DataFrame:
    """
    Remove records that are invalid for analysis.
    
    Invalid records typically include:
    - Negative quantities (product returns/cancellations)
    - Zero or negative prices (promotional items or data errors)
    
    Args:
        df: Input DataFrame
        quantity_col: Name of the quantity column
        price_col: Name of the unit price column
        remove_negative_quantity: If True, remove rows with quantity <= 0
        remove_zero_price: If True, remove rows with price <= 0
    
    Returns:
        DataFrame with invalid records removed
    
    Note:
        For return analysis, you may want to keep negative quantities
        in a separate dataset before calling this function.
    """
    df = df.copy()
    initial_count = len(df)
    
    if remove_negative_quantity and quantity_col in df.columns:
        df = df[df[quantity_col] > 0]
        
    if remove_zero_price and price_col in df.columns:
        df = df[df[price_col] > 0]
    
    removed_count = initial_count - len(df)
    if removed_count > 0:
        print(f"Removed {removed_count:,} invalid records")
    
    return df


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Remove duplicate records from the dataset.
    
    Args:
        df: Input DataFrame
        subset: List of columns to consider for identifying duplicates
                If None, all columns are used
    
    Returns:
        DataFrame with duplicates removed
    """
    df = df.copy()
    initial_count = len(df)
    
    df = df.drop_duplicates(subset=subset)
    
    removed_count = initial_count - len(df)
    if removed_count > 0:
        print(f"Removed {removed_count:,} duplicate records")
    
    return df


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add commonly used calculated columns for analysis.
    
    Calculated columns:
    - Revenue: Quantity * UnitPrice (transaction-level revenue)
    - Year: Extracted from InvoiceDate
    - Month: Extracted from InvoiceDate
    - YearMonth: Combined year-month for trend analysis
    - DayOfWeek: Day name for weekday analysis
    
    Args:
        df: Input DataFrame with Quantity, UnitPrice, and InvoiceDate columns
    
    Returns:
        DataFrame with additional calculated columns
    """
    df = df.copy()
    
    # Calculate revenue
    if 'Quantity' in df.columns and 'UnitPrice' in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
        print("Added 'Revenue' column")
    
    # Extract date components
    if 'InvoiceDate' in df.columns and pd.api.types.is_datetime64_any_dtype(df['InvoiceDate']):
        df['Year'] = df['InvoiceDate'].dt.year
        df['Month'] = df['InvoiceDate'].dt.month
        df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
        df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
        print("Added date component columns (Year, Month, YearMonth, DayOfWeek)")
    
    return df


def clean_data_pipeline(
    filepath: str,
    drop_missing_cols: Optional[List[str]] = None,
    date_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Execute the complete data cleaning pipeline.
    
    This function chains all cleaning steps together for convenience.
    For more control, use individual functions.
    
    Args:
        filepath: Path to the raw data CSV file
        drop_missing_cols: Columns where missing values should trigger row removal
        date_columns: Columns to convert to datetime
    
    Returns:
        Cleaned DataFrame ready for analysis
    
    Example:
        >>> clean_df = clean_data_pipeline(
        ...     filepath='../data/raw/ecommerce_data.csv',
        ...     drop_missing_cols=['CustomerID'],
        ...     date_columns=['InvoiceDate']
        ... )
    """
    # Set defaults
    if drop_missing_cols is None:
        drop_missing_cols = ['CustomerID']
    if date_columns is None:
        date_columns = ['InvoiceDate']
    
    print("=" * 50)
    print("STARTING DATA CLEANING PIPELINE")
    print("=" * 50)
    
    # Step 1: Load data
    df = load_data(filepath)
    
    # Step 2: Handle missing values
    df = handle_missing_values(df, drop_columns=drop_missing_cols)
    
    # Step 3: Convert date columns
    df = convert_date_columns(df, date_columns)
    
    # Step 4: Remove invalid records
    df = remove_invalid_records(df)
    
    # Step 5: Remove duplicates
    df = remove_duplicates(df)
    
    # Step 6: Add calculated columns
    df = add_calculated_columns(df)
    
    print("=" * 50)
    print(f"PIPELINE COMPLETE: {len(df):,} clean records")
    print("=" * 50)
    
    return df


def save_cleaned_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the cleaned DataFrame to a CSV file.
    
    Args:
        df: Cleaned DataFrame to save
        output_path: Path where the CSV file will be saved
    """
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")
