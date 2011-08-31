"""utils.py: Utility functions for pyaudioslave."""

import math
import os
from base64 import b64encode
from config import TEMP_PREFIX, SUPPORTED_TYPES

def setup_dest_path(destination_path):
    """Ensure the path to the desination exists, if not create them
        
        Keyword arguments:
        destination_path -- destination path for the media
    """
    
    dest_dir = os.path.split(destination_path)[0]
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

def get_temp_path():
    """Helper function to generate a unique filename for WAV file
       in defined TEMP_PREFIX directory."""
    
    #Taken from here :http://code.activestate.com/recipes/576722-pseudo-random-string/
    rand_str = lambda n: b64encode(os.urandom(int(math.ceil(0.75*n))),'-_')[:n]
    
    setup_dest_path(TEMP_PREFIX)
    while True:
        temp_path = os.path.join(TEMP_PREFIX, rand_str(10))
        if not os.path.exists(temp_path):
            return temp_path

def get_transcodeable_types():
    """Return supported destination file formats"""
    
    return SUPPORTED_TYPES.keys()