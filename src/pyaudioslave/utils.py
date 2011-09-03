"""utils.py: Utility functions for pyaudioslave."""

import os
from config import SUPPORTED_TYPES

def setup_dest_path(destination_path):
    """Ensure the path to the desination exists, if not create them
        
        Keyword arguments:
        destination_path -- destination path for the media
    """
    
    dest_dir = os.path.split(destination_path)[0]
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

def get_transcodeable_types():
    """Return supported destination file formats"""
    
    return SUPPORTED_TYPES.keys()