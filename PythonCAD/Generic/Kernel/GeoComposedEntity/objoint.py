#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# code for base composed object
#
from math import hypot, pi, sin, cos, tan, atan2

from Kernel.GeoEntity.geometricalentity    import *
from Kernel.GeoUtil.util                   import *
from Kernel.GeoUtil.intersection           import *
from Kernel.GeoEntity.segment              import Segment
#from Kernel.GeoEntity.acline               import ACLine
from Kernel.GeoEntity.arc                  import Arc
from Kernel.GeoEntity.ccircle              import CCircle
from Kernel.GeoUtil.geolib                 import Vector

_dtr = 180.0/pi

#ALLOW_CHAMFER_ENTITY=(Segment, ACLine)

class ObjectJoint(GeometricalEntityComposed):
    """
        A base class for chamfers and fillets
        A ObjectJoint object has the following methods:
    """
    def __init__(self, kw):
        from Kernel.initsetting import DRAWIN_ENTITY
        classNames=tuple(DRAWIN_ENTITY.keys())
        argDescription={"OBJECTJOINT_0":classNames, 
                        "OBJECTJOINT_1":classNames, 
                        "OBJECTJOINT_3":str, 
                        "OBJECTJOINT_4":(Point,None),  
                        "OBJECTJOINT_5":(Point,None)
                        }
        self.trimModeKey={"FIRST":0, "SECOND":1, "BOTH":2, "NO_TRIM":3}
        GeometricalEntityComposed.__init__(self, kw, argDescription)
        self._externalIntersectio=False
        spoolIntersection=[Point(x, y) for x, y in find_intersections(self.obj1, self.obj2)]
        if not spoolIntersection: #if not intesection is found extend it on cLine
            spoolIntersection=[Point(x, y) for x, y in find_segment_extended_intersection(self.obj1, self.obj2)]
            self._externalIntersectio=True
        self._intersectionPoints=spoolIntersection

    def setTrimMode(self, value):
        """
            Set The trim mode
        """    
        if value in self.trimModeKey:
            self["OBJECTJOINT_3"]=value
        else:
            raise AttributeError, "Bad trim mode use FIRST SECOND BOTH NO_TRIM" 
    def getTrimMode(self):
        """
            get the trim mode
        """
        return self["OBJECTJOINT_3"]
    
    trimMode=property(getTrimMode, setTrimMode, None, "Trim mode for the surce entity")
    
    def getObj1(self):    
        """
            get first object
        """
        return self["OBJECTJOINT_0"]

    def setObj1(self, value):
        """
            set the object 1
        """
        self["OBJECTJOINT_0"]=value
    
    obj1=property(getObj1, setObj1, None, "Set/Get  The first object")
    
    def getObj2(self):    
        """
            get first object
        """
        return self["OBJECTJOINT_1"]
    def setObj2(self, value):
        """
            set the object 1
        """
        self["OBJECTJOINT_1"]=value
   
    obj2=property(getObj2, setObj2, None, "Set/Get The Second object")   
    
    def getConstructionElements(self):
        """
            Return the two Entity Object joined by the ObjectJoint.
            This method returns a tuple holding the two Entity Object joined
            by the ObjectJoint.
        """
        return self
        
    def getIntersection(self):
        """
            Return the intersection points of the ObjectJoint Entity Object.

            This method returns an array of intersection point 
            [] no intersection
        """
        return self._intersectionPoints
    
    def getReletedComponent(self):
        """
            return the releted compont of the ObjectJoint
        """
        return self.getConstructionElements()
    def getPointClick1(self):
        """
            get the clicked point
        """
        return self["OBJECTJOINT_4"]
    def setPointClick1(self, value):
        """
            set the clicked point
        """
        self["OBJECTJOINT_4"]=value
    def getPointClick2(self):
        """
            get the clicked point
        """
        return self["OBJECTJOINT_5"]
    def setPointClick2(self, value):
        """
            set the clicked point
        """
        self["OBJECTJOINT_5"]=value
    pointClick1=property(getPointClick1, setPointClick1, None, "Set\Get the clicked point")
    pointClick2=property(getPointClick2, setPointClick2, None, "Set\Get the clicked point")


