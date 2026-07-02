class Connection:
    
    l_connections = []
    
    def __init__(self,tuple_connections,metadata):
        self.tuple_connections = tuple_connections
        self.metadata = metadata
        Connection.l_connections.append(self)
    
    @classmethod
    def get_connections_from_source_point(cls,source_point_name):
        return [connection for connection in cls.l_connections if connection.tuple_connections[0] == source_point_name]
    
        