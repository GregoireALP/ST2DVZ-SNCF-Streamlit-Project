import streamlit as st

from util.io import load_data, process_data, get_locations

@st.cache_data
def get_data():
    df_raw = load_data()
    tables = process_data(df_raw)
    return tables

@st.cache_data
def get_station_coord():
    return get_locations()
    
st.set_page_config(
    page_title="Data Storytelling Dashboard",
    layout="wide",
    page_icon="🚄"
)

st.title("🚄 Data Storytelling SNCF")
st.caption('Source: "Régularité mensuelle TGV par liaison" - OPEN DATA SNCF - Open Database License (ODbL)')
st.caption("https://data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/table/?sort=date")

st.markdown("""
## 🎓 Project Overview
The goal of this project is to analyze, visualize, and understand **train delays across France’s high-speed TGV network**, using open data provided by **SNCF**.
""")

st.markdown("""
### 📊 About the Dataset
The dataset records **monthly TGV performance** from **2018 to today**, including:
- 🕒 **Delay causes** (weather, technical issues, congestion, etc.)
- 🚉 **Average delay duration** per route
- 👥 **Passenger counts**
- 📅 **Monthly aggregation** of all delay events

It allows us to explore **patterns of train punctuality**, spot **the most delay-prone routes**, and assess how **different factors** influence travel reliability.
""")

st.markdown("""
### 🎯 Objectives
With this dashboard, we aim to:
1. Identify the **most delay-prone TGV routes** in France.  
2. Analyze **reasons for delays** (technical failures, external causes, infrastructure, etc.).  
3. Measure **average delay duration** per route and month.  
4. Estimate the **number of passengers affected** by delays.  
""")

st.divider()

st.markdown("""
### 💡 Project Vision
This application illustrates how **data storytelling** can transform raw datasets into **insightful narratives**.  
By combining **data science, visualization, and interpretability**, we aim to tell the story behind France’s TGV punctuality — highlighting not only **where** and **when** delays occur, but also **why** they happen.
""")

st.markdown("""
---
👩‍💻 **Developed by Grégoire ALPEROVITCH**  
""")
