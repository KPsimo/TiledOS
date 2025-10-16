import os
from pathlib import Path

# Get absolute paths
BASE_DIR = Path(__file__).parent.resolve()
CREDENTIALS_PATH = BASE_DIR / "data" / "credentials.json"

print("🧭 Current working directory:", Path.cwd())
print("📄 Script is located at:", BASE_DIR)
print("🔎 Looking for credentials at:", CREDENTIALS_PATH)

# Check existence and contents
if CREDENTIALS_PATH.exists():
    print("✅ Found credentials.json!")
    print("   Full path:", CREDENTIALS_PATH.resolve())
else:
    print("❌ credentials.json not found.")
    print("   Make sure it’s inside a folder named 'data' next to your TasksSync.py file.")
    print("   Example expected structure:")
    print("   project_folder/")
    print("   ├── TasksSync.py")
    print("   └── data/")
    print("       └── credentials.json")