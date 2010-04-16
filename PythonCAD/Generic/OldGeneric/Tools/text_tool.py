#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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
# tool stuff
#

import math
import types
import array

from PythonCAD.Generic import util
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic import tangent
from PythonCAD.Generic import intersections 
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import pyGeoLib 
from PythonCAD.Generic.snap import SnapPointStr

from PythonCAD.Generic import error
from PythonCAD.Generic.Tools.region_tool import RegionTool


class TextTool(RegionTool):
    """
        A specialized class for entering text.
        The TextTool class is derived from the Tool class, so it shares
        the attributes and methods of that class. The TextTool class also
        has the following additional methods:

        {set/get}Text(): Set/Get the text string in the tool.
        hasText(): Test if the tool has stored a text string
        {set/get}TextLocation(): Set/Get where the text is to be placed.
        {set/get}TextBlock(): Set/Get a TextBlock instance in the Tool
        {set/get}Bounds(): Set/Get the width and height of the text
        {set/get}PixelSize(): Set/Get the a rectangular region bounding the text.
        {set/get}Layout(): Set/Get the formatted text string display.
        {set/get/test}Attribute(): Set/Get/Test a TextBlock attribute
        {set/get}Value(): Set/Get the attribute value.
    """
    def __init__(self):
        super(TextTool, self).__init__()
        self.__text = None
        self.__location = None
        self.__tblock = None
        self.__attr = None
        self.__value = None
        self.__bounds = None
        self.__pixel_size = None
        self.__layout = None

    def setText(self, text):
        """
            Store some text in the tool.
            The argument 'text' should be a unicode object.
        """
        _text = text
        if not isinstance(_text, unicode):
            _text = unicode(text)
        self.__text = _text

    def getText(self):
        """
            Retrieve the stored text from the TextTool.
            If no text has been stored, this method raises a ValueError exception.
        """
        if self.__text is None:
            raise ValueError, "No text stored in TextTool."
        return self.__text

    def hasText(self):
        """
            Test if the tool has stored a text string.
        """
        return self.__text is not None

    def setTextLocation(self, x, y):
        """
            Store the location where the text will be placed.
            The arguments 'x' and 'y' should be float values.
        """
        _x, _y = util.make_coords(x, y)
        self.__location = (_x, _y)

    def getTextLocation(self):
        """
            Retrieve the location where the text will be placed.
            This method returns a tuple holding two floats:(x, y)
            A ValueError exception is raised if this method is called prior to
            setting the text location with setTextLocation().
        """
        if self.__location is None:
            raise ValueError, "No text location defined."
        return self.__location

    def testAttribute(self, attr):
        """
            Test that the given attribute is valid.
            Argument 'attr' should be one of the following: 'setAngle',
            'setAlignment', 'setFamily', 'setStyle', 'setWeight', 'setColor',
            or 'setSize'
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        return attr in ('setAngle', 'setAlignment', 'setFamily',
                        'setStyle', 'setWeight', 'setColor', 'setSize')

    def setAttribute(self, attr):
        """
            Define which attribute the tool is modifying.
            Argument 'attr' should be one of the following: 'setAngle',
            'setAlignment', 'setFamily', 'setStyle', 'setWeight', 'setColor',
            or 'setSize'
        """
        if not self.testAttribute(attr):
            raise ValueError, "Invalid attribute: " + attr
        self.__attr = attr

    def getAttribute(self):
        """
            Return the specified attribute.
            If called before invoking setAttribute(), this method raises a ValueError.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        return self.__attr

    def testValue(self, val):
        """
            Test that the given value is valid for the preset attribute.
            Argument 'val' depends on what attribute has been set with via setAttribute().
        """
        _a = self.__attr
        if _a == 'setAngle':
            _val = util.getFloat(val)
        elif _a == 'setAlignment':
            if not isinstance(val, int):
                raise TypeError, "Invalid alignment type: " + `type(val)`
            if (val != TextStyle.ALIGN_LEFT and
                val != TextStyle.ALIGN_CENTER and
                val != TextStyle.ALIGN_RIGHT):
                raise ValueError, "Invalid alignment value: %d" % val
            _val = val
        elif _a == 'setColor':
            if not isinstance(val, color.Color):
                raise TypeError, "Invalid Color: " + `type(val)`
            _val = val
        elif _a == 'setFamily':
            if not isinstance(val, types.StringTypes):
                raise TypeError, "Invalid family type: " + `type(val)`
            _val = val
        elif _a == 'setStyle':
            if not isinstance(val, int):
                raise TypeError, "Invalid style type: " + `type(val)`
            if (val != TextStyle.FONT_NORMAL and
                val != TextStyle.FONT_OBLIQUE and
                val != TextStyle.FONT_ITALIC):
                raise ValueError, "Invalid style value: %d" % val
            _val = val
        elif _a == 'setWeight':
            if not isinstance(val, int):
                raise TypeError, "Invalid weight type: " + `type(val)`
            if (val != TextStyle.WEIGHT_NORMAL and
                val != TextStyle.WEIGHT_LIGHT and
                val != TextStyle.WEIGHT_BOLD and
                val != TextStyle.WEIGHT_HEAVY):
                raise ValueError, "Invalid weight value: %d" % val
            _val = val
        elif _a == 'setSize':
            _val = util.get_float(val)
            if _val < 0.0:
                raise ValueError, "Invalid size: %g" % _val
        else:
            raise ValueError, "Unexpected attribute: " + _a
        return _val

    def setValue(self, val):
        """
            Store the new value of the entity attribute.
            Argument 'val' depends on the type of attribute defined for the
            tool. If no attribute is defined this method raises a ValueError.
            Invoking this method with 'None' as an argument sets the tool
            to restore the default attribute value.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        _val = None
        if val is not None:
            _val = self.testValue(val)
        self.__value = _val

    def getValue(self):
        """
            Get the stored attribute value.
            This method returns the value stored in setValue() or None.
        """
        return self.__value

    def getBounds(self):
        """
            Return the width and height of the TextBlock.       
        """
        if self.__bounds is None:
            raise ValueError, "TextBlock bounds not defined."
        return self.__bounds

    def setBounds(self, width, height):
        """
            Set the width and height of the TextBlock.
            Arguments 'width' and 'height' should be positive float values.
        """
        _w = util.get_float(width)
        if _w < 0.0:
            raise ValueError, "Invalid width: %g" % _w
        _h = util.get_float(height)
        if _h < 0.0:
            raise ValueError, "Invalid height: %g" % _h
        self.__bounds = (_w, _h)

    def setPixelSize(self, width, height):
        """
            Store a screen-size rectangular boundary for the text.
            Arguments 'width' and 'height' should be positive integer values.
            This method is somewhat GTK specific ...
        """
        _width = width
        if not isinstance(_width, int):
            _width = int(width)
        if _width < 0:
            raise ValueError, "Invalid width: %d" % _width
        _height = height
        if not isinstance(_height, int):
            _height = int(height)
        if _height < 0:
            raise ValueError, "Invalid height: %d" % _height
        self.__pixel_size = (_width, _height)

    def getPixelSize(self):
        """
            Retrieve the stored rectangular region of text.
            A ValueError exception is raised if this method is called before
            the size has been set by setPixelSize()
        """
        if self.__pixel_size is None:
            raise ValueError, "Pixel size is not defined."
        return self.__pixel_size

    def setLayout(self, layout):
        """
            Store a formatted layout string for the text.
            This method is very GTK/Pango specific ...
        """
        self.__layout = layout

    def getLayout(self):
        """
            Retrieve the formatted layout for the text string.
            This method is very GTK/Pango specific ...
        """
        return self.__layout

    def setTextBlock(self, tblock):
        """
            Store a TextBlock instance within the Tool.
            Argument 'tblock' must be a TextBlock.
        """
        if not isinstance(tblock, TextBlock):
            raise TypeError, "Invalid TextBlock: " + `type(tblock)`
        self.__tblock = tblock

    def getTextBlock(self):
        """
            Retrieve a stored TextBlock within the Tool.
            This method may return None if no TextBlock has been stored
            via setTextBlock().
        """
        return self.__tblock

    def create(self, image):
        """
            Create a new TextBlock and add it to the image.
            This method overrides the Tool::create() method.
        """
        _tb = self.__tblock
        if _tb is None:
            _text = self.getText()
            _x, _y = self.getTextLocation()
            _ts = image.getOption('TEXT_STYLE')
            _tb = TextBlock(_x, _y, _text, _ts)
            _f = image.getOption('FONT_FAMILY')
            if _f != _ts.getFamily():
                _tb.setFamily(_f)
            _s = image.getOption('FONT_STYLE')
            if _s != _ts.getStyle():
                _tb.setStyle(_s)
            _w = image.getOption('FONT_WEIGHT')
            if _w != _ts.getWeight():
                _tb.setWeight(_w)
            _c = image.getOption('FONT_COLOR')
            if _c != _ts.getColor():
                _tb.setColor(_c)
            _sz = image.getOption('TEXT_SIZE')
            if abs(_sz - _ts.getSize()) > 1e-10:
                _tb.setSize(_sz)
            _a = image.getOption('TEXT_ANGLE')
            if abs(_a - _ts.getAngle()) > 1e-10:
                _tb.setAngle(_a)
            _al = image.getOption('TEXT_ALIGNMENT')
            if _al != _ts.getAlignment():
                _tb.setAlignment(_al)
        image.addObject(_tb)
        self.reset()

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(TextTool, self).reset()
        self.__text = None
        self.__location = None
        self.__tblock = None
        self.__bounds = None
        self.__pixel_size = None
        self.__layout = None


