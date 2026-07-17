class Connection:
    
    l_connections = []
    
    def __init__(self,tuple_connections,metadata):
        self.tuple_connections = tuple_connections
        self.metadata = metadata
        Connection.l_connections.append(self)
    
    @classmethod
    def get_connections_from_source_point(cls,source_point_name):
        return [connection for connection in cls.l_connections if connection.tuple_connections[0] == source_point_name]
    
    @classmethod
    def get_connection(cls,source_point_name,target_point_name):
        return [connection for connection in cls.l_connections if connection.tuple_connections[0] == source_point_name and connection.tuple_connections[1] == target_point_name][0]
