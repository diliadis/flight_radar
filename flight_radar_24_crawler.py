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


def airports_crawler():
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
        scraper = cfscrape.create_scraper()
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


def routes_crawler():
    # load the csv with the european airport codes
    df = pd.read_csv('airports_data/european_airports.csv', sep=',')

    df2 = pd.read_csv('airports_data/flight_radar_24_airports.csv', sep=',')
    airports_list = df2['Label'].tolist() #extract the iata code of every airport

    source_airport_list = []
    target_airport_list = []
    number_of_flights_list = []

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
        print('destinations_list: '+str(destinations_list))
        for destination in destinations_list:
            if destination['iata'] != None:
                print('destination["iata"] != None : '+str(destination['iata'] != None))
                print('destination["iata"] in airports_list : '+str(destination['iata'] in airports_list))
                print('str(airport_code) in airports_list : '+str(str(airport_code) in airports_list))
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
                                print('m: '+str(m))
                                print('list(json_response[m].values()): '+str(list(json_response[m].values())))
                                print('list(list(json_response[m].values())[0]["airports"].values())'+str(list(list(json_response[m].values())[0]['airports'].values())))
                                flights = list(list(json_response[m].values())[0]['airports'].values())[0]['flights']
                                print('flights'+str(flights))
                                for flight in flights.values():
                                    hours = flight['utc']
                                    print('hours: '+str(hours))
                                    number_of_flights += len(hours)
                                    print('number_of_flights: '+str(number_of_flights))

                                number_of_flights_list.append(number_of_flights)
                                print('number_of_flights_list: '+str(number_of_flights_list))
                                print('destination["iata"]: '+str(destination['iata']))
                                airport_1_code = airports_list.index(destination['iata'])
                                print('airport_1_code: '+str(airport_1_code))
                                print('str(airport_code): '+str(airport_code))
                                airport_2_code = airports_list.index(str(airport_code))
                                print('airport_2_code: '+str(airport_2_code))
                                if m == 'arrivals':
                                    print('Arrivals     '+str(number_of_flights)+' flights')
                                    source_airport_list.append(airport_1_code)
                                    target_airport_list.append(airport_2_code)
                                else:
                                    print('Departures   '+str(number_of_flights) + ' flights')
                                    target_airport_list.append(airport_1_code)
                                    source_airport_list.append(airport_2_code)
                        except KeyError:
                            print('THERE ARE NOT DIRECT FLIGHTS')
                    else:
                        print('DOES NOT HAVE ANY FLIGHTS!!!')
            else:
                print('This airport has no iata code registered :' + destination['icao'])
        print('=======================================================================================================')
    routes_df = pd.DataFrame({'Source': source_airport_list, 'Target': target_airport_list, 'Weight': number_of_flights_list})
    now = datetime.datetime.now()
    output_file_name = 'routes_data/flight_radar_24_routes_with_weights_and_bi_direct_'+str(now.day)+'_'+str(now.month)+'_'+str(now.year)+'.csv'
    routes_df.to_csv(output_file_name, sep=',')
    return output_file_name


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