# Customer Insights Analytics

A production-ready customer analytics project that transforms raw e-commerce transaction data into actionable business insights. Built with Python and deployable as an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Business Problem](#-business-problem)
- [Solution Overview](#-solution-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Deploy to Streamlit Community Cloud](#-deploy-to-streamlit-community-cloud)
- [Features](#-features)
- [Future Improvements](#-future-improvements)

---

## 🎯 Business Problem

E-commerce businesses generate vast amounts of transaction data daily. Without proper analysis, valuable insights about customer behavior, revenue patterns, and market trends remain hidden. Key challenges include:

- **Lack of visibility** into customer purchasing patterns
- **Difficulty identifying** high-value customers for retention programs
- **No real-time tracking** of revenue trends and KPIs
- **Manual reporting** that is time-consuming and error-prone

---

## 💡 Solution Overview

This project provides an end-to-end analytics solution that:

1. **Cleans and preprocesses** raw transaction data
2. **Calculates key business metrics** (revenue, AOV, customer counts)
3. **Identifies trends** through time-series analysis
4. **Segments customers** by monetary value
5. **Visualizes insights** through an interactive dashboard

---

## 🛠️ Tech Stack

| Category            | Technology         |
| ------------------- | ------------------ |
| **Language**        | Python 3.9+        |
| **Data Processing** | Pandas, NumPy      |
| **Visualization**   | Plotly, Matplotlib |
| **Dashboard**       | Streamlit          |
| **Notebook**        | Jupyter            |

---

## 📁 Project Structure

```
customer-insights-analytics/
│
├── data/
│   ├── raw/                    # Raw input datasets
│   │   └── ecommerce_data.csv  # Place your data here
│   └── processed/              # Cleaned datasets
│       └── cleaned_data.csv    # Generated after cleaning
│
├── notebooks/
│   └── 01_data_exploration.ipynb  # Exploratory data analysis
│
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py        # Data preprocessing functions
│   └── analysis.py             # Business analytics functions
│
├── app/
│   ├── __init__.py
│   └── app.py                  # Streamlit dashboard
│
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/customer-insights-analytics.git
   cd customer-insights-analytics
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your data**

   Place your e-commerce CSV file in `data/raw/ecommerce_data.csv`

   Expected columns:

   - `InvoiceNo` - Unique transaction identifier
   - `StockCode` - Product code
   - `Description` - Product description
   - `Quantity` - Number of units purchased
   - `InvoiceDate` - Transaction timestamp
   - `UnitPrice` - Price per unit
   - `CustomerID` - Unique customer identifier
   - `Country` - Customer's country

---

## 📖 Usage

### 1. Explore the Data (Jupyter Notebook)

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

This notebook provides:

- Dataset overview and structure
- Missing values analysis
- Statistical summaries
- Data quality checks

### 2. Clean the Data

```python
from src.data_cleaning import clean_data_pipeline, save_cleaned_data

# Run the cleaning pipeline
clean_df = clean_data_pipeline(
    filepath='data/raw/ecommerce_data.csv',
    drop_missing_cols=['CustomerID'],
    date_columns=['InvoiceDate']
)

# Save cleaned data
save_cleaned_data(clean_df, 'data/processed/cleaned_data.csv')
```

### 3. Run Analysis

```python
from src.analysis import generate_summary_report
import pandas as pd

# Load cleaned data
df = pd.read_csv('data/processed/cleaned_data.csv')

# Generate comprehensive report
report = generate_summary_report(df)

# Access specific metrics
print(f"Total Revenue: ${report['kpis']['total_revenue']:,.2f}")
print(f"Total Customers: {report['kpis']['total_customers']:,}")
```

### 4. Launch the Dashboard

```bash
streamlit run app/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## ☁ Deploy to Streamlit Community Cloud

### 1. Push this project to GitHub

Make sure these files are in your repository:

- `app/app.py`
- `requirements.txt`
- `runtime.txt`
- `data/processed/cleaned_data.csv`

> Note: `data/raw/` remains ignored, but `data/processed/` is now allowed so the dashboard can load data in cloud.

### 2. Create the app in Streamlit Community Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repository and branch
4. Set **Main file path** to:

```text
app/app.py
```

5. Click **Deploy**

### 3. Verify after deploy

- App opens without "Processed data not found" warning
- KPIs and charts load correctly
- URL format will be:

```text
https://<your-app-name>.streamlit.app
```

---

## ✨ Features

### Data Cleaning Module (`src/data_cleaning.py`)

- Handle missing values with configurable strategies
- Convert date columns to proper datetime format
- Remove invalid records (returns, zero prices)
- Add calculated columns (Revenue, date components)
- Complete cleaning pipeline for automation

### Analysis Module (`src/analysis.py`)

- Calculate revenue KPIs (total, AOV, per customer)
- Monthly sales trend analysis
- Top customers by monetary value
- Top products by revenue
- Geographic sales breakdown
- Customer value segmentation

### Interactive Dashboard (`app/app.py`)

- Real-time KPI metrics cards
- Revenue trend visualization
- Orders and customers trend chart
- Top customers leaderboard
- Responsive design for all screen sizes

---

## 🔮 Future Improvements

- [ ] **RFM Analysis** - Implement Recency, Frequency, Monetary segmentation
- [ ] **Customer Cohort Analysis** - Track customer behavior over time
- [ ] **Predictive Analytics** - Customer churn prediction model
- [ ] **Product Recommendations** - Market basket analysis
- [ ] **Automated Reports** - Scheduled email reports
- [ ] **Database Integration** - Connect to SQL databases
- [ ] **Docker Deployment** - Containerized deployment
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **API Endpoints** - REST API for metric access

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or feedback, please open an issue in this repository.

---

_Built with ❤️ for data-driven decision making_
