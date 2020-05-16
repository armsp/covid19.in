import altair as alt
import pandas as pd
import geopandas as gpd
import glob

alt.renderers.set_embed_options(actions=False)

def make_chloropleth_json(clean_state_dataset_path):
    india = gpd.read_file('india_v2.json')
    files = glob.glob(clean_state_dataset_path+'/2020-*.csv')#../statewise_distribution/2020-*.csv'
    sorted_files = sorted(files, key=lambda d: tuple(map(int, d.split('/')[-1].split('.')[0].split('-'))))
    #print(sorted_files)
    latest_file = sorted_files[-1]
    print(latest_file)
    df = pd.read_csv(latest_file)
    df = df.drop(['sno.', 'lon', 'lat', 'day'], 1)
    df.rename(columns={'recovery': 'Recovery', 'death': 'Deaths'}, inplace=True)
    df['Active Cases'] = df['case'] - df['Recovery'] - df['Deaths']

    india = india.join(df.set_index('place'), on='state')

    # Mapping
    base = alt.Chart(india).mark_geoshape(fill='white', stroke='gray', strokeWidth=2).encode().properties(
            width='container',
            height=525,
        )

    choro = alt.Chart(india,width='container',height=525,).mark_geoshape(
            #fill='lightgray',
            fillOpacity=0.8,
            strokeWidth=1,
            stroke='gray',
        ).encode(
            color=alt.Color('Active Cases',
                    type='quantitative',
                    scale=alt.Scale(scheme='orangered',type='sqrt'),#sqrt band
                    #['linear', 'log', 'pow', 'sqrt', 'symlog', 'identity', 'sequential', 'time', 'utc', 'quantile', 'quantize', 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
                    title = "Active Cases",
                    bin=alt.BinParams(binned=False,maxbins=32,nice=True),
                    #legend=None
                    ),
            tooltip=[alt.Tooltip('state:N', title='State'),'Active Cases:Q', 'Deaths:Q', 'Recovery:Q'],
        )

    final_map = (base+choro).configure_view(
        strokeWidth=0
    )
    kwargs = {'actions': False}
    return final_map.to_json(indent=None, **kwargs)
# with open('charts.html', 'w') as f:
#     f.write(two_charts_template.format(
#         vega_version=alt.VEGA_VERSION,
#         vegalite_version=alt.VEGALITE_VERSION,
#         vegaembed_version=alt.VEGAEMBED_VERSION,
#         spec1=final_map.to_json(indent=None),
#         # spec2=final_map.to_json(indent=None),
#     ))