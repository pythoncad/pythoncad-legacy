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
            from Generic.Kernel.initsetting         import PYTHONCAD_COLOR, PYTHONCAD_LINETYPE
            self.__colorArray=PYTHONCAD_COLOR
            self.__lineType=PYTHONCAD_LINETYPE
            GeometricalEntity.__init__(self)  
            self.__color=PYTHONCAD_COLOR['black']
            self.__LineType=PYTHONCAD_LINETYPE['continue']
            if name:
                self.__name=name
            else: #assing a default name (usefoul for list o tree name)
                self.name=getRandomString()
        
        def getConstructionElements(self):        
            """
                get the construction elements of the style
            """
            #the style entity retun the self istance
            return (self, )
            
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
        
        name=property(setName, getName, None, "Style Name ")
        
        def setColor(self, colorName):
            """
                set style color
            """
            if colorName in self.__colorArray:
                self.color=self.__colorArray[colorName]
            else:
                raise StyleUndefinedAttribute, "Color not in the dictionary PYTHONCAD_COLOR"
            
        def getColor(self):
            """
                get the color
            """
            return self.color
        
        color=property(getColor, setColor, None,"Style Color")
        
        def setLineType(self, lineTypeName):
            """
                this class rappresent the line type
            """
            if lineTypeName in self.__lineType:
                self.__lineType=self.__lineType[lineTypeName]
            else:
                raise StyleUndefinedAttribute, "Line type not in the dictionary PYTHONCAD_LINETYPE"
                
        def getLineType(self):
            """
                get the lineType
            """
            return self.__lineType
        lineType=property(setLineType, getLineType, None, "Style lineType ")
        
