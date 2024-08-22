import pandas as pd
import csv
from create_HTML import createHtml
import os

def writeHospitals(instance_paths):
    output_location = instance_paths[1]

    output_location_hospital_csv = output_location + 'hospitals/'
    output_location_hospital_html = output_location + 'html/'

    try:
        os.mkdir(output_location_hospital_csv)
        print("HOSPITAL CSV DIRECTORY CREATED")
    except FileExistsError:
        print("HOSPITAL CSV DIRECTORY EXISTS")
        print("")

    try:
        os.mkdir(output_location_hospital_html)
        print("HOSPITAL HTML DIRECTORY CREATED")
    except FileExistsError:
        print("HOSPITAL HTML DIRECTORY EXISTS")
        print("")

    # define dataframes
    df_ij = pd.read_csv(output_location + 'x_ij.csv')
    df_jk = pd.read_csv(output_location + 'x_jk.csv')
    # df_jkjk = pd.read_csv(output_location + 'x_jkjk.csv')

    # dict_df = {'x_ij': df_ij,
    #            'x_jk': df_jk,
    #            'x_jkjk': df_jkjk}

    dict_df = {'x_ij': df_ij,
               'x_jk': df_jk}

    # define hospital codees
    path_code = '/Users/kyoung/Box Sync/github/data/location/'
    file_names = ['df_staging.csv', 'df_sender.csv', 'df_receiver.csv']

    df_code = pd.DataFrame()
    for name in file_names:
        temp_df = pd.read_csv(path_code + name)
        df_code = df_code.append(temp_df)

    # get scenarios
    scenarios = df_ij['scenario'].unique().tolist()

    # get locations for each scenario
    for s in scenarios:

        # get staging areas
        this_df = dict_df['x_ij']
        df = this_df[this_df['scenario'] == s]
        index = 'staging'
        staging_list = df[index].unique().tolist()

        # get senders
        # dict_sender_columns = {'x_ij': ['sender'],
        #                        'x_jkjk': ['sender1', 'sender2']}

        dict_sender_columns = {'x_ij': ['sender']}

        sender_list = []
        for key in dict_sender_columns.keys():
            this_df = dict_df[key]
            df = this_df[this_df['scenario'] == s]

            for index in dict_sender_columns[key]:
                temp_list = df[index].unique().tolist()
                sender_list = list(set(sender_list) | set(temp_list))

        # get receivers
        dict_receiver_columns = {'x_jk': ['receiver'],
                                 'x_jkjk': ['receiver1', 'receiver2']}

        dict_receiver_columns = {'x_jk': ['receiver']}

        receiver_list = []
        for key in dict_receiver_columns.keys():
            this_df = dict_df[key]
            df = this_df[this_df['scenario'] == s]

            for index in dict_receiver_columns[key]:
                temp_list = df[index].unique().tolist()
                receiver_list = list(set(receiver_list) | set(temp_list))

        this_csv_file = s + '.csv'

        with open(output_location_hospital_csv + this_csv_file, 'w', newline='') as myfile:
            wr = csv.writer(myfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            # write staging area
            for i in staging_list:
                # wr.writerow(['staging', i])
                wr.writerow(['staging', df_code[df_code.code == i].name.tolist()[0].lower()])

            for j in sender_list:
                # wr.writerow(['sender', j])
                wr.writerow(['sender', df_code[df_code.code == j].name.tolist()[0].lower()])

            for k in receiver_list:
                # wr.writerow(['receiver', k])
                wr.writerow(['receiver', df_code[df_code.code == k].name.tolist()[0].lower()])

        createHtml(output_location_hospital_csv, output_location_hospital_html, s)
