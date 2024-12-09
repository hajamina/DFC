#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from folium.plugins import MarkerCluster

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

# Choropleth toevoegen
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "Duurzaamheidsindex"],
    key_on="feature.properties.Buurtcode",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Duurzaamheidsindex (0-1)"
).add_to(m)

# Popup met buurtinformatie toevoegen


for _, row in gdf.iterrows():
    popup = folium.Popup(
        f"""
        <b>Buurt:</b> {row['Buurt']}<br>
        <b>Duurzaamheidsindex:</b> {row['Duurzaamheidsindex']:.3f}<br>
        <b>Energielabel A-B (%):</b> {row['Energielabel A++++ t/m B (%)']}<br>
        <b>Aardgasvrije woningen:</b> {row['aardgasvrije woningequivalenten']}<br>
        <b>Zonnepanelen:</b> {row['aantal_zonnepanelen']}
        """,
        max_width=300
    )
    marker = folium.Marker(location=[row["LAT"], row["LNG"]], popup=popup)
    marker.add_to(m)

# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)

from folium.plugins import HeatMap

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

# Legenda toevoegen
legend_html = '''
<div style="position: fixed; 
            bottom: 10px; left: 10px; width: 300px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Legenda:</b><br>
    <i style="background: #3186cc; color: white; font-size:12px; padding: 4px 6px; border-radius: 3px;">Cluster</i>
    : Groepering van meerdere locaties<br>
    <i style="background: #3186cc; color: white; font-size:12px; padding: 4px 6px; border-radius: 3px;">Marker</i>
    : Individuele locatie<br>
    <b>Klik op een marker:</b> Bekijk details zoals het aantal aardgasvrije equivalenten.<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Kaart weergeven in Streamlit
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
for index, row in data.iterrows():
    folium.Marker(
        location=[row["LAT"], row["LNG"]],
        popup=f"<b>Buurt:</b> {row['Buurt']}<br><b>Aardgasvrije Equivalenten:</b> {row['aardgasvrije woningequivalenten']}"
    ).add_to(marker_cluster)

# Legenda toevoegen
legend_html = '''
<div style="position: fixed; 
            bottom: 10px; left: 10px; width: 300px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Legenda:</b><br>
    <i style="background: #3186cc; color: white; font-size:12px; padding: 4px 6px; border-radius: 3px;">Cluster</i>
    : Groepering van meerdere locaties<br>
    <i style="background: #3186cc; color: white; font-size:12px; padding: 4px 6px; border-radius: 3px;">Marker</i>
    : Individuele locatie<br>
    <b>Klik op een marker:</b> Bekijk details zoals het aantal aardgasvrije equivalenten.<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Kaart weergeven in Streamlit
st_folium(m, width=800, height=500)


from folium.plugins import DualMap

st.subheader("Vergelijking: Twee Buurten")
dual_map = DualMap(location=[52.3728, 4.8936], zoom_start=12)

# Duurzaamheidsindex toevoegen aan de eerste kaart
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "Duurzaamheidsindex"],
    key_on="feature.properties.Buurtcode",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2
).add_to(dual_map.m1)

# Energielabels toevoegen aan de tweede kaart
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["Buurtcode", "Energielabel_normalized"],
    key_on="feature.properties.Buurtcode",
    fill_color="BuPu",
    fill_opacity=0.7,
    line_opacity=0.2
).add_to(dual_map.m2)

st_folium(dual_map, width=800, height=500)

# In[ ]:




