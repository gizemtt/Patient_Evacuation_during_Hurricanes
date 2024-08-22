import pandas as pd
import gmplot
import os


def read_result(df_list, paths):
    path_output = paths[1]
    # path_output = '/Users/kyoung/Box Sync/github/run/05012020_new_20_Tune0/output/'
    path_output = '/Users/kyoung/Box Sync/github/run/061520_single_full_A/output/'
    path_location_data = '/Users/kyoung/Box Sync/github/run/061520_single_full_A/input/'
    files = ['df_staging.csv', 'df_sender.csv', 'df_receiver.csv']

    path_map = path_output + 'map/'
    try:
        os.mkdir(path_map)
        print("directory created")
    except FileExistsError:
        print("directory exists")

    # create gps coordinate dictionary
    dict_location = {}
    for file in files:
        df_location = pd.read_csv(path_location_data + file)
        temp_dict = {key: [v1, v2] for key, v1, v2 in zip(df_location.code, df_location.latitude, df_location.longitude)}
        dict_location.update(temp_dict)

    # df_list = ['x_ij', 'x_jk', 'x_jkjk', 'x_ki']
    df_list = ['x_ij', 'x_jk', 'x_ki']

    # get scenario list
    ij_columns = ['staging', 'sender', 'vehicle', 'patient', 'scenario', 'number']
    jk_columns = ['sender', 'receiver', 'vehicle', 'patient', 'scenario', 'number']
    ki_columns = ['receiver', 'staging', 'vehicle', 'scenario', 'number']
    df_ij0 = pd.read_csv(path_output + 'result_x_ijs.csv', header=None, names=ij_columns)
    df_jk0 = pd.read_csv(path_output + 'result_x_jks.csv', header=None, names=jk_columns)
    # df_jkjk0 = pd.read_csv(path_output + 'x_jkjk.csv')
    df_ki0 = pd.read_csv(path_output + 'result_x_kis.csv', header=None, names=ki_columns)

    print(df_ij0)

    scenario_list = df_ij0.scenario.unique().tolist()

    # define color codes
    location_col = {'staging': 'blue',
                    'sender': 'red',
                    'receiver': 'green'}

    trip_col = {'x_ij': 'blue',
                'x_jk': 'red',
                'x_jkjk': 'orange',
                'x_ki': 'green'}

    for s in scenario_list:
        df_ij = df_ij0[df_ij0['scenario'] == s]
        df_jk = df_jk0[df_jk0['scenario'] == s]
        #  df_jkjk = df_jkjk0[df_jkjk0['scenario'] == s]
        df_ki = df_ki0[df_ki0['scenario'] == s]

        gmap = gmplot.GoogleMapPlotter(30, -95, zoom=8)
        gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'

        # plot location points
        # staging, sender from x_ij
        col = ['staging', 'sender']
        for loc in col:
            location_list = df_ij[loc].unique().tolist()
            print(s, location_list)

            lat_list = []
            lon_list = []
            for i in location_list:
                lat_list.append(dict_location[i][0])
                lon_list.append(dict_location[i][1])

            gmap.scatter(lat_list, lon_list, color=location_col[loc], marker=False, size=3000, alpha=0.7)

        # receiver from x_jk, x_jkjk
        receiver_df_list = df_jk['receiver'].unique().tolist()
        # receiver1_df_list = df_jkjk['receiver1'].unique().tolist()
        # receiver2_df_list = df_jkjk['receiver2'].unique().tolist()
        # receiver_list = list(set(receiver_df_list) | set(receiver1_df_list) | set(receiver2_df_list))
        receiver_list = list(set(receiver_df_list))
        lat_list = []
        lon_list = []
        for i in receiver_list:
            lat_list.append(dict_location[i][0])
            lon_list.append(dict_location[i][1])

        gmap.scatter(lat_list, lon_list, color=location_col['receiver'], marker=False, size=3000, alpha=0.7)

        '''
        # plot routing vectors
        # x_ij
        df = df_ij
        for i in range(len(df)):
            departure = df.iloc[i]['staging']
            destination = df.iloc[i]['sender']
            route = [departure, destination]

            lat_list = []
            lon_list = []
            for loc in route:
                lat_list.append(dict_location[loc][0])
                lon_list.append(dict_location[loc][1])

            gmap.plot(lat_list, lon_list, color=trip_col['x_ij'], edge_width=2)

        # x_jk
        df = df_jk
        for i in range(len(df)):
            departure = df.iloc[i]['sender']
            destination = df.iloc[i]['receiver']
            route = [departure, destination]

            lat_list = []
            lon_list = []
            for loc in route:
                lat_list.append(dict_location[loc][0])
                lon_list.append(dict_location[loc][1])

            gmap.plot(lat_list, lon_list, color=trip_col['x_jk'], edge_width=2)

        # x_jkjk
        df = df_jkjk
        for i in range(len(df)):
            location1 = df.iloc[i]['sender1']
            location2 = df.iloc[i]['receiver1']
            location3 = df.iloc[i]['sender2']
            location4 = df.iloc[i]['receiver2']
            route = [location1, location2, location3, location4]

            lat_list = []
            lon_list = []
            for loc in route:
                lat_list.append(dict_location[loc][0])
                lon_list.append(dict_location[loc][1])

            gmap.plot(lat_list, lon_list, color=trip_col['x_jkjk'], edge_width=2)

        # x_ki
        df = df_ki
        for i in range(len(df)):
            departure = df.iloc[i]['receiver']
            destination = df.iloc[i]['staging']
            route = [departure, destination]

            lat_list = []
            lon_list = []
            for loc in route:
                lat_list.append(dict_location[loc][0])
                lon_list.append(dict_location[loc][1])

            gmap.plot(lat_list, lon_list, color=trip_col['x_ki'], edge_width=2)
        '''

        file_name = 'map_%s.html' % (s)
        gmap.draw(path_map + file_name)
        print(s)


if __name__ == "__main__":
    read_result("", [0, 0])
