import os
from pathlib import Path
import pygame

def checkGoogleCredentials():
    BASE_DIR = Path(__file__).parent.resolve()
    CREDENTIALS_PATH = BASE_DIR / "data" / "credentials.json"

    if CREDENTIALS_PATH.exists():
        return True
    else:
        print("data/credentials.json not found.")
        return False

def checkKeysFile():
    BASE_DIR = Path(__file__).parent.resolve()
    KEYS_PATH = BASE_DIR / "data" / "keys.py"

    if KEYS_PATH.exists():
        return True
    else:
        print("data/keys.py not found.")
        return False

def checkForKeys():
    import data.keys as keys

    try:
        keys.openaiKey
        keys.canvasKey

        return True

    except Exception as e:
        print("Error: keys.py is missing required keys.")
        print("Please ensure keys.py contains 'openaiKey' and 'canvasKey' variables.")

        return False

def checkAllSecrets():
    credentialsOk = checkGoogleCredentials()
    keysFileOk = checkKeysFile()
    keysOk = False

    if keysFileOk:
        keysOk = checkForKeys()

    return credentialsOk and keysFileOk and keysOk