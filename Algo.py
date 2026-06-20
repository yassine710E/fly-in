class Algo:
    def dijkstra(self,graph,start_point,end_point):
        costs = {n_k : float('inf') for n_k in graph.keys()}
        costs[start_point] = 0
        visited = [start_point]
        stack_path = [(start_point,0)]
        while stack_path[-1][0] != end_point:
            connected_nodes = [c for c in graph[stack_path[-1][0]] if c[0] not in visited]
            if not connected_nodes:
                break
            for node in connected_nodes:
                if stack_path[-1][1] + node[1] < costs[node[0]]:
                     costs[node[0]] = stack_path[-1][1] + node[1]
                if len(stack_path) >= 2 and [node for node in graph[stack_path[-1][0]] if node[0] == stack_path[-2][0]] and  stack_path[-1][1] - stack_path[-2][1] != [node for node in graph[stack_path[-1][0]] if node[0] == stack_path[-2][0]][0][1] :
                     stack_path.pop(-2)
            min_node_key = min(connected_nodes,key=lambda x : x[1])[0]
            stack_path.append((min_node_key,costs[min_node_key]))
            visited.append(min_node_key)
            if len(stack_path) >= 2 and [node for node in graph[stack_path[-1][0]] if node[0] == stack_path[-2][0]] and  stack_path[-1][1] - stack_path[-2][1] != [node for node in graph[stack_path[-1][0]] if node[0] == stack_path[-2][0]][0][1] :
                     stack_path.pop(-2)
        print(stack_path)

if __name__ == "__main__":

    obj = Algo()    
    graph = {
    'A': [('B', 7),('C',9),('E',14)],
    'B': [('D', 15),('C',10)],
    'C': [('A', 9),('B',7), ('D', 11),  ('E', 6)],
    'D': [('B', 15), ('C', 11)],
    'E': [('C', 6), ('A',14)],
}

obj.dijkstra(graph, 'A', 'E')

