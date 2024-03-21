import sys

from config.light_config import light_map, number_of_columns, number_of_rows
from config.directories import PARENT_DIR, YAMLS_DIR, AUDIO_DIR , LIGHT_DIR , SOUND_DIR
sys.path.append(LIGHT_DIR)
sys.path.append(SOUND_DIR)



__all__ = [
    "light_map", "number_of_columns", "number_of_rows", "PARENT_DIR", "YAMLS_DIR", "AUDIO_DIR", "LIGHT_DIR", "SOUND_DIR"
]
