# Dataset

## timeseries_records :file_folder:
- Contains time series data extracted from [JHU-CSSE COVID-19 Repository](https://github.com/CSSEGISandData/COVID-19)
- The data is transformed such that it is easy to plot them as categorical plots simultaneously using pandas, seaborn or matplotlib.
- Columns in the dataset - `index`,	`category`, `value` where `index` is the *timestamp*, `category` is *cases*, *deaths*, *recoveries* and `value` is the corresponding value of the category at the given timestamp.
- New rows are added whenever the JHU data updates.

## statewise_distribution :file_folder:
- Contians the statewise statistics in a convinient csv format extracted from Ministry of Health & Family Welfare - [MOHFW](https://www.mohfw.gov.in/)
- Files are named datewise so that you can easily call convinience functions written in [pandas](https://pandas.pydata.org/) or [R](https://www.r-project.org/) for your analysis.
- I have also added **Latitude** and **Longitude** columns for your GIS plotting needs.

## Convinience Scripts
- [ ] Add some sample convinience scripts