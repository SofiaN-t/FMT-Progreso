# This script locates the configuration file
import os
import json

def load_config(config_file='config.json'):
    # Determine the absolute path to the config file
    config_file_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_file_path, 'r') as f:
        return json.load(f)