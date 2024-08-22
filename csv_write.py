import csv

def writeResult(list_var, _output_directory):
    output_directory = _output_directory

    for var in list_var:
        row_list = []
        thisvarobject = dict((index, value.x) for index, value in var.items() if value.x > 0)

        for key in thisvarobject.keys():
            thisrow = [i for i in key]
            thisrow.append(var[key].x)
            row_list.append(thisrow)

        file_name = 'result_' + str(var) + '.csv'
        with open(output_directory + file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(row_list)
