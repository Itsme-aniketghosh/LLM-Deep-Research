"""
Colored console logger
"""

class C:
    R = "\033[0m"
    B = "\033[94m"
    G = "\033[92m"
    Y = "\033[93m"
    M = "\033[95m"
    RED = "\033[91m"

def info(tag, msg): print(f"{C.B}[{tag}]{C.R} {msg}")
def success(tag, msg): print(f"{C.G}[{tag}] ✓{C.R} {msg}")
def warning(tag, msg): print(f"{C.Y}[{tag}] ⚠{C.R} {msg}")
def error(tag, msg): print(f"{C.RED}[{tag}] ✗{C.R} {msg}")
def step(tag, msg): print(f"{C.M}[{tag}] →{C.R} {msg}")
def data(tag, msg): print(f"{C.B}[{tag}]{C.R} {msg}")

# Windows support
import sys
if sys.platform == "win32":
    import os
    os.system("")
