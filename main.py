#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

sns.set(style="whitegrid")#darkgrid, whitegrid,dark,white,ticks
#sns.set(font_scale = 0.5)
sns.set_context("paper", rc={"font.size":8,"axes.titlesize":4,"axes.labelsize":5})#paper,talk,notebook
fig, ax = plt.subplots()

covid_data_path = os.path.join(os.environ['GITHUB_WORKSPACE'], 'covid-data', 'csse_covid_19_data', 'csse_covid_19_time_series')

cases_path = os.path.join(covid_data_path, 'time_series_19-covid-Confirmed.csv')
recoveries_path = os.path.join(covid_data_path, 'time_series_19-covid-Recovered.csv')
deaths_path = os.path.join(covid_data_path, 'time_series_19-covid-Deaths.csv')

cases = pd.read_csv(cases_path)
recoveries = pd.read_csv(recoveries_path)
deaths = pd.read_csv(deaths_path)

in_cases = cases[cases['Country/Region'] == 'India']
in_recoveries = recoveries[recoveries['Country/Region'] == 'India']
in_deaths = deaths[deaths['Country/Region'] == 'India']

in_cases_df = in_cases[in_cases.columns[4:]]
in_recoveries_df = in_recoveries_df[in_recoveries_df.columns[4:]]
in_deaths_df = in_deaths_df[in_deaths_df.columns[4:]]

#india = covid_data[covid_data['Country/Region'] == 'India']
#india_df = india[india.columns[4:]]

sns.barplot(data=in_cases_df, palette=sns.color_palette("Oranges", len(in_cases_df.columns)), ax=ax)
sns.barplot(data=in_recoveries_df, palette=sns.color_palette("Greens", len(in_recoveries_df.columns)), ax=ax)
sns.barplot(data=in_deaths_df, palette=sns.color_palette("Reds", len(in_deaths_df.columns)), ax=ax)

plt.xlabel = "Time"
plt.ylabel = "Cases"
plt.xticks(fontsize=6, rotation=75)
plt.yticks(fontsize=10)
plt.gca().set_position([0, 0, 1, 1])
plt.savefig("graph.svg", format='svg', dpi=1200)
plt.show()#must be in the end otherwise saving to svg won't work

namespace = {'current_time': datetime.now(), 'commit_sha': os.environ['GITHUB_SHA']}

with open('template.html') as f:
  template_html = f.read()

formatted_html = template_html.format(**namespace)

with open('index.html', 'w+') as f:
  f.write(formatted_html)

#india_df.index = pd.Index(['cases'], name='time')
#india_deaths_df.index = pd.Index(['deaths'], name='time')
#india_rec_df.index = pd.Index(['rec'], name='time')
#a = pd.DataFrame()
#b = pd.DataFrame()
#c = pd.DataFrame()

#a = india_df.T
#b = india_deaths_df.T
#c = india_rec_df.T
#d = a.join([b,c])
#e = pd.melt(d.reset_index(), id_vars='index', var_name='category', value_name='value')
#p = {"cases": sns.color_palette("Oranges", 51), "deaths" : sns.color_palette("Reds", 51), "rec": #sns.color_palette("Greens", 51)}
#sns.catplot(x='index', y='value', hue='category', data=e, kind='bar', palette=p)
#plt.show()


