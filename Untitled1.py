#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st # type: ignore
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
import geopandas as gpd # type: ignore
from folium.plugins import MarkerCluster # type: ignore
import pandas as pd
import numpy as np 
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

st.subheader("Kaart van de Duurzaamheidsindex")
st.markdown("""
Deze kaart toont de **Duurzaamheidsindex** voor Amsterdamse buurten in 2024.  
De kleuren representeren de duurzaamheidsprestaties, waarbij groen een hogere duurzaamheid betekent.
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
        aliases=["Buurt:", "Duurzaamheidsindex:", "Aanbod groen (1-10):", "Aardgasvrije woningen:", "Zonnepanelen:"],
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

legend_html = '''
<div style="position: fixed; 
            bottom: 10px; left: 10px; width: 250px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Legenda:</b><br>
    <i style="background: #ffeda0; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Hoge concentratie zonnepanelen<br>
    <i style="background: #feb24c; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Middelhoge concentratie<br>
    <i style="background: #f03b20; width: 20px; height: 10px; display: inline-block; border: 1px solid grey;"></i>
    Lage concentratie<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Kaart in Streamlit weergeven
st_folium(m, width=800, height=500)

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
