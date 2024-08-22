import pandas as pd
import numpy as np

# outputs a list: [df_staging, df_sender, df_receiver]
def getHospitals(new_location, scale, num_senders):

    reserve_proportion_hos = 0.5
    reserve_proportion_nh = 0.2
    evac_proportion = 1

    if new_location:
        file = 'healthcare_facilities_cmoc.csv'
    else:
        file = 'Hospitals_setrac.csv'

    file_path = '/Users/kyoung/Box Sync/github/data/gov/'
    # file_path = '/Users/kyoung/Box Sync/github/data/pelo_input_data/'
    df = pd.read_csv(file_path + file)
    df.columns = df.columns.str.lower()

    df_receiver = df[df.category == 'RECEIVER']
    df_other = df[df.category == 'OTHER']
    df_sender = df[df.category == 'SENDER']
    df_staging = df[df.category == 'STAGING']

    df_receiver = df_receiver.reset_index(drop=True)
    df_other = df_other.reset_index(drop=True)
    df_sender = df_sender.reset_index(drop=True)
    df_staging = df_staging.reset_index(drop=True)

    if scale == 0:
        df_sender = df_sender[0:num_senders]

    print('TOTAL SENDERS: ', len(df_sender))

    list_df = [df_staging, df_sender, df_receiver]

    for i in list_df:
        this_df = i
        list_id = []
        list_target = []

        if this_df.category.unique()[0] == 'STAGING':
            id_code = 'a'
        elif this_df.category.unique()[0] == 'RECEIVER':
            id_code = 'r'
            rate = reserve_proportion
        elif this_df.category.unique()[0] == 'SENDER':
            id_code = 's'
            rate = evac_proportion

        if id_code == 'r':
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

                this_category = this_df.category.unique()[0]
                if this_category == 'STAGING':
                    pass
                else:
                    target = int(this_df.iloc[i].beds * rate)
                    list_target.append(target)

        elif id_code == 's':
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

                this_category = this_df.category.unique()[0]
                if this_category == 'STAGING':
                    pass
                else:
                    target = int(this_df.iloc[i].beds * rate)
                    list_target.append(target)

        elif id_code == 'a':
            for i in range(len(this_df)):
                location_number = i + 1
                location_num = str(location_number)

                location_id = id_code + location_num
                list_id.append(location_id)

                this_category = this_df.category.unique()[0]
                if this_category == 'STAGING':
                    pass
                else:
                    target = int(this_df.iloc[i].beds * rate)
                    list_target.append(target)

        this_df['code'] = list_id

        if this_category == 'RECEIVER':
            this_df['capacity'] = list_target
        elif this_category == 'SENDER':
            this_df['demand'] = list_target

        path_write = '/Users/kyoung/Box Sync/github/data/location/'
        file_name = 'df_' + this_category.lower() + '.csv'
        this_df.to_csv(path_write + file_name)

    output = [df_staging, df_sender, df_receiver]

    return output

def main(getHospitals_output):

    reserve_rate = 0.5

    df = getHospitals_output[2]
    print(df.columns)
    table = pd.pivot_table(df, values=['name', 'beds'], index='county', aggfunc={'beds': np.sum, 'name': len})
    print('RECEIVING HOSPITAL STATUS')
    print(table)
    print('     NUMBER OF COUNTIES: %s' % len(df['county'].unique()))
    print('     NUMBER OF HOSPITALS: %s' % sum(table['name']))
    print('     NUMBER OF TOTAL BEDS: %s' % sum(table['beds']))
    print('     NUMBER OF AVAILABLE BEDS: %s' % str(sum(table['beds']) * reserve_rate))
    print("")

    df = getHospitals_output[1]
    table = pd.pivot_table(df, values=['name', 'beds'], index='county', aggfunc={'beds': np.sum, 'name': len})
    print('SENDING HOSPITAL STATUS')
    print(table)
    print('     NUMBER OF COUNTIES: %s' % len(df['county'].unique()))
    print('     NUMBER OF HOSPITALS: %s' % sum(table['name']))
    print('     NUMBER OF TOTAL BEDS: %s' % sum(table['beds']))
    print('     NUMBER OF EVACUATION DEMAND: %s' % str(sum(table['beds']) * (1 - reserve_rate)))


if __name__ == "__main__":
    output = getHospitals(1, 1, 1)
    main(output)
