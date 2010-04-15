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
# This module provide basic DB class for storing entity in pythoncad
#

from Generic.Kernel.Entity.style            import Style
from Generic.Kernel.Entity.pycadobject      import PyCadObject
from Generic.Kernel.Entity.point            import Point

PY_CAD_ENT=['POINT','SEGMENT','SETTINGS','LAYER','ARC', 'ELLIPSE']

class Entity(PyCadObject):
    """
        basic PythonCad entity structure
    """
    def __init__(self,entType,constructionElements,style,objId):
        PyCadObject.__init__(self,objId)
        if not entType in PY_CAD_ENT:
            raise TypeError,'entType not supported'
        self.__entType=entType
        #if not (PyCadStyle is None or isinstance(style,PyCadStyle)):
        #    raise TypeError,'style not supported'
        self.__style=style
        if not isinstance(constructionElements,dict):
            raise TypeError,'type error in dictionary'
        self.setConstructionElement(constructionElements)

    def getBBox(self):
        """
            get the bounding Box Of the entity
        """
        return self.__bBox

    def updateBBox(self):
        """
            update the bounding box from the construction elements
        """
        # Todo : Find a better way to create the bounding box for all
        # the geometrical entity may be is better that all the geometrical
        # entity have an implementatio of the bounding box
        _xList=[]
        _yList=[]
        for key in self._constructionElements:
            if isinstance(self._constructionElements[key],Point):
                x,y=self._constructionElements[key].getCoords()
                _xList.append(x)
                _yList.append(y)
        _xList.sort()
        _yList.sort()
        if len(_xList)>0:
            if len(_xList)==1:
                _yList=_xList
            self.__bBox=(_xList[0],_yList[0],_xList[-1],_yList[-1])
        else:
            self.__bBox=(0,0,0,0)

    def getConstructionElements(self):
        """
            return the base entity array
        """
        return self._constructionElements

    def setConstructionElement(self, constructionElements):
        """
            set the construction elements for the object
        """
        self._constructionElements=constructionElements
        self.updateBBox()

    def getEntityType(self):
        """
            Get the entity type
        """
        return self.__entType

    eType=property(getEntityType,None,None,"Get the etity type read only attributes")

    def getStyle(self):
        """
            get the object style
        """
        return self.__style

    def setStyle(self,style):
        """
            set/update the entity style
        """
        #if not isinstance(style,PyCadStyle):
        #    raise TypeError,'Type error in style'
        self.__style=style

    style=property(getStyle,setStyle,None,"Get/Set the entity style")


