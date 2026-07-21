from Zone import Zone
from Connection import Connection
import types
import pygame


class Display:
    """Handles rendering of zones, connections, and animated drones in Pygame.

    Attributes:
        pygame (types.ModuleType): The Pygame module reference.
        history (list): Historical timeline of drone positions across turns.
        zone_coords (dict): Screen coordinates computed for each zone name.
        DRONE_RADIUS (int): Fallback circle radius when drone image is missing.
        offset_x (float): Horizontal screen centering offset.
        offset_y (float): Vertical screen centering offset.
    """

    def __init__(self, pygame: types.ModuleType, history: list):
        """Initialize Display instance attributes.

        Args:
            pygame (types.ModuleType): Pygame library module instance.
            history (list): Log of drone position states per turn.
        """
        self.pygame = pygame
        self.history = history
        self.zone_coords: dict = {}
        self.DRONE_RADIUS = 15  # Fallback radius when drone.png is missing
        self.offset_x: float = 0
        self.offset_y: float = 0

    def __enter__(self) -> 'Display':
        """Context manager entry point initializing Pygame and fonts.

        Returns:
            Display: The initialized Display instance.
        """
        self.pygame.init()
        self.pygame.font.init()
        return self

    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None:
        """Context manager exit point releasing Pygame resources.

        Args:
            exc_type (None): Exception type if raised.
            exc_val (None): Exception value if raised.
            exc_tb (None): Exception traceback if raised.
        """
        self.pygame.quit()

    # ------------------------------------------------------------------
    # Coordinate system
    # ------------------------------------------------------------------
    def _compute_fit_scale(self, screen_width: int,
                           screen_height: int,
                           margin: int = 50) -> float:
        """Base scale that makes the map fill the available window space,
        regardless of how sparse/dense the grid is. A small/easy map
        (few zones close together) gets a LARGER base scale so it still
        stretches to fill the screen -> zones spread out, connections
        end up longer. A big/dense map gets a smaller base scale so it
        still fits. Independent from the user's manual zoom.

        Args:
            screen_width (int): Current window width in pixels.
            screen_height (int): Current window height in pixels.
            margin (int): Surrounding outer padding margin.

        Returns:
            float: Scale multiplier fitting map within window boundaries.
        """
        map_grid_w = Zone.max_x() - Zone.min_x() + 1
        map_grid_h = Zone.max_y() - Zone.min_y() + 1

        map_px_w_at_1 = map_grid_w * 50
        map_px_h_at_1 = map_grid_h * 50

        available_w = screen_width - margin * 2
        available_h = screen_height - margin * 2

        return min(available_w / map_px_w_at_1, available_h / map_px_h_at_1)

    def _update_transform(self, screen_width: int,
                          screen_height: int,
                          effective_scale: float) -> None:
        """Recompute the offset needed to keep the whole map centered in the
        window, given the final effective_scale (fit_scale * user_zoom).
        Every drawing routine (zones, connections, drones) must go through
        zone_to_screen() so they always agree on where things are.

        Args:
            screen_width (int): Window width in pixels.
            screen_height (int): Window height in pixels.
            effective_scale (float): Scale resulting from fit and user zoom.
        """
        map_grid_w = Zone.max_x() - Zone.min_x() + 1
        map_grid_h = Zone.max_y() - Zone.min_y() + 1

        map_px_w = map_grid_w * 50 * effective_scale
        map_px_h = map_grid_h * 50 * effective_scale

        self.offset_x = (screen_width - map_px_w) / 2
        self.offset_y = (screen_height - map_px_h) / 2

    def zone_to_screen(self, grid_x: int,
                       grid_y: int,
                       effective_scale: float) -> tuple:
        """Convert grid coordinates to screen pixel coordinates.

        Args:
            grid_x (int): Horizontal grid coordinate.
            grid_y (int): Vertical grid coordinate.
            effective_scale (float): Current effective scaling factor.

        Returns:
            tuple: Transformed (x, y) screen position tuple.
        """
        x = self.offset_x + ((grid_x - Zone.min_x()) *
                             50 + 25) * effective_scale
        y = self.offset_y + ((grid_y - Zone.min_y()) *
                             50 + 25) * effective_scale
        return x, y

    def _refresh_zone_coords(self, effective_scale: float) -> None:
        """Update cached screen positions for all existing zones.

        Args:
            effective_scale (float): Current effective scaling factor.
        """
        for zone in Zone.l_zones:
            gx, gy = zone.coordinates[0], zone.coordinates[1]
            self.zone_coords[zone.name] = self.zone_to_screen(
                gx, gy, effective_scale)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def display_window(self) -> None:
        """Run Pygame main loop rendering zones, connections, and drones."""
        width = 1800
        height = 900
        font = self.pygame.font.SysFont('Arial', 18, bold=True)
        screen = self.pygame.display.set_mode((width, height))
        clock = self.pygame.time.Clock()

        bg_image = self.pygame.image.load("surfaces/background.jpg").convert()
        bg_image = self.pygame.transform.scale(bg_image, (width, height))

        try:
            base_drone_image = self.pygame.image.load(
                'surfaces/drone.png').convert_alpha()
        except Exception:
            base_drone_image = None

        running = True
        ZOOM_SPEED = 0.1
        MIN_ZOOM = 0.5
        MAX_ZOOM = 4.0
        user_zoom = 1.0  # multiplier on top of the auto-fit scale

        current_turn_idx = 0
        progress = 0.0
        speed = 0.02

        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.MOUSEWHEEL:
                    user_zoom += event.y * ZOOM_SPEED
                    user_zoom = max(MIN_ZOOM, min(MAX_ZOOM, user_zoom))
                if event.type == self.pygame.QUIT:
                    running = False

            screen.fill('blue')
            screen.blit(bg_image, (0, 0))

            # 1) Base scale that stretches the map to fill the window,
            #    whether it's a small/sparse map or a huge dense one
            fit_scale = self._compute_fit_scale(width, height)
            # 2) User wheel-zoom is a multiplier on top of that
            zoom_scale = fit_scale * user_zoom

            # 3) Recompute the centered transform for this frame's scale
            self._update_transform(width, height, zoom_scale)
            # 4) Refresh zone screen-coords ONCE, everything
            # else reads from here
            self._refresh_zone_coords(zoom_scale)

            # Connections drawn first (under the zone circles), using the
            # exact same coordinates the zones will be drawn at
            self.draw_connections(screen, zoom_scale)
            self.draw_zones(screen, zoom_scale)

            total_turns = len(self.history) - 1

            if current_turn_idx < total_turns:
                progress += speed
                if progress >= 1.0:
                    progress = 0.0
                    current_turn_idx += 1
            else:
                progress = 1.0

            current_positions = self.history[current_turn_idx]
            next_positions = self.history[min(
                current_turn_idx + 1, total_turns)]

            drone_size = max(4, int(30 * zoom_scale))
            if base_drone_image:
                drone_image = self.pygame.transform.scale(
                    base_drone_image, (drone_size, drone_size))
            else:
                drone_image = None

            for drone_id, current_zone in current_positions.items():
                if current_zone not in self.zone_coords:
                    continue
                start_px, start_py = self.zone_coords[current_zone]

                next_zone = next_positions.get(drone_id, current_zone)
                target_px, target_py = self.zone_coords[next_zone]

                animated_x = start_px + (target_px - start_px) * progress
                animated_y = start_py + (target_py - start_py) * progress

                if drone_image:
                    screen.blit(drone_image, (animated_x -
                                drone_size // 2, animated_y - drone_size // 2))
                else:
                    self.pygame.draw.circle(
                        screen,
                        (255, 0, 0),
                        (int(animated_x), int(animated_y)),
                        int(self.DRONE_RADIUS * zoom_scale),
                    )

            turn_text = f"Turn: {current_turn_idx} / {total_turns}"
            text_surface = font.render(turn_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(10, 10))
            self.pygame.draw.rect(screen, (0, 0, 0, 180),
                                  text_rect.inflate(10, 6))
            screen.blit(text_surface, text_rect)

            self.pygame.display.flip()
            clock.tick(200)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_zones(self, screen: pygame.Surface, zoom_scale: float) -> None:
        """Render all zone circles and borders onto the target screen.

        Args:
            screen (pygame.Surface): Surface to render zones onto.
            zoom_scale (float): Current effective zoom factor.
        """
        for zone in Zone.l_zones:
            x, y = self.zone_coords[zone.name]

            self.pygame.draw.circle(
                screen, self.pygame.color.THECOLORS[zone.metadata['color']],
                (x, y), 20 * zoom_scale
            )
            border_color = self.pygame.color.THECOLORS['white']
            border_thickness = max(1, int(2 * zoom_scale))
            self.pygame.draw.circle(
                screen, border_color,
                (x, y), 20 * zoom_scale, width=border_thickness)

    def draw_connections(self, screen: pygame.Surface,
                         zoom_scale: float) -> None:
        """Render connection lines between zones onto the target screen.

        Args:
            screen (pygame.Surface): Surface to render connections onto.
            zoom_scale (float): Current effective zoom factor.
        """
        for connection in Connection.l_connections:
            zone1_name = connection.tuple_connections[0]
            zone2_name = connection.tuple_connections[1]

            x_1, y_1 = self.zone_coords[zone1_name]
            x_2, y_2 = self.zone_coords[zone2_name]

            self.pygame.draw.line(
                screen, 'white', (x_1, y_1),
                (x_2, y_2), max(1, int(2 * zoom_scale)))
