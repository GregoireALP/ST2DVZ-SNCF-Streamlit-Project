import streamlit as st
import pandas as pd
from io import StringIO
import re

st.set_page_config(page_title="Data Cleaning", layout="wide")
st.title("🧹 Data Cleaning & Preparation")

st.markdown("""
In this section, we explain **how we cleaned the raw SNCF dataset** to keep only valid rows.
We focus on:
- Removing comment lines
- Keeping only rows starting with a valid date (YYYY-MM)
- Ensuring each row has the correct number of columns
""")

# -----------------------------
# Step 0: Show sample of raw dataset
# -----------------------------
st.header("Step 0: Sample of the raw dataset")

sample_raw = """# This is a comment
Date;Service;Gare de départ;Gare d'arrivée;Durée moyenne du trajet;Nombre de circulations prévues
2018-01;TGV INOUI;Paris;Lyon;120;50
Comment line inside file
2018-02;TGV INOUI;Paris;Marseille;180;45
"""

st.markdown("Here is an example of the raw data containing comment lines:")
st.code(sample_raw, language="csv")

# -----------------------------
# Step 1: Explain cleaning logic
# -----------------------------
st.header("Step 1: Cleaning logic applied")

st.markdown("""
1️⃣ **Keep the header** (first line) to preserve column names.  
2️⃣ **Filter lines starting with a valid date** in the format `YYYY-MM`.  
3️⃣ **Count the number of columns** and keep only rows matching the header.  
4️⃣ **Load the cleaned lines into pandas** for further analysis.
""")

st.code("""
import re
from io import StringIO
import pandas as pd

pattern = re.compile(r"^20\\d{2}-\\d{2}")
clean_lines = []
expected_cols = None

with open("data.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Keep header
header = lines[0]
clean_lines.append(header)

# Filter valid rows
for line in lines[1:]:
    if pattern.match(line.strip()):
        n_cols = line.count(";") + 1
        if expected_cols is None:
            expected_cols = header.count(";") + 1
        if n_cols == expected_cols:
            clean_lines.append(line)

# Load into pandas
df = pd.read_csv(StringIO("".join(clean_lines)), sep=";")
print(f"{len(df)} valid rows loaded.")
df.info()
""", language="python")
# -----------------------------
# Step 2: Convert data types
# -----------------------------
st.header("Step 2: Convert data types")
st.markdown("To make it easier to manipulate the data, particularly the dates, we need to convert the dates in the dataset to the correct Python format. We clean the dataset further by removing unnecessary columns and filtering out invalid values.")
st.code("""
    # Drop unnecessary comment columns
    df = df.drop(columns=['Commentaire annulations', 'Commentaire retards au départ'])
    
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
    df.info()        
            
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns

    # We only keep the data greater than 0, values less than 0 are not valid
    df_clean = df[(df[num_cols] >= 0).all(axis=1)]
    df = df_clean
""", language="python")
# -----------------------------
# Step 3: Show cleaned dataset info
# -----------------------------
st.header("Step 3: Cleaned dataset overview")

st.markdown("After cleaning, we have **10,335 valid rows** and the following columns:")

columns_overview = [
    "Date", "Service", "Gare de départ", "Gare d'arrivée",
    "Durée moyenne du trajet", "Nombre de circulations prévues",
    "Nombre de trains annulés", "Nombre de trains en retard au départ",
    "Retard moyen des trains en retard au départ", 
    "Retard moyen de tous les trains au départ",
    "Nombre de trains en retard à l'arrivée",
    "Retard moyen des trains en retard à l'arrivée",
    "Retard moyen de tous les trains à l'arrivée",
    "Prct retard pour causes externes", 
    "Prct retard pour cause infrastructure",
    "Prct retard pour cause gestion trafic",
    "Prct retard pour cause matériel roulant",
    "Prct retard pour cause gestion en gare et réutilisation de matériel",
    "Prct retard pour cause prise en compte voyageurs"
]

st.write(columns_overview)

# -----------------------------
# Step 4: Show cleaned dataset sample
# -----------------------------
st.header("Step 4: Sample of cleaned dataset")

# Example cleaned DataFrame for demonstration
cleaned_df = pd.DataFrame({
    "Date": ["2018-01", "2018-01", "2018-02"],
    "Service": ["TGV INOUI", "TGV INOUI", "TGV INOUI"],
    "Gare de départ": ["Paris", "Paris", "Paris"],
    "Gare d'arrivée": ["Lyon", "Marseille", "Lyon"],
    "Durée moyenne du trajet": [120, 180, 125],
    "Nombre de circulations prévues": [50, 45, 48],
    "Nombre de trains en retard au départ": [5, 0, 10],
    "Retard moyen des trains en retard au départ": [5.0, 0.0, 10.0],
    "Retard moyen de tous les trains au départ": [0.5, 0.0, 2.1]
})
st.warning("⚠️ Note: The actual dataset is large, so we are showing a simplified example here.")
st.dataframe(cleaned_df)
st.markdown("✅ Now the dataset is ready for further **analysis and visualization**.")
