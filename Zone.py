class Zone:
    def __init__(self,name,type,coordinates,metadata,l_drones):
        self.name = name
        self.type = type
        self.coordinates = coordinates
        self.metadata = metadata
        self.l_drones = l_drones if self.type == "start_hub" else []
        self.connections = []
        self.next_action = 'STOP'
    
    
        
    

        