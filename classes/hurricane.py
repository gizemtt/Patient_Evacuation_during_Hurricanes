class Hurricane:
    def __init__(self, impactLocation=None, impactCategory=None, impactSize=None, radius=None, impactLeadTime=None, minPressure=None, maxWindSpeed=None):
        self.impactLocation = impactLocation
        self.radius = radius
        self.impactLeadTime = impactLeadTime
        self.minPressure = minPressure
        self.maxWindSpeed = maxWindSpeed

    def windCategory(self, input):
        if 0 < input <= 34:
            self.impactCategory = 0
        elif 34 < input <= 50:
            self.impactCategory = 1
        elif 50 < input <= 64:
            self.impactCategory = 2
        elif 64 < input:
            self.impactCategory = 3

    def impactSize(self, input):
        if 0 <= input < 20:
            self.impactSize = 0
        elif 20 <= input < 40:
            self.impactSize = 1
        elif 40 <= input:
            self.impactSize = 2
