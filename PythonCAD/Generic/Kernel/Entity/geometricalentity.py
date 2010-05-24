#
# Copyright (c) 2010 Matteo Boscolo
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
# This is the base class for all the geometrical entitys
#
import math


class GeometricalEntity(dict):
    """
        This class provide the basic interface for all the geometrical entitys
    """
    def __init__(self, kw, argNameType):
        """
            argv name must be created befor init the base class
        """
        if kw is None and argNameType is none:
            return
        if len(kw)!=len(argNameType):
            raise TypeError, "Wrong number of items "
        for k in kw:
            if k in argNameType:
                if isinstance(kw[k],argNameType[k]):
                    self[k]=kw[k]
                else:
                    raise TypeError, "Wrong Type for argument %s"%str(k)
            else:
                raise TypeError, "Wrong argument %s "%str(k)
        self.arguments=argNameType
    
    def getArgumentsName(self):
        """
            get the construction arguments Name
        """
        return self.arguments
    
    def getConstructionElements(self):
        """
            Get the construction element of entity..
        """
        return self
        
    def setConstructionElements(self, **kw):
        """
            set the construction elemtnts
        """
        self=kw
        
    def move(self, fromPoint, toPoint):
        """
            this method must be defined for moving operation
        """
        from pygeolib import Vector
        from point import Point
        v=Vector(fromPoint, toPoint)
        for key in self:
            if isinstance(self[key] , Point):
                self[key]+=v.point()
        return v.point()
    
    def rotate(self, rotationPoint, angle):
        """
            this method must be defined for rotation
        """
        x, y=rotationPoint.getCoords()
        x1=x*math.cos(angle)-y*math.sin(angle)
        y1=x*math.sin(angle)+y*math.cos(angle)
        return Point(x1, y1)
        
    
class GeometricalEntityComposed(dict):
    """
        this class provide the basic object for composed entity 
        like dimension labels ...
    """
    def __init__(self, kw, argNameType):
        if kw is None and argNameType is none:
            return
        if len(kw)!=len(argNameType):
            raise TypeError, "Wrong number of items "
        for k in kw:
            if k in argNameType:
                if isinstance(kw[k],argNameType[k]):
                    self[k]=kw[k]
                else:
                    raise TypeError, "Wrong Type for argument %s"%str(k)
            else:
                raise TypeError, "Wrong argument %s "%str(k)
        self.arguments=argNameType
    
    def getArgumentsName(self):
        """
            get the construction arguments Name
        """
        return self.arguments
    def getConstructionElements(self):
        """
            Get the construction element of ..
            This must return a tuple of object better if there are point
        """
        pass
    def getReletedComponent(self):
        """
            Get The releted object to be updated
        """
        pass
