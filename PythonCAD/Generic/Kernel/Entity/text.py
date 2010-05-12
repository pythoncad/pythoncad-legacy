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
# basic text functionality
#

from geometricalentity      import GeometricalEntity


from util import *

#
# Text
#
class Text(GeometricalEntity):
    """
        A class representing text in a drawing.
        A Text instance has the following attributes:
    """
    def __init__(self, p, text, angle=None,pointPosition=None):
        """
            Initialize a Text instance
        """
        from Generic.Kernel.initsetting             import TEXT_POSITION
        self.__angle =0
        if angle:
            self.__angle = angle
        self.__pointPosition='sw' #is the left down corner
        if pointPosition:
            if pointPosition in TEXT_POSITION:
                self.__pointPosition=pointPosition
        
        self.__location = p
        self.__text = text
        
    def __eq__(self, objTest):
        if isistance(objTest,Text):
            if(self.text== objTest.text and
                self.angle ==objTest.angle and
                self.location==objTest.location and
                self.pointPosition==objTest.pointPosition):
                return True
            else:
                return False
        else:
            raise TypeError,"obj must be of type Text"
        
    def getConstructionElements(self):
        """
            get the construction elements
        """
        return (self.__text, 
                self.__angle, 
                self.__location,
                self.__pointPosition)
        
    def getText(self):
        """
            Get the current text within the Text.
        """
        return self.__text

    def setText(self, text):
        """
            Set the text within the Text.
        """
        if not isinstance(text, str):
            raise TypeError, "Invalid text data: " + str(text)
        self.__text = text

    text = property(getText, setText, None, "Text text.")

    def getLocation(self):
        """
            Return the Text spatial position.
        """
        return self.__location


    def setLocation(self, x, y):
        """
            Store the spatial position of the Text.
        """
        _x = get_float(x)
        _y = get_float(y)
        self.__location = (_x, _y)

    location = property(getLocation, None, None, "Text location")

    def getAngle(self):
        """
            Return the angle at which the text is drawn.
        """
        return self.__angle

    def setAngle(self, angle=None):
        """
            Set the angle at which the text block should be drawn.
        """
        self.__angle= get_float(_angle)
    angle = property(getAngle, setAngle, None, "Text angle.")

    def getPointPosition(self):
        """
            return the position of the textrefered to the point 
        """
        return self.__pointPosition
    
    def setPointPosition(self, position):
        """
            set the position of the textrefered to the point 
        """
        from Generic.Kernel.initsetting             import TEXT_POSITION
        from Generic.Kernel.exception               import PythopnCadWarning
        if position in TEXT_POSITION:
            self.__pointPosition=position
        raise PythopnCadWarning,"bad Point position"    
    
    pointPosition=property(setPointPosition, getPointPosition, None, "Position of the text refered to the point")
    
    def getLineCount(self):
        """
            Return the number of lines of text in the Text
        """
        #
        # ideally Python itself would provide a linecount() method
        # so the temporary list would not need to be created ...
        #
        return len(self.__text.splitlines())

    def clone(self):
        """
            Return an identical copy of a Text.
        """
        _x, _y = self.getLocation().getCoords()
        _text = self.getText()
        _tb = Text(_x, _y, _text)
        _tb.angle = self.getAngle()
        _tb.pointPosition=self.pointPosition
        return _tb
   


