"""Module for DMX universe."""

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

from typing import List, Set

from dmx.constants import DMX_MAX_ADDRESS, DMX_EMPTY_BYTE
from dmx.light import DMXLight

universe_map = []


class DMXUniverse:
    """Represents a DMX universe."""

    def __init__(self, universe_id: int = 1):
        """Initialises the DMX universe."""
        self._lights = set()  # type: Set[DMXLight]
        self._id = universe_id
        universe_map.append(self)

    def add_light(self, light: DMXLight):
        """Adds a light to the universe."""
        self._lights.add(light)

    def remove_light(self, light: DMXLight):
        """Removes a light from the universe."""
        self._lights.remove(light)

    def has_light(self, light: DMXLight) -> bool:
        """Checks if the universe has at least a light."""
        return light in self._lights

    def get_lights(self) -> Set[DMXLight]:
        """Gets all lights in this universe."""
        return self._lights

    def has_light_at_address(self, address: int) -> bool:
        """Check if a light is at a given address."""
        for light in self._lights:
            if light.start_address <= address*4 <= light.end_address:
                return True

        return False

    def get_light_at_address(self, address: int) -> DMXLight:
        for l in self._lights:
            if l.start_address <= address*4 <= l.end_address:
                return l
        raise ValueError("No light at address {}".format(address))

    def serialise(self):
        """Serialises the universe into a DMX frame. This is a list of 512 bytes, each representing a DMX address.

        Returns:
            List[int]: The DMX frame.
        """
        frame = [DMX_EMPTY_BYTE] * DMX_MAX_ADDRESS
        for u in universe_map:
            for light in u._lights:
                serialised_light = light.serialise()
                for address in range(light.start_address, light.end_address + 1): # TODO: Check this
                    frame[address] |= int(serialised_light[address - light.start_address])


        return frame
