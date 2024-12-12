#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st # type: ignore
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
import geopandas as gpd # type: ignore
from folium.plugins import MarkerCluster # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import numpy as np 
from folium import CircleMarker

st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        color: #0A1172;  /* Donkerblauwe kleur */
        font-family: 'Arial', sans-serif;  /* Je kunt het lettertype hier veranderen */
    }
    </style>
    <h1 class="title">Duurzaamheidsindex Amsterdam 2024</h1>
    """, unsafe_allow_html=True)

st.markdown("""
Welkom bij de **Duurzaamheidsatlas van Amsterdam (2024)**!  
Deze interactieve applicatie presenteert de resultaten van mijn onderzoek naar de **Duurzaamheidsindex**, een samengestelde maat die de duurzaamheid van Amsterdamse buurten meet.  

De index combineert verschillende indicatoren, zoals:  
- **Groene aanbod** (A++++ tot B)  
- **Aardgasvrije woningen**  
- **Aantal zonnepanelen**  

Met deze visualisaties krijgt u inzicht in hoe buurten presteren op het gebied van duurzaamheid en hoe deze data stedenbouwkundig beleid kan ondersteunen.  

Gebruik de kaarten en grafieken om trends te ontdekken, buurten te vergelijken, en strategische inzichten te verkrijgen voor een duurzamer Amsterdam!
""")

gdf = gpd.read_file("output.geojson")

st.subheader("Gemiddelde Duurzaamheidsindex per Stadsdeel")
avg_index = gdf.groupby("Stadsdeel")["Duurzaamheidsindex"].mean().sort_values()
fig = plt.figure(figsize=(10, 6))
sns.barplot(x=avg_index.values, y=avg_index.index, palette="YlGn")
plt.title("Gemiddelde Duurzaamheidsindex per Stadsdeel")
st.pyplot(fig)

st.subheader("Duurzaamheidsindex voor Amsterdamse buurten in 2024")
st.markdown("""
De kleuren representeren de duurzaamheidsprestaties, waarbij donkergroen een hogere duurzaamheidsindex betekent.
Klik op een buurt voor meer details.
""")

m = folium.Map(location=[52.3728, 4.8936], zoom_start=12)
choropleth = folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "Duurzaamheidsindex"],
    key_on="feature.properties.Buurtcode",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Duurzaamheidsindex (0-1)"
).add_to(m)

# Kleurinformatie van Choropleth ophalen
choropleth_style = choropleth.geojson

# Click-popup toevoegen aan de buurten zonder kleuren te overschrijven
def style_function(feature):
    return {
        "fillOpacity": 0,  # Laat Choropleth-kleuren intact
        "weight": 0.5,
        "color": "white"  # Optionele randkleur
    }

def highlight_function(feature):
    return {
        "fillOpacity": 1,
        "weight": 2,
        "color": "blue"
    }

folium.GeoJson(
    data=gdf,
    style_function=style_function,  # Zorgt ervoor dat de Choropleth kleuren behouden blijven
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Buurt", "Duurzaamheidsindex"],
        aliases=["Buurt:", "Duurzaamheidsindex:"],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["Buurt", "Duurzaamheidsindex", "Aanbod groen (1-10)", "aardgasvrije woningequivalenten", "aantal_zonnepanelen"],
        aliases=["Buurt:", "Duurzaamheidsindex:", "Aanbod groen (1-10):", "Aardgasvrije woningen(%):", "Aantal Zonnepanelen:"],
        max_width=300
    )
).add_to(m)

# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)
from folium.plugins import HeatMap # type: ignore

# Kaart maken
st.subheader("Warmtekaart: Concentratie van Zonnepanelen")
st.markdown("""
Deze warmtekaart visualiseert de concentratie van zonnepanelen in Amsterdam.  
Donkere gebieden representeren een lagere dichtheid, terwijl lichtere gebieden een hogere concentratie zonnepanelen tonen.
""")

m = folium.Map(location=[52.3728, 4.8936], zoom_start=12)

# Warmtekaart toevoegen
heat_data = gdf[["LAT", "LNG", "aantal_zonnepanelen"]].dropna()
HeatMap(
    [[row["LAT"], row["LNG"], row["aantal_zonnepanelen"]] for index, row in heat_data.iterrows()],
    radius=15,
    blur=10,
    max_zoom=1
).add_to(m)

# Kaart in Streamlit weergeven
st_folium(m, width=800, height=500)

st.markdown("""
    Deze kaart toont het groenaanbod in verschillende buurten. 
    Elke marker heeft een vorm die het groenaanbod reflecteert:
    - Vierkant voor laag groenaanbod
    - Driehoek voor gemiddeld groenaanbod
    - Cirkel voor hoog groenaanbod
""")


def get_marker_shape(green_value):
    """Bepaalt de vorm van de marker op basis van de groenwaarde"""
    if green_value <= 3:
        return 'square'   # Laag groenaanbod krijgt een vierkant
    elif green_value <= 6:
        return 'triangle'  # Gemiddeld groenaanbod krijgt een driehoek
    else:
        return 'circle'    # Hoog groenaanbod krijgt een cirkel

# Functie om de kleur van de marker te bepalen op basis van groenaanbod
def get_marker_color(green_value):
    """Bepaalt de kleur van de marker op basis van de groenwaarde"""
    if green_value <= 3:
        return "red"  # Laag groen = rood
    elif green_value <= 6:
        return "orange"  # Gemiddeld groen = oranje
    else:
        return "green"  # Hoog groen = groen

# Maak de Folium-kaart aan
m = folium.Map(location=[52.3776, 4.9141], zoom_start=12)

# Maak een MarkerCluster aan
marker_cluster = MarkerCluster().add_to(m)

# Voeg markers toe aan de cluster
for _, row in gdf.iterrows():
    green_value = row["Aanbod groen (1-10)"]
    
    # Bepaal de kleur en vorm
    color = get_marker_color(green_value)
    shape = get_marker_shape(green_value)
    
    # Afhankelijk van de vorm, maak een marker aan
    if shape == 'square':
        icon = Icon(color=color, icon='square', prefix='fa')
    elif shape == 'triangle':
        icon = Icon(color=color, icon='triangle', prefix='fa')
    elif shape == 'circle':
        icon = Icon(color=color, icon='circle', prefix='fa')
    
    # Voeg de marker toe aan de cluster
    Marker(
        location=[row["LAT"], row["LNG"]],
        icon=icon,
        popup=(
            f"<b>Buurt:</b> {row['Buurt']}<br>"
            f"<b>Aanbod groen:</b> {row['Aanbod groen (1-10)']}"
        )
    ).add_to(marker_cluster)

# We gebruiken streamlit's components om de Folium-kaart weer te geven
from streamlit.components.v1 import html
html(m._repr_html_(), width=700, height=500)


# Titel en toelichting
st.subheader("Visualisatie van Aanbod Groen per Buurt")
st.markdown(
    """
    Deze kaart toont het **Aanbod groen (1-10)** per buurt in de stad. Hoe hoger de waarde, 
    hoe meer groenvoorzieningen aanwezig zijn in de buurt. De cirkels geven de relatieve score 
    weer, waarbij de grootte en kleur de hoeveelheid aanbod visualiseren.
    """
)

# Initiële kaart maken
m = folium.Map(location=[gdf["LAT"].mean(), gdf["LNG"].mean()], zoom_start=12)

from folium.plugins import MarkerCluster

# Maak een MarkerCluster aan
marker_cluster = MarkerCluster().add_to(m)

# Voeg cirkelmarkers toe aan de cluster
for _, row in gdf.iterrows():
    CircleMarker(
        location=[row["LAT"], row["LNG"]],
        radius=row["Aanbod groen (1-10)"] * 2,  # Schaal de radius
        color="#4CAF50",  # Groen
        fill=True,
        fill_color="#4CAF50",
        fill_opacity=0.6,
        tooltip=(
            f"<b>Buurt:</b> {row['Buurt']}<br>"
            f"<b>Aanbod groen:</b> {row['Aanbod groen (1-10)']}"
        ),
    ).add_to(marker_cluster)

# Voeg de kaart toe aan Streamlit
st_data = st_folium(m, width=700, height=500)

# Kaart voor aardgasvrije woningequivalenten
st.subheader("Kaart: Aardgasvrije Woningequivalenten per Buurt")
st.markdown("""
Deze kaart toont het aantal **aardgasvrije woningequivalenten** per buurt in Amsterdam.  
De kleuren geven een indicatie van de mate waarin buurten overgeschakeld zijn op aardgasvrije oplossingen.  
Klik op een buurt om details te bekijken.
""")

# Folium kaart maken
m = folium.Map(location=[52.3728, 4.8936], zoom_start=12)

# Choropleth toevoegen voor aardgasvrije woningequivalenten
choropleth = folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "aardgasvrije woningequivalenten"],
    key_on="feature.properties.Buurtcode",
    fill_color="PuBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Aardgasvrije woningequivalenten"
).add_to(m)

# Klikbare popups en tooltips toevoegen
folium.GeoJson(
    data=gdf,
    style_function=lambda feature: {
        "fillOpacity": 0,  # Laat Choropleth-kleuren intact
        "weight": 0.5,
        "color": "white"
    },
    highlight_function=lambda feature: {
        "fillOpacity": 1,
        "weight": 2,
        "color": "blue"
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Buurt", "aardgasvrije woningequivalenten"],
        aliases=["Buurt:", "Aardgasvrije Woningequivalenten:"],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["Buurt", "aardgasvrije woningequivalenten", "Duurzaamheidsindex"],
        aliases=["Buurt:", "Aardgasvrije Woningequivalenten:", "Duurzaamheidsindex:"],
        max_width=300
    )
).add_to(m)

# Legenda aanpassen
legend_html = '''
<div style="position: fixed; 
            bottom: 10px; left: 10px; width: 250px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Legenda:</b><br>
    <i style="background: #edf8fb; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Lage concentratie<br>
    <i style="background: #b2e2e2; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Middelhoge concentratie<br>
    <i style="background: #66c2a4; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Hoge concentratie<br>
    <i style="background: #2ca25f; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Zeer hoge concentratie<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)



import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium import Choropleth
from branca.colormap import linear

gdf1 = gpd.read_file("combined_data1.geojson")
st.subheader('Energielabel Kaart: Buurten van Amsterdam')
st.markdown(
    "Deze kaart laat de duurzaamheidsniveaus van Amsterdamse buurten zien, gebaseerd op energielabels. "
    "De kleuren variëren van **groen** (hoog aandeel energielabel A++++ t/m B) tot **rood** (hoog aandeel energielabel E t/m G). "
    "Dit geeft inzicht in de duurzaamheid van verschillende buurten en kan helpen bij verdere stadsplanning en verduurzaming."
)

# Grootste aandeel bepalen
def determine_dominant_label(row):
    labels = {
        "A++++ t/m B": row["Energielabel A++++ t/m B (%)"],
        "C t/m D": row["Energielabel C t/m D (%)"],
        "E t/m G": row["Energielabel E t/m G (%)"],
    }
    return max(labels, key=labels.get)

gdf1["Dominant_Label"] = gdf1.apply(determine_dominant_label, axis=1)

# Kleuren toewijzen op basis van dominant label
color_mapping = {
    "A++++ t/m B": "#2ecc71",  # Groen
    "C t/m D": "#f1c40f",      # Geel
    "E t/m G": "#e74c3c",      # Rood
}

gdf1["Color"] = gdf1["Dominant_Label"].map(color_mapping)

# Folium kaart genereren
m = folium.Map(location=[52.3676, 4.9041], zoom_start=12)

for _, row in gdf1.iterrows():
    folium.GeoJson(
        row.geometry,
        style_function=lambda feature, color=row["Color"]: {
            "fillColor": color,
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.6,
        },
        tooltip=(
            f"<b>Buurt:</b> {row['Buurt']}<br>"
            f"<b>Dominant label:</b> {row['Dominant_Label']}<br>"
            f"<b>A++++ t/m B:</b> {row['Energielabel A++++ t/m B (%)']}%<br>"
            f"<b>C t/m D:</b> {row['Energielabel C t/m D (%)']}%<br>"
            f"<b>E t/m G:</b> {row['Energielabel E t/m G (%)']}%"
        ),
    ).add_to(m)

# Kaart weergeven
st_folium(m, width=800, height=600)

# Conclusie
st.markdown(
    "**Hoe te interpreteren:** De buurten met een groene kleur hebben het grootste aandeel woningen met een hoog energielabel (A++++ t/m B). "
    "De rode buurten hebben het grootste aandeel woningen met een laag energielabel (E t/m G). "
    "Deze visualisatie helpt om inzicht te krijgen in de duurzaamheid van buurten binnen Amsterdam."
)


# Titel en introductie
st.subheader("Vergelijking van duurzaamheid in Amsterdamse buurten")

st.markdown(
    "Hieronder worden twee kaarten weergegeven: \n"
    "1. **Duurzaamheidsindexkaart**: Toont de algemene duurzaamheidsprestaties per buurt in 2024. \n"
    "2. **Energielabelkaart**: Geeft het dominante energielabel in elke buurt weer. \n"
    "Deze kaarten kunnen worden vergeleken om inzicht te krijgen in de relatie tussen energielabels en de algemene duurzaamheidsindex."
)


m1 = folium.Map(location=[52.3728, 4.8936], zoom_start=12)
choropleth = folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "Duurzaamheidsindex"],
    key_on="feature.properties.Buurtcode",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Duurzaamheidsindex (0-1)"
).add_to(m1)

def style_function(feature):
    return {
        "fillOpacity": 0,  # Laat Choropleth-kleuren intact
        "weight": 0.5,
        "color": "white"  # Optionele randkleur
    }

def highlight_function(feature):
    return {
        "fillOpacity": 1,
        "weight": 2,
        "color": "blue"
    }

folium.GeoJson(
    data=gdf,
    style_function=style_function,  # Zorgt ervoor dat de Choropleth kleuren behouden blijven
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Buurt", "Duurzaamheidsindex"],
        aliases=["Buurt:", "Duurzaamheidsindex:"],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["Buurt", "Duurzaamheidsindex", "Aanbod groen (1-10)", "aardgasvrije woningequivalenten", "aantal_zonnepanelen"],
        aliases=["Buurt:", "Duurzaamheidsindex:", "Aanbod groen (1-10):", "Aardgasvrije woningen(%):", "Aantal Zonnepanelen:"],
        max_width=300
    )
).add_to(m1)


# Grootste aandeel bepalen
def determine_dominant_label(row):
    labels = {
        "A++++ t/m B": row["Energielabel A++++ t/m B (%)"],
        "C t/m D": row["Energielabel C t/m D (%)"],
        "E t/m G": row["Energielabel E t/m G (%)"],
    }
    return max(labels, key=labels.get)

gdf1["Dominant_Label"] = gdf1.apply(determine_dominant_label, axis=1)

# Kleuren toewijzen op basis van dominant label
color_mapping = {
    "A++++ t/m B": "#2ecc71",  # Groen
    "C t/m D": "#f1c40f",      # Geel
    "E t/m G": "#e74c3c",      # Rood
}

gdf1["Color"] = gdf1["Dominant_Label"].map(color_mapping)

m2 = folium.Map(location=[52.3676, 4.9041], zoom_start=12)

for _, row in gdf1.iterrows():
    folium.GeoJson(
        row.geometry,
        style_function=lambda feature, color=row["Color"]: {
            "fillColor": color,
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.6,
        },
        tooltip=(
            f"<b>Buurt:</b> {row['Buurt']}<br>"
            f"<b>Dominant label:</b> {row['Dominant_Label']}<br>"
            f"<b>A++++ t/m B:</b> {row['Energielabel A++++ t/m B (%)']}%<br>"
            f"<b>C t/m D:</b> {row['Energielabel C t/m D (%)']}%<br>"
            f"<b>E t/m G:</b> {row['Energielabel E t/m G (%)']}%"
        ),
    ).add_to(m2)

# --- Beide kaarten naast elkaar weergeven ---
st.markdown("### Vergelijking van de twee kaarten")
col1, col2 = st.columns(2)

with col1:
    st_folium(m1, width=400, height=500, key="duurzaamheidsindex_kaart")
    st.caption("Duurzaamheidsindexkaart")

with col2:
    st_folium(m2, width=400, height=500, key="energielabel_kaart")
    st.caption("Energielabelkaart")

