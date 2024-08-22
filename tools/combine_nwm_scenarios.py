import pandas as pd
from tools.get_hospitals import getHospitals
from datetime import timedelta, date, datetime
# from get_hospitals import getHospitals

# -------------------------------------------------------------------------------------
# OUTPUT: A DATAFRAME WITH HOSPITAL INFORMATION AND DAILY MAX STAGE HEIGHT
# -------------------------------------------------------------------------------------
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def combine_nwm_output(_computer, _dict_parameter):

    # get information from input_param.csv
    new_location = int(_dict_parameter['new_location'])
    _start_date = _dict_parameter['start_date']
    _end_date = _dict_parameter['end_date']
    scale = int(_dict_parameter['scale'])
    num_senders = int(_dict_parameter['num_senders'])

    # create nwm_output dataframe with 5 NWM landfall locations
    if new_location:

        stage_output_path = '/Users/kyoung/Box Sync/github/data/nwm/stage_height/v6/'
        stage_output_file = 'stage_output_all.csv'
        df0 = pd.read_csv(stage_output_path + stage_output_file)
        df0 = df0[df0['CATEGORY'] == 'SENDER']
        cols = df0.columns.values
        cols[1] = 'id'
        df0.columns = cols

        # Get sender IDs
        path = '/Users/kyoung/Box Sync/github/data/location/'
        file = 'df_sender.csv'
        df_sender_id = pd.read_csv(path + file)
        dict_sender_id = dict(zip(df_sender_id['id'], df_sender_id['code']))
        df0['code'] = df0['id'].map(dict_sender_id)
        cols = list(df0.columns)
        new_cols = cols[:len(cols) - 26] + cols[-1:] + cols[len(cols) - 26: len(cols) - 1]
        df0 = df0[new_cols]
        df0.to_csv(stage_output_path + "nwm_output_combined.csv")

        # num_scenarios = 5
        # print("NWM Runs: ", num_scenarios)
        # if _computer == 'mac':
        #     file_location = '/Users/kyoung/Box Sync/github/data/nwm/stage_height/v2/'
        # else:
        #     file_location = '/work/06447/kykim/pelo/data/nwm/stage_height/'
        # list_file_name = []
        # file_prefix = '20170824-20170902.dailymax.ens_'
        # file_extension = '.csv'

        # for i in range(num_scenarios):
        #     scenario_num = str(num_scenarios) + '-' + str(i + 1)
        #     file_suffix = 'c' + scenario_num
        #     file_name = file_prefix + file_suffix + file_extension
        #     list_file_name.append([file_name, scenario_num])

        # # IMPORT FILES FROM THE FILE LIST
        # start_dt = datetime.strptime(_start_date, '%Y-%m-%d')
        # end_dt = datetime.strptime(_end_date, '%Y-%m-%d')

        # start_date = start_dt.strftime("%-d-%b")
        # end_date = end_dt.strftime("%-d-%b")

        # this_file = list_file_name[0][0]
        # df = pd.read_csv(file_location + this_file)
        # cols = df.columns.tolist()
        # index_start_date = cols.index(start_date)
        # index_end_date = cols.index(end_date)
        # df_default = df[cols[:index_start_date]]

        # list_hospitals = getHospitals(new_location, scale, num_senders)
        # df_sender = list_hospitals[1]
        # list_id = df_sender['objectid'].tolist()

        # for i in list_file_name:
        #     df = pd.read_csv(file_location + i[0])
        #     cols = df.columns.tolist()
        #     index_start_date = cols.index(start_date)
        #     index_end_date = cols.index(end_date)
        #     max_height = df[cols[index_start_date:index_end_date + 1]].max(axis=1)
        #     max_height = pd.to_numeric(max_height, errors='coerce')
        #     df_default[i[1]] = max_height

        # dict_code = {}
        # df0 = pd.DataFrame()
        # for j in list_id:
        #     dict_code[j] = df_sender[df_sender['objectid'] == j].code.values[0]
        #     df1 = df_default[df_default['OBJECTID_1'].isin([j])]
        #     df0 = df0.append(df1)

        # df0['code'] = df0['OBJECTID_1'].map(dict_code)

        # cols = df0.columns.tolist()
        # last_index = cols.index('Costline') + 1
        # num_scenarios = 5
        # cols = cols[:last_index] + cols[-1:] + cols[last_index: last_index + num_scenarios]
        # df0 = df0[cols]
        # df0.columns = df0.columns.str.lower()

    # create nwm_output dataframe with 5 NWM landfall locations
    else:
        num_scenarios = 25
        print("NWM Runs: ", num_scenarios)
        if _computer == 'mac':
            path = '/Users/kyoung/Box Sync/github/data/nwm/stage_height/v3/'
        else:
            path = '/work/06447/kykim/pelo/data/nwm/stage_height/'

        # get nwm_format file
        format_file = 'nwm_format.csv'
        df_format = pd.read_csv(path + format_file)
        cols_df_format = df_format.columns.tolist()

        # IMPORT FILES FROM THE FILE LIST
        start_dt = datetime.strptime(_start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(_end_date, '%Y-%m-%d')
        num_dates = int((end_dt - start_dt).days) + 1

        list_dates = []
        for single_date in daterange(start_dt, end_dt):
            list_dates.append(single_date.strftime("%-d-%b"))

        # get default sending hospital locations
        list_hospitals = getHospitals(new_location, scale, num_senders)
        df_sender = list_hospitals[1]
        list_id = df_sender['objectid'].tolist()

        # add column names to 25-# result
        df = df_format[cols_df_format]

        # read NWM outputs
        file_prefix = 'DailyMaxStage_hospitalv2_c25-'
        for i in range(num_scenarios):
            file_num_col = i + 1
            file_num = i + 1
            if file_num < 10:
                file_num = '0' + str(file_num)
            else:
                file_num = str(file_num)
            file = '%s%s' % (file_prefix, file_num)

            with open(path + file, 'r') as f:
                data = f.read().splitlines()

            data_formatted = []
            for line in data:
                line_str = line.split()
                if len(line_str) == num_dates:
                    line_num = [float(i) for i in line_str]
                    data_formatted.append(line_num)
                else:
                    line_num = []
                    for i in range(num_dates):
                        line_num.append("********")

                    data_formatted.append(line_num)

            df_data = pd.DataFrame(data_formatted)

            # find max stage height
            max_height = df_data.max(axis=1)
            max_height = pd.to_numeric(max_height, errors='coerce')

            # Add columns of max_height
            new_col_name = '%s-%s' % (num_scenarios, file_num_col)
            df = pd.concat((df, max_height.rename(new_col_name)), axis=1)

        # select only sending locations
        dict_code = {}
        df0 = pd.DataFrame()
        for j in list_id:
            dict_code[j] = df_sender[df_sender['objectid'] == j].code.values[0]
            df1 = df[df['OBJECTID_1'].isin([j])]
            df0 = df0.append(df1)

        df0['code'] = df0['OBJECTID_1'].map(dict_code)
        cols = df0.columns.tolist()
        last_index = cols.index('Costline') + 1
        cols = cols[:last_index] + cols[-1:] + cols[last_index: last_index + num_scenarios]
        df0 = df0[cols]
        df0.columns = df0.columns.str.lower()
        df0.to_csv(path + "nwm_output_combined.csv")

    return df0


if __name__ == "__main__":
    input_param_file = 'input_param.csv'
    path_input_file = '/Users/kyoung/Box Sync/github/pelo/input_param/'
    df_param = pd.read_csv(path_input_file + input_param_file)
    dict_input_param = dict(zip(df_param.parameter, df_param.value))
    df = combine_nwm_output('mac', dict_input_param)
