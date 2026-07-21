class Connection:
    """Represents a directional connection between source and target points.

    Attributes:
        l_connections (list[Connection]): Class-level registry of all created
            connections.
        tuple_connections (tuple): Pair of (source_point_name,
            target_point_name).
        metadata (dict): Additional attributes or properties of the connection.
    """

    l_connections: list['Connection'] = []

    def __init__(self, tuple_connections: tuple, metadata: dict) -> None:
        """Initialize a Connection instance and register it in l_connections.

        Args:
            tuple_connections (tuple): Source and target point names.
            metadata (dict): Additional connection details.
        """
        self.tuple_connections = tuple_connections
        self.metadata = metadata
        Connection.l_connections.append(self)

    @classmethod
    def get_connections_from_source_point(
        cls,
        source_point_name: str
    ) -> list['Connection']:
        """Retrieve all connections originating from a given source point.

        Args:
            source_point_name (str): Name of the source point.

        Returns:
            list[Connection]: Matching Connection instances.
        """
        return [connection for connection in cls.l_connections
                if connection.tuple_connections[0] == source_point_name]

    @classmethod
    def get_connection(
            cls,
            source_point_name: str,
            target_point_name: str) -> 'Connection':
        """Retrieve a connection matching a specific source and target pair.

        Args:
            source_point_name (str): Name of the source point.
            target_point_name (str): Name of the target point.

        Returns:
            Connection: The matching Connection instance.
        """
        return [connection for connection in cls.l_connections
                if connection.tuple_connections[0] == source_point_name
                and connection.tuple_connections[1] == target_point_name][0]
