import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from Project import get_data, get_locations, get_station_coord

# ============================================================================
# DATA PREPARATION
# ============================================================================

df = get_data()

# Load station coordinates
locations = get_station_coord()  # DataFrame with columns: Gare, lat, lon
coord_dict = locations.set_index("Gare")[["lat", "lon"]].to_dict(orient="index")

# Calculate statistics by departure station
stats_by_station = df.groupby("Gare de départ").agg({
    "Retard moyen de tous les trains au départ": ["mean", "std"],
    "Nombre de circulations prévues": "sum",
    "Nombre de trains annulés": "sum",
    "Nombre de trains en retard au départ": "sum",
    "Retard moyen des trains en retard au départ": "mean"
}).reset_index()

# Flatten multi-index columns
stats_by_station.columns = [
    "Station",
    "Average Delay",
    "Delay Std Dev",
    "Total Services",
    "Total Cancellations",
    "Total Delayed Trains",
    "Avg Delay of Delayed Trains"
]

# Calculate cancellation and punctuality rates
stats_by_station["Cancellation Rate (%)"] = (
    stats_by_station["Total Cancellations"] / stats_by_station["Total Services"] * 100
).round(2)

stats_by_station["Punctuality Rate (%)"] = (
    100 - (stats_by_station["Total Delayed Trains"] / stats_by_station["Total Services"] * 100)
).round(2)

# Add GPS coordinates
stats_by_station["lat"] = stats_by_station["Station"].map(
    lambda x: coord_dict.get(x, {}).get("lat", None)
)
stats_by_station["lon"] = stats_by_station["Station"].map(
    lambda x: coord_dict.get(x, {}).get("lon", None)
)

# Filter stations without coordinates
stations_without_coords = stats_by_station[stats_by_station["lat"].isna()]
if len(stations_without_coords) > 0:
    with st.expander(f"⚠️ {len(stations_without_coords)} station(s) without GPS coordinates"):
        st.write(stations_without_coords["Station"].tolist())

stats_by_station = stats_by_station.dropna(subset=["lat", "lon"])

# Categorize delays
def categorize_delay(delay):
    if delay < 2:
        return "🟢 Excellent (< 2 min)"
    elif delay < 5:
        return "🟡 Good (2-5 min)"
    elif delay < 10:
        return "🟠 Average (5-10 min)"
    else:
        return "🔴 Needs Improvement (> 10 min)"

stats_by_station["Category"] = stats_by_station["Average Delay"].apply(categorize_delay)

# ============================================================================
# STREAMLIT INTERFACE
# ============================================================================
st.title("🗺️ Interactive Delay Map by Departure Station")
st.markdown("### Geographic Analysis of TGV Network Punctuality")

# ============================================================================
# FILTERS AND CONTROLS
# ============================================================================
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    size_metric = st.selectbox(
        "📊 Bubble Size Based On",
        options=[
            "Average Delay", 
            "Total Services", 
            "Total Cancellations",
            "Cancellation Rate (%)"
        ],
        index=1,
        help="Criterion to size the markers"
    )

with col_filter2:
    st.markdown("**🎨 Visual Settings**")
    st.caption("🗺️ Map Style: Carto Dark Matter")
    st.caption("🌈 Color Scale: Turbo")

# Advanced filters
st.markdown("---")
col_slider1, col_slider2, col_slider3 = st.columns(3)

with col_slider1:
    delay_range = st.slider(
        "⏱️ Average Delay (minutes)",
        min_value=float(stats_by_station["Average Delay"].min()),
        max_value=float(stats_by_station["Average Delay"].max()),
        value=(
            float(stats_by_station["Average Delay"].min()),
            float(stats_by_station["Average Delay"].max())
        ),
        step=0.1
    )

with col_slider2:
    min_services = st.number_input(
        "🚆 Minimum Services",
        min_value=0,
        value=0,
        step=10,
        help="Filter stations with minimum number of services"
    )

with col_slider3:
    categories_filter = st.multiselect(
        "🏷️ Categories",
        options=stats_by_station["Category"].unique(),
        default=stats_by_station["Category"].unique(),
        help="Filter by delay category"
    )

# Apply filters
filtered_data = stats_by_station[
    (stats_by_station["Average Delay"] >= delay_range[0]) &
    (stats_by_station["Average Delay"] <= delay_range[1]) &
    (stats_by_station["Total Services"] >= min_services) &
    (stats_by_station["Category"].isin(categories_filter))
].copy()

# ============================================================================
# KEY PERFORMANCE INDICATORS
# ============================================================================
st.markdown("---")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        "🚉 Stations",
        f"{len(filtered_data)} / {len(stats_by_station)}"
    )

with kpi2:
    st.metric(
        "⏱️ Avg Delay",
        f"{filtered_data['Average Delay'].mean():.2f} min"
    )

with kpi3:
    st.metric(
        "🚆 Total Services",
        f"{filtered_data['Total Services'].sum():,.0f}"
    )

with kpi4:
    if len(filtered_data) > 0:
        best_station = filtered_data.loc[filtered_data["Average Delay"].idxmin(), "Station"]
        best_delay = filtered_data["Average Delay"].min()
        st.metric(
            "🏆 Best",
            best_station[:12] + "..." if len(best_station) > 12 else best_station,
            f"{best_delay:.2f} min"
        )

with kpi5:
    if len(filtered_data) > 0:
        worst_station = filtered_data.loc[filtered_data["Average Delay"].idxmax(), "Station"]
        worst_delay = filtered_data["Average Delay"].max()
        st.metric(
            "⚠️ Worst",
            worst_station[:12] + "..." if len(worst_station) > 12 else worst_station,
            f"{worst_delay:.2f} min",
            delta_color="inverse"
        )

# ============================================================================
# INTERACTIVE MAP
# ============================================================================
st.markdown("---")

# Create custom hover text
filtered_data["hover_text"] = filtered_data.apply(
    lambda row: (
        f"<b style='font-size:14px'>{row['Station']}</b><br>"
        f"<span style='color:#666'>━━━━━━━━━━━━━━━━</span><br>"
        f"<b>⏱️ Average Delay:</b> {row['Average Delay']:.2f} min<br>"
        f"<b>📊 Std Deviation:</b> {row['Delay Std Dev']:.2f} min<br>"
        f"<b>🚆 Total Services:</b> {int(row['Total Services']):,}<br>"
        f"<b>❌ Cancellations:</b> {int(row['Total Cancellations'])} "
        f"({row['Cancellation Rate (%)']:.1f}%)<br>"
        f"<b>⏰ Delayed Trains:</b> {int(row['Total Delayed Trains'])}<br>"
        f"<b>✅ Punctuality:</b> {row['Punctuality Rate (%)']:.1f}%<br>"
        f"<b>🏷️ Category:</b> {row['Category']}"
    ),
    axis=1
)

# Normalize bubble sizes
max_size = 50
min_size = 10
size_values = filtered_data[size_metric]
if size_values.max() > 0:
    normalized_sizes = (
        (size_values - size_values.min()) / (size_values.max() - size_values.min()) 
        * (max_size - min_size) + min_size
    )
else:
    normalized_sizes = [min_size] * len(filtered_data)

# Create the map
fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    lat=filtered_data["lat"],
    lon=filtered_data["lon"],
    mode="markers",
    marker=dict(
        size=normalized_sizes,
        color=filtered_data["Average Delay"],
        colorscale="Turbo",
        showscale=True,
        colorbar=dict(
            title=dict(
                text="Average<br>Delay<br>(min)",
                side="right"
            ),
            thickness=15,
            len=0.6,
            x=1.01,
            xpad=10
        ),
        opacity=0.85
    ),
    text=filtered_data["hover_text"],
    hovertemplate="%{text}<extra></extra>",
    name="",
    customdata=filtered_data["Station"]
))

# Map configuration
fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        zoom=5,
        center=dict(lat=46.8, lon=2.5)
    ),
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    hovermode="closest",
    showlegend=False,
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# DETAILED TABLE
# ============================================================================
st.markdown("---")
st.subheader("📊 Station Rankings")

col_table1, col_table2, col_table3 = st.columns([2, 2, 1])

with col_table1:
    show_top = st.radio(
        "Display",
        options=["All Stations", "Top 15 Worst", "Top 15 Best"],
        index=0,
        horizontal=True
    )

with col_table2:
    sort_by = st.selectbox(
        "Sort By",
        options=[
            "Average Delay",
            "Total Services",
            "Cancellation Rate (%)",
            "Punctuality Rate (%)"
        ],
        index=0
    )

with col_table3:
    sort_order = st.radio(
        "Order",
        options=["⬇️ Desc", "⬆️ Asc"],
        index=0
    )

# Prepare table data
table_data = filtered_data[[
    "Station",
    "Average Delay",
    "Delay Std Dev",
    "Total Services",
    "Total Cancellations",
    "Cancellation Rate (%)",
    "Punctuality Rate (%)",
    "Category"
]].copy()

# Sort data
ascending = (sort_order == "⬆️ Asc")
table_data = table_data.sort_values(sort_by, ascending=ascending)

# Filter top/bottom
if show_top == "Top 15 Worst":
    if sort_by == "Average Delay":
        table_data = table_data.head(15)
    else:
        table_data = table_data.tail(15)
elif show_top == "Top 15 Best":
    if sort_by == "Average Delay":
        table_data = table_data.tail(15)
    else:
        table_data = table_data.head(15)

# Display table
st.dataframe(
    table_data.reset_index(drop=True),
    use_container_width=True,
    height=400,
    column_config={
        "Station": st.column_config.TextColumn("🚉 Station", width="large"),
        "Average Delay": st.column_config.NumberColumn(
            "⏱️ Avg Delay",
            format="%.2f min"
        ),
        "Delay Std Dev": st.column_config.NumberColumn(
            "📊 Std Dev",
            format="%.2f min"
        ),
        "Total Services": st.column_config.NumberColumn(
            "🚆 Services",
            format="%d"
        ),
        "Total Cancellations": st.column_config.NumberColumn(
            "❌ Cancellations",
            format="%d"
        ),
        "Cancellation Rate (%)": st.column_config.NumberColumn(
            "📉 Cancel. Rate",
            format="%.2f%%"
        ),
        "Punctuality Rate (%)": st.column_config.NumberColumn(
            "✅ Punctuality",
            format="%.2f%%"
        ),
        "Category": st.column_config.TextColumn("🏷️ Category", width="medium")
    }
)

# ============================================================================
# KEY INSIGHTS
# ============================================================================
st.markdown("---")
st.subheader("💡 Key Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    excellent = filtered_data[filtered_data["Category"] == "🟢 Excellent (< 2 min)"]
    st.success(f"""
    **✅ Excellent Stations**
    
    {len(excellent)} stations ({len(excellent)/len(filtered_data)*100:.1f}%)  
    Average delay < 2 minutes
    """)

with insight_col2:
    poor = filtered_data[filtered_data["Category"] == "🔴 Needs Improvement (> 10 min)"]
    st.warning(f"""
    **⚠️ Needs Improvement**
    
    {len(poor)} stations ({len(poor)/len(filtered_data)*100:.1f}%)  
    Average delay > 10 minutes
    """)

with insight_col3:
    avg_cancel = filtered_data["Cancellation Rate (%)"].mean()
    st.info(f"""
    **📊 Cancellation Rate**
    
    Average: {avg_cancel:.2f}%  
    Max: {filtered_data['Cancellation Rate (%)'].max():.2f}%
    """)
