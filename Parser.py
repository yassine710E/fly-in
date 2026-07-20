import re
import pygame


def is_int(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_duplicated_prop(l_props: list[str]) -> str | None:
    seen = set()
    for prop in l_props:
        if prop in seen:
            return prop
        else:
            seen.add(prop)
    return None


def raise_for_order_prop(order, index_checker, prop, index) -> None:
    if order > index_checker:
        raise ParsingError(
            f'prop "\033[4m{prop}\033[0m" is not ordered in line {index+1}')


class ParsingError(Exception):
    pass


class Parser:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.metadata = {
            'color': list(pygame.color.THECOLORS.keys()),
            'zone': ['normal', 'blocked', 'restricted', 'priority'],
            'max_drones': 1
        }
        self.config_data = {
            'nb_drones': None,
            'zones': [],
            'connections': []
        }
        self.prop_flags = {'nb_drones': False, 'start_hub': False,
                           'end_hub': False, 'hub': False, 'connection': False}

    def set_content(self) -> None:
        try:
            with open(self.file_name, 'r') as file:
                self.content = file.readlines()
        except FileNotFoundError:
            raise ParsingError(
                "Error: The requested file does not exist at this location.")
        except PermissionError:
            raise ParsingError(
                "Error: System permissions deny access to this file.")
        except IsADirectoryError:
            raise ParsingError(
                "Error: The target path points to a directory, not a file.")
        except OSError as error:
            raise ParsingError(f"System I/O failure occurred: {error}")

    def check_nb_drones(self, line: str) -> None | dict:
        splited_line: list[str] = line.split(':')
        if len(splited_line) != 2:
            return {'error': 'key and value not exist'}
        prop: str = (splited_line[0]).strip()
        if prop != "nb_drones":
            return {'error': f'key "{prop}" is not matching with "nb_drones"'}
        val: str = splited_line[1].strip()
        if not re.search(r"^\s*[1-9]\d*\s*$", val):
            return {'error': 'number integer value is not valid'}
        return {'nb_drones': int(val)}

    def check_hubs(self, line: str) -> dict:
        splited_line: list[str] = line.split(':')
        correct_value = dict()
        if len(splited_line) != 2:
            return {'error': 'line doesn\'t respect this pattern '
                    '"\033[4mkey : value\033[0m"'}
        striped_prop: str = (splited_line[0]).strip()
        striped_values: str = (splited_line[1]).strip()

        # 1st : check the name of hub
        check_str = r"^[^-\s]+\s+"
        match = re.findall(check_str, striped_values)
        if not match:
            return {'error': 'name of hub is not valid '
                    f'"\033[4m{striped_values.split()[0]}\033[0m"'}

        if (match[0].strip() in [zone['name']
                                 for zone in self.config_data['zones']]):
            return {'error': f'name of hub "\033[4m{match[0].strip()}\033[0m"'
                    ' is already exist'}

        correct_value['name'] = match[0].strip()
        # 2nd : check coordinates of hub
        check_str += r"-?\d+\s+-?\d+"
        match = re.findall(check_str, striped_values)
        if not match:
            err_data = striped_values.split()[1] if not is_int(
                striped_values.split()[1]) else striped_values.split()[2]
            return {'error': 'coordinates of hub  are not valid '
                    f'"\033[4m{err_data}\033[0m"'}
        correct_value['coordinates'] = (
            int(match[0].split()[1]), int(match[0].split()[2]))

        # 3rd : check metadata
        check_str += (r"(\s+\[\s*(color|zone|max_drones)\s*=\s*[^\s=\]]+"
                      r"(\s+(color|zone|max_drones)\s*=\s*[^\s=\]]+)*\s*\])?$")
        match = re.match(check_str, striped_values)
        if match is None:
            return {'error': 'this part is not respecting the metadata pattern'
                    ' "\033[4m[color:... zone:... max_drones:...]\033[0m"'}
        arr_props: list[str] = re.findall(
            r"[^:]\s*(color|zone|max_drones)", striped_values)
        if get_duplicated_prop(arr_props) is not None:
            return {'error': 'duplicted prop '
                    f'"\033[4m{get_duplicated_prop(arr_props)}\033[0m"'}

        # 4th : check values of metadat keys [color : ....]
        dict_metadata: dict = dict(re.findall(
            r"(color|zone|max_drones)\s*=\s*([^\s=\]]+)", striped_values))
        for k, v in dict_metadata.items():
            if k == "zone" and v not in self.metadata[k]:
                return {'error': 'zone value in metadata '
                        f'is not validated "\033[4m{v}\033[0m"'}
            elif k == "max_drones":
                try:
                    dict_metadata[k] = int(v)
                    if dict_metadata[k] < 1:
                        return {'error': 'not valid integer less than 1 '
                                f'"\033[4m{v}\033[0m"'}
                except ValueError:
                    return {'error': 'max_drones is not valid integer '
                            f'"\033[4m{v}\033[0m"'}
            elif k == 'color' and v not in self.metadata[k]:
                dict_metadata[k] = 'gray10'

        # 5th : set the default value
        if not dict_metadata.get('zone'):
            dict_metadata['zone'] = 'normal'
        if not dict_metadata.get('color'):
            dict_metadata['color'] = 'gray10'
        if not dict_metadata.get('max_drones'):
            dict_metadata['max_drones'] = 1
        correct_value['metadata'] = dict_metadata
        correct_value['type'] = striped_prop
        if (striped_prop in ['end_hub', 'start_hub']
            and striped_prop
                in [zone['type'] for zone in self.config_data['zones']]):
            return {'error': f'"\033[4m{striped_prop}\033[0m" '
                    'is duplicated and already exist'}
        if (correct_value['coordinates']
                in [zone['coordinates']
                    for zone in self.config_data['zones']]):
            return {'error': 'coordinates are already exist'}
        return correct_value

    def check_connection(self, line: str) -> None | tuple:
        splited_line: list[str] = line.split(':')
        if len(splited_line) != 2:
            return {'error': 'line doesn\'t respect this pattern '
                    '"\033[4mkey : value\033[0m"'}
        zone_names: str = '|'.join([zone['name']
                                   for zone in self.config_data['zones']])
        striped_values: str = (splited_line[1]).strip()
        clear_value = dict()

        # 1st : check the value of hubs in connection is valid or not
        checker_pattern = fr"^({zone_names})-({zone_names})"
        match = re.search(checker_pattern, striped_values)
        if match is None:
            return {'error': f'there a problem in connection '
                    f'"\033[4m{striped_values.split()[0]}\033[0m" '
                    'it should be line "\033[4mzone-zone '
                    '(and zone must be exist in hubs config data)\033[0m"'}
        match = tuple(striped_values.split()[0].split('-'))
        if match[0] == match[1]:
            return {'error': 'duplicated names of hub '
                    f'"\033[4m{match[0]}\033[0m" in one connection'}
        prev_tuple_connections = [connection['tuple_connections']
                                  for connection
                                  in self.config_data['connections']
                                  if 'connections']
        if match in prev_tuple_connections:
            return {'error': f'"\033[4m{match}\033[0m" '
                    'already exist in previous connections'}
        if match[::-1] in prev_tuple_connections:
            return {'error': f'reversed "\033[4m{match}\033[0m" '
                    'already exist in previous connections'}

        # set tuple connection
        clear_value['tuple_connections'] = match

        # 2nd : check the metadata if valid or not
        checker_pattern += r"(\s+\[\s*max_link_capacity\s*=\s*[1-9]\d*\s*\])?$"
        match = re.search(checker_pattern, striped_values)
        if match is None:
            return {'error': 'there is a problem in metadata '
                    f'"\033[4m{striped_values.split()[1]}\033[0m'}

        connections_and_metadata: tuple = striped_values.split()
        metadata = {'max_link_capacity': 1}

        if len(connections_and_metadata) == 2:
            metadata = dict(re.findall(
                r"\[\s*(max_link_capacity)\s*=\s*([1-9]\d*)\s*\]",
                connections_and_metadata[1]))
            metadata['max_link_capacity'] = int(metadata['max_link_capacity'])

        # set metadata
        clear_value |= {'metadata': metadata}

        return clear_value

    def parsing(self) -> dict:
        self.set_content()
        if not self.content:
            raise ParsingError("Error: No Content In The File")
        lines_without_comments: list[str] = [
            line for line in self.content if
            line and not re.search(r"^#", line)]
        if not lines_without_comments:
            raise ParsingError('Error : Completely empty file just comments')

        # set list of collable for checking line
        checkers_list = [self.check_nb_drones,
                         self.check_hubs, self.check_connection]
        index_checker = 0
        order = 0
        flag_hubs = False
        flag_connection = False
        # this is for hubs , start point and end point
        for index, line in enumerate(self.content):
            line = line.strip()
            if not line or (line and line[0] == '#'):
                continue
            line = line.split("#")[0]
            prop = (line.split(':')[0]).strip()

            # choose prop by the collable in list
            if prop == 'nb_drones':
                if not self.prop_flags[prop]:
                    self.prop_flags[prop] = True
                index_checker = 0
                raise_for_order_prop(order, index_checker, prop, index)
            elif prop == 'hub' or prop == 'end_hub' or prop == "start_hub":
                if not self.prop_flags[prop]:
                    self.prop_flags[prop] = True
                index_checker = 1
                if not flag_hubs:
                    order += 1
                    flag_hubs = True
                raise_for_order_prop(order, index_checker, prop, index)
            elif prop == "connection":
                if not self.prop_flags[prop]:
                    self.prop_flags[prop] = True
                index_checker = 2
                if not flag_connection:
                    order += 1
                    flag_connection = True
                raise_for_order_prop(order, index_checker, prop, index)
            checker_returned_value = checkers_list[index_checker](line)
            if 'error' in checker_returned_value:
                raise ParsingError(
                    f"Error : {checker_returned_value['error']} "
                    f"in line {index + 1}")
            k = list(self.config_data.keys())[index_checker]
            if isinstance(self.config_data[k], list):
                self.config_data[k].append(checker_returned_value)
            else:
                self.config_data[k] = checker_returned_value['nb_drones']
        for prop, flag in self.prop_flags.items():
            if not flag and prop != "hub":
                raise ParsingError(
                    f'Error : key "\033[4m{prop}\033[0m" doesn\'t exist')

        return self.config_data
