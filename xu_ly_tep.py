import json
import pathlib as pl
import sys
import os

def luu_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def tra_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
    
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)