*This project has been created as part of the 42 curriculum by ychabane.*

# Fly-in

## Description

Fly-in is a drone routing simulator. Given a map of interconnected zones (a
custom text format) and a fleet size, it computes the shortest cost path from
the `start_hub` to the `end_hub` with Dijkstra, then runs a turn-based
multi-agent simulation that moves every drone from the start to the end zone
while respecting zone capacities, connection capacities, and per-zone
movement costs (`normal`, `restricted`, `priority`, `blocked`). The goal is
to deliver all drones to the end zone in the fewest possible simulation
turns.

The project is split into fully object-oriented modules:

- `Parser.py` — reads and validates the map file, producing zones,
  connections and the drone count.
- `Zone.py` — represents a zone/hub, its metadata, coordinates and occupancy.
- `Connection.py` — represents a bidirectional link between two zones.
- `Drone.py` — represents a single drone and its assigned path.
- `Algo.py` — builds the adjacency graph and runs Dijkstra to find the
  shortest cost path between two zones.
- `SimFunctions.py` — the turn-by-turn simulation engine that moves drones
  according to zone/connection capacity, path cost and priority rules.
- `Display.py` — Pygame-based visual replay of the simulation (zones,
  connections, animated drones, zoom/pan).
- `Fly-in.py` — entry point that wires the parser, the algorithm, the
  simulation and the display together.

## Instructions

Dependencies are listed in `requirements.txt` (`pygame`, `flake8`, `mypy`).

```bash
make install   # install dependencies
make run SRC=<path_to_map_file>   # run the simulation on a given map file
make lint      # flake8 + mypy checks
make clean     # remove __pycache__ and .mypy_cache
```

Example:

```bash
make run SRC=maps/easy_2.txt
```

The program prints, turn by turn, the movement of every drone
(`D<ID>-<zone>` or `D<ID>-<connection>` for drones in transit toward a
restricted zone), then opens a Pygame window replaying the whole simulation.

## Resources

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Pygame documentation](https://www.pygame.org/docs/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/)

**AI usage:** AI assistance was used to help design the parsing logic (regex
validation for hubs/connections/metadata) and to review the Dijkstra and
simulation scheduling logic for edge cases (capacity conflicts, restricted
zone transit). All AI-suggested code was read, tested and understood line by
line before being kept in the project; peers were involved in reviewing the
pathfinding and simulation logic.

## Algorithm choices and implementation strategy

- **Pathfinding:** `Algo.py` builds an adjacency list from `Connection`
  objects, using a per-zone-type cost (`normal`/`priority` = 1,
  `restricted` = 2, `blocked` = unreachable), then runs a Dijkstra variant
  implemented with a `heapq`-based priority queue. Ties are broken in favor
  of `priority` zones, so the algorithm naturally prefers preferred zones
  when several paths have the same cost. No external graph library is used,
  in line with the subject's constraint.
- **Path caching:** each zone's shortest distance and path to the end hub is
  precomputed once (`Zone.set_shortest_path`) rather than recomputed every
  turn, which keeps the simulation loop cheap.
- **Scheduling / multi-drone movement:** `SimFunctions.main_simulation` runs
  turn by turn. At each turn, hubs are processed in order of their distance
  to the end hub, and for each hub, candidate target zones are filtered by
  capacity/blocked status and sorted by priority status, path cost, then
  current load (`get_target_zones_object`). Drones are only moved once a
  zone has paid its full movement cost (`current_cost` counter reaching the
  zone's cost), which enforces the 1-turn/2-turn movement rules without a
  separate "in transit" state.
- **Capacity handling:** zone occupancy (`max_drones`) and connection
  throughput (`max_link_capacity`) are checked before any drone is moved
  into a target zone, and only one path per turn is used per zone
  (`source.name not in target_zone.path`) to avoid immediate backtracking.
- **Complexity:** Dijkstra runs in roughly O((V + E) log V) with the
  heap-based queue; it's run once per zone to precompute distances to the
  end hub, so overall setup is O(V · (V + E) log V). The simulation loop
  itself is O(turns × hubs) per run, which stays cheap since paths are
  cached and not recalculated.

## Visual representation

`Display.py` provides a Pygame-based graphical replay of the full
simulation history:

- Zones are drawn as colored circles (using each zone's `color` metadata)
  connected by lines representing the map's connections.
- Drones are animated moving smoothly between zone positions turn by turn,
  using either a `drone.png` sprite or a fallback colored circle.
- The map automatically scales and centers itself to fit the window
  regardless of map size (`_compute_fit_scale` / `_update_transform`), and
  supports mouse-wheel zoom.
- An on-screen counter shows the current turn out of the total number of
  turns, making it easy to follow the simulation's progress and verify
  correctness at a glance.
