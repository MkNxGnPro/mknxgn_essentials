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


### <b>ShrinkLink(long_url)</b> <span style="color:red">Requires an Internet Connection</span><br>
```
    Shrink a Link via Python and MkNxGn
    Uses MkNxGn's Free Link Shrinking API
    takes a long url and return a mkls.in short link

    Example:
    https://github.com/MkNxGnPro/mknxgn_essentials/tree/master/essentials

    Returns:
    https://mkls.in/zXC
```

### <b>SortDictOfDict(Dict, key, reverseOrder=False)</b>
```
    Sort Dictionary of Dictionaries

    Parses a dictionary of containing dictionarys, returns it in order based off the keyname you provide.

    Example:
```
``` python
unsorted = { 'c': {'time_stamp': 150}, 'a': {'time_stamp': 100}, 'b': {'time_stamp': 50}}
key = 'time_stamp'  # The key you want to sort by
reverseOrder = True # Accending Order

essentials.SortDictOfDict(unsorted, key)
>> {'b': {'time_stamp': 50}, 'a': {'time_stamp': '100'}, 'c': {'time_stamp': 150}}
```

### <b>DictToArgs(Dict)</b>
```
    Dictionary to URL Args
    Give a dictionary of keys and values to convert it to a url applyable string

    Example:
```
``` python
keys = {'a': 'val', 'b': 'val2'}
essentials.DictToArgs(keys)

>> "?a=val&b=val2"

```

<b>Note:</b> Documentation is still being processed