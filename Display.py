
class Display:
    def __init__(self,pygame,data):
        self.pygame = pygame
        self.config_data = data
    
    def __enter__(self):
        self.pygame.init()
        return self
    
    def __exit__(self,exc_type,exc_val,exc_tb):
        self.pygame.quit()
    
    def display_window(self,x,y):
        self.screen = self.pygame.display.set_mode((x,y))
        background = self.pygame.image.load('surfaces/background.jpg')
        background = self.pygame.transform.scale(background,(x,y))
        drone_image = self.pygame.image.load('surfaces/drone.png')
        drone_image = self.pygame.transform.scale(drone_image,(30,30))
        running = True
        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
            self.screen.blit(background,(0,0))
            self.draw_zones()
            for i in range(0,self.config_data['nb_drones']):
                self.display_drone(drone_image)
            
            self.pygame.display.flip()

    def display_drone(self,drone_image):
        coordinates_start = [zone['coordinates'] for zone in self.config_data['zones'] if zone['type'] == 'start_hub'][0]
        self.screen.blit(drone_image,((coordinates_start[0] * 10) + 20,(coordinates_start[1] * 10) + 20))
    
    def draw_zones(self):
        for zone in self.config_data['zones']:
            print(zone['coordinates'])
            self.pygame.draw.circle(self.screen, (255, 0, 0), ((zone['coordinates'][0]*100)+50, (zone['coordinates'][1]*100)+50), 20)
        
    
        
