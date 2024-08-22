import csv
import numpy as np
import pandas as pd

import os
import sys
import inspect

import time
import itertools

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from tools.gps_distance_calculator import haversine

def trunc(values, decs=0):
    if decs == 0:
        output = int(values)
    else:
        output = np.trunc(values * 10 ** decs) / (10 ** decs)
    return output

# ----------------------------------------
# ------------ Summary ------------------
# 1. Defines locations of staging area, receiving, sending hospitals
# 2. Creates T (time) and C (weighted cost) matrices
# 3. Defines demand of each sending hospitals
# 4. Defines capacity of receiving hospitals
# 5. Creates coordinate_lookup.csv
# ----------------------------------------

# --------------------------------------------
# ------ DETERMIN SIZE OF THE PROBLEM --------
# --------------------------------------------
def paramGen(dict_path, dict_input_param, path_instance_input):

    print("=====================")
    print("CHECK - PAPER VERSION")
    print("=====================")

    # Define formulation type
    preprocess = int(dict_input_param['preprocess'])
    trip = dict_input_param['trip']
    formulation_type = dict_input_param['formulation_type']
    scale = int(dict_input_param['scale'])
    num_sender = dict_input_param['num_senders']
    check_EV = int(dict_input_param['check_EV'])

    # parameters related to demand
    icu_bed_rate = float(dict_input_param['icu_bed_rate'])
    hos_cr_occupancy_rate = float(dict_input_param['hos_cr_occupancy_rate'])
    hos_nc_occupancy_rate = float(dict_input_param['hos_nc_occupancy_rate'])
    nh_bed_occupancy_rate = float(dict_input_param['nh_occupancy_rate'])
    hos_bed_worst_occupancy = float(dict_input_param['worst_demand_hos'])
    nh_bed_worst_occupancy = float(dict_input_param['worst_demand_nh'])

    # parameters related to capacity
    gamma = float(dict_input_param['gamma'])
    gamma_nh = float(dict_input_param['gamma_nh'])
    hos_cr_occupancy_rate_receiver = float(dict_input_param['hos_cr_occupancy_rate_receiver'])
    hos_nc_occupancy_rate_receiver = float(dict_input_param['hos_nc_occupancy_rate_receiver'])
    nh_bed_occupancy_rate_receiver = float(dict_input_param['nh_occupancy_rate_receiver'])
    hos_cr_bed_vacancy_rate_receiver = 1 - hos_cr_occupancy_rate_receiver
    hos_nc_bed_vacancy_rate_receiver = 1 - hos_nc_occupancy_rate_receiver
    nh_bed_vacancy_rate_receiver = 1 - nh_bed_occupancy_rate_receiver

    # parameters related to sender demand
    evacuation_proportion = float(dict_input_param['evaucation_proportion'])
    worst_case_demand = int(dict_input_param['worst_case'])

    # Cost related parameters
    ambulance_per_mile_cost = int(dict_input_param['ambulance_per_mile_cost'])
    ambus_per_mile_cost = int(dict_input_param['ambus_per_mile_cost'])
    ambulance_procurement_cost = int(dict_input_param['ambulance_procurement_cost'])
    # ambus_procurement_cost = int(dict_input_param['ambus_procurement_cost'])
    ambus_procurement_cost_1 = int(dict_input_param['ambus_procurement_cost_1'])
    ambus_procurement_cost_2 = int(dict_input_param['ambus_procurement_cost_2'])
    ambus_procurement_cost_3 = int(dict_input_param['ambus_procurement_cost_3'])
    ambus_procurement_cost_4 = int(dict_input_param['ambus_procurement_cost_4'])
    fixed_cost = int(dict_input_param['fixed_cost'])
    fixed_cost_shelter = int(dict_input_param['fixed_cost_shelter'])
    discount_shelter = float(dict_input_param['discount_shelter'])

    # Travel time related parameters
    avg_mph_ambul = int(dict_input_param['avg_mph_ambul'])  # mi/hr
    avg_mph_ambus = int(dict_input_param['avg_mph_ambus'])  # mi/hr
    addTime = int(dict_input_param['addTime'])  # additional time (minutes) per patient for AmBuses
    timeMax = int(dict_input_param['timeMax'])

    # Create time related dictionaries
    type_ambulance = 'v00'
    ambusCapacity_min = int(dict_input_param['ambusCapacity_min'])
    ambusCapacity = int(dict_input_param['ambusCapacity'])
    dict_velocity = {}  # mi / hr
    dict_add_time = {}  # hrs
    dict_velocity[type_ambulance] = avg_mph_ambul
    dict_add_time[type_ambulance] = 0

    for v in range(ambusCapacity - ambusCapacity_min + 1):
        v_type = v + ambusCapacity_min
        if v_type < 10:
            key = 'v0%s' % v_type
        else:
            key = 'v%s' % v_type
        dict_velocity[key] = avg_mph_ambus
        dict_add_time[key] = round(v_type * addTime / 60, 2)

    # Other parameters
    vehicleMix = dict_input_param['vehicleMix']
    minVehicle = int(dict_input_param['minVehicle'])
    ambusMax = int(dict_input_param['ambusMax'])
    bigM = int(dict_input_param['bigM'])

    # --------------------------------
    # ------ LOAD INPUT FILES --------
    # --------------------------------
    
    # input file names
    if check_EV != 1:
        scenario_lookup_file_name = 'scenario_lookup.tab'
    else:
        scenario_lookup_file_name = 'scenario_lookup_mean_demand.tab'
    input_sender_file = 'input_sender.tab'
    input_receiver_file = 'input_receiver.tab'
    input_stagingarea_file = 'input_stagingArea.tab'
    input_patient_file = 'input_patient.tab'
    input_vehicle_file = 'input_vehicle.tab'
    input_minvehicle_file = 'input_minVehicle.tab'
    input_ambusmax_file = 'input_ambusMax.tab'
    input_t_max_file = 'input_T_max.tab'

    input_c_ij_file_tab = 'input_c_ijv.tab'
    input_c_jk_file_tab = 'input_c_jkv.tab'
    input_c_ki_file_tab = 'input_c_kiv.tab'
    input_c_jkjk_file_tab = 'input_c_jkjkv.tab'
    input_c1_file_tab = 'input_c1.tab'
    input_c2_file_tab = 'input_c2.tab'
    input_c_v_file = 'input_c_v.tab'
    input_receiverCapacity_file = 'input_receiverCapacity.csv'
    input_receiverCapacity_file_tab = 'input_receiverCapacity.tab'
    input_receiverBedcount_file = 'input_receiverBedcount.csv'
    input_receiverBedcount_file_tab = 'input_receiverBedcount.tab'

    input_demand_file = 'input_demand.tab'
    input_demand_s_temp_file = 'input_demand_s_temp.tab'
    input_demand_vs_file_csv = 'input_demand_vs.csv'
    input_demand_vs_file_tab = 'input_demand_vs.tab'
    input_openingCost_file = 'input_openingCost.tab'
    input_openingCost_shelter_file = 'input_openingCost_shelter.tab'
    input_operatingCost_file = 'input_operatingCost.tab'
    input_ambulanceCapacity_file = 'input_ambulanceCapacity.tab'
    input_bigM_file = 'input_bigM.tab'
    input_arc1_file = 'input_arc1.tab'
    input_arc2_file = 'input_arc2.tab'

    # FIND SENDING HOSPITALS FOUND IN SCENARIOS
    df_stagingArea = pd.read_csv(path_instance_input + '\\df_staging.csv', index_col=0)    # Staging area Dataframe
    df_receiver = pd.read_csv(path_instance_input + '\\df_receiver.csv', index_col=0)  # Receiver Dataframe
    senderDF = pd.read_csv(os.path.join(path_instance_input , scenario_lookup_file_name), delimiter='\t')
    senderList_temp = list()
    senderList_temp = list(senderDF.sender.unique())
    senderList_temp.sort()

    # Temporary sender Dataframe
    temp_df_sender = pd.read_csv(path_instance_input + '\\df_sender.csv', index_col=0)
    df_sender = temp_df_sender[temp_df_sender.code.isin(senderList_temp)]

    list_locations = [df_stagingArea, df_receiver, df_sender]
    df_hospitals = pd.concat(list_locations)

    stagingAreaList = list(df_stagingArea.code)
    senderList = list(df_sender.code)
    receiverList = list(df_receiver.code)
    receiverList_sh = [k for k in df_receiver.code if k[0] == 'q']
    patientList = ["c", "n"]

    df_hos = df_hospitals[['latitude', 'longitude']]
    df_hos.index = df_hospitals['code']
    dict_gps = df_hos.to_dict('index')

    # --------------------------------
    # -- DEFINE DEFAULT RECEIVERS ----
    # --------------------------------
    output = open(os.path.join(path_instance_input , input_receiver_file), 'w')
    output.write("receiver" + "\n")

    for j in receiverList:
        output.write(j + "\n")

    output.close()

    # ------------------------------------
    # -- DEFINE DEFAULT STAGING AREAS ----
    # ------------------------------------
    output = open(os.path.join(path_instance_input , input_stagingarea_file), 'w')
    output.write("stagingArea" + "\n")

    for j in stagingAreaList:
        output.write(j + "\n")

    output.close()

    # --------------------------------
    # -- DEFINE DEFAULT SENDERS ------
    # --------------------------------
    output = open(os.path.join(path_instance_input , input_sender_file), 'w')
    output.write("sender" + "\n")

    for j in senderList:
        output.write(j + "\n")

    output.close()

    # --------------------------------
    # -- DEFINE DEFAULT Patients -----
    # --------------------------------
    output = open(os.path.join(path_instance_input , input_patient_file), 'w')
    output.write("patientType" + "\n")

    for j in patientList:
        output.write(j + "\n")

    output.close()

    # ------------------------------
    # -- DEFINE MAX TRAVEL TIME ----
    # ------------------------------
    output = open(os.path.join(path_instance_input , input_t_max_file), 'w')
    output.write(str(timeMax) + "\n")
    output.close()

    # -------------------------------------------
    # -- DEFINE DEFAULT MAX NUMBER OF AMBUS -----
    # -------------------------------------------
    output = open(os.path.join(path_instance_input , input_ambusmax_file), 'w')
    output.write(str(ambusMax) + "\n")
    output.close()

    # -------------------------------------------
    # -- DEFINE BIG M ---------------------------
    # -------------------------------------------
    output = open(os.path.join(path_instance_input , input_bigM_file), 'w')
    output.write(str(bigM) + "\n")
    output.close()

    # ----------------------------------------------------------
    # -- DEFINE MINIMUM VEHICLE NUMBERS TO OPEN STAGING AREA ---
    # ----------------------------------------------------------
    output = open(os.path.join(path_instance_input , input_minvehicle_file), 'w')
    output.write(str(minVehicle) + "\n")
    output.close()

    # --------------------------------
    # -- DEFINE DEFAULT Ambulances ---
    # --------------------------------
    output = open(os.path.join(path_instance_input , input_vehicle_file), 'w')
    output.write("ambulanceType" + "\n")
    ambulanceCapacityList = range(ambusCapacity_min, ambusCapacity + 1)

    output_capacity = open(os.path.join(path_instance_input , input_ambulanceCapacity_file), 'w')
    output_capacity.write("ambulanceType" + "\t" + "capacity" + "\n")

    ambulanceList = list()
    capacityList = list()

    # if ambulances are only
    if vehicleMix != "mix":
        ambulanceList.append(type_ambulance)
        capacityList.append(1)

    # if ambulances and ambuses are both used
    else:
        # add ambulance
        ambulanceList.append(type_ambulance)
        capacityList.append(1)

        # add ambus
        for i in range(len(ambulanceCapacityList)):
            if ambulanceCapacityList[i] % 5 == 0:
                if ambulanceCapacityList[i] <= 9:
                    capacityString = "v0" + str(ambulanceCapacityList[i])
                    ambulanceList.append(capacityString)
                    capacityList.append(ambulanceCapacityList[i])

                else:
                    capacityString = "v" + str(ambulanceCapacityList[i])
                    ambulanceList.append(capacityString)
                    capacityList.append(ambulanceCapacityList[i])

            else:
                continue

    for j in range(len(ambulanceList)):
        output.write(str(ambulanceList[j]) + "\n")
        output_capacity.write(str(ambulanceList[j]) + "\t" + str(capacityList[j]) + "\n")

    output.close()
    output_capacity.close()

    # numAmbulanceType = len(ambulanceList)

    # # -------------------------------------
    # # -----  CREATE AMBULANCE CAPACITY ----
    # # -------------------------------------
    # output = open(os.path.join(path_instance_input , input_ambulanceCapacity_file), 'w')
    # capacityList = list()
    # capacityList.append(1)
    # for i in range(numAmbulanceType - 1):
    #     c = i + ambusCapacity_min
    #     capacityList.append(c)

    # try:
    #     titleline = "ambulanceType" + "\t" + "capacity" + "\n"
    #     output.write(titleline)

    #     for i in range(numAmbulanceType):
    #         thisType = ambulanceList[i]
    #         thisCapacity = capacityList[i]
    #         newline = str(thisType) + "\t" + str(thisCapacity) + "\n"
    #         output.write(newline)

    # finally:
    #     output.close()

    # ---------------------------------------------
    # -----  CREATE AMBULANCE PROCUREMENT COST ----
    # ---------------------------------------------
    ambus_set_1 = ['v01', 'v02', 'v03', 'v04', 'v05']
    ambus_set_2 = ['v06', 'v07', 'v08', 'v09', 'v10']
    ambus_set_3 = ['v11', 'v12', 'v13', 'v14', 'v15']
    ambus_set_4 = ['v16', 'v17', 'v18', 'v19', 'v20']

    try:
        output = open(os.path.join(path_instance_input , input_c_v_file), 'w')
        titleline = 'vehicleType' + "\t" + 'c_v' + '\n'
        output.write(titleline)

        for i in ambulanceList:
            if i == type_ambulance:
                cost = ambulance_procurement_cost
            else:
                if i in ambus_set_1:
                    cost = ambus_procurement_cost_1
                if i in ambus_set_2:
                    cost = ambus_procurement_cost_2
                elif i in ambus_set_3:
                    cost = ambus_procurement_cost_3
                else:
                    cost = ambus_procurement_cost_4

            newline = str(i) + '\t' + str(cost) + '\n'
            output.write(newline)

    finally:
        output.close()

    # ------------------------------------------------------
    # --------    CAPACITY Bjp: NEW CAPACITY  ---------
    # ------------------------------------------------------
    dict_receiver_bedcount = dict(zip(df_receiver['code'], df_receiver['beds']))
    dict_receiver_type = dict(zip(df_receiver['code'], df_receiver['type']))

    list_capacity_data = []
    list_bedcount_data = []
    for i in receiverList:
        nameReceiver = i

        # Hospital Capacity
        bedcount = int(dict_receiver_bedcount[nameReceiver])
        receiverType = dict_receiver_type[nameReceiver]

        newline_bedcount = [nameReceiver, bedcount]
        list_bedcount_data.append(newline_bedcount)

        if receiverType == 'HOSPITAL':
            critical_beds = int(bedcount * icu_bed_rate)

            for j in patientList:
                current_patient = j
                if current_patient == 'c':
                    occupied = int(critical_beds * hos_cr_occupancy_rate_receiver)
                    total_adjusted = int(critical_beds * gamma)
                    capacity = total_adjusted - occupied
                    # capacity = int(critical_beds * hos_cr_bed_vacancy_rate_receiver * gamma)
                elif current_patient == 'n':
                    total_ncr = bedcount - critical_beds
                    occupied = int(total_ncr * hos_nc_occupancy_rate_receiver)
                    total_adjusted = int(total_ncr * gamma)
                    capacity = total_adjusted - occupied
                    # capacity = int((bedcount - critical_beds) * hos_nc_bed_vacancy_rate_receiver * gamma)

                newline = [nameReceiver, current_patient, capacity]
                list_capacity_data.append(newline)

        # Nursing home capacity
        elif receiverType == 'NH':
            for j in patientList:
                current_patient = j

                if current_patient == 'c':
                    capacity = 0

                elif current_patient == 'n':
                    bedcount = dict_receiver_bedcount[nameReceiver]
                    occupied = int(bedcount * nh_bed_occupancy_rate_receiver)
                    total_adjusted = int(bedcount * gamma_nh)
                    capacity = total_adjusted - occupied
                    # capacity = int(bedcount * nh_bed_vacancy_rate_receiver * gamma_nh)

                newline = [nameReceiver, current_patient, capacity]
                list_capacity_data.append(newline)

        elif receiverType == 'SLT':
            for j in patientList:
                current_patient = j

                if current_patient == 'c':
                    capacity = 0

                elif current_patient == 'n':
                    bedcount = dict_receiver_bedcount[nameReceiver]
                    capacity = int(bedcount)

                newline = [nameReceiver, current_patient, capacity]
                list_capacity_data.append(newline)

    col_name = ["receiver", "patientType", "receiverCapacity"]
    df_receiverCapacity = pd.DataFrame(list_capacity_data, columns=col_name)
    df_receiverCapacity.to_csv(os.path.join(path_instance_input, input_receiverCapacity_file), index=False)
    df_receiverCapacity.to_csv(os.path.join(path_instance_input, input_receiverCapacity_file_tab), sep='\t', index=False)

    col_name_bedcount = ["receiver", "bedcount"]
    df_receiverBedcount = pd.DataFrame(list_bedcount_data, columns=col_name_bedcount)
    df_receiverBedcount.to_csv(os.path.join(path_instance_input, input_receiverBedcount_file), index=False)
    df_receiverBedcount.to_csv(os.path.join(path_instance_input, input_receiverBedcount_file_tab), sep='\t', index=False)

    # --------------------------------------------
    # ------    CREATE OPENING COST MATRIX   -----
    # --------------------------------------------
    output = open(os.path.join(path_instance_input , input_openingCost_file), 'w')

    try:
        titleline = "stagingArea" + "\t" + "openingCost" + "\n"
        output.write(titleline)

        for i in stagingAreaList:
            newline = i + "\t" + str(fixed_cost) + "\n"
            output.write(newline)

    finally:
        output.close()

    # --------------------------------------------
    # ------    CREATE OPENING COST MATRIX   -----
    # --------------------------------------------
    output = open(os.path.join(path_instance_input , input_openingCost_shelter_file), 'w')

    try:
        titleline = "receiver" + "\t" + "openingCost" + "\n"
        output.write(titleline)

        for i in receiverList_sh:
            if i == 'q001':
                cost_opening_shelter = int(fixed_cost_shelter * discount_shelter)
            else:
                cost_opening_shelter = fixed_cost_shelter

            newline = i + "\t" + str(cost_opening_shelter) + "\n"
            output.write(newline)

    finally:
        output.close()

    # --------------------------------------------
    # ------    CREATE VEHICLE OPERATING COST MATRIX   -----
    # --------------------------------------------
    output = open(os.path.join(path_instance_input , input_operatingCost_file), 'w')
    dict_operating_cost = {}
    try:
        titleline = "vehicleType" + "\t" + "cost" + "\n"
        output.write(titleline)

        for i in ambulanceList:
            if i == type_ambulance:
                newline = i + "\t" + str(ambulance_per_mile_cost) + "\n"
                dict_operating_cost[i] = ambulance_per_mile_cost
            else:
                newline = i + "\t" + str(ambus_per_mile_cost) + "\n"
                dict_operating_cost[i] = ambus_per_mile_cost
            output.write(newline)

    finally:
        output.close()

    # --------------------------------------
    # --------    DEMAND Djp : NEW ---------
    # --------------------------------------
    output = open(os.path.join(path_instance_input , input_demand_file), 'w')
    dict_sender_beds = dict(zip(df_sender['code'], df_sender['beds']))
    dict_sender_type = dict(zip(df_sender['code'], df_sender['type']))

    try:
        titleline = "sender" + "\t" + "patientType" + "\t" + "demand" + "\n"
        output.write(titleline)

        for i in senderList:
            nameSender = i

            # Hospital demand
            bedcount = int(dict_sender_beds[nameSender])
            potential_demand = int(bedcount * evacuation_proportion)
            senderType = dict_sender_type[nameSender]

            if senderType == 'HOSPITAL':
                for j in patientList:
                    current_patient = j
                    critical_demand = int(potential_demand * icu_bed_rate)
                    noncr_demand = int(potential_demand - critical_demand)

                    if worst_case_demand == 1:
                        if current_patient == 'c':
                            demand = int(critical_demand * hos_bed_worst_occupancy)
                        elif current_patient == 'n':
                            demand = int(noncr_demand * hos_bed_worst_occupancy)

                    else:
                        if current_patient == 'c':
                            demand = int(critical_demand * hos_cr_occupancy_rate)
                        elif current_patient == 'n':
                            demand = int(noncr_demand * hos_nc_occupancy_rate)

                    newline = nameSender + "\t" + current_patient + "\t" + str(demand) + "\n"
                    output.write(newline)

            elif senderType == 'NH':
                for j in patientList:
                    current_patient = j

                    if worst_case_demand == 1:
                        if current_patient == 'c':
                            demand = 0
                        else:
                            demand = int(potential_demand * nh_bed_worst_occupancy)
                    else:
                        if current_patient == 'c':
                            demand = 0
                        else:
                            demand = int(potential_demand * nh_bed_occupancy_rate)

                    newline = nameSender + "\t" + current_patient + "\t" + str(demand) + "\n"
                    output.write(newline)

    finally:
        output.close()

    # ----------------------------------------------------
    # ------    GENERATE SCENARIO BASED PARAMETERS   -----
    # ----------------------------------------------------
    # DEMAND
    inputDemandDF = pd.read_csv(os.path.join(path_instance_input , input_demand_file), delimiter='\t')
    output_s = open(os.path.join(path_instance_input , input_demand_s_temp_file), 'w')

    titleLine = "sender" + "\t" + "patientType" + "\t" + "scenario" + "\t" + "demand" + "\n"
    output_s.write(titleLine)

    for i in range(len(senderDF)):
        thisSender = senderDF.sender[i]
        thisMultiplier = senderDF.multiplier[i]
        thisScenario = senderDF.scenario[i]

        for j in patientList:
            thisPatient = j
            thisDemand = inputDemandDF.demand[inputDemandDF.sender == thisSender][inputDemandDF.patientType == thisPatient] * thisMultiplier
            newline = str(thisSender) + "\t" + str(thisPatient) + "\t" + str(thisScenario) + "\t" + str(trunc(thisDemand, 0)) + "\n"
            output_s.write(newline)

    output_s.close()

    demandDF = pd.read_csv(os.path.join(path_instance_input , input_demand_s_temp_file), delimiter='\t')
    demandDF_final = demandDF.sort_values(by=['sender', 'scenario'])
    demandDF_final = demandDF_final.reset_index(drop=True)
    demandDF_final.to_csv(os.path.join(path_instance_input , input_demand_vs_file_tab), sep='\t', index=False)
    demandDF_final.to_csv(os.path.join(path_instance_input , input_demand_vs_file_csv), index=False)

    # ---------------------------------------
    # NEW METHOD FOR GENERATING COST MATRIX
    # ---------------------------------------
    # GENERATE REFERENCE DICTIONARIES
    path = dict_path['data']
    df_loc = pd.read_csv(path + '\\healthcare_facilities_cmoc.csv', index_col = 0)
    cut_columns = ['LATITUDE', 'LONGITUDE']
    df = df_loc[cut_columns]
    df.index = df_loc['NID']
    dict_loc = df.to_dict('index')

    # CODE: NID MAP
    dict_sender = dict(zip(df_sender['code'], df_sender['nid']))
    dict_receiver = dict(zip(df_receiver['code'], df_receiver['nid']))
    dict_staging = dict(zip(df_stagingArea['code'], df_stagingArea['nid']))

    # --------------------------------
    # SKIP FOR PATH_BASED FORMULATION
    # --------------------------------
    if formulation_type == 'path':
        print("-- SKIPPED: c_ijv")
        print("-- SKIPPED: c_jkv")
        print("-- SKIPPED: c_kiv")
        print("-- SKIPPED: c_jkjkv")
        pass
    else:

        # --------------------------------------------
        # CREATE PARAMETER MATRIX - C_IJ (index: ijv)
        # --------------------------------------------
        cols = ['stagingArea', 'sender', 'vehicleType']
        value_col = 'c_ijv'
        b = list(itertools.product(stagingAreaList, senderList, ambulanceList))
        print("Length of %s: %s" % (value_col, len(b)))

        distance_values = [round(haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                           dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE']), 2)
                           for item_list in b]

        cost_values = [int(haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                     dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                           * dict_operating_cost[item_list[2]])
                       for item_list in b]

        df_cost = pd.DataFrame(b, columns=cols)
        df_cost[value_col] = cost_values
        file = 'input_%s.csv' % (value_col)
        df_cost.to_csv(os.path.join(path_instance_input, file), index=False)
        df_cost.to_csv(os.path.join(path_instance_input, input_c_ij_file_tab), sep='\t', index=False)

        value_col = 'd_ijv'
        df_distance = pd.DataFrame(b, columns=cols)
        df_distance[value_col] = distance_values
        file = 'input_%s.csv' % (value_col)
        df_distance.to_csv(os.path.join(path_instance_input, file), index=False)

        print("-- %s CREATED" % (value_col))

        # --------------------------------------------
        # CREATE PARAMETER MATRIX - C_JK (index: jkv)
        # --------------------------------------------
        cols = ['sender', 'receiver', 'vehicleType']
        value_col = 'c_jkv'
        b = list(itertools.product(senderList, receiverList, ambulanceList))
        print("j: %s, k: %s, v: %s" % (len(senderList), len(receiverList), len(ambulanceList)))
        print("Length of %s: %s" % (value_col, len(b)))

        distance_values = [round(haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                           dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE']), 2)
                           for item_list in b]

        time_values = [round(haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                       dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE']) / dict_velocity[item_list[2]]
                            + dict_add_time[item_list[2]], 2)
                       for item_list in b]

        cost_values = [int(haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                     dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'])
                           * dict_operating_cost[item_list[2]])
                       for item_list in b]

        df_cost = pd.DataFrame(b, columns=cols)
        rows_before = len(df_cost)
        df_cost[value_col] = cost_values
        df_cost['t_jkv'] = time_values
        df_cost = df_cost[df_cost['t_jkv'] < 8]   # remove arc time greater than 8 hours
        cols_final = cols + [value_col]
        df_cost = df_cost[cols_final]
        rows_after = len(df_cost)
        print("")
        print("C_JKV NUMBER OF ROWS REMOVED: %s" % (rows_before - rows_after))
        print("")

        file = 'input_%s.csv' % (value_col)
        df_cost.to_csv(os.path.join(path_instance_input, file), index=False)
        df_cost.to_csv(os.path.join(path_instance_input, input_c_jk_file_tab), sep='\t', index=False)

        value_col = 'd_jkv'
        df_distance = pd.DataFrame(b, columns=cols)
        df_distance[value_col] = distance_values
        file = 'input_%s.csv' % (value_col)
        df_distance.to_csv(os.path.join(path_instance_input, file), index=False)

        print("-- %s CREATED" % (value_col))

        # --------------------------------------------
        # CREATE PARAMETER MATRIX - C_KI (index: kiv)
        # --------------------------------------------
        cols = ['receiver', 'stagingArea', 'vehicleType']
        value_col = 'c_kiv'
        b = list(itertools.product(receiverList, stagingAreaList, ambulanceList))
        print("Length of %s: %s" % (value_col, len(b)))

        distance_values = [round(haversine(dict_loc[dict_receiver[item_list[0]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[0]]]['LATITUDE'],
                                           dict_loc[dict_staging[item_list[1]]]['LONGITUDE'], dict_loc[dict_staging[item_list[1]]]['LATITUDE']), 2)
                           for item_list in b]

        cost_values = [int(haversine(dict_loc[dict_receiver[item_list[0]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[0]]]['LATITUDE'],
                                     dict_loc[dict_staging[item_list[1]]]['LONGITUDE'], dict_loc[dict_staging[item_list[1]]]['LATITUDE'])
                           * dict_operating_cost[item_list[2]])
                       for item_list in b]

        df_cost = pd.DataFrame(b, columns=cols)
        df_cost[value_col] = cost_values
        file = 'input_%s.csv' % (value_col)
        df_cost.to_csv(os.path.join(path_instance_input, file), index=False)
        df_cost.to_csv(os.path.join(path_instance_input, input_c_ki_file_tab), sep='\t', index=False)

        value_col = 'd_kiv'
        df_distance = pd.DataFrame(b, columns=cols)
        df_distance[value_col] = distance_values
        file = 'input_%s.csv' % (value_col)
        df_distance.to_csv(os.path.join(path_instance_input, file), index=False)

        print("-- %s CREATED" % (value_col))

        if trip == 'single':
            print("-- SKIPPED: c_jkjk")
            pass
        else:
            # --------------------------------------------
            # CREATE PARAMETER MATRIX - C_JKJK (index: jkjkv)
            # --------------------------------------------
            cols = ['sender1', 'receiver1', 'sender2', 'receiver2', 'vehicleType']
            value_col = 'c_jkjkv'
            print("j: %s, k: %s, v: %s" % (len(senderList), len(receiverList), len(ambulanceList)))
            print("Length of c_jkjkv: ", len(senderList)* len(senderList) * len(receiverList) * len(receiverList) * len(ambulanceList))
            b = list(itertools.product(senderList, receiverList, senderList, receiverList, ambulanceList))
            print("Length of %s: %s" % (value_col, len(b)))

            distance_values = [round(haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                               dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'],
                                                 dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'],
                                                 dict_loc[dict_receiver[item_list[3]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[3]]]['LATITUDE']), 2)
                               for item_list in b]

            print("%s distance created" % (value_col))

            df_all = pd.DataFrame(b, columns=cols)
            rows_before = len(df_all)
            df_all['d_jkjkv'] = distance_values
            df_all['velocity'] = df_all['vehicleType'].map(dict_velocity)
            df_all['add_time'] = df_all['vehicleType'].map(dict_add_time)
            df_all['operating_cost'] = df_all['vehicleType'].map(dict_operating_cost)
            df_all['t'] = round(df_all['d_jkjkv'] / df_all['velocity'] + df_all['add_time'], 2)
            df_all[value_col] = df_all['d_jkjkv'] * df_all['operating_cost']
            df_all[value_col] = df_all[value_col].astype(int)
            df_all = df_all[df_all['t'] < 8]   # remove arc time greater than 8 hours

            cols_final = cols + [value_col]
            df_cost = df_all[cols_final]
            rows_after = len(df_cost)

            print("")
            print("C_JKV NUMBER OF ROWS REMOVED: %s" % (rows_before - rows_after))
            print("")

            file = 'input_%s.csv' % (value_col)
            df_cost.to_csv(os.path.join(path_instance_input, file), index=False)
            df_cost.to_csv(os.path.join(path_instance_input, input_c_jkjk_file_tab), sep='\t', index=False)

            value_col = 'd_jkjkv'
            cols_final = cols + [value_col]
            df_distance = df_all[cols_final]
            file = 'input_%s.csv' % (value_col)
            df_distance.to_csv(os.path.join(path_instance_input, file), index=False)

            print("-- %s CREATED" % (value_col))

            '''
            distance_values = [round(haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                               dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'],
                                                 dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'],
                                                 dict_loc[dict_receiver[item_list[3]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[3]]]['LATITUDE']), 2)
                               for item_list in b]

            print("%s distance created" % (value_col))

            time_values = [round((haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                               dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'],
                                                 dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'])
                                     + haversine(dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'],
                                                 dict_loc[dict_receiver[item_list[3]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[3]]]['LATITUDE'])) / dict_velocity[item_list[4]]
                                + dict_add_time[item_list[4]], 2)
                               for item_list in b]

            print("%s time created" % (value_col))

            cost_values = [int((haversine(dict_loc[dict_sender[item_list[0]]]['LONGITUDE'], dict_loc[dict_sender[item_list[0]]]['LATITUDE'],
                                          dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'])
                                + haversine(dict_loc[dict_receiver[item_list[1]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[1]]]['LATITUDE'],
                                            dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'])
                                + haversine(dict_loc[dict_sender[item_list[2]]]['LONGITUDE'], dict_loc[dict_sender[item_list[2]]]['LATITUDE'],
                                            dict_loc[dict_receiver[item_list[3]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[3]]]['LATITUDE']))
                               * dict_operating_cost[item_list[4]])
                           for item_list in b]

            print("%s cost created" % (value_col))

            df_cost = pd.DataFrame(b, columns=cols)
            rows_before = len(df_cost)
            df_cost[value_col] = cost_values
            df_cost['t'] = time_values
            df_cost = df_cost[df_cost['t'] < 8]   # remove arc time greater than 8 hours
            cols_final = cols + [value_col]
            df_cost = df_cost[cols_final]
            rows_after = len(df_cost)
            print("")
            print("C_JKV NUMBER OF ROWS REMOVED: %s" % (rows_before - rows_after))
            print("")

            file = 'input_%s.csv' % (value_col)
            file_path = "%s%s" % (path_instance_input, file)
            file_path_tab = "%s%s" % (path_instance_input, input_c_jkjk_file_tab)
            df_cost.to_csv(file_path, index=False)
            df_cost.to_csv(file_path_tab, sep='\t', index=False)

            value_col = 'd_jkjkv'
            df_distance = pd.DataFrame(b, columns=cols)
            df_distance[value_col] = distance_values
            file = 'input_%s.csv' % (value_col)
            file_path = "%s%s" % (path_instance_input, file)
            df_distance.to_csv(file_path, index=False)

            print("-- %s CREATED" % (value_col))
            '''

    if formulation_type == 'arc':
        # print("-- SKIPPED: c_1")
    #     print("-- SKIPPED: c_2")
    #     pass
    # else:
        # --------------------------------------------
        # CREATE PARAMETER MATRIX - C_1 (index: ijkiv)
        # --------------------------------------------
        cols = ['stagingArea1', 'sender', 'receiver', 'vehicleType']
        final_cols = ['stagingArea1', 'sender', 'receiver', 'stagingArea2', 'vehicleType']
        value_col = 'c_1'
        final_cols.append(value_col)
        b = list(itertools.product(stagingAreaList, senderList, receiverList, ambulanceList))
        print("Length of %s: %s" % (value_col, len(b)))

        distance_values = [round(haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                           dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                                 + haversine(dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'],
                                             dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'])
                                 + haversine(dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'],
                                             dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE']), 2)
                           for item_list in b]

        time_values = [round((haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                                       dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                                             + haversine(dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'],
                                                         dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'])
                                             + haversine(dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'],
                                                         dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'])) / dict_velocity[item_list[3]]
                                        + dict_add_time[item_list[3]], 2)
                                       for item_list in b]


        cost_values = [int((haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                      dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                            + haversine(dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'],
                                        dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'])
                            + haversine(dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'],
                                        dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE']))
                           * dict_operating_cost[item_list[3]])
                       for item_list in b]

        df_cost = pd.DataFrame(b, columns=cols)
        df_cost['stagingArea2'] = df_cost['stagingArea1']
        df_cost['t_1'] = time_values
        df_cost[value_col] = cost_values
        final_cols = ['stagingArea1', 'sender', 'receiver', 'stagingArea2', 'vehicleType', 't_1', 'c_1']
        df_cost = df_cost[final_cols]  # rearrange column

        file = 'input_%s.csv' % (value_col)
        df_cost.to_csv(os.path.join(path_instance_input, file), index=False)
        df_cost.to_csv(os.path.join(path_instance_input, input_c1_file_tab), sep='\t', index=False)

        # save time dataframe
        final_cols = ['stagingArea1', 'sender', 'receiver', 'stagingArea2', 'vehicleType']
        value_col = 't_1'
        final_cols.append(value_col)
        df_time = pd.DataFrame(b, columns=cols)
        df_time['stagingArea2'] = df_time['stagingArea1']
        df_time[value_col] = time_values
        df_time = df_time[final_cols]
        file = 'input_%s.csv' % (value_col)
        df_time.to_csv(os.path.join(path_instance_input, file), index=False)

        # save distance dataframe
        final_cols = ['stagingArea1', 'sender', 'receiver', 'stagingArea2', 'vehicleType']
        value_col = 'd_1'
        final_cols.append(value_col)
        df_distance = pd.DataFrame(b, columns=cols)
        df_distance['stagingArea2'] = df_distance['stagingArea1']
        df_distance[value_col] = distance_values
        df_distance = df_distance[final_cols]  # rearrange column
        file = 'input_%s.csv' % (value_col)
        df_distance.to_csv(os.path.join(path_instance_input, file), index=False)

        print("-- %s CREATED" % (value_col))

        print("-- SKIPPED: c_2")
        '''
        if trip == 'single':
            print("-- SKIPPED: c_2")
            pass
        else:

            # --------------------------------------------
            # CREATE PARAMETER MATRIX - C_2 (index: ijkijkiv)
            # --------------------------------------------
            for stg in stagingAreaList:

                cols = ['stagingArea1', 'sender1', 'receiver1', 'sender2', 'receiver2', 'vehicleType']
                final_cols = ['stagingArea1', 'sender1', 'receiver1', 'stagingArea2', 'sender2', 'receiver2', 'stagingArea3', 'vehicleType']
                value_col = 'c_2'
                final_cols.append(value_col)
                print(len(senderList))
                print(len(receiverList))
                print(len(ambulanceList))
                print(len(stagingAreaList))
                print("Length of c_2: ", len(stagingAreaList) * len(senderList) * len(senderList) * len(receiverList) * len(receiverList) * len(ambulanceList))

                # b = list(itertools.product(stagingAreaList, senderList, receiverList, senderList, receiverList, ambulanceList))
                b = list(itertools.product(stg, senderList, receiverList, senderList, receiverList, ambulanceList))
                print("Length of %s: %s" % (value_col, len(b)))

                distance_values = [round(haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                                   dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                                         + haversine(dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'],
                                                     dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'])
                                         + haversine(dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'],
                                                     dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'])
                                         + haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                                     dict_loc[dict_sender[item_list[3]]]['LONGITUDE'], dict_loc[dict_sender[item_list[3]]]['LATITUDE'])
                                         + haversine(dict_loc[dict_sender[item_list[3]]]['LONGITUDE'], dict_loc[dict_sender[item_list[3]]]['LATITUDE'],
                                                     dict_loc[dict_receiver[item_list[4]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[4]]]['LATITUDE'])
                                         + haversine(dict_loc[dict_receiver[item_list[4]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[4]]]['LATITUDE'],
                                                     dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE']), 2)
                                   for item_list in b]

                cost_values = [int((haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                              dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'])
                                    + haversine(dict_loc[dict_sender[item_list[1]]]['LONGITUDE'], dict_loc[dict_sender[item_list[1]]]['LATITUDE'],
                                                dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'])
                                    + haversine(dict_loc[dict_receiver[item_list[2]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[2]]]['LATITUDE'],
                                                dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'])
                                    + haversine(dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE'],
                                                dict_loc[dict_sender[item_list[3]]]['LONGITUDE'], dict_loc[dict_sender[item_list[3]]]['LATITUDE'])
                                    + haversine(dict_loc[dict_sender[item_list[3]]]['LONGITUDE'], dict_loc[dict_sender[item_list[3]]]['LATITUDE'],
                                                dict_loc[dict_receiver[item_list[4]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[4]]]['LATITUDE'])
                                    + haversine(dict_loc[dict_receiver[item_list[4]]]['LONGITUDE'], dict_loc[dict_receiver[item_list[4]]]['LATITUDE'],
                                                dict_loc[dict_staging[item_list[0]]]['LONGITUDE'], dict_loc[dict_staging[item_list[0]]]['LATITUDE']))
                                   * dict_operating_cost[item_list[5]])
                               for item_list in b]

                df_cost = pd.DataFrame(b, columns=cols)
                df_cost['stagingArea2'] = df_cost['stagingArea1']
                df_cost['stagingArea3'] = df_cost['stagingArea1']
                df_cost[value_col] = cost_values
                df_cost = df_cost[final_cols]  # rearrange column

                # file = 'input_%s.csv' % (value_col)
                file = 'input_%s_%s.csv' % (value_col, stg)

                file_path = "%s%s" % (path_instance_input, file)
                file_path_tab = "%s%s" % (path_instance_input, input_c2_file_tab)
                df_cost.to_csv(file_path, index=False)
                df_cost.to_csv(file_path_tab, sep='\t', index=False)

                final_cols = ['stagingArea1', 'sender1', 'receiver1', 'stagingArea2', 'sender2', 'receiver2', 'stagingArea3', 'vehicleType']
                value_col = 'd_1'
                final_cols.append(value_col)
                df_distance = pd.DataFrame(b, columns=cols)
                df_distance['stagingArea2'] = df_distance['stagingArea1']
                df_distance['stagingArea3'] = df_distance['stagingArea1']
                df_distance[value_col] = distance_values
                df_distance = df_distance[final_cols]  # rearrange column

                # file = 'input_%s.csv' % (value_col)
                file = 'input_%s_%s.csv' % (value_col, stg)
                file_path = "%s%s" % (path_instance_input, file)
                df_distance.to_csv(file_path, index=False)

            print("-- %s CREATED" % (value_col))
        '''
