import pandas as pd
import numpy as np
import os

# outputs a list: [df_staging, df_sender, df_receiver]
# def getHospitals(new_location, scale, num_senders, reserve_proportion_hos, reserve_proportion_nh, evac_proportion, path_df_output):

def getHospitals(dict_path, dict_parameter, check_mean_scenario, shelter, num_senders, path_df_output):

    file_path = dict_path['data']
    scale = int(dict_parameter['scale'])

    df = pd.read_csv(file_path + '\\healthcare_facilities_cmoc.csv', index_col=0)
    df.columns = df.columns.str.lower()

    df_receiver = df[df.category == 'RECEIVER']
    df_other = df[df.category == 'OTHER']
    df_sender = df[df.category == 'SENDER']
    df_staging = df[df.category == 'STAGING']
    df_shelter = df[df.category == 'SHELTER']

    df_receiver = df_receiver.reset_index(drop=True)
    df_other = df_other.reset_index(drop=True)
    df_sender = df_sender.reset_index(drop=True)
    df_staging = df_staging.reset_index(drop=True)
    df_shelter = df_shelter.reset_index(drop=True)

#scale == 0, small data set
    if scale == 0:

        num_sender_hos = 5
        num_sender_nh = 5
        df_sender_hos = df_sender.loc[df_sender.type == 'HOSPITAL']
        df_sender_nh = df_sender.loc[df_sender.type == 'NH']
        df_sender_hos = df_sender_hos[0:int(num_sender_hos)]
        df_sender_nh = df_sender_nh[0:int(num_sender_nh)]
        list_sender_df = [df_sender_hos, df_sender_nh]
        df_sender = pd.concat(list_sender_df)

        num_receiver_hos = 10
        num_receiver_nh = 10
        df_receiver_hos = df_receiver.loc[df_receiver.type == 'HOSPITAL']
        df_receiver_nh = df_receiver.loc[df_receiver.type == 'NH']
        df_receiver_hos = df_receiver_hos[0:int(num_receiver_hos)]
        df_receiver_nh = df_receiver_nh[0:int(num_receiver_nh)]
        list_receiver_df = [df_receiver_hos, df_receiver_nh]
        df_receiver = pd.concat(list_receiver_df)

    else:
        if shelter == 0:
            if num_senders == 'all':
                pass

            else:
                df_sender_hos = df_sender.loc[df_sender.type == 'HOSPITAL']
                df_sender_nh = df_sender.loc[df_sender.type == 'NH']
                df_sender_nh = df_sender_nh[0:int(num_senders)]
                list_sender_df = [df_sender_hos, df_sender_nh]
                df_sender = pd.concat(list_sender_df)

                df_receiver_hos = df_receiver.loc[df_receiver.type == 'HOSPITAL']
                df_receiver_nh = df_receiver.loc[df_receiver.type == 'NH']
                df_receiver_nh = df_receiver_nh[0:int(250)]
                list_receiver_df = [df_receiver_hos, df_receiver_nh]
                df_receiver = pd.concat(list_receiver_df)
        else:
            if num_senders == 'all':
                df_receiver = pd.concat([df_receiver, df_shelter])
                df_receiver = df_receiver.reset_index(drop=True)

            else:
                df_sender_hos = df_sender.loc[df_sender.type == 'HOSPITAL']
                df_sender_nh = df_sender.loc[df_sender.type == 'NH']
                df_sender_nh = df_sender_nh[0:int(num_senders)]
                list_sender_df = [df_sender_hos, df_sender_nh]
                df_sender = pd.concat(list_sender_df)

                df_receiver_hos = df_receiver.loc[df_receiver.type == 'HOSPITAL']
                df_receiver_nh = df_receiver.loc[df_receiver.type == 'NH']
                df_receiver_sh = df_shelter
                df_receiver_nh = df_receiver_nh[0:int(250)]
                list_receiver_df = [df_receiver_hos, df_receiver_nh, df_receiver_sh]
                df_receiver = pd.concat(list_receiver_df)

    # print('POTENTIAL TOTAL SENDERS: %s, HOSPITALS: %s, NH: %s' % (len(df_sender), len(df_sender.loc[df_sender.type == 'HOSPITAL']), len(df_sender.loc[df_sender.type == 'NH'])))
    # print('TOTAL RECEIVERS: %s, HOSPITALS: %s, NH: %s' % (len(df_receiver), len(df_receiver.loc[df_receiver.type == 'HOSPITAL']), len(df_receiver.loc[df_receiver.type == 'NH'])))

    # print("TOTAL RECEIVERS: ", len(df_receiver), )

    list_df = [df_staging, df_sender, df_receiver]

    for i in list_df:
        this_df = i
        list_id = []

        this_category = this_df.category.unique()[0]
        # for this_category in this_df.category.unique():

        if this_category == 'STAGING':
            id_code = 'a'

            for i in range(len(this_df)):
                location_number = i + 1
                location_num = str(location_number)

                location_id = id_code + location_num
                list_id.append(location_id)

            this_df['code'] = list_id

        elif (this_category == 'RECEIVER') or (this_category == 'SHELTER'):
            location_number_rec = 0
            location_number_sh = 0

            for i in range(len(this_df)):
                if this_df.iloc[i]['category'] == 'RECEIVER':
                    id_code = 'r'
                    location_number_rec = location_number_rec + 1

                    if len(str(location_number_rec)) == 1:
                        location_number_rec_str = '00' + str(location_number_rec)
                    elif len(str(location_number_rec)) == 2:
                        location_number_rec_str = '0' + str(location_number_rec)
                    elif len(str(location_number_rec)) == 3:
                        location_number_rec_str = str(location_number_rec)

                    location_id = id_code + location_number_rec_str
                    list_id.append(location_id)

                elif this_df.iloc[i]['category'] == 'SHELTER':
                    id_code = 'q'
                    location_number_sh = location_number_sh + 1
                    location_number_sh_str = '00' + str(location_number_sh)
                    location_id = id_code + location_number_sh_str
                    list_id.append(location_id)

            this_df['code'] = list_id

        elif this_category == 'SENDER':
            id_code = 's'

            for i in range(len(this_df)):
                location_number = i + 1
                if len(str(location_number)) == 1:
                    location_num = '00' + str(location_number)

                elif len(str(location_number)) == 2:
                    location_num = '0' + str(location_number)

                elif len(str(location_number)) == 3:
                    location_num = str(location_number)

                location_id = id_code + location_num
                list_id.append(location_id)

            this_df['code'] = list_id

            # if this_category == 'RECEIVER':
            #     id_code = 'r'
            # else:
            #     id_code = 'h'

            # for i in range(len(this_df)):
            #     location_number = i + 1
            #     if len(str(location_number)) == 1:
            #         location_num = '00' + str(location_number)

            #     elif len(str(location_number)) == 2:
            #         location_num = '0' + str(location_number)

            #     elif len(str(location_number)) == 3:
            #         location_num = str(location_number)

            #     location_id = id_code + location_num
            #     list_id.append(location_id)

            # this_df['code'] = list_id

        elif this_category == 'SENDER':
            id_code = 's'

            for i in range(len(this_df)):
                location_number = i + 1
                if len(str(location_number)) == 1:
                    location_num = '00' + str(location_number)

                elif len(str(location_number)) == 2:
                    location_num = '0' + str(location_number)

                elif len(str(location_number)) == 3:
                    location_num = str(location_number)

                location_id = id_code + location_num
                list_id.append(location_id)

            this_df['code'] = list_id

        path_write = path_df_output
        file_name = 'df_' + this_category.lower() + '.csv'
        this_df.to_csv(os.path.join(path_write , file_name))

    # modification for finding EV solution
    if check_mean_scenario == 1:

        scenario_cols = ['25-1', '25-2', '25-3', '25-4', '25-5', '25-6', '25-7',
                         '25-8', '25-9', '25-10', '25-11', '25-12', '25-13', '25-14',
                         '25-15', '25-16', '25-17', '25-18', '25-19', '25-20', '25-21',
                         '25-22', '25-23', '25-24', '25-25']

        list_flood_levels = []
        for col in scenario_cols:
            list_flood_levels.append([i if i > 0 else 0 for i in df_sender[col] - df_sender['hand']])

        # get mean flood level
        mean_flood_level = []
        for i in range(len(df_sender['hand'])):
            mean_flood_level.append(sum([item[i] for item in list_flood_levels]) / len(list_flood_levels))

        df_sender['25-00'] = mean_flood_level
        file_name = 'df_sender.csv'
        df_sender.to_csv(os.path.join(path_df_output , file_name))

    output = [df_staging, df_sender, df_receiver]

    return output

# def main(getHospitals_output):

#     reserve_rate = 0.5

#     df = getHospitals_output[2]
#     print(df.columns)
#     table = pd.pivot_table(df, values=['name', 'beds'], index='county', aggfunc={'beds': np.sum, 'name': len})
#     print('RECEIVING HOSPITAL STATUS')
#     print(table)
#     print('     NUMBER OF COUNTIES: %s' % len(df['county'].unique()))
#     print('     NUMBER OF HOSPITALS: %s' % sum(table['name']))
#     print('     NUMBER OF TOTAL BEDS: %s' % sum(table['beds']))
#     print('     NUMBER OF AVAILABLE BEDS: %s' % str(sum(table['beds']) * reserve_rate))
#     print("")

#     df = getHospitals_output[1]
#     table = pd.pivot_table(df, values=['name', 'beds'], index='county', aggfunc={'beds': np.sum, 'name': len})
#     print('SENDING HOSPITAL STATUS')
#     print(table)
#     print('     NUMBER OF COUNTIES: %s' % len(df['county'].unique()))
#     print('     NUMBER OF HOSPITALS: %s' % sum(table['name']))
#     print('     NUMBER OF TOTAL BEDS: %s' % sum(table['beds']))
#     print('     NUMBER OF EVACUATION DEMAND: %s' % str(sum(table['beds']) * (1 - reserve_rate)))


if __name__ == "__main__":
    path_output = path_df_output+ '\\parameters'
    output = getHospitals(1, 0, 100, path_output)
    # main(output)
