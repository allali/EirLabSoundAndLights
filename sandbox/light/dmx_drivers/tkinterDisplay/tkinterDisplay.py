"""A DMX driver design for the University of York Serial-to-DMX usb adapter based on the FT232R."""

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

from os import path
import sys
from typing import List

from pylibftdi import Device

from dmx.drivers import DMXDriver
currentDir = path.dirname(path.abspath(__file__))
sys.path.append(currentDir)
import tkinter_utils as tkutils

DRIVER_PATH = path.abspath(path.dirname(__file__))

class TkinterDisplayer(Device, DMXDriver):
    """A DMX driver design for the University of York Serial-to-DMX usb adapter based on the FT232R."""

    def __init__(self, device_index=0):
        """Initialise the driver."""
        self._opened = True
        self.tkDisplayer = tkutils.TkinterDisplayer()


    def write(self, data: List[int]):
        """Write 512 bytes or less of DMX data."""
        self.tkDisplayer.set_light_colors(data)
        self.tkDisplayer.update()
        if (self.tkDisplayer.exitProgram):
            exit(130)

    def _set_break_on(self):
        pass
        

    def _set_break_off(self):
        pass

    @staticmethod
    def get_driver_name() -> str:
        """Get driver name."""
        return "TkinterDisplayer"
    
    def close(self):
        """Close the driver."""
        self._opened = False
        self.tkDisplayer.close()


DRIVER_CLASS = TkinterDisplayer

__ALL__ = ["DRIVER_CLASS"]
