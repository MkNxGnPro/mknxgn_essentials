import struct, socket, threading, json, os, pickle
from typing import Union, List, Dict
from essentials import tokening
import essentials
import copy
import time
from hashlib import sha1
import base64
import time
import six

PYTHONIC = "python based"
WEBONIC = "web based"
LEGACY = "legacy"

class socketMessageTransport:
    def __init__(self, controller, sock:socket.socket, useMeter=None):
        self.controller:Union[Socket_Server_Client, Socket_Connector] = controller
        self.usage:Transfer_Record = useMeter
        self.pendingMessages = []
        self.socket:socket.socket = sock
        self.buffer = b""
        self.frameInfoSize = struct.calcsize(">L")
        self.fixImports = True
        self.outbound = []
        threading.Thread(target=self.__download__, daemon=True).start()
        threading.Thread(target=self.__upload__, daemon=True).start()


    def sendMessage(self, message):
        self.outbound.append(message)

    @property
    def firstPendingMessage(self):
        while self.pendingMessages.__len__() < 1:
            time.sleep(0.01)
        return self.pendingMessages.pop(0)

    def __upload__(self):
        while self.controller.running:
            try:
                while self.outbound.__len__() <= 0:
                    time.sleep(0.1)
                message = self.outbound.pop(0)
                data = pickle.dumps(message, 0, fix_imports=self.fixImports)
                frame = struct.pack(">L", len(data)) + data
                if self.usage != None:
                    self.usage.sent.add(len(frame))
                self.socket.sendall(frame)
            except:
                self.controller.shutdown()
            time.sleep(0.01)

    def __download__(self):
        while self.controller.running:
            # Download the inital frame size
            while len(self.buffer) < self.frameInfoSize and self.controller.running:
                try:
                    self.buffer += self.socket.recv(self.frameInfoSize)
                except ConnectionResetError:
                    self.controller.shutdown()
                    return
                except socket.timeout as e:
                    pass

            if self.controller.running == False:
                return 
            
            packed_msg_size = self.buffer[:self.frameInfoSize]
            self.buffer = self.buffer[self.frameInfoSize:]

            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(self.buffer) < msg_size and self.controller.running:
                try:
                    self.buffer += self.socket.recv(msg_size - len(self.buffer)) 
                except ConnectionResetError:
                    self.controller.shutdown()
                    return 

            if self.controller.running == False:
                return         

            frame = self.buffer[:msg_size]
            self.buffer = self.buffer[msg_size:]
            if self.usage != None:
                self.usage.received.add(len(frame))
            try:
                message = pickle.loads(frame, fix_imports=self.fixImports, encoding="bytes")
                self.pendingMessages.append(message)
            except EOFError as e:
                print("EOF Error Caught.")
                print(e)
            
def Encode_WebSocket_Message(data="", mask=0):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')

    length = len(data)
    fin, rsv1, rsv2, rsv3, opcode = 1, 0, 0, 0, 0x1

    frame_header = chr(fin << 7 | rsv1 << 6 | rsv2 << 5 | rsv3 << 4 | opcode)

    if length < 0x7e:
        frame_header += chr(mask << 7 | length)
        frame_header = six.b(frame_header)
    elif length < 1 << 16:
        frame_header += chr(mask << 7 | 0x7e)
        frame_header = six.b(frame_header)
        frame_header += struct.pack("!H", length)
    else:
        frame_header += chr(mask << 7 | 0x7f)
        frame_header = six.b(frame_header)
        frame_header += struct.pack("!Q", length)

    return frame_header + data

def SocketUpload_WebBased(sock, data, usage=None):
    """
        Helper function for Socket Classes
    """
    try:
        if type(data) != type(b""):
            print("WARNING: Web Sockets allow byte like data. Make sure your data is encoded next time.")
            data = data.encode()
        frame = Encode_WebSocket_Message(data)
        if usage != None:
            usage.add(len(frame))
        sock.send(frame)
    except Exception as e:
        raise ConnectionError("Connection Error: " + str(e))

def HostServer(HOST, PORT, connections=5, SO_REUSEADDR=True):
    """
        Helper function for Socket Classes
    """
    PORT = int(os.getenv('PORT', PORT))
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if SO_REUSEADDR == True:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST,PORT))
    sock.listen(connections)
    return sock

def ConnectorSocket(HOST, PORT, timeout=5):
    """
        Helper function for Socket Classes
    """
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.settimeout(timeout)
    clientsocket.connect((HOST, PORT))
    return  clientsocket

def WebSocket_Decode_Message(data):
    """
        Helper function for Socket Classes
    """
    data = bytearray(data)
    if(len(data) < 6):
        raise Exception("Error reading data")
    assert(0x1 == (0xFF & data[0]) >> 7)
    assert(0x1 == (0xF & data[0]))
    assert(0x1 == (0xFF & data[1]) >> 7)
    datalen = (0x7F & data[1])
    if(datalen > 0):
        mask_key = data[2:6]
        masked_data = data[6:(6+datalen)]
        unmasked_data = [masked_data[i] ^ mask_key[i%4] for i in range(len(masked_data))]
        resp_data = bytearray(unmasked_data).decode("utf-8")
    else:
        resp_data = ""
    return resp_data

class Transfer_Record(object):
    def __init__(self):
        self.sent = Data_Storage()
        self.received = Data_Storage()
    
class Data_Storage(object):
    def __init__(self):
        self.bytes = 0
        self.commits = 0

    def add(self, count, unit_type="b"):
        if unit_type == "b":
            self.bytes += count
        elif unit_type == "mb":
            self.bytes += (1048576 * count)
        elif unit_type == "gb":
            self.bytes += (1073741824 * count)
        else:
            raise ValueError("unit type not found for conversion")

        self.commits += 1

    @property
    def megabytes(self):
        return self.bytes * 0.000001

    @property
    def gigabyte(self):
        return self.megabytes * 0.001

class Socket_Server_Host:
    def __init__(self, HOST, PORT, on_connection_open, on_data_recv, on_question, on_connection_close=False, daemon=True, autorun=True, connections=5, SO_REUSEADDR=True, heart_beats=True, heart_beat_wait=20, legacy_buffer_size=1024, PYTHONIC_only=False):
        """Host your own Socket server to allows connections to this computer.

        Parameters
        ----------
        HOST (:obj:`str`): Your hosting IP Address for this server.

        PORT (:obj:`int`): Which port you'd like to host this server on.

        on_connection_open (:obj:`def`): The function to call when you get a new connection. Gives Socket_Server_Client Class

        on_data_recv (:obj:`def`): The function to call when you receive data from a connection.

        on_question (:obj:`def`): The function to call when you receive a question from a connection.

        on_connection_close (:obj:`def`, optional): The function to call when a connection is closed.

        daemon (:obj:`bool`, optional): If you'd like the server to close when the python file closes or is interrupted. 

        autorun (:obj:`bool`, optional): Will run the server on init.

        connections (:obj:`int`, optional): How many connections to allow at one time. To be used with autorun = True

        Attributes
        ----------

        running (:obj:`bool`): Is the server still running.

        connections (:obj:`dict`): Holds all connection threads.

        on_connection_open (:obj:`def`): Holds the function you specified to use, can be over written. NOTE: Overwriting this will not overwrite old connection values.

        on_connection_close (:obj:`def`): Holds the function you specified to use, can be over written. NOTE: Overwriting this will not overwrite old connection values.

        on_data_recv (:obj:`def`): Holds the function you specified to use, can be over written. NOTE: Overwriting this will not overwrite old connection values.

        """
        self.on_connection_open = on_connection_open
        self.on_connection_close = on_connection_close
        self.on_data_recv = on_data_recv
        self.HOST = HOST
        self.PORT = PORT
        self.heart_beats = heart_beats
        self.heart_beat_wait = heart_beat_wait
        self.connections = {}
        self.on_question = on_question
        self.running = False
        self.PYTHONIC_only = PYTHONIC_only
        self.legacy_buffer_size = legacy_buffer_size
        if autorun:
            self.Run(connections, daemon, SO_REUSEADDR)
        
    def Run(self, connections=5, daemon=True, SO_REUSEADDR=True):
        """
        Will start the server on the specified host, port and listening count.

        This setup allows you to shutdown, change, and restart the server.

        Parameters
        ----------

        connections (:obj:`int`): How many connections to accept at one time


        :rtype: None

        """
        self.server = HostServer(self.HOST, self.PORT, connections, SO_REUSEADDR)
        self.running = True
        self.broker = threading.Thread(target=self.ConnectionBroker, daemon=daemon)
        self.broker.start()

    def ConnectionBroker(self):
        """
        Server background task for accepting connections, you'll not need to use this.

        :rtype: None

        """
        while self.running:
            try:
                conn, addr = self.server.accept()
                if self.running == False:
                    conn.close()
                    return
                conID = tokening.CreateToken(12, self.connections)
                connector = Socket_Server_Client(conn, addr, self, conID, self.on_connection_open, self.on_data_recv, on_question=self.on_question, on_close=self.close_connection, Heart_Beat=self.heart_beats, Heart_Beat_Wait=self.heart_beat_wait, legacy_buffer_size=self.legacy_buffer_size, PYTHONIC_only=self.PYTHONIC_only)
                self.connections[conID] = connector
                time.sleep(0.05)
            except Exception as e:
                self.running = False
                raise e
                
    def close_connection(self, connection):
        """
        Server background task for clearing connections and notifying the parent file, you'll not need to use this.

        :rtype: None

        """
        try:
            self.on_connection_close(connection)
        except:
            pass
        del self.connections[connection.conID]

    def Shutdown(self):
        """
        Shutdown the server and close all connections.

        :rtype: None

        """
        self.running = False
        keys = list(self.connections.keys())
        for con in keys:
            try:
                self.connections[con].shutdown()
            except:
                pass
        self.connections = {}
        try:
            self.server.close()
        except:
            pass

    def CloseConnection(self, conID):
        """
        Shortcut to close a certain connection.

        Can also be used as Server.connections[conID].shutdown()

        :rtype: None

        """
        self.connections[conID].shutdown()

class Socket_Server_Client:

    def __init__(self, sock, addr, server, conID, on_connection_open, on_data, on_question, on_close, Heart_Beat=True, Heart_Beat_Wait=20, legacy_buffer_size=1024, PYTHONIC_only=False):
        """CLIENT for Socket_Server_Host"""
        self.socket:socket.socket = sock
        self.addr = addr
        self.server = server
        self.conID = conID
        self.on_data = on_data
        self.on_close = on_close
        self.running = True
        self.meta = {}
        self.data_usage = Transfer_Record()
        self.client_type = None
        self.on_question = on_question
        self.legacy_buffer_size = legacy_buffer_size
        self.__get_next__ = False
        self.__ask_list__ = {}
        self.created = essentials.TimeStamp()
        self.heart_beat_wait = Heart_Beat_Wait
        self.heart_beat = Heart_Beat
        self.PYTHONIC_only = PYTHONIC_only
        self.pendingQuestions:Dict[str, Socket_Question] = {}
        if PYTHONIC_only:
            self.client_type = PYTHONIC
            self.dataManager = socketMessageTransport(self, self.socket, self.data_usage)
            threading.Thread(target=self.__data_rev__, daemon=True).start()
            if self.heart_beat == True:
                self.socket.setblocking(1)
                threading.Thread(target=self.__heart_beat__, daemon=True).start()
            threading.Thread(target=on_connection_open, args=[self]).start()
        else:
            threading.Thread(target=self.__detect_client_type__, args=[on_connection_open]).start()

    def __detect_client_type__(self, on_open):
        firstMessage = self.dataManager.firstPendingMessage
        if type(firstMessage) != bytes:
            firstMessage = str(firstMessage).encode()

        if b"PING" in firstMessage:
            try:
                self.socket.send(b"PONG")
            except:
                pass
            self.shutdown()
            return

        if b"permessage-deflate" in firstMessage:
            self.client_type = WEBONIC
            GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            msg = firstMessage.decode("utf-8")
            vals = msg.replace("\r", "").split("\n")
            headers = {}
            for item in vals:
                if item != "" and ":" in item:
                    headers[item.split(":")[0]] = item.split(": ")[1]
            self.WEBONIC_headers = headers
            key = headers['Sec-WebSocket-Key']
            sha1f = sha1()
            sha1f.update(key.encode('utf-8') + GUID.encode('utf-8'))
            response_key = base64.b64encode(sha1f.digest()).decode('utf-8')
            websocket_answer = (
                'HTTP/1.1 101 Switching Protocols',
                'Upgrade: websocket',
                'Connection: Upgrade',
                'Sec-WebSocket-Accept: {key}\r\n\r\n',
            )
            response = '\r\n'.join(websocket_answer).format(key=response_key)
            self.socket.send(response.encode('utf-8'))
            self.socket.settimeout(0.5)
        elif b"pythonic" in firstMessage:
            self.client_type = PYTHONIC
        else:
            self.socket.settimeout(0.075)
            self.client_type = LEGACY

        threading.Thread(target=on_open, args=[self], daemon=True).start()
        threading.Thread(target=self.__data_rev__, daemon=True).start()

        if self.heart_beat == True and self.client_type == PYTHONIC:
            self.socket.setblocking(1)
            threading.Thread(target=self.__heart_beat__, daemon=True).start()

    def __heart_beat__(self):
        while self.running:
            self.send({"heart_beat_function": True})
            time.sleep(self.heart_beat_wait)

    def shutdown(self):
        """
        Shuts down this connection and removes any place it is still stored. Completes the on_close event.

        :rtype: None

        """
        
        try:
            self.on_close(self)
        except:
            pass
        self.running = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass

    def send(self, data):
        """
        Send data to the remote connection.

        :rtype: None

        """
        timeout = 0
        while self.client_type == None and timeout < 4:
            time.sleep(0.01)
            timeout += 0.01

        if self.client_type == None:
            raise ValueError("Couldn't detect Client Type.")

        if self.running == False:
            raise ConnectionResetError("No Connection")
        
        if self.client_type == PYTHONIC:
            try:
                self.dataManager.sendMessage(data)
            except Exception as e:
                print("EXCEPTION:", e)
                self.shutdown()
        elif self.client_type == WEBONIC:
            try:
                SocketUpload_WebBased(self.socket, data, self.data_usage.sent)
            except Exception as e:
                print(e)
                self.shutdown()
        elif self.client_type == LEGACY:
            try:
                self.socket.sendall(data)
            except Exception as e:
                print("EXCEPTION:", e)
                self.shutdown()

    def ask(self, data, timeout=5):
        if self.client_type == WEBONIC:
            print("WARNING: ask for Web Based Clients is not currently supported.")
            return False
        tok = essentials.CreateToken(20, self.__ask_list__)
        self.__ask_list__[tok] = False
        self.send({"function_ask_question": tok, "data": data})
        while self.__ask_list__[tok] == False and self.running == True:
            time.sleep(0.01)
            timeout -= 0.01
            if timeout <= 0:
                raise TimeoutError("No response within time.")
        if self.__ask_list__[tok] == False and self.running == False:
            raise ConnectionError("We've been disconnected while waiting for a response")
        copyed = copy.deepcopy(self.__ask_list__[tok])
        del self.__ask_list__[tok]
        return copyed['data']

    def get_next(self):
        self.__get_next__ = True
        self.get_next_data = False
        while self.__get_next__ == True:
            time.sleep(0.05)
        return self.get_next_data

    def __data_rev__(self):
        """
        Server background task for accepting data and run the on_data event, you'll not need to use this.

        :rtype: None

        """
        if self.client_type == PYTHONIC:
            while self.running:
                try:
                    data = self.dataManager.firstPendingMessage
                except:
                    self.shutdown()
                    return
                if type(data) == type({}) and "pythonic" in data:
                    pass
                elif type(data) == type({}) and 'heart_beat_function' in data:
                    pass
                elif type(data) == type({}) and 'function_ask_response' in data:
                    self.__ask_list__[data['function_ask_response']] = data
                elif type(data) == type({}) and 'function_ask_question' in data:
                    question = Socket_Question(data['data'], self, data['function_ask_question'])
                    self.pendingQuestions[question.__answer_token__] = question
                    threading.Thread(target=self.on_question, args=[question], daemon=True).start()
                else:
                    if self.__get_next__ == True:
                        self.get_next_data = data
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.on_data, args=[data, self], daemon=True).start()
                time.sleep(0.05)
        elif self.client_type == WEBONIC:
            while self.running:
                msg = b""
                conti = True
                while conti:
                    buffer = b""
                    while b"\n" not in buffer:
                        try:
                            buffer += self.socket.recv(1)
                        except:
                            conti = False
                            break
                        time.sleep(0.01)
                    msg += buffer
                if msg != b"":
                    self.data_usage.received.add(len(msg))
                    try:
                        socket_message = WebSocket_Decode_Message(msg)
                    except:
                        pass
                    try:
                        socket_message = json.loads(socket_message)
                    except:
                        pass
                    if self.__get_next__ == True:
                        self.get_next_data = data
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.on_data, args=[socket_message, self], daemon=True).start()
                time.sleep(0.01)
        elif self.client_type == LEGACY:
            while self.running:
                msg = b""
                conti = True
                while b"\n" not in msg:
                    try:
                        msg += self.socket.recv(self.legacy_buffer_size)
                    except:
                        conti = False
                        break
                    time.sleep(0.01)
                if msg != b"":
                    self.data_usage.received.add(len(msg))
                    if self.__get_next__ == True:
                        self.get_next_data = data
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.on_data, args=[msg, self], daemon=True).start()
                time.sleep(0.01)

class Socket_Question:
    def __init__(self, data, client, tok):
        self.data = data
        self.questioner:Union[Socket_Connector, Socket_Server_Client] = client
        self.__answer_token__ = tok
        self.answered = False
    
    def answer(self, data):
        self.questioner.send({"function_ask_response": self.__answer_token__, "data": data})
        self.answered = True

    def __repr__(self) -> str:
        return f"<Question: ID: {self.__answer_token__}, Answered: {self.answered}, {str(self.data)[:15]}>"

class Configuration(object):

    def __init__(self, default=PYTHONIC, on_data_recv=None, on_question=None, on_connection_close=None):
        self.client_type = default
        self.heart_beat = True
        self.heart_beat_wait = 10
        self.legacy_buffer_size = 1024
        self.socket_timeout = 0.25
        self.on_data_recv = on_data_recv
        self.on_question = on_question
        self.on_connection_close = on_connection_close
        self.server_PYTHONIC_only = False

    @property
    def PYTHONIC(self):
        return self.client_type == "python based"

    @PYTHONIC.setter
    def PYTHONIC(self, value):
        if value == True:
            self.client_type = "python based"
        else:
            raise ValueError("Setting value must be True")

    @property
    def WEBONIC(self):
        return self.client_type == "web based"

    @WEBONIC.setter
    def WEBONIC(self, value):
        if value == True:
            self.client_type = "web based"
        else:
            raise ValueError("Setting value must be True")

    @property
    def LEGACY(self):
        return self.client_type == "legacy"

    @LEGACY.setter
    def LEGACY(self, value):
        if value == True:
            self.client_type = "legacy"
        else:
            raise ValueError("Setting value must be True")

class Socket_Connector:

    def __init__(self, HOST, PORT, Config=Configuration(PYTHONIC)):
        """Host your own Socket server to allows connections to this computer.

        Parameters
        ----------
        HOST (:obj:`str`): The hosting IP Address for the server.

        PORT (:obj:`int`): The port the server is using.

        Attributes
        ----------

        running (:obj:`bool`): Is the server still running.

        on_connection_close (:obj:`def`): Holds the function you specified to use, can be over written.

        on_data_recv (:obj:`def`): Holds the function you specified to use, can be over written.

        """
        self.running = False
        self.HOST = HOST
        self.PORT = PORT
        self.data_usage = Transfer_Record()
        self.__ask_list__ = {}
        self.__get_next__ = False
        self.configuration = Config
        self.pendingQuestions:Dict[str, Socket_Question] = {}

    def get_next(self, timeout=30):
        self.__get_next__ = True
        self.get_next_data = False
        start = 0
        while self.__get_next__ == True and self.running == True and start < timeout:
            time.sleep(0.05)
            start += 0.05
        if self.running == False:
            raise ConnectionResetError("The connection was closed.")
        if start >= timeout:
            raise TimeoutError("No response in time.")
        return self.get_next_data
        
    def connect(self, timeout=5):
        if self.configuration.WEBONIC:
            raise NotImplementedError("Websocket Clients Haven't been Implemented Yet.")
        self.socket = ConnectorSocket(self.HOST, self.PORT, timeout)
        self.running = True
        if self.configuration.PYTHONIC == True:
            self.dataManager = socketMessageTransport(self, self.socket, self.data_usage)
            self.send({"pythonic": True})
            if self.configuration.server_PYTHONIC_only == False:
                time.sleep(2)
            if self.configuration.heart_beat == True:
                threading.Thread(target=self.__heart_beat__, daemon=True).start()
        elif self.configuration.WEBONIC == True:
            self.socket.settimeout(self.configuration.socket_timeout)
        elif self.configuration.LEGACY == True:
            self.socket.settimeout(self.configuration.socket_timeout)
        else:
            raise ValueError("No configuration values set.")

        threading.Thread(target=self.__data_rev__, daemon=True).start()

    def __heart_beat__(self):
        while self.running:
            time.sleep(self.configuration.heart_beat_wait)
            self.send({"heart_beat_function": True})
            
    def ask(self, data, timeout=5):
        if self.configuration.PYTHONIC != True:
            print("ERROR: Can't ask questions to non-Pythonic connections")
            return
        tok = essentials.CreateToken(20, self.__ask_list__)
        self.__ask_list__[tok] = False
        self.send({"function_ask_question": tok, "data": data})
        while self.__ask_list__[tok] == False and self.running == True:
            time.sleep(0.01)
            timeout -= 0.01
            if timeout <= 0:
                raise TimeoutError("No response within time.")
        if self.__ask_list__[tok] == False and self.running == False:
            raise ConnectionError("We've been disconnected while waiting for a response")
        copyed = copy.deepcopy(self.__ask_list__[tok])
        del self.__ask_list__[tok]
        return copyed['data']

    def send(self, data):
        """
        Send data to the remote connection.

        :rtype: None

        """
        if self.running == False:
            raise ConnectionResetError("No Connection")
        try:
            if self.configuration.LEGACY:
                self.socket.sendall(data)
            elif self.configuration.PYTHONIC:
                self.dataManager.sendMessage(data)
            elif self.configuration.WEBONIC:
                self.socket.send(data)
        except Exception as e:
            print(e)
            self.shutdown()

    def shutdown(self):
        """
        Shuts down this connection. Completes the on_close event.

        :rtype: None

        """
        self.running = False
        try:
            self.configuration.on_connection_close()
        except:
            print("WARN: No On Close Function")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
    
    def __data_rev__(self):
        """
        Client background task for accepting data and run the on_data event, you'll not need to use this.

        :rtype: None

        """
        if self.configuration.LEGACY:
            while self.running:
                msg = b""
                while b"\n" not in msg:
                    try:
                        msg += self.socket.recv(self.configuration.legacy_buffer_size)
                    except Exception as e:
                        break
                    time.sleep(0.01)
                if msg != b"":
                    self.data_usage.received.add(len(msg))
                    if self.__get_next__ == True:
                        self.get_next_data = msg
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.configuration.on_data_recv, args=[msg], daemon=True).start()
                time.sleep(0.01)
        elif self.configuration.PYTHONIC:
            while self.running:
                try:
                    toDel = []
                    for id in self.pendingQuestions:
                        q = self.pendingQuestions[id]
                        if q.answered:
                            toDel.append(id)
                    for id in toDel:
                        del self.pendingQuestions[id]
                except:
                    pass
                try:
                    data = self.dataManager.firstPendingMessage
                except ConnectionError as e:
                    print(e.errno)
                    print("shutting down", e)
                    self.shutdown()
                    raise e
                except Exception as e:
                    print("Error main", e)
                    continue
                if type(data) == type({}) and 'heart_beat_function' in data:
                    pass
                elif type(data) == type({}) and 'function_ask_response' in data:
                    self.__ask_list__[data['function_ask_response']] = data
                elif type(data) == type({}) and 'function_ask_question' in data:
                    question = Socket_Question(data['data'], self, data['function_ask_question'])
                    self.pendingQuestions[question.__answer_token__] = question
                    threading.Thread(target=self.configuration.on_question, args=[question], daemon=True).start()
                else:
                    if self.__get_next__ == True:
                        self.get_next_data = data
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.configuration.on_data_recv, args=[data], daemon=True).start()
        elif self.configuration.WEBONIC:
            while self.running:
                msg = b""
                conti = True
                while conti:
                    buffer = b""
                    while b"\n" not in buffer:
                        try:
                            buffer += self.socket.recv(1)
                        except:
                            conti = False
                            break
                        time.sleep(0.001)
                    msg += buffer
                if msg != b"":
                    self.data_usage.received.add(len(msg))
                    socket_message = msg
                    try:
                        socket_message = WebSocket_Decode_Message(socket_message)
                    except:
                        pass
                    try:
                        socket_message = json.loads(socket_message)
                    except:
                        pass
                    try:
                        socket_message = socket_message.decode()
                    except:
                        pass
                    if self.__get_next__ == True:
                        self.get_next_data = data
                        self.__get_next__ = False
                    else:
                        threading.Thread(target=self.configuration.on_data_recv, args=[socket_message], daemon=True).start()
                time.sleep(0.01)

class UDP_Server_Client(object):
    def __init__(self, addr, on_data, server):
        self.on_data = on_data
        self.addr = addr
        self.server = server
        self.meta = {}

    def __attemp_data_delivery__(self, data):
        def _attempt_():
            try:
                self.on_data(data, self)
            except:
                pass
        threading.Thread(target=_attempt_, daemon=True).start()

    def send(self, data):
        self.server.sendto(data, self.addr)

class UDP_Server(object):

    def __init__(self, HOST, PORT, on_new_client=None, on_data=None, timeout=1, max_buffer=1024):
        self.clients = {}
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.settimeout(timeout)
        self.on_data = on_data
        self.max_buffer = max_buffer
        self.on_new_client = on_new_client

        def data_recv():
            while True:
                try:
                    data, address = server.recvfrom(self.max_buffer)
                except:
                    continue
                client_ad = ":".join([str(address[0]), str(address[1])])
                if client_ad not in self.clients:
                    self.clients[client_ad] = UDP_Server_Client(address, self.on_data, server)
                    threading.Thread(target=self.on_new_client, daemon=True, args=[self.clients[client_ad]]).start()
                self.clients[client_ad].__attemp_data_delivery__(data)
                

        threading.Thread(target=data_recv, daemon=True).start()
    
    def shutdown(self):
        """
        Shuts down this connection.

        :rtype: None

        """
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass

class UDP_Connector(object):

    def __init__(self, HOST, PORT, on_data=None, timeout=1, max_buffer=1024):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (HOST, PORT)
        self.clientSocket.settimeout(timeout)
        self.max_buffer = max_buffer
        self.on_data = on_data

        def data_recv():
            while True:
                try:
                    data, address = self.clientSocket.recvfrom(self.max_buffer)
                except Exception as e:
                    continue
                if self.on_data != None:
                    threading.Thread(target=self.on_data, daemon=True, args=[data, address]).start()

        threading.Thread(target=data_recv, daemon=True).start()

    def send(self, data):
        self.clientSocket.sendto(data, self.address)

"""
The following is intended to record package loads.
Nothing about your person, location, or IP Address is recorded.

This task:
Runs in the background,
Keeps a maximum open time of 3 seconds,
Won't run if there is no internet.
Won't keep your program running if your program finishes before it does.
Boosts my moral to keep this package free and up to date.

This specific placement is to determin if Socket_Ops should become it's own package.

If you wish to not be apart of this program, please delete these next lines or change true to false.
"""

if True:
    try:
        import threading
        def bg():
            try:
                import requests
                response = requests.get("https://analyticscom.mknxgn.pro/rpg/mknxgn_essentials_SOP_V2", timeout=3)
                # If you ever feel like deleting this, uncomment the line below...
                #print(response.text)
            except:
                pass
        threading.Thread(target=bg, daemon=True).start()
    except:
        pass