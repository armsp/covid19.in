#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
from datetime import date
#import webbrowser
import pandas as pd
import folium
from folium import plugins
map_kwargs = {"zoomSnap": 0.5}
m = folium.Map(location=[22.7041, 79.1025], tiles='CartoDB Positron', zoom_start=4.5, **map_kwargs)#, prefer_canvas=True)

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
for lon, lat, territory, cases, recovered, deaths in zip(list(df['Lon']), list(df['Lat']), list(df.iloc[:,1]), list(df.iloc[:,2]), list(df.iloc[:,3]), list(df.iloc[:,4])):
    popup_html=f"""
<table border-spacing: 0; border-collapse: collapse; display: block; width: 100%; overflow: auto;">
    <thead>
    <tr>
        <th colspan="3" style="padding: 6px 13px;font-weight: 600; border: 1px solid #dfe2e5;">{territory}</th>
    </tr>
        <tr style="border-top: 1px solid #c6cbd1; background-color: #fff; font-weight: bolder;">
            <td style="color: darkorange; padding: 0px 5px;
            border: 1px solid #dfe2e5;">Active Cases</td>
            <td style="padding: 0px 5px; color: red;
            border: 1px solid #dfe2e5;">Deaths</td>
            <td style="padding: 0px 5px; color: mediumseagreen;
            border: 1px solid #dfe2e5;">Recovered</td>
        </tr>
    </thead>
    <tbody>
        <tr style="border-top: 1px solid #c6cbd1; background-color: #fff; font-weight: bolder;">
            <td style="padding: 6px 13px;
            border: 1px solid #dfe2e5;">{cases}</td>
            <td style="padding: 6px 13px;
            border: 1px solid #dfe2e5;">{recovered}</td>
            <td style="padding: 6px 13px;
            border: 1px solid #dfe2e5;">{deaths}</td>
        </tr>
    </tbody>
</table>
"""
    folium.Circle(radius = (int(cases))*100,location=[lat, lon],color='crimson',fill=True,popup=folium.Popup(popup_html),**kwargs).add_to(m)

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