import re
import pygame

class ParsingError(Exception):
    pass
class Parser:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.metadata = {
            'color':list(pygame.color.THECOLORS.keys()),
            'zone':['normal','blocked','restricted','priority'],
            'max_drones':1
        }
        self.counter_descripted_zones = {'hub':0,'start_hub':0,'end_hub':0}
        self.config_data = {
            'nb_drones':None,
            'zones':[],
            'connections':[]
        }

    def set_content(self)->None:
        try :
            with open(self.file_name,'r') as file:
                self.content = file.read()
        except FileNotFoundError:
            raise ParsingError("Error: The requested file does not exist at this location.")
        except PermissionError:
            raise ParsingError("Error: System permissions deny access to this file.")
        except IsADirectoryError:
            raise ParsingError("Error: The target path points to a directory, not a file.")
        except OSError as error:
            raise ParsingError(f"System I/O failure occurred: {error}")
    
    def check_nb_drones(self,line:str)->None | int:
        splited_line : list[str] = line.split(':') 
        if len(splited_line) != 2:
            return None
        prop:str = (splited_line[0]).strip()
        if prop != "nb_drones":
            return None
        val:str = splited_line[1]
        if not re.search(r"^\s*[1-9]\d*\s*$",val):
            return None
        return int(val.strip())

    def check_hubs(self,line:str)->None | dict:
        splited_line:list[str] = line.split(':')
        if len(splited_line) != 2:
            return None
        striped_prop:str = (splited_line[0]).strip()
        striped_values : str = (splited_line[1]).strip()
        # validate pattern of the sentence
        match = re.search(r"^[^-\s]+\s+-?\d+\s+-?\d+(\s+\[\s*(color|zone|max_drones)\s*=\s*[^\s=\]]+(\s+(color|zone|max_drones)\s*=\s*[^\s=\]]+)*\s*\])?$",striped_values)
        if match is None:
            return None
        arr_props : list[str] = re.findall(r"[^:]\s*(color|zone|max_drones)",striped_values)
        if len(arr_props) != len(set(arr_props)):
            return None
        dict_metadata : dict = dict(re.findall(r"(color|zone|max_drones)\s*=\s*([^\s=\]]+)",striped_values))
        for k,v in dict_metadata.items():
            if k != "max_drones" and v not in self.metadata[k]:
                return None
            elif k == "max_drones":
                try :
                    dict_metadata[k] = int(v)
                    if dict_metadata[k] < 1:
                        return None
                except ValueError as e:
                    return None
        if not dict_metadata.get('zone'):
            dict_metadata['zone'] = 'normal'
        if not dict_metadata.get('color'):
            dict_metadata['color'] = None
        if not dict_metadata.get('max_drones'):
            dict_metadata['max_drones'] = 1

        final_str_l : list = striped_values.split()
        self.counter_descripted_zones[striped_prop]+=1
        coordinates : tuple[int] = (int(final_str_l[1]),int(final_str_l[2]))
        if coordinates in [zone['coordinates'] for zone in self.config_data['zones']]:
            return None
        return {'name':final_str_l[0],'type':striped_prop,'coordinates':coordinates,'metadata':dict_metadata}

    def check_connection(self,line:str)->None|tuple:
        splited_line:list[str] = line.split(':')
        if len(splited_line) != 2:
            return None
        zone_names:str = '|'.join([zone['name'] for zone in self.config_data['zones']])
        striped_values : str = (splited_line[1]).strip()
        if re.search(fr"^({zone_names})-({zone_names})(\s+\[\s*max_link_capacity\s*=\s*[1-9]\d*\s*\])?$",striped_values) is None:
            return None
        connections_and_metadata : tuple = striped_values.split()
        tuple_connections = tuple(connections_and_metadata[0].split('-')) 
        metadata = {'max_link_capacity':1}  
        if tuple_connections[0] == tuple_connections[1]:
            return None
        if tuple_connections in self.config_data['connections'] or tuple_connections[::-1] in self.config_data['connections']:
            return None
        if len(connections_and_metadata) == 2:
            metadata = dict(re.findall(r"\[\s*(max_link_capacity)\s*=\s*([1-9]\d*)\s*\]",connections_and_metadata[1]))

        return {'tuple_connections' :tuple_connections,'metadata' : metadata}
        
    def parsing(self)->dict:
        self.set_content()
        if not self.content:
            raise ParsingError("Error: No Content In The File")
        lines : list[str] = [line for line in self.content.split("\n") if line and not re.search(r"^#",line)]
        if not lines:
            raise ParsingError('Error : Completely empty file just comments')
        nb_drones : int | None = self.check_nb_drones(lines[0])
        if nb_drones is None:
            raise ParsingError("Error : line nb_drones is not valid")
        
        # number of drones is validated 
        self.config_data['nb_drones'] = nb_drones

        # this is for hubs , start point and end point
        for i in range(1,len(lines)):
            prop : str = lines[i].split(':')[0].strip()
            if prop == 'connection':
                break
            if prop != 'hub' and prop != 'start_hub' and prop != 'end_hub':
                raise ParsingError('Error : Hub Zone Not Valid !!')
            hubs_data : dict | None = self.check_hubs(lines[i])
            if hubs_data is None:
                raise ParsingError('Error : Hub Zone Not Valid !!')
            self.config_data['zones'].append(hubs_data)
        if self.counter_descripted_zones['start_hub'] != 1:
            raise ParsingError('Error : start Hub Error')
        elif  self.counter_descripted_zones['end_hub'] != 1:
            raise ParsingError('Error : end Hub Error')
        names_tmp : list[str] = [zone['name'] for zone in self.config_data['zones']]
        if len(names_tmp) != len(set(names_tmp)):
            raise ParsingError('Error : Hub Name must be unique')   
        for j in range(i,len(lines)):
            prop : str = lines[j].split(':')[0].strip()
            if prop != "connection":
                raise ParsingError('Error : connection ??')
            connection_data : tuple | None = self.check_connection(lines[j])
            if connection_data is None:
                raise ParsingError('Error : There is a problem in Connections')
            self.config_data['connections'].append(connection_data) 
            
        return self.config_data
            
        
    

