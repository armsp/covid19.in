import os
import glob
from datetime import date
import pandas as pd
import folium
from folium import plugins
from folium.features import GeoJson, GeoJsonTooltip
import geopandas as gpd

map_kwargs = {"zoomSnap": 0.5}
m = folium.Map(location = [20.5937, 78.9629], tiles='CartoDB Positron', zoom_start=4.5, **map_kwargs)

list_of_files = glob.glob('./datasets/clean_daily_statewise_distribution/2020-*.csv')
sorted_files = sorted(list_of_files, key=lambda d: tuple(map(int, d.split('/')[-1].split('.')[0].split('-'))))
data_file = sorted_files[-1]
df = pd.read_csv(data_file)
#kwargs = {'stroke': True, 'weight': 1.5, 'opacity': 0.8, 'bubblingMouseEvents': False}


#df = pd.read_csv('../../datasets/clean_daily_statewise_distribution/2020-05-16.csv')
df = df.drop(['sno.', 'lon', 'lat', 'day'], 1)
new = gpd.read_file('india_v2.json')
new = new.join(df.set_index('place'), on='state')
#new.crs = {'init' :'epsg:4326'}
new = new.to_crs(epsg='4326')

#bins = list(new['case'].quantile([0, 0.25, 0.5, 0.75, 1]))

c = folium.Choropleth(
    geo_data=new,
    name='choropleth',
    data=new,
    columns=['state', 'case'],
    key_on='feature.properties.state',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    legend_name='Cases',
    bins=8,
    reset=True,
    #popup=folium.features.GeoJsonTooltip(fields=['case']),
    nan_fill_color='white',
    nan_fill_opacity=0.4,
).add_to(m)
#folium.GeoJson(new, overlay=False, show=False, tooltip=folium.features.GeoJsonTooltip(fields=['case'])).add_to(m)
tooltip = GeoJsonTooltip(
    fields=["state", "case", "death", "recovery"],
    aliases=["State:", "Cases", "Deaths", "Recovered"],
    localize=True,
    sticky=False,
    labels=True,
    # style="""
    #     background-color: #F0EFEF;
    #     border: 2px solid black;
    #     border-radius: 3px;
    #     box-shadow: 3px;
    # """,
    #max_width=800,
)
tooltip.add_to(c.geojson)
#folium.LayerControl(k).add_to(m)

#m
plugins.ScrollZoomToggler().add_to(m)
m.save('foliummap.html')