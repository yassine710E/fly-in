from Zone import Zone
from Drone import Drone
from Connection import Connection

def get_target_zones_object(target_connections):
    connected_target_zones = []

    for connection in target_connections:
        zone = Zone.get_zone_by_its_prop(connection.tuple_connections[1], 'name')
        if zone.shortest_path_from_current_hub_to_end != None and zone.metadata['zone'] != 'blocked' and (len(zone.l_drones) < zone.metadata['max_drones'] or zone.type == "end_hub"):
            connected_target_zones.append(zone)
    connected_target_zones.sort(key=lambda x: (x.metadata['zone'] != 'priority', x.shortest_path_from_current_hub_to_end,len(x.l_drones)))    
    return connected_target_zones

def main_simulation(l_drones_end):
        history = []
        
        initial_positions = {}
        for z in Zone.l_zones:
            for drone in z.l_drones:
                initial_positions[drone.id] = z.name
        history.append(initial_positions)

        turn_counter = 0
        while len(l_drones_end) != len(Drone.l_drones):
            hubs = [hub for hub in Zone.l_zones if hub.l_drones and hub.type != 'end_hub']
            hubs.sort(key=lambda x: (x.shortest_path_from_current_hub_to_end))
            for hub in hubs:
                if Zone.costs[hub.metadata['zone']] and hub.current_cost == Zone.costs[hub.metadata['zone']]:
                    connected_target_zones = Connection.get_connections_from_source_point(hub.name)
                    target_zones_object = get_target_zones_object(connected_target_zones)
                    Zone.travel_to_other_hubs(hub, target_zones_object,hub)
                    hub.current_cost = 1
                elif Zone.costs[hub.metadata['zone']] and hub.current_cost < Zone.costs[hub.metadata['zone']]:
                    hub.current_cost += 1
            turn_counter += 1
            turn_positions = {}
            for z in Zone.l_zones:
                for drone in z.l_drones:
                    turn_positions[drone.id] = z.name
            history.append(turn_positions)
        return history
