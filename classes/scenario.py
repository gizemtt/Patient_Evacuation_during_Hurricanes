class Scenario:
    def __init__(self, zoneNum=None, name=None, probability=None, receiverset=None, senderList=None,
                 stagingareaset=None, leadtime=None, impactCategory=None, coordinate=None, stormSize=None,
                 regionalWindSpeed=None, numRegions=None, spanRegions=None, key=None):
        self.zoneNum = zoneNum
        self.impactCategory = impactCategory
        self.numRegions = numRegions
        self.stormSize = stormSize
        self.name = name
        self.probability = probability
        self.coordinate = coordinate
        self.receiverset = receiverset
        self.stagingset = stagingareaset
        self.leadtime = leadtime
        self.spanRegions = spanRegions
        self.key = key

    def regionalWindSpeedCalc(self, input):
        if input == 3:
            self.regionalWindSpeed = [64, 50, 34, 17]
        elif input == 2:
            self.regionalWindSpeed = [50, 34, 17]
        elif input == 1:
            self.regionalWindSpeed = [34, 17]
        elif input == 0:
            self.regionalWindSpeed = [17]

    def senderSetCalc(self, input):
        self.senderList = []
        for i in range(input):
            self.senderList.append([])
