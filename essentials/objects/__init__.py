from copy import deepcopy
import sys
from typing import Dict, Union

DEFAULTS = [{}, [], "", None, False, 0]

def formatItems(input:Union[dict, list]) -> Union[dict, list]:
    if type(input) == list:
        data = []
        for item in input:
            if isinstance(item, baseObject):
                data.append(item.json)
            elif type(item) in [list, dict]:
                data.append(formatItems(item))
            elif type(item) in [tuple, int, float, str, bool, None]:
                data.append(item)
            elif callable(item):
                continue
    elif type(input) == dict:
        data = {}
        for key in input:
            if "__" in str(key):
                continue
            item = input[key]
            if isinstance(item, baseObject):
                data[key] = item.json
            elif type(item) in [list, dict]:
                data[key] = formatItems(item)
            elif type(item) in [tuple, int, float, str, bool, None]:
                data[key] = item
            elif callable(item):
                continue
    return data
    
class baseObject:
    def __init__(self, data:dict={}):
        self.update(data)

    @property
    def json(self) -> dict:
        data = {}
        for name in self.__dict__:
            try:
                if "__" not in name:
                    item = self.__dict__[name]
                    if isinstance(item, baseObject):
                        data[name] = item.json
                    elif type(item) in [list, dict]:
                        try:
                            data[name] = formatItems(item)
                        except Exception as e:
                            print("error", e)
                            print("Is dual ommited", name, type(item), item)
                            raise e
                    elif type(item) in [tuple, int, float, str, bool, None]:
                        data[name] = item
                    elif callable(item):
                        continue
                    else:
                        pass
                        #print("Is ommited", name, type(item), item)
                        #print(data)
            except Exception as e:
                print("baseObject EXCEPTION!", name)
                print(e)
                raise e
        return data

    def update(self, data:dict):
        if type(data) not in [type(None), dict]:
            return
            #raise TypeError(f"baseObject requires type 'Dict' on function update, Got: [{type(data)}: {data}]")
        if data is not None and type(data) == dict:
            for name in data:
                item = data[name]
                if name in self.__dict__:
                    if isinstance(self.__dict__[name], baseObject):
                        self.__dict__[name].update(item)
                    elif type(item) in [list, int, float, str, dict, bool]:
                        self.__setattr__(name, item)
                

    def __repr__(self) -> str:
        return str(self.json) # "baseObject: " + json.dumps(self.json)

class __fileDirectory__(baseObject):
    def __init__(self, data, path="", url=""):
        self.path:str = ""
        self.url:str = ""
        super().__init__(data)
        if self.path == "":
            self.path = path
        if self.url == "":
            self.url = url

def properCasing(input:str) -> str:
    out = []
    if " " in input:
        for item in input.strip().split(" "):
            out.append(item[0].upper() + item[1:].lower())
    else:
        return input[0].upper() + input[1:].lower()
    return " ".join(out)

def partition_object(data:Dict[str, str], seperator="."):
    new = {}
    for key in data:
        if seperator in key:
            lv = key.split(seperator)
            i = 0
            gate = new
            for part in lv:
                if i < len(lv)-1:
                    if part not in gate:
                        gate[part] = {}
                    gate = gate[part]
                else:
                    gate[part] = data[key]
                i += 1
        else:
            new[key] = data[key]
    return new

def compact_object(data:Dict[str, str], seperator=".", prev=None):
    new = {}
    for key in data:
        if type(data[key]) == dict:
            new.update(compact_object(data[key], seperator, (prev + "." if prev is not None else "") + key))
        else:
            new[(prev + "." if prev is not None else "") + key] = data[key]
    return new

class response(baseObject):
    def __init__(self, data={}):
        self.status = 0
        self.hint = None
        self.data = None
        self.error = None
        self.update(data)

class runtime_options(baseObject):
    def __init__(self, data: dict = {}, parse=True):
        self.args:Union[baseObject, dict]
        self.parse_error_exit:bool
        self.parse_types:bool
        self.parse_error_keep:bool
        self.partition_seperator:str
        self.__sys_argv__ = {}
        self.__arg_types__ = {}
        super().__init__(data)

        for pack in [
                ['args', {}],
                ['parse_error_exit', False],
                ['parse_types', True],
                ['parse_error_keep', False],
                ['partition_seperator', '.']
            ]:
            n, d = pack
            try:
                v = self.__getattribute__(n)
            except:
                v = None
            if v is None:
                self.__setattr__(n, d)
        
        if parse:
            self.parse()

    def __get_types__(self) -> dict[str, type]:
        types = self.args.json if isinstance(self.args, baseObject) else self.args
        types = compact_object(types, self.partition_seperator)
        types = {x: type(types[x]) for x in types}
        return types
    
    def parse(self):
        data = {}
        types = self.__get_types__()
        self.__arg_types__ = types
        #print("types", types)
        for item in sys.argv:
            if "=" in item:
                key, value = item.split("=")
                data[key] = value
        self.__sys_argv__ = deepcopy(data)
        #print("Sys.argv", data)

        for key in list(data.keys()):
            value = data[key]
            try:
                data[key] = types.get(key)(value)
            except:
                if self.parse_error_exit:
                    raise ValueError(f"Could not set param[{key}] to Type of [{types.get(key)}], value: [{value}]")
                else:
                    if self.parse_error_keep == False:
                        print("Warning:", f"Could not set param[{key}] to Type of [{types.get(key)}], value: [{value}]")
                        del data[key]


        data = partition_object(data, self.partition_seperator)
        if type(self.args) == dict or isinstance(self.args, baseObject):
            self.args.update(data)


class grave_content(baseObject):
    def __init__(self, input:str, data = {}):
        self.parsed = False
        self.input:Union[None, str] = input
        self.language:Union[None, str] = None
        self.content:Union[None, str] = None
        super().__init__(data)
        if self.parsed == False:
            self.parse()

    def __test__(self, input:Optional[str]=None) -> bool:
        if input is None and self.input not in [None, ""]:
            input = self.input

        if input is None:
            return False

        if input.startswith("```") == False:
            return False
        if input.endswith("```") == False:
            return False
        return True

    def parse(self, input:Optional[str]=None) -> Union[None, "grave_content"]:
        if input is None and self.input not in [None, ""]:
            input = self.input

        if input is None:
            return None

        if self.__test__(input) == False:
            return None
        
        reg_pattern = r"^```(.+)\n([.\S\s]*)```"
        import re
        match = re.match(reg_pattern, input)
        if match is not None:
            m = match.groups()
            self.language = m[0]
            self.content = m[1].strip()
            self.parsed = True
            return self
        
        return None
