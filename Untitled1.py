#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st # type: ignore
import folium # type: ignore
from streamlit.components.v1 import html

from streamlit_folium import st_folium # type: ignore
import geopandas as gpd # type: ignore
from folium.plugins import MarkerCluster # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
from folium import GeoJson, GeoJsonTooltip
import seaborn as sns 
from folium import Choropleth
import numpy as np 
from folium import Icon, Marker
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

st.subheader("Correlatie tussen variabelen")
corr_matrix = gdf[["Duurzaamheidsindex", "aantal_zonnepanelen", "Aanbod groen (1-10)", "aardgasvrije woningequivalenten"]].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
ax.set_title("Correlatiematrix", fontsize=16)
st.pyplot(fig)

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
from folium.plugins import FloatImage
import streamlit as st
from streamlit_folium import st_folium

# Clusteranalyse uitvoeren
features = gdf[["Duurzaamheidsindex", "aantal_zonnepanelen", "Aanbod groen (1-10)"]].fillna(0)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)
kmeans = KMeans(n_clusters=4, random_state=42).fit(scaled_features)

gdf["Cluster"] = kmeans.labels_

# Folium kaart maken
cluster_map = folium.Map(location=[52.3728, 4.8936], zoom_start=12)
colors = ["red", "blue", "green", "purple"]

# Markers toevoegen
for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row["LAT"], row["LNG"]],
        radius=6,
        color=colors[row["Cluster"]],
        fill=True,
        fill_color=colors[row["Cluster"]],
        fill_opacity=0.7,
        popup=f"Buurt: {row['Buurt']}<br>Cluster: {row['Cluster']}"
    ).add_to(cluster_map)

# Legenda toevoegen
legend_html = """
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 250px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px; 
            border:2px solid grey; padding: 10px;">
    <b>Legenda:</b><br>
    <span style="color:red;">&#9679;</span> Cluster 0: Lage duurzaamheid, weinig groen<br>
    <span style="color:blue;">&#9679;</span> Cluster 1: Gemiddelde duurzaamheid, matig zonnepanelen<br>
    <span style="color:green;">&#9679;</span> Cluster 2: Hoog groenaanbod, weinig zonnepanelen<br>
    <span style="color:purple;">&#9679;</span> Cluster 3: Hoge duurzaamheid, veel zonnepanelen
</div>
"""
cluster_map.get_root().html.add_child(folium.Element(legend_html))

# Toelichting toevoegen (tekst voor gebruikers)
st.subheader("Clustering van buurten op basis van duurzaamheid")
st.markdown("""
De bovenstaande kaart toont clusters van buurten op basis van duurzaamheidskenmerken:
- **Duurzaamheidsindex**: Een algemene score van duurzaamheid.
- **Aantal zonnepanelen**: De hoeveelheid zonnepanelen in de buurt.
- **Aanbod groen (1-10)**: De hoeveelheid groen in de buurt.

Elke kleur vertegenwoordigt een cluster met buurten die qua duurzaamheidseigenschappen overeenkomen. 
Gebruik de kaart om patronen te ontdekken en klik op de markers voor meer informatie.
""")

# Streamlit-kaart tonen
folium_html = cluster_map._repr_html_() + legend_html  # Voeg kaart en legenda samen
html(folium_html, width=800, height=600)

st.subheader("Verdeling van de Duurzaamheidsindex")
st.markdown("""
Deze grafiek laat zien hoe de duurzaamheidsindex is verdeeld over alle buurten van Amsterdam.
""")

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(gdf["Duurzaamheidsindex"], kde=True, bins=20, color="teal")
ax.set_title("Verdeling van de Duurzaamheidsindex", fontsize=16)
ax.set_xlabel("Duurzaamheidsindex", fontsize=12)
ax.set_ylabel("Aantal buurten", fontsize=12)
st.pyplot(fig)


# Titel en toelichting
st.subheader("Visualisatie van Aanbod Groen per Buurt")
st.markdown(
    """
    Deze kaart toont het **Aanbod groen (1-10)** per buurt in de stad. Hoe hoger de waarde, 
    hoe meer groenvoorzieningen aanwezig zijn in de buurt. De cirkels geven de relatieve score 
    weer, waarbij de grootte en kleur de hoeveelheid aanbod visualiseren.
    """
)

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

import streamlit as st
import folium
from folium import Choropleth
import pandas as pd
import json

# Functie om groenaanbod in te delen in categorieën
def categorize_green_offer(green_value):
    if pd.isna(green_value):  # Als de waarde ontbreekt
        return 'Geen gegevens'
    elif green_value > 7.5:
        return 'Veel beter dan gemiddeld'
    elif 7.3 <= green_value <= 7.5:
        return 'Beter dan gemiddeld'
    elif 6.6 <= green_value <= 7.2:
        return 'Rond het stedelijk gemiddelde'
    elif 6.3 <= green_value <= 6.5:
        return 'Slechter dan gemiddeld'
    else:
        return 'Veel slechter dan gemiddeld'

# Pas de functie toe om de buurten te categoriseren
gdf['Categorie'] = gdf['Aanbod groen (1-10)'].apply(categorize_green_offer)

# Maken van een dictionary voor kleuren op basis van de categorische indeling
category_colors = {
    'Veel beter dan gemiddeld': 'green',
    'Beter dan gemiddeld': 'lightgreen',
    'Rond het stedelijk gemiddelde': 'yellow',
    'Slechter dan gemiddeld': 'orange',
    'Veel slechter dan gemiddeld': 'red',
    'Geen gegevens': 'white'  # Wit voor ontbrekende gegevens
}

# Voeg de kleur toe aan de DataFrame op basis van de categorie
gdf['Color'] = gdf['Categorie'].apply(lambda x: category_colors[x])

# Maak de basiskaart
m = folium.Map(location=[52.3776, 4.9141], zoom_start=12)

# Functie om de kleur van elke buurt in het GeoJSON-bestand toe te passen
def style_function(feature):
    buurtnaam = feature['properties']['Buurt']
    if buurtnaam in gdf['Buurt'].values:
        color = gdf[gdf['Buurt'] == buurtnaam]['Color'].values[0]
    else:
        color = 'white'  # Wit als de buurt niet in de data zit
    return {
        'fillColor': color,
        'color': 'black',  # Rand van de buurten zwart maken
        'weight': 0.5,
        'fillOpacity': 0.7
    }

# Functie om een pop-up toe te voegen
def popup_function(feature):
    buurtnaam = feature['properties']['Buurt']
    if buurtnaam in gdf['Buurt'].values:
        waarde = gdf[gdf['Buurt'] == buurtnaam]['Aanbod groen (1-10)'].values[0]
        return f"<b>{buurtnaam}</b><br>Aanbod groen: {waarde:.1f}"
    else:
        return f"<b>{buurtnaam}</b><br>Geen gegevens beschikbaar"

# Voeg de geojson-data toe aan de kaart met de stylingfunctie en pop-up
geojson = GeoJson(
    gdf,
    name="Groenaanbod per Buurt",
    style_function=style_function,
    tooltip=GeoJsonTooltip(
        fields=["Buurt"],
        aliases=["Buurt:"],
        sticky=True
    ),
    popup=folium.GeoJsonPopup(fields=[], labels=False, parse_html=False)
)
geojson.add_child(
    folium.features.GeoJsonPopup(fields=[], labels=False, parse_html=False)
)
geojson.add_to(m)

# Voeg een legenda toe (handmatig toegevoegd voor duidelijkheid)
legend_html = """
<div style="position: fixed; 
            bottom: 30px; left: 30px; width: 250px; height: 180px; 
            border:2px solid grey; background-color:white; z-index:9999;
            font-size: 12px; padding: 10px;">
    <b>Legenda</b><br>
    <i style="background: green; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></i>Veel beter dan gemiddeld<br>
    <i style="background: lightgreen; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></i>Beter dan gemiddeld<br>
    <i style="background: yellow; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></i>Rond het stedelijk gemiddelde<br>
    <i style="background: orange; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></i>Slechter dan gemiddeld<br>
    <i style="background: red; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></i>Veel slechter dan gemiddeld<br>
    <i style="background: white; width: 20px; height: 20px; display: inline-block; margin-right: 5px; border: 1px solid black;"></i>Geen gegevens<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Toon de kaart in Streamlit
st.title("Visualisatie Groenaanbod per Buurt")
st.markdown("""
    Deze kaart toont het groenaanbod in verschillende buurten van 2023. 
    De kleuren geven aan hoe het groenaanbod zich verhoudt tot het stedelijk gemiddelde van 6.9.
""")

# Gebruik Streamlit's components om de Folium-kaart weer te geven
from streamlit.components.v1 import html
html(m._repr_html_(), width=800, height=600)

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

