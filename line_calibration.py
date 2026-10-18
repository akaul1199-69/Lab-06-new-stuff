"""SOME INFO: save/load the black/white calibration as JSON (Lab 0x06).

File format (same as the course helper):
  {"channels": [1 to 13], "black": [13 averages], "white": [13 averages]}
Values are raw ADC averages on the 0-4095 scale (NOT normalized weights).
"""
import json

CAL_FILE = "line_calibration.json"


def save_calibration(channels, black, white, path=CAL_FILE):
    data = {"channels": list(channels),
            "black": [round(x, 1) for x in black],
            "white": [round(x, 1) for x in white]}
    with open(path, "w") as f:
        json.dump(data, f)


def load_calibration(path=CAL_FILE, n=13):
    """Return the dict, or None if the file is missing or invalid."""
    try:
        with open(path) as f:
            data = json.load(f)
        for key in ("channels", "black", "white"):
            if len(data[key]) != n:
                return None
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return None
