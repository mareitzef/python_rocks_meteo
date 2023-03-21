# Import Meteostat library and dependencies
# https://github.com/meteostat/meteostat-python
# https://openweathermap.org/api/one-call-3#how
# pip install plotly
# pip install meteostat
# pip install requests

import pandas as pd
from meteostat import Point, Daily, Hourly, Stations
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import plot
import requests
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
import webbrowser

def get_meteostat_data(lat, lon, start_date, end_date):
    """
    Fetch hourly weather data from the closest Meteostat weather station.

    Args:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.
        start_date (datetime): The start date of the period to fetch.
        end_date (datetime): The end date of the period to fetch.

    Returns:
        A pandas DataFrame containing the hourly weather data.
    """
    stations = Stations().nearby(float(lat),float(lon))
    station = stations.fetch(1)

    point = Point(station['latitude'], station['longitude'], 250)
    data_hourly_Mstat = Hourly(point, start_date, end_date).fetch()

    return data_hourly_Mstat


def get_weather_data(lat, lon, api_key):
    
    # Make API request
    response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric')
    
    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data_OWM = response.json()
        
        # Extract temperature and wind speed data
        temps = []
        wind_speeds = []
        timestamps = []
        rain_probabs = []
        rains = []
        for i in range(0,len(data_OWM['list'])):
            temp = data_OWM['list'][i]['main']['temp']
            wind_speed = data_OWM['list'][i]['wind']['speed']*3.6
            timestamp = data_OWM['list'][i]['dt_txt']
            rain_probab = data_OWM['list'][i]['pop']*100
            try:
                rain = data_OWM['list'][i]['rain']['3h']
            except KeyError:
                rain = 0
     
            temps.append(temp)
            wind_speeds.append(wind_speed)
            timestamps.append(timestamp)
            rain_probabs.append(rain_probab)
            rains.append(rain)
        
    else:
        print("Error: Request failed")

    return (temps, wind_speeds, timestamps, rain_probabs, rains)




def main():
    ####################### Main Function - Settings: #####################################
        
    # CCC coordinates
    lat = "47.99305"
    lon = "7.84068"
    # Time period for the past
    start_date = datetime(2023, 3, 1)
    end_date = datetime(2023, 3, 18)
    
    api_key = "6545b0638b99383c1a278d3962506f4b"
    
    temps, wind_speeds, timestamps, rain_probabs, rains = get_weather_data(lat, lon, api_key)
    
    
    ####################### Main Function - Plots: #####################################
    
    data_hourly_Mstat = get_meteostat_data(lat, lon, start_date, end_date)
    
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
    fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['wspd'], name='Wind Speed',opacity=0.7, line=dict(width=1, dash='dot'),marker=dict(color='red')), row=2, col=1)
    fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
    fig.update_yaxes(title_text="Precipitation (mm)", secondary_y=True, row=2, col=1, range=[0, max(data_hourly_Mstat['prcp'])+1])
    fig.update_layout(title='Historic Data - Meteostat', height=600)
    #plot(fig, filename='Meteostat.html', auto_open=True)
    
    # Create a figure with two subplots
    fig2 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,specs=[[{}],[{}],[{"secondary_y": True}]])
    # Add traces for temperature and wind speed to the first subplot
    fig2.add_trace(go.Scatter(x=timestamps, y=temps, name="Temperature",marker=dict(color='green')), row=1, col=1)
    # Add a trace for wind speed to the second subplot
    fig2.add_trace(go.Scatter(x=timestamps, y=wind_speeds, name="Wind Speed",opacity=0.7, line=dict(width=1, dash='dot'),marker=dict(color='pink')), row=2, col=1)
    # Set the y-axis titles for the subplots
    fig2.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig2.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
    
    fig2.add_trace(go.Bar(x=timestamps, y=rains, name='3-Hourly Precipitation',opacity=0.5,marker=dict(color='black')), row=3, col=1)
    fig2.add_trace(go.Scatter(x=timestamps, y=rain_probabs, name='Precipitation Probability',opacity=0.7, line=dict(width=1),marker=dict(color='yellow')), row=3, col=1, secondary_y=True)
    fig2.update_yaxes(title_text="Precipitation (mm/3h)", row=3, col=1, range=[0, max(rains)+1])
    fig2.update_yaxes(title_text="Precipitation Probability (%)", secondary_y=True, row=3, col=1, range=[0, 100])
    
    # Update the layout of the figure
    fig2.update_layout(title="Openweathermap Forecast", height=600)
    
    # Save the plots
    #plot(fig2, filename='openweathermap.html', auto_open=True)
    
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

