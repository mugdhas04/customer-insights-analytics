import sqlite3
import pandas as pd
from pathlib import Path


def load_data_to_sqlite(db_path=None):
    """
    Load cleaned CSV data into SQLite database.
    """
    PROJECT_ROOT = Path(__file__).parent.parent

    if db_path is None:
        db_path = PROJECT_ROOT / "data" / "processed" / "analytics.db"

    data_path = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Cleaned data not found at {data_path}")

    df = pd.read_csv(data_path, parse_dates=["InvoiceDate"])

    conn = sqlite3.connect(db_path)
    df.to_sql("transactions", conn, if_exists="replace", index=False)

    return conn


def sql_total_revenue(conn):
    query = """
    SELECT SUM(Revenue) AS total_revenue
    FROM transactions
    """
    return pd.read_sql(query, conn)


def sql_monthly_revenue(conn):
    query = """
    SELECT 
        strftime('%Y-%m', InvoiceDate) AS year_month,
        SUM(Revenue) AS revenue
    FROM transactions
    GROUP BY year_month
    ORDER BY year_month
    """
    return pd.read_sql(query, conn)


def sql_top_customers(conn, limit=10):
    query = f"""
    SELECT 
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS orders,
        SUM(Revenue) AS total_revenue
    FROM transactions
    GROUP BY CustomerID
    ORDER BY total_revenue DESC
    LIMIT {limit}
    """
    return pd.read_sql(query, conn)
