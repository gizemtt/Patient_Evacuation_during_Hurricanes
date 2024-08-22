# import geocoding_for_kml
import csv
# import xml.dom.minidom
# import sys
import pandas as pd


# Input the file name."JoeDupes3_forearth"
# fname = input("Enter file name WITHOUT extension: ")
# data = csv.reader(open(fname + '.csv'), delimiter=',')


path = '/Users/kyoung/Box Sync/github/data/gov/'
file_name = 'Hospitals_setrac'
extension = '.csv'
df = pd.read_csv(path + file_name + extension)

# Open the file to be written.
kml_file = 'test2.kml'
f = open(path + kml_file, 'w')

# Writing the kml file.
f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
# f.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
f.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
f.write("<Document>\n")
f.write("   <name>" + file_name + '.kml' + "</name>\n")

for i in range(len(df)):
    f.write("   <Placemark>\n")
    f.write("       <name>" + str(df.iloc[i]['NAME']) + "</name>\n")
    f.write("       <description>" + str(df.iloc[i]['TYPE']) + "</description>\n")
    f.write("       <Point>\n")
    f.write("           <coordinates>" + str(df.iloc[i]['LONGITUDE']) + "," + str(df.iloc[i]['LATITUDE']) + "," + str() + "</coordinates>\n")
    f.write("       </Point>\n")
    f.write("   </Placemark>\n")
f.write("</Document>\n")
f.write("</kml>\n")

print("File Created. ")
f.close()


'''
def extractAddress(row):
    # This extracts an address from a row and returns it as a string. This requires knowing
    # ahead of time what the columns are that hold the address information.
    return '%s,%s,%s,%s,%s' % (row['Address1'], row['Address2'], row['City'], row['State'], row['Zip'])


def createPlacemark(kmlDoc, row, order):
    # This creates a  element for a row of data.
    # A row is a dict.
    placemarkElement = kmlDoc.createElement('Placemark')
    extElement = kmlDoc.createElement('ExtendedData')
    placemarkElement.appendChild(extElement)
    # Loop through the columns and create a  element for every field that has a value.
    for key in order:
        if row[key]:
            dataElement = kmlDoc.createElement('Data')
            dataElement.setAttribute('name', key)
            valueElement = kmlDoc.createElement('value')
            dataElement.appendChild(valueElement)
            valueText = kmlDoc.createTextNode(row[key])
            valueElement.appendChild(valueText)
            extElement.appendChild(dataElement)

    pointElement = kmlDoc.createElement('Point')
    placemarkElement.appendChild(pointElement)
    coordinates = geocoding_for_kml.geocode(extractAddress(row))
    coorElement = kmlDoc.createElement('coordinates')
    coorElement.appendChild(kmlDoc.createTextNode(coordinates))
    pointElement.appendChild(coorElement)

    return placemarkElement

def createKML(csvReader, fileName, order):
    # This constructs the KML document from the CSV file.
    kmlDoc = xml.dom.minidom.Document()

    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns', 'http://earth.google.com/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    # Skip the header line.
    csvReader.next()

    for row in csvReader:
        placemarkElement = createPlacemark(kmlDoc, row, order)
        documentElement.appendChild(placemarkElement)
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml('  ', newl='\n', encoding='utf-8'))

def main():
    # This reader opens up 'google-addresses.csv', which should be replaced with your own.
    # It creates a KML file called 'google.kml'.

    # If an argument was passed to the script, it splits the argument on a comma
    # and uses the resulting list to specify an order for when columns get added.
    # Otherwise, it defaults to the order used in the sample.

    if len(sys.argv) > 1:
        order = sys.argv[1].split(',')
    else:
        order = ['Office', 'Address1', 'Address2', 'Address3', 'City', 'State', 'Zip', 'Phone', 'Fax']

    csvreader = csv.DictReader(open('google-addresses.csv'), order)
    kml = createKML(csvreader, 'google-addresses.kml', order)

if __name__ == '__main__':
    main()
'''
