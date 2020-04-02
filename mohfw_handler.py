import json
import logging as lg
from urllib import request, parse
from datetime import date, datetime

import requests
import pandas as pd

log = lg.getLogger(__name__)

def mohfw_data_to_df():
    url = 'http://www.mohfw.gov.in/'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    req = requests.get(url, headers=header)
    if req.status_code == 200:
        table_list = pd.read_html(req.content)
        df = table_list[-1]
        return df
    else:
        log.error(f"Could not read MoHFW website. Request status code = {req.status_code}")
        return None

def extract_clean_df(df):
    clean_df = df.head(-1)
    return clean_df

def geocode(city, logger):
    url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    param_dict = {"f": "json", "singleLine": f"{city}, IND", "maxLocations": 1}
    params = parse.urlencode(param_dict).encode('UTF-8')
    req = request.Request(url, headers=header, data=params)

    try:
      response = request.urlopen(req)
    except Exception:
      log.error("Geocode request Failed", exc_info=True)
    else:
      log.debug("Response code = " + response.getcode())#some other code? handle it here
      log.info("Not adding Latitude and Longitude")
      return None

    if response.getcode() == 200:
      response_dict = json.load(response)
      return (response_dict['candidates'][0]["location"]["x"], response_dict['candidates'][0]["location"]["y"])

def add_lat_lon(df):
    temp_df = pd.DataFrame()
    temp_df = df
    try:
        temp_df['Lon'], temp_df['Lat'] = zip(*(df['Name of State / UT'].map(geocode)))
    except Exception:
        log.error("adding lat & lon failed", exc_info=True)
    else:
        return temp_df

#TODO
# Melting data -> should happen in the main file

def get_mohfw_stats(df):
    cases_sum = df.iloc[:,2].sum()
    deaths_sum = df.iloc[:,4].sum()
    recovered_sum = df.iloc[:,3].sum()
    #return (cases_sum, deaths_sum, recovered_sum)
    return {"in_stats":{'cases': cases_sum, 'deaths': deaths_sum, 'recovered': recovered_sum}}
