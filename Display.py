from Zone import Zone
from Connection import Connection
import types


class Display:
    """Simplified display class for rendering zones, connections, and
    drones.
    """

    def __init__(self, pygame_module: types.ModuleType, history: list):
        self.pygame = pygame_module
        self.history = history
        self.width = 1200
        self.height = 800
        self.margin = 80
        self.current_turn = 0

    def __enter__(self) -> "Display":
        """Context manager entry point initializing Pygame."""
        self.pygame.init()
        self.pygame.font.init()
        return self

    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None:
        """Context manager exit point releasing Pygame resources."""
        self.pygame.quit()

    def grid_to_screen(self, grid_x: int, grid_y: int) -> tuple[int, int]:
        """Maps grid coordinates directly to screen pixels fitting any
        map size.
        """
        min_x, max_x = Zone.min_x(), Zone.max_x()
        min_y, max_y = Zone.min_y(), Zone.max_y()

        # Prevent division by zero if map is 1x1 grid
        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        usable_w = self.width - (self.margin * 2)
        usable_h = self.height - (self.margin * 2)

        screen_x = self.margin + int((grid_x - min_x) / range_x * usable_w)
        screen_y = self.margin + int((grid_y - min_y) / range_y * usable_h)

        return screen_x, screen_y

    def display_window(self) -> None:
        """Main display loop."""
        screen = self.pygame.display.set_mode((self.width, self.height))
        self.pygame.display.set_caption("Drone Simulation Map")
        clock = self.pygame.time.Clock()
        font = self.pygame.font.SysFont("Arial", 20, bold=True)

        running = True
        total_turns = max(0, len(self.history) - 1)

        while running:
            # 1. Event Handling
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
                elif event.type == self.pygame.KEYDOWN:
                    # Press SPACE or RIGHT ARROW to advance turn
                    keys = (self.pygame.K_SPACE, self.pygame.K_RIGHT)
                    if event.key in keys and self.current_turn < total_turns:
                        self.current_turn += 1
                    # Press LEFT ARROW to go back
                    elif event.key == self.pygame.K_LEFT:
                        if self.current_turn > 0:
                            self.current_turn -= 1

            # 2. Clear Screen
            screen.fill((30, 30, 30))  # Dark grey background

            # Cache current screen coordinates for all zones
            zone_positions = {}
            for zone in Zone.l_zones:
                gx, gy = zone.coordinates[0], zone.coordinates[1]
                zone_positions[zone.name] = self.grid_to_screen(gx, gy)

            # 3. Draw Connections (Lines)
            for conn in Connection.l_connections:
                z1, z2 = (
                    conn.tuple_connections[0],
                    conn.tuple_connections[1],
                )
                if z1 in zone_positions and z2 in zone_positions:
                    self.pygame.draw.line(
                        screen,
                        (200, 200, 200),
                        zone_positions[z1],
                        zone_positions[z2],
                        2,
                    )

            # 4. Draw Zones (Circles)
            for zone in Zone.l_zones:
                pos = zone_positions[zone.name]
                color_name = zone.metadata.get("color", "blue")
                color = self.pygame.color.THECOLORS.get(
                    color_name, (0, 0, 255)
                )
                self.pygame.draw.circle(screen, color, pos, 18)
                self.pygame.draw.circle(
                    screen, (255, 255, 255), pos, 18, 2
                )  # Border

            # 5. Draw Drones at current turn positions
            if self.history and self.current_turn < len(self.history):
                positions = self.history[self.current_turn]
                for drone_id, zone_name in positions.items():
                    if zone_name in zone_positions:
                        px, py = zone_positions[zone_name]
                        # Draw pink circle for each drone (255, 105, 180)
                        self.pygame.draw.circle(
                            screen, (255, 105, 180), (px, py), 8
                        )

            # 6. Render Overlay Info
            status = (
                f"Turn: {self.current_turn} / {total_turns} "
                "(Press SPACE / RIGHT ARROW to step)"
            )
            info_text = font.render(status, True, (255, 255, 255))
            screen.blit(info_text, (15, 15))

            self.pygame.display.flip()
            clock.tick(30)
