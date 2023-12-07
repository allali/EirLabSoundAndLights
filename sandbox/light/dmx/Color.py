"""Module for DMX color."""

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

from typing import Union


class Color:
    """Represents a color in 24 bit RGB."""

    def __init__(self, red: int, green: int, blue: int, white: int = 0):
        """Initialise the color."""
        self._red = red
        self._green = green
        self._blue = blue
        self._white = white

    def serialise(self):
        """Serialise the color into a list of 4 integers corresponding to the RGBW values.

        Returns:
            List[int]: The serialised color.
        """
        return [self._red, self._green, self._blue, self._white]

    @property
    def red(self) -> int:
        """Get red component."""
        return self._red

    @red.setter
    def red(self, value: int):
        """Set red component."""
        self._red = int(max(0, min(value, 255)))

    @property
    def green(self) -> int:
        """Get green component."""
        return self._green

    @green.setter
    def green(self, value: int):
        """Set green component."""
        self._green = int(max(0, min(value, 255)))

    @property
    def blue(self) -> int:
        """Get blue component."""
        return self._red

    @blue.setter
    def blue(self, value: int):
        """Set blue component."""
        self._blue = int(max(0, min(value, 255)))

    @property
    def white(self) -> int:
        """Get white component."""
        return self._white

    @white.setter
    def white(self, value: int):
        """Set white component."""
        self._white = int(max(0, min(value, 255)))

    def __add__(self, other: Union['Color', int, float]):
        """Handle addition of colors.

        Args:
            other (Union[Color, int, float]): The color to add to this one.
        """
        if isinstance(other, Color):
            self.red += other.red
            self.green += other.green
            self.blue += other.blue
            self.white += other.white
        elif isinstance(other, (int, float)):
            self.red = int(self.red + other)
            self.green = int(self.green + other)
            self.blue = int(self.blue + other)
            self.white = int(self.white + other)

    def __sub__(self, other: Union['Color', int, float]):
        """Handle subtraction of colors.

        Args:
            other (Union[Color, int, float]): The color to subtract by
        """
        if isinstance(other, Color):
            self.red -= other.red
            self.green -= other.green
            self.blue -= other.blue
            self.white -= other.white
        elif isinstance(other, (int, float)):
            self.red = int(self.red - other)
            self.green = int(self.green - other)
            self.blue = int(self.blue - other)
            self.white = int(self.white - other)

    def __mul__(self, other: Union['Color', int, float]):
        """Handle multiplication of colors.

        Args:
            other (Union[Color, int, float]): The color to multiply by.
        """
        if isinstance(other, Color):
            self.red *= other.red
            self.green *= other.green
            self.blue *= other.blue
            self.white *= other.white
        elif isinstance(other, (int, float)):
            self.red = int(self.red * other)
            self.green = int(self.green * other)
            self.blue = int(self.blue * other)
            self.white = int(self.white * other)

    def __truediv__(self, other: Union['Color', int, float]):
        """Handle true division of colors.

        Args:
            other (Union[Color, int, float]): The color to divide by.
        """
        if isinstance(other, Color):
            self.red = int(self.red / other.red)
            self.green = int(self.green / other.green)
            self.blue = int(self.blue / other.blue)
            self.white = int(self.white / other.white)
        elif isinstance(other, (int, float)):
            self.red = int(self.red / other)
            self.green = int(self.green / other)
            self.blue = int(self.blue / other)
            self.white = int(self.white / other)

    def __floordiv__(self, other: Union['Color', int, float]):
        """ Handle floor division of colors.

        Args:
            other (Union[Color, int, float]): The color to divide by.
        """
        if isinstance(other, Color):
            self.red //= other.red
            self.green //= other.green
            self.blue //= other.blue
            self.white //= other.white
        elif isinstance(other, (int, float)):
            self.red = int(self.red // other)
            self.green = int(self.green // other)
            self.blue = int(self.blue // other)
            self.white = int(self.white // other)


RED = Color(255, 0, 0, 10)
GREEN = Color(0, 255, 0, 10)
BLUE = Color(0, 0, 255, 10)
WHITE = Color(255, 255, 255, 255)
BLACK = Color(0, 0, 0, 10)
