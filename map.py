#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
from datetime import date
#import webbrowser
import pandas as pd
import folium
from folium import plugins
m = folium.Map(location=[23.7041, 87.1025], tiles='CartoDB Positron', zoom_start=4)#, prefer_canvas=True)

list_of_files = glob.glob('./datasets/statewise_distribution/*.csv') # * means all if need specific format then *.csv
#latest_file = max(list_of_files, key=lambda x: x.split('.')[1].split('-')[2])
#print(list_of_files)
sorted_files = sorted(list_of_files, key=lambda d: tuple(map(int, d.split('/')[-1].split('.')[0].split('-'))))
#print(latest_file)
#data_file = f'./datasets/statewise_distribution/{str(date.today())}.csv'
data_file = sorted_files[-1]
df = pd.read_csv(data_file)
kwargs = {'stroke': True, 'weight': 1.5, 'opacity': 0.8, 'bubblingMouseEvents': False}
#https://leafletjs.com/reference-1.3.4.html#path-weight
for lon, lat, ind, forei in zip(list(df['Lon']), list(df['Lat']), list(df['Total Confirmed cases (Indian National)']), list(df['Total Confirmed cases ( Foreign National )'])):
    #print(lon,lat,ind,forei)
    folium.Circle(
        radius=(ind+forei)*2000,
        location=[lat, lon],
        #popup='',
        color='crimson',
        fill=True,
        **kwargs
    ).add_to(m)
plugins.ScrollZoomToggler().add_to(m)
    #folium.CircleMarker(
    #    location=[lat, lon],
    #    radius=(ind+forei)/4,
    #    #popup='Laurelhurst Park',
    #    color='crimson',
    #    fill=True,
    #    fill_color='crimson',
    #    **kwargs
    #).add_to(m)
m.save('foliummap.html')
#webbrowser.open('foliummap.html')