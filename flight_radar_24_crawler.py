import os
os.environ["PROJ_LIB"] = os.path.join(os.environ["CONDA_PREFIX"], "share", "proj")
import pandas as pd
from bs4 import BeautifulSoup as soup
import cfscrape
import json
import csv
import networkx as nx
import datetime
import glob
import network_visualizer
import datetime
from datetime import timedelta
import time
import numpy as np
from tqdm import tqdm
from folium import Map
from folium.plugins import HeatMap
import cloudscraper


def main():
    choice = input("Plot a newly crawled route network (y/n): ")
    if choice == 'y':
        output_file_name = routes_crawler()
    elif choice == 'n':
        print('These are the available cralwed route networks')
        files_list = glob.glob("routes_data/*.csv")
        for index, file_name in enumerate(files_list):
            print(str(index) + ') ' + file_name)
        try:
            file_index = int(input("Choose the index of the file you want to plot: "))
        except ValueError:
            print('Problem with the input type. By default using the last crawled route network')
            file_index = len(files_list)-1

        try:
            output_file_name = files_list[file_index]
        except IndexError:
            print('Problem with the index. By default using the last crawled route network')
            output_file_name = files_list[-1]

    plot_airport_network(output_file_name)


def airports_crawler(scraper_bypasser='cloudscraper'):
    # load the csv with the european airport codes
    df = pd.read_csv('airports_data/european_airports.csv', sep=',')
    target_list = []
    name_list = []
    city_list = []
    lon_list = []
    lat_list = []
    country_list = []

    # for every airport code in the dataframe we loeaded get the location where you can fly to and from
    counter = 0
    for code in df.IATA:
        counter +=1
        print(str(counter)+') Crawling on '+str(code))
        # open up connection
        airport_url = 'https://www.flightradar24.com/data/airports/'+str(code)+'/routes'
        # take the page

        if scraper_bypasser == 'cfscrape':
            scraper = cfscrape.create_scraper()
        else:
            scraper = cloudscraper.create_scraper()
        raw_html = scraper.get(airport_url).content
        scraper.close()
        # parse contents to html
        page_soup = soup(raw_html, "html.parser")
        print('     ' + page_soup.title.string.encode('utf-8'))

        # get all the script tags
        destinations_container = page_soup.findAll("script")
        # find the specific script that contains all the routes
        for tag in destinations_container:
            # tag = tag.encode('utf-8')
            tag = str(tag)

            if (tag.startswith('<script>var arrRoutes')):
                start = tag.find('[')
                finish = tag.find(']')
                destinations_list = json.loads(tag[start:finish+1])

        for i in destinations_list:
            if i['iata'] != None:
                if i['iata'] not in target_list:
                    print('New airport: '+i['iata'])
                    city_list.append(i['city'])
                    name_list.append(i['name'])
                    country_list.append(i['country'])
                    target_list.append(i['iata'])
                    lon_list.append(i['lon'])
                    lat_list.append(i['lat'])
            else:
                print('This airport has no iata code registered :'+i['icao'])

    # create a new dataframe to store all the routes we get from crawling the website www.world-airport-codes.com
    airports_df = pd.DataFrame({#'Origin': source_list,
                              'Label': target_list,
                              'Name': name_list,
                              'Country': country_list,
                              'City': city_list,
                              'longitude': lon_list,
                              'latitude': lat_list})
    airports_df.to_csv('airports_data/flight_radar_24_airports.csv', sep=',')


def routes_crawler(scraper_bypasser='cloudscraper', starting_airport=None, verbose=True, num_attempts=10):

    now = datetime.datetime.now()
    current_day, current_month, current_year = str(now.day), str(now.month), str(now.year)

    # load the csv with the european airport codes
    df = pd.read_csv('airports_data/european_airports.csv', sep=',')

    df2 = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    airports_list = df2['Label'].tolist() #extract the iata code of every airport

    source_airport_list = []
    target_airport_list = []
    number_of_flights_list = []

    # for every airport code in the dataframe we loeaded get the location where you can fly to
    remaining_airports_list = []
    if starting_airport is not None:
        remaining_airports_list = df.loc[df.loc[df['IATA'] == starting_airport].index[0]:].IATA
    else:
        remaining_airports_list = df.IATA

    for counter, airport_code in enumerate(remaining_airports_list):
        print(50*"=")
        print(str(counter) + ') Crawling on ' + str(airport_code))
        time.sleep(10)
        print('sleeping...')
        print(50*"=")

        # open up connection
        airport_fr_url = 'https://www.flightradar24.com/data/airports/' + str(airport_code) + '/routes'
        
        # take the page
        if scraper_bypasser == 'cfscrape':
            scraper = cfscrape.create_scraper()
        else:
            scraper = cloudscraper.create_scraper()

        raw_html = scraper.get(airport_fr_url).content
        scraper.close()
        # parse contents to html
        page_soup = soup(raw_html, "html.parser")
        print('     ' + page_soup.title.string)

        # get all the script tags
        destinations_container = page_soup.findAll("script")
        # find the specific script that contains all the destination airport data
        for tag in destinations_container:
            tag = str(tag)
            if tag.startswith('<script>var arrRoutes'):
                start = tag.find('[')
                finish = tag.find(']')
                destinations_list = json.loads(tag[start:finish + 1])

        if verbose:
            print('checking '+str(len(destinations_list))+' routes')
            # print('destinations_list: '+str(destinations_list))

        for destination_count, destination in enumerate(tqdm(destinations_list)):
            if verbose:
                print('')
            time.sleep(5)
            if verbose:
                print(str(destination_count)+')  sleeping...')
                print()
            if destination['iata'] != None:
                if verbose:
                    # print('destination["iata"] != None : '+str(destination['iata'] != None))
                    # print('destination["iata"] in airports_list : '+str(destination['iata'] in airports_list))
                    # print('str(airport_code) in airports_list : '+str(str(airport_code) in airports_list))
                    pass
                if destination['iata'] in airports_list and str(airport_code) in airports_list:

                    print(str(airport_code) + ' <- -> ' + destination['iata'])
                    json_url = airport_fr_url + '?get-airport-arr-dep='+destination['iata']+'&format=json'
                    for attempt_no in range(num_attempts):
                        try:
                            if scraper_bypasser == 'cfscrape':
                                scraper = cfscrape.create_scraper(delay=30)
                            else:
                                scraper = cloudscraper.create_scraper(delay=30)
                            json_response = json.loads(scraper.get(json_url).content)
                            scraper.close()
                            break
                        except:
                            time.sleep(30)
                            print('ERROR PARSING JSON FILE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

                    if json_response: #check if the json is not empty
                        try:
                            for m in ['arrivals', 'departures']:
                                number_of_flights = 0
                                flights = list(list(json_response[m].values())[0]['airports'].values())[0]['flights']
                                if verbose:
                                    # print('m: '+str(m))
                                    # print('list(json_response[m].values()): '+str(list(json_response[m].values())))
                                    # print('list(list(json_response[m].values())[0]["airports"].values())'+str(list(list(json_response[m].values())[0]['airports'].values())))
                                    # print('flights'+str(flights))
                                    pass
                                for flight in flights.values():
                                    hours = flight['utc']
                                    number_of_flights += len(hours)
                                    if verbose:
                                        # print('hours: '+str(hours))
                                        # print('number_of_flights: '+str(number_of_flights))
                                        pass
                                number_of_flights_list.append(number_of_flights)
                                airport_1_code = airports_list.index(destination['iata'])
                                airport_2_code = airports_list.index(str(airport_code))

                                if verbose:
                                    # print('number_of_flights_list: '+str(number_of_flights_list))
                                    # print('destination["iata"]: '+str(destination['iata']))
                                    # print('airport_1_code: '+str(airport_1_code))
                                    # print('str(airport_code): '+str(airport_code))
                                    # print('airport_2_code: '+str(airport_2_code))
                                    pass
                                if m == 'arrivals':
                                    if verbose:
                                        print('Arrivals     '+str(number_of_flights)+' flights')
                                    source_airport_list.append(airport_1_code)
                                    target_airport_list.append(airport_2_code)
                                else:
                                    if verbose:
                                        print('Departures   '+str(number_of_flights) + ' flights')
                                    target_airport_list.append(airport_1_code)
                                    source_airport_list.append(airport_2_code)
                        except KeyError:
                            if verbose:
                                print('THERE ARE NOT DIRECT FLIGHTS')
                    else:
                        if verbose:
                            print('DOES NOT HAVE ANY FLIGHTS!!!')
            else:
                if verbose:
                    print('This airport has no iata code registered :' + destination['icao'])
        print('=======================================================================================================')
    routes_df = pd.DataFrame({'Source': source_airport_list, 'Target': target_airport_list, 'Weight': number_of_flights_list})
    now = datetime.datetime.now()
    output_file_name = 'routes_data/flight_radar_24_routes_with_weights_and_bi_direct_'+current_day+'_'+current_month+'_'+current_year+'.csv'
    routes_df.to_csv(output_file_name, sep=',')
    return output_file_name


def get_flight_codes():

    # load the csv with the european airport codes
    df = pd.read_csv('airports_data/european_airports.csv', sep=',')

    df2 = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    airports_list = df2['Label'].tolist() #extract the iata code of every airport

    flight_codes_list = []

    # for every airport code in the dataframe we loeaded get the location where you can fly to
    counter = 0
    for airport_code in df.IATA:
        counter += 1
        print(str(counter) + ') Crawling on ' + str(airport_code))
        # open up connection
        airport_fr_url = 'https://www.flightradar24.com/data/airports/' + str(airport_code) + '/routes'
        # take the page
        scraper = cfscrape.create_scraper()
        raw_html = scraper.get(airport_fr_url).content
        scraper.close()
        # parse contents to html
        page_soup = soup(raw_html, "html.parser")
        print('     ' + page_soup.title.string)

        # get all the script tags
        destinations_container = page_soup.findAll("script")
        # find the specific script that contains all the destination airport data
        for tag in destinations_container:
            tag = str(tag)
            if tag.startswith('<script>var arrRoutes'):
                start = tag.find('[')
                finish = tag.find(']')
                destinations_list = json.loads(tag[start:finish + 1])

        print('checking '+str(len(destinations_list))+' routes')
        # print('destinations_list: '+str(destinations_list))
        for destination in destinations_list:
            if destination['iata'] != None:
                # print('destination["iata"] != None : '+str(destination['iata'] != None))
                # print('destination["iata"] in airports_list : '+str(destination['iata'] in airports_list))
                # print('str(airport_code) in airports_list : '+str(str(airport_code) in airports_list))
                if destination['iata'] in airports_list and str(airport_code) in airports_list:

                    print(str(airport_code) + ' <- -> ' + destination['iata'])
                    json_url = airport_fr_url + '?get-airport-arr-dep='+destination['iata']+'&format=json'
                    scraper = cfscrape.create_scraper(delay=30)
                    json_response = json.loads(scraper.get(json_url).content)
                    scraper.close()

                    if json_response: #check if the json is not empty
                        try:
                            for m in ['arrivals', 'departures']:
                                number_of_flights = 0
                                # print('m: '+str(m))
                                # print('list(json_response[m].values()): '+str(list(json_response[m].values())))
                                # print('list(list(json_response[m].values())[0]["airports"].values())'+str(list(list(json_response[m].values())[0]['airports'].values())))
                                flights = list(list(json_response[m].values())[0]['airports'].values())[0]['flights']
                                # print('flights'+str(flights))
                                for flight_code in flights.keys():
                                    flight_codes_list.append(flight_code)
                                    print(flight_code)
                        except KeyError:
                            print('THERE ARE NOT DIRECT FLIGHTS')
                    else:
                        print('DOES NOT HAVE ANY FLIGHTS!!!')
            else:
                print('This airport has no iata code registered :' + destination['icao'])
        print('=======================================================================================================')
    routes_df = pd.DataFrame({'Flight_code': flight_codes_list})
    now = datetime.datetime.now()
    output_file_name = 'flight_codes/flight_radar_24_flight_codes_snapshot'+str(now.day)+'_'+str(now.month)+'_'+str(now.year)+'.csv'
    routes_df.to_csv(output_file_name, sep=',')
    return output_file_name


def get_flight_details_per_flight_code():

    from_airports_list = []
    to_airports_list = []
    departure_delay_list = []
    arrival_delay_list = []
    departure_delay_time_list = []
    arrival_delay_time_list = []
    flight_code_list = []
    canceled_departure_list = []
    canceled_arrival_list = []
    canceled_flight_codes_list = []

    day_to_compare_txt = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%d %b %Y')

    df = pd.read_csv('flight_codes/flight_radar_24_flight_codes_snapshot19_7_2020.csv', sep=',')
    counter = 1
    for flight_code in tqdm(df.Flight_code):
        time.sleep(5)
        if (counter != 0) and (counter % 1000 == 0):
            time.sleep(60)

        if (str(flight_code) != 'nan') and (str(flight_code) != ''):
            print(str(counter)+') '+str(flight_code))
            counter += 1
            flight_code_url = 'https://www.flightradar24.com/data/flights/'+flight_code

            # take the page
            scraper = cfscrape.create_scraper(delay=30)
            raw_html = scraper.get(flight_code_url).content
            scraper.close()
            # parse contents to html
            page_soup = soup(raw_html, "html.parser")

            # get all the data-row trs
            data_container = page_soup.findAll("tr", {"class": "data-row"})

            for row_container in data_container:

                row_tds = row_container.findAll("td")

                row_date_text = row_tds[2].text.strip()

                from_airport_whole_name = row_tds[3].text.strip()
                from_airport_code = from_airport_whole_name[from_airport_whole_name.find("(")+1:from_airport_whole_name.find(")")]
                to_airport_whole_name = row_tds[4].text.strip()
                to_airport_code = to_airport_whole_name[to_airport_whole_name.find("(")+1:to_airport_whole_name.find(")")]

                if row_date_text == day_to_compare_txt:
                    print('From airport code: ' + str(from_airport_code))
                    print('To airport code: ' + str(to_airport_code))

                    print('I found a flight scheduled for today '+str(day_to_compare_txt))
                    print('!!!!!!!!!!!!!!!!!!!!!!: '+str(row_tds[6].text))
                    if row_tds[11].text.strip() == 'Canceled':
                        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>This flights got canceled....')
                        canceled_flight_codes_list.append(flight_code)
                        canceled_departure_list.append(from_airport_code)
                        canceled_arrival_list.append(to_airport_code)

                    elif (row_tds[6].text.strip() != '—') and (row_tds[7].text.strip() != '—') and (row_tds[8].text.strip() != '—') and (row_tds[9].text.strip() != '—') and (row_tds[11].text.strip() != '—'):
                        flight_code_list.append(flight_code)
                        print("The flight looks like it was completed earlier today")
                        scheduled_departure_timestamp_str = row_tds[7]['data-timestamp']
                        actual_departure_timestamp_str = row_tds[8]['data-timestamp']
                        print('Scheduled Departure time --> '+str(scheduled_departure_timestamp_str))
                        print('Actual Departure time --> '+str(actual_departure_timestamp_str))
                        # create timestamp objects from the strings
                        scheduled_departure_timestamp = datetime.datetime.fromtimestamp(int(scheduled_departure_timestamp_str))
                        actual_departure_timestamp = datetime.datetime.fromtimestamp(int(actual_departure_timestamp_str))


                        scheduled_arrival_timestamp_str = row_tds[9]['data-timestamp']
                        actual_arrival_timestamp_str = row_tds[11]['data-timestamp']
                        print('Scheduled Arival time --> '+str(scheduled_arrival_timestamp_str))
                        print('Actual Arival time --> '+str(actual_arrival_timestamp_str))
                        # create timestamp objects from the strings
                        scheduled_arrival_timestamp = datetime.datetime.fromtimestamp(int(scheduled_arrival_timestamp_str))
                        actual_arrival_timestamp = datetime.datetime.fromtimestamp(int(actual_arrival_timestamp_str))

                        print(' ')

                        departure_time_diff = (scheduled_departure_timestamp - actual_departure_timestamp).total_seconds()
                        print('Departure time difference: '+str(departure_time_diff))
                        departure_delay_time_list.append(departure_time_diff)
                        # check if there is a delay during the departure of the flight
                        if actual_departure_timestamp > scheduled_departure_timestamp:
                            # use the timestamp objects to calculate the difference in seconds
                            departure_delay_list.append(True)
                            print('There was a delay during departure')
                        else:
                            departure_delay_list.append(False)
                            print('The flight started earlier than expected')

                        arrival_time_diff = (scheduled_arrival_timestamp - actual_arrival_timestamp).total_seconds()
                        print('Arival time difference: '+str(arrival_time_diff))
                        arrival_delay_time_list.append(arrival_time_diff)
                        # check if there is a delay during the arrival of the flight
                        if actual_arrival_timestamp > scheduled_arrival_timestamp:
                            # use the timestamp objects to calculate the difference in seconds
                            arrival_delay_list.append(True)
                            print('There was a delay during arival')
                        else:
                            arrival_delay_list.append(False)
                            print('The flight landed earlier than expected')

                        from_airports_list.append(from_airport_code)
                        to_airports_list.append(to_airport_code)

    routes_df = pd.DataFrame({'from_airports_list': from_airports_list, 'to_airports_list': to_airports_list, 'departure_delay_time_list': departure_delay_time_list, 'departure_delay_list': departure_delay_list, 'arrival_delay_time_list': arrival_delay_time_list, 'arrival_delay_list': arrival_delay_list, 'flight_code_list': flight_code_list})
    output_file_name = 'delays/departure_arival_delays'+day_to_compare_txt.replace(' ', '_')+'.csv'
    routes_df.to_csv(output_file_name, sep=',')

    canceled_flights_df = pd.DataFrame({'canceled_departure_list': canceled_departure_list, 'canceled_arrival_list': canceled_arrival_list, 'canceled_flight_codes_list': canceled_flight_codes_list})
    canceled_output_file_name = 'canceled_flights/canceled_flights_on_'+day_to_compare_txt.replace(' ', '_')+'.csv'
    canceled_flights_df.to_csv(canceled_output_file_name, sep=',')


def generate_delay_heatmap(input_dir='delays/departure_arival_delays21_Jul_2020.csv', departures_output_dir='', arrivals_output_dir=''):
    airports_df = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    european_airports_df = pd.read_csv('airports_data/european_airports.csv', sep=',')
    delays_df = pd.read_csv('delays/departure_arival_delays21_Jul_2020.csv', sep=',')

    european_airport_codes_list = european_airports_df['IATA'].tolist()

    departures_delays_list = []
    arrivals_delays_list = []

    airports_dict = {}
    for index, row in airports_df.iterrows():
        airports_dict[row['Label']] = (row['latitude'], row['longitude'])

    for index, row in delays_df.iterrows():
        if row['departure_delay_list']:
            if (row['from_airports_list'] in airports_dict.keys()) and (
                    row['from_airports_list'] in european_airport_codes_list):
                lat, longt = airports_dict[row['from_airports_list']]
                departures_delays_list.append((lat, longt, abs(float(row['departure_delay_time_list']))))

        if row['arrival_delay_list']:
            if (row['to_airports_list'] in airports_dict.keys()) and (
                    row['to_airports_list'] in european_airport_codes_list):
                lat, longt = airports_dict[row['to_airports_list']]
                arrivals_delays_list.append((lat, longt, abs(float(row['arrival_delay_time_list']))))

    departures_map = Map(location=[48.499998, 23.3833318], zoom_start=4, )
    arrivals_map = Map(location=[48.499998, 23.3833318], zoom_start=4, )

    departures_layer = HeatMap(departures_delays_list,
                               min_opacity=0.9,
                               radius=17,
                               blur=25,
                               max_zoom=5,
                               )
    arrivals_layer = HeatMap(arrivals_delays_list,
                               min_opacity=0.9,
                               radius=17,
                               blur=25,
                               max_zoom=5,
                               )

    departures_map.add_child(departures_layer)
    arrivals_map.add_child(arrivals_layer)

    departures_map.save(departures_output_dir)
    arrivals_map.save(arrivals_output_dir)


#just calculate the average departure and arrival delay of every airport and then create the heatmaps again
def generate_average_delay_heatmap(input_dir='delays/departure_arival_delays21_Jul_2020.csv', departures_output_dir='', arrivals_output_dir=''):
    airports_df = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    european_airports_df = pd.read_csv('airports_data/european_airports.csv', sep=',')
    delays_df = pd.read_csv('delays/departure_arival_delays21_Jul_2020.csv', sep=',')

    european_airport_codes_list = european_airports_df['IATA'].tolist()

    departures_delays_list = []
    arrivals_delays_list = []

    airports_dict = {}
    for index, row in airports_df.iterrows():
        airports_dict[row['Label']] = (row['latitude'], row['longitude'])

    average_departure_delay_per_airport = {}
    average_arrival_delay_per_airport = {}

    # for every airport gather all the departure and arrival delays
    for index, row in delays_df.iterrows():
        if row['departure_delay_list']:
            if row['from_airports_list'] in airports_dict.keys() and row['from_airports_list'] in european_airport_codes_list:
                if row['from_airports_list'] not in average_departure_delay_per_airport.keys():
                    average_departure_delay_per_airport[row['from_airports_list']] = []
                average_departure_delay_per_airport[row['from_airports_list']].append(abs(float(row['departure_delay_time_list'])))
        if row['arrival_delay_list']:
            if row['to_airports_list'] in airports_dict.keys() and row['to_airports_list'] in european_airport_codes_list:
                if row['to_airports_list'] not in average_arrival_delay_per_airport.keys():
                    average_arrival_delay_per_airport[row['to_airports_list']] = []
                average_arrival_delay_per_airport[row['to_airports_list']].append(abs(float(row['arrival_delay_time_list'])))

    average_departures_delays_per_coordinates = []
    for key, delays_list in average_departure_delay_per_airport.items():
        if key in airports_dict.keys():
            lat, longt = airports_dict[key]
            average_departures_delays_per_coordinates.append((lat, longt, np.mean(delays_list)))

    average_arrivals_delays_per_coordinates = []
    for key, delays_list in average_arrival_delay_per_airport.items():
        if key in airports_dict.keys():
            lat, longt = airports_dict[key]
            average_arrivals_delays_per_coordinates.append((lat, longt, np.mean(delays_list)))

    average_departures_map = Map(location=[48.499998, 23.3833318], zoom_start=4, )
    average_arrivals_map = Map(location=[48.499998, 23.3833318], zoom_start=4, )

    average_departures_layer = HeatMap(average_departures_delays_per_coordinates,
                                       max_val=max([i[2] for i in average_departures_delays_per_coordinates]),
                                       min_opacity=0.2,
                                       radius=20,
                                       blur=1,
                                       max_zoom=1,
                                       )
    average_arrivals_layer = HeatMap(average_arrivals_delays_per_coordinates,
                                     max_val=max([i[2] for i in average_arrivals_delays_per_coordinates]),
                                     min_opacity=0.2,
                                     radius=20,
                                     blur=1,
                                     max_zoom=1,
                                     )

    average_departures_map.add_child(average_departures_layer)
    average_arrivals_map.add_child(average_arrivals_layer)

    average_departures_map.save(departures_output_dir)
    average_departures_map.save(arrivals_output_dir)


def plot_airport_network(output_file_name):

    df = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    airports_list = df['Label'].tolist() #extract the iata code of every airport

    csv_file = open(output_file_name, mode='r')
    csv_reader = csv.DictReader(csv_file)

    freq_dict = {}
    graph = nx.DiGraph()
    # add nodes and edges to the graph
    for row in csv_reader:
        source = airports_list[int(row['Source'])]
        target = airports_list[int(row['Target'])]
        weight = int(row['Weight'])

        if weight in freq_dict:
            freq_dict[weight] +=1
        else:
            freq_dict[weight] = 1

        graph.add_edge(source, target, weight=weight)

    date_list = output_file_name.split('.')[0].split('_')[-3:]
    output_file_name = date_list[0]+'_'+date_list[1]+'_'+date_list[2]
    network_visualizer.plot_network_on_map(graph, df, node_size_choice='in_degree', node_color_choice='in_degree', input_data_file_name=output_file_name)


if __name__ == "__main__": main()