class Drone:
    l_drones = []
    def __init__(self,id):
        self.id = id
        self.path = None
        self.cost_counter = 0
        Drone.l_drones.append(self)
    def set_path(self,dijkstra_path):
        self.path = dijkstra_path
        