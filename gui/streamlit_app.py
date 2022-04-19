import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as soup
import cfscrape
import json
import csv
import datetime
from datetime import timedelta
import time
import numpy as np
from streamlit_lottie import st_lottie
import plotly.graph_objects as go
import pydeck as pdk


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(
    page_title="Flight info app",
    layout="wide",
)

st.title('Flight status report')

# load lottie animation
lottie_logo_url = 'https://assets9.lottiefiles.com/packages/lf20_jlmgqgx2.json'
lottie_logo_icon = load_lottieurl(lottie_logo_url)
st_lottie(lottie_logo_icon, speed=1, height=200, key='initial')

lottie_route_url = 'https://assets1.lottiefiles.com/packages/lf20_fo9dd5nw.json'
# lottie_route_url = 'https://assets1.lottiefiles.com/packages/lf20_vbmp7ua7.json'
lottie__route_icon = load_lottieurl(lottie_route_url)


# get the flight code provided by the user
flight_code = st.text_input('Flight code', 'a3540')


print('------------'+flight_code+'------------')
flight_code_url = 'https://www.flightradar24.com/data/flights/'+flight_code

# take the page
scraper = cfscrape.create_scraper(delay=30)
raw_html = scraper.get(flight_code_url).content
scraper.close()

# parse contents to html
page_soup = soup(raw_html, "html.parser")

# get all the data-row trs
data_container = page_soup.findAll("tr", {"class": "data-row"})


std_per_flight = []
atd_per_flight = []
departure_diff_per_time = []
sta_per_flight = []
ata_per_flight = []
arrival_diff_per_time = []
canceled_flights_counter = 0
flight_duration_per_flight = []

departure_city = data_container[0].findAll("td")[3]['title']
departure_airport_code = data_container[0].findAll("td")[3].findAll("a")[0].text
arrival_city = data_container[0].findAll("td")[4]['title']
arrival_airport_code = data_container[0].findAll("td")[4].findAll("a")[0].text

st.markdown("""---""")

st.header('Route info')
cols_1 = [i for i in st.columns([1,2,1])]
cols_1[0].subheader(departure_city)

with cols_1[1]:
    st_lottie(lottie__route_icon, speed=1, height=150)

cols_1[2].subheader(arrival_city)    

for row_container in data_container:
    row_tds = row_container.findAll("td")
    row_date_text = row_tds[2].text.strip()
    print(row_date_text)
    if row_tds[11].text.strip() == 'Canceled':
        print('  flight cancelled')
        canceled_flights_counter += 1
    elif row_tds[11].text.strip() == 'Scheduled':
        print('  flight not yet started')
        pass
    elif 'Estimated' in row_tds[11].text.strip():
        print('  This flight will begin shortly')
    else:
        flight_duration_per_flight.append(row_tds[6].text.strip())
        print('  flight_duration_per_flight: '+str(flight_duration_per_flight[-1]))
        std_per_flight.append(datetime.datetime.fromtimestamp(int(row_tds[7]['data-timestamp'])))
        print('  std_per_flight: '+str(std_per_flight[-1]))
        atd_per_flight.append(datetime.datetime.fromtimestamp(int(row_tds[8]['data-timestamp'])))
        print('  atd_per_flight: '+str(atd_per_flight[-1]))
        sta_per_flight.append(datetime.datetime.fromtimestamp(int(row_tds[9]['data-timestamp'])))
        print('  sta_per_flight: '+str(sta_per_flight[-1]))
        ata_per_flight.append(datetime.datetime.fromtimestamp(int(row_tds[11]['data-timestamp'])))
        print('  ata_per_flight: '+str(ata_per_flight[-1]))


        departure_diff_per_time.append((std_per_flight[-1] - atd_per_flight[-1]).total_seconds()) 
        arrival_diff_per_time.append((sta_per_flight[-1] - ata_per_flight[-1]).total_seconds())

st.markdown("""---""")
st.header('Latest flights')
explanation_text = """
* **std**: scheduled time of departure
* **atd**: actuall time of departure
* **sta**: scheduled time of arrival
* **ata**: actuall time of arrival 
* **departure diff**: std - atd
* **arrival diff**: sta - ata
"""
with st.expander("See column explanations"):
    st.markdown(explanation_text)
df = pd.DataFrame(list(zip(std_per_flight, atd_per_flight, sta_per_flight, ata_per_flight, departure_diff_per_time, arrival_diff_per_time)), columns=['std', 'atd', 'sta', 'ata', 'departure_diff', 'arivall_diff'])
st.dataframe(df)

st.markdown("""---""")
cols_2 = [i for i in st.columns([1,4])]
cols_2[0].metric("Average departure delay", str(std_per_flight[0].time()), str(round(-1*np.mean(departure_diff_per_time),2))+' sec', delta_color='inverse')
fig2 = go.Figure([go.Scatter(x=df['std'].dt.date, y=np.abs(df['departure_diff']))])
cols_2[1].plotly_chart(fig2, use_container_width=True)

st.markdown("""---""")
cols_3 = [i for i in st.columns([1,4])]
cols_3[0].metric("Average arrival delay", str(sta_per_flight[0].time()), str(round(-1*np.mean(arrival_diff_per_time),2))+' sec', delta_color='inverse')
fig3 = go.Figure([go.Scatter(x=df['sta'].dt.date, y=np.abs(df['arivall_diff']))])
cols_3[1].plotly_chart(fig3, use_container_width=True)