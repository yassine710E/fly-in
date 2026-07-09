class Display:
    def __init__(self, pygame, data, min_x, min_y, history):
        self.pygame = pygame
        self.config_data = data
        self.min_x = min_x
        self.min_y = min_y
        self.history = history  # List of dicts matching: {drone_id: zone_name}
        
        # Map zone names directly to their pixel positions for quick lookup
        self.zone_coords = {}
        for zone in self.config_data['zones']:
            px = ((zone['coordinates'][0] - self.min_x) * 70) + 50
            py = ((zone['coordinates'][1] - self.min_y) * 70) + 50
            self.zone_coords[zone['name']] = (px, py)

    def __enter__(self):
        self.pygame.init()
        self.pygame.font.init()  # Initialize font module for text rendering
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pygame.quit()

    def display_window(self, x, y):
        self.screen = self.pygame.display.set_mode((x, y))
        
        # Set up font for the turn counter
        font = self.pygame.font.SysFont('Arial', 24, bold=True)

        try:
            background = self.pygame.image.load('surfaces/background.jpg')
            background = self.pygame.transform.scale(background, (x, y))
        except:
            background = None

        try:
            drone_image = self.pygame.image.load('surfaces/drone.png')
            drone_image = self.pygame.transform.scale(drone_image, (30, 30))
        except:
            drone_image = None

        clock = self.pygame.time.Clock()
        running = True

        current_turn_idx = 0
        progress = 0.0  
        speed = 0.05    # Controls transition animation speed between turns

        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False

            # Progress the transition state
            if current_turn_idx < len(self.history) - 1:
                progress += speed
                if progress >= 1.0:
                    progress = 0.0
                    current_turn_idx += 1
            else:
                progress = 1.0  

            # Rendering background
            if background:
                self.screen.blit(background, (0, 0))
            else:
                self.screen.fill((30, 30, 30))

            self.draw_connections()
            self.draw_zones()

            # Calculate and draw every drone's current animated spot
            current_positions = self.history[current_turn_idx]
            next_positions = self.history[min(current_turn_idx + 1, len(self.history) - 1)]

            for drone_id, current_zone in current_positions.items():
                start_px, start_py = self.zone_coords[current_zone]
                
                next_zone = next_positions.get(drone_id, current_zone)
                target_px, target_py = self.zone_coords[next_zone]

                animated_x = start_px + (target_px - start_px) * progress - 15
                animated_y = start_py + (target_py - start_py) * progress - 15

                if drone_image:
                    self.screen.blit(drone_image, (animated_x, animated_y))
                else:
                    self.pygame.draw.circle(self.screen, (255, 0, 0), (int(animated_x + 15), int(animated_y + 15)), 8)

            # --- NEW CODE: Render Turn Count Overlay ---
            # Turn index 0 represents the initial state before any movements occur
            total_turns = len(self.history) - 1
            turn_text = f"Turn: {current_turn_idx} / {total_turns}"
            text_surface = font.render(turn_text, True, (255, 255, 255))
            
            # Draw a dark backing box for readability
            text_rect = text_surface.get_rect(topleft=(20, 20))
            self.pygame.draw.rect(self.screen, (0, 0, 0, 180), text_rect.inflate(15, 10))
            self.screen.blit(text_surface, text_rect)
            # --------------------------------------------

            self.pygame.display.flip()
            clock.tick(40)

    def draw_zones(self):
        for zone in self.config_data['zones']:
            color_name = zone['metadata'].get('color', 'white')
            try:
                color = self.pygame.color.THECOLORS[color_name]
            except KeyError:
                color = (255, 255, 255)

            self.pygame.draw.circle(
                self.screen,
                color,
                (
                    ((zone['coordinates'][0] - self.min_x) * 70) + 50,
                    ((zone['coordinates'][1] - self.min_y) * 70) + 50
                ),
                20
            )

    def draw_connections(self):
        for connection in self.config_data['connections']:
            dict_zone_1 = [
                zone for zone in self.config_data['zones']
                if zone['name'] == connection['tuple_connections'][0]
            ][0]

            dict_zone_2 = [
                zone for zone in self.config_data['zones']
                if zone['name'] == connection['tuple_connections'][1]
            ][0]

            self.pygame.draw.line(
                self.screen,
                (0, 255, 0),
                (
                    ((dict_zone_1['coordinates'][0] - self.min_x) * 70) + 50,
                    ((dict_zone_1['coordinates'][1] - self.min_y) * 70) + 50
                ),
                (
                    ((dict_zone_2['coordinates'][0] - self.min_x) * 70) + 50,
                    ((dict_zone_2['coordinates'][1] - self.min_y) * 70) + 50
                ),
                2
            )