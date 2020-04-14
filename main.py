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
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
import matplotlib.transforms as transforms
from jinja2 import Environment, FileSystemLoader

template_loader = FileSystemLoader('./templates')
template_env = Environment(loader=template_loader)

sns.set(style="ticks")#darkgrid, whitegrid,dark,white,ticks
#sns.set(font_scale = 0.5)
sns.set_context("paper", rc={"font.size":8,"axes.titlesize":9,"axes.labelsize":10,"lines.linewidth": 2,'lines.markersize':4})#paper,talk,notebook
fig, ax = plt.subplots()

covid_data_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_time_series')

cases_path = os.path.join(covid_data_path, 'time_series_covid19_confirmed_global.csv')
recoveries_path = os.path.join(covid_data_path, 'time_series_covid19_recovered_global.csv')
deaths_path = os.path.join(covid_data_path, 'time_series_covid19_deaths_global.csv')

cases = pd.read_csv(cases_path)
recoveries = pd.read_csv(recoveries_path)
deaths = pd.read_csv(deaths_path)

in_cases = cases[cases['Country/Region'] == 'India']
in_recoveries = recoveries[recoveries['Country/Region'] == 'India']
in_deaths = deaths[deaths['Country/Region'] == 'India']

in_cases_df = in_cases[in_cases.columns[4:]]
in_recoveries_df = in_recoveries[in_recoveries.columns[4:]]
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
#changed again - added another footer row
#changed again - 1 footer row
#changed again - 2 footer - need to automate this process
# again
table_df = table_list[-1]
table_df = table_df[pd.to_numeric(table_df['S. No.'], errors='coerce').notna()]
print(table_df.columns)
print(table_df)
def geocode(city):
    url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    param_dict = {"f": "json", "singleLine": f"{city}, IND", "maxLocations": 2}
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
      if city == 'Andhra Pradesh':
        return (response_dict['candidates'][1]["location"]["x"], response_dict['candidates'][1]["location"]["y"])
      else:
        return (response_dict['candidates'][0]["location"]["x"], response_dict['candidates'][0]["location"]["y"])


def add_lat_lon(df):
    df['Lon'], df['Lat'] = zip(*(df['Name of State / UT'].map(geocode))) #SettingWithCopyWarning
    return df

table_df = add_lat_lon(table_df)
table_df.to_csv(f'./datasets/statewise_distribution/{str(date.today())}.csv', sep=',', encoding='utf-8', index=False)

#####################
in_cases_df.index = pd.Index(['cases'], name='time')
in_deaths_df.index = pd.Index(['deaths'], name='time')
in_recoveries_df.index = pd.Index(['recoveries'], name='time')

cases_T = in_cases_df.T
deaths_T = in_deaths_df.T
recoveries_T = in_recoveries_df.T
temp_df = cases_T.join([deaths_T, recoveries_T])

final_df = pd.melt(temp_df.reset_index(), id_vars='index', var_name='category', value_name='value')
final_df['index'] = final_df['index'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
#changing the name of file on 25-03-2020 since JHU deprecated recoveries data
#changing the name of file since recoveries data appeared again
final_df.to_csv(f'./datasets/timeseries_records/cases_deaths_recoveries_timeseries.csv', sep=',', encoding='utf-8', index=False)

# live updating JHU data using MoHFW
#live_cases_deaths_recoveries_timeseries = os.path.join(covid_data_path, 'time_series_covid19_deaths_global.csv')
#live_df = pd.read_csv(live_cases_deaths_recoveries_timeseries)
#table_df - for cases cumulative, deaths cumulative, recov cumulativve
#today = datetime.today() -> format it to 1/22/20 type
#extract last column of each category, live_cases_deaths_recoveries_timeseries
#see if date matches today
#if yes - update it
#if no, add new column
#now plot this

ax = plt.axes()
kwargs = {'markeredgewidth': 0.25}
sns.lineplot(x='index', y='value', hue='category', hue_order=['cases', 'recoveries', 'deaths'], style='category', palette={'cases': 'Orange', 'recoveries': 'Green', 'deaths': 'Red'}, dashes=False, data=final_df, markers={'deaths': 'X', 'recoveries': 'd', 'cases': 'o'}, ax=ax, **kwargs)

cases_max = int(final_df['value'].where(final_df['category'] == 'cases').max())
deaths_max = int(final_df['value'].where(final_df['category'] == 'deaths').max())
recoveries_max = int(final_df['value'].where(final_df['category'] == 'recoveries').max())
ax.axhline(cases_max, ls='dotted', linewidth=0.5)
ax.axhline(deaths_max, ls='dotted', linewidth=0.5)
ax.axhline(recoveries_max, ls='dotted', linewidth=0.5)

#'-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
plt.title('COVID-19 Cases, Recoveries & Deaths Graph')
ax.set(xlabel='Time ->', ylabel='Cases / Deaths')
ax.xaxis.label.set_visible(False)
ax.yaxis.label.set_visible(False)
ax.legend(labels=['Confirmed Cases', 'Recoveries', 'Deaths'], frameon=False)#loc='upper left'
myFmt = DateFormatter("%d %b %y")
ax.xaxis.set_major_formatter(myFmt)
#ax.set(xticks=final_df['index'].values)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
#ax.spines['left'].set_edgecolor('gray')
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
ax.tick_params(axis="x", direction='in', length=5)
ax.get_yaxis().set_visible(False)
ax.grid(color='#f3f3f3', linestyle=':', linewidth=0.5)##cdcdcd #f3f3f3 #D3D3D3
ratio = 0.5
ax.set_aspect(1.0/ax.get_data_ratio()*ratio)
plt.xticks(fontsize=6, rotation=30, ha='right')
plt.yticks(fontsize=6)

#trans = transforms.blended_transform_factory(ax.get_yticklabels()[0].get_transform(), ax.transData)
#ax.text(0, cases_max, color="red", s=cases_max, transform=trans, ha="right", va="center")
#ax.text(0, deaths_max, color="red", s=deaths_max, transform=trans, ha="right", va="center")
ax.text(0.01, cases_max, cases_max, color="red", transform=ax.get_yaxis_transform(), ha="left", va="bottom")
ax.text(0.01, deaths_max, deaths_max, color="red", transform=ax.get_yaxis_transform(), ha="left", va="bottom")
ax.text(0.01, recoveries_max, recoveries_max, color="green", transform=ax.get_yaxis_transform(), ha="left", va="bottom")
#ax.annotate(cases_max, [ax.get_xticks()[-1], cases_max], va='bottom', ha='right', color='red')
#ax.annotate(deaths_max, [ax.get_xticks()[-1], deaths_max], va='bottom', ha='left', color='red')
xt = ax.get_xticks()
last_x_tick = date2num(final_df['index'].values[-1])
xt = np.append(xt, last_x_tick)
xtl = xt.tolist()
ax.set_xticks(xt)
ax.axvline(last_x_tick, ls='dotted', linewidth=0.5)
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
commit_info_dict = {'current_time': datetime.now().strftime("%B %d, %Y at %I:%M %p"), 'commit_sha': os.environ['GITHUB_SHA']}
state_info = {'link': f"https://github.com/armsp/covid19.in/blob/master/datasets/statewise_distribution/{str(date.today())}.csv"}
namespace = {'statistics': stats_dict, 'safety_resources': resources['SAFETY & PREVENTION'], 'about': resources['Virus & the Disease'], 'fakes': resources['Fads, Fake News & Scams'], 'misc': resources['Miscellaneous'], 'commit_info': commit_info_dict, 'state_info': state_info}

rendered_html = template.render(**namespace)

with open("index.html", "w+") as f:
    f.write(rendered_html)

#webbrowser.open("index_.html")