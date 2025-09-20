"""This module contains functions to read, write, and validate the config.json file.

Functions:
    - cfgExists: Checks if the config file exists.
    - setDefaultParams: Creates or resets the config file with default values.
    - readCfg: Reads the config file, creating it if it doesn't exist or is corrupt.
    - writeCfg: Writes a key-value pair to the config file.
    - getKeyValue: Retrieves a value from the config file by its key.
"""

import os
import json

config_file = "config.json"

def cfgExists() -> bool:
    """Checks if the 'config.json' file exists in the current directory.

    Args:
        None

    Returns:
        bool: True if 'config.json' exists, False otherwise.
    """
    if not os.path.exists(config_file):
        return False
    return True


def setDefaultParams():
    """Creates or resets the 'config.json' file with default parameters.

    This function creates a new 'config.json' file with a default structure,
    including a `path` key with an empty string as its value. If the file
    already exists, it will be overwritten.

    Args:
        None

    Returns:
        None
    """
    data = {
    "path": ""
    }
    try:
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        # Handle cases where file can't be written (e.g., permissions)
        print(f"Error: Could not write config file: {e}")
        

def readCfg() -> dict:
    """Reads the 'config.json' file and returns its content.

    If the file does not exist or is corrupted, it will be recreated with
    default values before reading.

    Args:
        None

    Returns:
        dict: A dictionary containing the configuration data.
    """
    if not cfgExists():
        setDefaultParams()
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # File is corrupt, reset to defaults
        setDefaultParams()
        try:
            # Re-read the freshly written default file
            with open(config_file, 'r') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            # If it fails again, something is badly wrong
            print(f"Error: Failed to read config after reset: {e}")
            return {"path": ""} # Return in-memory fallback
    except IOError as e:
        print(f"Error: Could not read config file: {e}")
        return {"path": ""} # Return in-memory fallback
        
    return data
        
        
def writeCfg(key, value):
    """Writes a key-value pair to the 'config.json' file.

    Args:
        key (str): The key to be added or updated in the config file.
        value (any): The value to be associated with the key.

    Returns:
        None
    """
    data = readCfg() # Now robust
    data[key] = value
    try:
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
         print(f"Error: Could not write config update: {e}")
        

def getKeyValue(key):
    """Retrieves the value for a given key from the 'config.json' file.

    Args:
        key (str): The key whose value is to be retrieved.

    Returns:
        any: The value associated with the key, or None if the key is not found.
    """
    data = readCfg() # Now robust
    return data.get(key)
        
