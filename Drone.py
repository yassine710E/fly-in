class Drone:
    def __init__(self,id):
        self.id = id
        self.current_hub = None
    
    def init_current_start_hub(self,obj_zone):
        self.current_hub = obj_zone
        