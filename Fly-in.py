import sys
from Parser import Parser,ParsingError
import pygame
from Display import Display

if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        parser_object = Parser(file_name)
        config_data = parser_object.parsing()
        max_x,min_x = max(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0],min(config_data['zones'],key=lambda zone : zone['coordinates'][0])['coordinates'][0]
        max_y,min_y = max(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1],min(config_data['zones'],key=lambda zone : zone['coordinates'][1])['coordinates'][1]
        # print(config_data)
        #declaring Display Object
        with Display(pygame,config_data,min_x,min_y) as d:
            d.display_window(((max_x-min_y)*70)+100,((max_y-min_y)*70)+100)  
        
              
    except ParsingError as e:
        print(e)
