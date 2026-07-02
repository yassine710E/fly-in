import sys
from Parser import Parser,ParsingError
import pygame
from Display import Display
from Algo import Algo
from Zone import Zone
from Connection import Connection
from Drone import Drone


if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        parser_object = Parser(file_name)
        config_data = parser_object.parsing()
        max_x,min_x = max(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0],min(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0]
        max_y,min_y = max(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1],min(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1]
        

        #create drones list for controlling them
        l_drones = [Drone(i) for i in range(1,config_data['nb_drones']+1)]

        # create zone  objects and append them in class attributes l_zones 
        for zone in config_data['zones']:
            Zone(zone['name'],zone['type'],zone['coordinates'],zone['metadata'])
        
        # get start and end zone object
        start_zone = Zone.get_zone_by_its_prop('start_hub','type')
        end_zone  = Zone.get_zone_by_its_prop('end_hub','type')
        
        # and set all drones to start hub
        start_zone.l_drones = l_drones[::1]
        
        
        # put l_zone on class connections for search on single zone using its name (zone name is unique)
        for connection in config_data['connections']:
            Connection(connection['tuple_connections'],connection['metadata'])

        # algo for dijkstra algo 
        obj = Algo(Connection.l_connections)
        
        start_point = start_zone.name
        end_point = end_zone.name
        
        dijkstra_output = obj.dijkstra(start_point,end_point)
        if dijkstra_output is None:
            raise ParsingError('no Path exist to end point')
    
        
        Zone.set_shortest_path(obj,end_point)
        l_drones_end =end_zone.l_drones
        while len(l_drones_end) != len(l_drones):
            hubs = [hub for hub in Zone.l_zones if hub.l_drones and hub.type != 'end_hub']
            hubs.sort(key=lambda x:x.shortest_path_from_current_hub_to_end['cost'])
            for hub in hubs:
                print(f'-------- source zone name : {hub.name} ------------')
                connected_target_zones = Connection.get_connections_from_source_point(hub.name)
                target_zones_object = [Zone.get_zone_by_its_prop(connection.tuple_connections[1],'name') for connection in connected_target_zones if Zone.get_zone_by_its_prop(connection.tuple_connections[1],'name').shortest_path_from_current_hub_to_end and hub.name not in Zone.get_zone_by_its_prop(connection.tuple_connections[1],'name').shortest_path_from_current_hub_to_end['path']]
                
                target_zones_object.sort(key=lambda x:x.shortest_path_from_current_hub_to_end['cost'])
                Zone.travel_to_other_hubs(hub,target_zones_object)
                print('----------------------------------------------------')
                
        with Display(pygame,config_data,min_x,min_y,dijkstra_output) as d:
            d.display_window(((max_x-min_y)*70)+100,((max_y-min_y)*70)+100)  
        
              
    except ParsingError as e:
        print(e)
