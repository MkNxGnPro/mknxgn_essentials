from essentials import socket_ops_v2 as socket_ops
from essentials import run_data
from essentials import network_ops
import time

args = run_data.Run_Data(__name__)
SocketPort = args.add_arg(default_arg=run_data.Default_Arg("port", description="Use this to set the Socket's Port.", arg_type=run_data.INT))
SocketIP = args.add_arg(default_arg=run_data.Default_Arg("ip", description="Use this to set the Socket's IP Address.", default="127.0.0.1", required=False))
DestPort = args.add_arg(default_arg=run_data.Default_Arg("destport", description="Use this to set the Destination Port."))
DestIP = args.add_arg(default_arg=run_data.Default_Arg("dest", description="Use this to set the Destination IP Address or Host Address.", required=True))

def NewConnector(client=socket_ops.Socket_Server_Client):
    print("New connector")
    client.meta['proxy'] = socket_ops.Socket_Connector(DestIP, DestPort)
    config = socket_ops.Configuration(socket_ops.LEGACY, client.send, None, None)
    client.meta['proxy'].configuration = config
    client.meta['proxy'].connect()
    client.on_data = client.meta['proxy'].send
    

Server = socket_ops.Socket_Server_Host(SocketIP, SocketPort, NewConnector, None, None, None, connections=0, heart_beats=False)
print("Server Running - IP:", SocketIP, "   PORT:", SocketPort)

try:
    while True:
        time.sleep(2)
except:
    pass