class Connection:
    def __init__(self,l_zones,tuple_connections,metadata):
        self.l_zones = l_zones
        self.tuple_connections = tuple_connections
        self.metadata = metadata
        self.start_and_target_objects = dict()
        self.set_start_and_end_zone_object()
    
    def set_start_and_end_zone_object(self):
        for zone in self.l_zones:
            if zone.name == self.tuple_connections[0]:
                self.start_and_target_objects['start'] = zone
                zone.connections.append(self)
            elif zone.name == self.tuple_connections[1]:
                self.start_and_target_objects['target'] = zone
                zone.connections.append(self)
        
        