import heapq

class Algo:
    def __init__(self,connections,zones):
        self.connections = connections
        self.zones = zones
        self.costs = {'normal':1,'restricted':2,'priority':1,'blocked':None}
        self.graph = dict()
        self.priority_zones = set()
        self.create_graph()
        
    def create_graph(self):
        for connection in self.connections:
            obj_start = connection.start_and_target_objects['start']
            obj_target = connection.start_and_target_objects['target']
            if obj_target.metadata['zone'] == 'priority':
                self.priority_zones.add(obj_target.name)
            if obj_start.metadata['zone'] == 'priority':
                self.priority_zones.add(obj_start.name)
            if self.costs[obj_target.metadata['zone']]:
                if self.graph.get(obj_start.name) is None:
                    self.graph[obj_start.name] = []
                self.graph[obj_start.name].append((obj_target.name,self.costs[obj_target.metadata['zone']]))                   
            if self.costs[obj_start.metadata['zone']]:
                if self.graph.get(obj_target.name) is None:
                    self.graph[obj_target.name] = []
                self.graph[obj_target.name].append((obj_start.name,self.costs[obj_start.metadata['zone']]))                   
    
    def dijkstra(self,start_point,end_point):
        # start_point = [zone.name for zone in self.zones if zone.type == 'start_hub'][0]
        # end_point = [zone.name for zone in self.zones if zone.type == 'end_hub'][0]
        visited = []
        priority_queue = []
        dist_point_and_prev = {start_point : None}
        heapq.heappush(priority_queue,(0,start_point))
        
        while priority_queue:
            if self.graph.get(priority_queue[0][1]) is None:
                return None
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
                    if not (dist_point_and_prev.get(point) and dist_point_and_prev[point] in self.priority_zones):
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


