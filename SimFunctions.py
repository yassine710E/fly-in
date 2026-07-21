from Zone import Zone
from Drone import Drone
from Connection import Connection


def get_target_zones_object(
        target_connections: list['Connection']) -> list['Zone']:
    """Filter and sort eligible target zones based on capacity and path cost.

    Args:
        target_connections (list[Connection]): List of candidate outbound
            connection objects from the source hub.

    Returns:
        list[Zone]: Sorted list of valid destination Zone objects prioritized
            by priority status, path cost to the end hub, and drone load.
    """
    connected_target_zones = []

    for connection in target_connections:
        zone = Zone.get_zone_by_its_prop(
            connection.tuple_connections[1], 'name')
        if (isinstance(zone, Zone)
            and zone.shortest_path_from_current_hub_to_end is not None
            and zone.metadata['zone'] != 'blocked'
            and (len(zone.l_drones) < zone.metadata['max_drones']
                 or zone.type == "end_hub")):
            connected_target_zones.append(zone)
    connected_target_zones.sort(key=lambda x: (
        x.metadata['zone'] != 'priority',
        x.shortest_path_from_current_hub_to_end, len(x.l_drones)))
    return connected_target_zones


def main_simulation(l_drones_end: list['Drone']) -> list[dict]:
    """Execute the multi-turn drone movement simulation until all reach end.

    Args:
        l_drones_end (list[Drone]): List tracking drones that have arrived
            at the designated end hub.

    Returns:
        list[dict]: Historical record mapping drone IDs to zone names for
            each turn in the simulation.
    """
    history = []
    initial_positions = {}
    for z in Zone.l_zones:
        for drone in z.l_drones:
            initial_positions[drone.id] = z.name
    history.append(initial_positions)
    turn_counter = 0

    def lambda_func_sort(hub: Zone) -> bool | int:
        """Extract the path cost sorting key for a given hub.

        Args:
            hub (Zone): The zone object to evaluate.

        Returns:
            bool | int: Integer distance to end hub, or False if unreachable.
        """
        cost: int | None = hub.shortest_path_from_current_hub_to_end
        if cost is None:
            return False
        return cost

    while len(l_drones_end) != len(Drone.l_drones):
        hubs = [hub for hub in Zone.l_zones
                if hub.l_drones and hub.type != 'end_hub']
        hubs.sort(key=lambda_func_sort)
        for hub in hubs:
            zone_cost = Zone.costs[hub.metadata['zone']]
            if (zone_cost
                    and hub.current_cost == zone_cost):
                connected_z = Connection.get_connections_from_source_point(
                    hub.name)
                target_zones_object = get_target_zones_object(
                    connected_z)
                Zone.travel_to_other_hubs(hub, target_zones_object)
                hub.current_cost = 1
            elif (zone_cost is not None
                  and hub.current_cost < zone_cost):
                print(f'D{hub.l_drones[-1].id}-{hub.name}', end=" ")
                hub.current_cost += 1
        turn_counter += 1
        print()
        turn_positions = {}
        for z in Zone.l_zones:
            for drone in z.l_drones:
                turn_positions[drone.id] = z.name
        history.append(turn_positions)
    return history
