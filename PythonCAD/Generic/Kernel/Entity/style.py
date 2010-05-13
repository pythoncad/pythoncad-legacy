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
# This class provide all the style operation for the pythoncadDB
#

from geometricalentity                  import GeometricalEntity
from util                               import getRandomString



class Style(GeometricalEntity):
        """
            This class rappresent the style in pythoncad
            objID is the object that rappresent the id in the db
        """
        def __init__(self, name=None):
            GeometricalEntity.__init__(self) 
            self.__styleProperty={}
            if name:
                self.__name=name
            else: #assing a default name (usefoul for list o tree name)
                self.name=getRandomString()       
            
        def setName(self, name):
            """
                set the name of the style
            """
            self.__name=name

        def getName(self):
            """
                get the style name
            """
            return self.__name
        
        name=property(setName, getName, None, "Style Name")
        
        def getStyleProp(self, name):
            """
                get the style property
            """
            if name in  self.__styleProperty:
                return  self.__styleProperty[name]
            else:
                return None
        
        def setStyleProp(self, name, value):
            """
                set the style property 
            """
            self.__styleProperty[name]=value
