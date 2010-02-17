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

from pycadstyle import PyCadStyle
from pycadobject import PyCadObject

PY_CAD_ENT=['POINT','SEGMENT']

class PyCadEnt(PyCadObject):
    """
        basic PythonCad entity structure
    """
    def __init__(self,entType,constructionPoints,style,objId):
        PyCadObject.__init__(self,objId)
        if not entType in PY_CAD_ENT:
            raise TypeError,'entType not supported' 
        self.__entType=entType
        #if not (PyCadStyle is None or isinstance(style,PyCadStyle) ):          
        #    raise TypeError,'style not supported' 
        self.__style=style        
        if not isinstance(constructionPoints,dict):
            raise TypeError,'type error in dictionary'
        self.__PointDic=constructionPoints

    def getConstructionPoint(self):
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


