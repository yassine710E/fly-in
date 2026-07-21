class Drone:
    """Represents a drone entity with a unique identifier and movement path.

    Attributes:
        l_drones (list): Class-level registry of all created Drone instances.
        id (int): Unique identifier for the drone.
        path (None | list[str]): Current planned path of zone names.
    """

    l_drones: list = []

    def __init__(self, id: int) -> None:
        """Initialize a Drone instance and register it in l_drones.

        Args:
            id (int): Unique identifier for the drone.
        """
        self.id: int = id
        self.path: None | list[str] = None
        Drone.l_drones.append(self)

    def set_path(self, dijkstra_path: list[str]) -> None:
        """Assign a calculated path to the drone.

        Args:
            dijkstra_path (list[str]): Sequence of zone names
                representing the path.
        """
        self.path = dijkstra_path
