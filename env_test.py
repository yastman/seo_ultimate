import pandas as pd
import sys
import platform

print("-" * 30)
print(f"Python Version: {platform.python_version()}")
print(f"Executable: {sys.executable}")
try:
    print(f"Pandas Version: {pd.__version__}")
    print("SUCCESS: Pandas imported successfully.")
except ImportError:
    print("ERROR: Pandas not found.")

print("-" * 30)
print("Environment check complete.")
