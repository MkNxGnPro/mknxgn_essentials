from essentials import socket_ops_v2 as socket_ops
from essentials import run_data
import time

args = run_data.Run_Data(__name__)
SocketPort = args.add_arg(default_arg=run_data.Default_Arg("port", description="Use this to set the Socket's Port.", arg_type=run_data.INT))
SocketIP = args.add_arg(default_arg=run_data.Default_Arg("ip", description="Use this to set the Socket's IP Address.", default="127.0.0.1", required=False))
DestPort = args.add_arg(default_arg=run_data.Default_Arg("destport", description="Use this to set the Destination Port.", arg_type=run_data.INT))
DestIP = args.add_arg(default_arg=run_data.Default_Arg("dest", description="Use this to set the Destination IP Address or Host Address.", required=True))

def new_connector(client=socket_ops.UDP_Server_Client):
    print("New connection")
    client.meta['proxy'] = socket_ops.UDP_Connector(DestIP, DestPort, timeout=3)
    client.meta['proxy'].on_data = client.send
    client.on_data = client.meta['proxy'].send


Server = socket_ops.UDP_Server(SocketIP, SocketPort, new_connector)

while True:
    time.sleep(1)