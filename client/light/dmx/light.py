"""Module for DMX light definitions."""

# BSD 3-Clause License
#
# Copyright (c) 2019-2022, Jacob Allen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from abc import ABC, abstractmethod
from typing import List

from dmx.Color import BLACK, Color

import sys
import os


parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/config"
sys.path.append(parent_dir)
import config


DMX_MAX_ADDRESS = 512
DMX_MIN_ADDRESS = 1

light_map = config.light_map

def light_id(adress):
    """ Get the light id from the config file.

    Args:
        adress (int): adress of the light

    Returns:
        int: id of the light in the config file
    """
    return light_map[adress]
    
def light_coord_to_id(x, y):
    """ Convert a coordinate to a light id, where (0, 0) is the top left corner.

    Args:
        x (int): column number 
        y (int): row number

    Returns:
        int: id of the light in the config file
    """
    return light_map[y + x * config.number_of_columns]

def light_id_to_coord(id):
    """ Convert a light id to a coordinate, where (0, 0) is the top left corner.

    Args:
        id (int): id of the light in the config file

    Returns:
        tuple: x, y coordinate of the light
    """
    return light_map.index(id) % config.number_of_columns, light_map.index(id) // config.number_of_columns

def distance_between_lights(id1, id2):
    """ Calculate the distance between two lights.

    Args:
        id1 (int): id of the first light
        id2 (int): id of the second light

    Returns:
        float: distance between the two lights
    """
    x1, y1 = light_id_to_coord(id1)
    x2, y2 = light_id_to_coord(id2)
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

class DMXLight(ABC):
    """Represents a DMX light."""

    def __init__(self, address: int = 1):
        """Initialise the light. The base initialiser simply stores the address."""
        self._address = int(max(0, min(address, DMX_MAX_ADDRESS)))

    @abstractmethod
    def serialise(self) -> List[int]:
        """Serialise the DMX light to a sequence of bytes."""

    @property
    def start_address(self):
        """Start address (inclusive) of the light.
        
        Returns:
            int: start address of the light
        """
        return self._address

    @property
    def end_address(self):
        """End address (inclusive) of the light.

        Returns:
            int: end address of the light
        """
        end_address = self._address + self.slot_count - 1
        if end_address > DMX_MAX_ADDRESS or end_address < DMX_MIN_ADDRESS:
            return (end_address % DMX_MAX_ADDRESS) + DMX_MIN_ADDRESS
        return end_address

    @property
    def slot_count(self) -> int:
        """Gets the number of slots used by this light."""
        return 0


class DMXLight4Slot(DMXLight):
    """Represents a DMX light with RGBW."""

    def __init__(self, address: int = 0):
        """Initialise the light."""
        super().__init__(address=address * 4)
        self._colour = BLACK

    @property
    def slot_count(self):
        """Gets the number of slots used by this light."""
        return 4

    def set_colour(self, color: Color):
        """Sets the color for the light."""
        self._colour = color

    def get_colour(self) -> Color:
        """Gets the color for the light."""
        return self._colour
    
    def serialise(self) -> List[int]:
        """Serialises the DMX light to a sequence of bytes."""
        return self._colour.serialise()
