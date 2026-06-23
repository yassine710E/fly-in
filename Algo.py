import heapq

class Algo:
    def __init__(self,config_data):
        self.config_data = config_data
        self.graph = dict()
        self.costs = {'normal':1,'restricted':2,'priority':1,'blocked':None}
    
    def get_zones_for_connected_zone(self,zone_name):
        return [name for connection_metadata in self.config_data['connections'] for name in connection_metadata['tuple_connections'] if zone_name != name and zone_name in connection_metadata['tuple_connections']]

    def create_graph(self):
        for zone in self.config_data['zones']:
            self.graph[zone['name']] = []
            for connected_zone_name in self.get_zones_for_connected_zone(zone['name']):
                self.graph[zone['name']].append((connected_zone_name,[self.costs[zone['metadata']['zone']] for zone in self.config_data['zones'] if zone['name'] == connected_zone_name and self.costs[zone['metadata']['zone']]][0]))

    def dijkstra(self):
        start_point = [zone['name'] for zone in self.config_data['zones'] if zone['type'] == 'start_hub'][0]
        print(start_point)
        end_point = [zone['name'] for zone in self.config_data['zones'] if zone['type'] == 'end_hub'][0]
        print(end_point)
        visited = []
        priority_queue = []
        dist_point_and_prev = {start_point : None}
        heapq.heappush(priority_queue,(0,start_point))
        while priority_queue:
            connections = [(point[1]+priority_queue[0][0],point[0]) for point in self.graph[priority_queue[0][1]] if point[0] not in visited]
            for connection in connections:
                if connection[1] in [node[1] for node in priority_queue]:
                    node_from_pq = [node for node in priority_queue if node[1] == connection[1]][0]
                    if connection[0] < node_from_pq[0]:
                        priority_queue = [connection if connection[1] == node[1] else node for node in priority_queue]
                else:
                    heapq.heappush(priority_queue,connection)
            distance_from_source = {point[0]:point[1] for point in self.graph[priority_queue[0][1]] if point[0] not in visited}
            distance_from_source['source'] = priority_queue[0]
            current_connections_costs = {node[1]:node[0] for node in priority_queue if node[1] in distance_from_source}
            for point,dist in current_connections_costs.items():
                if dist - distance_from_source['source'][0] == distance_from_source[point]:
                    dist_point_and_prev[point] = distance_from_source['source'][1]
            popped_val = heapq.heappop(priority_queue)
            visited.append(popped_val[1])
            if popped_val[1] == end_point:
                path = [end_point]
                while path[-1] != start_point:
                    path.append(list({k:v for k,v in dist_point_and_prev.items() if k == path[-1]}.values())[0])
                path.reverse()
                return {'cost':popped_val[0],'path':path}
        return None


