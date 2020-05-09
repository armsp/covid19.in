import glob
import pandas as pd

def add_clean_state_data(state_dataset_path):
    files = glob.glob(state_dataset_path+'/statewise_distribution/2020-*.csv')#../statewise_distribution/2020-*.csv'
    #latest_file = max(list_of_files, key=lambda x: x.split('/')[-1].split('.')[0].split('-')[1])
    sorted_files = sorted(files, key=lambda d: tuple(map(int, d.split('/')[-1].split('.')[0].split('-'))))
    latest_file = sorted_files[-7:]
    #sorted_files = ['2020-04-09.csv', '2020-04-10.csv']
    #state_set = set()
    df_list = []
    for f in latest_file:
        print(f)
        df = pd.read_csv(f)
        print(df.columns)
        df.iloc[:,1] = df.iloc[:,1].str.strip()
        #df.to_csv(f, index=False)
        df = df.sort_values('Name of State / UT')
        #df.iloc[:, 0] = df.index
        df.columns = ['sno.', 'place', 'case', 'recovery', 'death', 'lon', 'lat']
        #df.to_csv(f, index=False)
        #state_set |= set(df.iloc[:,1])

        #tt = df.drop('sno.', 1).set_index('place').T
        #tt['day'] = pd.to_datetime(f.split('.')[0])
        df['day'] = pd.to_datetime(f.split('/')[-1].split('.')[0])
        print(df.columns)
        df.to_csv(f"state_dataset_path/statewise_distribution/clean_daily_statewise_distribution/{f.split('/')[-1]}", index=False)
        df_list.append(df)

#add_clean_state_data()

#k = pd.concat(df_list)
#k.to_csv('doom.csv', index=True)

#z = pd.concat(df_list, ignore_index=True)
##z.to_csv('hello.csv', index=True)
#z.to_csv('world.csv', index=False)
#print(state_set)


#tt = df.drop('sno.', 1).set_index('place').T
#tt['day'] = pd.to_datetime(str(date.today()))

#temp = pd.DataFrame({'Assam': [1,2,3,4,5], 'Bihar': [6,7,8,9,10]})