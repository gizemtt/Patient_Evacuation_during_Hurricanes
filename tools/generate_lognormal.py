from scipy.stats import norm
import numpy as np
import math
from tools.get_surge_height import getSurge
import pandas as pd

# find avg, var for lognormal distribution
def inv_lognormal(set1, set2):
    # find z score
    z1 = norm.ppf(set1[1])
    z2 = norm.ppf(set2[1])
    # Normal transform
    x1 = math.log(set1[0])
    x2 = math.log(set2[0])
    rho = z2 / z1
    sigma = (x1 - x2) / (z1 - z2)
    mu = (rho * x1 - x2) / (rho - 1)
    # Calculate mean and variance for log-normal
    avg = math.exp(mu + sigma ** 2 / 2)
    var = (math.exp(sigma ** 2) - 1) * (math.exp(2 * mu + sigma ** 2))
    parameters = [mu, sigma]
    return parameters

# geenerate a random number with mu and sigma
def simulate_surge(mu, sigma):
    rand = np.random.normal(mu, sigma)
    rand_surge = math.exp(rand)
    return rand_surge


def calculate_distribution(_location):
    df = getSurge(_location)
    df = df.sort_values(by=['code'])
    df = df.drop(columns=['probability_gt00'])
    df = df.reset_index(drop=True)
    dict_params = {}
    for i in df.code:
        print(i)
        sub_df = df.loc[df.code == i]
        sub_df = sub_df.dropna(axis=1)
        list_mu = []
        list_sigma = []
        if len(sub_df.columns) <= 2:
            continue
        else:
            for j in range(len(sub_df.columns) - 2):
                col1 = j + 1
                col1_name = sub_df.columns[col1]
                col1_name_length = len(col1_name)
                surge_height = int(col1_name[col1_name_length - 2:col1_name_length])
                probability = 1 - sub_df[col1_name][sub_df.code == i].values[0]
                _set1 = [surge_height, probability]
                for k in range(len(sub_df.columns) - 1 - col1):
                    col2 = col1 + k + 1
                    col2_name = sub_df.columns[col2]
                    col2_name_length = len(col2_name)
                    surge_height = int(col2_name[col2_name_length - 2:col2_name_length])
                    probability = 1 - sub_df[col2_name][sub_df.code == i].values[0]
                    _set2 = [surge_height, probability]
                    if _set1[1] == _set2[1]:
                        continue
                    else:
                        param = inv_lognormal(_set1, _set2)
                        list_mu.append(param[0])
                        list_sigma.append(param[1])
        try:
            avg_mu = round(sum(list_mu) / len(list_mu), 5)
            avg_sigma = round(sum(np.multiply(list_sigma, list_sigma)) * ((1 / len(list_sigma)) ** 2), 5)
            dict_params[i] = {'mu': avg_mu, 'sigma': avg_sigma}
        except ZeroDivisionError:
            continue
    df_params = pd.DataFrame.from_dict(dict_params, orient='index', columns=['mu', 'sigma'])
    df_params['code'] = df_params.index
    df_params = df_params.reset_index(drop=True)
    cols = df_params.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_params = df_params[cols]
    if _location == 'mac':
        output_location = '/Users/kyoung/Box Sync/github/pelo/input/data/slosh/psurge/'
    else:
        output_location = '/work/06447/kykim/pelo/input/data/slosh/psurge/'
    output_file = 'surge_distribution.csv'
    output_path = output_location + output_file
    df_params.to_csv(output_path)
