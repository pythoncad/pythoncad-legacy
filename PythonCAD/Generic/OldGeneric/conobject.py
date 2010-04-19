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
# construction line/circle base class
#
# These variables provide the defaults for
# the construction line style attributes
#

from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import point

class ConstructionObject(graphicobject.GraphicObject):
    """A base class for construction lines and circles.

This class is meant to provide the most basic bits for
construction lines and circles. All construction lines
and circles will share a common Style object style, meaning
all instances will be drawn with the same linetype, have
the same color, and be the same thickness. Construction
entities should never be plotted out, however.
    """

    # static class variables

    __defstyle = None
    
    def __init__(self, **kw):
        super(ConstructionObject, self).__init__(ConstructionObject.__defstyle, **kw)

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Construction Object Style',
                             linetype.Linetype(u'Construction Line', [2,2]),
                             color.Color(255, 0, 0),
                             0.0)
            cls.__defstyle = _s
        return cls.__defstyle

    getDefaultStyle = classmethod(getDefaultStyle)

    def setDefaultStyle(cls, s):
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid style: " + `type(s)`
        cls.__defstyle = s

    setDefaultStyle = classmethod(setDefaultStyle)

    def finish(self):
        super(ConstructionObject, self).finish()

    def getStyle(self):
        return self.getDefaultStyle()
    
    def setStyle(self, s):
        pass

    def getColor(self):
        return self.getDefaultStyle().getColor()
    
    def setColor(self, c):
        pass

    def getLinetype(self):
        return self.getDefaultStyle().getLinetype()
    
    def setLinetype(self, l):
        pass

    def getThickness(self):
        return self.getDefaultStyle().getThickness()
    
    def setThickness(self, t):
        pass

#
# ConstructionObject history class
#

class ConstructionObjectLog(graphicobject.GraphicObjectLog):
    def __init__(self, obj):
        if not isinstance(obj, ConstructionObject):
            raise TypeError, "Invalid ConstructionObject: " + `obj`
        super(ConstructionObjectLog, self).__init__(obj)
