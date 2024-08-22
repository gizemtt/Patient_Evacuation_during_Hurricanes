import pandas as pd
from classes.scenario import Scenario
from choose_senders import senderGen
from tools.get_hospitals_paper import getHospitals

# ---------------------------------------------------------------------
# TWO FINAL OUTPUTS USED IN pelo_recourse.py
# 1) input_probability.tab: defines probabilities for each scenario
# 2) input_scenario.tab: defines each scenario name.
# 3) scenario_lookup.tab: used in generate_parameters_recourse.py
# ---------------------------------------------------------------------

def scenarioGen(dict_path, dict_parameter, instance_path):
    print("=====================")
    print("CHECK - PAPER VERSION")
    print("=====================")
    shelter = int(dict_parameter['shelter'])
    reduced_num_senders = dict_parameter['num_senders']
    matching_SLOSH = int(dict_parameter['matching_SLOSH'])
    current_scenario = int(dict_parameter['current_scenario'])
    check_mean_path = int(dict_parameter['check_mean_path'])
    mean_scenario = dict_parameter['mean_scenario']
    evpi = int(dict_parameter['evpi'])
    vss = int(dict_parameter['vss'])
    check_mean_scenario = int(dict_parameter['check_mean_scenario'])    # checking mean path
    check_EV = int(dict_parameter['check_EV'])  # checking expected demand

    print("DIRECTION MATCHING NWM: ", matching_SLOSH)
    print("")

    # DEFINE DEFAULT LOCATIONS
    path_instance_input = instance_path[0]
    path_instance_output = instance_path[1]

    # GET DEFAULT HOSPITALS
    list_hospitals = getHospitals(dict_path, dict_parameter, check_mean_scenario, shelter, reduced_num_senders, path_instance_input)
    stagingAreaList = list_hospitals[0].code.tolist()
    receiverList = list_hospitals[2].code.tolist()
    df_sender = list_hospitals[1]
    _senderList = df_sender.code.unique().tolist()
    senderList_default = sorted(_senderList)

    print('TOTAL NUMBER OF STG AREA: %s, RECEIVER: %s, SENDER: %s' % (len(stagingAreaList), len(receiverList), len(_senderList)))

    # ------------------------------
    # DEFINE SCENARIOS
    # ------------------------------
    # STEP 1: NWM SCENARIOS
    # get intersections from csv file
    path_track = dict_path['track']
    file_track = 'landfall_locations_hr10.csv'

    df_track = pd.read_csv(path_track + '\\landfall_locations_hr10.csv')
    df_track = df_track[df_track['location'] != 'reference']

    total_scenarios = int(dict_parameter['total_scenarios'])

    # Define stage per scenario dataframe
    stage_output_path = path_instance_input
    stage_output_file = 'df_sender.csv'
    df0 = pd.read_csv(stage_output_path + '\\df_sender.csv')

    if check_mean_scenario == 1:
        nwm_scenario_set = [mean_scenario]
    elif check_mean_path == 1:
        nwm_scenario_set = ['25-%s' % (current_scenario)]
    else:
        if (evpi == 1) or (vss == 1):
            nwm_scenario_set = ['25-%s' % (current_scenario)]
        else:
            nwm_scenario_set = ['25-%s' % (i + 1) for i in range(total_scenarios)]

    list_column = ['id', 'nid', 'code', 'dem', 'hand'] + nwm_scenario_set
    df_stage = df0[list_column]

    # determine probability of each NWM scenario
    dict_nwm_probability = {}
    for i in nwm_scenario_set:
        dict_nwm_probability[i] = 1 / len(nwm_scenario_set)

    # STEP 2: COMBINE NWM AND SLOSH
    slosh_category_set = dict_parameter['slosh_intensity'].split('/')
    slosh_tide_set = dict_parameter['slosh_tide'].split('/')

    slosh_scenario_set = []
    for j in slosh_category_set:
        for k in slosh_tide_set:
            this_scenario = [j, k]
            slosh_scenario_set.append(this_scenario)

    scenario_set = []
    for i in nwm_scenario_set:
        for j in slosh_scenario_set:
            this_slosh_direction = df_track[df_track['location'] == i]['direction'].tolist()[0]
            this_scenario_set = [this_slosh_direction, j[0], j[1], i]
            scenario_set.append(this_scenario_set)

    # - GET PROBABILITY FOR EACH SCENARIO
    dict_scenario_probability = {}
    for i in scenario_set:
        this_scenario_key = i[0] + i[1] + i[2] + '_' + i[3]
        this_nwm_scenario = i[3]
        this_slosh_scenario = i[0]
        this_probability = dict_nwm_probability[this_nwm_scenario]
        dict_scenario_probability[this_scenario_key] = this_probability

    # ------------------------------
    # DEFINE SCENARIOS PROBABILITIES
    # ------------------------------
    print('')
    print("NUMBER OF SCENARIOS TO GENERATE: ", len(scenario_set))
    print('CHECK SUM OF SCENARIO PROBABILITIES: ', sum(dict_scenario_probability.values()))
    print("")

    # ------------------------------------------
    # GET GRID NUMBER FOR HOSPITAL LOCATIONS
    # (THIS RESULT IS FROM RUNNING find_grid.py)
    # ------------------------------------------
    grid_file_location = dict_path['data']
    grid_file_name = 'location_grid_index.csv'

    #grid_file = grid_file_location + grid_file_name
    df_grid_index = pd.read_csv(grid_file_location + '\\location_grid_index.csv')
    dict_hospital_grid = dict(zip(df_grid_index['sender'], df_grid_index['Poly_id']))

    # ------------------------------
    # DEFINE SCENARIOS SET
    # ------------------------------
    # 1. name: scenario_number = ['n', '3', '05i2', '5-1']
    # 2. staging set
    # 3. sender set
    # 4. receiver set
    # 5. probability of scenario
    scenario_list_count = []
    scenarioSet = []
    scenario_count = 0
    list_list_waterlevel = []
    list_list_waterlevel_slosh = []
    list_list_waterlevel_nwm = []
    # list_scenario = []

    for i in scenario_set:
        scenario_count = scenario_count + 1
        print("    SCENARIO: ", scenario_count, " / ", len(scenario_set), " / ", i)
        newScenario = Scenario()
        scenario_key = i[0] + str(i[1]) + i[2] + '_' + i[3]
        inundated_set = senderGen(i, dict_hospital_grid, dict_path, dict_parameter, df_stage, df_sender)
        this_list_count = [i, len(inundated_set[0].keys()), len(inundated_set[1].keys()), len(inundated_set[2].keys())]
        inundated_dict_slosh = inundated_set[0]
        inundated_dict_nwm = inundated_set[1]
        inundated_dict = inundated_set[2] #1 for only inland flooding solution, 2for mix
        senders_affected = sorted(inundated_dict.keys())
        # newScenario.name = scenario_key
        if scenario_count <= 9:
            newScenario.name = 'n0%s' % (scenario_count)
        else:
            newScenario.name = 'n%s' % (scenario_count)
        newScenario.key = i
        newScenario.stagingset = stagingAreaList
        newScenario.receivingset = receiverList
        newScenario.senderset = senders_affected
        newScenario.probability = dict_scenario_probability[scenario_key]
        scenarioSet.append(newScenario)
        scenario_list_count.append(this_list_count)

        # CREATE A WATER HEIGHT DATAFRAME FROM SLOSH & NWM
        list_waterlevel = []
        list_waterlevel.append(scenario_key)
        for sender in senderList_default:
            if sender in inundated_dict.keys():
                waterlevel = round(inundated_dict[sender], 3)
            else:
                waterlevel = 0
            list_waterlevel.append(waterlevel)

        list_list_waterlevel.append(list_waterlevel)

        # CREATE A WATER HEIGHT DATAFRAME FROM SLOSH
        list_waterlevel_slosh = []
        list_waterlevel_slosh.append(scenario_key)
        for sender in senderList_default:
            if sender in inundated_dict_slosh.keys():
                waterlevel = round(inundated_dict_slosh[sender], 3)
            else:
                waterlevel = 0
            list_waterlevel_slosh.append(waterlevel)
        list_list_waterlevel_slosh.append(list_waterlevel_slosh)

        # CREATE A WATER HEIGHT DATAFRAME FROM NWM
        list_waterlevel_nwm = []
        list_waterlevel_nwm.append(scenario_key)
        for sender in senderList_default:
            if sender in inundated_dict_nwm.keys():
                waterlevel = round(inundated_dict_nwm[sender], 3)
            else:
                waterlevel = 0
            list_waterlevel_nwm.append(waterlevel)
        list_list_waterlevel_nwm.append(list_waterlevel_nwm)

    # write waterlevel dataframes to csv
    senderList_default.insert(0, 'scenario')
    df_waterlevel = pd.DataFrame(list_list_waterlevel, columns=senderList_default)
    waterlevel_file = 'water_height.csv'
    df_waterlevel.to_csv(path_instance_output +'\\water_height.csv')

    df_waterlevel_slosh = pd.DataFrame(list_list_waterlevel_slosh, columns=senderList_default)
    waterlevel_file = 'water_height_slosh.csv'
    df_waterlevel_slosh.to_csv(path_instance_output + 'water_height_slosh.csv')

    df_waterlevel_nwm = pd.DataFrame(list_list_waterlevel_nwm, columns=senderList_default)
    waterlevel_file = 'water_height_nwm.csv'
    df_waterlevel_nwm.to_csv(path_instance_output + '\\water_height_nwm.csv')

    print("")
    print('%s %s %s' % ("    Total ", len(scenarioSet), " scenarios generated"))
    print("")

    # write number of flooded locations into a csv file
    df_scenarios = pd.DataFrame(scenario_list_count)
    flooded_locations_per_scenario_file = 'flooded_locations_per_scenario.csv'
    df_scenarios.to_csv(path_instance_input + '\\flooded_locations_per_scenario.csv')

    # ----------------------------------------
    # --- DEFINE SCENARIO LOOKUP DATAFRAME ---
    # ----------------------------------------
    scenario_file_name = 'scenario_lookup.tab'
    scenarioOutput = open(path_instance_input + '\\scenario_lookup.tab', 'w')
    titleLine = "scenario" + "\t" + "sender" + "\t" + "multiplier" + "\n"
    scenarioOutput.write(titleLine)

    for i in range(len(scenarioSet)):
        if scenarioSet[i].probability != 0:
            for j in range(len(scenarioSet[i].senderset)):
                sender = scenarioSet[i].senderset[j]
                multiplier = 1
                newline = scenarioSet[i].name + "\t" + str(sender) + "\t" + str(multiplier) + "\n"
                scenarioOutput.write(newline)
        else:
            continue
    scenarioOutput.close()

    # -------------------------------------------------
    # --- CREATE PROBABILITY PER SCENARIO DATAFRAME ---
    # -------------------------------------------------
    probability_file_name_tab = 'input_probability.tab'
    scenario_file_name_tab = 'input_scenario.tab'
    probabilityOutput = open(path_instance_input + '\\input_probability.tab', 'w')
    scenarioSetOutput = open(path_instance_input + '\\input_scenario.tab', 'w')

    titleLine = "scenario" + "\t" + "probability" + "\n"
    titleLine_scenarioSet = "scenario" + "\n"

    probabilityOutput.write(titleLine)
    scenarioSetOutput.write(titleLine_scenarioSet)

    if check_EV != 1:

        for i in range(len(scenarioSet)):
            if scenarioSet[i].probability != 0:
                newline = scenarioSet[i].name + "\t" + str(scenarioSet[i].probability) + "\n"
                newline_scenarioSet = scenarioSet[i].name + "\n"
                probabilityOutput.write(newline)
                scenarioSetOutput.write(newline_scenarioSet)
            else:
                continue

    else:
        newline = 'n00' + "\t" + str(1) + "\n"
        newline_scenarioSet = 'n00' + "\n"
        probabilityOutput.write(newline)
        scenarioSetOutput.write(newline_scenarioSet)

    probabilityOutput.close()
    scenarioSetOutput.close()
