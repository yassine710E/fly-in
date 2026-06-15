import sys
from Parser import Parser,ParsingError
import pygame
from Display import Display

if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        parser_object = Parser(file_name)
        config_data = parser_object.parsing()
        #declaring Display Object
        with Display(pygame,config_data) as d:
            d.display_window(1900,800)  
              
    except ParsingError as e:
        print(e)
