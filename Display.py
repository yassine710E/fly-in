from Zone import Zone
from Connection import Connection
from Drone import Drone

class Display:
    def __init__(self, pygame, history):
        self.pygame = pygame
        self.history = history
        self.zone_coords = {}
        self.DRONE_RADIUS = 15  # Added fallback radius just in case

    def __enter__(self):
        self.pygame.init()
        self.pygame.font.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pygame.quit()

    def display_window(self):
        width = 1800
        height = 900
        font = self.pygame.font.SysFont('Arial', 18, bold=True)
        screen = self.pygame.display.set_mode((width, height))
        clock = self.pygame.time.Clock()
        
        # Load background outside the loop
        bg_image = self.pygame.image.load("surfaces/background.jpg").convert()
        bg_image = self.pygame.transform.scale(bg_image, (width, height))
        
        # --- FIX 1: Load base drone image OUTSIDE the loop for performance ---
        try:
            base_drone_image = self.pygame.image.load('surfaces/drone.png').convert_alpha()
        except Exception:
            base_drone_image = None

        running = True
        ZOOM_SPEED = 0.1
        MIN_ZOOM = 0.5
        MAX_ZOOM = 4.0
        
        mq_width = (Zone.max_x() - Zone.min_x() + 1) * 50
        mq_height = (Zone.max_y() - Zone.min_y() + 1) * 50
        screen_width, screen_height = 1750, 850 
        zoom_scale = min(screen_width / mq_width, screen_height / mq_height)
        
        current_turn_idx = 0
        progress = 0.0
        speed = 0.02  # Adjusted speed for smoother interpolation (lower = slower)

        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.MOUSEWHEEL:
                    zoom_scale += event.y * ZOOM_SPEED
                    zoom_scale = max(MIN_ZOOM, min(MAX_ZOOM, zoom_scale))
                if event.type == self.pygame.QUIT:
                    running = False

            screen.fill('blue')
            screen.blit(bg_image, (0, 0))
            
            # Populate/refresh zone coordinates dynamically 
            self.draw_connections(screen, zoom_scale)
            self.draw_zones(screen, zoom_scale)            
            
            # --- FIX 2: Handle Animation State Progress ---
            total_turns = len(self.history) - 1
            
            if current_turn_idx < total_turns:
                progress += speed
                if progress >= 1.0:
                    progress = 0.0
                    current_turn_idx += 1
            else:
                progress = 1.0  # Snap to final position when history ends

            current_positions = self.history[current_turn_idx]
            next_positions = self.history[min(current_turn_idx + 1, total_turns)]

            # Scale drone image dynamically based on zoom
            drone_size = int(30 * zoom_scale)  # Adjusted down from 100 for better proportion
            if base_drone_image:
                drone_image = self.pygame.transform.scale(base_drone_image, (drone_size, drone_size))
            else:
                drone_image = None

            for drone_id, current_zone in current_positions.items():
                if current_zone not in self.zone_coords:
                    continue
                start_px, start_py = self.zone_coords[current_zone]

                next_zone = next_positions.get(drone_id, current_zone)
                target_px, target_py = self.zone_coords[next_zone]

                # Linear Interpolation (Lerp) for smooth movement
                animated_x = start_px + (target_px - start_px) * progress 
                animated_y = start_py + (target_py - start_py) * progress 

                if drone_image:
                    # Center the image over the zone coordinate
                    screen.blit(drone_image, (animated_x - drone_size // 2, animated_y - drone_size // 2))
                else:
                    self.pygame.draw.circle(
                        screen,
                        (255, 0, 0),
                        (int(animated_x), int(animated_y)),
                        int(self.DRONE_RADIUS * zoom_scale),
                    )

            # Draw Turn Text HUD
            turn_text = f"Turn: {current_turn_idx} / {total_turns}"
            text_surface = font.render(turn_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(10, 10))
            self.pygame.draw.rect(screen, (0, 0, 0, 180), text_rect.inflate(10, 6))
            screen.blit(text_surface, text_rect)

            self.pygame.display.flip()
            clock.tick(100)
    
    def draw_zones(self, screen, zoom_scale):
        for zone in Zone.l_zones:
            exact_point_x = (zone.coordinates[0]) - Zone.min_x()
            exact_point_y = (zone.coordinates[1]) - Zone.min_y()
            x = int((exact_point_x * 50 + 25) * zoom_scale)
            y = int((exact_point_y * 50 + 25) * zoom_scale)
            self.zone_coords[zone.name] = (x, y)
            
            self.pygame.draw.circle(screen, self.pygame.color.THECOLORS[zone.metadata['color']], (x, y), 20 * zoom_scale)
            border_color = self.pygame.color.THECOLORS['white'] 
            border_thickness = max(1, int(2 * zoom_scale))    
            self.pygame.draw.circle(screen, border_color, (x, y), 20 * zoom_scale, width=border_thickness)

    def draw_connections(self, screen, zoom_scale):
        for connection in Connection.l_connections:
            zone1 = Zone.get_zone_by_its_prop(connection.tuple_connections[0], 'name')
            zone2 = Zone.get_zone_by_its_prop(connection.tuple_connections[1], 'name')
            x_1 = ((((zone1.coordinates[0]) - Zone.min_x()) + 0.5) * 50 * zoom_scale) 
            y_1 = ((((zone1.coordinates[1]) - Zone.min_y()) + 0.5) * 50 * zoom_scale)
            x_2 = ((((zone2.coordinates[0]) - Zone.min_x()) + 0.5) * 50 * zoom_scale) 
            y_2 = ((((zone2.coordinates[1]) - Zone.min_y()) + 0.5) * 50 * zoom_scale) 
            self.pygame.draw.line(screen, 'white', (x_1, y_1), (x_2, y_2), int(2 * zoom_scale))