import collections
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap


def plot_network_on_map(graph, df, node_size_choice=None, node_color_choice=None,  input_data_file_name='default'):
    number_of_airports_to_be_labeled_in_map = 20
    # set the coordinates of the map that will be used to plot all the airports and their routes
    plt.figure(figsize=(10, 9))
    m = Basemap(projection='merc', llcrnrlat=30, urcrnrlat=65, llcrnrlon=-15, urcrnrlon=70, lat_ts=0, resolution='l',
                suppress_ticks=True)

    # extract the longitude and latitude info of every airport
    mx, my = m(df['longitude'].values, df['latitude'].values)

    pos = {}
    for count, elem in enumerate(df['Label']):
        pos[elem] = (mx[count], my[count])

    cmap = plt.cm.jet
    if node_color_choice is None:
        cmap = None
        node_color = 'r'
        node_color_choice = 'r'
    elif node_color_choice == 'degree':
        node_color = [graph.degree(n) for n in graph.nodes()]
    elif node_color_choice == 'in_degree':
        node_color = [graph.in_degree(n) for n in graph.nodes()]
    elif node_color_choice == 'out_degree':
        node_color = [graph.out_degree(n) for n in graph.nodes()]

    if node_size_choice is None:
        node_size = 1
        node_size_choice = 1
    elif node_size_choice == 'degree':
        node_size = [graph.degree(n) for n in graph.nodes]
    elif node_size_choice == 'in_degree':
        node_size = [graph.in_degree(n) for n in graph.nodes]
    elif node_size_choice == 'out_degree':
        node_size = [graph.out_degree(n) for n in graph.nodes]

    if node_color_choice is not None and node_color_choice != 'r':
        nc = nx.draw_networkx_nodes(G=graph, pos=pos, node_list=graph.nodes(),
                                    node_color=node_color, alpha=0.8, node_size=node_size,
                                    cmap=cmap)
        plt.colorbar(nc)
    else:
        nx.draw_networkx_nodes(G=graph, pos=pos, node_list=graph.nodes(),
                               node_color=node_color, alpha=0.8, node_size=node_size,
                               cmap=cmap)

    nx.draw_networkx_edges(G=graph, pos=pos, edge_color='g', alpha=0.01, arrows=False)

    # draw the labels of the n top
    if node_size_choice is None or node_size_choice == 'degree':
        od = collections.OrderedDict(sorted(dict(graph.degree).items(), key=lambda t: t[1], reverse=True))
    elif node_size_choice == 'in_degree':
        od = collections.OrderedDict(sorted(dict(graph.in_degree).items(), key=lambda t: t[1], reverse=True))
    else:
        od = collections.OrderedDict(sorted(dict(graph.out_degree).items(), key=lambda t: t[1], reverse=True))

    top_airports = list(od)[:number_of_airports_to_be_labeled_in_map]
    labels_dict = {}
    for iata_label in graph.nodes():
        if iata_label in top_airports:
            labels_dict[iata_label] = iata_label
        else:
            labels_dict[iata_label] = ''
    nx.draw_networkx_labels(G=graph, pos=pos, labels=labels_dict, font_size=11)

    m.drawcountries(linewidth=0.7)
    m.drawstates(linewidth=0.7)
    m.drawcoastlines(linewidth=0.7)
    plt.tight_layout()
    image_dir = './images/'+input_data_file_name+'_node_size__'+node_size_choice+'__node_color_'+node_color_choice+'.png'
    plt.savefig(image_dir, format="png", dpi=500)
    print('route network plot finished successfully and saved as '+image_dir)
    plt.show()
