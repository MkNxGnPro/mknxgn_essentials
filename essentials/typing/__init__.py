from typing import Union, List, Dict, Tuple
from essentials import file_ops

DEFAULTS = {
    "str": '""',
    "list": "[]",
    "int": 0,
    "float": 0,
    "bool": False
}
INDENTCHAR = " "
INDENTCHAR_COUNT = 4

def parse_dictList(name, input:Union[List[dict], dict]) -> Tuple[dict, dict]:
    """
        Parses a dict to convert it to a dict of types,
        to be used by create_typing_file
    """
    fields:Dict[str, list, dict] = {}
    subs = {}

    if type(input) not in [list, dict]:
        raise ValueError("The input must be a dict or list of dicts")

    if type(input) == list:
        if name is None:
            raise ValueError("Name must be given if using list of dicts")
        for item in input:
            if type(item) != dict:
                continue
            parsed, subbs = parse_dictList(f"{name}__list", item)
            for key in parsed[f"{name}__list"]:
                if key in fields:
                    if type(fields[key]) == list:
                        if parsed[f"{name}__list"][key] not in fields[key]:
                            fields[key].append(parsed[f"{name}__list"][key])
                    else:
                        if parsed[f"{name}__list"][key] != fields[key]:
                            fields[key] = [parsed[f"{name}__list"][key], fields[key]]
                else:
                    fields[key] = parsed[f"{name}__list"][key]
            #fields.update(parsed[f"{name}__list"])
            subs.update(subbs)
    else:
        for key in input:
            if type(input[key]) == dict:
                parsed, subbs = parse_dictList(f"{name}_{key}_dict", input[key])
                subs.update(subbs)
                subs.update(parsed)
                fields[key] = (f"{name}_{key}_dict", f"{name}_{key}_dict")
            elif type(input[key]) == list:
                if len(input[key]) > 0:
                    if type(input[key][0]) == dict:
                        parsed, subbs = parse_dictList(f"{name}_{key}_list", input[key])
                        subs.update(subbs)
                        subs.update(parsed)
                        fields[f"{key}"] = (f"List[{name}_{key}_list]", f"{name}_{key}_list")
                    else:
                        fields[f"{key}"] = (f"EmptyList[{type(input[key][0]).__name__}]", [])
                else:
                    fields[f"{key}"] = f"list"
                
            else:
                fields[key] = type(input[key]).__name__
    
    return {name: fields}, subs

def create_class(name, data:dict, indent=0):
    classData = [
        f"{INDENTCHAR*indent*INDENTCHAR_COUNT}class {name}(objects.baseObject):",
        f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT}def __init__(self, data:Dict={{}}):"
    ]
    lasts = []
    for key in data:
        useKey = key.replace(" ", "_").replace("-", "_")
        for item in ['#']:
            useKey = useKey.replace(item, "")
        if type(data[key]) == list:
            line = f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.{useKey}:Union[{','.join(data[key])},None] = None"
            classData.append(line)
        elif type(data[key]) == tuple:
            if "EmptyList" in data[key][0]:
                line = f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.{useKey}:{data[key][0].replace('EmptyList', 'List')} = []"
                classData.append(line)
            else:
                if "List" in data[key][0]:
                    line = f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.{useKey}:{data[key][0]} = [{data[key][1]}(x) for x in data.get('{key}', [])]"
                else:
                    line = f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.{useKey}:{data[key][0]} = {data[key][1]}(data.get('{key}', {{}}))"
                lasts.append(line)
        else:
            line = f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.{useKey}:{data[key]} = {DEFAULTS.get(data.get(key, None), None)}"
            classData.append(line)
        
    classData.append(f"{INDENTCHAR*indent*INDENTCHAR_COUNT}{INDENTCHAR*INDENTCHAR_COUNT*2}self.update(data)")
    classData += lasts
    return classData

def create_typing_file(name, data:dict, fp:str, append=False):
    """
        Parses a dict to convert it to a typing support file. Ideal for turning JSON into Python.\n
        The objects/classes written can be used OTB.\n
        - Supports Recursion 

        Example:
            - CREATE:\n
                data = {"pizza": {"toppings": ["cheese"], "cut": "normal", "mobileOrder": False}}\n
                create_typing_file("Pizza", data['pizza'], 'pizza.py')
            
            - Use:\n
                from pizza import Pizza\n
                Pizza(data['pizza']).mobileOrder\n
                >> False
    """
    parsed, subs = parse_dictList(name, data)
    if append == False:
        fileData = ["from typing import Union, List, Dict, Tuple", "from essentials import objects\n"]
    else:
        fileData = ['\n']
    for key in subs:
        lines = create_class(key, subs[key])
        lines.append("\n")
        fileData += lines
    fileData += create_class(name, parsed[name])
    file_ops.write_file(fp, "\n".join(fileData), append=append)