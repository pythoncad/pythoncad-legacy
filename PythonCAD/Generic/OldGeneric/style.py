#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# classes for styles
#

import types

from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import util

class Style(object):
    """A class storing a particular of Linetype, Color, and Thickness.

A Style consists of four attributes:

name: The Style name
linetype: A Linetype object
color: A Color object
thickness: A positive float value giving the line thickness

A Style has the following methods:

getName(): Get the Style name.
getColor(): Get the Style color.
getLinetype(): Get the Style Linetype.
getThickness(): Get the Style line thickness.
clone(): Return an identical copy of the Style.

Once a Style is created, the values in that object cannot
be changed.
    """

    __defcolor = color.Color(0xffffff)
    
    def __init__(self, name, lt=None, col=None, t=None):
        """Instatiate a Style object.

Style(name [, lt, col, t])

name: A string giving the style a name

Option arguments:
lt: A Linetype object - defaults to a solid line Linetype
col: A Color object - defaults to the default Color object
t: A positive float value - defaults to 1.0
        """
        if not isinstance(name, types.StringTypes):
            raise TypeError, "Invalid Style name: " + `name`
        _n = name
        if not isinstance(_n, unicode):
            _n = unicode(name)
        _lt = lt
        if _lt is None:
            _lt = linetype.Linetype('Default_Solid', None)
        if not isinstance(_lt, linetype.Linetype):
            raise TypeError, "Invalid linetype: " + `_lt`
        _c = col
        if _c is None:
            _c = Style.__defcolor
        if not isinstance(_c, color.Color):
            _c = color.Color(color)
        _t = t
        if _t is None:
            _t = 1.0
        _t = util.get_float(_t)
        if _t < 0.0:
            raise ValueError, "Invalid line thickness: %g" % _t
        self.__name = _n
        self.__linetype = _lt
        self._color = _c
        self.__thickness = _t

    def __eq__(self, obj):
        """Compare a Style object to another Style for equality.

Comparing two styles is really comparing that the linetypes
are the same, then the colors are the same, and that the
line thickness are the same (within a tiny tolerance). If all
three are the same, the comparison returns True. Otherwise, the
comparison returns False.
        """
        if not isinstance(obj, Style):
            return False
        if obj is self:
            return True
        return (self.__name == obj.getName() and
                self.__linetype == obj.getLinetype() and
                self._color == obj.getColor() and
                abs(self.__thickness - obj.getThickness()) < 1e-10)

    def __ne__(self, obj):
        """Compare a Style object to another Style for non-equality.

Comparing two styles is really comparing that the linetypes
are the same, then the colors are the same, and that the
line thickness are the same (within a tiny tolerance). If all
three are the same, the comparison returns False. Otherwise, the
comparison returns True.
        """
        return not self == obj

    def __hash__(self):
        """Return a hash value for the Style.

Defining this method allows Styles to be stored in dictionaries.
        """
        _val = hash(self._color)
        _val = _val ^ hash(self.__linetype)
        _val = _val ^ hash(long(self.__thickness * 1e10))
        return _val

    def getName(self):
        """Return the name of the Style.

getName()        
        """
        return self.__name

    name = property(getName, None, None, "Style name.")
    
    def getLinetype(self):
        """Return the Linetype used by this Style.

getLinetype()        
        """
        return self.__linetype

    linetype = property(getLinetype, None, None, "Style Linetype")

    def getColor(self):
        """Return the Color used by this Style.

getColor()
        """
        return self._color

    color = property(getColor, None, None, "Style Color")
    
    def getThickness(self):
        """Return the line thickness used by this style.

getThickness()        
        """
        return self.__thickness

    thickness = property(getThickness, None, None, "Style Thickness.")

    def getStyleValues(self):
        _n = self.__name
        _l = self.__linetype.getName(), self.__linetype.getList()
        _c = self._color.getColors()
        _t = self.thickness
        return _n, _l, _c, _t
    
    def clone(self):
        """Return an identical copy of a Style.

clone()
        """
        _name = self.__name[:]
        _linetype = self.__linetype.clone()
        _color = self._color.clone()
        _thickness = self.__thickness
        return Style(_name, _linetype, _color, _thickness)
#
# StyleDict Class
#
# The StyleDict is built from the dict object. Using instances
# of this class will guarantee than only Style objects will be
# stored in the instance
#

class StyleDict(dict):
    def __init__(self):
        super(StyleDict, self).__init__()
        
    def __setitem__(self, key, value):
        if not isinstance(key, Style):
            raise TypeError, "StyleDict keys must be Style objects: " + `key`
        if not isinstance(value, Style):
            raise TypeError, "StyleDict values must be Style objects: " + `value`
        super(StyleDict, self).__setitem__(key, value)
