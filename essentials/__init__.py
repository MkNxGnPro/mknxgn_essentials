try:
    import numpy as np
except:
    numpy = False

try:
    from io import BytesIO
except:
    BytesIO = False

try:
    import json
except:
    json = False

try:
    import datetime
except:
    datetime = False

try:
    import random
except:
    random = False

try:
    from flask import request
except:
    flask = False
try:
    import requests
except:
    requests = False
try:
    import base64
except:
    base64 = False

try:
    import collections
except:
    collections = False

try:
    import tarfile
except:
    tar = False

try:
    import os
except:
    os = False

try:
    from PIL import Image
except:
    Image = False

try:
    import cv2
except:
    cv2 = False

workingDir = False

def cv2_to_pil(cv2_img):
    if not cv2:
        raise ImportError("OpenCv was never found during boot. Install opencv to use this function")
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

def pil_to_cv2(pil_img):
    if not cv2:
        raise ImportError("OpenCv was never found during boot. Install opencv to use this function")
    if not Image:
        raise ImportError("PIL was never found during boot. Install Python Image Lib. to use this function")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def DecompressTar(file, dirs=False):
    if not tar:
        raise ImportError("TAR was not found during boot, Install TAR to use this function")
    if workingDir != False:
        file = os.path.join(workingDir, file)
    tfile = tarfile.open(file, "r")
    if dirs == False:
        dirs = file.split(".")[0]
    os.makedirs(dirs, exist_ok=True)
    tfile.extractall(dirs)
    return dirs

def ShrinkLink(link):
    """
    Shrink a Link via Python and MkNxGn

    ** Needs an Internet Connection **

    Uses MkNxGn's Free Link Shrinking API

    takes a (long) url and return a mkls.in short link
    """

    if not json:
        raise ImportError("Json was not found during boot, Install Json to use this function")
    if not requests:
        raise ImportError("Requests was not found during boot, Install Requests to use this function")
    return json.loads(requests.get("https://mknxgn.pro/tools/LinkShrink?url=" + link).text)

def SortDictOfDict(Dict, key, reverseOrder=False):
    """
    Sort Dictionary of Dictionaries

    will parse a dictionary of dictionarys returning it in order.

    dict = {'a': {'time_stamp': 100}, 'b': {'time_stamp': 50}, 'c': {'time_stamp': 150}}
    key = 'time_stamp'
    reverseOrder = True

    >> {'b': {'time_stamp': 50}, 'a': {'time_stamp': '100'}, 'c': {'time_stamp': 150}}
    """
    if not collections:
        raise ImportError("collections was not found during boot, Install collections to use this function")
    r = collections.OrderedDict(sorted(Dict.items(), key=lambda t:t[1][key], reverse=reverseOrder))
    data = {}
    for item in r:
        data[item] = Dict[item]
    return data

def DictToArgs(Dict):
    """
    Dictionary to Args

    Give a dictionary of keys and values to convert it to a url applyable string
    
    {'a': 'val', 'b': 'val2'} >> ?a=val&b=val2
    """
    args = []
    for item in Dict:
        args.append(item + "=" + str(Dict[item]))
    args = "&".join(args)
    return "?" + args

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

def TimeStamp():
    """
    Timestamp

    Get a timestamp for the current time
    
    A shortcut to datetime timestamp method

    Timestamp() >> Timestamp in seconds
    """

    return datetime.datetime.now().timestamp()

def Base64ToString(base64data):
    """
    Base64 to String

    Decodes a base64 encoded string of data
    """

    return base64.b64decode(base64data).decode('utf-8')

def StringToBase64(string):
    """
    String to Base64

    Encodes a string of data to base64
    """

    return base64.b64encode(string.encode('utf-8'))

def GetPublicIP():
    """
    Get your public IP address

    ** Requires Internet **

    GetPublicIP() >> Your (Public) IP Address

    """
    return json.loads(requests.get('https://api.ipify.org/?format=json').text)['ip']

def GetOrdinal(number):
    """
    Get Ordinal

    Gets the Ordinal of the given (int) number input

    12 >> 12th
    1 >> 1st
    925 >> 925th
    632 >> 632nd
    """

    if type(number) != type(1):
        try:
            number = int(number)
        except:
            raise ValueError("Intergers only")
    lastdigit = int(str(number)[len(str(number))-1])
    last2 = int(str(number)[len(str(number))-2:])
    if last2 > 10 and last2 < 13:
        return str(number) + "th"
    if lastdigit == 1:
        return str(number) + "st"
    if lastdigit == 2:
        return str(number) + "nd"
    if lastdigit == 3:
        return str(number) + "rd"
    return str(number) + "th"

def AssembleToken(length, AvailChars=False):
    """
    Assemble Token

    Create a randomly generated 'Token' with a-z 1-0 characters
    Change AvailChars to list of your characters
    
    length - int: How long you want the Token to be"""

    if not AvailChars:
        TokenChars = ["a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F", "g", "G", "h", "H", "i", "I", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "o", "O",
                  "p", "P", "q", "Q", "r", "R", "s", "S", "t", "T", "u", "U", "v", "V", "w", "W", "x", "X", "y", "Y", "z", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    else:
        TokenChars = AvailChars
    start = 0
    Token = ""
    while start < length:
        start += 1
        Random = random.randint(0, len(TokenChars) - 1)
        character = TokenChars[Random]
        Token = Token + character
    return Token

def CreateToken(length, AllTokens=[], AvailChars=False):
    """
    Create Token

    Uses AssembleToken To create a token with int(length) characters, validates it is not in your list (AllTokens)

    length - int: How long you want the Token to be
    AllTokens - List/Dict: Your List/Dict of tokens to create against
    AvailChars - list of your characters"""

    Token = AssembleToken(length, AvailChars)
    while Token in AllTokens:
        Token = AssembleToken(length, AvailChars)
    return Token

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

def StringFromTime(time=False):
    """
    String From Time

    Converts a datetime object to string for storage using a system type format

    time - Datetime Object, Current Time: the datetime object you'd like to convert. Defaults to the current date and time.
    
    Datetime (Object) >> 1999-09-24 12:00:00
    """
    if time == False:
        time = datetime.datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S")

def StringToTime(time):
    """
    String To Time
    
    Converts a string, provided by essentials or in same format, to a time for storage use in a program

    time - String: the string you'd like to convert to a datetime object.
    
    1999-09-24 12:00:00 >> Datetime (Object)
    """
    return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

def ReadableTime(time=False):
    """
    Readable Time

    Converts a datetime object to user/front end readable time formatted string

    time - Datetime Object, Current Time: the datetime object you'd like to convert. Defaults to the current date and time.
    
    Datetime (Object) >> Fri Sep 24 12:00 PM
    """
    if time == False:
        time = datetime.datetime.now()
    return time.strftime("%a %b %e %I:%M %p")

def DictData(request):
    """
    Dict Data

    Converts Flask Request Object (from flask import request) to a dictionary with data sent from a POST request

    Use when sending JSON data

    data = DictData(rq) >> {'a': 'value'}
    """

    return json.loads(request.data.decode("utf-8"))

def DictArgs(request):
    """
    Dict Args

    Converts Flask Request Object (from flask import request) to a dictionary from url args

    data = DictArgs(rq) [?a=value&b=value2] >> {'a': 'value', 'b': 'value2'} 
    """

    data = {}
    for item in request.args:
        data[item] = request.args.get(item)
    return data

def DictHeaders(request):
    """
    Dict Headers

    Converts Flask Request Object (from flask import request) to a dictionary with headers sent from a request


    data = DictHeaders(rq) >> {'cookie': 'value', 'accept-language': 'en-US', 'prama': 'no-cache'}
    """
    data = {}
    for item in request.headers:
        data[item[0]] = request.headers.get(item[0])
    return data

def DictForm(request):
    """
    Dict Form

    Converts Flask Request Object (from flask import request) to a dictionary with data sent from a FORM request

    Use when sending FORM data

    data = DictForm(rq) >> {'name': 'mark', 'date': '09/24/1999'}
    """
    data = {}
    for item in request.form:
        data[item] = request.form.get(item)
    return data

class ESRequestObject:
    """
    Es Requests Object
    
    Creates a MkNxGn Essentails Request Object, for use with flask. Simplifies request data into dicts ({}). Pass your request like
    [from flask import request]

    var requestdata = EsRequestObject(request)
    
    
    if 'arg1' in requestdata.args:
        print(requestdata.args['arg1'])
        
    Creates a Dict for the form, args, headers and data. Gives access to request address, json, and memetype."""

    def __init__(self, request):
        try:
            self.form = DictForm(request)
        except:
            self.form = None
        try:
            self.args = DictArgs(request)
        except:
            self.args = None
        try:
            self.headers = DictHeaders(request)
        except:
            self.headers = None
        try:
            self.data = DictData(request)
        except:
            self.data = None
        try:
            self.address = request.remote_addr
        except:
            self.address = None
        self.json = request.get_json(force=True, silent=True)
        try:
            self.meme = request.mimetype
        except:
            self.meme = None
    

class EsTimeObject:
    """
    Es Time Object

    Creates a MkNxGn Essentials Time Object, Use var = EsTimeObject(time) to create the time object. If time is left empty, it will use the current system time.
    time can be the MkNxGn preferred formatted string or a datetime object.

    On creation, you can use
    var.time: to get the datetime object associated with this object,
    var.string: to get the time in a MkNxGn perferred format,
    var.readable: to get the time in a user readable format"""

    def __init__(self, time=datetime.datetime.now()):
        try:
            self.string = StringFromTime(time)
            self.time = time
        except:
            self.time = StringToTime(time)
            self.string = time
        self.readable = ReadableTime(self.time)   

class Timer:

    def __init__(self):
        pass

    def start(self):
        self.Started = TimeStamp()

    def stop(self):
        self.Stopped = TimeStamp()
        self.Seconds = self.Stopped - self.Started
        self.Minutes = self.Seconds/60
        self.Hours = self.Seconds/3600
        self.Days = self.Seconds/86400
        self.Milliseconds = self.Seconds*1000

class EsFileObject:
    """
    Es File Object

    Creates a MkNxGn Essentials File Object, Use var = EsFileObject(filedir) to create the file object. if filedir doesnt exisit, it will create it on save
    
    JSON Capabilities: On creation the object will try to create a json version if the file has json,
    You can access this at var.json,
    You can set the object json with var.setjson(json)
    Update a json key: var.json[key] = value
    You can access the object data at var.data
    You can set the objectt data with var.setdata(data)
    Save the EsFileObject with var.save(), by default this will try to save to the location it came from, unless dirs is set. if json is avalible, it will use json unless json=False
    """
    def __init__(self, dirs):
        self.dirs = dirs
        try:
            self.data = read_file(dirs)
        except:
            self.data = ""
        try:
            self.json = read_json(dirs)
        except:
            self.json = False

    def savedata(self, dirs=False):
        if (dirs == False):
            write_file(self.dirs, self.data)
        else:
            write_file(dirs, self.data)

    def savejson(self, dirs=False):
        if (dirs == False):
            write_json(self.dirs, self.json)
        else:
            if self.json == False:
                raise ValueError("Json Data is not set")
            write_json(dirs, self.json)

    def setdata(self, data):
        self.data = data
        try:
            self.json = json.loads(data)
        except:
            self.json = False

    def setjson(self, jsondata):
        try:
            self.data = json.dumps(jsondata, indent=4, sort_keys=True)
            self.json = jsondata
        except Exception as e:
            raise ValueError("Given 'JSON' is not JSON seriable-" + str(e))

    def save(self, dirs=False, asjson=True):
        if dirs == False:
            dirs = self.dirs
        if self.json != False and asjson:
            write_json(dirs, self.json)
        else:
            write_file(self.dirs, self.data)


def b64_data_to_file(b64_data):
    if BytesIO == False:
        raise ImportError("BytesIO was never found, please install it to use this feature")
    tempfile = BytesIO()
    tempfile.write(base64.b64decode(b64_data))
    tempfile.seek(0)
    return tempfile

def pil_to_memory_file(pil_img):
    if BytesIO == False:
        raise ImportError("BytesIO was never found, please install it to use this feature")
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

def FileToBase64(file):
    if workingDir != False:
        file = os.path.join(workingDir, file)
    fi = open(file, 'rb')
    return base64.b64encode(fi.read())

"""
The following is intended to record package loads.
Nothing about your person, location, or IP Address is recorded.

This task:
Runs in the background,
Keeps a maximum open time of 3 seconds,
Won't run if there is no internet.
Won't keep your program running if your program finishes before it does.
Boosts my moral to keep this package free and up to date.
Allows me to spend more money on what's important by shutting down or suspending what isn't being used.

If you wish to not be apart of this program, please delete these next lines or change true to false.
"""

if True:
    try:
        import threading
        def bg():
            try:
                import requests
                response = requests.get("https://analyticscom.mknxgn.pro/rpg/mknxgn_essentials", timeout=3)
                # If you ever feel like deleting this, uncomment the line below...
                #print(response.text)
            except:
                pass
        threading.Thread(target=bg, daemon=True).start()
    except:
        pass