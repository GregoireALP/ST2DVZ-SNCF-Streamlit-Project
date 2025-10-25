import streamlit as st
import plotly.express as px
from Project import get_data, get_station_coord
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
df = get_data()
# Si process_data retourne un dictionnaire : df = st.session_state.data['main_table']

# ======================
# HEADER
# ======================
st.title("📊 Analyse des retards de trains")
st.markdown("---")

# ======================
# GRAPHIQUES
# ======================

# -----------------------------
# 1️⃣ Distribution des retards mensuels
# -----------------------------
st.header("🔹 Delayed trains by month")

df_monthly = (
    df.groupby('Date', as_index=False)['Nombre de trains en retard au départ']
    .sum()
    .sort_values('Date')
)

fig_hist = px.bar(
    df_monthly, 
    x='Date',
    y='Nombre de trains en retard au départ',
    title='Distribution des retards mensuels'
)

st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------
# 2️⃣ Nombre de trains annulés par mois
# -----------------------------
st.header("🔹 Canceled train by month")

df_annules = df.groupby('Date', as_index=False)['Nombre de trains annulés'].sum()

fig_annules = px.bar(
    df_annules,
    x='Date',
    y='Nombre de trains annulés',
    title='Nombre de trains annulés par mois'
)

st.plotly_chart(fig_annules, use_container_width=True)

# -----------------------------
# 3️⃣ Top 10 des lignes avec le plus de retard moyen
# -----------------------------
st.header("🔹 10 most most delayed station")

df_retards = (
    df.groupby(['Gare de départ', 'Gare d\'arrivée'], as_index=False)['Retard moyen de tous les trains à l\'arrivée']
    .mean()
    .sort_values('Retard moyen de tous les trains à l\'arrivée', ascending=False)
    .head(10)
)

# Créer une colonne pour les labels
df_retards['Ligne'] = df_retards['Gare de départ'] + " → " + df_retards['Gare d\'arrivée']

fig_top10 = px.bar(
    df_retards,
    x='Retard moyen de tous les trains à l\'arrivée',
    y='Ligne',
    orientation='h',
    title='🚆 Top 10 des lignes avec le plus de retard moyen à l\'arrivée'
)

st.plotly_chart(fig_top10, use_container_width=True)

st.header("🔹 Acerage delay by routes")

fig1 = px.line(
    df.groupby('Date', as_index=False)['Retard moyen de tous les trains à l\'arrivée'].mean(),
    x='Date',
    y='Retard moyen de tous les trains à l\'arrivée',
    title='Évolution du retard moyen à l’arrivée (tous services confondus)',
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)


st.header("🔹 Delays causes")

cols_causes = [
    'Prct retard pour causes externes',
    'Prct retard pour cause infrastructure',
    'Prct retard pour cause gestion trafic',
    'Prct retard pour cause matériel roulant',
    'Prct retard pour cause gestion en gare et réutilisation de matériel',
    'Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances)'
]

# Moyenne de chaque cause sur l'ensemble du dataset
mean_causes = df[cols_causes].mean().reset_index()
mean_causes.columns = ['Cause', 'Pourcentage']

fig5 = px.pie(
    mean_causes,
    names='Cause',
    values='Pourcentage',
    title='Répartition moyenne des causes de retard'
)
st.plotly_chart(fig5, use_container_width=True)

selected_line = st.selectbox(
    "🚄 Select a route :", 
    sorted(df['Gare de départ'].unique())
)

# ---- Filtrage et graphique ----
filtered_df = df[df['Gare de départ'] == selected_line]

fig = px.line(
    filtered_df,
    x='Date',
    y='Retard moyen de tous les trains à l\'arrivée',
    title=f"Évolution du retard moyen à l’arrivée — {selected_line}",
    markers=True
)

# ---- Affichage ----
st.plotly_chart(fig, use_container_width=True)

# ---- Compute average delay per departure station ----
avg_delay = (
    df.groupby("Gare de départ", as_index=False)["Retard moyen de tous les trains à l'arrivée"]
    .mean()
    .rename(columns={"Retard moyen de tous les trains à l'arrivée": "Retard moyen"})
)

# Dataset des gares avec latitude et longitude
locations = get_station_coord()
coord_dict = locations.set_index("Gare")[["lat", "lon"]].to_dict(orient="index")

# Calculer le retard moyen par gare de départ
retard_par_gare = df.groupby("Gare de départ")["Retard moyen de tous les trains au départ"].mean().reset_index()

# Ajouter lat/lon à partir du dictionnaire
retard_par_gare["lat"] = retard_par_gare["Gare de départ"].apply(lambda x: coord_dict[x]["lat"] if x in coord_dict else None)
retard_par_gare["lon"] = retard_par_gare["Gare de départ"].apply(lambda x: coord_dict[x]["lon"] if x in coord_dict else None)

# Filtrer les gares sans coordonnées
retard_par_gare = retard_par_gare.dropna(subset=["lat", "lon"])

# Titre Streamlit
st.title("Average delay by stations")

# Création de la carte
fig = px.scatter_mapbox(
    retard_par_gare,
    lat="lat",
    lon="lon",
    size="Retard moyen de tous les trains au départ",
    color="Retard moyen de tous les trains au départ",
    hover_name="Gare de départ",
    hover_data={"lat": False, "lon": False, "Retard moyen de tous les trains au départ": True},
    size_max=40,
    zoom=5,
    mapbox_style="carto-positron"
)

st.plotly_chart(fig, use_container_width=True)

retard_par_gare_not_null = df.groupby("Gare de départ")["Retard moyen de tous les trains au départ" > 0].mean().reset_index()

