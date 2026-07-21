from __future__ import annotations
from Connection import Connection
from Algo import Algo


class Zone:

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
        for target_zone in target_zones:
            connection = Connection.get_connection(
                source.name, target_zone.name)
            limit = target_zone.metadata['max_drones'] if connection.metadata[
                'max_link_capacity'] == target_zone.metadata[
                    'max_drones'] else 1
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
        for zone in cls.l_zones:
            zone.shortest_path_from_current_hub_to_end = algo_object.dijkstra(
                zone.name, end_point_name)
            if zone.shortest_path_from_current_hub_to_end is not None:
                zone.path = algo_object.path

    @classmethod
    def min_x(cls) -> int:
        m: int = min([zone.coordinates[0] for zone in cls.l_zones])
        return m

    @classmethod
    def min_y(cls) -> int:
        m: int = min([zone.coordinates[1] for zone in cls.l_zones])
        return m

    @classmethod
    def max_x(cls) -> int:
        m: int = max([zone.coordinates[0] for zone in cls.l_zones])
        return m

    @classmethod
    def max_y(cls) -> int:
        m: int = max([zone.coordinates[1] for zone in cls.l_zones])
        return m
