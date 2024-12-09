#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st # type: ignore
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
import geopandas as gpd # type: ignore
from folium.plugins import MarkerCluster # type: ignore

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
- **Energielabels** (A++++ tot B)  
- **Aardgasvrije woningen**  
- **Aantal zonnepanelen**  

Met deze visualisaties krijgt u inzicht in hoe buurten presteren op het gebied van duurzaamheid en hoe deze data stedenbouwkundig beleid kan ondersteunen.  

Gebruik de kaarten en grafieken om trends te ontdekken, buurten te vergelijken, en strategische inzichten te verkrijgen voor een duurzamer Amsterdam!
""")

gdf = gpd.read_file("output2.geojson")

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
        fields=["Buurt", "Duurzaamheidsindex", "Energielabel A++++ t/m B (%)", "aardgasvrije woningequivalenten", "aantal_zonnepanelen"],
        aliases=["Buurt:", "Duurzaamheidsindex:", "Energielabel A-B (%):", "Aardgasvrije woningen:", "Zonnepanelen:"],
        max_width=300
    )
).add_to(m)

# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)

st.subheader("Kaart: Duurzaamheidsindex per Stadsdeel")
st.markdown("""
Deze kaart toont het gemiddelde van de Duurzaamheidsindex per stadsdeel.  
Groene gebieden geven een hogere duurzaamheidsprestatie aan.
""")

gdf["Duurzaamheidsindex"] = pd.to_numeric(gdf["Duurzaamheidsindex"], errors="coerce")

# Controleer opnieuw of het type correct is
print(gdf["Duurzaamheidsindex"].dtype)

# Daarna de berekening opnieuw proberen voor de stadsdelen
if "Stadsdeel" in gdf.columns:
    # Bereken het gemiddelde van de Duurzaamheidsindex per Stadsdeel
    stadsdeel_avg = gdf.dissolve(by="Stadsdeel", aggfunc="mean", as_index=False)
    
    # Maak de kaart voor Duurzaamheidsindex per Stadsdeel
    m = folium.Map(location=[52.3728, 4.8936], zoom_start=12)

    folium.Choropleth(
        geo_data=stadsdeel_avg,
        data=stadsdeel_avg,
        columns=["Stadsdeel", "Duurzaamheidsindex"],
        key_on="feature.properties.Stadsdeel",
        fill_color="BuGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Duurzaamheidsindex"
    ).add_to(m)

    folium.GeoJson(
        data=stadsdeel_avg,
        style_function=lambda x: {"fillOpacity": 0, "color": "white", "weight": 0.5},
        highlight_function=lambda x: {"weight": 2, "color": "blue", "fillOpacity": 0.7},
        tooltip=folium.GeoJsonTooltip(
            fields=["Stadsdeel", "Duurzaamheidsindex"],
            aliases=["Stadsdeel:", "Gemiddelde Duurzaamheidsindex:"],
            localize=True
        ),
    ).add_to(m)

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

# Introductie
st.subheader("Cluster Map: Locaties van Aardgasvrije Woningequivalenten")
st.markdown("""
Deze kaart toont de locaties van **aardgasvrije woningequivalenten** in Amsterdam.  
De markers zijn geclusterd om een overzichtelijker beeld te geven.  
Klik op een cluster of een individuele marker voor meer informatie over het aantal aardgasvrije woningequivalenten in een specifieke buurt.
""")

# Basiskaart
m = folium.Map(location=[52.3728, 4.8936], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# Markers toevoegen
for index, row in gdf.iterrows():
    folium.Marker(
        location=[row["LAT"], row["LNG"]],
        popup=f"<b>Buurt:</b> {row['Buurt']}<br><b>Aardgasvrije Equivalenten:</b> {row['aardgasvrije woningequivalenten']}"
    ).add_to(marker_cluster)


# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)


