import os

def createHtml(path_csv, path_html, input_csv):

    csv_file = input_csv + '.csv'
    html_file = input_csv + '.html'

    filein = open(path_csv + csv_file, "r")
    fileout = open(path_html + html_file, "w")
    data = filein.readlines()

    table = "<table>\n"

    # Create the table's column headers
    header = data[0].split(",")
    header = ['type', 'location']
    table += "  <tr>\n"
    for column in header:
        table += "    <th>{0}</th>\n".format(column.strip())
    table += "  </tr>\n"

    # Create the table's row data
    for line in data[0:]:
        row = line.split(",")
        table += "  <tr>\n"
        for column in row:
            table += "    <td>{0}</td>\n".format(column.strip())
        table += "  </tr>\n"

    table += "</table>"

    fileout.writelines(table)
    fileout.close()
    filein.close()
