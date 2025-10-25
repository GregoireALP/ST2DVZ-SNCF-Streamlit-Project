# 🚄 TGV Punctuality Analysis Dashboard

Interactive data storytelling application analyzing French TGV train punctuality patterns using SNCF Open Data.

## 📊 Overview

This Streamlit application provides comprehensive analysis of TGV delay patterns across the French rail network, featuring:

- **Interactive geographic visualizations** of delay patterns by station
- **Seasonal trend analysis** revealing the "Summer Paradox"
- **Root cause attribution** of delays by operational factors
- **Route-level performance metrics** and comparisons
- **Data cleaning documentation** and methodology

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
project/
├── app.py                          # Main entry point
├── data/
│   ├── regularite_tgv.csv          # SNCF TGV punctuality dataset
│   └── station_coordinates.csv     # GPS coordinates (manually collected)
├── sections/
│   ├── intro.py                    # Introduction & context
│   ├── overview.py                 # High-level statistics
│   ├── deep_dives.py               # Detailed narrative analysis
│   └── conclusions.py              # Insights & recommendations
├── utils/
│   ├── io.py                       # Data loading functions
│   ├── prep.py                     # Data cleaning pipeline
│   └── viz.py                      # Visualization utilities
└── assets/                         # Images and styling
```

## 📊 Dataset

**Source:** SNCF Open Data - Monthly TGV Punctuality by Route

**Enrichments:**
- GPS coordinates (manually collected)
- Temporal features (season, quarter, month)
- Derived KPIs (punctuality rate, cancellation rate)
- Performance categories (Excellent/Good/Average/Poor)

## 🛠️ Technologies

- **Streamlit** - Web application framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **Python 3.10+** - Core language


## 🎯 Project Goal

Transform raw operational data into a compelling narrative that guides users from problem discovery through analysis to actionable insights, demonstrating the power of data storytelling in transportation analytics.

## 👥 Author

Data Science Student Project - 2025

## 📄 License

Educational project using public SNCF Open Data