#
# Copyright (c) 2002, 2003, 2004, 2005 Art Haas
#
# This file is part of PythonCAD.
# 
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# PythonCAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# classes for colors
#

from PythonCAD.Generic import globals

#
# a seemingly good way to convert from string to integer
# for a couple of common ways of expressing colors ...
#

def color_str_to_int(cstr):
    if cstr.startswith('0x') or cstr.startswith('0X'):
        _val = int(cstr, 16)
    elif cstr.startswith('#'):
        _val = int(cstr[1:], 16)
    else:
        _val = int(cstr)
    return _val

class Color(object):
    """An object representing an RGB color.

The class purpose is self evident.

A Color object has three attributes:

r: Red (0-255)
g: Green (0-255)
b: Blue (0-255)

There is no alpha-channel attribute (yet)...

A Color object has the following methods:

getRed(): Get the Red value in the Color.
getBlue(): Get the Blue value in the Color.
getGreen(): Get the Green value in the Color.
clone(): Return an identical copy of a Color.

Once a color object is created, the values it
contains may not be changed.
    """
    def __init__(self, r=None, g=None, b=None):
        """Initialize a Color object.

There are several ways to create a color object:

Color(r,g,b) => r, g, and b values are all integers 0 <= value <= 255
Color(0xxxxx) => A hexidecimal value - it must begin with 0x. The color
                 is computed as follows:
                 r = (0xff0000 & value) >> 16
                 g = (0xff00 & value) >> 8
                 b = (0xff & value)
Color('#hexvalue') => A string prefixed with '#', with the remaining
                      characters representing a hexidecimal value.
Color() => A default color with r = g = b = 255.
        """
        _r = r
        _g = g
        _b = b
        if isinstance(_r, str):
            _val = color_str_to_int(_r)
            _r = (0xff0000 & _val) >> 16
            _g = (0xff00 & _val) >> 8
            _b = (0xff & _val)
        elif isinstance(_r, int) and _g is None and _b is None:
            _r = (0xff0000 & r) >> 16
            _g = (0xff00 & r) >> 8
            _b = (0xff & r)
        elif (isinstance(_r, int) and
              isinstance(_g, int) and
              isinstance(_b, int)):
            if _r < 0 or _r > 255:
                raise ValueError, "Invalid Red value: %d" % _r
            if _g < 0 or _g > 255:
                raise ValueError, "Invalid Green value: %d" % _g
            if _b < 0 or _b > 255:
                raise ValueError, "Invalid Blue value: %d" % _b
        elif _r is None and _g is None and _b is None:
            _r = 255
            _g = 255
            _b = 255
        else:
            raise SyntaxError, "Invalid call to Color()."
        self._color = (_r << 16) | (_g << 8) | _b

    def __eq__(self, obj):
        """Compare two Color objects for equivalence.
        """
        if not isinstance(obj, Color):
            return False
        return self.getColors() == obj.getColors()

    def __ne__(self, obj):
        """Compare two Color objects for equivalence.
        """
        if not isinstance(obj, Color):
            return True
        return self.getColors() != obj.getColors()
    
    def __cmp__(self, obj):
        """Compare two Color objects.

The comparison is done based on the RGB values.

red value of C1 < red value of C2 ==> return -1
red value of C1 > red value of C2 ==> return 1

Then green values are compared, then blue. If
all values are equal, return 0.
        """
        if not isinstance(obj, Color):
            raise TypeError, "Invalid object for color comparison: " + `obj`
        _val = self._color
        _objval = hash(obj)
        return cmp(_val, _objval)

    def __hash__(self):
        """Return a hash value for the Color object.

Providing this method means that Color objects can be used
as keys in dictionaries.
        """
        return self._color
        
    def __repr__(self):
        _val = self._color
        _r = (_val & 0xff0000) >> 16
        _g = (_val & 0xff00) >> 8
        _b = (_val & 0xff)
        return "Color(%d,%d,%d)" % (_r, _g, _b)
    
    def __str__(self):
        return "#%06x" % self._color

    def getColors(self):
        """Return a three-item tuple with the values comprising this color.

getColors()        
        """
        _val = self._color
        _r = (_val & 0xff0000) >> 16
        _g = (_val & 0xff00) >> 8
        _b = (_val & 0xff)
        return _r, _g, _b

    def getRed(self):
        """Return the red value of the color.

getRed()        
        """
        return (self._color & 0xff0000) >> 16

    r = property(getRed, None, None, "Red value of the color.")

    def getGreen(self):
        """Return the green value of the color.

getGreen()        
        """
        return (self._color & 0xff00) >> 8

    g = property(getGreen, None, None, "Green value of the color.")

    def getBlue(self):
        """Return the blue value of the color.

getBlue()        
        """
        return (self._color & 0xff)

    b = property(getBlue, None, None, "Blue value of the color.")

    def clone(self):
        """Return a new Color object with the same color values.

clone()
        """
        _val = self._color
        return Color(_val)

#
# ColorDict Class
#
# The ColorDict is built from the dict object. Using instances
# of this class will guarantee than only Color objects will be
# stored in the instance
#

class ColorDict(dict):
    def __init__(self):
        super(ColorDict, self).__init__()
        
    def __setitem__(self, key, value):
        if not isinstance(key, Color):
            raise TypeError, "ColorDict keys must be color objects: " + `key`
        if not isinstance(value, Color):
            raise TypeError, "ColorDict values must be Color objects: " + `value`
        super(ColorDict, self).__setitem__(key, value)

#
# find a Color object stored in the global color dictionary
# or make a new one and store it
#

def get_color(r, g, b):
    if not isinstance(r, int):
        raise TypeError, "Invalid red value:" + `r`
    if r < 0 or r > 255:
        raise ValueError, "Invalid red value: %d" % r
    if not isinstance(g, int):
        raise TypeError, "Invalid green value:" + `g`
    if g < 0 or g > 255:
        raise ValueError, "Invalid green value: %d" % g
    if not isinstance(b, int):
        raise TypeError, "Invalid blue value:" + `b`
    if b < 0 or b > 255:
        raise ValueError, "Invalid blue value: %d" % b
    _color = Color(r, g, b)
    if _color in globals.colors:
        _color = globals.colors[_color]
    else:
        globals.colors[_color] = _color
    return _color
