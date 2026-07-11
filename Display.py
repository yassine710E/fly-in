from Zone import Zone
from Connection import Connection

class Display:
    def __init__(self, pygame, data):
        self.pygame = pygame
        self.config_data = data
        

    def __enter__(self):
        self.pygame.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pygame.quit()

    def display_window(self):
        width = 1500
        height = 700
        screen = self.pygame.display.set_mode((width,height))
        clock = self.pygame.time.Clock()
        bg_image = self.pygame.image.load("surfaces/background.jpg").convert()
        bg_image = self.pygame.transform.scale(bg_image, (width, height))
        running = True
        ZOOM_SPEED = 0.1
        MIN_ZOOM = 0.5
        MAX_ZOOM = 4.0
        zoom_scale = 1.0
        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.MOUSEWHEEL:
                    zoom_scale += event.y * ZOOM_SPEED
                    zoom_scale = max(MIN_ZOOM,min(MAX_ZOOM,zoom_scale))

                if event.type == self.pygame.QUIT:
                    running = False
            
            screen.fill('blue')
            screen.blit(bg_image, (0, 0))
            i = 0
            while i < width*2:
                self.pygame.draw.line(screen,self.pygame.color.THECOLORS['white'],(i*zoom_scale,0),(i*zoom_scale,(height-1)))
                i += 50
            i = 0
            while i < height*2:
                self.pygame.draw.line(screen,self.pygame.color.THECOLORS['white'],(0,i*zoom_scale),((width-1),i*zoom_scale))
                i+= 50
            self.draw_zones(screen,width,height,zoom_scale)
            
            tmp_x = 0
            tmp_y = 0
            self.pygame.draw.circle(screen,self.pygame.color.THECOLORS['blue'],((2+((width//2)-1))*zoom_scale,(0+((height//2)-1))*zoom_scale),20*zoom_scale)
            self.pygame.draw.circle(screen,self.pygame.color.THECOLORS['red'],((52+((width//2)-1))*zoom_scale,(0+((height//2)-1))*zoom_scale),20*zoom_scale)
            
            self.draw_connections()
            self.pygame.display.flip()
            clock.tick(60)
    
    def draw_zones(self,screen,width,height,zoom_scale):
        i = 0
        for zone in Zone.l_zones:
            print(zone.name,zone.coordinates)

            # i += 50
    def draw_connections(self):
        for connection in Connection.l_connections:
            pass