#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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

import math
import types

from PythonCAD.Generic import color
from PythonCAD.Generic import entity
from PythonCAD.Generic import util

def font_style_string(style):
    """Return a text string for the font style.

font_style_string(style)
    """
    if style == TextStyle.FONT_NORMAL:
        _str = 'normal'
    elif style == TextStyle.FONT_OBLIQUE:
        _str = 'oblique'
    elif style == TextStyle.FONT_ITALIC:
        _str = 'italic'
    else:
        raise ValueError, "Unknown font style: " + str(style)
    return _str

def font_weight_string(weight):
    """Return a text string for the font weight.

font_weight_string(weight)
    """
    if weight == TextStyle.WEIGHT_NORMAL:
        _str = 'normal'
    elif weight == TextStyle.WEIGHT_LIGHT:
        _str = 'light'
    elif weight == TextStyle.WEIGHT_BOLD:
        _str = 'bold'
    elif weight == TextStyle.WEIGHT_HEAVY:
        _str = 'heavy'
    else:
        raise ValueError, "Unknown font weight: " + str(weight)
    return _str

#
# the font_prop_map and parse_font() should be moved as
# they are GTK specific ...
#

font_prop_map = {
    'Oblique' : 'style',
    'Italic' : 'style',
    'Ultra-Light' : 'weight',
    'Light' : 'weight',
    'Medium' : 'weight',
    'Semi-Bold' : 'weight',
    'Bold' : 'weight',
    'Ultra-Bold' : 'weight',
    'Heavy' : 'weight',
    'Ultra-Condensed' : 'stretch',
    'Extra-Condensed' : 'stretch',
    'Condensed' : 'stretch',
    'Semi-Condensed' : 'stretch',
    'Semi-Expanded' : 'stretch',
    'Expanded' : 'stretch',
    'Extra-Expanded' : 'stretch',
    'Ultra-Expanded' : 'stretch',
    }

def parse_font(fontstr):
    _size = 12
    _weight = 0 # NORMAL
    _style = 0 # NORMAL
    _stretch = 0# NORMAL
    _family = 'Sans'
    if fontstr != '':
        _fontlist = fontstr.split()
        _fontlist.reverse()
        if _fontlist[0].isdigit():
            _sz = _fontlist.pop(0)
            _size = int(_sz)
        while (_fontlist[0] in font_prop_map):
            _prop = _fontlist.pop(0)
            _item = font_prop_map[_prop]
            # print "prop: " + _prop
            # print "item: " + _item
            if _item == 'style':
                if _prop == 'Oblique':
                    _style = 1
                elif _prop == 'Italic':
                    _style = 2
                else:
                    _style = 0 # NORMAL # default
            elif _item == 'weight':
                if (_prop == 'Ultra-Light' or
                    _prop == 'Light' or
                    _prop == 'Medium'):
                    _weight = 1
                elif (_prop == 'Semi-Bold' or
                      _prop == 'Bold'):
                    _weight = 2
                elif (_prop == 'Ultra-Bold' or
                      _prop == 'Heavy'):
                    _weight = 3
                else:
                    _weight = 0 # NORMAL
            elif _item == 'stretch':
                _stretch = _prop # fixme - add stretching bits
            else:
                raise ValueError, "Unknown font property: " + _item
        _fontlist.reverse()
        if len(_fontlist):
            _family = ' '.join(_fontlist)
    return (_family, _style, _weight, _stretch, _size)

#
# Style class for a text block
#

class TextStyle(object):
    """A class for describing text properties.

A TextStyle object has the following attributes:

family: The font family
style: The font style
weight: The font weight
color: The font color
alignment: Text positioning relative to the location
angle: Angular position of the text

A TextStyle object has the following methods:

getFamily(): Get the font family.
getStyle(): Get the font style.
getWeight(): Get the font weight.
getColor(): Get the font color.
getSize(): Get the text size.
getAngle(): Get the text angle
getAlignment(): Get the text positioning.

The TextStyle class has the following classmethods:

getStyleAsString(): Get the font style in string form.
getStyleFromString(): Get the font style value given a string argument
getWeightAsString(): Get the font weight in string form.
getWeightFromString(): Get the font weight value given a string argument
getAlignmentAsString(): Get the text positioning in string form.
getAlignmentFromString(): Get the text positioning value given a string.
getStyleStrings(): Get the available font style values as strings.
getStyleValues(): Get the available font style values.
getWeightStrings(): Get the available font weight values as strings.
getWeightValues(): Get the available font weight values.
getAlignmentStrings(): Get the available text alignment values as strings.
getAlignmentValues(): Get the available text alignment values.
    """

    FONT_NORMAL = 0
    FONT_OBLIQUE = 1
    FONT_ITALIC = 2

    WEIGHT_NORMAL = 0
    WEIGHT_LIGHT = 1
    WEIGHT_BOLD = 2
    WEIGHT_HEAVY = 3

    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    __defcolor = color.Color(0xffffff)

    def __init__(self, name, **kw):
        """Initialize a TextStyle object.

ts = TextStyle(name)

The following are the defaults:

family: Sans
style: NORMAL
weight: NORMAL
color: White (#ffffff)
size: 1.0
angle: 0.0
alignment: LEFT
        """
        _name = name
        if not isinstance(_name, unicode):
            _name = unicode(name)
        _family = 'Sans'
        if 'family' in kw:
            _family = kw['family']
            if not isinstance(_family, str):
                raise TypeError, "Invalid font family: " + str(_family)
        _style = TextStyle.FONT_NORMAL
        if 'style' in kw:
            _style = kw['style']
            if not isinstance(_style, int):
                raise TypeError, "Invalid font style: " + str(_style)
            if (_style != TextStyle.FONT_NORMAL and
                _style != TextStyle.FONT_OBLIQUE and
                _style != TextStyle.FONT_ITALIC):
                raise ValueError, "Invalid font style value: %d" % _style
        _weight = TextStyle.WEIGHT_NORMAL
        if 'weight' in kw:
            _weight = kw['weight']
            if not isinstance(_weight, int):
                raise TypeError, "Invalid font weight: " + str(_weight)
            if (_weight != TextStyle.WEIGHT_NORMAL and
                _weight != TextStyle.WEIGHT_LIGHT and
                _weight != TextStyle.WEIGHT_BOLD and
                _weight != TextStyle.WEIGHT_HEAVY):
                raise ValueError, "Invalid font weight value: %d" % _weight
        _color = TextStyle.__defcolor
        if 'color' in kw:
            _color = kw['color']
            if not isinstance(_color, color.Color):
                raise TypeError, "Invalid color: " + str(_color)
        _size = 1.0
        if 'size' in kw:
            _size = util.get_float(kw['size'])
            if _size < 0.0:
                raise ValueError, "Invalid text size: %g" % _size
        _angle = 0.0
        if 'angle' in kw:
            _angle = util.get_float(kw['angle'])
            if _angle > 360.0 or _angle < -360.0:
                _angle = math.fmod(_angle, 360.0)
        _align = TextStyle.ALIGN_LEFT
        if 'align' in kw:
            _align = kw['align']
            if not isinstance(_align, int):
                raise TypeError, "Invalid text alignment: " + str(_align)
            if (_align != TextStyle.ALIGN_LEFT and
                _align != TextStyle.ALIGN_CENTER and
                _align != TextStyle.ALIGN_RIGHT):
                raise ValueError, "Invalid text alignment value: %d" % _align
        super(TextStyle, self).__init__()
        self.__name = _name
        self.__family = _family
        self.__style = _style
        self.__weight = _weight
        self.__color = _color
        self.__size = _size
        self.__angle = _angle
        self.__alignment = _align

    def __eq__(self, obj):
        if not isinstance(obj, TextStyle):
            return False
        if obj is self:
            return True
        return (self.__name == obj.getName() and
                self.__family == obj.getFamily() and
                self.__style == obj.getStyle() and
                self.__weight == obj.getWeight() and
                self.__color == obj.getColor() and
                abs(self.__size - obj.getSize()) < 1e-10 and
                abs(self.__angle - obj.getAngle()) < 1e-10 and
                self.__alignment == obj.getAlignment())

    def __ne__(self, obj):
        if not isinstance(obj, TextStyle):
            return True
        if obj is self:
            return False
        return (self.__name != obj.getName() or
                self.__family != obj.getFamily() or
                self.__style != obj.getStyle() or
                self.__weight != obj.getWeight() or
                self.__color != obj.getColor() or
                abs(self.__size - obj.getSize()) > 1e-10 or
                abs(self.__angle - obj.getAngle()) > 1e-10 or
                self.__alignment != obj.getAlignment())

    def finish(self):
        """Finalization for TextStyle instances.
        """
        self.__color = None


    def getValues(self):
        _vals = {}
        _vals['name'] = self.__name
        _vals['family'] = self.__family
        _vals['style'] = self.__style
        _vals['weight'] = self.__weight
        _vals['color'] = self.__color.getColors()
        _vals['size'] = self.__size
        _vals['angle'] = self.__angle
        _vals['align'] = self.__alignment
        return _vals

    def getName(self):
        """Retrieve the name of the TextStyle.

getName()
        """
        return self.__name

    name = property(getName, None, None, "TextStyle name.")

    def getFamily(self):
        """Return the font family.

getFamily()
        """
        return self.__family

    family = property(getFamily, None, None, "Text font family")

    def getStyle(self):
        """Return the font style.

getStyle()
        """
        return self.__style

    style = property(getStyle, None, None, "Text font style")

    def getStyleAsString(cls, s):
        """Return a text string for the font style.

getStyleAsString(s)

This classmethod returns 'normal', 'oblique', or 'italic'
        """
        if not isinstance(s, int):
            raise TypeError, "Invalid argument type: " + `type(s)`
        if s == TextStyle.FONT_NORMAL:
            _str = 'normal'
        elif s == TextStyle.FONT_OBLIQUE:
            _str = 'oblique'
        elif s == TextStyle.FONT_ITALIC:
            _str = 'italic'
        else:
            raise ValueError, "Unexpected style value: %d" % s
        return _str

    getStyleAsString = classmethod(getStyleAsString)

    def getStyleFromString(cls, s):
        """Return a font style value based on a text string.

getStyleFromString(s)

This classmethod returns a value based on the string argument:

'normal' -> TextStyle.FONT_NORMAL
'oblique' -> TextStyle.FONT_OBLIQUE
'italic' -> TextStyle.FONT_ITALIC

If the string is not listed above a ValueError execption is raised.
        """
        if not isinstance(s, str):
            raise TypeError, "Invalid argument type: " + `type(s)`
        _ls = s.lower()
        if _ls == 'normal':
            _v = TextStyle.FONT_NORMAL
        elif _ls == 'oblique':
            _v = TextStyle.FONT_OBLIQUE
        elif _ls == 'italic':
            _v = TextStyle.FONT_ITALIC
        else:
            raise ValueError, "Unexpected style string: " + s
        return _v

    getStyleFromString = classmethod(getStyleFromString)

    def getStyleStrings(cls):
        """Return the font style values as strings.

getStyleStrings()

This classmethod returns a list of strings.
        """
        return [_('Normal'),
                _('Oblique'),
                _('Italic')
                ]

    getStyleStrings = classmethod(getStyleStrings)

    def getStyleValues(cls):
        """Return the font style values.

getStyleValues()

This classmethod returns a list of values.
        """
        return [TextStyle.FONT_NORMAL,
                TextStyle.FONT_OBLIQUE,
                TextStyle.FONT_ITALIC
                ]

    getStyleValues = classmethod(getStyleValues)
    
    def getWeight(self):
        """Return the font weight.

getWeight()
        """
        return self.__weight

    weight = property(getWeight, None, None, "Text font weight")

    def getWeightAsString(cls, w):
        """Return a text string for the font weight.

getWeightAsString(w)

This classmethod returns 'normal', 'light', 'bold', or 'heavy'.
         """
        if not isinstance(w, int):
            raise TypeError, "Invalid argument type: " + `type(w)`
        if w == TextStyle.WEIGHT_NORMAL:
            _str = 'normal'
        elif w == TextStyle.WEIGHT_LIGHT:
            _str = 'light'
        elif w == TextStyle.WEIGHT_BOLD:
            _str = 'bold'
        elif w == TextStyle.WEIGHT_HEAVY:
            _str = 'heavy'
        else:
            raise ValueError, "Unexpected weight value: %d" % w
        return _str

    getWeightAsString = classmethod(getWeightAsString)

    def getWeightFromString(cls, s):
        """Return a font weight value for a given string argument.

getWeightFromString(s)

This classmethod returns a value based on the string argument:

'normal' -> TextStyle.WEIGHT_NORMAL
'light' -> TextStyle.WEIGHT_LIGHT
'bold' -> TextStyle.WEIGHT_BOLD
'heavy' -> TextStyle.WEIGHT_HEAVY

If the string is not listed above a ValueError execption is raised.
         """
        if not isinstance(s, str):
            raise TypeError, "Invalid argument type: " + `type(s)`
        _ls = s.lower()
        if _ls == 'normal':
            _v = TextStyle.WEIGHT_NORMAL
        elif _ls == 'light':
            _v = TextStyle.WEIGHT_LIGHT
        elif _ls == 'bold':
            _v = TextStyle.WEIGHT_BOLD
        elif _ls == 'heavy':
            _v = TextStyle.WEIGHT_HEAVY
        else:
            raise ValueError, "Unexpected weight string: " + s
        return _v

    getWeightFromString = classmethod(getWeightFromString)

    def getWeightStrings(cls):
        """Return the font weight values as strings.

getWeightStrings()

This classmethod returns a list of strings.
        """
        return [_('Normal'),
                _('Light'),
                _('Bold'),
                _('Heavy')
                ]

    getWeightStrings = classmethod(getWeightStrings)

    def getWeightValues(cls):
        """Return the font weight values.

getWeightValues()

This classmethod returns a list of values.
        """
        return [TextStyle.WEIGHT_NORMAL,
                TextStyle.WEIGHT_LIGHT,
                TextStyle.WEIGHT_BOLD,
                TextStyle.WEIGHT_HEAVY
                ]

    getWeightValues = classmethod(getWeightValues)
    
    def getColor(self):
        """Return the font color.

getColor()
        """
        return self.__color

    color = property(getColor, None, None, "Text color")

    def getSize(self):
        """Return the specified size.

getSize()
        """
        return self.__size

    size = property(getSize, None, None, "Text size.")

    def getAngle(self):
        """Return the angle at which the text is drawn.

getAngle()

This method returns an angle -360.0 < angle < 360.0.
        """
        return self.__angle

    angle = property(getAngle, None, None, "Text angle.")

    def getAlignment(self):
        """Return the line justification setting.

getAlignment()
        """
        return self.__alignment

    alignment = property(getAlignment, None, "Text alignment.")

    def getAlignmentAsString(cls, a):
        """Return a text string for the text alignment.

getAlignmentAsString(w)

This classmethod returns 'left', 'center', or 'right'
         """
        if not isinstance(a, int):
            raise TypeError, "Invalid argument type: " + `type(a)`
        if a == TextStyle.ALIGN_LEFT:
            _str = 'left'
        elif a == TextStyle.ALIGN_CENTER:
            _str = 'center'
        elif a == TextStyle.ALIGN_RIGHT:
            _str = 'right'
        else:
            raise ValueError, "Unexpected alignment value: %d" % a
        return _str

    getAlignmentAsString = classmethod(getAlignmentAsString)

    def getAlignmentFromString(cls, s):
        """Return a text alignment based on a string argument.

getAlignmentFromString(s)

This classmethod returns a value based on the string argument:

'left' -> TextStyle.ALIGN_LEFT
'center' -> TextStyle.ALIGN_CENTER
'right' -> TextStyle.ALIGN_RIGHT

If the string is not listed above a ValueError execption is raised.
         """
        if not isinstance(s, str):
            raise TypeError, "Invalid argument type: " + `type(s)`
        _ls = s.lower()
        if _ls == 'left':
            _v = TextStyle.ALIGN_LEFT
        elif _ls == 'center':
            _v = TextStyle.ALIGN_CENTER
        elif _ls == 'right':
            _v = TextStyle.ALIGN_RIGHT
        else:
            raise ValueError, "Unexpected alignment string: " + s
        return _v

    getAlignmentFromString = classmethod(getAlignmentFromString)

    def getAlignmentStrings(cls):
        """Return the text alignment values as strings.

getAlignmentStrings()

This classmethod returns a list of strings.
        """
        return [_('Left'),
                _('Center'),
                _('Right')
                ]

    getAlignmentStrings = classmethod(getAlignmentStrings)

    def getAlignmentValues(cls):
        """Return the text alignment values.

getAlignmentValues()

This classmethod returns a list of values.
        """
        return [TextStyle.ALIGN_LEFT,
                TextStyle.ALIGN_CENTER,
                TextStyle.ALIGN_RIGHT
                ]

    getAlignmentValues = classmethod(getAlignmentValues)

#
# TextBlock
#

class TextBlock(entity.Entity):
    """A class representing text in a drawing.

A TextBlock instance has the following attributes:

text: Text within the TextBlock
location: Spatial location of the TextBlock
family: The font family
style: The font style
weight: The font weight
color: The font color
size: Text size
alignment: Text positioning at the location
angle: Angular position of the text

A TextBlock instance has the following methods:

{get/set}TextStyle(): Get/Set the TextStyle for the TextBlock
{get/set}Text(): Get/Set the text
{get/set}Location(): Get/Set the TextBlock location
{get/set}Family(): Get/Set the font family.
{get/set}Style(): Get/Set the font style.
{get/set}Weight(): Get/Set the font weight.
{get/set}Color(): Get/Set the font color.
{get/set}Size(): Get/Set the text size.
{get/set}Angle(): Get/Set the text angle
{get/set}Alignment(): Get/Set the text positioning
{get/set}Bounds(): Get/Set the height and width of the TextBlock.
{get/set}FontScale(): Get/Set a scale factor used for font display.
getLineCount(): Get the number of lines stored in the TextBlock

The TextBlock class has the following classmethods:

{get/set}DefaultTextStyle(): Get/Set the default TextStyle for the class.
    """
    __messages = {
        'text_changed' : True,
        'textstyle_changed' : True,
        'font_family_changed' : True,
        'font_style_changed' : True,
        'font_weight_changed' : True,
        'font_color_changed' : True,
        'text_size_changed' : True,
        'text_angle_changed' : True,
        'text_alignment_changed' : True,
        'moved' : True,
        }

    __defstyle = None

    def __init__(self, x, y, text, textstyle=None, **kw):
        """Initialize a TextBlock instance.

TextBlock(x, y, text[, textstyle=None])
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        if not isinstance(text, types.StringTypes):
            raise TypeError, "Invalid text data: " + str(text)
        _tstyle = textstyle
        if _tstyle is None:
            _tstyle = self.getDefaultTextStyle()
        else:
            if not isinstance(_tstyle, TextStyle):
                raise TypeError, "Invalid TextStyle object: " + `_tstyle`
        _family = None
        if 'family' in kw:
            _family = kw['family']
            if not isinstance(_family, types.StringTypes):
                raise TypeError, "Invalid font family: " + str(_family)
            if _family == _tstyle.getFamily():
                _family = None
        _style = None
        if 'style' in kw:
            _style = kw['style']
            if not isinstance(_style, int):
                raise TypeError, "Invalid font style: " + str(_style)
            if (_style != TextStyle.FONT_NORMAL and
                _style != TextStyle.FONT_OBLIQUE and
                _style != TextStyle.FONT_ITALIC):
                raise ValueError, "Invalid font style value: %d" % _style
            if _style == _tstyle.getStyle():
                _style = None
        _weight = None
        if 'weight' in kw:
            _weight = kw['weight']
            if not isinstance(_weight, int):
                raise TypeError, "Invalid font weight: " + str(_weight)
            if (_weight != TextStyle.WEIGHT_NORMAL and
                _weight != TextStyle.WEIGHT_LIGHT and
                _weight != TextStyle.WEIGHT_BOLD and
                _weight != TextStyle.WEIGHT_HEAVY):
                raise ValueError, "Invalid font weight value: %d" % _weight
            if _weight == _tstyle.getWeight():
                _weight = None
        _color = None
        if 'color' in kw:
            _color = kw['color']
            if not isinstance(_color, color.Color):
                raise TypeError, "Invalid font color: " + str(_color)
            if _color == _tstyle.getColor():
                _color = None
        _size = None
        if 'size' in kw:
            _size = util.get_float(kw['size'])
            if _size < 0.0:
                raise ValueError, "Invalid text size: %g" % _size
            if abs(_size - _tstyle.getSize()) < 1e-10:
                _size = None
        _angle = None
        if 'angle' in kw:
            _angle = util.get_float(kw['angle'])
            if _angle > 360.0 or _angle < -360.0:
                _angle = math.fmod(_angle, 360.0)
            if abs(_angle - _tstyle.getAngle()) < 1e-10:
                _angle = None
        _align = None
        if 'align' in kw:
            _align = kw['align']
            if not isinstance(_align, int):
                raise TypeError, "Invalid text alignment: " + str(_align)
            if (_align != TextStyle.ALIGN_LEFT and
                _align != TextStyle.ALIGN_CENTER and
                _align != TextStyle.ALIGN_RIGHT):
                raise ValueError, "Invalid text alignment value: %d" % _align
            if _align == _tstyle.getAlignment():
                _align = None
        super(TextBlock, self).__init__(**kw)
        self.__location = (_x, _y)
        self.__text = text
        self.__tstyle = _tstyle
        self.__family = _family
        self.__style = _style
        self.__weight = _weight
        self.__color = _color
        self.__size = _size
        self.__angle = _angle
        self.__alignment = _align
        self.__bounds = None
        self.__scale = None

    def getDefaultTextStyle(cls):
        if cls.__defstyle is None:
            cls.__defstyle = TextStyle(u'Default Text Style',
                                       color=color.Color(0xffffff))
        return cls.__defstyle

    getDefaultTextStyle = classmethod(getDefaultTextStyle)

    def setDefaultTextStyle(cls, s):
        if not isinstance(s, TextStyle):
            raise TypeError, "Invalid TextStyle: " + `type(s)`
        cls.__defstyle = s

    setDefaultTextStyle = classmethod(setDefaultTextStyle)

    def finish(self):
        """Finalization for TextBlock instances.

finish()
        """
        if self.__color is not None:
            self.__color = None
        super(TextBlock, self).finish()

    def getValues(self):
        """Return values comprising the TextBlock.

getValues()

This method extends the Entity::getValues() method.
        """
        _data = super(TextBlock, self).getValues()
        _data.setValue('type', 'textblock')
        _data.setValue('location', self.__location)
        _data.setValue('text', self.__text)
        _data.setValue('textstyle', self.__tstyle.getValues())
        if self.__family is not None:
            _data.setValue('family', self.__family)
        if self.__style is not None:
            _data.setValue('style', self.__style)
        if self.__weight is not None:
            _data.setValue('weight', self.__weight)
        if self.__color is not None:
            _data.setValue('color', self.__color.getColors())
        if self.__size is not None:
            _data.setValue('size', self.__size)
        if self.__angle is not None:
            _data.setValue('angle', self.__angle)
        if self.__alignment is not None:
            _data.setValue('align', self.__alignment)
        return _data

    def getText(self):
        """Get the current text within the TextBlock.

getText()
        """
        return self.__text

    def setText(self, text):
        """Set the text within the TextBlock.

setText(text)
        """
        if not isinstance(text, types.StringTypes):
            raise TypeError, "Invalid text data: " + str(text)
        _ot = self.__text
        if _ot != text:
            self.startChange('text_changed')
            self.__text = text
            self.endChange('text_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('text_changed', _ot)
            self.modified()

    text = property(getText, setText, None, "TextBlock text.")

    def getLocation(self):
        """Return the TextBlock spatial position.

getLocation()
        """
        return self.__location

    def setLocation(self, x, y):
        """Store the spatial position of the TextBlock.

setLocation(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _ox, _oy = self.__location
        if abs(_ox - _x) > 1e-10 or abs(_oy - _y) > 1e-10:
            self.startChange('moved')
            self.__location = (_x, _y)
            self.endChange('moved')
            self.sendMessage('moved', _ox, _oy)
            self.modified()

    location = property(getLocation, None, None, "TextBlock location")

    def getTextStyle(self):
        """Return the TextStyle associated with this TextBlock.

getTextStyle()
        """
        return self.__tstyle

    def setTextStyle(self, textstyle=None):
        """Store the TextStyle associated with this TextBlock.

setTextStyle([textstyle])

Optional argument 'textstyle' should be an TextStyle instance. If
no argument is given the TextBlock will use a default TextStyle.
The TextBlock will have all the text appearance and positioning
attributes set the the values in the TextStyle.
        """
        _ts = textstyle
        if _ts is None:
            _ts = self.getDefaultTextStyle()
        if not isinstance(_ts, TextStyle):
            raise TypeError, "Invalid text style: " + `_ts`
        _os = self.__tstyle
        if _os != _ts:
            _opts = {}
            if self.__family is not None:
                _opts['family'] = self.__family
            if self.__style is not None:
                _opts['style'] = self.__style
            if self.__weight is not None:
                _opts['weight'] = self.__weight
            if self.__color is not None:
                _opts['color'] = self.__color
            if self.__size is not None:
                _opts['size'] = self.__size
            if self.__angle is not None:
                _opts['angle'] = self.__angle
            if self.__alignment is not None:
                _opts['align'] = self.__alignment
            self.startChange('textstyle_changed')
            self.__tstyle = _ts
            self.endChange('textstyle_changed')
            #
            # call the methods with no arguments to set the values
            # given in the new TextStyle
            #
            self.setFamily()
            self.setStyle()
            self.setWeight()
            self.setColor()
            self.setSize()
            self.setAngle()
            self.setAlignment()
            self.sendMessage('textstyle_changed', _os, _opts)
            self.modified()

    def getFamily(self):
        """Return the font family.

getFamily()
        """
        _family = self.__family
        if _family is None:
            _family = self.__tstyle.getFamily()
        return _family

    def setFamily(self, family=None):
        """Set the font family.

setFamily([family])

Optional argument 'family' should be a string giving the
font family. Calling this method without an argument
sets the font family to that defined in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting family not allowed - object locked."
        _family = family
        if _family is not None:
            if not isinstance(family, types.StringTypes):
                raise TypeError, "Invalid family type: " + `type(family)`
        _f = self.getFamily()
        if ((_family is None and self.__family is not None) or
            (_family is not None and _family != _f)):
            self.startChange('font_family_changed')
            self.__family = _family
            self.endChange('font_family_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('font_family_changed', _f)
            self.modified()

    family = property(getFamily, setFamily, None, "Text object font family")

    def getStyle(self):
        """Return the font style.

getStyle()
        """
        _style = self.__style
        if _style is None:
            _style = self.__tstyle.getStyle()
        return _style

    def setStyle(self, style=None):
        """Set the font style.

setStyle([style])

Optional argument 'style' should be one of the following:

TextStyle.FONT_NORMAL
TextStyle.FONT_OBLIQUE
TextStyle.FONT_ITALIC

Calling this method without an argument restores the font
style to that defined in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting style not allowed - object locked."
        _style = style
        if _style is not None:
            if not isinstance(_style, int):
                raise TypeError, "Invalid TextStyle font style type: " + `type(_style)`
            if (_style != TextStyle.FONT_NORMAL and
                _style != TextStyle.FONT_OBLIQUE and
                _style != TextStyle.FONT_ITALIC):
                raise ValueError, "Invalid font style: " + str(_style)
        _s = self.getStyle()
        if ((_style is None and self.__style is not None) or
            (_style is not None and _style != _s)):
            self.startChange('font_style_changed')
            self.__style = _style
            self.endChange('font_style_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('font_style_changed', _s)
            self.modified()

    style = property(getStyle, setStyle, None, "Text font style")

    def getWeight(self):
        """Return the font weight.

getWeight()
        """
        _weight = self.__weight
        if _weight is None:
            _weight = self.__tstyle.getWeight()
        return _weight

    def setWeight(self, weight=None):
        """Set the font weight.

setWeight([weight])

Optional argument 'weight' should be one of the following values:

TextStyle.WEIGHT_NORMAL
TextStyle.WEIGHT_LIGHT
TextStyle.WEIGHT_BOLD
TextStyle.WEIGHT_HEAVY

Calling this method without an argument restores the font weight
to that defined in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting weight not allowed - object locked."
        _weight = weight
        if _weight is not None:
            if not isinstance(_weight, int):
                raise TypeError, "Invalid TextStyle font weight type: " + `type(_weight)`
            if (_weight != TextStyle.WEIGHT_NORMAL and
                _weight != TextStyle.WEIGHT_LIGHT and
                _weight != TextStyle.WEIGHT_BOLD and
                _weight != TextStyle.WEIGHT_HEAVY):
                raise ValueError, "Invalid text weight: %d" % _weight
        _w = self.getWeight()
        if ((_weight is None and self.__weight is not None) or
            (_weight is not None and _weight != _w)):
            self.startChange('font_weight_changed')
            self.__weight = _weight
            self.endChange('font_weight_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('font_weight_changed', _w)
            self.modified()

    weight = property(getWeight, setWeight, None, "Text font weight")

    def getColor(self):
        """Return the font color.

getColor()
        """
        _color = self.__color
        if _color is None:
            _color = self.__tstyle.getColor()
        return _color

    def setColor(self, col=None):
        """Set the font color.

setColor([col])

Optional argument 'col' should be a Color object. Calling
this method without an argument restores the font color to
that defined in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting color not allowed - object locked."
        _col = col
        if _col is not None:
            if not isinstance(_col, color.Color):
                raise TypeError, "Invalid color type: " + `type(_col)`
        _c = self.getColor()
        if ((_col is None and self.__color is not None) or
            (_col is not None and _col != _c)): 
            self.startChange('font_color_changed')
            self.__color = _col
            self.endChange('font_color_changed')
            self.sendMessage('font_color_changed', _c)
            self.modified()

    color = property(getColor, setColor, None, "Text color")

    def getSize(self):
        """Return the text size.

getSize()
        """
        _size = self.__size
        if _size is None:
            _size = self.__tstyle.getSize()
        return _size

    def setSize(self, size=None):
        """Set the size of the text.

setSize([size])

Optionala rgument 'size' should be a float value greater than 0.
Calling this method without an argument restores the text size
to the value given in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting size not allowed - object locked."
        _size = size
        if _size is not None:
            _size = util.get_float(_size)
            if _size < 0.0:
                raise ValueError, "Invalid size: %g" % _size
        _os = self.getSize()
        if ((_size is None and self.__size is not None) or
            (_size is not None and abs(_size - _os) > 1e-10)):
            self.startChange('text_size_changed')
            self.__size = _size
            self.endChange('text_size_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('text_size_changed', _os)
            self.modified()

    size = property(getSize, setSize, None, "Text size.")

    def getAngle(self):
        """Return the angle at which the text is drawn.

getAngle()

This method returns an angle -360.0 < angle < 360.0.
        """
        _angle = self.__angle
        if _angle is None:
            _angle = self.__tstyle.getAngle()
        return _angle

    def setAngle(self, angle=None):
        """Set the angle at which the text block should be drawn.

setAngle([angle])

Optional argument 'angle' should be a float value. Calling this
method without arguments sets the angle to be the value defined
in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting angle not allowed - object locked."
        _angle = angle
        if _angle is not None:
            _angle = util.get_float(_angle)
            if _angle > 360.0 or _angle < -360.0:
                _angle = math.fmod(_angle, 360.0)
        _a = self.getAngle()
        if ((_angle is None and self.__angle is not None) or
            (_angle is not None and abs(_angle - _a) > 1e-10)):
            self.startChange('text_angle_changed')
            self.__angle = _angle
            self.endChange('text_angle_changed')
            self.sendMessage('text_angle_changed', _a)
            self.modified()

    angle = property(getAngle, setAngle, None, "Text angle.")

    def getAlignment(self):
        """Return the line justification setting.

getAlignment()
        """
        _align = self.__alignment
        if _align is None:
            _align = self.__tstyle.getAlignment()
        return _align

    def setAlignment(self, align=None):
        """Set left, center, or right line justification.

setAlignment([align])

Optional argument 'align' should be one of

TextStyle.ALIGN_LEFT
TextStyle.ALIGN_CENTER
TextStyle.ALIGN_RIGHT

Calling this method without arguments sets the text alignment
to be that given in the TextStyle.
        """
        if self.isLocked():
            raise RuntimeError, "Setting alignment not allowed - object locked."
        _align = align
        if _align is not None:
            if not isinstance(_align, int):
                raise TypeError, "Invalid TextStyle alignment type: " + `type(_align)`
            if (_align != TextStyle.ALIGN_LEFT and
                _align != TextStyle.ALIGN_CENTER and
                _align != TextStyle.ALIGN_RIGHT):
                raise ValueError, "Invalid text alignment value: %d" % _align
        _a = self.getAlignment()
        if ((_align is None and self.__alignment is not None) or
            (_align is not None and _align != _a)):
            self.startChange('text_alignment_changed')
            self.__alignment = _align
            self.endChange('text_alignment_changed')
            if self.__bounds is not None:
                self.__bounds = None
            self.sendMessage('text_alignment_changed', _a)
            self.modified()

    alignment = property(getAlignment, setAlignment, None, "Text alignment.")

    def move(self, dx, dy):
        """Move a TextBlock.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked():
            raise RuntimeError, "Moving not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__location
            self.startChange('moved')
            self.__location = ((_x + _dx), (_y + _dy))
            self.endChange('moved')
            self.sendMessage('moved', _x, _y)
            self.modified()

    def getLineCount(self):
        """Return the number of lines of text in the TextBlock

getLineCount()        
        """
        #
        # ideally Python itself would provide a linecount() method
        # so the temporary list would not need to be created ...
        #
        return len(self.__text.splitlines())

    def clone(self):
        """Return an identical copy of a TextBlock.

clone()        
        """
        _x, _y = self.getLocation()
        _text = self.getText()
        _textstyle = self.getTextStyle()
        _tb = TextBlock(_x, _y, _text, _textstyle)
        _family = self.getFamily()
        if _family != _textstyle.getFamily():
            _tb.setFamily(_family)
        _style = self.getStyle()
        if _style != _textstyle.getStyle():
            _tb.setStyle(_style)
        _weight = self.getWeight()
        if _weight != _textstyle.getWeight():
            _tb.setWeight(_weight)
        _color = self.getColor()
        if _color != _textstyle.getColor():
            _tb.setColor(_color)
        _size = self.getSize()
        if abs(_size - _textstyle.getSize()) > 1e-10:
            _tb.setSize(_size)
        _angle = self.getAngle()
        if abs(_angle - _textstyle.getAngle()) > 1e-10:
            _tb.setAngle(_angle)
        _align = self.getAlignment()
        if _align != _textstyle.getAlignment():
            _tb.setAlignment(_align)
        return _tb
        
    def getBounds(self):
        """Get the width and height of the TextBlock.

getBounds()

This method can return None if the boundary has not been calculated
or the TextBlock has been changed.
        """
        return self.__bounds

    def setBounds(self, width=None, height=None):
        """Set the width and height of the TextBlock.

setBounds([width, height])

Arguments 'width' and 'height' should be positive float values
if used. If both arguments are None, the boundary of the TextBlock
is unset.
        """
        _w = width
        _h = height
        if _w is None and _h is None:
            self.__bounds = None
        else:
            if _w is None:
                raise ValueError, "Width cannot be None"
            _w = util.get_float(_w)
            if _w < 0.0:
                raise ValueError, "Invalid width: %g" % _w
            if _h is None:
                raise ValueError, "Height cannot be None"
            _h = util.get_float(_h)
            if _h < 0.0:
                raise ValueError, "Invalid height: %g" % _w
            self.__bounds = (_w, _h)

    def inRegion (self, xmin, ymin, xmax, ymax, fully=True):
        """Returns True if the TextBlock is within the bounding values.

inRegion(xmin, ymin, xmax, ymax)

The four arguments define the boundary of an area, and the
function returns True if the TextBlock lies within that area.
Otherwise, the function returns False.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        util.test_boolean(fully)
        _x, _y = self.__location
        if self.__bounds is None:
            return not ((_x < _xmin) or
                        (_x > _xmax) or
                        (_y < _ymin) or
                        (_y > _ymax))
        else:
            _w, _h = self.__bounds
            _flag = True
            _align = self.getAlignment()
            if _align == TextStyle.ALIGN_LEFT:
                if ((_x > _xmax) or ((_x + _w) < _xmin)):
                    _flag = False
            elif _align == TextStyle.ALIGN_CENTER:
                if (((_x - (_w/2.0)) > _xmax) or ((_x + (_w/2.0)) < _xmin)):
                    _flag = False
            elif _align == TextStyle.ALIGN_RIGHT:
                if (((_x - _w) > _xmax) or (_x < _xmin)):
                    _flag = False
            else:
                raise ValueError, "Unexpected alignment: %d" % _align
            if _flag:
                _flag = not ((_y < _ymin) or ((_y - _h) > _ymax))
            return _flag

    def getFontScale(self):
        """Return the stored font scaling factor

getFontScale()

This method will raise a ValueError exception if there has
not be a value stored with the setFontScale() call.
        """
        if self.__scale is None:
            raise ValueError, "Scale not set."
        return self.__scale

    def setFontScale(self, scale):
        """Store a value used to scale the TextBlock font.

setFontScale(scale)

Argument 'scale' should be a positive float value.
        """
        _s = util.get_float(scale)
        if not _s > 0.0:
            raise ValueError, "Invalid scale value: %g" % _s
        self.__scale = _s

    def sendsMessage(self, m):
        if m in TextBlock.__messages:
            return True
        return super(TextBlock, self).sendsMessage(m)

#
# TextBlock history class
#

class TextBlockLog(entity.EntityLog):
    __setops = {
        'text_changed' : TextBlock.setText,
        'font_family_changed' : TextBlock.setFamily,
        'font_style_changed' : TextBlock.setStyle,
        'font_color_changed' : TextBlock.setColor,
        'font_weight_changed' : TextBlock.setWeight,
        'text_size_changed' : TextBlock.setSize,
        'text_angle_changed' : TextBlock.setAngle,
        'text_alignment_changed' : TextBlock.setAlignment,
        }

    __getops = {
        'text_changed' : TextBlock.getText,
        'font_family_changed' : TextBlock.getFamily,
        'font_style_changed' : TextBlock.getStyle,
        'font_color_changed' : TextBlock.getColor,
        'font_weight_changed' : TextBlock.getWeight,
        'text_size_changed' : TextBlock.getSize,
        'text_angle_changed' : TextBlock.getAngle,
        'text_alignment_changed' : TextBlock.getAlignment,
        }

    def __init__(self, tblock):
        if not isinstance(tblock, TextBlock):
            raise TypeError, "Invalid TextBlock: " + `tblock`
        super(TextBlockLog, self).__init__(tblock)
        tblock.connect('textstyle_changed', self._textstyleChanged)
        tblock.connect('text_changed', self._textChanged)
        tblock.connect('font_family_changed', self._familyChanged)
        tblock.connect('font_style_changed', self._styleChanged)
        tblock.connect('font_color_changed', self._colorChanged)
        tblock.connect('font_weight_changed', self._weightChanged)
        tblock.connect('text_size_changed', self._sizeChanged)
        tblock.connect('text_angle_changed', self._angleChanged)
        tblock.connect('text_alignment_changed', self._alignmentChanged)
        tblock.connect('moved', self._moveText)

    def _textstyleChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _ts = args[0]
        if not isinstance(_ts, TextStyle):
            raise TypeError, "Invalid TextStyle type: " + `type(_ts)`
        _opts = args[1]
        if not isinstance(_opts, dict):
            raise TypeError, "Invalid option type: " + `type(_opts)`
        _data = {}
        _data['textstyle'] = _ts.getValues()
        for _k, _v in _opts:
            if _k == 'color':
                _data['color'] = _v.getColors()
            else:
                _data[_k] = _v
        self.saveUndoData('textstyle_changed', _data)

    def _textChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _text = args[0]
        if not isinstance(_text, types.StringTypes):
            raise TypeError, "Invalid text type: " + `type(_text)`
        self.saveUndoData('text_changed', _text)

    def _familyChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _family = args[0]
        if not isinstance(_family, types.StringTypes):
            raise TypeError, "Invalid family type: " + `type(_family)`
        self.saveUndoData('font_family_changed', _family)

    def _styleChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _style = args[0]
        if (_style != TextStyle.FONT_NORMAL and
            _style != TextStyle.FONT_OBLIQUE and
            _style != TextStyle.FONT_ITALIC):
            raise ValueError, "Invalid font style: " + str(_style)
        self.saveUndoData('font_style_changed', _style)

    def _colorChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _color = args[0]
        if not isinstance(_color, color.Color):
            raise TypeError, "Invalid color type: " + `type(_color)`
        self.saveUndoData('font_color_changed', _color.getColors())

    def _weightChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _weight = args[0]
        if (_weight != TextStyle.WEIGHT_NORMAL and
            _weight != TextStyle.WEIGHT_LIGHT and
            _weight != TextStyle.WEIGHT_BOLD and
            _weight != TextStyle.WEIGHT_HEAVY):
            raise ValueError, "Invalid text weight: %d" % _weight
        self.saveUndoData('font_weight_changed', _weight)

    def _sizeChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _size = args[0]
        if not isinstance(_size, float):
            raise TypeError, "Unexpected size type: " + `type(_size)`
        if _size < 0.0:
            raise ValueError, "Invalid text size: %g" % _size
        self.saveUndoData('text_size_changed', _size)

    def _angleChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _angle = args[0]
        if not isinstance(_angle, float):
            raise TypeError, "Unexpected angle type: " + `type(_angle)`
        if _angle > 360.0 or _angle < -360.0:
            _angle = math.fmod(_angle, 360.0)
        self.saveUndoData('text_angle_changed', _angle)

    def _alignmentChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _align = args[0]
        if (_align != TextStyle.ALIGN_LEFT and
            _align != TextStyle.ALIGN_CENTER and
            _align != TextStyle.ALIGN_RIGHT):
            raise ValueError, "Invalid text alignment value: %d" % _align
        self.saveUndoData('text_alignment_changed', _align)

    def _moveText(self, tb, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = args[0]
        if not isinstance(_x, float):
            raise TypeError, "Unexpected type for x: " + `type(_x)`
        _y = args[1]
        if not isinstance(_y, float):
            raise TypeError, "Unexpected type for y: " + `type(_y)`
        self.saveUndoData('moved', _x, _y)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _tblock = self.getObject()
        _image = None
        _layer = _tblock.getParent()
        if _layer is not None:
            _image = _layer.getParent()
        _op = args[0]
        if (_op == 'text_changed' or
            _op == 'font_family_changed' or
            _op == 'font_style_changed' or
            _op == 'font_weight_changed' or
            _op == 'text_size_changed' or
            _op == 'text_angle_changed' or
            _op == 'text_alignment_changed'):
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _val = args[1]
            _get = TextBlockLog.__getops[_op]
            _sdata = _get(_tblock)
            self.ignore(_op)
            try:
                _set = TextBlockLog.__setops[_op]
                if undo:
                    _tblock.startUndo()
                    try:
                        _set(_tblock, _val)
                    finally:
                        _tblock.endUndo()
                else:
                    _tblock.startRedo()
                    try:
                        _set(_tblock, _val)
                    finally:
                        _tblock.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'moved':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _x = args[1]
            if not isinstance(_x, float):
                raise TypeError, "Unexpected type for x: " + `type(_x)`
            _y = args[2]
            if not isinstance(_y, float):
                raise TypeError, "Unexpected type for y: " + `type(_y)`
            _tx, _ty = _tblock.getLocation()
            self.ignore(_op)
            try:
                if undo:
                    _tblock.startUndo()
                    try:
                        _tblock.setLocation(_x, _y)
                    finally:
                        _tblock.endUndo()
                else:
                    _tblock.startRedo()
                    try:
                        _tblock.setLocation(_x, _y)
                    finally:
                        _tblock.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _tx, _ty)
        elif _op == 'font_color_changed':
            if _image is None:
                raise RuntimeError, "TextBlock not stored in an Image"
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _tblock.getColor().getColors()
            self.ignore(_op)
            try:
                _color = None
                for _c in _image.getImageEntities('color'):
                    if _c.getColors() == args[1]:
                        _color = _c
                        break
                if undo:
                    _tblock.startUndo()
                    try:
                        _tblock.setColor(_color)
                    finally:
                        _tblock.endUndo()
                else:
                    _tblock.startRedo()
                    try:
                        _tblock.setColor(_color)
                    finally:
                        _tblock.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'textstyle_changed':
            if _image is None:
                raise RuntimeError, "TextBlock not stored in an Image"
            if _alen < 2:
                raise ValueError, "Invalid argument cound: %d" % _alen
            _data = args[1]
            _tsdata = _data['textstyle']            
            _sdata = {}
            _ts = _tblock.getTextStyle()
            _sdata['textstyle'] = _ts.getValues()
            _family = _tblock.getFamily()
            if _family != _ts.getFamily():
                _sdata['family'] = _family
            _style = _tblock.getStyle()
            if _style != _ts.getStyle():
                _sdata['style'] = _style
            _weight = _tblock.getWeight()
            if _weight != _ts.getWeight():
                _sdata['weight'] = _weight
            _color = _tblock.getColor()
            if _color != _ts.getColor():
                _sdata['color'] = _color.getColors()
            _size = _tblock.getSize()
            if abs(_size - _ts.getSize()) > 1e-10:
                _sdata['size'] = _size
            _angle = _tblock.getAngle()
            if abs(_angle - _ts.getAngle()) > 1e-10:
                _sdata['angle'] = _angle
            _align = _tblock.getAlignment()
            if _align != _ts.getAlignment():
                _sdata['align'] = _align
            self.ignore(_op)
            try:
                _tstyle = None
                for _ts in _image.getImageEntities('textstyle'):
                    if _ts.getName() != _tsdata['name']:
                        continue
                    if _ts.getFamily() != _tsdata['family']:
                        continue
                    if _ts.getStyle() != _tsdata['style']:
                        continue
                    if _ts.getWeight() != _tsdata['weight']:
                        continue
                    if _ts.getColor().getColors() != _tsdata['color']:
                        continue
                    if abs(_ts.getSize() - _tsdata['size']) > 1e-10:
                        continue
                    if abs(_ts.getAngle() - _tsdata['angle']) > 1e-10:
                        continue
                    if _ts.getAlignment() != _tsdata['align']:
                        continue
                    _tstyle = _ts
                    break
                if undo:
                    _tblock.startUndo()
                    try:
                        _tblock.setTextStyle(_tstyle)
                    finally:
                        _tblock.endUndo()
                else:
                    _tblock.startRedo()
                    try:
                        _tblock.setTextStyle(_tstyle)
                    finally:
                        _tblock.endRedo()
            finally:
                self.receive(_op)
            #
            # restore values differing from the TextStyle
            #
            _tblock.mute()
            try:
                _family = _data.get('family')
                if _family is not None:
                    _tblock.setFamily(_family)
                _style = _data.get('style')
                if _style is not None:
                    _tblock.setStyle(_style)
                _weight = _data.get('weight')
                if _weight is not None:
                    _tblock.setWeight(_weight)
                _color = _data.get('color')
                if _color is not None:
                    _col = None
                    for _c in _image.getImageEntities('color'):
                        if _c.getColors() == _color:
                            _col = _c
                            break
                    _tblock.setColor(_col)
                _size = _data.get('size')
                if _size is not None:
                    _tblock.setSize(_size)
                _angle = _data.get('angle')
                if _angle is not None:
                    _tblock.setAngle(_angle)
                _align = _data.get('align')
                if _align is not None:
                    _tblock.setAlignment(_align)
            finally:
                _tblock.unmute()
            self.saveData(undo, _op, _sdata)
        else:
            super(TextBlockLog, self).execute(undo, *args)
