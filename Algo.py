from __future__ import annotations
import heapq
from Connection import Connection


class Algo:
    def __init__(self, connections: list['Connection']) -> None:
        from Zone import Zone
        self.connections = connections
        self.costs = {'normal': 1, 'restricted': 2,
                      'priority': 1, 'blocked': None}
        self.graph: dict = dict()
        for zone in Zone.l_zones:
            self.graph[zone.name] = []
        self.create_graph()
        self.path: list[str] = []

    def create_graph(self) -> None:
        from Zone import Zone
        for connection in self.connections:
            obj_start = Zone.get_zone_by_its_prop(
                connection.tuple_connections[0], 'name')
            obj_target = Zone.get_zone_by_its_prop(
                connection.tuple_connections[1], 'name')
            if (isinstance(obj_target, Zone)
                and isinstance(obj_start, Zone)
                    and self.costs[obj_target.metadata['zone']]):
                self.graph[obj_start.name].append(
                    (obj_target.name, self.costs[obj_target.metadata['zone']]))

    def dijkstra(self, start_point: str, end_point: str) -> int | None:
        from Zone import Zone
        priority_queue: list[tuple] = []
        visited: list[str] = []
        path: list[str] = []
        dict_curr_and_prev: dict = dict()
        dict_curr_and_prev[start_point] = None
        heapq.heappush(priority_queue, (0, start_point))
        while priority_queue:
            connections = [(point[1]+priority_queue[0][0], point[0])
                           for point in self.graph[priority_queue[0][1]]
                           if point[0] not in visited]
            for connection in connections:
                if connection[1] in [node[1] for node in priority_queue]:
                    node_from_pq = [
                        node for node in priority_queue
                        if node[1] == connection[1]][0]
                    if connection[0] < node_from_pq[0]:
                        priority_queue = [
                            connection if connection[1] == node[1]
                            else node for node in priority_queue
                        ]
                else:
                    heapq.heappush(priority_queue, connection)

                    def func_priority_sort(
                            item: tuple[int, str]) -> bool | tuple:
                        zone = Zone.get_zone_by_its_prop(item[1], 'name')
                        if zone is None:
                            return False
                        return (item[0], zone.metadata['zone'] != 'priority')
                    priority_queue.sort(key=func_priority_sort)
                    dict_curr_and_prev[connection[1]] = priority_queue[0][1]
            popped_val: tuple[int, str] = heapq.heappop(priority_queue)
            visited.append(popped_val[1])
            if popped_val[1] == end_point:
                key = end_point
                path.append(key)
                while dict_curr_and_prev[key]:
                    path.append(dict_curr_and_prev[key])
                    key = dict_curr_and_prev[key]
                path.reverse()
                self.path = path
                return popped_val[0]
        return None
