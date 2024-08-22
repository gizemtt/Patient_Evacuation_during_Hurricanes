import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates


print('Beginning file download with urllib2...')


destination = '/Users/kyoung/Box Sync/github/pelo/weather_data/'
url = 'https://water.weather.gov/ahps2/rss/obs/cust2.rss'
file_name = 'feed.csv'

url2 = 'https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=cust2&output=tabular&time_zone=cst'
url3 = 'https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=glit2&output=tabular&time_zone=cst'

header = ['Date', 'Stage', 'Flow']
weather = pd.read_html(url2, header=0)

for i in range(1, len(weather)):
    df = weather[i]
    df = df[1:]
    df = df.reset_index(drop=True)
    df.columns = header
    df.Stage = df.Stage.map(lambda x: str(x)[:-2])
    unit_stage = 'ft'
    if df.Flow[1][-4:] == 'kcfs':
        df.Flow = df.Flow.map(lambda x: str(x)[:-4])
        unit_flow = 'kcfs'
    else:
        df.Flow = df.Flow.map(lambda x: str(x)[:-3])
        unit_flow = 'cfs'
    df.Stage = pd.to_numeric(df.Stage)
    df.Flow = pd.to_numeric(df.Flow)

    if i == 1:
        observed = df
    elif i == 2:
        forecasted = df

try:
    forecasted
except NameError:
    frames = [observed]
else:
    frames = [observed, forecasted]

this_df = pd.concat(frames)
this_df = this_df.sort_values(by='Date')
this_df = this_df.reset_index(drop=True)

dates_list = this_df.Date
x = [dt.datetime.strptime(date, "%m/%d %H:%M") for date in dates_list]
y = this_df.Stage


days = mdates.DayLocator()
hours = mdates.HourLocator(range(0, 25, 6))
myFmt = mdates.DateFormatter('%m/%d')

fig, ax = plt.subplots()
ax.plot(x, y)
# ax.xaxis.set_major_locator(days)
# ax.xaxis.set_minor_locator(hours)
ax.xaxis.set_major_formatter(myFmt)
plt.show()
