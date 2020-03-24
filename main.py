#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import json
import yaml
from pathlib import Path
from datetime import date, datetime
from urllib import request, parse
#import webbrowser

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

template_loader = FileSystemLoader('./templates')
template_env = Environment(loader=template_loader)

sns.set(style="ticks")#darkgrid, whitegrid,dark,white,ticks
#sns.set(font_scale = 0.5)
sns.set_context("paper", rc={"font.size":8,"axes.titlesize":15,"axes.labelsize":10,"lines.linewidth": 2,'lines.markersize':4})#paper,talk,notebook
fig, ax = plt.subplots()

covid_data_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_time_series')

cases_path = os.path.join(covid_data_path, 'time_series_covid19_confirmed_global.csv')
#recoveries_path = os.path.join(covid_data_path, 'time_series_19-covid-Recovered.csv')
# Recovery data is not accurate, need to find another source
deaths_path = os.path.join(covid_data_path, 'time_series_covid19_deaths_global.csv')

cases = pd.read_csv(cases_path)
#recoveries = pd.read_csv(recoveries_path)
deaths = pd.read_csv(deaths_path)

in_cases = cases[cases['Country/Region'] == 'India']
#in_recoveries = recoveries[recoveries['Country/Region'] == 'India']
in_deaths = deaths[deaths['Country/Region'] == 'India']

in_cases_df = in_cases[in_cases.columns[4:]]
#in_recoveries_df = in_recoveries[in_recoveries.columns[4:]]
in_deaths_df = in_deaths[in_deaths.columns[4:]]

#sns.barplot(data=in_cases_df, palette=sns.color_palette("Oranges", len(in_cases_df.columns)), ax=ax)
#sns.barplot(data=in_recoveries_df, palette=sns.color_palette("Greens", len(in_recoveries_df.columns)), ax=ax)
#sns.barplot(data=in_deaths_df, palette=sns.color_palette("Reds", len(in_deaths_df.columns)), ax=ax)

#plt.title('COVID-19 Cases, Deaths and Recovery Graph')
#ax.set(xlabel='Time ->', ylabel='Cases')
#plt.xticks(fontsize=6, rotation=75)
#plt.yticks(fontsize=6)
#ax.axhline(int(in_cases_df.iloc[:, -1]), ls='--')
#plt.gca().set_position([0, 0, 1, 1])
#plt.savefig("graph.svg", format='svg', dpi=1200, bbox_inches='tight')
#plt.show()#must be in the end otherwise saving to svg won't work

Path(os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid19-in', 'datasets', 'timeseries_records')).mkdir(parents=True, exist_ok=True)
Path(os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid19-in', 'datasets', 'statewise_distribution')).mkdir(parents=True, exist_ok=True)

## Download, modify and store MOHFW dataset
url = 'http://www.mohfw.gov.in/'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
#param_dict = {"f": "json", "singleLine": "delhi, IND", "maxLocations": 1}
#params = parse.urlencode(param_dict).encode('UTF-8')
req = request.Request(url, headers=header)#, data=params)
response = request.urlopen(req)

table_list = pd.read_html(response, header=0)
#MOHFW Website changed again. Looks like they keep the table in the end
table_df = table_list[-1].head(-1)

def geocode(city):
    url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    param_dict = {"f": "json", "singleLine": f"{city}, IND", "maxLocations": 1}
    params = parse.urlencode(param_dict).encode('UTF-8')
    req = request.Request(url, headers=header, data=params)

    try:
      response = request.urlopen(req)
    except Exception as e:
      #logging.error("Request Failed", exc_info=True)
      print("Request Failed")
      raise e
    else:
      #logging.debug(response.getcode())
      #logging.debug(response.info())
      pass

    if response.getcode() == 200:
      response_dict = json.load(response)
      return (response_dict['candidates'][0]["location"]["x"], response_dict['candidates'][0]["location"]["y"])

def add_lat_lon(df):
    df['Lon'], df['Lat'] = zip(*df['Name of State / UT'].map(geocode))
    return df

table_df = add_lat_lon(table_df)
table_df.to_csv(f'./datasets/statewise_distribution/{str(date.today())}.csv', sep=',', encoding='utf-8', index=False)

#####################
in_cases_df.index = pd.Index(['cases'], name='time')
in_deaths_df.index = pd.Index(['deaths'], name='time')
#in_recoveries_df.index = pd.Index(['recoveries'], name='time')

cases_T = in_cases_df.T
deaths_T = in_deaths_df.T
#recoveries_T = in_recoveries_df.T
temp_df = cases_T.join([deaths_T])#, recoveries_T])

final_df = pd.melt(temp_df.reset_index(), id_vars='index', var_name='category', value_name='value')
final_df['index'] = final_df['index'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
#changing the name of file on 25-03-2020 since JHU deprecated recoveries data
final_df.to_csv(f'./datasets/timeseries_records/cases_deaths_timeseries.csv', sep=',', encoding='utf-8', index=False)

ax = plt.axes()
kwargs = {'markeredgewidth': 0.25}
sns.lineplot(x='index', y='value', hue='category', hue_order=['cases', 'deaths'], style='category', palette={'cases': 'Orange', 'deaths': 'Red'}, dashes=False, data=final_df, markers={'deaths': 'X', 'cases': 'o'}, ax=ax, **kwargs)
ax.axhline(int(final_df['value'].where(final_df['category'] == 'cases').max()), ls='dotted')
#'-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
plt.title('COVID-19 Cases and Deaths Graph')
ax.set(xlabel='Time ->', ylabel='Cases / Deaths')
ax.legend(labels=['Confirmed Cases', 'Deaths'])#loc='upper left'
ax.set(xticks=final_df['index'].values)
ax.grid(color='#f3f3f3', linestyle=':', linewidth=0.5)##cdcdcd #f3f3f3 #D3D3D3
ratio = 0.5
ax.set_aspect(1.0/ax.get_data_ratio()*ratio)
plt.xticks(fontsize=6, rotation=75)
plt.yticks(fontsize=6)
plt.savefig("graph.svg", format='svg', dpi=1200, bbox_inches='tight')
plt.show()

### Write templates
TEMPLATE = "template.html"
template = template_env.get_template(TEMPLATE)
#get stats
covid_daily_reports_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_daily_reports')

list_of_files = glob.glob(covid_daily_reports_path+"/*.csv") # * means all if need specific format then *.csv
print(list_of_files)
#latest_file = max(list_of_files, key=lambda x: x.split('/')[-1].split('.')[0].split('-')[1])
sorted_files = sorted(list_of_files, key=lambda d: tuple(map(int, d.split('/')[-1].split('.')[0].split('-'))))
latest_file = sorted_files[-1]
print(latest_file)
## Getting stats data
stats = pd.read_csv(latest_file)
in_confirmed = int(stats.loc[stats['Country_Region'] == "India"]['Confirmed'])
in_deaths = int(stats.loc[stats['Country_Region'] == "India"]['Deaths'])
in_recovered = int(stats.loc[stats['Country_Region'] == "India"]['Recovered'])
#sum of time series data seems > daily report data. Change it after confirmation
w_confirmed = stats['Confirmed'].sum()
w_recovered = stats['Recovered'].sum()
w_deaths = stats['Deaths'].sum()


## read resource yaml
with open('resources.yaml') as fs:
    resources = yaml.load(fs, yaml.SafeLoader)

stats_dict={'w_cases': w_confirmed, 'w_deaths': w_deaths, 'w_recovered': w_recovered, 'i_cases': in_confirmed, 'i_deaths': in_deaths , 'i_recovered': in_recovered}
commit_info_dict = {'current_time': datetime.now(), 'commit_sha': os.environ['GITHUB_SHA']}
namespace = {'statistics': stats_dict, 'safety_resources': resources['SAFETY'], 'about': resources['Virus & the Disease'], 'fakes': resources['Fads & Fake News'], 'misc': resources['Miscellaneous'], 'commit_info': commit_info_dict}

rendered_html = template.render(**namespace)

with open("index.html", "w+") as f:
    f.write(rendered_html)

#webbrowser.open("index_.html")