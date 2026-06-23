class Display:
    def __init__(self, pygame, data, min_x, min_y, dijkstra_output):
        self.pygame = pygame
        self.config_data = data
        self.min_x = min_x
        self.min_y = min_y
        self.dijkstra_output = dijkstra_output

    def __enter__(self):
        self.pygame.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pygame.quit()

    def display_window(self, x, y):
        self.screen = self.pygame.display.set_mode((x, y))

        background = self.pygame.image.load('surfaces/background.jpg')
        background = self.pygame.transform.scale(background, (x, y))

        drone_image = self.pygame.image.load('surfaces/drone.png')
        drone_image = self.pygame.transform.scale(drone_image, (30, 30))

        clock = self.pygame.time.Clock()
        running = True

        path = self.dijkstra_output['path']
        index = 0
        speed = 2

        coordinates_start = [
            zone['coordinates']
            for zone in self.config_data['zones']
            if zone['name'] == path[index]
        ][0]

        coordinates_target = [
            zone['coordinates']
            for zone in self.config_data['zones']
            if zone['name'] == path[index + 1]
        ][0]

        start_x, start_y = (
            ((coordinates_start[0] - self.min_x) * 70) + 50 - 15,
            ((coordinates_start[1] - self.min_y) * 70) + 50 - 15
        )

        target_x, target_y = (
            ((coordinates_target[0] - self.min_x) * 70) + 50 - 15,
            ((coordinates_target[1] - self.min_y) * 70) + 50 - 15
        )

        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False

            dx = target_x - start_x
            dy = target_y - start_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= speed:
                start_x = target_x
                start_y = target_y

                index += 1

                if index + 1 < len(path):
                    coordinates_target = [
                        zone['coordinates']
                        for zone in self.config_data['zones']
                        if zone['name'] == path[index + 1]
                    ][0]

                    target_x, target_y = (
                        ((coordinates_target[0] - self.min_x) * 70) + 50 - 15,
                        ((coordinates_target[1] - self.min_y) * 70) + 50 - 15
                    )
            else:
                start_x += dx / distance * speed
                start_y += dy / distance * speed

            self.screen.blit(background, (0, 0))
            self.draw_connections()
            self.draw_zones()

            self.screen.blit(drone_image, (start_x, start_y))

            self.pygame.display.flip()
            clock.tick(120)

    def display_drone(self, drone_image):
        coordinates_start = [
            zone['coordinates']
            for zone in self.config_data['zones']
            if zone['type'] == 'start_hub'
        ][0]

        self.screen.blit(
            drone_image,
            (
                ((coordinates_start[0] - self.min_x) * 70) + 50 - 15,
                ((coordinates_start[1] - self.min_y) * 70) + 50 - 15
            )
        )

    def draw_zones(self):
        for zone in self.config_data['zones']:
            self.pygame.draw.circle(
                self.screen,
                self.pygame.color.THECOLORS[zone['metadata']['color']],
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