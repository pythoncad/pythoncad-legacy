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
# The class for a drawing
#

import sys
import math
import types
import tempfile
import stat
import os
from PythonCAD.Generic import fileio
from PythonCAD.Generic import imageio

from PythonCAD.Generic import globals
from PythonCAD.Generic import layer
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import point
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import intersections
from PythonCAD.Generic import dimension
from PythonCAD.Generic import color
from PythonCAD.Generic import text
from PythonCAD.Generic import units
from PythonCAD.Generic import options
from PythonCAD.Generic import baseobject
from PythonCAD.Generic import entity
from PythonCAD.Generic import logger
from PythonCAD.Generic import util
from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap

class Image(entity.Entity):
    """The class representing a CAD drawing.

This class contains all the interface-neutral parts of
a drawing. An image is essentially a collection of Layer
objects, plus the bits needed to store the colors, linetypes,
and styles used in a drawing.

Each instance has several attributes:

active_layer: The currently active Layer
top_layer: The initial Layer in the Image
scale: The scale factor of the Image

The following methods are available for each instance:

{get/set}Scale(): Get/Set the current scale factor.
hasColor(): See if a color is already in use in the drawing.
addColor(): Add a Color to the set available for objects in the drawing.
hasLinetype(): See if a Linetype is found in the drawing.
addLinetype(): Add a Linetype to the set available for objects in the drawing.
hasStyle(): See if a Style is in the drawing.
addStyle(): Add a Style to the set available for objects in the drawing.
{get/set}ActiveLayer(): Get/Set the currently active Layer.
addChildLayer(): Make one Layer object a child of another.
addLayer(): Make one Layer object a child of the active Layer's parent.
delLayer(): Remove a Layer from the image.
findPoint(): Find a Point object in the drawing.
mapPoint(): Find objects in the drawing where at some location.
{get/set}CurrentPoint(): Get/Set a coordinate pair
addObject(): Add an object to the drawing.
delObject(): Delete an object from the drawing.
getObject(): Return an object with a specific entity ID
selectObject(): Store a references to an object in the drawing.
deselectObject(): Release a reference to a stored object.
getSelectedObjects(): Retrieve all the selected objects.
clearSelectedObjects(): Release all references to selected objects.
hasSelection(): Return whether the image has an active selection.
getExtents(): Find the size of the drawing.
{get/set}Option(): Retrieve/Store an option used in the drawing.
{get/set}Filename(): Get/Set the filename for this image.
getImageEntities(): Get all the instances of certain image-wide object.
{get/set}Units(): Get/Set the basic length unit in the image.
scaleLength(): Return a linear distance in millimeters.
getClosestPoint(): Return the point/coordinates nearest to a given x/y pair.
{start/end}Action(): Begin/End a sequence of actions to be treated as one event
inAction(): Test if the Image is currently in a startAction()/endAction() block
getAction(): Return the number of startAction()/endAction() blocks performed.
{get/set}Tool(): Get/Set the active Tool used in the Image.
    """

    __options = [
        'AUTOSPLIT',
        'HIGHLIGHT_POINTS',
        'LEADER_ARROW_SIZE',
        'CHAMFER_LENGTH',
        'FILLET_RADIUS',
        'FILLET_TWO_TRIM_MODE',
        'INACTIVE_LAYER_COLOR',
        'BACKGROUND_COLOR',
        'SINGLE_POINT_COLOR',
        'MULTI_POINT_COLOR',
        'UNITS',
        'LINE_STYLE',
        'LINE_TYPE',
        'LINE_COLOR',
        'LINE_THICKNESS',
        'TEXT_STYLE',
        'FONT_FAMILY',
        'FONT_STYLE',
        'FONT_WEIGHT',
        'TEXT_SIZE',
        'FONT_COLOR',
        'TEXT_ANGLE',
        'TEXT_ALIGNMENT',
        'DIM_STYLE',
        'DIM_PRIMARY_FONT_FAMILY',
        'DIM_PRIMARY_FONT_STYLE',
        'DIM_PRIMARY_FONT_WEIGHT',
        'DIM_PRIMARY_FONT_COLOR',
        'DIM_PRIMARY_TEXT_SIZE',
        'DIM_PRIMARY_TEXT_ANGLE',
        'DIM_PRIMARY_TEXT_ALIGNMENT',
        'DIM_PRIMARY_PREFIX',
        'DIM_PRIMARY_SUFFIX',
        'DIM_PRIMARY_PRECISION',
        'DIM_PRIMARY_UNITS',
        'DIM_PRIMARY_LEADING_ZERO',
        'DIM_PRIMARY_TRAILING_DECIMAL',
        'DIM_SECONDARY_FONT_FAMILY',
        'DIM_SECONDARY_FONT_WEIGHT',
        'DIM_SECONDARY_FONT_STYLE',
        'DIM_SECONDARY_FONT_COLOR',
        'DIM_SECONDARY_TEXT_SIZE',
        'DIM_SECONDARY_TEXT_ANGLE',
        'DIM_SECONDARY_TEXT_ALIGNMENT',
        'DIM_SECONDARY_PREFIX',
        'DIM_SECONDARY_SUFFIX',
        'DIM_SECONDARY_PRECISION',
        'DIM_SECONDARY_UNITS',
        'DIM_SECONDARY_LEADING_ZERO',
        'DIM_SECONDARY_TRAILING_DECIMAL',
        'DIM_OFFSET',
        'DIM_EXTENSION',
        'DIM_COLOR',
        'DIM_THICKNESS',
        'DIM_POSITION',
        'DIM_POSITION_OFFSET',
        'DIM_ENDPOINT',
        'DIM_ENDPOINT_SIZE',
        'DIM_DUAL_MODE',
        'DIM_DUAL_MODE_OFFSET',
        'RADIAL_DIM_PRIMARY_PREFIX',
        'RADIAL_DIM_PRIMARY_SUFFIX',
        'RADIAL_DIM_SECONDARY_PREFIX',
        'RADIAL_DIM_SECONDARY_SUFFIX',
        'RADIAL_DIM_DIA_MODE',
        'ANGULAR_DIM_PRIMARY_PREFIX',
        'ANGULAR_DIM_PRIMARY_SUFFIX',
        'ANGULAR_DIM_SECONDARY_PREFIX',
        'ANGULAR_DIM_SECONDARY_SUFFIX'
        ]
        
    __messages = {
        'scale_changed' : True,
        'units_changed' : True,
        'tool_changed' : True,
        'added_object' : True,
        'deleted_object' : True,
        'selected_object' : True,
        'deselected_object' : True,
        'active_layer_changed' : True,
        'current_point_changed' : True,
        'group_action_started' : True,
        'group_action_ended' : True,
        'option_changed' : True
        }
    def __init__(self, **kw):
        """
            Instatiate a Image object.
            There are no parameters used to create the object.
        """
        super(Image, self).__init__(**kw)
        self.__scale = 1.0
        self.__cp = None
        self.__styles = []
        self.__dimstyles = []
        self.__textstyles = []
        self.__linetypes = []
        self.__colors = baseobject.TypedDict(keytype=color.Color)
        self.__units = units.Unit(units.MILLIMETERS)
        self.__options = baseobject.TypedDict(keytype=str) # miscellaneous options
        self.__fonts = baseobject.TypedDict(keytype=types.StringTypes) # font names
        self.__tool = None
        self.__selected = []
        self.__filename = tempfile.mkdtemp(suffix='_temp', prefix='PyCad_')
        self.__vars = {}
        self.__busy = False
        self.__undo = []
        self.__redo = []
        self.__delhist = {}
        self.__logs = {}
        self.__action = 0L
        self.__closing = False
        #
        # add the initial layer
        #
        _top = layer.Layer(_(u'TopLayer'))
        _top.setParent(self)
        self.__top_layer = _top
        self.__active_layer = _top
        _top.connect('modified', self.__objectModified)
        _top.connect('added_child', self.__layerAddedChild)
        _top.connect('removed_child', self.__layerRemovedChild)
        _log = layer.LayerLog(_top)
        _top.setLog(_log)
        self.setDefaults()
        self.connect('modified', self.__objectModified)
        self.__vars['image'] = self
        #
        # Snap Obj
        #
        self.__snapProvider=snap.SnapServices(self) 
        #
        #file status
        #
        self.__saved=False

    def isSaved(self):
        """
            Sai if the file is saved
        """
        return self.__saved
    def setSaved(self):
        """
            force the file to be saved
        """
        self.__saved=True
    def setUnsaved(self):
        """
            force the file to be unsaved
        """
        self.__saved=False
    def save(self,filename=None):
        if filename==None:
            filename=self.__filename
        _abs = os.path.abspath(filename)
        _bname = os.path.basename(_abs)
        if _bname.endswith('.gz'):
            _bname = _bname[:-3]
        _newfile = _abs + '.new'
        _handle = fileio.CompFile(_newfile, "w", truename=_bname)
        try:
            imageio.save_image(self, _handle)
        finally:
            _handle.close()
            self.setSaved()
        _backup = _abs + '~'
        if os.path.exists(_backup):
            os.unlink(_backup)
        _mode = None
        if os.path.exists(_abs):
            _st = os.stat(_abs)
            _mode = stat.S_IMODE(_st.st_mode)
            os.rename(_abs, _backup)
        try:
            os.rename(_newfile, _abs)
        except:
            os.rename(_backup, _abs)
            raise
        if _mode is not None and hasattr(os, 'chmod'):
            os.chmod(_abs, _mode)
        if self.getFilename() is None:
            self.setFilename(_abs)
#
# Snap method
#
    def getSnapProvider(self):
        """
            Return the snap Provider
        """
        return self.__snapProvider
#
# Snap Property
#
    snapProvider=property(getSnapProvider,None,None,"Provide the SnapServicesObject for snap operations")
    
    def __contains__(self, obj):
        """
            Define if an object is in the Drawing.
            Defining this method allows the use of 'in' type test.
        """
        _res = False
        if isinstance(obj, style.Style):
            _res = obj in self.__styles
        elif isinstance(obj, linetype.Linetype):
            _res = obj in self.__linetypes
        elif isinstance(obj, color.Color):
            _res = obj in self.__colors
        elif isinstance(obj, dimension.DimStyle):
            _res = obj in self.__dimstyles
        elif isinstance(obj, text.TextStyle):
            _res = obj in self.__textstyles
        else:
            _layers = [self.__top_layer]
            while (len(_layers)):
                _layer = _layers.pop()
                _res = obj in _layer
                if _res:
                    break
                _layers.extend(_layer.getSublayers())
        return _res

    def close(self):
        """Release all the entities stored in the drawing

close()
        """
        # print "in image::close()"
        self.__cp = None
        del self.__styles[:]
        del self.__dimstyles[:]
        del self.__textstyles[:]
        del self.__linetypes[:]
        self.__colors.clear()
        self.__options.clear()
        self.__fonts.clear()
        del self.__selected[:]
        self.__filename = None
        self.__vars.clear()
        del self.__undo[:]
        del self.__redo[:]
        self.__delhist.clear()
        self.__logs.clear()
        self.__closing = True
        _top = self.__top_layer
        _layers = []
        _sublayers = [_top]
        while len(_sublayers):
            _layer = _sublayers.pop()
            _layers.append(_layer)
            _sublayers.extend(_layer.getSublayers())
        _layers.reverse()
        for _layer in _layers:
            # print "closing layer " + _layer.getName()
            _layer.clear()
            self.delLayer(_layer)
            _layer.finish()
        self.disconnect(self)

    def addChildLayer(self, l, p=None):
        """
            Add a child Layer of the active Layer.
            There is a one required argument
            l: The child Layer
            There is one optional argument:
            p: The new parent Layer of the child
            The default parent is the currently active layer.
            The child layer cannot be a layer found when moving
            up from the new parent layer to the topmost layer.
        """
        _child = l
        if not isinstance(_child, layer.Layer):
            raise TypeError, "Unexpected type for layer: " + `type(_child)`
        _pl = p
        if _pl is None:
            _pl = self.__active_layer
        if not isinstance(_pl, layer.Layer):
            raise TypeError, "Unexpected type for parent layer: " + `type(_pl)`
        if _pl.getParent() is not self:
            raise ValueError, "Parent layer not in Image."
        if _child is _pl:
            raise ValueError, "Child and parent layers identical."
        _tpl = _pl.getParentLayer()
        while _tpl is not None:
            if _tpl is _child:
                raise ValueError, "Child layer found in parent chain"
            _tpl = _tpl.getParentLayer()
        if not self.inUndo():
            self.ignore('modified')
        try:
            _child.setParentLayer(_pl)
        finally:
            if not self.inUndo():
                self.receive('modified')
        if _child.getParent() is not self:
            _child.setParent(self)
        #
        # restore the Layer log if possible
        #
        _cid = _child.getID()
        _log = _child.getLog()
        if _log is None:
            _log = layer.LayerLog(_child)
            _child.setLog(_log)
        _oldlog = self.__logs.get(_cid)
        if _oldlog is not None: # re-attach old log
            _log.transferData(_oldlog)
            del self.__logs[_cid]
        #
        # re-add deleted entity history
        #
        _data = self.__delhist.get(_cid)
        if _data is not None:
            _child.setDeletedEntityData(_data)
            del self.__delhist[_cid]
        _child.connect('modified', self.__objectModified)
        _child.connect('added_child', self.__layerAddedChild)
        _child.connect('removed_child', self.__layerRemovedChild)
        self.__active_layer = _child

    def addLayer(self, l):
        """
            Add a new Layer as a child of the active Layer's parent.
            If the active layer is the topmost Layer in the drawing, the Layer
            is added as a child Layer to that Layer. Otherwise, the new layer
            is added and is a sibling to the active Layer.
        """

        if not isinstance(l, layer.Layer):
            raise TypeError, "Invalid Layer type: " + `type(l)`
        _pl = self.__active_layer.getParentLayer()
        if _pl is None:
            _pl = self.__top_layer
        self.addChildLayer(l, _pl)

    def delLayer(self, l):
        """Remove a Layer from the drawing.

delLayer(l)

A Layer object cannot be removed until its children are
either deleted or moved to another Layer.

The topmost Layer in a drawing cannot be deleted.
        """
        _layer = l
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Invalid Layer type: " + `type(_layer)`
        if _layer.getParent() is not self:
            raise ValueError, "Layer not found in Image: " + _layer.getName()
        
        if (self.__closing or
            (_layer.getParentLayer() is not None and
             not _layer.hasSublayers())):
            if not self.__closing:
                # print "deleting layer ..."
                _lid = _layer.getID()
                _data = _layer.getDeletedEntityData()
                #
                # save the layer info so it can be reattched if
                # the layer deletion is undone
                #
                if len(_data):
                    # print "has DeletedEntityData()"
                    self.__delhist[_lid] = _data
            _log = _layer.getLog()
            if _log is not None:
                # print "Saving log file ..."
                _log.detatch()
                if not self.__closing:
                    self.__logs[_lid] = _log
                _layer.setLog(None)
            #
            # stop listening for messages
            #
            _layer.disconnect(self)
            #
            # call setParent() before setParentLayer() so
            # the Layer's getValues() calls will have
            # the parent layer information
            #
            _layer.setParent(None)
            if not self.inUndo():
                self.ignore('modified')
            try:
                _layer.setParentLayer(None)
            finally:
                if not self.inUndo():
                    self.receive('modified')

    def hasLayer(self, l):
        """Return whether or not a layer is in a drawing.

hasLayer(l)
        """
        _layer = l
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Invalid Layer type : " + `type(_layer)`
        _flag = False
        _l = _layer
        _p = _l.getParentLayer()
        while _p is not None:
            _l = _p
            _p = _p.getParentLayer()
        if _l is self.__top_layer:
            _flag = True
        _image = _layer.getParent()
        if ((_image is self and _flag is False) or
            (_image is not self and _flag is True)):
            raise ValueError, "Image/Layer parent inconsistency"
        return _flag

    def getActiveLayer(self):
        """
            Return the active Layer in the drawing.
            The active Layer is the Layer to which any new objects will
            be stored.
        """
        return self.__active_layer

    def setActiveLayer(self, l=None):
        """Set the active Layer in the Image.

setActiveLayer(l)

The the Layer 'l' to be the active Layer in the drawing. If
the function is called without arguments, the topmost Layer
in the drawing is set to the active layer.
        """
        _layer = l
        if _layer is None:
            _layer = self.__top_layer
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Invalid Layer type: " + `type(_layer)`
        if _layer is not self.__top_layer:
            _l = _layer
            _p = _l.getParentLayer()
            while _p is not None:
                _l = _p
                _p = _p.getParentLayer()
            if _l is not self.__top_layer:
                raise ValueError, "Layer not found in image: " + `_layer`
            _parent = _layer.getParentLayer()
            if not _parent.hasSublayers():
                raise ValueError, "Layer not in parent sublayer: " + `_layer`
            if _layer not in _parent.getSublayers():
                raise ValueError, "Layer not in parent sublayers: " + `_layer`
            if _layer.getParent() is not self:
                raise ValueError, "Image/Layer parent inconsistency"
        _active = self.__active_layer
        if _layer is not _active:
            self.__active_layer = _layer
            self.sendMessage('active_layer_changed', _active)

    active_layer = property(getActiveLayer, setActiveLayer,
                            None, "Image active Layer object.")

    def getTopLayer(self):
        """Return the top Layer of the image

getTopLayer()
        """
        return self.__top_layer

    top_layer = property(getTopLayer, None, None, "Image top Layer.")

    def getScale(self):
        """Return the image's scale factor.

getScale()
        """
        return self.__scale

    def setScale(self, scale):
        """Set the image's scale factor.

setScale(scale)

The scale must be a float greater than 0.
        """
        _s = util.get_float(scale)
        if _s < 1e-10:
            raise ValueError, "Invalid scale factor: %g" % _s
        _os = self.__scale
        if abs(_os - _s) > 1e-10:
            self.__scale = _s
            self.sendMessage('scale_changed', _os)
            self.modified()

    scale = property(getScale, setScale, None, "Image scale factor.")

    def canParent(self, obj):
        """Test if an Entity can be the parent of another Entity.

canParent(obj)

This method overrides the Entity::canParent() method. An Image can
be the parent of Layer entities only.
        """
        return isinstance(obj, layer.Layer)

    def getImageEntities(self, entity):
        """Return all the entities of a particular type

getImageEntities(entity)

The argument 'entity' should be one of the following:
color, linetype, style, font, dimstyle, or textstyle
        """
        if entity == "color":
            _objs = self.__colors.keys()
        elif entity == "linetype":
            _objs = self.__linetypes[:]
        elif entity == "style":
            _objs = self.__styles[:]
        elif entity == "font":
            _objs = self.__fonts.keys()
        elif entity == "dimstyle":
            _objs = self.__dimstyles[:]
        elif entity == "textstyle":
            _objs = self.__textstyles[:]
        else:
            raise ValueError, "Invalid image entity: " + `entity`
        return _objs

    def addColor(self, c):
        """Add a Color object to the drawing.

addColor(c)
        """
        if not isinstance(c, color.Color):
            raise TypeError, "Invalid Color type: " + `type(c)`
        if c not in self.__colors:
            self.__colors[c] = True # maybe count entities ?

    def hasColor(self, c):
        """Check if a Color already exists in the drawing.

hasColor(c)
        """
        _c = c
        if not isinstance(_c, color.Color):
            _c = color.Color(c)
        return _c in self.__colors

    def addLinetype(self, lt):
        """Add a Linetype to the drawing.

addLinetype(lt)
        """
        if not isinstance(lt, linetype.Linetype):
            raise TypeError, "Invalid Linetype type: " + `type(lt)`
        if lt not in self.__linetypes:
            self.__linetypes.append(lt)

    def hasLinetype(self, lt):
        """Check if a Linetype already exists in the drawing.

hasLinetype(lt)
        """
        if not isinstance(lt, linetype.Linetype):
            raise TypeError, "Invalid Linetype type: " + `type(lt)`
        return lt in self.__linetypes

    def addStyle(self, s):
        """Add a Style to the drawing.

addStyle(s)
        """
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid Style type: " + `type(s)`
        if s not in self.__styles:
            _col = s.getColor()
            if _col not in self.__colors:
                self.__colors[_col] = True
            _lt = s.getLinetype()
            if _lt not in self.__linetypes:
                self.__linetypes.append(_lt)
            self.__styles.append(s)

    def hasStyle(self, s):
        """Check if a Style already exists within the drawing.

hasStyle(s)
        """
        _s = s
        if not isinstance(_s, style.Style):
            _s = style.Style(s)
        return _s in self.__styles

    def addDimStyle(self, ds):
        """Add a DimStyle to the drawing

addDimStyle(ds)
        """
        if not isinstance(ds, dimension.DimStyle):
            raise TypeError, "Invalid DimStyle type: " + `type(ds)`
        if ds not in self.__dimstyles:
            _col = ds.getValue('DIM_COLOR')
            if _col is not None and _col not in self.__colors:
                self.__colors[_col] = True
            _col = ds.getValue('DIM_PRIMARY_FONT_COLOR')
            if _col is not None and _col not in self.__colors:
                self.__colors[_col] = True
            _col = ds.getValue('DIM_SECONDARY_FONT_COLOR')
            if _col is not None and _col not in self.__colors:
                self.__colors[_col] = True
            _family = ds.getValue('DIM_PRIMARY_FONT_FAMILY')
            if _family is not None and _family not in self.__fonts:
                self.__fonts[_family] = 1
            _family = ds.getValue('DIM_SECONDARY_FONT_FAMILY')
            if _family is not None and _family not in self.__fonts:
                self.__fonts[_family] = 1
            self.__dimstyles.append(ds)

    def hasDimStyle(self, ds):
        """Check if a DimStyle already exists within the drawing.

hasDimStyle(ds)
        """
        if not isinstance(ds, dimension.DimStyle):
            raise TypeError, "Invalid DimStyle type: " + `type(ds)`
        return ds in self.__dimstyles

    def addTextStyle(self, ts):
        """Add a TextStyle to the drawing.

addTextStyle(ts)
        """
        # print "Image::addTextStyle() ..."
        if not isinstance(ts, text.TextStyle):
            raise TypeError, "Invalid TextStyle type: " + `type(ts)`
        if ts not in self.__textstyles:
            # print "adding TextStyle: %s" % ts.getName()
            _color = ts.getColor()
            if _color not in self.__colors:
                self.__colors[_color] = True
            _family = ts.getFamily()
            if _family in self.__fonts:
                self.__fonts[_family] = 1
            self.__textstyles.append(ts)

    def hasTextStyle(self, ts):
        """Return whether or not a TextStyle is already in an image.

hasTextStyle(ts)
        """
        if not isinstance(ts, text.TextStyle):
            raise TypeError, "Invalid TextStyle: " + str(ts)
        return ts in self.__textstyles

    def addFont(self, family):
        """Store the usage of a font in the image.

addFont(family)

Invoking this method does not set the current text font to
the value used in this function. That must be done with setOption().
        """
        if not isinstance(family, types.StringTypes):
            raise TypeError, "Invalid font family type: " + `type(family)`
        self.__fonts[family] = 1

    def getUnits(self):
        """Return the currently selected unit.

getUnits()
        """
        return self.__units.getUnit()

    def setUnits(self, unit):
        """Set the basic unit for the image.

setUnits(unit)

The available choices for the units are defined in the units.py file.
        """
        _ou = self.__units.getUnit()
        self.__units.setUnit(unit)
        if unit != _ou:
            self.sendMessage('units_changed', _ou)
            self.modified()

    units = property(getUnits, setUnits, None,
                     "Linear dimensional units for the image.")

    def scaleLength(self, l):
        """Convert some distance to a value in millimeters.

scaleLength(l)

The argument 'l' should be a float equal or greater than 0.0.
        """
        _l = util.get_float(l)
        if _l < 0.0:
            raise ValueError, "Invalid scaling length: %g" % _l
        return self.__units.toMillimeters(_l)

    def getClosestPoint(self, x, y, **kw):
        """
            Return a Point or (x, y) coordinate tuple in the Image.

            getClosestPoint(self, x, y [,**kw])

            The function has two required arguments

            x: A float representing the x-coordinate
            y: A float representing the y-coordinate

            The accepted keyword arguements are:

            tolerance: The distance between the existing objects and the 'x'
                       and 'y' arguments. The default value is 1e-10.

            This method returns a tuple of two values, one of which
            will be None. If an existing Point was found in the active
            layer, the first value in the tuple is the point, and the
            second value is None. If no point was found, the first
            value will be None and the second value will be a tuple
            of (x, y) coordinates where a new Point could be created.
            When the method returns the coordinate tuple, the location
            could be a projected point onto an Entity found in the Layer,
            or possibly the intersection of two or more entities, or
            simply a distinct point in the Layer if no nearby entities
            were found.
        """
        raise "Function getClosestPoint banned " 
        _t=5.0
        if 'tolerance' in kw:
            _t=util.get_float(kw['tolerance'])
        _sobj=self.GetSnapObject()
        _ix, _iy,validate,cursor=_sobj.GetSnap(x,y,_t,None)
        _sobj.StopOneShutSnap()
        if(validate):
            return (_ix, _iy)     
        return (x, y)
    def findPoint(self, x, y, tol=tolerance.TOL):
        """Return a Point object found at the x-y coordinates.

findPoint(self, x, y [,tol])

The function has two required arguments

x: A float representing the x-coordinate
y: A float representing the y-coordinate

The optional argument 'tol' gives a distance between the
existing objects and the 'x' and 'y' arguments. The default
value is 1e-10.

This method returns a tuple of two objects, the first
object is a Point object, and the second object is a
boolean True/False value indicating if the point is an
exisiting point in the active layer or a newly created
point.

If there were no Point objects found within the tolerance
supplied, the Point object in the tuple is None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _test_point = point.Point(_x, _y)
        _active_layer = self.__active_layer
        _new_pt = False
        _pt = None
        _pts = _active_layer.find('point', _x, _y, _t)
        if len(_pts) != 0:
            _pt = _pts[0]
        if _pt is None:
            _objs = []
            _ptmap = {}
            _layers = [self.__top_layer]
            while len(_layers):
                _layer = _layers.pop()
                if _layer is not _active_layer:
                    _pts = _layer.find('point', _x, _y, _t)
                    if len(_pts) != 0:
                        _pt = _pts[0].clone()
                        _new_pt = True
                        break
                _stop = False
                for _obj, _map_pt in _layer.mapPoint(_test_point, _t, None):
                    if isinstance(_obj, dimension.Dimension):
                        continue
                    if len(_objs):
                        for _tobj in _objs:
                            _ints = intersections.find_intersections(_tobj, _obj)
                            _count = len(_ints)
                            if _count == 1:
                                _stop = True
                                _x, _y = _ints[0]
                                _pt = point.Point(_x, _y)
                                _new_pt = True
                                break
                            elif _count == 2:
                                _stop = True
                                _tx, _ty = _test_point.getCoords()
                                _x1, _y1 = _ints[0]
                                _d1 = math.hypot((_tx - _x1), (_ty - _y1))
                                _x2, _y2 = _ints[1]
                                _d2 = math.hypot((_tx - _x2), (_ty - _y2))
                                if _d1 < _d2:
                                    _pt = point.Point(_x1, _y1)
                                else:
                                    _pt = point.Point(_x2, _y2)
                                _new_pt = True
                                break
                            else:
                                pass # this should handle _count > 2
                    _ptmap[_obj] = _map_pt
                    _objs.append(_obj)
                if _stop:
                    break
                _layers.extend(_layer.getSublayers())
            if _pt is None: # need to use one of the mapped points ...
                _min_sep = None
                _map_obj = None
                for _obj in _ptmap:
                    _sep = _ptmap[_obj] - _test_point
                    if _min_sep is None or _sep < _min_sep:
                        _map_obj = _obj
                if _map_obj is not None:
                    _pt = _ptmap[_map_obj]
                    _new_pt = True
        return _pt, _new_pt

    def mapCoords(self, x, y, tol, count=None):
        """Return a set of Layers with objects found at the (x, y) location

mapCoords(self, x, y, tol[, count])

This method has three required arguments:

x: A float representing the x-coordinate
y: A float representing the y-coordinate
tol: A positive float giving the maximum distance between the
     x and y coordinates and the projected points of the objects

There is a single optional argument:

count: An integer value specifying the maximum number of objects to
       retrieve in any layer. By default the limit is the 'sys.maxint'
       value, essentially making the count unlimited.

The function returns a list of tuples, where each tuple
is of the form (layer, list). The 'list' in the tuple
is itself a list of tuples consiting of an entity and either
an existing Point in the layer or an x/y coordinate pair.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _count = count
        if _count is None:
            _count = sys.maxint
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 0:
            raise ValueError, "Invalid negative entity count: %d" % _count
        _objlist = []
        if _count == 0:
            return _objlist
        _active_layer = self.__active_layer
        _hits = _active_layer.mapCoords(_x, _y, tolerance=_t, count=_count)
        if len(_hits):
            _objlist.append((_active_layer, _hits))
        else:
            _layers = [self.__top_layer]
            while len(_layers):
                _layer = _layers.pop()
                if _layer is not _active_layer:
                    _hits = _layer.mapCoords(_x, _y, tolerance=_t, count=_count)
                    if len(_hits):
                        _objlist.append((_layer, _hits))
                _layers.extend(_layer.getSublayers())
        return _objlist

    def mapPoint(self, x, y, tol, count=2):
        """Return a set of Layers with objects found at the (x,y) location

mapPoint(self, x, y, tol[, count])

This method has three required arguments:

x: A float representing the x-coordinate
y: A float representing the y-coordinate
tol: A positive float giving the maximum distance between the
     x and y coordinates and the projected points of the objects

There is a single optional argument:

count: The maximum number of objects to retrieve in any layer. The
       default value of objects is 2.

Setting 'count' to either None or a negative value will result
in the maximum number of objects as unlimited.

The function returns a dict object, with each key being
a Layer object where some objects were found, and the
value being a list of some tuples. Read the doc-string
info for the layer::mapPoint() method for details regarding
the tuple(s) in the list.

If any objects in the currently active layer are identified, no
other layers in the drawing will be examined.

If there were no objects found within the tolerance
supplied, the function returns an empty dict.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _count = count
        if _count is None:
            _count = sys.maxint
        else:
            if not isinstance(_count, int):
                _count = int(count)
            if _count < 0: # What if _count == 0 ???
                _count = sys.maxint
        _tp = point.Point(_x, _y)
        _active_layer = self.__active_layer
        _objdict = {}
        _hits = _active_layer.mapPoint(_tp, _t, _count)
        if len(_hits):
            _objdict[_active_layer] = _hits
        else:
            _layers = [self.__top_layer]
            while len(_layers):
                _layer = _layers.pop()
                if _layer is not _active_layer:
                    _hits = _layer.mapPoint(_tp, _t, _count)
                    if len(_hits):
                        _objdict[_layer] = _hits
                _layers.extend(_layer.getSublayers())
        return _objdict

    def getCurrentPoint(self):
        """Get the current point defined for the Image.

getCurrentPoint()

This method returns a tuple containing two floats, or None if the point
has not been defined
        """
        return self.__cp

    def setCurrentPoint(self, x, y):
        """Set the current point.

setCurrentPoint(x, y)

Arguments 'x' and 'y' should be floats
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        if self.__cp is not None:
            _cx, _cy = self.__cp
        if self.__cp is None or abs(_cx - _x) > 1e-10 or abs(_cy - _y) > 1e-10:
            self.__cp = (_x, _y)
            self.sendMessage('current_point_changed')

    current_point = property(getCurrentPoint, None, None, 'Current point')
        
    def __objectModified(self, obj, *args):
        # print "Image::objectModified()"
        # print "obj: " + `obj`
        if self.__closing:
            return
        if obj.inUndo():
            raise RuntimeError, "Recieved 'modified' during undo: " + `obj`
        _oid = obj.getID()
        _pid = None
        _parent = obj.getParent()
        if _parent is None:
            if obj is not self:
                raise ValueError, "Invalid object without parent: " + `obj`
        else:
            _pid = _parent.getID()
            if _parent is self:
                if not isinstance(obj, layer.Layer):
                    raise ValueError, "Non-layer with Image as parent: " + `obj`
            else:
                _layer = None
                for _child in self.getChildren():
                    _cid = _child.getID()
                    if _cid == _pid:
                        _layer = _child
                        break
                if _layer is None:
                    raise ValueError, "Parent %d not in Image children: %s" % (_pid,  `_parent`)
                _lobj = _layer.getObject(_oid)
                if _lobj is not obj:
                    raise ValueError, "Object %d not found in Layer: %s" % (_oid, `obj`)
        _i = self.__action
        # print "i: %d" % _i
        _undo = self.__undo
        # print "len(self.__undo): %d" % len(_undo)
        if len(_undo) == _i:
            _undo.insert(_i, [(_pid, _oid)])
        else:
            _undo[_i].append((_pid, _oid))
        if not self.__busy:
            self.__action = _i + 1

    def __layerAddedChild(self, l, *args):
        # print "Image::layerAddedChild() ..."
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        # print "obj: " + `_obj`
        _obj.connect('modified', self.__objectModified)
        if isinstance(_obj, graphicobject.GraphicObject):
            self.addStyle(_obj.getStyle())
            self.addLinetype(_obj.getLinetype())
            self.addColor(_obj.getColor())
            _obj.connect('style_changed', self.__styleChanged)
            _obj.connect('color_changed', self.__colorChanged)
            _obj.connect('linetype_changed', self.__linetypeChanged)
        if isinstance(_obj, text.TextBlock):
            self.addColor(_obj.getColor())
            self.addTextStyle(_obj.getTextStyle())
            _obj.connect('font_color_changed', self.__colorChanged)
            _obj.connect('textstyle_changed', self.__textstyleChanged)
        if isinstance(_obj, dimension.Dimension):
            self.addDimStyle(_obj.getDimStyle())
            self.addColor(_obj.getColor())
            _obj.connect('dimstyle_changed', self.__dimstyleChanged)
            _obj.connect('color_changed', self.__colorChanged)
            _ds1, _ds2 = _obj.getDimstrings()
            self.addColor(_ds1.getColor())
            self.addTextStyle(_ds1.getTextStyle())
            _ds1.connect('font_color_changed', self.__colorChanged)
            _ds1.connect('textstyle_changed', self.__textstyleChanged)
            self.addColor(_ds2.getColor())
            self.addTextStyle(_ds2.getTextStyle())
            _ds2.connect('font_color_changed', self.__colorChanged)
            _ds2.connect('textstyle_changed', self.__textstyleChanged)
        self.sendMessage('added_object', l, _obj)
        #
        # If a Point was added set the Layer to the global AUTOSPLIT
        # option value unless the Layer has autosplitting set
        # 
        if isinstance(_obj, point.Point) and l.getAutosplit():
            l.setAutosplit(self.getOption('AUTOSPLIT'))

    def __layerRemovedChild(self, l, *args):
        # print "Image::layerRemovedChild() ..."
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        # print "obj: " + `_obj`
        _obj.disconnect(self)
        if isinstance(_obj, dimension.Dimension):
            _ds1, _ds2 = _obj.getDimstrings()
            _ds1.disconnect(self)
            _ds2.disconnect(self)
        _objs = self.__selected
        for _i in range(len(_objs)):
            if _obj is _objs[_i]:
                del _objs[_i]
                break
        self.sendMessage('deleted_object', l, _obj)

    def __styleChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        self.addStyle(obj.getStyle())

    def __colorChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        self.addColor(obj.getColor())

    def __linetypeChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        self.addLinetype(obj.getLinetype())

    def __textstyleChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        self.addTextStyle(obj.getTextstyle())

    def __dimstyleChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        self.addDimStyle(obj.getDimStyle())

    def printStack(self, undo):
        if undo:
            print "Image undo list:"
            _stack = self.__undo
        else:
            print "Image redo list:"
            _stack = self.__redo
        print "length: %d" % len(_stack)
        for _data in _stack:
            print _data

    def canUndo(self):
        return len(self.__undo) > 0

    def canRedo(self):
        return len(self.__redo) > 0

    def doUndo(self):
        # print "Image::doUndo() ..."
        if len(self.__undo):
            _act = self.__undo.pop()
            # print "Actions: " + str(_act)
            # print "undo length: %d" % len(self.__undo)
            self.__redo.append(_act[:])
            self.__action = len(self.__undo)
            _act.reverse()
            self.ignore('modified')
            self.sendMessage('group_action_started')
            try:
                _sid = self.getID()
                _layers = {}
                for _pid, _oid in _act:
                    # print "pid: " + str(_pid)
                    # print "oid: %d" % _oid
                    _obj = None
                    if _pid is None:
                        if _oid != _sid:
                            raise ValueError, "Invalid orphan: %d" % _oid
                        _obj = self
                    if _obj is None and _pid == _sid:
                        _obj = _layers.get(_oid)
                        if _obj is None:
                            for _layer in self.getChildren():
                                _lid = _layer.getID()
                                _layers[_lid] = _layer
                                if _lid == _oid:
                                    _obj = _layer
                                    break
                        if _obj is None:
                            raise ValueError, "Layer %d not found in Image" % _oid
                    if _obj is None:
                        _par = _layers.get(_pid)
                        if _par is None:
                            for _layer in self.getChildren():
                                _lid = _layer.getID()
                                _layers[_lid] = _layer
                                if _lid == _pid:
                                    _par = _layer
                                    break
                        if _par is None:
                            raise ValueError, "Parent layer not found: %d" % _pid
                        _obj = _par.getObject(_oid)
                        if _obj is None:
                            raise ValueError, "Object %d not found in parent %d" % (_oid, _pid)
                    # print "executing undo on obj: " + `_obj`
                    _obj.undo()
            finally:
                self.sendMessage('group_action_ended')
                self.receive('modified')

    def doRedo(self):
        # print "Image::doRedo() ..."
        if len(self.__redo):
            _act = self.__redo.pop()
            self.__action = len(self.__undo)
            #
            # wrap all the redo() actions within a
            # startAction()/endAction block - this will
            # ensure that all the 'modified' messages the
            # redo operations generate will be stored in
            # in the undo list as a single set of operations
            #
            self.startAction()
            try:
                _sid = self.getID()
                _layers = {}
                for _pid, _oid in _act:
                    _obj = None
                    if _pid is None:
                        if _oid != _sid:
                            raise ValueError, "Invalid orphan: %d" % _oid
                        _obj = self
                    if _obj is None and _pid == _sid:
                        _obj = _layers.get(_oid)
                        if _obj is None:
                            for _layer in self.getChildren():
                                _lid = _layer.getID()
                                _layers[_lid] = _layer
                                if _lid == _oid:
                                    _obj = _layer
                                    break
                        if _obj is None:
                            raise ValueError, "Layer %d not found in Image" % _oid
                    if _obj is None:
                        _par = _layers.get(_pid)
                        if _par is None:
                            for _layer in self.getChildren():
                                _lid = _layer.getID()
                                _layers[_lid] = _layer
                                if _lid == _pid:
                                    _par = _layer
                                    break
                        if _par is None:
                            raise ValueError, "Parent layer not found: %d" % _pid
                        _obj = _par.getObject(_oid)
                        if _obj is None:
                            raise ValueError, "Object %d not found in parent %d" % (_oid, _pid)
                    # print "executing redo on obj: " + `_obj`
                    _obj.redo()
            finally:
                self.endAction()

    def addObject(self, obj, l=None):
        """Add an object to the Drawing.

addObject(obj [, l])

Argument 'obj' is the entity to be added in the Image. Optional
arguement 'l' is the Layer that will contain the object. If no
layer is specfied then the object is placed in the active Layer.
        """
        _layer = l
        if _layer is None:
            _layer = self.__active_layer
        _op = obj.getParent()
        if _op is not None:
            raise RuntimeError, "Object already in layer '%s'" % _op.getName()
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Invalid Layer: " + `type(_layer)`
        if _layer.getParent() is not self:
            raise RuntimeError, "Layer not found in Image."
        _layer.setAutosplit(self.getOption('AUTOSPLIT'))
        _layer.addObject(obj)

    def delObject(self, obj):
        """Remove an object from the Drawing.

delObject(obj)

Argument 'obj' must be an object stored in a Layer in the Image.
        """
        _layer = obj.getParent()
        if _layer is None:
            raise RuntimeError, "Object not stored within a Layer."
        if _layer.getParent() is not self:
            raise RuntimeError, "Object parent Layer not found in Image."
        _layer.delObject(obj)

    def getObject(self, eid):
        """Retrieve an object with a specified ID.

getObject(eid)

Argument eid is an entity ID. If an object with an ID of
that specified is found, the object is returned. Otherwise
this method returns None.
        """
        _layers = [self.__top_layer]
        while len(_layers):
            _layer = _layers.pop()
            if _layer.getID() == eid:
                return _layer
            _obj = _layer.getObject(eid)
            if _obj is not None:
                return _obj
            _layers.extend(_layer.getSublayers())
        return None

    def startAction(self):
        """Set the Image to the point starting a sequence of operations.

startAction()

This method is called in conjunction with endAction() to store a sequence
of operations on an Image as a single operation for undo/redo purposes.
        """
        if self.__busy:
            raise ValueError, "Image already in busy state"
        self.__busy = True
        self.sendMessage('group_action_started')

    def endAction(self):
        """
            Set the Image to the point completing a sequence of operations.
            This method is called in conjunction with startAction() to store a sequence
            of operations on an Image as a single operation for undo/redo purposes.
        """
        if not self.__busy:
            raise ValueError, "Image not in busy state"
        self.__busy = False
        self.__action = len(self.__undo)
        self.sendMessage('group_action_ended')

    def inAction(self):
        """Test if the Image is with a startAction()/endAction() operation.

inAction()

This method returns a boolean.
        """
        return self.__busy

    def getAction(self):
        return self.__action

    action = property(getAction, None, None, "Action value.")

    def selectObject(self, obj):
        """Store a reference to an object in the Image.

selectObject(obj)

The argument 'obj' is one of the objects stored in the Image.
Storing an object with selectObject() is the means by which
objects can be copied or modified.
        """
        _parent = obj.getParent()
        if _parent is None:
            raise ValueError, "Object has no parent: " + `obj`
        if not isinstance(_parent, layer.Layer):
            raise TypeError, "Invalid object parent: " + `type(_parent)`
        if _parent.getParent() is not self:
            raise ValueError, "Object not in Image: " + `obj`
        _seen = False
        for _obj in self.__selected:
            if _obj is obj:
                _seen = True
                break
        if not _seen:
            self.__selected.append(obj)
            self.sendMessage('selected_object', obj)

    def deselectObject(self, obj):
        """Remove any occurance of an object in the Image.

deselectObject(obj)

If the object is not already selected a ValueError is returned.
        """
        _parent = obj.getParent()
        if _parent is None:
            raise ValueError, "Object has no parent: " + `obj`
        if not isinstance(_parent, layer.Layer):
            raise TypeError, "Invalid object parent: " + `type(_parent)`
        if _parent.getParent() is not self:
            raise ValueError, "Object not in Image: " + `obj`
        _objs = self.__selected
        for _i in range(len(_objs)):
            if _objs[_i] is obj:
                del _objs[_i]
                self.sendMessage('deselected_object', obj)
                break

    def getSelectedObjects(self, delete=True):
        """Return all the currently selected objects.

getSelectedObjects([delete])

Optional argument 'delete' defaults to True, so calling this method
with no arguments will deselected all the selected objects. If the
argument is False, the selected entities remain stored.
        """
        util.test_boolean(delete)
        _objs = self.__selected[:]
        if delete:
            self.clearSelectedObjects()
        return _objs

    def clearSelectedObjects(self):
        """Empty the list list of selected objects.

clearSelectedObjects()
        """
        for _obj in self.__selected:
            self.sendMessage('deselected_object', _obj)
        del self.__selected[:]

    def hasSelection(self):
        """Return whether or not there are selected objects in the drawing.

hasSelection()
        """
        return len(self.__selected) > 0

    def getImageVariables(self):
        """Get the dictionary storing the variables local to the image.

getImageVariables()
        """
        return self.__vars
    
    def getExtents(self):
        """Return the coordinates of a window holding the whole drawing

getExtents()

The function will return a tuple of the format:

(xmin, ymin, xmax, ymax)

Each value will be a float.
        """
        _xmin = None
        _ymin = None
        _xmax = None
        _ymax = None
        _set = False
        _layers = [self.__top_layer]
        while (len(_layers)):
            _layer = _layers.pop()
            if _layer.isVisible():
                _set = True
                _xmn, _ymn, _xmx, _ymx = _layer.getBoundary()
                if _xmin is None or _xmn < _xmin:
                    _xmin = _xmn
                if _ymin is None or _ymn < _ymin:
                    _ymin = _ymn
                if _xmax is None or _xmx > _xmax:
                    _xmax = _xmx
                if _ymax is None or _ymx > _ymax:
                    _ymax = _ymx
            _layers.extend(_layer.getSublayers())
        if _set: # make sure the values are different
            if abs(_xmax - _xmin) < 1e-10:
                _xmin = _xmin - 1.0
                _xmax = _xmax + 1.0
            if abs(_ymax - _ymin) < 1e-10:
                _ymin = _ymin - 1.0
                _ymax = _ymax + 1.0
        else:
            _xmin = -1.0
            _ymin = -1.0
            _xmax = 1.0
            _ymax = 1.0
        return (_xmin, _ymin, _xmax, _ymax)

    def getOptions(cls):
        """Return the list of options that can be set in an Image.

getOptions()

This method returns a list of strings.
        """
        return Image.__options[:]

    getOptions = classmethod(getOptions)
    
    def getOption(self, key):
        """Return the value of an option set in the drawing.

getOption(key)

Return the value of the option associated with the string 'key'.
If there is no option found for that key, return None.
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        if key not in Image.__options:
            raise ValueError, "Invalid option key: '%s'" % key
        return self.__options.get(key)


    def setOption(self, key, value):
        """Set an option in the drawing.

setOption(key, value)

Argument 'key' must be a string, and argument 'value' can
any type of object. Using the same key twice will result on
the second value overwriting the first.
        """
        #
        # testOption will raise a exceptions for invalid values ...
        #
        if not isinstance(key, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        options.OptionManager.testOption(key, value)
        if (key == 'LINE_COLOR' or
            key == 'FONT_COLOR' or
            key == 'BACKGROUND_COLOR' or
            key == 'INACTIVE_LAYER_COLOR' or
            key == 'SINGLE_POINT_COLOR' or
            key == 'MULTI_POINT_COLOR' or
            key == 'DIM_COLOR' or
            key == 'DIM_PRIMARY_FONT_COLOR' or
            key == 'DIM_SECONDARY_FONT_COLOR'):
            if value not in self.__colors:
                self.__colors[value] = True
        elif key == 'LINE_STYLE':
            self.setOption('LINE_COLOR', value.getColor())
            self.setOption('LINE_TYPE', value.getLinetype())
            self.setOption('LINE_THICKNESS', value.getThickness())
            if value not in self.__styles:
                self.__styles.append(value)
        elif key == 'LINE_TYPE':
            if value not in self.__linetypes:
                self.__linetypes.append(value)
        elif key == 'DIM_STYLE':
            for _opt in value.getOptions():
                _optval = value.getValue(_opt)
                self.setOption(_opt, _optval)
            if value not in self.__dimstyles:
                self.__dimstyles.append(value)
        elif key == 'TEXT_STYLE':
            self.setOption('FONT_COLOR', value.getColor())
            self.setOption('FONT_WEIGHT', value.getWeight())
            self.setOption('FONT_STYLE', value.getStyle())
            self.setOption('FONT_FAMILY',  value.getFamily())
            self.setOption('TEXT_SIZE', value.getSize())
            self.setOption('TEXT_ANGLE', value.getAngle())
            self.setOption('TEXT_ALIGNMENT', value.getAlignment())
            if value not in self.__textstyles:
                self.__textstyles.append(value)
        elif (key == 'FONT_FAMILY' or
              key == 'DIM_PRIMARY_FONT_FAMILY' or
              key == 'DIM_SECONDARY_FONT_FAMILY'):
            if value not in self.__fonts:
                self.__fonts[value] = True
        else:
            pass
        self.__options[key] = value
        self.sendMessage('option_changed', key, value)

    def setDefaults(self):
        """Set Image options to the current global settings.

setDefaults()
        """
        _gp = globals.prefs
        for _opt in Image.__options:
            self.setOption(_opt, _gp[_opt])
            
    def setFilename(self, fname):
        """
            Set the filename for this image.
            The filename will be where the system will save
            the data in this file.
        """
        self.__filename = fname

    def getFilename(self):
        """
            Return the filename for this image.
        """
        return self.__filename

    filename = property(getFilename, setFilename, None, "Image filename.")

    def setTool(self, tool=None):
        """
            Replace the Tool in the Image with a new Tool.
            The argument 'tool' should be an instance of a Tool object or 'None'.
        """
        if tool is not None and not isinstance(tool, tools.Tool):
            raise TypeError, "Invalid tool: " + `type(tool)`
        _ot = self.__tool
        self.setUnsaved() #each time i set a tool i make some modification 
        if (_ot is not tool):
            self.__tool = tool
            self.sendMessage('tool_changed')

    def getTool(self):
        """Return the current Tool used in the drawing.

getTool()
        """
        return self.__tool

    tool = property(getTool, setTool, None, "Tool for adding/modifying entities.")

    def sendsMessage(self, m):
        if m in Image.__messages:
            return True
        return super(Image, self).sendsMessage(m)

#
# provide some default colors, linetypes, and styles
# for an image
#

def add_defaults(image):
    #
    # standard styles
    #
    _sstyle = globals.prefs['STANDARD_STYLE']
    _dstyle = globals.prefs['DEFAULT_STYLE']
    _set_style = False
    for _style in globals.prefs['STYLES']:
        image.addStyle(_style)
        if _style.getName() == _dstyle.getName():
            image.setOption('LINE_STYLE', _style)
            _set_style = True
    if not _set_style:
        image.setOption('LINE_STYLE', _sstyle)
    #
    # standard colors
    #
    for _color in globals.prefs['COLORS']:
        image.addColor(_color)
    #
    # standard linetypes
    #
    for _linetype in globals.prefs['LINETYPES']:
        image.addLinetype(_linetype)
    #
    # standards styles
    #
    # solid = linetype.Linetype('Solid')
    # dash1 = linetype.Linetype('Dash1', [4,1])
    # dash2 = linetype.Linetype('Dash2', [8,2])
    # dash3 = linetype.Linetype('Dash3', [12,2])
    # dash4 = linetype.Linetype('Dash4', [10,2,2,2])
    # dash5 = linetype.Linetype('Dash5', [15,5,5,5])
    # st = style.Style('Solid White Line', solid, white, 1)
    # image.addStyle(st)
    # image.setOption('LINE_STYLE', st)
    # st = style.Style('Solid Black Line', solid, black, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Red Line', dash1, red, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Green Line', dash1, green, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Blue Line', dash1, blue, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Yellow Line', dash2, yellow, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Violet Line', dash2, violet, 1)
    # image.addStyle(st)
    # st = style.Style('Dashed Cyan Line', dash2, cyan, 1)
    # image.addStyle(st)

    _ds = dimension.Dimension.getDefaultDimStyle()
    image.addDimStyle(_ds)
    _dstyle = globals.prefs['DEFAULT_DIMSTYLE']
    _dname = None
    if _dstyle is not None:
        _dname = _dstyle.getName()
    _set_style = False
    for _dimstyle in globals.prefs['DIMSTYLES']:
        image.addDimStyle(_dimstyle)
        _name = _dimstyle.getName()
        if _dname is not None and _name == _dname:
            image.setOption('DIM_STYLE', _dimstyle)
            _set_style = True
    if not _set_style:
        # print "setting DIM_STYLE to default _ds ..."
        image.setOption('DIM_STYLE', _ds)
        # for _opt in _ds.getOptions():
            # _val = str(_ds.getValue(_opt))
            # print "opt: %s; value: %s" % (_opt, _val)
    #
    # FIXME: re-examine this once new text stuff is in place
    #
    # _ts = text.TextStyle('default')
    _ts = text.TextBlock.getDefaultTextStyle()
    image.addTextStyle(_ts)
    _tstyle = globals.prefs['DEFAULT_TEXTSTYLE']
    _tname = None
    if _tstyle is not None:
        _tname = _tstyle.getName()
    _set_style = False
    for _textstyle in globals.prefs['TEXTSTYLES']:
        image.addTextStyle(_textstyle)
        _name = _textstyle.getName()
        if _tname is not None and _name == _tname:
            image.setOption('TEXT_STYLE', _textstyle)
            _set_style = True
    if not _set_style:
        image.setOption('TEXT_STYLE', _ts)
    #
    # these will override what the style has set
    #
    # image.setOption('FONT_FAMILY', globals.prefs['FONT_FAMILY'])
    # image.setOption('FONT_SIZE', globals.prefs['FONT_SIZE'])
    # image.setOption('FONT_STYLE', globals.prefs['FONT_STYLE'])
    # image.setOption('FONT_WEIGHT', globals.prefs['FONT_WEIGHT'])
    # _font_color = globals.prefs['FONT_COLOR'].clone()
    # image.setOption('FONT_COLOR', _font_color)
    # image.setOption('CHAMFER_LENGTH', globals.prefs['CHAMFER_LENGTH'])
    # image.setOption('FILLET_RADIUS', globals.prefs['FILLET_RADIUS'])

    image.setUnits(globals.prefs['UNITS'])
    # image.setOption('HIGHLIGHT_POINTS', globals.prefs['HIGHLIGHT_POINTS'])

    # image.setOption('INACTIVE_LAYER_COLOR', globals.prefs['INACTIVE_LAYER_COLOR'])
    # image.setOption('AUTOSPLIT', globals.prefs['AUTOSPLIT'])
    # image.setOption('LEADER_ARROW_SIZE', globals.prefs['LEADER_ARROW_SIZE'])

#
# Image history class
#

class ImageLog(entity.EntityLog):
    def __init__(self, image):
        if not isinstance(image, Image):
            raise TypeError, "Invalid Image: " + `image`
        super(ImageLog, self).__init__(image)
        image.connect('scale_changed', self.__scaleChanged)
        image.connect('units_changed', self.__unitsChanged)
        image.connect('added_child', self.__addedChild)
        image.connect('removed_child', self.__removedChild)

    def __scaleChanged(self, image, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _scale = args[0]
        if not isinstance(_scale, float):
            raise TypeError, "Unexpected type for scale: " + `type(_scale)`
        if _scale < 1e-10:
            raise ValueError, "Invalid scale: %g" % _scale
        self.saveUndoData('scale_changed', _scale)

    def __unitsChanged(self, image, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _units = args[0]
        # fixme - maybe add error checking  ...
        self.saveUndoData('units_changed', _units)

    def __addedChild(self, image, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        _vals = _obj.getValues()
        if not isinstance(_vals, entity.EntityData):
            raise TypeError, "non EntityData for obj: " + `_obj`
        _vals.lock()
        self.saveUndoData('added_child', _vals)

    def __removedChild(self, image, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        _vals = _obj.getValues()
        if not isinstance(_vals, entity.EntityData):
            raise TypeError, "non EntityData for obj: " + `_obj`
        _vals.lock()
        self.saveUndoData('removed_child', _vals)

    def execute(self, undo, *args):
        # print "ImageLog::execute() ..."
        # print args
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _img = self.getObject()
        _op = args[0]
        if _op == 'units_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _img.getUnits()
            self.ignore(_op)
            try:
                _unit = args[1]
                if undo:
                    _img.startUndo()
                    try:
                        _img.setUnits(_unit)
                    finally:
                        _img.endUndo()
                else:
                    _img.startRedo()
                    try:
                        _img.setUnits(_unit)
                    finally:
                        _img.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'scale_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _img.getScale()
            self.ignore(_op)
            try:
                _scale = args[1]
                if undo:
                    _img.startUndo()
                    try:
                        _img.setScale(_scale)
                    finally:
                        _img.endUndo()
                else:
                    _img.startRedo()
                    try:
                        _img.setScale(_scale)
                    finally:
                        _img.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'added_child':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _vals = args[1]
            if not isinstance(_vals, entity.EntityData):
                raise TypeError, "Invalid EntityData: " + `_vals`
            self.ignore('modified')
            try:
                if undo:
                    _lid = _vals.get('id')
                    _layer = None
                    for _child in _img.getChildren():
                        if _child.getID() == _lid:
                            _layer = _child
                            break
                    if _layer is None:
                        raise ValueError, "Layer not found in Image"
                    _sdata = _vals
                    self.ignore('removed_child')
                    try:
                        _img.startUndo()
                        try:
                            _img.delLayer(_layer)
                        finally:
                            _img.endUndo()
                    finally:
                        self.receive('removed_child')
                else:
                    _pid = _vals.get('parent_layer')
                    _parent_layer = None
                    for _child in _img.getChildren():
                        if _child.getID() == _pid:
                            _parent_layer = _child
                            break
                    if _parent_layer is None:
                        raise ValueError, "Parent layer not found in Image"
                    _layer = self.__makeLayer(_vals)
                    self.ignore(_op)
                    try:
                        _img.startRedo()
                        try:
                            _img.addChildLayer(_layer, _parent_layer)
                        finally:
                            _img.endRedo()
                        _sdata = _layer.getValues()
                        _sdata.lock()
                    finally:
                        self.receive(_op)
            finally:
                self.receive('modified')
            self.saveData(undo, _op, _sdata)
        elif _op == 'removed_child':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _vals = args[1]
            if not isinstance(_vals, entity.EntityData):
                raise TypeError, "Invalid EntityData: " + `_vals`
            self.ignore('modified')
            try:
                if undo:
                    _pid = _vals.get('parent_layer')
                    _parent_layer = None
                    for _child in _img.getChildren():
                        if _child.getID() == _pid:
                            _parent_layer = _child
                            break
                    if _parent_layer is None:
                        raise ValueError, "Parent layer not found in Image"
                    _layer = self.__makeLayer(_vals)
                    self.ignore('added_child')
                    try:
                        _img.startUndo()
                        try:
                            _img.addChildLayer(_layer, _parent_layer)
                        finally:
                            _img.endUndo()
                        _sdata = _layer.getValues()
                        _sdata.lock()
                    finally:
                        self.receive('added_child')
                else:
                    _lid = _vals.get('id')
                    _layer = None
                    for _child in _img.getChildren():
                        if _child.getID() == _lid:
                            _layer = _child
                            break
                    if _layer is None:
                        raise ValueError, "Layer not found in Image"
                    _sdata = _vals
                    self.ignore(_op)
                    try:
                        _img.startRedo()
                        try:
                            _img.delLayer(_layer)
                        finally:
                            _img.endRedo()
                    finally:
                        self.receive(_op)
            finally:
                self.receive('modified')
            self.saveData(undo, _op, _sdata)                
        else:
            super(ImageLog, self).execute(undo, *args)

    def __makeLayer(self, values):
        _type = values.get('type')
        if _type != 'layer':
            _keys = values.keys()
            _keys.sort()
            for _key in _keys:
                print "key: %s: value: %s" % (_key, str(values.get(_key)))
            raise RuntimeError, "Invalid layer values"
        _id = values.get('id')
        if _id is None:
            raise ValueError, "Lost 'id' for recreating Layer"
        _name = values.get('name')
        if _name is None:
            raise ValueError, "Lost 'name' value for Layer"
        _scale = values.get('scale')
        if _scale is None:
            raise ValueError, "Lost 'scale' value for Layer"
        _layer = layer.Layer(_name, id=_id)
        _layer.setScale(_scale)
        return _layer
    
