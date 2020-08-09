import json, base64, os

workingDir = False

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