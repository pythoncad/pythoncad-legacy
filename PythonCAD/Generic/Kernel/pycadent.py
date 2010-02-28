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

from Entity.pycadstyle  import PyCadStyle
from Entity.pycadobject import PyCadObject

PY_CAD_ENT=['POINT','SEGMENT','SETTINGS','LAYER']

class PyCadEnt(PyCadObject):
    """
        basic PythonCad entity structure
    """
    def __init__(self,entType,constructionPoints,style,objId):
        PyCadObject.__init__(self,objId)
        if not entType in PY_CAD_ENT:
            raise TypeError,'entType not supported' 
        self.__entType=entType
        #if not (PyCadStyle is None or isinstance(style,PyCadStyle)):          
        #    raise TypeError,'style not supported' 
        self.__style=style        
        if not isinstance(constructionPoints,dict):
            raise TypeError,'type error in dictionary'
        self.__PointDic=constructionPoints
        isFirst=True
        #for p in constructionPoints:
        #    _x,_y=p.getCoords()
        #    if isFirst:
                #todo finire qui la creazione del bbox
        #        pass 
        self.__bBox=(0,0,0,0)               
        
    
    def getBBox(self):
        """
            get the bounding Box Of the entity
        """
        return self.__bBox
    
    def getConstructionElements(self):
        """
            return the base entity array
        """      
        return self.__PointDic
    
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


