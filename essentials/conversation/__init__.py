from typing import Dict, List, Tuple, Union
from essentials import objects
from essentials import tokening
from essentials.search import text as text_search
import random
from essentials.search.text import search_engine_response
import re as reg_ex

SEARCH_ENGINE = text_search.reason()

def SEARCH_ENGINE_RESULT(in1:str, in2:List[str]) -> search_engine_response:
    re = search_engine_response(SEARCH_ENGINE.auto(in1, in2))
    return re

class variable_grab_failures(objects.baseObject):
    def __init__(self, data={}):
        self.need_input:Union[List[str], str] = None
        self.type_failure:Union[List[str], str] = None
        self.acceptable_failure:Union[List[str], str] = None
        self.acceptable_failure_options = True
        self.update(data)

class variable_result(objects.baseObject):
    def __init__(self, name, value=None, score=1, data={}):
        self.name = name
        self.value = value
        self.score = score
        self.required = True
        self.on_set = None
        self.update(data)

    def reject(self):
        self.value = None
        self.score = 0

class conversation_variable(objects.baseObject):
    def __init__(self, name, type, acceptable_values=None, minScore=1, data:dict={}):
        self.name = name
        self.type = type
        self.acceptable_values:Union[str, list[str]] = acceptable_values
        self.minScore = minScore
        self.pull_variable = True
        self.on_set = None
        self.parse_multi = True
        self.label = None
        self.update(data)
        self.failures = variable_grab_failures(data.get('failures', {}))
        if self.type in [int, float]:
            self.parse_multi = False
        
    def grab(self, input:str, failure_list:list, in_count=0, session:"conversation_session"=None) -> Tuple[str, int]:
        if input.count(" ") > 0:
            if self.acceptable_values is not None:
                if type(self.acceptable_values) == list:
                    if self.minScore == 1:
                        for item in self.acceptable_values:
                            if str(item).lower() in input.lower():
                                return item, 1
                    else:
                        highest = None
                        for item in self.acceptable_values:
                            re = SEARCH_ENGINE_RESULT(item.lower(), input.lower().split(" "))
                            #print(item.lower(), input.lower())
                            if item.count(" ") > 0:
                                for xword in item.lower().split(" "):
                                    if xword in input.lower():
                                        re.best.score += 0.25
                            if item.lower() in input.lower():
                                re.best.score += 0.5
                            if highest is None:
                                highest = item, re.best.score
                            else:
                                if re.best.score > highest[1]:
                                    highest = item, re.best.score
                        if highest is not None and highest[1] > self.minScore:
                            return highest
            else:
                if self.type == int:
                    for re in reg_ex.findall("[0-9]+", input):
                        return int(re), 1
                        
            if self.failures.need_input is not None:
                if type(self.failures.need_input) == list:
                    failure = self.failures.need_input[random.randint(0, len(self.failures.need_input)-1)]
                else:
                    failure = self.failures.need_input
                if self.failures.acceptable_failure_options:
                    if type(self.acceptable_values) == list:
                        acp = '\n'.join(self.acceptable_values)
                    else:
                        acp = self.acceptable_values
                    failure += f"\nPlease Select From The Following Options:\n\n{acp}"
                failure_list.append([failure, self.name])

        else:
            if self.minScore == 1:
                if self.type == str:
                    if type(self.acceptable_values) == list:
                        for item in self.acceptable_values:
                            if str(item).lower() == input.lower():
                                return item, 1
                    else:
                        raise TypeError("Acceptable values for str type must be a list!")
                else:
                    if self.type == int:
                        try:
                            return int(input), 1
                        except:
                            pass
                    elif self.type == float:
                        try:
                            return float(input), 1
                        except:
                            pass
            else:
                highest = None
                for item in self.acceptable_values:
                    re = SEARCH_ENGINE_RESULT(item.lower(), input.lower().split(" "))
                    if highest is None:
                        highest = item, re.best.score
                    else:
                        if re.best.score > highest[1]:
                            highest = item, re.best.score
                if highest is not None and highest[1] > self.minScore:
                    return highest  

            if in_count >= 1 or self.type in [int, float]:
                if self.type in [int, float]:
                    if session.current_subject == self.name:
                        failure_list.append(["That was an invalid number. Please try again!", self.name])
                else:
                    if self.acceptable_values is not None:
                        if type(self.failures.acceptable_failure) == list:
                            failure = self.failures.acceptable_failure[random.randint(0, len(self.failures.acceptable_failure)-1)]
                        else:
                            failure = self.failures.acceptable_failure
                        if self.failures.acceptable_failure_options:
                            if type(self.acceptable_values) == list:
                                acp = '\n'.join(self.acceptable_values)
                            else:
                                acp = self.acceptable_values
                            failure += f"\nPlease Select From The Following Options:\n\n{acp}"
                        failure_list.append([failure, self.name])
            else:
                if self.failures.need_input is not None:
                    if type(self.failures.need_input) == list:
                        failure = self.failures.need_input[random.randint(0, len(self.failures.need_input)-1)]
                    else:
                        failure = self.failures.need_input
                    if self.failures.acceptable_failure_options:
                        if type(self.acceptable_values) == list:
                            acp = '\n'.join(self.acceptable_values)
                        else:
                            acp = self.acceptable_values
                        failure += f"\nPlease Select From The Following Options:\n\n{acp}"
                    failure_list.append([failure, self.name])

        return None
                
class conversation_session(objects.baseObject):
    def __init__(self, conversation:"conversation", data={}):
        self.tk = None
        self.variables:Dict[str, variable_result] = {}
        self.complete = False
        self.__conversation__ = conversation
        self.failure_list = []
        self.history = []
        self.in_count = 0
        self.current_subject = ""
        self.update(data)

        if self.tk is None:
            self.tk = tokening.CreateToken(5, self.__conversation__.sessions)
        if self.__conversation__.sessions.get(self.tk, False) == False:
            self.__conversation__.sessions[self.tk] = self

        if self.__conversation__.pull_variables:
            for vName in self.__conversation__.variables:
                var = self.__conversation__.variables[vName]
                if vName not in self.variables and var.pull_variable:
                    self.variables[vName] = variable_result(vName, None, 0)
                    self.variables[vName].on_set = var.on_set

    def resume(self, data):
        self.update(data)
        self.variables = {x:variable_result(x, None, 0, self.variables[x]) for x in self.variables}
        for vName in list(self.variables.keys()):
            var = self.__conversation__.variables.get(vName)
            self.variables[vName].on_set = var.on_set

            if self.variables[vName].value is not None:
                if var.on_set is not None:
                    try:
                        accept = var.on_set(self)
                        if accept == False:
                            self.variables[vName].reject()
                    except:
                        pass


    def pause(self) -> dict:
        return self.json
    
    def purge(self):
        try:
            del self.__conversation__.sessions[self.tk]
        except:
            pass

    def get_variable(self, name):
        return self.variables[name].value

    def pull_variable(self, vName, check_history=False) -> "conversation_variable":
        var = self.__conversation__.variables.get(vName, False)
        if var:
            self.variables[vName] = variable_result(vName, None, 0)
            self.variables[vName].on_set = var.on_set
            self.complete = False
            self.failure_list.append([var.failures.need_input, vName])
            if check_history:
                highest = None
                for in1 in self.history:
                    r = var.grab(in1, [], 0, self)
                    if r is not None:
                        r, score = r
                        if highest is None:
                            highest = r, score
                        elif score > highest[1]:
                            highest = r, score
                if highest is not None:
                    if highest[1] > var.minScore:
                        self.variables[vName].value = highest[0]
            return var
        else:
            raise ValueError("This variable doesn't exist")

    def input(self, input):
        self.history.append(input)
        self.failure_list = []

        t = 20
        while True:
            t -= 1
            if t <= 0:
                break

            for vName in [self.current_subject]+list(self.variables.keys()):
                var = self.variables.get(vName, False)
                if var == False:
                    continue
                if var.value is None and var.required:
                    response = self.__conversation__.variables.get(vName).grab(input, self.failure_list, self.in_count, self)
                    if response is not None:
                        response, score = response
                        var.value = response
                        var.score = score
                        self.in_count = 0
                        if var.on_set is not None:
                            try:
                                #print("Check", vName)
                                accept = var.on_set(self)
                                if accept == False:
                                    var.reject()
                                    need_input = self.__conversation__.variables.get(vName).failures.need_input
                                    if need_input not in [x[0] for x in self.failure_list]:
                                        self.failure_list.append([need_input, vName])
                            except:
                                pass
                        
                    else:
                        need_input = self.__conversation__.variables.get(vName).failures.need_input
                        if need_input not in [x[0] for x in self.failure_list]:
                            self.failure_list.append([need_input, vName])

            if len(self.failure_list) > 0 or False not in [self.variables[x].value is not None for x in self.variables]:
                break
                

        if False not in [self.variables[x].value is not None for x in self.variables]:
            self.complete = True

        self.in_count += 1
        if len(self.failure_list) > 0:
            self.current_subject = self.failure_list[0][1]

        return self.failure_list

class conversation:
    def __init__(self, on_complete=None):
        self.sessions:Dict[str, conversation_session] = {}
        self.variables:Dict[str, conversation_variable] = {}
        self.on_complete = on_complete
        self.clear_session_on_complete = False
        self.pull_variables = True

    def append_variable(self, name, type, acceptable_values=None, minScore=1, data={}) -> conversation_variable:
        self.variables[name] = conversation_variable(name, type, acceptable_values, minScore, data)
        return self.variables[name]


    def input(self, input, identifier:str=None, session:conversation_session=None) -> conversation_session:
        if session is None:
            if self.sessions.get(identifier, False) == False:
                session = conversation_session(self, {"tk": identifier})
            else:
                session = self.sessions.get(identifier)

        if input is not None:
            session.input(input)

        return session


class __phrase_group_holder__(objects.baseObject):
    def __init__(self, data={}):
        self.groups:Dict[str, list[Union[str, interchange]]] = {}
        self.type = "phase_group"
        self.update(data)
        self.__load__()

    def __load__(self):
        for key in self.groups:
            pg_list = self.groups[key]
            i = 0
            for item in pg_list:
                if type(item) == dict:
                    i_type = item.get("type")
                    if i_type == "interchange":
                        pg_list[i] = interchange(item)
                i += 1


    def prep(self, group_name, index=None):
        group = self.groups[group_name]
        if index is None:
            index = random.randint(0, len(group)-1)
        selected = group[index]
        return selected

    def add_group(self, name, posibilites):
        self.groups[name] = posibilites

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except Exception as e:
            if __name in self.groups:
                return self.prep(__name)
            raise e

class interchange(objects.baseObject):
    def __init__(self, data={}):
        self.strings:List[Union[str, interchange]] = []
        self.type = "interchange"
        self.update(data)
        self.phrase_groups:__phrase_group_holder__ = __phrase_group_holder__(data.get("phrase_groups"))
        self.__load__()

    def __load__(self):
        self.__load_strings__()      
        
    def __load_strings__(self):
        i = 0
        for item in self.strings:
            if type(item) == dict:
                i_type = item.get("type")
                if i_type == "interchange":
                    self.strings[i] = interchange(item)
            i += 1

    def prep(self, variables=Dict[str, Union[str, bool, int, float]]):
        if len(self.strings) == 0:
            raise ValueError("There are no string to create this interchange")
        string = self.strings[random.randint(0, len(self.strings)-1)]
        if isinstance(string, interchange):
            string = string.prep(variables)
        
        for tag in reg_ex.finditer(r"\{([^}]*)\}", string):
            inner = tag.group(1)
            replace = tag.group(0)
            value = "Unknown"
            if "ev:" in inner:
                ev = inner.split(":", 1)[1]
                try:
                    vars:dict = variables.copy()
                    vars.update({"pg": self.phrase_groups})
                    value = eval(ev, vars)
                except:
                    pass
            elif "pg:" in inner:
                label = inner.split(":", 1)[1]
                index = None
                if ":" in label:
                    label, index = label.split(":", 1)
                value = self.phrase_groups.prep(label, index)
            else:
                value = variables.get(inner, 'Unknown')
            if isinstance(value, interchange):
                value = value.prep(variables)
            string = string.replace(replace, str(value))
        return string