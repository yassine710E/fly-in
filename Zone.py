from __future__ import annotations
from Connection import Connection
from Algo import Algo


class Zone:
    """Represent a hub or zone node within the simulation graph.

    Attributes:
        l_zones (list[Zone]): Class attribute tracking all instantiated zones.
        m_hub (Zone | None): Class attribute tracking the last updated hub.
        costs (dict[str, int | None]): Delay cost mapping by zone type.
        name (str): Unique identifier for the zone.
        type (str): Functional type (e.g., 'start_hub', 'end_hub', 'hub').
        coordinates (tuple[int, int]): Spatial (x, y) coordinates of the zone.
        metadata (dict): Metadata mapping (e.g., color, max_drones, zone type).
        l_drones (list): Collection of drones currently residing in this zone.
        current_cost (int): Counter tracking progress towards traversal cost.
        shortest_path_from_current_hub_to_end (int | None): Dijkstra distance
            from this zone to the designated end hub.
        path (list[str]): Recorded node path sequence from Dijkstra execution.
    """

    # for stock all zone object that i created
    l_zones: list['Zone'] = []

    # for marking the last hub that i pushed drones on it for the next turn
    m_hub = None
    costs = {'normal': 1, 'restricted': 2, 'priority': 1, 'blocked': None}

    def __init__(
        self,
            name: str,
            type: str,
            coordinates: tuple[int, int],
            metadata: dict):
        """Initialize a Zone instance and register it in class-level index.

        Args:
            name (str): Unique name of the zone.
            type (str): Classification type of the hub.
            coordinates (tuple[int, int]): X and Y position coordinates.
            metadata (dict): Configuration properties and limits.
        """
        self.name = name
        self.type = type
        self.coordinates = coordinates
        self.metadata = metadata
        self.l_drones: list = []
        self.current_cost: int = 1
        self.shortest_path_from_current_hub_to_end: int | None = None
        self.path: list[str] = []
        Zone.l_zones.append(self)

    # get zone by its zone because zone name is unique
    @classmethod
    def get_zone_by_its_prop(cls, string: str, prop: str) -> 'Zone' | None:
        """Find a zone instance matching a target property value.

        Args:
            string (str): Target string value to search for.
            prop (str): Property key to match against ('name' or 'type').

        Returns:
            Zone | None: Matching Zone instance if found, otherwise None.
        """
        for zone in cls.l_zones:
            if ((prop == "name" and zone.name == string)
                    or (prop == "type" and zone.type == string)):
                return zone
        return None

    # pop drones in instance in push them in other
    @classmethod
    def travel_to_other_hubs(cls,
                             source: 'Zone',
                             target_zones: list['Zone']) -> None:
        """Transfer eligible drones from source zone to target zones.

        Args:
            source (Zone): Origin zone containing departing drones.
            target_zones (list[Zone]): Candidate destination zones for move.
        """
        for target_zone in target_zones:
            connection = Connection.get_connection(
                source.name, target_zone.name)
            limit = (connection.metadata['max_link_capacity']
                     if connection.metadata[
                'max_link_capacity'] <= target_zone.metadata[
                    'max_drones'] else target_zone.metadata['max_drones'])
            for i in range(0, limit):
                if (source.l_drones and source.name not in target_zone.path and
                    (len(target_zone.l_drones) <
                     target_zone.metadata['max_drones']
                     or target_zone.type == "end_hub")):
                    source.l_drones.sort(key=lambda x: (x.id))
                    popped_drone = source.l_drones.pop()
                    target_zone.l_drones.append(popped_drone)
                    if target_zone.metadata['zone'] != 'restricted':
                        print(f'D{popped_drone.id}-{target_zone.name}',
                              end=' ')
                    else:
                        print(
                            f'D{popped_drone.id}-{source.name}-'
                            f'{target_zone.name}', end=' ')

    @classmethod
    def set_shortest_path(cls,
                          algo_object: 'Algo',
                          end_point_name: str) -> None:
        """Calculate and store shortest path distance to target end point.

        Args:
            algo_object (Algo): Graph pathfinding algorithm handler instance.
            end_point_name (str): Name of the destination hub zone.
        """
        for zone in cls.l_zones:
            zone.shortest_path_from_current_hub_to_end = algo_object.dijkstra(
                zone.name, end_point_name)
            if zone.shortest_path_from_current_hub_to_end is not None:
                zone.path = algo_object.path

    @classmethod
    def min_x(cls) -> int:
        """Find the minimum X-coordinate among all registered zones.

        Returns:
            int: Smallest X-coordinate value.
        """
        m: int = min([zone.coordinates[0] for zone in cls.l_zones])
        return m

    @classmethod
    def min_y(cls) -> int:
        """Find the minimum Y-coordinate among all registered zones.

        Returns:
            int: Smallest Y-coordinate value.
        """
        m: int = min([zone.coordinates[1] for zone in cls.l_zones])
        return m

    @classmethod
    def max_x(cls) -> int:
        """Find the maximum X-coordinate among all registered zones.

        Returns:
            int: Largest X-coordinate value.
        """
        m: int = max([zone.coordinates[0] for zone in cls.l_zones])
        return m

    @classmethod
    def max_y(cls) -> int:
        """Find the maximum Y-coordinate among all registered zones.

        Returns:
            int: Largest Y-coordinate value.
        """
        m: int = max([zone.coordinates[1] for zone in cls.l_zones])
        return m
