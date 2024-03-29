import json, base64, os
import tarfile
import threading
import time
from typing import Dict, List, Union

workingDir = False

def formatFileName(name:str, starter):
    if starter != "":
        return (starter + name[::-1].split(starter[::-1], 1)[0][::-1]).replace("\\", "/")
    else:
        return name.replace("\\", "/")

class __fileInfo__:
    def __init__(self, name, time, fullPath):
        self.name = name
        self.time = time
        self.fullPath = fullPath
        self.reason = ""
        self.pair: Union[None, __fileInfo__] = None
        self._td = 0
    
    @property
    def timeDifference(self):
        return self.time - self._td

    @timeDifference.setter
    def timeDifference(self, value):
        self._td = value

    def __repr__(self) -> str:
        return f"<essentials.File Info Object, name: {self.name}>"


def getFilesModifiedTime(dir, starter) -> Dict[str, __fileInfo__]:
    current = {}
    for dir, dirNames, fileNames in os.walk(dir):
        for item in fileNames:
            if "cpython-36.pyc" in item or "__pycache__" in item:
                continue
            file = os.path.join(dir, item)
            data = os.stat(file)
            name = formatFileName(file, starter)
            current[name] = __fileInfo__(name, data.st_mtime, file)
    return current


class __fileChanges__:
    def __init__(self, changed, files):
        self.files:List[__fileInfo__] = files
        self.changed = changed

    def __repr__(self) -> str:
        return f"<essentials.File Changes Object: Changes: {self.changed}, Count: {self.files.__len__()}>"

def detectChanges(dir1, dir2, starter="") -> __fileChanges__:
    past = getFilesModifiedTime(dir1, starter)
    current = getFilesModifiedTime(dir2, starter)
    return compareFilesModifedTime(past, current)

def compareFilesModifedTime(past:Dict[str, __fileInfo__], current:Dict[str, __fileInfo__]) -> __fileChanges__:
    pullFiles = []
    for item in current:
        if item not in past:
            current[item].reason = "Created"
            pullFiles.append(current[item])
            continue
        if current[item].time > past[item].time:
            current[item].timeDifference = past[item].time
            current[item].reason = "Modified"
            current[item].pair = past[item]
            pullFiles.append(current[item])
    return __fileChanges__(pullFiles.__len__() > 0, pullFiles)

def EncodeWithKey(key, string):
    """
    Encode with Key

    Takes your string and encodes it with another string(key), only the key will decode the string

    string = "Hello"
    key = "key"
    
    >> "w5PDisOlw5fDlA=="
    """

    enc = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(string[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def DecodeWithKey(key, string):
    """
    Decode with Key

    Takes your encoded string and decodes it with another string(key)

    string = "w5PDisOlw5fDlA=="
    key = "key"
    
    >> "Hello"
    """

    dec = []
    enc = base64.urlsafe_b64decode(string).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def read_json(path, encrypt=False):
    """
    Read Json File
    
    Read and returns JSON From a file

    path - String: Dir of the json file
    encrypt - Bool/String: If the file was encrypted with MkEncrypt, use the string that encrypted it."""

    if workingDir != False:
        path = os.path.join(workingDir, path)

    if encrypt:
        return json.loads(DecodeWithKey(encrypt, read_file(path)))

    return json.loads(read_file(path))

def read_file(path, byte=False, encrypt=False):
    """
    Read File
    
    Read and returns data From a file optionally gives bytes to read in bytes format

    path - String: Dir of the json file
    byte - Bool, False: Read as bytes, defaults to false."""
    if workingDir != False:
        path = os.path.join(workingDir, path)

    if byte:
        file = open(path, "rb")
    else:
        file = open(path, "r")
    data = file.read()
    file.close()
    if encrypt:
        return DecodeWithKey(encrypt, data)
    return data

def write_file(path, data, append=False, byte=False, encrypt=False):
    """
    Write File
    
    Writes data to a file optionally gives bytes to write in bytes format, includes append

    path - String: Dir of the file,
    append - Bool, False: Append to the current file,
    byte - Bool, False: Read as bytes, defaults to false."""
    if workingDir != False:
        path = os.path.join(workingDir, path)
    otype = "w"
    if append:
        otype = "a"
    if byte:
        otype += "b"
    else:
        data = str(data)
    file = open(path, otype)
    if encrypt:
        data = EncodeWithKey(encrypt, data)
    file.write(data)
    file.close()
    return data

def write_json(path, data, pretty=True, encrypt=False):
    """
    Write Json File
    
    Uses write_file, writes JSON data to a file. For use with Lists/Dicts

    path - String: Dir of the json file,
    data - Dict/List: What you'd like to be written to the file,
    pretty - Bool, True: Pretty Print the file for reading.
    encrypt - Bool/String, False: Will encrypt the file with the string given in place. If True, replaces pretty print with false."""
    if workingDir != False:
        path = os.path.join(workingDir, path)

    if encrypt:
        return write_file(path, EncodeWithKey(encrypt, json.dumps(data)))

    if pretty:
        return write_file(path, json.dumps(data, indent=4, sort_keys=True))
    else:
        return write_file(path, json.dumps(data))


def generate_file(path, size=1):
    """
    Writes a param:SIZE (MB) file with "_test_file_" data.

    path - String: Dir of the file,
    size - How Many MB (Megabytes) your file will be.
    """
    write_file(path, ("test_file_"*104859)*size)

def DecompressTar(file, dirs=False):
    if not tarfile:
        raise ImportError("TAR was not found during boot, Install TAR to use this function")
    if workingDir != False:
        file = os.path.join(workingDir, file)
    tfile = tarfile.open(file, "r")
    if dirs == False:
        dirs = file.split(".")[0]
    os.makedirs(dirs, exist_ok=True)
    tfile.extractall(dirs)
    return dirs

def write_csv(path, data):
    strs = ""
    for item in data:
        items = []
        for x in item:
            if ',' in x:
                items.append('"' + str(x) + '"')
            else:
                items.append(str(x))
        strs += ",".join(items)
        strs += "\n"
    write_file(path, strs)


__busy_files__ = {}
def __biz_File__(path, data=None, append_txt=False):
    global __busy_files__
    if path not in __busy_files__:
        __busy_files__[path] = False
    while __busy_files__[path] == True:
        time.sleep(0.01)
    __busy_files__[path] = True
    if data is not None:
        if append_txt:
            write_file(path, data, True)
        else:
            write_json(path, data)
        __busy_files__[path] = False
        return
    if append_txt:
        try:
            data = read_file(path)
        except:
            data = ""
    else:
        try:
            data = read_json(path)
        except:
            data = {}
    __busy_files__[path] = False
    return data

class Updating_Dict_File(dict):

    def __init__(self, path):
        self.path = path
        data = __biz_File__(path)
        for item in data:
            self.__setitem__(item, data[item], False)

    def __save_on_change__(self):
        time.sleep(0.5)
        __biz_File__(self.path, self)

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)

    def __setitem__(self, key, value, save=True):
        if save:
            threading.Thread(target=self.__save_on_change__).start()
        return super().__setitem__(key, value)