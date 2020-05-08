# mknxgn_essentials
Essentials for python programming.

# Base import
``` python
import essentials
```
# NOTE
Most functions in the base import are being moved to their respective modules, please use those instead.<br>
Functions in this document will be staying here until futher notice.

# What's Inside

``` python
ShrinkLink(long_link)
"""
Shrink a Link via Python and MkNxGn

** Requires an Internet Connection **

Uses MkNxGn's Free Link Shrinking API

takes a (long) url and return a mkls.in short link
"""

SortDictOfDict(Dict, key, reverseOrder=False)
"""
Sort Dictionary of Dictionaries

will parse a dictionary of dictionarys returning it in order based off the keyname you provide

dict = { 'c': {'time_stamp': 150}, 'a': {'time_stamp': 100}, 'b': {'time_stamp': 50}}
key = 'time_stamp'
reverseOrder = True

>> {'b': {'time_stamp': 50}, 'a': {'time_stamp': '100'}, 'c': {'time_stamp': 150}}
"""

DictToArgs(Dict)
"""
Dictionary to URL Args

Give a dictionary of keys and values to convert it to a url applyable string

{'a': 'val', 'b': 'val2'} >> ?a=val&b=val2
"""


```