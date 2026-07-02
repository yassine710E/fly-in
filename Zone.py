class Zone:
    
    #for stock all zone object that i created
    l_zones = []
    
    def __init__(self,name,type,coordinates,metadata):
        self.name = name
        self.type = type
        self.coordinates = coordinates
        self.metadata = metadata
        self.l_drones =  []
        self.shortest_path_from_current_hub_to_end = None 
        Zone.l_zones.append(self)

    #get zone by its zone because zone name is unique
    @classmethod
    def get_zone_by_its_prop(cls,string:str,prop:str):
        for zone in cls.l_zones:
            if (prop == "name" and zone.name == string) or (prop == "type" and zone.type == string):
                return zone
        return None
    
    #pop drones in instance in push them in other
    @classmethod
    def travel_to_other_hubs(cls,source,target_zones):
        for target_zone in target_zones:
            for i in range(0,target_zone.metadata['max_drones']):
                if source.l_drones:
                    popped_drone = source.l_drones.pop()
                    target_zone.l_drones.append(popped_drone)
                    print(f"move drone with id {popped_drone.id} from {source.name} to {target_zone.name}")

    @classmethod 
    def set_shortest_path(cls,algo_object,end_point_name):
        for zone in cls.l_zones:
            zone.shortest_path_from_current_hub_to_end = algo_object.dijkstra(zone.name,end_point_name)
         