import random

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