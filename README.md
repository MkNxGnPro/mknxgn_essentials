# mknxgn_essentials
Essentials for python programming.

This is the package we compile essentials code we use in our products that we deem as "essential".

Installing
```
pip3 install mknxng_essentials
```

# What's Inside


## essentials.file_ops
Read and Write Files.<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Writing JSON files.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reading JSON files.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Writing 'Soft' encryption files<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reading 'Soft' encryption files<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tar Decompressing<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Generating Files of X size in MB<br>

``` python
from essentials import file_ops
```

## essentials.logger_ops
Write Log Files.<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Debugging with --debug parameter<br>

``` python
from essentials import logger_ops
```

## essentials.run_data
Collects file running data.<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Argument Parser<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;File Run Time<br>

``` python
from essentials import run_data
```

## essentials.socket_ops
Socket Engine <b>Note:</b> this item has been depreciated, please use essentials.socket_ops_v2<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Socket Hosting Server<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Socket Connecting Client<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WebSocket Support<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Multiple Resources to make socketing with python easier<br>

``` python
from essentials import socket_ops
```
## essentials.socket_ops_v2
Socket Engine <b>Note:</b> Documentation for this module is not complete<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Socket Hosting Server<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Socket Connecting Client<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WebSocket Support<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Multiple Resources to make socketing with python easier<br>

``` python
from essentials import socket_ops_v2
```

## essentials.time_events
Time Events <b>Note:</b> Documentation for this module is not complete<br>
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Time Event Listener, Calls function when second/minute/hour/day/week/month/year change occurs<br>

``` python
from essentials import time_events
```

## essentials.tokening
Unique Tokening
Includes:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Assemble Token, Assemble a token at (x)Length with predefined or custom characters<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Create Token, Create a token at (x)Length with predefined or custom characters and check is it exists in (y), if so, recreate it. <br>

``` python
from essentials import tokening
```
