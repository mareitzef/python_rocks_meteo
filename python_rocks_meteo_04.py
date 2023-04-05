# Import Meteostat library and dependencies
# https://github.com/meteostat/meteostat-python
# https://openweathermap.org/api/one-call-3#how
# pip install plotly
# pip install meteostat
# pip install requests

import pandas as pd
from meteostat import Point, Daily, Hourly, Stations
from datetime import datetime, timedelta
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import plot
import requests
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
import webbrowser
import argparse
import sys

def get_meteostat_data(lat, lon, first_date, today):
    """
    Fetch hourly weather data from the closest Meteostat weather station.

    Args:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.
        first_date (datetime): The start date of the period to fetch.
        today (datetime): The end date of the period to fetch.

    Returns:
        A pandas DataFrame containing the hourly weather data.
    """
    stations = Stations().nearby(float(lat),float(lon))
    station = stations.fetch(1)

    point = Point(station['latitude'], station['longitude'], station['elevation'][0])
    data_hourly_Mstat = Hourly(point, first_date, today).fetch()

    return data_hourly_Mstat


def get_forecast_data(lat, lon, api_key):
    
    # Make API request
    response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric')
    
    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data_OWM = response.json()
        
        # Extract temperature and wind speed data
        temps = []
        humiditys = []
        wind_speeds = []
        timestamps = []
        rain_probabs = []
        rains = []
        for i in range(0,len(data_OWM['list'])):
            temp = data_OWM['list'][i]['main']['temp']
            humidity = data_OWM['list'][i]['main']['humidity']
            wind_speed = data_OWM['list'][i]['wind']['speed']*3.6
            timestamp = data_OWM['list'][i]['dt_txt']
            rain_probab = data_OWM['list'][i]['pop']*100
            try:
                rain = data_OWM['list'][i]['rain']['3h']
            except KeyError:
                rain = 0
     
            temps.append(temp)
            humiditys.append(humidity)
            wind_speeds.append(wind_speed)
            timestamps.append(timestamp)
            rain_probabs.append(rain_probab)
            rains.append(rain)
        
    else:
        print("Error: Request failed")

    return (temps,humiditys, wind_speeds, timestamps, rain_probabs, rains)




def main():
    ####################### Main Function - Settings: #####################################
    
    # Time period for the past 7 days
    today = datetime.today()
    #start date is one week before today 
    nr_days = 7
    first_date = (datetime.today() - timedelta(days=nr_days))
    # OpenWeatherMap API key
    api_key = "6545b0638b99383c1a278d3962506f4b"
    
    #check if there are arguments   
    if len(sys.argv) > 1:
        # create an ArgumentParser object
        parser = argparse.ArgumentParser(description='Get weather forecast from OpenWeatherMap API')
    
        # add arguments to the parser
        parser.add_argument('-a', '--api_key', help='OpenWeatherMap API key',default="6545b0638b99383c1a278d3962506f4b")
        #lat with CCC coordinates as default value
        parser.add_argument('-lat', '--latitude', help='Latitude of location', default='47.99305')
        parser.add_argument('-lon', '--longitude', help='Longitude of location',default='7.84068')
        parser.add_argument('-f', '--first_date', help='Set first day to plot past weather',default=first_date)
        parser.add_argument('-l', '--last_date', help='Set last day to plot past weather',default=today)
        # add input variable number_of_days to parser
        parser.add_argument('-n', '--number_of_days', help='Number of days into the  past to plot',default=nr_days)
    
        # parse the command-line arguments
        args = parser.parse_args()
        # write args into lat and lon if empty
        #convert lat to datetime
        lat = args.latitude
        lon = args.longitude
        api_key = args.api_key
        first_date = datetime.strptime(args.first_date, '%Y-%m-%d')
        # if there is argment in number_of_days, replace first_date with (datetime.today() - timedelta(days=nr_days))
        if args.number_of_days:
            nr_days = int(args.number_of_days)
            first_date = (datetime.today() - timedelta(days=nr_days))
            first_date = datetime.strptime(args.first_date, '%Y-%m-%d')

    else:
        #use default values
        # Kühtai 
        #lat = '47.210925591216'
        #lon = '11.009436247238742'
        lat = '47.99305'
        lon = '7.84068'
        api_key = '6545b0638b99383c1a278d3962506f4b'


    temps,humiditys, wind_speeds, timestamps, rain_probabs, rains = get_forecast_data(lat, lon, api_key)
    
    ####################### Main Function - Plots: #####################################
    
    data_hourly_Mstat = get_meteostat_data(lat, lon, first_date, today)
    
    # Plot hourly data
    # Create a figure with two subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
    #fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['dwpt'], name='Hourly Dewpoint Temperature', opacity=0.9, marker=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['temp'], name='Hourly Temperature', marker=dict(color='red')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['rhum'], name='Hourly Humidity', line=dict(width=1, dash='dot'),marker=dict(color='grey')), row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False, row=1, col=1)
    fig.update_yaxes(title_text="Humidity (%)", secondary_y=True, row=1, col=1)
    
    fig.add_trace(go.Bar(x=data_hourly_Mstat.index, y=data_hourly_Mstat['prcp'], name='Hourly Precipitation',  marker=dict(color='blue')), row=2, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['wspd'], name='Wind Speed',opacity=1, line=dict(width=1.2, dash='dot'),marker=dict(color='red')), row=2, col=1)
    fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
    # if length of data_hourly_Mstat['prcp'] is 0, set range to 0,1
    if len(data_hourly_Mstat['prcp']) == 0:
        fig.update_yaxes(title_text="Precipitation (mm)", secondary_y=True, row=2, col=1, range=[0, 1])
    else:
        fig.update_yaxes(title_text="Precipitation (mm)", secondary_y=True, row=2, col=1, range=[0, max(data_hourly_Mstat['prcp'])+1])
    fig.update_layout(title='Historic Data - Meteostat', height=600)
    
    # Create a figure with two subplots
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,specs=[[{"secondary_y": True}],[{"secondary_y": True}]])
    # Add traces for temperature and wind speed to the first subplot
    fig2.add_trace(go.Scatter(x=timestamps, y=temps, name="Temperature",marker=dict(color='red')), row=1, col=1)
    fig2.add_trace(go.Scatter(x=timestamps, y=humiditys, name='Humidity', line=dict(width=1, dash='dot'),marker=dict(color='grey')), row=1, col=1, secondary_y=True)
   # Set the y-axis titles for the subplots
    fig2.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig2.update_yaxes(title_text="Humidity (%)", secondary_y=True, row=1, col=1)

    # for i, p in enumerate(rain_probabs):
    #     opac = p/100 # update only the first subplot
    # color='rgba(100,0,255,'+opac+')'

    # Add a trace for precipitation to the second subplot
    fig2.add_trace(go.Bar(x=timestamps, y=rains, name='3-Hourly Precipitation',opacity=0.7,marker=dict(color='blue')), row=2, col=1)
    # Add a trace for wind speed to the second subplot
    fig2.add_trace(go.Scatter(x=timestamps, y=wind_speeds, name="Wind Speed",opacity=1, line=dict(width=1.2, dash='dot'),marker=dict(color='red')), row=2, col=1, secondary_y=True)
    # Set the y-axis titles for the subplots
    fig2.update_yaxes(title_text="Precipitation (mm/3h)", row=2, col=1, range=[0, max(rains)+max(rains)*0.15])
    fig2.update_yaxes(title_text="Wind Speed (km/h)", secondary_y=True, row=2, col=1, range=[0, max(wind_speeds)+1])
    # add precipitation probability to second subplot as text on top of the bars
    for i in range(len(rain_probabs)):
        fig2.add_annotation(x=timestamps[i], y=max(rains)+max(rains)*0.1, text=str(int(round(rain_probabs[i])))+"%", showarrow=False, font=dict(color="grey",size=10), row=2, col=1)
    
    # for i, p in enumerate(rain_probabs):
    #     if p < 33:
    #         color = 'rgba(173, 216, 230, ' + str(p/100) + ')'
    #     elif p >= 33 and p < 67:
    #         color = 'rgba(0, 0, 255, ' + str(p/100) + ')'
    #     else:
    #         color = 'rgba(0, 0, 139, ' + str(p/100) + ')'
    #     fig2.data[1].marker.color[i] = color



    # Update the layout of the figure
    fig2.update_layout(title="Openweathermap Forecast", height=600)
    
    # Get the HTML code for each plot
    plot1_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    plot2_html = fig2.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Load the HTML template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template.html")
    
    # Render the template with the plots' HTML
    html_output = template.render(plot1=plot1_html, plot2=plot2_html)
    
    # Write the output to an HTML file
    with open("Meteostat_and_openweathermap.html", "w") as f:
        f.write(html_output)

    filename = 'Meteostat_and_openweathermap.html'
    webbrowser.open_new_tab(filename)


if __name__ == '__main__':
    main()

