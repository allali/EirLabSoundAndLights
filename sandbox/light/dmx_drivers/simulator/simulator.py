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
from platform import system
from typing import List

from pylibftdi import Device, Driver, LibraryMissingError

from dmx.drivers import DMXDriver
import socketio
import eventlet

DRIVER_PATH = path.abspath(path.dirname(__file__))

if system() == "Linux":

    from ctypes import cdll, c_long, byref, Structure

    Driver._lib_search["libftdi"] = tuple([
        path.join(DRIVER_PATH, "libftdi.so"),
        path.join(DRIVER_PATH, "libftdi.so.1"),
        path.join(DRIVER_PATH, "libftdi1.so")
    ] + list(Driver._lib_search["libftdi"]))

    _LIBC = cdll.LoadLibrary("libc.so.6")

    class timespec(Structure):
        """A timespec."""

        _fields_ = [("tv_sec", c_long), ("tv_nsec", c_long)]

    def wait_ms(milliseconds):
        """Wait for a specified number of milliseconds."""
        dummy = timespec()
        sleeper = timespec()
        sleeper.tv_sec = int(milliseconds / 1000)
        sleeper.tv_nsec = (milliseconds % 1000) * 1000000
        _LIBC.nanosleep(byref(sleeper), byref(dummy))

    def wait_us(nanoseconds):
        """Wait for a specified number of nanoseconds."""
        dummy = timespec()
        sleeper = timespec()
        sleeper.tv_sec = int(nanoseconds / 1000000)
        sleeper.tv_nsec = (nanoseconds % 1000) * 1000
        _LIBC.nanosleep(byref(sleeper), byref(dummy))

elif system() == "Windows":

    from ctypes import wintypes, windll, byref

    _WIN32 = windll.kernel32
    _MS = 1000000
    _INFINITE = 0xFFFFFFFF

    def wait_ms(milliseconds):
        """Wait for a specified number of milliseconds."""
        wait_time = wintypes.LARGE_INTEGER(-(_MS * abs(milliseconds)))
        timer_handle = _WIN32.CreateWaitableTimerW(None, True, None)
        if timer_handle == 0:
            raise Exception("CreateWaitableTimerW returned NULL")
        if _WIN32.SetWaitableTimer(timer_handle, byref(wait_time), 0, None, None, False) == 0:
            raise Exception("SetWaitableTimer returned 0")
        _WIN32.WaitForSingleObject(timer_handle, _INFINITE)
        _WIN32.CloseHandle(timer_handle)

    def wait_us(nanoseconds):
        """Wait for a specified number of nanoseconds."""
        wait_time = wintypes.LARGE_INTEGER(-abs(nanoseconds))
        timer_handle = _WIN32.CreateWaitableTimerW(None, True, None)
        if timer_handle == 0:
            raise Exception("CreateWaitableTimerW returned NULL")
        if _WIN32.SetWaitableTimer(timer_handle, byref(wait_time), 0, None, None, False) == 0:
            raise Exception("SetWaitableTimer returned 0")
        _WIN32.WaitForSingleObject(timer_handle, _INFINITE)
        _WIN32.CloseHandle(timer_handle)


class SIMULATOR(DMXDriver):
    """A DMX driver design for the University of York Serial-to-DMX usb adapter based on the FT232R."""

    _BITS_8 = 8
    _STOP_BITS_2 = 2
    _PARITY_NONE = 0
    _BREAK_OFF = 0
    _BREAK_ON = 1

    _client = None

    def __init__(self, device_index=0):
        """Initialise the driver."""
        print("[*] Initialising DMX Simulator")

        self._opened = False

    def write(self, data: List[int]):
        """Write 512 bytes or less of DMX data."""
        try:
            byte_data = bytes(data)
        except TypeError:
            byte_data = self.encoder.encode(data)

        wait_ms(10)
        wait_us(8)
        # Frame body
        # Device.write(self, b"\x00" + byte_data)
        self._client.emit('light_frame', byte_data)
        wait_ms(15)

    def _set_break_on(self):
        pass

    def _set_break_off(self):
        pass

    @staticmethod
    def get_driver_name() -> str:
        """Get driver name."""
        return "SIMULATOR"

    def close(self):
        """Close the driver."""
        self._opened = False

    def open(self):
        """Open the driver."""
        self._client = socketio.Client()
        print("[*] SocketIO Client Started")

        @self._client.event
        def connect():
            print("[*] SocketIO Client Connected")
            self._opened = True

        @self._client.event
        def disconnect():
            print("[*] SocketIO Client Disconnected")
            self._opened = False

        @self._client.event
        def message(data):
            print("[*] SocketIO Client Message: " + data)

        self._client.connect('http://localhost:5000', wait_timeout=10)

    @property
    def closed(self):
        """Check if the driver is closed."""
        return not self._opened


DRIVER_CLASS = SIMULATOR

__ALL__ = ["DRIVER_CLASS"]
