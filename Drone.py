class Drone:
    def __init__(self,id):
        self.id = id
        self.path = None
    
    def set_path(self,dijkstra_path):
        self.path = dijkstra_path
        