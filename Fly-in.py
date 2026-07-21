import sys
from Parser import Parser, ParsingError
import pygame
from Display import Display
from Algo import Algo
from Zone import Zone
from Connection import Connection
from Drone import Drone
from SimFunctions import main_simulation

if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        parser_object = Parser(file_name)
        config_data = parser_object.parsing()

        # create zone objects and append them in class attributes l_zones
        for zone in config_data['zones']:
            Zone(zone['name'], zone['type'],
                 zone['coordinates'], zone['metadata'])

        # get start and end zone object
        start_zone = Zone.get_zone_by_its_prop('start_hub', 'type')
        end_zone = Zone.get_zone_by_its_prop('end_hub', 'type')

        if start_zone is None or end_zone is None:
            raise ParsingError('hub not found')

        # create drones list for controlling them
        for i in range(1, config_data['nb_drones'] + 1):
            Drone(i)

        # and set all drones to start hub
        start_zone.l_drones = Drone.l_drones[::1]

        # put l_zone on class connections
        # for search on single zone using its name (zone name is unique)
        for connection in config_data['connections']:
            Connection(connection['tuple_connections'], connection['metadata'])

        # algo for dijkstra algo
        obj = Algo(Connection.l_connections)

        start_point = start_zone.name
        end_point = end_zone.name

        dijkstra_output = obj.dijkstra(start_point, end_point)
        if dijkstra_output is None:
            raise ParsingError('no Path exist to end point')
        Zone.set_shortest_path(obj, end_point)

        l_drones_end = end_zone.l_drones

        history = main_simulation(l_drones_end)

        # Pass history to the display window instead of dijkstra_output
        with Display(pygame, history) as d:
            d.display_window()

    except (BaseException, ParsingError) as e:
        print(e)
