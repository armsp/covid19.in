from datetime import date, datetime
import logging as lg
from urllib import request, parse
import glob

import requests
import pandas as pd

log = lg.getLogger(__name__)

def get_india_stats_from_jhu(cases_path, recoveries_path, deaths_path):
    cases = pd.read_csv(cases_path)
    recoveries = pd.read_csv(recoveries_path)
    deaths = pd.read_csv(deaths_path)

    in_cases = cases[cases['Country/Region'] == 'India']
    in_recoveries = recoveries[recoveries['Country/Region'] == 'India']
    in_deaths = deaths[deaths['Country/Region'] == 'India']

    in_cases_df = in_cases[in_cases.columns[4:]]
    in_recoveries_df = in_recoveries[in_recoveries.columns[4:]]
    in_deaths_df = in_deaths[in_deaths.columns[4:]]
    return (in_cases_df, in_recoveries_df, in_deaths_df)


def melt_data(in_cases_df, in_deaths_df, in_recoveries_df):
    in_cases_df.index = pd.Index(['cases'], name='time')
    in_deaths_df.index = pd.Index(['deaths'], name='time')
    in_recoveries_df.index = pd.Index(['recoveries'], name='time')

    cases_T = in_cases_df.T
    deaths_T = in_deaths_df.T
    recoveries_T = in_recoveries_df.T
    # Join dataframes
    temp_df = cases_T.join([deaths_T, recoveries_T])
    # Melt dataframe into one that can be directly used for plotting -
    final_df = pd.melt(temp_df.reset_index(), id_vars='index', var_name='category', value_name='value')
    final_df['index'] = final_df['index'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
    # df to csv should be in main
    #final_df.to_csv(f'./datasets/timeseries_records/cases_deaths_recoveries_timeseries.csv', sep=',', encoding='utf-8', index=False)
    return final_df

def get_jhu_stats(covid_daily_reports_path):
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
    return {"in_stats":{'cases': in_confirmed, 'deaths': in_deaths, 'recovered': in_recovered}, "w_stats":{'cases': w_confirmed, 'deaths': w_deaths, 'recovered': w_recovered}}

