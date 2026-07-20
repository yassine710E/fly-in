class Drone:
    l_drones: list = []

    def __init__(self, id: int) -> None:
        self.id: int = id
        self.path: None | list[str] = None
        Drone.l_drones.append(self)

    def set_path(self, dijkstra_path: list[str]) -> None:
        self.path = dijkstra_path
