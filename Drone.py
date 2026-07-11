class Drone:
    def __init__(self,id,start_hub):
        self.id = id
        self.path = None
        self.cost_counter = 0
        self.updated_path = [start_hub]
    
    def set_path(self,dijkstra_path):
        self.path = dijkstra_path
        