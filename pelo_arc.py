import pandas as pd
import re
import time
import itertools

import os
import sys
import inspect

from generate_parameter import paramGen
from generate_scenario import scenarioGen

# Call functions from parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = "%s\\tools" % (currentdir)
paramdir = '%s\\input_param' % (currentdir)
datadir = '%s\\data' % (currentdir)
trackdir = '%s\\track_simulation\\output' % (currentdir)

parentdir = os.path.dirname(currentdir)
rundir = '%s\\pelo_run' % (parentdir)
sloshdir = '%s\\slosh' % (parentdir)

sys.path.insert(0, parentdir)
sys.path.insert(0, currentdir)
sys.path.insert(0, tooldir)

sys.path.insert(0,'/Users/toplu/anaconda3/Lib/site-packages') 
                # '/Users/kyoung/opt/anaconda3/lib/python3.7/site-packages'

# from csv_write import writeResult
import gurobipy as gp
from gurobipy import GRB

# ----------------------------
# DEFINE INPUTS TO THE MODEL
# ----------------------------

# INITIALIZE MODEL
path_input_param = paramdir
dict_path = {'data': datadir,
             'slosh': sloshdir,
             'track': trackdir}

# INPUT TUNING PARAMETER AND MODEL PARAMETER
constraint_parameter = ['param_constraint_paper.csv']
model_parameter = ['param_model_paper.csv']

df_constraint_param = pd.read_csv(path_input_param +"\\param_constraint_paper.csv")
#df_constraint_param = pd.read_csv(os.path.join(path_input_param,constraint_parameter[0]))
df_model_param = pd.read_csv(path_input_param + '\\param_model_paper.csv')
df_param = pd.concat([df_constraint_param, df_model_param])
dict_parameter = dict(zip(df_param.parameter, df_param.value))

# INPUT TUNING PARAMETER
input_tuning_param = 'param_tuning_paper.csv'
df_tune = pd.read_csv(path_input_param + '\\param_tuning_paper.csv')
dict_tuning_param = dict(zip(df_tune['parameter'], df_tune['value']))

# ----------------------
# MULTIPLE RUN PARAMETERS
# ----------------------
# list_num_sender = [50, 100, 'all']
# list_unique_demand = [0, 1, 2]
# list_ambusCap_min = [20]

# list_unique_demand = [1]
# list_ambusCap_min = [20]

# # Analysis 7
# list_unique_demand = [1, 2]
# list_num_sender = [100, 'all']
# list_gamma = [1]


# Solve for n12 / different demand profiles
# num_scenarios = 1
# dict_parameter['check_mean_path'] = 1
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [1]
# list_num_sender = ['all']
# # list_gamma = [1]
# list_occupancy_sender = [1]


# # # Analysis 4 VSS / EVPI
# num_scenarios = 25
# # get_EV = 1
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [1]
# list_num_sender = ['all']
# list_occupancy_sender = [0.8]
# list_gamma = [1]

# Analysis 0: Expected Value solution
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [1]
# list_num_sender = ['all']
# list_ambusMix = [0]
# dict_parameter['check_EV'] = 1


# Analysis 11: Routing strategy
vss = int(dict_parameter['vss'])
evpi = int(dict_parameter['evpi'])
list_unique_demand = [2]
list_num_sender = ['all']
list_ambusMax = [16]


# Analysis 22: More Ambus
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [2]
# list_num_sender = ['all']
# # num_sender = 'all'
# # list_speed_type = [1]
# list_ambusMax = [16]


# Analysis 33: Demand
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [1, 2]
# list_occupancy_sender = [1.1, 1, 0.9, 0.8]   # [1.1, 1, 0.9, 0.8]
# list_num_sender = ['all']

# # Analysis 44: utilization
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [1, 2]
# list_occupancy_receiver = [1, 0.95, 0.9]
# list_nums_sender = ['all']


# ## default
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_unique_demand = [2]
# # list_occupancy_sender = [1.1, 1, 0.9, 0.8]   # [1.1, 1, 0.9, 0.8]
# # # list_worst_case_demand = [0]
# # # occupancy_receiver = 'base'
# list_nums_sender = ['all']


# # Analysis 3: Flood threshold
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_threshold = [12, 24, 36, 48]
# list_unique_demand = [1, 2]
# list_num_sender = ['all']


# # fixed cost
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_fixed_cost = [2000000, 3000000]
# list_unique_demand = [1, 2]
# list_num_sender = ['all']


# Analysis 6: Occupancy rate
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_gamma = [0.90, 0.95, 1.0]
# list_unique_demand = [2]
# list_num_sender = ['all']

# # Analysis 7: Shelter decision
# vss = int(dict_parameter['vss'])
# evpi = int(dict_parameter['evpi'])
# list_gamma = [0.85]  # [1, 0.95, 0.9]
# list_unique_demand = [1, 2]  # [1, 2]
# list_num_sender = ['all']   # ['all', '100']


for unique_demand in list_unique_demand:

    for num_sender in list_num_sender:

        dict_objective_solutions = {}

        for ambusMax in list_ambusMax:

            # ------------------------
            # INITIALIZE MODEL
            # ------------------------

            # Update parameter dictionary
            # 1. Parameters to iterate
            dict_parameter['unique_demand'] = unique_demand
            # dict_parameter['fixed_cost'] = fixed_cost
            dict_parameter['num_senders'] = num_sender

            # if occupancy_sender != 1.1:
            #     dict_parameter['hos_cr_occupancy_rate'] = occupancy_sender
            #     dict_parameter['hos_nc_occupancy_rate'] = occupancy_sender
            #     dict_parameter['nh_occupancy_rate'] = occupancy_sender
            #     worst_case_demand = 0
            # else:
            #     worst_case_demand = 1

            # dict_parameter['worst_case'] = worst_case_demand

            # if occupancy_receiver == 'base':
            #     pass
            # else:
            #     dict_parameter['hos_cr_occupancy_rate_receiver'] = 0.5
            #     dict_parameter['hos_nc_occupancy_rate_receiver'] = 0.5
            #     dict_parameter['nh_occupancy_rate_receiver'] = 0.5

            speed_type = 1
            if speed_type == 0:
                dict_parameter['avg_mph_ambul'] = 45
                dict_parameter['avg_mph_ambus'] = 30
            else:
                dict_parameter['avg_mph_ambul'] = 30
                dict_parameter['avg_mph_ambus'] = 20

            # Check if finding a solution for mean path (VSS)
            # if dict_parameter['check_mean_path'] == 1:
            #     current_scenario = 12
            # else:
            #     current_scenario = this_scenario + 1
            # dict_parameter['current_scenario'] = current_scenario

            print(dict_parameter)

            dict_parameter['current_scenario'] = 0
            # 2. Fixed parameters
            if (evpi == 1) or (vss == 1):
                output_suffix = '%s_%s' % (dict_parameter['suffix'], current_scenario)
            else:
                output_suffix = '%s_DEFAULT%s' % (dict_parameter['suffix'], ambusMax)

            # Names used for directory creation
            staging_iteration = int(dict_parameter['staging_iteration'])
            trip = dict_parameter['trip']
            cr_by_ambus = int(dict_parameter['cr_by_ambus'])
            num_sender = dict_parameter['num_senders']
            ambusCap_min = int(dict_parameter['ambusCapacity_min'])
            shelter = int(dict_parameter['shelter'])
            gamma = dict_parameter['gamma']

            instance_suffix = ('%s_Iter[%s]_Trip[%s]_Opt[%s]_AmbusCR[%s]_Sender[%s]_AmbusMin[%s]_shelter[%s]_g[%s]') % (output_suffix, staging_iteration, trip, unique_demand, cr_by_ambus, num_sender, ambusCap_min, shelter, gamma)
            suffix = instance_suffix
            path_run = rundir
            path_instance = os.path.join(path_run , suffix)
            path_instance_output = path_instance + '\\output\\'
            path_instance_input = path_instance + '\\input\\'
            instance_paths = [path_instance_input, path_instance_output]

            try:
                os.mkdir(path_run)
                
                os.mkdir(path_run+'\\pelo_tests')
                os.mkdir(path_run+'\\pelo_tests\\set_VSS')
                
                os.mkdir(path_instance)
                os.mkdir(path_instance_output)
                os.mkdir(path_instance_input)
                #os.mkdir(path_instance__input+ '\\parameters')
               
                print("DIRECTORIES CREATED")
                print("")
            except FileExistsError:
                print("DIRECTORIES EXIST")
                print("")

            # ------------------------
            # BUILD MODEL
            # ------------------------
            path_instance_input = instance_paths[0]
            path_instance_output = instance_paths[1]
            print(path_instance_input)
            print(path_instance_output)

            print("-------------------------------- ")
            print("START GENERATING SCENARIOS")
            print("")
            time_scenario_gen_start = time.time()
            scenarioGen(dict_path, dict_parameter, instance_paths)
            time_scenario_gen_end = time.time()
            time_scen_generation = time_scenario_gen_end - time_scenario_gen_start

            print("")
            print("SCENARIOS GENERATED")
            print("-------------------------------- ")
            print("")

            print("-------------------------------- ")
            print("START GENERATING PARAMETERS")
            print("")

            time_param_gen_start = time.time()
            print(dict_parameter)
            paramGen(dict_path, dict_parameter, path_instance_input)
            time_param_gen_end = time.time()
            time_param_generation = time_param_gen_end - time_param_gen_start

            print("")
            print("PARAMETERS GENERATED")
            print("-------------------------------- ")
            print("")

            print("SCENARIO GENERATION TIME: %s" % (time_scen_generation))
            print("PARAMETER GENERATION TIME: %s" % (time_param_generation))

            # Sets
            input_stagingArea = 'input_stagingArea.tab'
            input_sender = 'input_sender.tab'
            input_receiver = 'input_receiver.tab'
            input_scenario = 'input_scenario.tab'
            input_vehicle = 'input_vehicle.tab'
            input_patient = 'input_patient.tab'

            # Zero index parameters
            input_bigM = 'input_bigM.tab'
            input_minVehicle = 'input_minVehicle.tab'
            input_ambusMax = 'input_ambusMax.tab'

            # Single index parameters
            input_probability = 'input_probability.tab'
            input_openingCost = 'input_openingCost.tab'
            input_openingCost_shelter = 'input_openingCost_shelter.tab'
            input_vehicleCost = 'input_c_v.tab'
            input_vehicleCapacity = 'input_ambulanceCapacity.tab'

            # Multi index parameters
            input_c_ijv = 'input_c_ijv.csv'
            input_c_jkv = 'input_c_jkv.csv'
            input_c_kiv = 'input_c_kiv.csv'
            input_c_jkjkv = 'input_c_jkjkv.csv'
            if dict_parameter['check_EV'] == 1:
                input_demand_vs = 'input_mean_demand.csv'
            else:
                input_demand_vs = 'input_demand_vs.csv'

            input_receiverCapacity = 'input_receiverCapacity.csv' #it was as follows: 'input_receiverCapacity_v2.csv'
            input_receiverBedcount = 'input_receiverBedcount.tab'

            # Set
            input_set_list = [input_stagingArea, input_sender, input_receiver, input_vehicle, input_patient, input_scenario]
            set_list = []

            for i in input_set_list:
                df = pd.read_csv(os.path.join(path_instance_input , i))
                set_list.append(list(df[df.columns.values[0]].values))

            stagingArea = set_list[0]
            sender = set_list[1]
            receiver = set_list[2]
            vehicle = set_list[3]
            patient = set_list[4]
            scenario = set_list[5]

            # get receivers by type
            df = pd.read_csv(path_instance_input + 'df_receiver.csv')
            receiver_hos = list(df.loc[df['type'] == 'HOSPITAL']['code'])
            receiver_nh = list(df.loc[df['type'] == 'NH']['code'])

            # DEFINE HOSPITAL / NURSING HOME SETS
            path = dict_path['data']
            df_location_type = pd.read_csv(path + '\\healthcare_facilities_cmoc.csv', index_col=0)
            dict_location_type = dict(zip(df_location_type['NID'], df_location_type['TYPE']))

            df_sender_type = pd.read_csv(path_instance_input + 'df_sender.csv', index_col=0)
            dict_sender_type = dict(zip(df_sender_type['code'], df_sender_type['nid']))
            df_receiver_type = pd.read_csv(path_instance_input + 'df_receiver.csv', index_col=0)
            dict_receiver_type = dict(zip(df_receiver_type['code'], df_receiver_type['nid']))

            receiver_hos = []
            receiver_nh = []
            receiver_sh = []
            for k in receiver:
                if dict_location_type[dict_receiver_type[k]] == 'HOSPITAL':
                    receiver_hos.append(k)
                elif dict_location_type[dict_receiver_type[k]] == 'NH':
                    receiver_nh.append(k)
                elif dict_location_type[dict_receiver_type[k]] == 'SLT':
                    receiver_sh.append(k)
                else:
                    print("ERROR RECEIVER KIND %s" % (k))

            sender_hos = []
            sender_nh = []
            for j in sender:
                if dict_location_type[dict_sender_type[j]] == 'HOSPITAL':
                    sender_hos.append(j)
                elif dict_location_type[dict_sender_type[j]] == 'NH':
                    sender_nh.append(j)
                else:
                    print("ERROR SENDER KIND %s" % (j))

            # Parameter: Zero index parameters
            input_param_list = [input_bigM, input_minVehicle, input_ambusMax]
            param_list = []

            for i in input_param_list:
                df = pd.read_csv(os.path.join(path_instance_input , i), header=None)
                param_list.append(df[0][0])

            bigM = param_list[0]
            minVehicle = param_list[1]
            ambusMax = param_list[2]

            # Parameter: Single Index Parameter
            input_param_list = [input_probability, input_openingCost, input_vehicleCost, input_vehicleCapacity, input_openingCost_shelter, input_receiverBedcount]
            param_list = []

            for i in input_param_list:
                df = pd.read_csv(os.path.join(path_instance_input , i), delimiter='\t')
                cols = list(df.columns)
                dict_param = dict(zip(df[cols[0]], df[cols[1]]))
                param_list.append(dict_param)

            probability = param_list[0]
            openingCost = param_list[1]
            vehicleCost = param_list[2]
            vehicleCapacity = param_list[3]
            openingCost_shelter = param_list[4]
            receiverBedcount = param_list[5]
            bedProportion_hos = {'c': float(dict_parameter['icu_bed_rate']),
                                 'n': 1 - float(dict_parameter['icu_bed_rate'])}
            bedProportion_nh = {'c': 0, 'n': 1}

            occupancyRate_hos = {'n': float(dict_parameter['hos_nc_occupancy_rate']),
                                 'c': float(dict_parameter['hos_cr_occupancy_rate'])}
            occupancyRate_nh = {'n': float(dict_parameter['nh_occupancy_rate']), 'c': 0}

            # Parameters: Multi-Indexed parameters
            if trip == 'single':
                input_param_list = [input_c_ijv, input_c_jkv, input_c_kiv, input_demand_vs, input_receiverCapacity]
            elif trip == 'double':
                input_param_list = [input_c_ijv, input_c_jkv, input_c_kiv, input_demand_vs, input_receiverCapacity, input_c_jkjkv]
            param_list = []

            for i in input_param_list:
                print(i)
                df = pd.read_csv(os.path.join(path_instance_input , i))
                index_cols = list(df.columns)[:-1]
                index_col_name = 'key'
                value_col = df.columns[-1]
                df[index_col_name] = list(zip(*[df[c] for c in index_cols]))
                dict_param = dict(zip(df[index_col_name], df[value_col]))
                param_list.append(dict_param)

            c_ij = param_list[0]
            c_ki = param_list[2]
            demand_update = param_list[3]
            receiverCapacity = param_list[4]
            # receiverBedcount = param_list[5]

            c_jk_update = param_list[1]
            default_arc_cost = 1000000
            cost_keys = list(itertools.product(sender, receiver, vehicle))
            c_jk = dict.fromkeys(cost_keys, default_arc_cost)
            c_jk.update(c_jk_update)

            if trip == 'double':
                # Set default c_jkjk as very large value
                c_jkjk_update = param_list[5]
                cost_keys = list(itertools.product(sender, receiver, sender, receiver, vehicle))
                c_jkjk = dict.fromkeys(cost_keys, default_arc_cost)
                c_jkjk.update(c_jkjk_update)

            # Set default demand as 0
            default_demand = 0
            demand_keys = list(itertools.product(sender, patient, scenario))
            demand = dict.fromkeys(demand_keys, default_demand)
            demand.update(demand_update)

            # CREATE A MODEL AND DECLARE VARIABLES
            time_model_gen_start = time.time()

            m = gp.Model('arcRouting')
            x_ij = m.addVars(list(itertools.product(stagingArea, sender, vehicle, patient, scenario)), vtype=GRB.INTEGER, name='x_ij')
            x_jk = m.addVars(list(itertools.product(sender, receiver, vehicle, patient, scenario)), vtype=GRB.INTEGER, name='x_jk')
            x_ki = m.addVars(list(itertools.product(receiver, stagingArea, vehicle, scenario)), vtype=GRB.INTEGER, name='x_ki')
            q = m.addVars(stagingArea, vehicle, vtype=GRB.INTEGER, name='q')

            # # linear x variables
            # x_ij = m.addVars(list(itertools.product(stagingArea, sender, vehicle, patient, scenario)), vtype=GRB.CONTINUOUS, name='x_ij')
            # x_jk = m.addVars(list(itertools.product(sender, receiver, vehicle, patient, scenario)), vtype=GRB.CONTINUOUS, name='x_jk')
            # x_ki = m.addVars(list(itertools.product(receiver, stagingArea, vehicle, scenario)), vtype=GRB.CONTINUOUS, name='x_ki')
            # q = m.addVars(stagingArea, vehicle, vtype=GRB.CONTINUOUS, name='q')

            z = m.addVars(stagingArea, vtype=GRB.BINARY, name='z')

            if shelter == 1:
                y = m.addVars(receiver_sh, vtype=GRB.BINARY, name='y')

            if trip == 'single':
                pass
            else:
                x_jkjk = m.addVars(list(itertools.product(sender, receiver, sender, receiver, vehicle, patient, scenario)), vtype=GRB.INTEGER, name='x_jkjk')

            print("GENERATED VARIABLES")

            # ADD CONSTRAINTS
            v_ambul = 'v00'
            p_cr = 'c'
            p_nc = 'n'

            # DEFINE SET INDICATOR DICTIONARY (possible sender to receiver)
            all_jk = list(itertools.product(sender, receiver))
            beta = dict.fromkeys(all_jk, 0) #assign all jk zero. Then in the following part, we will update beta!
            print("")
            print("INDICATOR SET TOTAL: ", len(beta))

            if unique_demand == 0:
                hh = list(itertools.product(sender_hos, receiver_hos))
                hn = list(itertools.product(sender_hos, receiver_nh))
                nn = list(itertools.product(sender_nh, receiver_nh))
                nh = list(itertools.product(sender_nh, receiver_hos))
                nsh = list(itertools.product(sender_nh, receiver_sh))
                allowed_arc = hh + hn + nn + nh + nsh
                beta_1 = dict.fromkeys(allowed_arc, 1)
                beta.update(beta_1)
                print("INDICATOR SET = 1: ", len(beta_1))

            elif unique_demand == 1:
                hh = list(itertools.product(sender_hos, receiver_hos))
                nn = list(itertools.product(sender_nh, receiver_nh))
                nsh = list(itertools.product(sender_nh, receiver_sh))
                allowed_arc = hh + nn + nsh
                beta_1 = dict.fromkeys(allowed_arc, 1)
                beta.update(beta_1)
                print("INDICATOR SET = 1: ", len(beta_1))

            elif unique_demand == 2:
                hh = list(itertools.product(sender_hos, receiver_hos))
                nn = list(itertools.product(sender_nh, receiver_nh))
                nh = list(itertools.product(sender_nh, receiver_hos))
                nsh = list(itertools.product(sender_nh, receiver_sh))
                allowed_arc = hh + nn + nh + nsh
                beta_1 = dict.fromkeys(allowed_arc, 1)
                beta.update(beta_1)
                print("INDICATOR SET = 1: ", len(beta_1))

            print("")

            if trip == 'single':

                if cr_by_ambus == 0:    # if 1, ambus may take critical patients
                    demand_critical = m.addConstrs(
                        (gp.quicksum(vehicleCapacity[v_ambul] * beta[(j, k)] * x_jk[j, k, v_ambul, p_cr, s] for k in receiver) == demand[j, p_cr, s] for j in sender for s in scenario), 'constr_demand_critical')

                    demand_noncritical = m.addConstrs(
                        (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p_nc, s] for k in receiver for v in vehicle) == demand[j, p_nc, s] for j in sender for s in scenario), 'constr_demand_noncritical')
                else:
                    demand_all = m.addConstrs(
                        (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for k in receiver for v in vehicle) == demand[j, p, s] for j in sender for p in patient for s in scenario), 'constr_demand_all')

                # capacity_nh = m.addConstrs(
                #     (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) <= receiverBedcount[k] * bedProportion_nh[p] * (gamma - occupancyRate_nh[p]) for k in receiver_nh for p in patient for s in scenario), 'constr_nh_capacity')

                # capacity_hos = m.addConstrs(
                #     (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) <= receiverBedcount[k] * bedProportion_hos[p] * (gamma - occupancyRate_hos[p]) for k in receiver_hos for p in patient for s in scenario), 'constr_hos_capacity')

                hospital_capacity = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) <= receiverCapacity[k, p] for k in receiver for p in patient for s in scenario), 'constr_hospital_capacity')

                # hospital_capacity_nh = m.addConstrs(
                #     (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) <= receiverCapacity[k, p] for k in receiver_nh for p in patient for s in scenario), 'constr_nh_capacity')

                # hospital_capacity_hos = m.addConstrs(
                #     (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) <= receiverCapacity[k, p] - receiverBedcount[k, p] * (1 - gamma) for k in receiver_hos for p in patient for s in scenario), 'constr_hospital_capacity')

                flowbalance_j = m.addConstrs(
                    (gp.quicksum(x_ij[i, j, v, p, s] for i in stagingArea) == gp.quicksum(beta[(j, k)] * x_jk[j, k, v, p, s] for k in receiver) for j in sender for v in vehicle for p in patient for s in scenario), 'constr_flowbalance_j')

                flowbalance_k = m.addConstrs(
                    (gp.quicksum(x_ki[k, i, v, s] for i in stagingArea) == gp.quicksum(beta[(j, k)] * x_jk[j, k, v, p, s] for j in sender for p in patient) for k in receiver for v in vehicle for s in scenario), 'constr_flowbalance_k')

            elif trip == 'double':
                demand_critical = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v_ambul] * x_jk[j, k, v_ambul, p_cr, s] for k in receiver) + gp.quicksum(vehicleCapacity[v_ambul] * x_jkjk[j, k, j_hat, k_hat, v_ambul, p_cr, s] for k in receiver for j_hat in sender for k_hat in receiver) + gp.quicksum(vehicleCapacity[v_ambul] * x_jkjk[j_hat, k_hat, j, k, v_ambul, p_cr, s] for k in receiver for j_hat in sender for k_hat in receiver) == demand[j, p_cr, s]
                        for j in sender for s in scenario), 'constr_demand_critical')

                demand_noncritical = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v] * x_jk[j, k, v, p_nc, s] for k in receiver for v in vehicle) + gp.quicksum(vehicleCapacity[v] * x_jkjk[j, k, j_hat, k_hat, v, p_nc, s] for k in receiver for j_hat in sender for k_hat in receiver for v in vehicle) + gp.quicksum(vehicleCapacity[v] * x_jkjk[j_hat, k_hat, j, k, v, p_nc, s] for k in receiver for j_hat in sender for k_hat in receiver for v in vehicle) == demand[j, p_nc, s]
                        for j in sender for s in scenario), 'constr_demand_noncritical')

                hospital_capacity = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v] * x_jk[j, k, v, p, s] for j in sender for v in vehicle) + gp.quicksum(vehicleCapacity[v] * x_jkjk[j, k, j_hat, k_hat, v, p, s] for j in sender for j_hat in sender for k_hat in receiver for v in vehicle) + gp.quicksum(vehicleCapacity[v] * x_jkjk[j_hat, k_hat, j, k, v, p, s] for j in sender for j_hat in sender for k_hat in receiver for v in vehicle) <= gamma * receiverCapacity[k, p]
                        for k in receiver for p in patient for s in scenario), 'constr_hospital_capacity')

                flowbalance_j = m.addConstrs(
                    (gp.quicksum(x_ij[i, j, v, p, s] for i in stagingArea) == gp.quicksum(x_jk[j, k, v, p, s] for k in receiver) + gp.quicksum(x_jkjk[j, k, j_hat, k_hat, v, p, s] for k in receiver for j_hat in sender for k_hat in receiver) for j in sender for v in vehicle for p in patient for s in scenario), 'constr_flowbalance_j')

                flowbalance_k = m.addConstrs(
                    (gp.quicksum(x_ki[k, i, v, s] for i in stagingArea) == gp.quicksum(x_jk[j, k, v, p, s] for j in sender for p in patient) + gp.quicksum(x_jkjk[j_hat, k_hat, j, k, v, p, s] for j in sender for j_hat in sender for k_hat in receiver for p in patient) for k in receiver for v in vehicle for s in scenario), 'constr_flowbalance_k')

            # COMMON CONSTRAINTS
            vehicle_allocation = m.addConstrs(
                (gp.quicksum(x_ij[i, j, v, p, s] for j in sender for p in patient) <= q[i, v]
                 for i in stagingArea for v in vehicle for s in scenario), 'constr_vehicle_allocation')

            facility_operation_outflow = m.addConstrs(
                (x_ij[i, j, v, p, s] <= bigM * z[i] for i in stagingArea for j in sender for v in vehicle for p in patient for s in scenario), 'constr_facility_operation_outflow')

            facility_operation_inflow = m.addConstrs(
                (x_ki[k, i, v, s] <= bigM * z[i] for k in receiver for i in stagingArea for v in vehicle for s in scenario), 'constr_facility_operation_inflow')

            vehicle_operation = m.addConstrs(
                (minVehicle * z[i] <= gp.quicksum(q[i, v] for v in vehicle) for i in stagingArea), 'constr_vehicle_operation')

            facility_operation_vehicle = m.addConstrs(
                (q[i, v] <= bigM * z[i] for i in stagingArea for v in vehicle), 'constr_facility_operation_vehicle')

            ambus_limit = m.addConstrs(
                (gp.quicksum(q[i, v] for i in stagingArea for v in vehicle if v != v_ambul) <= ambusMax for i in stagingArea), 'constr_ambus_limit')

            if shelter == 1:
                # NEW CONSTRAINTS FOR SHELTERS
                open_shelter_inflow = m.addConstrs(
                    (x_jk[j, k, v, p, s] <= bigM * y[k] for k in receiver_sh for j in sender for v in vehicle for p in patient for s in scenario), 'const_open_shelter_inflow')

                # open_shelter_outflow = m.addConstrs(
                #     (x_ki[k, i, v, s] <= bigM * y[k] for k in receiver_sh for i in stagingArea for v in vehicle for s in scenario), 'const_open_shelter_outflow')

                capacity_sh_nc = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p_nc, s] for j in sender for v in vehicle) <= receiverBedcount[k] for k in receiver_sh for s in scenario), 'constr_sh_capacity_nc')

                capacity_sh_c = m.addConstrs(
                    (gp.quicksum(vehicleCapacity[v] * beta[(j, k)] * x_jk[j, k, v, p_cr, s] for j in sender for v in vehicle) <= 0 for k in receiver_sh for s in scenario), 'constr_sh_capacity_cr')

            else:
                print("")
                print("Shelter constraints skipped")
                print("")
                pass

            print("GENERATED CONSTRAINTS")
            print("")

            # 0. Objective Function

            if shelter == 1:
                fixedCost_shelter = gp.quicksum(openingCost_shelter[k] * y[k] for k in receiver_sh)
            else:
                fixedCost_shelter = 0

            fixedCost = gp.quicksum(openingCost[i] * z[i] for i in stagingArea)
            resourceCost = gp.quicksum(vehicleCost[v] * q[i, v] for i in stagingArea for v in vehicle)
            operationCost_ij = gp.quicksum(probability[s] * c_ij[i, j, v] * x_ij[i, j, v, p, s] for i in stagingArea for j in sender for v in vehicle for p in patient for s in scenario)
            operationCost_jk = gp.quicksum(probability[s] * c_jk[j, k, v] * x_jk[j, k, v, p, s] for j in sender for k in receiver for v in vehicle for p in patient for s in scenario)
            operationCost_ki = gp.quicksum(probability[s] * c_ki[k, i, v] * x_ki[k, i, v, s] for k in receiver for i in stagingArea for v in vehicle for s in scenario)

            if trip == 'double':
                operationCost_jkjk = gp.quicksum(probability[s] * c_jkjk[j, k, j_hat, k_hat, v] * x_jkjk[j, k, j_hat, k_hat, v, p, s] for j in sender for k in receiver for j_hat in sender for k_hat in receiver for v in vehicle for p in patient for s in scenario)
                obj = operationCost_ij + operationCost_jk + operationCost_ki + operationCost_jkjk + fixedCost + resourceCost
            elif trip == 'single':
                obj = operationCost_ij + operationCost_jk + operationCost_ki + fixedCost + fixedCost_shelter + resourceCost

            m.setObjective(obj, GRB.MINIMIZE)  # maximize profit

            print("GENERATED OBJECTIVE")
            print("")

            # SET TUNING PARAMETER
            if len(dict_tuning_param) != 0:
                for key, value in dict_tuning_param.items():
                    if key == 'TimeLimit':
                        m.setParam(key, 3600 * value)
                    else:
                        m.setParam(key, value)

                    print("Tune parameter %s: %s" % (key, value))

            # DEFINE STAGING AREA CONSTRAINT
            if staging_iteration == 1:

                time_model_gen_end = time.time()
                best_obj = 1000000000
                solution_set = []
                for iteration in range(len(stagingArea)):

                    stg_location = stagingArea[iteration]
                    closed_location = m.addConstrs(
                        (z[i] == 0 for i in stagingArea if i != stg_location), 'constraint_closed_locations')

                    opened_location = m.addConstrs(
                        (z[i] == 1 for i in stagingArea if i == stg_location), 'constraint_open_location')

                    script_file_name = 'script_%s_%s' % (instance_suffix, stg_location)
                    m.setParam('LogFile', script_file_name)

                    # -- OPTIMIZE
                    m.optimize()
                    m.printStats()
                    m.printQuality()

                    # -- PRINT RESULT
                    print(" ---------------------- ")
                    objective_value = m.objVal
                    print(objective_value)
                    print("")
                    v = m.getVars()
                    for i in range(7):
                        print(v[len(v) - (7 - i)])
                    print(" ---------------------- ")
                    print("")

                    # -- SAVE SOLUTION
                    print("")
                    solution_set.append([stg_location, m.objVal])
                    print("")

                    # -- WRITE COLUTION
                    if (trip == 'single') & (shelter == 0):
                        var_list = ['x_ij', 'x_jk', 'x_ki', 'z', 'q']
                    elif (trip == 'single') & (shelter == 1):
                        var_list = ['x_ij', 'x_jk', 'x_ki', 'z', 'q', 'y']
                    elif (trip == 'double') & (shelter == 0):
                        var_list = ['x_ij', 'x_jk', 'x_ki', 'x_jkjk', 'z', 'q']
                    elif (trip == 'double') & (shelter == 1):
                        var_list = ['x_ij', 'x_jk', 'x_ki', 'x_jkjk', 'z', 'q', 'y']

                    dict_col = {'x_ij': ['variable', 'staging', 'sender', 'vehicle', 'patient', 'scenario', 'value'],
                                'x_jk': ['variable', 'sender', 'receiver', 'vehicle', 'patient', 'scenario', 'value'],
                                'x_ki': ['variable', 'receiver', 'staging', 'vehicle', 'scenario', 'value'],
                                'x_jkjk': ['variable', 'sender1', 'receiver1', 'sender2', 'receiver2', 'vehicle', 'patient', 'scenario', 'value'],
                                'z': ['variable', 'staging', 'value'],
                                'q': ['variable', 'staging', 'vehicle', 'value'],
                                'y': ['variable', 'receiver', 'value']}

                    solution_list = []
                    vars = m.getVars()
                    for var in vars:
                        if var.X > 0.00001:
                            list_var = [x for x in list(filter(None, re.split('[\[\],]', var.varName)))]
                            list_var.append(var.X)
                            solution_list.append(list_var)

                    for i in var_list:
                        this_var_list = [x for x in solution_list if x[0] == i]
                        df = pd.DataFrame(this_var_list, columns=dict_col[i])
                        output_file = '%s_%s.csv' % (i, stg_location)
                        output_path = instance_paths[1]
                        df.to_csv(os.path.join(output_path , output_file), index=False)

                    if objective_value < best_obj:
                        print("-----------")
                        print("BEST SOLUTION : %s" % (stg_location))
                        print("-----------")
                        best_obj = objective_value
                        best_obj_staging = stg_location
                        best_mipgap = m.mipgap * 100

                    else:
                        pass

                    if iteration == 4:
                        continue

                    else:
                        m.reset()
                        m.remove(closed_location)
                        m.remove(opened_location)
                        m.update()

                time_optimize = time.time()

                # -- PRINT TIMES
                time_scen_gen = time_scenario_gen_end - time_scenario_gen_start
                time_param_gen = time_param_gen_end - time_param_gen_start
                time_model_gen = time_model_gen_end - time_model_gen_start
                time_solving = time_optimize - time_model_gen_end

                print("SCENARIO GENERATION TIME: ", time_scen_gen)
                print("PARAMETER GENERATION TIME: ", time_param_gen)
                print("MODEL GENERATION TIME: ", time_model_gen)
                print("OPTIMIZATION TIME: ", time_solving)
                print(solution_set)

                dict_time = {'scen_gen': time_scen_gen,
                             'param_gen': time_param_gen,
                             'model_gen': time_model_gen,
                             'solving': time_solving,
                             'obj_val': best_obj,
                             'mip_gap': best_mipgap,
                             'staging': best_obj_staging}

                cols = ['type', 'value']
                df_time = pd.DataFrame.from_dict(dict_time, orient='index')
                df_time = df_time.reset_index()
                df_time.columns = cols
                df_time.to_csv(path_instance_output + 'computation_result.csv')

                # # ----------------------------
                # #  WRITE RESULT
                # # def writeResult(model, path):
                # # ----------------------------
                # if trip == 'single':
                #     var_list = ['x_ij', 'x_jk', 'x_ki', 'z', 'q']
                # elif trip == 'double':
                #     var_list = ['x_ij', 'x_jk', 'x_ki', 'x_jkjk', 'z', 'q']

                # dict_col = {'x_ij': ['variable', 'staging', 'sender', 'vehicle', 'patient', 'scenario', 'value'],
                #             'x_jk': ['variable', 'sender', 'receiver', 'vehicle', 'patient', 'scenario', 'value'],
                #             'x_ki': ['variable', 'receiver', 'staging', 'vehicle', 'scenario', 'value'],
                #             'x_jkjk': ['variable', 'sender1', 'receiver1', 'sender2', 'receiver2', 'vehicle', 'patient', 'scenario', 'value'],
                #             'z': ['variable', 'staging', 'value'],
                #             'q': ['variable', 'staging', 'vehicle', 'value']}

                # # vars = m.getVars()
                # solution_list = []
                # vars = solution_set[best_sol_iteration]
                # # vars = m_best.getVars()
                # for var in vars:
                #     if var.X > 0.00001:
                #         list_var = [x for x in list(filter(None, re.split('[\[\],]', var.varName)))]
                #         list_var.append(var.X)
                #         solution_list.append(list_var)

                # for i in var_list:
                #     this_var_list = [x for x in solution_list if x[0] == i]
                #     df = pd.DataFrame(this_var_list, columns=dict_col[i])
                #     output_file = i + '.csv'
                #     output_path = instance_paths[1]
                #     df.to_csv(output_path + output_file, index=False)

            else:

                if vss == 1:

                    # Mean scenario solution

                    dict_num_vehicles = {0.8: [6833, 817],
                                         0.9: [7734, 920],
                                         1: [8694, 1025],
                                         1.1: [9522, 1123]}
                    dict_vehicle_nums = {'a1': dict_num_vehicles[occupancy_sender][0],
                                         'a4': dict_num_vehicles[occupancy_sender][1]}
                    print("")
                    print(dict_vehicle_nums)
                    print("")

                    stg_location = ['a1', 'a4']
                    stg_location_ambus = ['a1']
                    print_string = 'ADDING CONSTRAINTS FOR SENDER %s' % (num_sender)

                    print("---------------------------------")
                    print(print_string)
                    print("---------------------------------")

                    closed_location = m.addConstrs(
                        (z[i] == 0 for i in stagingArea if i not in stg_location), 'constraint_closed_locations')

                    opened_location = m.addConstrs(
                        (z[i] == 1 for i in stagingArea if i in stg_location), 'constraint_open_location')

                    set_vehicle_num_v00_0 = m.addConstrs(
                        (q[i, 'v00'] == 0 for i in stagingArea if i not in stg_location), 'constraint_fix_vehicles_v00_0')

                    set_vehicle_num_v00_1 = m.addConstrs(
                        (q[i, 'v00'] == dict_vehicle_nums[i] for i in stagingArea if i in stg_location), 'constraint_fix_vehicles_v00_1')

                    set_vehicle_num_v20_0 = m.addConstrs(
                        (q[i, 'v20'] == 0 for i in stagingArea if i not in stg_location_ambus), 'constraint_fix_vehicles_v20_0')

                    set_vehicle_num_v20_1 = m.addConstrs(
                        (q[i, 'v20'] == 16 for i in stagingArea if i in stg_location_ambus), 'constraint_fix_vehicles_v20_1')

                # -- DEFINE LOG FILE NAME
                script_file_name = 'script_%s' % (instance_suffix)
                m.setParam('LogFile', script_file_name)

                # -- OPTIMIZE
                time_model_gen_end = time.time()
                m.optimize()
                time_optimize = time.time()
                m.printStats()
                m.printQuality()
                sol_mipgap = m.mipgap * 100

                # -- PRINT RESULT
                print(" ---------------------- ")
                objective_value = m.objVal

                if (vss == 1) or (evpi == 1):
                    dict_objective_solutions[current_scenario] = objective_value

                print(objective_value)
                print("")
                v = m.getVars()
                for i in range(5):
                    print(v[len(v) - (5 - i)])
                print(" ---------------------- ")
                print("")
                
            
                # -- PRINT TIMES
                time_scen_gen = time_scenario_gen_end - time_scenario_gen_start
                time_param_gen = time_param_gen_end - time_param_gen_start
                time_model_gen = time_model_gen_end - time_model_gen_start
                time_solving = time_optimize - time_model_gen_end

                print("SCENARIO GENERATION TIME: ", time_scen_gen)
                print("PARAMETER GENERATION TIME: ", time_param_gen)
                print("MODEL GENERATION TIME: ", time_model_gen)
                print("OPTIMIZATION TIME: ", time_solving)

                dict_time = {'scen_gen': time_scen_gen,
                             'param_gen': time_param_gen,
                             'model_gen': time_model_gen,
                             'solving': time_solving,
                             'mip_gap': sol_mipgap,
                             'Opt. Total Cost': objective_value,
                             }

                cols = ['type', 'value']
                df_time = pd.DataFrame.from_dict(dict_time, orient='index')
                df_time = df_time.reset_index()
                df_time.columns = cols
                df_time.to_csv(path_instance_output + 'computation_result.csv')

                # ----------------------------
                #  WRITE RESULT
                # def writeResult(model, path):
                # ----------------------------
                if (trip == 'single') & (shelter == 0):
                    var_list = ['x_ij', 'x_jk', 'x_ki', 'z', 'q']
                elif (trip == 'single') & (shelter == 1):
                    var_list = ['x_ij', 'x_jk', 'x_ki', 'z', 'q', 'y']
                elif (trip == 'double') & (shelter == 0):
                    var_list = ['x_ij', 'x_jk', 'x_ki', 'x_jkjk', 'z', 'q']
                elif (trip == 'double') & (shelter == 1):
                    var_list = ['x_ij', 'x_jk', 'x_ki', 'x_jkjk', 'z', 'q', 'y']

                dict_col = {'x_ij': ['variable', 'staging', 'sender', 'vehicle', 'patient', 'scenario', 'value'],
                            'x_jk': ['variable', 'sender', 'receiver', 'vehicle', 'patient', 'scenario', 'value'],
                            'x_ki': ['variable', 'receiver', 'staging', 'vehicle', 'scenario', 'value'],
                            'x_jkjk': ['variable', 'sender1', 'receiver1', 'sender2', 'receiver2', 'vehicle', 'patient', 'scenario', 'value'],
                            'z': ['variable', 'staging', 'value'],
                            'q': ['variable', 'staging', 'vehicle', 'value'],
                            'y': ['variable', 'receiver', 'value']}

                vars = m.getVars()
                solution_list = []
                for var in vars:
                    if var.X > 0.00001:
                        list_var = [x for x in list(filter(None, re.split('[\[\],]', var.varName)))]
                        list_var.append(var.X)
                        solution_list.append(list_var)

                for i in var_list:
                    this_var_list = [x for x in solution_list if x[0] == i]
                    df = pd.DataFrame(this_var_list, columns=dict_col[i])
                    output_file = i + '.csv'
                    output_path = instance_paths[1]
                    df.to_csv(output_path + output_file, index=False)

        if vss == 1:

            df = pd.DataFrame.from_dict(dict_objective_solutions, orient='index')
            df = df.reset_index()
            df.columns = ['scenario', 'objective']
            file_name = 'result_option%s_sender%s_%s.csv' % (unique_demand, num_sender, occupancy_sender)
            df.to_csv(path_run+'\\pelo_tests\\set_VSS\\'+ file_name)
