import heapq
class Algo:
    def dijkstra(self,graph,start_point,end_point):
        visited = []
        priority_queue = []
        heapq.heappush(priority_queue,(0,start_point))
        while priority_queue:
            connections = [(point[1]+priority_queue[0][0],point[0]) for point in graph[priority_queue[0][1]] if point[0] not in visited]
            for connection in connections:
                if connection[1] in [node[1] for node in priority_queue]:
                    node_from_pq = [node for node in priority_queue if node[1] == connection[1]][0]
                    if connection[0] < node_from_pq[0]:
                        priority_queue = [connection if connection[1] == node[1] else node for node in priority_queue]
                else:
                    heapq.heappush(priority_queue,connection)
            popped_val = heapq.heappop(priority_queue)
            if popped_val[1] == end_point:
                print(popped_val)
            visited.append(popped_val[1])
        
        

if __name__ == "__main__":
    
    obj = Algo()
    map_network = {
    'A': [('B', 10), ('C', 1)],
    'B': [('A', 10), ('D', 1)],
    'C': [('A', 1), ('D', 20), ('E', 2)],
    'D': [('B', 1), ('C', 20), ('F', 1)],
    'E': [('C', 2), ('F', 2)],
    'F': [('D', 1), ('E', 2)]
}

obj.dijkstra(map_network, 'A', 'F')



