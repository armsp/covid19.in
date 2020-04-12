import os
import glob
import json
import logging as lg
from pathlib import Path
from datetime import date, datetime

import yaml
import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
import matplotlib.transforms as transforms
from jinja2 import Environment, FileSystemLoader

from jhu_handler import melt_data, get_jhu_stats, get_india_stats_from_jhu
from mohfw_handler import mohfw_data_to_df, add_lat_lon, get_mohfw_stats, extract_clean_df

lg.basicConfig(level=lg.DEBUG, format=("[%(asctime)s] [%(levelname)8s] %(filename)s - %(message)s"), datefmt="%d-%b-%Y %I:%M:%S %p")#, filename='log.txt', filemode='a+'
template_loader = FileSystemLoader('./templates')
template_env = Environment(loader=template_loader)
TEMPLATE = "template.html"
template = template_env.get_template(TEMPLATE)

sns.set(style="ticks")
sns.set_context("paper", rc={"font.size":8,"axes.titlesize":9,"axes.labelsize":10,"lines.linewidth": 1.5,'lines.markersize':3})#paper,talk,notebook
fig, ax = plt.subplots()

covid_data_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_time_series')

cases_path = os.path.join(covid_data_path, 'time_series_covid19_confirmed_global.csv')
recoveries_path = os.path.join(covid_data_path, 'time_series_covid19_recovered_global.csv')
deaths_path = os.path.join(covid_data_path, 'time_series_covid19_deaths_global.csv')

Path(os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid19-in', 'datasets', 'timeseries_records')).mkdir(parents=True, exist_ok=True)
Path(os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid19-in', 'datasets', 'statewise_distribution')).mkdir(parents=True, exist_ok=True)

mohfw_data_df = mohfw_data_to_df()
table_df = extract_clean_df(mohfw_data_df)
table_df = add_lat_lon(table_df)
#print("Table DF")
#print(table_df)
if not table_df.empty:
    table_df.to_csv(f'./datasets/statewise_distribution/{str(date.today())}.csv', sep=',', encoding='utf-8', index=False)
else:
    lg.warning("Failed to write statewise distribution file. Map will use old file even though new data is available")

in_cases_df, in_recoveries_df, in_deaths_df = get_india_stats_from_jhu(cases_path, recoveries_path, deaths_path)
# Transforming data to a format lineplot likes
final_df = melt_data(in_cases_df, in_deaths_df, in_recoveries_df)

final_df.to_csv(f'./datasets/timeseries_records/cases_deaths_recoveries_timeseries.csv', sep=',', encoding='utf-8', index=False)

## Using data that is larger
live_cases = in_cases_df
live_recoveries = in_recoveries_df
live_deaths = in_deaths_df
date_today_str = date.today().strftime("%-m/%-d/%y")
print(f"Today's date is = {date_today_str}")
date_today = date.today()
print(date_today)
#check date in index
live_cases_latest_date = live_cases.columns[-1]
live_recoveries_latest_date = live_recoveries.columns[-1]
live_deaths_latest_date = live_deaths.columns[-1]
#get today's stats from mohfw
mohfw_stats = get_mohfw_stats(table_df)
print(mohfw_stats)
#compare dates
live_cases_latest_date = datetime.strptime(live_cases_latest_date, "%m/%d/%y").date()
live_recoveries_latest_date = datetime.strptime(live_recoveries_latest_date, "%m/%d/%y").date()
live_deaths_latest_date = datetime.strptime(live_deaths_latest_date, "%m/%d/%y").date()
print(live_cases_latest_date, live_recoveries_latest_date, live_deaths_latest_date)
if date_today > live_cases_latest_date:
    if mohfw_stats['in_stats']['cases'] > int(live_cases.iloc[:,-1:].iloc[0]):
        print(mohfw_stats['in_stats']['cases'], int(live_cases.iloc[:,-1:].iloc[0]))
        live_cases[date_today_str] = mohfw_stats['in_stats']['cases']# new column in live with mohfw value
elif date_today == live_cases_latest_date:
    if mohfw_stats['in_stats']['cases'] > int(live_cases.iloc[:,-1:].iloc[0]):
        live_cases.iloc[:,-1:].iloc[0] = mohfw_stats['in_stats']['cases']

if date_today > live_recoveries_latest_date:
    print(mohfw_stats['in_stats']['recovered'], int(live_recoveries.iloc[:,-1:].iloc[0]))
    if mohfw_stats['in_stats']['recovered'] > int(live_recoveries.iloc[:,-1:].iloc[0]):
        live_recoveries[date_today_str] = mohfw_stats['in_stats']['recovered']
elif date_today == live_recoveries_latest_date:
    if mohfw_stats['in_stats']['recovered'] > int(live_recoveries.iloc[:,-1:].iloc[0]):
        live_recoveries.iloc[:,-1:].iloc[0] = mohfw_stats['in_stats']['recovered']

if date_today > live_deaths_latest_date:
    if mohfw_stats['in_stats']['deaths'] > int(live_deaths.iloc[:,-1:].iloc[0]):
        live_deaths[date_today_str] = mohfw_stats['in_stats']['deaths']
elif date_today == live_deaths_latest_date:
    if mohfw_stats['in_stats']['deaths'] > int(live_deaths.iloc[:,-1:].iloc[0]):
        live_deaths.iloc[:,-1:].iloc[0] = mohfw_stats['in_stats']['deaths']
print(live_cases)
print(live_deaths)
print(live_recoveries)
plot_df = melt_data(live_cases, live_deaths, live_recoveries)
#plot_df['index'] = plot_df['index'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
plot_df.to_csv(f'./datasets/timeseries_records/live_cases_deaths_recoveries_timeseries.csv', sep=',', encoding='utf-8', index=False)

jhu_df = melt_data(in_cases_df, in_deaths_df, in_recoveries_df)
#jhu_df['index'] = jhu_df['index'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
jhu_df.to_csv(f'./datasets/timeseries_records/cases_deaths_recoveries_timeseries.csv', sep=',', encoding='utf-8', index=False)

# Make plot
ax = plt.axes()
kwargs = {'markeredgewidth': 0.25}
sns.lineplot(x='index', y='value', hue='category', hue_order=['cases', 'recoveries', 'deaths'], style='category', palette={'cases': 'Orange', 'recoveries': 'Green', 'deaths': 'Red'}, dashes=False, data=plot_df, markers={'deaths': 'X', 'recoveries': 'd', 'cases': 'o'}, ax=ax, **kwargs)
# Draw horizontal lines at max values
cases_max = int(plot_df['value'].where(plot_df['category'] == 'cases').max())
deaths_max = int(plot_df['value'].where(plot_df['category'] == 'deaths').max())
recoveries_max = int(plot_df['value'].where(plot_df['category'] == 'recoveries').max())
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
ax.grid(color='#f3f3f3', linestyle=':', linewidth=0.5)##cdcdcd #f3f3f3 #D3D3D3
ratio = 0.5
ax.set_aspect(1.0/ax.get_data_ratio()*ratio)
plt.xticks(fontsize=6, rotation=75)
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
last_x_tick = date2num(plot_df['index'].values[-1])
xt = np.append(xt, last_x_tick)
xtl = xt.tolist()
ax.set_xticks(xt)
ax.axvline(last_x_tick, ls='dotted', linewidth=0.5)

plt.savefig("graph.svg", format='svg', dpi=1200, bbox_inches='tight')
plt.show()

# Make index.html
# accquire latest statistics
covid_daily_reports_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_daily_reports')
jhu_stats = get_jhu_stats(covid_daily_reports_path)

#Compare JHU Stats with MoHFW stats for india
if mohfw_stats['in_stats']['cases'] > jhu_stats['in_stats']['cases']:
    in_cases_greater = mohfw_stats['in_stats']['cases']
else:
    in_cases_greater = jhu_stats['in_stats']['cases']

if mohfw_stats['in_stats']['deaths'] > jhu_stats['in_stats']['deaths']:
    in_deaths_greater = mohfw_stats['in_stats']['deaths']
else:
    in_deaths_greater = jhu_stats['in_stats']['deaths']

if mohfw_stats['in_stats']['recovered'] > jhu_stats['in_stats']['recovered']:
    in_recovered_greater = mohfw_stats['in_stats']['recovered']
else:
    in_recovered_greater = jhu_stats['in_stats']['recovered']

#world stats
w_confirmed = jhu_stats['w_stats']['cases']
w_deaths = jhu_stats['w_stats']['deaths']
w_recovered = jhu_stats['w_stats']['recovered']
## read resource yaml
with open('resources.yaml') as fs:
    resources = yaml.load(fs, yaml.SafeLoader)

# Get ready to pass data to template
stats_dict = {'w_cases': w_confirmed, 'w_deaths': w_deaths, 'w_recovered': w_recovered, 'i_cases': in_cases_greater, 'i_deaths': in_deaths_greater , 'i_recovered': in_recovered_greater}

commit_info_dict = {'current_time': datetime.now().strftime("%B %d, %Y at %I:%M %p"), 'commit_sha': os.environ['GITHUB_SHA']}

state_info = {'link': f"https://github.com/armsp/covid19.in/blob/master/datasets/statewise_distribution/{str(date.today())}.csv"}

namespace = {'statistics': stats_dict, 'safety_resources': resources['SAFETY & PREVENTION'], 'about': resources['Virus & the Disease'], 'fakes': resources['Fads, Fake News & Scams'], 'misc': resources['Miscellaneous'], 'commit_info': commit_info_dict, 'state_info': state_info}
rendered_html = template.render(**namespace)
with open("index.html", "w+") as f:
    f.write(rendered_html)