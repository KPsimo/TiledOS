import os
from pathlib import Path

# Get absolute paths
# BASE_DIR = Path(__file__).parent.resolve()
# CREDENTIALS_PATH = BASE_DIR / "data" / "credentials.json"

# print("Current working directory:", Path.cwd())
# print("Script is located at:", BASE_DIR)
# print("Looking for credentials at:", CREDENTIALS_PATH)

# # Check existence and contents
# if CREDENTIALS_PATH.exists():
#     print("Found credentials.json!")
#     print("   Full path:", CREDENTIALS_PATH.resolve())
# else:
#     print("credentials.json not found.")
#     print("   Make sure it's inside a folder named 'data' next to your TasksSync.py file.")
#     print("   Example expected structure:")
#     print("   project_folder/")
#     print("   ├── TasksSync.py")
#     print("   └── data/")
#     print("       └── credentials.json")

def checkGoogleCredentials():
    BASE_DIR = Path(__file__).parent.resolve()
    CREDENTIALS_PATH = BASE_DIR / "data" / "credentials.json"

    if CREDENTIALS_PATH.exists():
        return True
    else:
        print("credentials.json not found.")
        print("   Make sure it's inside a folder named 'data' next to your TasksSync.py file.")
        print("   Example expected structure:")
        print("   project_folder/")
        print("   ├── TasksSync.py")
        print("   └── data/")
        print("       └── credentials.json")
        return False

def checkKeysFile():
    BASE_DIR = Path(__file__).parent.resolve()
    KEYS_PATH = BASE_DIR / "data" / "keys.py"

    if KEYS_PATH.exists():
        return True
    else:
        print("keys.py not found.")
        print("   Make sure it's inside a folder named 'data' next to your TasksSync.py file.")
        print("   Example expected structure:")
        print("   project_folder/")
        print("   ├── TasksSync.py")
        print("   └── data/")
        print("       └── keys.py")
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

def checkAll():
    credentialsOk = checkGoogleCredentials()
    keysFileOk = checkKeysFile()
    keysOk = False

    if keysFileOk:
        keysOk = checkForKeys()

    return credentialsOk and keysFileOk and keysOk