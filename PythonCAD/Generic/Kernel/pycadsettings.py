#!/usr/bin/env python
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
# This module provide all the basic operation for the pythoncad settings
#

class PyCadSettings(object):
    """
        this class provide access at all the pythoncad settings
    """
    def __init__(self,name):
        """
            the name of the settings schema
        """
        self.__name=name
        self.__activeLayer="ROOT"
        
    def getName(self):
        """
            get the settings Name
        """
        return self.__name
    def setName(self,name):
        """
            set the settings name
        """
        self.__name=name
    name=property(getName,setName,None,"get/set the name of the settings")
    
    def getActiveLayer(self):
        """
            get the anctive layer of the settings
        """
        return self.__activeLayer
    
    def setActiveLayer(self,lName):
        """
            set the active layer id
        """
        self.__activeLayer=lName
        
    layerName=property(getActiveLayer,setActiveLayer,None,"get/set the active layer name")
    