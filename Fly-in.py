import sys
from Parser import Parser,ParsingError
import pygame
from Display import Display
from Algo import Algo
from Zone import Zone
from Connection import Connection
from Drone import Drone

#get zone by its zone because zone name is unique
def get_zone_by_its_prop(string:str,l_zones:list[Zone],prop:str) -> Zone | None:
    for zone in l_zones:
        if (prop == "name" and zone.name == string) or (prop == "type" and zone.type == string):
            return zone
    return None



if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        parser_object = Parser(file_name)
        config_data = parser_object.parsing()
        max_x,min_x = max(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0],min(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0]
        max_y,min_y = max(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1],min(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1]

        #create drones list for controlling them
        l_drones = [Drone(i) for i in range(1,config_data['nb_drones']+1)]

        # create zones list of zone object
        l_zones = [Zone(zone['name'],zone['type'],zone['coordinates'],zone['metadata'],l_drones[::1]) for zone in config_data['zones']]

        # init current zone for drones
        start_zone = get_zone_by_its_prop('start_hub',l_zones,'type')
        end_zone = get_zone_by_its_prop('end_hub',l_zones,'type')
        for drone in l_drones:
            drone.init_current_start_hub(start_zone)        

        # put l_zone on class connections for search on single zone using its name (zone name is unisque)
        l_connections = [Connection(l_zones,connection['tuple_connections'],connection['metadata']) for connection in config_data['connections']]


        # algo for dijkstra algo 
        obj = Algo(l_connections,l_zones)
        
        start_point = start_zone.name
        end_point = end_zone.name
        
        dijkstra_output = obj.dijkstra(start_point,end_point)
        if dijkstra_output is None:
            raise ParsingError('no Path exist to end point')
        
        l_drones_end =end_zone.l_drones

        while len(l_drones_end) != config_data['nb_drones']:
        # for i in range(0,5):
            hubs_of_all_drones = {drone.current_hub for drone in l_drones}
            print('-----------------')
            for hub in hubs_of_all_drones:
                print(hub.name)
            print('-----------------')
            # print(len(hubs_of_all_drones))
            for hub in hubs_of_all_drones:
                # sort connection by its target hub priority 
                for connection in hub.connections:
                    target_name = connection.start_and_target_objects['target'].name
                    target_obj = get_zone_by_its_prop(target_name,l_zones,'name')
                    # shortest path direction (if the hub is not full using max_drones in metadata)
                    if target_obj.name in dijkstra_output['path']:
                        if target_obj.metadata['max_drones'] > len(target_obj.l_drones) or target_obj.type == "end_hub":
                            last_drone = hub.l_drones.pop()
                            target_obj.l_drones.append(last_drone)
                            last_drone.current_hub = target_obj
                            print(f'(simple case)move drone with id {last_drone.id} from {hub.name} to {target_obj.name}')
                    
                    # other path for time complixity
                    elif target_obj.metadata['zone'] != 'blocked' :
                        dijkstra_output_tmp = obj.dijkstra(target_name,end_point)
                        if dijkstra_output_tmp and hub.l_drones:
                            last_drone = hub.l_drones.pop()
                            target_obj.l_drones.append(last_drone)
                            last_drone.current_hub = target_obj
                            print(f'move drone with id {last_drone.id} from {hub.name} to {target_obj.name}')
        
        for connection in l_connections:
            print(connection.start_and_target_objects['start'].name,connection.start_and_target_objects['target'].name)
        # declaring Display Object
        # with Display(pygame,config_data,min_x,min_y,dijkstra_output) as d:
        #     d.display_window(((max_x-min_y)*70)+100,((max_y-min_y)*70)+100)  
        
              
    except ParsingError as e:
        print(e)
