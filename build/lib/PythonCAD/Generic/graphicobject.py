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
# classes for graphic objects
#

from PythonCAD.Generic import style
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import baseobject
from PythonCAD.Generic import entity
from PythonCAD.Generic import util

class GraphicObject(baseobject.Subpart):
    """A class representing an object that is drawn.

This class is meant to be a base class for things like
line segments, circles, etc. The GraphicObject class
has one attribute that cannot be None:

style: The Style object

There are three other attributes that override values in
the style attribute:

color: A Color object
thickness: A positive float value
linetype: A Linetype object

A GraphicObject object has the following methods:

{get/set}Style(): Get/Set the Style of a GraphicObject.
{get/set}Color(): Get/Set the Color of a GraphicObject.
{get/set}Thickness(): Get/Set the thickness of a GraphicObject.
{get/set}Linetype(): Get/Set the Linetype of a GraphicObject.
    """
    __messages = {
        'style_changed' : True,
        'color_changed' : True,
        'linetype_changed' : True,
        'thickness_changed' : True,
        }

    __defstyle = None

    def __init__(self, st=None, lt=None, col=None, t=None, **kw):
        """Initialize a GraphicObject.

GraphicObject([st, lt, col, t])

Optional arguments:
style: A style object that overrides the class default
linetype: A Linetype object that overrides the value in the Style
color: A Color object that overrides the value in the Style
thickness: A positive float that overrides the value in the Style
        """
        super(GraphicObject, self).__init__(**kw)
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        if not isinstance(_st, style.Style):
            raise TypeError, "Invalid style type: " + `type(_st)`
        _col = _lt = _t = None
        if 'color' in kw:
            _col = kw['color']
        if _col is None:
            _col = col
        if _col is not None:
            if not isinstance(_col, color.Color):
                _col = color.Color(_col)
            if _col == _st.getColor():
                _col = None
        if 'linetype' in kw:
            _lt = kw['linetype']
        if _lt is None:
            _lt = lt
        if _lt is not None:
            if not isinstance(_lt, linetype.Linetype):
                raise TypeError, "Invalid linetype type: " + `type(_lt)`
            if _lt == _st.getLinetype():
                _lt = None
        if 'thickness' in kw:
            _t = kw['thickness']
        if _t is None:
            _t = t
        if _t is not None:
            if not isinstance(_t, float):
                _t = util.get_float(_t)
            if _t < 0.0:
                raise ValueError, "Invalid thickness: %g" % _t
            if abs(_t - _st.getThickness()) < 1e-10:
                _t = None
        self.__style = _st
        self.__color = _col
        self.__linetype = _lt
        self.__thickness = _t

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Style',
                             linetype.Linetype(u'Solid', None),
                             color.Color(0xffffff),
                             1.0)
            cls.__defstyle = _s
        return cls.__defstyle

    getDefaultStyle = classmethod(getDefaultStyle)

    def setDefaultStyle(cls, s):
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid style: " + `type(s)`
        cls.__defstyle = s

    setDefaultStyle = classmethod(setDefaultStyle)
    
    def finish(self):
        self.__style = None
        self.__color = None
        self.__linetype = None
        self.__thickness = None
        super(GraphicObject, self).finish()

    def getStyle(self):
        """Get the Style of the GraphicObject.

getStyle()

Returns the current Style of an object. The values in the
style may be overriden if any of the color, linetype, or
thickness attributes are not None.
        """
        return self.__style

    def setStyle(self, s):
        """Set the Style of the Object.

setStyle(s)

Setting the style of a GraphicObject unsets any overrides for
the object. Setting the Style to None restores the default
style.
        """
        if self.isLocked():
            raise RuntimeError, "Style change not allowed - objected locked."
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        if not isinstance(_s, style.Style):
            raise TypeError, "Invalid style: " + `type(_s)`
        _cs = self.getStyle()
        if _cs != _s:
            _col = None
            if self.__color is not None:
                _col = self.__color
            _lt = None
            if self.__linetype is not None:
                _lt = self.__linetype
            _t = None
            if self.__thickness is not None:
                _t = self.__thickness
            self.startChange('style_changed')
            self.__style = _s
            self.__color = None
            self.__linetype = None
            self.__thickness = None
            self.endChange('style_changed')
            self.sendMessage('style_changed', _cs, _lt, _col, _t)
            self.modified()

    style = property(getStyle, setStyle, None, "Object Style.")

    def getColor(self):
        """Get the Color of the Object.

getColor()
        """
        _color = self.__color
        if _color is None:
            _color = self.__style.getColor()
        return _color

    def setColor(self, c=None):
        """Set the color of the object.

setColor([c])

Setting the color overrides the value in the Style. Setting
the color to None or invoking this method without arguments
restores the color value defined in the Style.
        """
        if self.isLocked():
            raise RuntimeError, "Color change not allowed - object locked."
        _c = c
        if _c is not None:
            if not isinstance(_c, color.Color):
                _c = color.Color(c)
        _oc = self.getColor()
        if ((_c is None and self.__color is not None) or
            (_c is not None and _c != _oc)):
            self.startChange('color_changed')
            self.__color = _c
            self.endChange('color_changed')
            self.sendMessage('color_changed', _oc)
            self.modified()

    color = property(getColor, setColor, None, "Object color.")

    def getThickness(self):
        """Get the thickness of the GraphicObject.

getThickness()
        """
        _th = self.__thickness
        if _th is None:
            _th = self.__style.getThickness()
        return _th

    def setThickness(self, t=None):
        """Set the thickness of a object.

setThickness([t])

Setting the thickness overrides the value in the Style. Setting
the thickness to None, or invoking this method without an
argument, restores the thickness value defined in the Style.
        """
        if self.isLocked():
            raise RuntimeError, "Thickness change not allowed - object locked."
        _t = t
        if _t is not None:
            _t = util.get_float(_t)
            if _t < 0.0:
                raise ValueError, "Invalid thickness: %g" % _t
        _ot = self.getThickness()
        if ((_t is None and self.__thickness is not None) or
            (_t is not None and abs(_t - _ot) > 1e-10)):
            self.startChange('thickness_changed')
            self.__thickness = _t
            self.endChange('thickness_changed')
            self.sendMessage('thickness_changed', _ot)
            self.modified()

    thickness = property(getThickness, setThickness, None, "Object thickness.")

    def getLinetype(self):
        """Get the Linetype of the object.

getLinetype()
        """
        _lt = self.__linetype
        if _lt is None:
            _lt = self.__style.getLinetype()
        return _lt

    def setLinetype(self, lt=None):
        """Set the Linetype of the GraphicObject.

setLinetype([lt])

Setting the Linetype overrides the value in the Sytle. Setting
the Linetype to None or invoking this method without arguments
restores the linetype value defined in the Style.
        """
        if self.isLocked():
            raise RuntimeError, "Linetype change not allowed - object locked."
        _lt = lt
        if _lt is not None:
            if not isinstance(_lt, linetype.Linetype):
                raise TypeError, "Invalid linetype: " + `type(_lt)`
        _ol = self.getLinetype()
        if ((_lt is None and self.__linetype is not None) or
            (_lt is not None and _lt != _ol)):
            self.startChange('linetype_changed')
            self.__linetype = _lt
            self.endChange('linetype_changed')
            self.sendMessage('linetype_changed', _ol)
            self.modified()

    linetype = property(getLinetype, setLinetype, None, "Object Linetype.")

    def getGraphicValues(self):
        _l = _c = _t = None
        _s = self.__style.getStyleValues()
        if self.__linetype is not None:
            _name = self.__linetype.getName()
            _dash = self.__linetype.getList()
            _l = (_name, _dash)
        if self.__color is not None:
            _c = self.__color.getColors()
        if self.__thickness is not None:
            _t = self.__thickness
        return _s, _l, _c, _t

    def getValues(self):
        """Return values comprising the GraphicObject.

getValues()

This method extends the Subpart::getValues() method.
        """
        _data = super(GraphicObject, self).getValues()
        _data.setValue('style', self.__style.getStyleValues())
        if self.__color is not None:
            _data.setValue('color', self.__color.getColors())
        if self.__linetype is not None:
            _lt = self.__linetype
            _data.setValue('linetype', (_lt.getName(), _lt.getList()))
        if self.__thickness is not None:
            _data.setValue('thickness', self.__thickness)
        return _data
    
    def sendsMessage(self, m):
        if m in GraphicObject.__messages:
            return True
        return super(GraphicObject, self).sendsMessage(m)

#
# GraphicObject history class
#

class GraphicObjectLog(entity.EntityLog):
    def __init__(self, obj):
        if not isinstance(obj, GraphicObject):
            raise TypeError, "Invalid GraphicObject: " + `type(obj)`
        super(GraphicObjectLog, self).__init__(obj)
        obj.connect('style_changed', self.__styleChanged)
        obj.connect('linetype_changed', self.__linetypeChanged)
        obj.connect('color_changed', self.__colorChanged)
        obj.connect('thickness_changed', self.__thicknessChanged)

    def __styleChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _data = []
        _style = args[0]
        if not isinstance(_style, style.Style):
            raise TypeError, "Invalid style type: " + `type(_style)`
        _data.append(_style.getStyleValues())
        _lt = args[1]
        if _lt is None:
            _data.append(None)
        else:
            if not isinstance(_lt, linetype.Linetype):
                raise TypeError, "Invalid linetype type: " + `type(_lt)`
            _name = _lt.getName()
            _list = _lt.getList()
            _data.append((_name, _list))
        _col = args[2]
        if _col is None:
            _data.append(None)
        else:
            if not isinstance(_col, color.Color):
                raise TypeError, "Invalid color type: " + `type(_col)`
            _data.append(_col.getColors())
        _t = args[3]
        if _t is None:
            _data.append(None)
        else:
            if not isinstance(_t, float):
                raise TypeError, "Invalid thickness type: " + `type(_t)`
            _data.append(_t)
        self.saveUndoData('style_changed', tuple(_data))

    def __linetypeChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _lt = args[0]
        if not isinstance(_lt, linetype.Linetype):
            raise TypeError, "Invalid linetype type: " + `type(_lt)`
        self.saveUndoData('linetype_changed', (_lt.getName(), _lt.getList()))

    def __colorChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _color = args[0]
        if not isinstance(_color, color.Color):
            raise TypeError, "Invalid color type: " + `type(_color)`
        self.saveUndoData('color_changed', _color.getColors())

    def __thicknessChanged(self, tb, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _t = util.get_float(args[0])
        if _t < 0.0:
            raise ValueError, "Invalid thickness: %g" % _t
        self.saveUndoData('thickness_changed', _t)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _obj = self.getObject()
        _op = args[0]
        _image = None
        _layer = _obj.getParent()
        if _layer is not None:
            _image = _layer.getParent()
        if _op == 'style_changed':
            if _image is None:
                raise RuntimeError, "Object not stored in an Image"
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _style = None
            _sv, _olt, _oc, _ot = args[1]
            _name, _ltdata, _col, _th = _sv
            for _s in _image.getImageEntities('style'):
                if _s.getName() != _name:
                    continue
                _lt = _s.getLinetype()
                if (_lt.getName() != _ltdata[0] or
                    _lt.getList() != _ltdata[1]):
                    continue
                if _s.getColor().getColors() != _col:
                    continue
                if abs(_s.getThickness() - _th) > 1e-10:
                    continue
                _style = _s
                break
            _sdata = _obj.getGraphicValues()
            if _style is not None:
                self.ignore(_op)
                try:
                    if undo:
                        _obj.startUndo()
                        try:
                            _obj.setStyle(_style)
                        finally:
                            _obj.endUndo()
                    else:
                        _obj.startRedo()
                        try:
                            _obj.setStyle(_style)
                        finally:
                            _obj.endRedo()
                finally:
                    self.receive(_op)
                #
                # restore values differing from the Style
                #
                if _olt is not None:
                    _name, _list = _olt
                    _lt = None
                    for _l in _image.getImageEntities('linetype'):
                        if (_l.getName() == _name and _l.getList() == _list):
                            _lt = _l
                            break
                    _obj.mute()
                    try:
                        _obj.setLinetype(_lt)
                    finally:
                        _obj.unmute()
                if _oc is not None:
                    _col = None
                    for _c in _image.getImageEntities('color'):
                        if _c.getColors() == _oc:
                            _col = _c
                            break
                    _obj.mute()
                    try:
                        _obj.setColor(_col)
                    finally:
                        _obj.unmute()
                if _ot is not None:
                    _obj.mute()
                    try:
                        _obj.setThickness(_ot)
                    finally:
                        _obj.unmute()
            self.saveData(undo, _op, _sdata)
        elif _op == 'linetype_changed':
            if _image is None:
                raise RuntimeError, "Object not stored in an Image"
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _lt = _obj.getLinetype()
            _sdata = (_lt.getName(), _lt.getList())
            self.ignore(_op)
            try:
                _name, _list = args[1]
                _lt = None
                for _l in _image.getImageEntities('linetype'):
                    if (_l.getName() == _name and _l.getList() == _list):
                        _lt = _l
                        break
                if undo:
                    _obj.startUndo()
                    try:
                        _obj.setLinetype(_lt)
                    finally:
                        _obj.endUndo()
                else:
                    _obj.startRedo()
                    try:
                        _obj.setLinetype(_lt)
                    finally:
                        _obj.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'color_changed':
            if _image is None:
                raise RuntimeError, "Object not stored in an Image"
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _obj.getColor().getColors()
            self.ignore(_op)
            try:
                _col = None
                for _c in _image.getImageEntities('color'):
                    if _c.getColors() == args[1]:
                        _col = _c
                        break
                if undo:
                    _obj.startUndo()
                    try:
                        _obj.setColor(_col)
                    finally:
                        _obj.endUndo()
                else:
                    _obj.startRedo()
                    try:
                        _obj.setColor(_col)
                    finally:
                        _obj.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'thickness_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _obj.getThickness()
            self.ignore(_op)
            try:
                _t = args[1]
                if undo:
                    _obj.startUndo()
                    try:
                        _obj.setThickness(_t)
                    finally:
                        _obj.endUndo()
                else:
                    _obj.startRedo()
                    try:
                        _obj.setThickness(_t)
                    finally:
                        _obj.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(GraphicObjectLog, self).execute(undo, *args)
