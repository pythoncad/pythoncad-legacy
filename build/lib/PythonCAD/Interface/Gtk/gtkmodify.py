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
# functions for doing modifications on drawing
# entities
#

import pygtk
pygtk.require('2.0')
import gtk

from math import atan2, pi

from PythonCAD.Generic.dimension import Dimension
from PythonCAD.Generic.dimension import LinearDimension
from PythonCAD.Generic.dimension import HorizontalDimension
from PythonCAD.Generic.dimension import VerticalDimension
from PythonCAD.Generic.dimension import RadialDimension
from PythonCAD.Generic.dimension import AngularDimension
from PythonCAD.Generic import color
from PythonCAD.Generic.graphicobject import GraphicObject
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic import util
from PythonCAD.Generic import split

import PythonCAD.Generic.units
import PythonCAD.Generic.move
import PythonCAD.Generic.transfer
import PythonCAD.Generic.delete
import PythonCAD.Generic.rotate

#
# common code
#

def select_motion_notify(gtkimage, widget, event, tool):
    _tx, _ty = tool.getLocation()
    _px, _py = gtkimage.coordToPixTransform(_tx, _ty)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _xmin = min(_xc, _px)
        _ymin = min(_yc, _py)
        _rw = abs(_xc - _px)
        _rh = abs(_yc - _py)
        widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    tool.setCurrentPoint(_x, _y)
    _xmin = min(_x, _px)
    _ymin = min(_y, _py)
    _rw = abs(_x - _px)
    _rh = abs(_y - _py)
    widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    return True

#
# move objects
#

def move_objects(gtkimage, objlist, tool):
    _init_func = tool.getHandler("initialize")
    _dx, _dy = tool.getDistance()
    _image = gtkimage.getImage()
    _image.startAction()
    try:
        PythonCAD.Generic.move.move_objects(objlist, _dx, _dy)
    finally:
        _image.endAction()
    gtkimage.setPrompt(_('Click in the drawing area or enter a distance.'))
    tool.reset()
    _init_func(gtkimage, tool)
    
def move_button_press(gtkimage, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    #
    # need to find if the point is an intersection of drawing objects ...
    #
    tool.pushObject(_x)
    tool.pushObject(_y)
    return True

def move_end_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _active_layer = _image.getActiveLayer()
    _objlist = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
    move_objects(gtkimage, _objlist, tool)
    return True

def move_elem_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                _objs.append(_obj)
            _dx, _dy = tool.getDistance()
            move_objects(gtkimage, _objs, tool)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", move_end_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        _gc = gtkimage.getGC()
        _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        _gc.set_function(gtk.gdk.INVERT)
    return True
    
#
# move horizontal
#

def move_horizontal_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _image = gtkimage.getImage()
        _dist = util.get_float(eval(_text, _image.getImageVariables()))
        tool.setDistance(_dist, 0.0)
        if _image.hasSelection():
            move_objects(gtkimage, _image.getSelectedObjects(), tool)
        else:
            gtkimage.setPrompt(_('Click on the objects to move.'))
            tool.setHandler("button_press", move_elem_button_press_cb)
            tool.delHandler("entry_event")

def move_horizontal_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _x1, _y1 = tool.getLocation()
    tool.setDistance((_x - _x1), 0.0)
    if _image.hasSelection():
        move_objects(gtkimage, _image.getSelectedObjects(), tool)
    else:
        tool.clearLocation()
        gtkimage.setPrompt(_('Select the objects to move.'))
        tool.setHandler("button_press", move_elem_button_press_cb)
        tool.delHandler("entry_event")
    return True

def move_horizontal_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setLocation(_x, _y)
    gtkimage.setPrompt(_('Click another point to define the distance'))
    tool.setHandler("button_press", move_horizontal_second_button_press_cb)
    return True
    
def move_horizontal_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the distance.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", move_horizontal_first_button_press_cb)
    _tool.setHandler("entry_event", move_horizontal_entry_event)
    _tool.setHandler("initialize", move_horizontal_init)


#
# move vertical
#

def move_vertical_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _image = gtkimage.getImage()
        _dist = util.get_float(eval(_text, _image.getImageVariables()))
        tool.setDistance(0.0, _dist)
        if _image.hasSelection():
            move_objects(gtkimage, _image.getSelectedObjects(), tool)
        else:
            gtkimage.setPrompt(_('Click on the objects to move.'))
            tool.setHandler("button_press", move_elem_button_press_cb)
            tool.delHandler("entry_event")
    
def move_vertical_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _x1, _y1 = tool.getLocation()
    tool.setDistance(0.0, (_y - _y1))
    if _image.hasSelection():
        move_objects(gtkimage, _image.getSelectedObjects(), tool)
    else:
        tool.clearLocation()
        gtkimage.setPrompt(_('Select the objects to move.'))
        tool.setHandler("button_press", move_elem_button_press_cb)
        tool.delHandler("entry_event")
    return True

def move_vertical_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setLocation(_x, _y)
    gtkimage.setPrompt(_('Click another point to define the distance'))
    tool.setHandler("button_press", move_vertical_second_button_press_cb)
    return True

def move_vertical_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the distance.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", move_vertical_first_button_press_cb)
    _tool.setHandler("entry_event", move_vertical_entry_event)
    _tool.setHandler("initialize", move_vertical_init)

    
#
# move based on two mouse clicks
#

def move_xy_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _image = gtkimage.getImage()
        _x, _y = eval(_text, _image.getImageVariables())
        tool.setDistance(util.get_float(_x), util.get_float(_y))
        if _image.hasSelection():
            move_objects(gtkimage, _image.getSelectedObjects(), tool)
        else:
            gtkimage.setPrompt(_('Click on the objects to move.'))
            tool.setHandler("button_press", move_elem_button_press_cb)
            tool.delHandler("entry_event")

def move_xy_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _x1, _y1 = tool.getLocation()
    tool.setDistance((_x - _x1), (_y - _y1))
    if _image.hasSelection():
        move_objects(gtkimage, _image.getSelectedObjects(), tool)
    else:
        tool.clearLocation()
        gtkimage.setPrompt(_('Select the objects to move.'))
        tool.setHandler("button_press", move_elem_button_press_cb)
        tool.delHandler("entry_event")
    return True

def move_xy_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setLocation(_x, _y)
    gtkimage.setPrompt(_('Click another point to define the distance'))
    tool.setHandler("button_press", move_xy_second_button_press_cb)
    return True

def move_twopoint_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the x and y distances.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", move_xy_first_button_press_cb)
    _tool.setHandler("entry_event", move_xy_entry_event)    
    _tool.setHandler("initialize", move_twopoint_init)


#
# delete objects
#

def delete_region_end_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    tool.delHandler("motion_notify")
    tool.setHandler("button_press", delete_button_press_cb)
    _active_layer = _image.getActiveLayer()
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
    if len(_objs):
        _image.startAction()
        try:
            PythonCAD.Generic.delete.delete_objects(_objs)
        finally:
            _image.endAction()
    tool.reset()
    delete_mode_init(gtkimage)
    gtkimage.redraw()
    
def delete_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _objs = _active_layer.mapPoint((_x, _y), _tol)
    if len(_objs):
        _dims = []
        _image.startAction()
        try:
            for _obj in _objs:
                if isinstance(_obj, Dimension):
                    _dims.append(_obj)
                elif isinstance(_obj, tuple):
                    _entity, _pt = _obj
                    _active_layer.delObject(_entity)
                else:
                    raise TypeError, "Unhandled object: " + `_obj`
            for _dim in _dims:
                if _dim in _active_layer: # it may have been removed ...
                    _active_layer.delObject(_dim)
        finally:
            _image.endAction()
            gtkimage.redraw()
    else:
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", delete_region_end_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        _gc = gtkimage.getGC()
        _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        _gc.set_function(gtk.gdk.INVERT)
    return True
        
def delete_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the items you want to delete.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", delete_button_press_cb)
    _tool.setHandler("initialize", delete_mode_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = _image.getSelectedObjects()
        _image.startAction()
        try:
            PythonCAD.Generic.delete.delete_objects(_objs)
        finally:
            _image.endAction()

#
# stretch operations
#

def stretch_end_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _y1 = tool.popObject()
    _x1 = tool.popObject()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    tool.delHandler("motion_notify")
    _active_layer = _image.getActiveLayer()
    _dx, _dy = tool.getDistance()
    _image.startAction()
    try:
        for _pt in _active_layer.getLayerEntities("point"):
            if _pt.inRegion(_xmin, _ymin, _xmax, _ymax):
                _pt.move(_dx, _dy)
    finally:
        _image.endAction()
    tool.clearLocation()
    tool.clearCurrentPoint()
    tool.setHandler("button_press", stretch_elem_button_press_cb)
    return True

def stretch_elem_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pt = None
    _pts = _active_layer.find('point', _x, _y, _tol)
    if len(_pts):
        _dx, _dy = tool.getDistance()
        _image.startAction()
        try:
            for _pt in _pts:
                _pt.move(_dx, _dy)
        finally:
            _image.endAction()
    else:
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", stretch_end_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        _gc = gtkimage.getGC()
        _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        _gc.set_function(gtk.gdk.INVERT)
    return True

#
# stretch horizontal
#

def stretch_horiz_button_press_cb(gtkimage, widget, event, tool):
    if not len(tool):
        move_button_press(gtkimage, tool)
        gtkimage.setPrompt(_('Click a second point to indicate the horizontal distance'))
    else:
        _x, _y = gtkimage.image.getCurrentPoint()
        #
        # see if the point is at an intersection of drawing objects ...
        #
        _y1 = tool.popObject()
        _x1 = tool.popObject()
        tool.setDistance((_x - _x1), 0.0)
        gtkimage.setPrompt(_('Select the points to move.'))
        tool.delHandler("entry_event")
        tool.setHandler("button_press", stretch_elem_button_press_cb)
    return True

def stretch_horiz_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _dist = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setDistance(_dist, 0.0)
        gtkimage.setPrompt(_('Select the points to move.'))
        tool.setHandler("button_press", stretch_elem_button_press_cb)
        tool.delHandler("entry_event")

def stretch_horizontal_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on a point or enter the horizontal distance.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", stretch_horiz_button_press_cb)
    _tool.setHandler("entry_event", stretch_horiz_entry_event)
    _tool.setHandler("initialize", stretch_horizontal_init)


#
# stretch vertical
#

def stretch_vert_button_press_cb(gtkimage, widget, event, tool):
    if not len(tool):
        move_button_press(gtkimage, tool)
        gtkimage.setPrompt(_('Click a second point to indicate the vertical distance'))
    else:
        _x, _y = gtkimage.image.getCurrentPoint()
        #
        # see if the point is at an intersection of drawing objects ...
        #
        _y1 = tool.popObject()
        _x1 = tool.popObject()
        tool.setDistance(0.0, (_y - _y1))
        gtkimage.setPrompt(_('Select the points to move.'))
        tool.delHandler("entry_event")
        tool.setHandler("button_press", stretch_elem_button_press_cb)
    return True

def stretch_vert_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _dist = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setDistance(0.0, _dist)
        gtkimage.setPrompt(_('Select the points to move.'))
        tool.setHandler("button_press", stretch_elem_button_press_cb)
        tool.delHandler("entry_event")

def stretch_vertical_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the distance.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", stretch_vert_button_press_cb)
    _tool.setHandler("entry_event", stretch_vert_entry_event)
    _tool.setHandler("initialize", stretch_vertical_init)


#
# stretch x/y
#

def stretch_xy_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = eval(_text, gtkimage.image.getImageVariables())
        tool.setDistance(util.get_float(_x), util.get_float(_y))
        gtkimage.setPrompt(_('Select the points to move.'))
        tool.setHandler("button_press", stretch_elem_button_press_cb)
        tool.delHandler("entry_event")

def stretch_xy_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _x1, _y1 = tool.getLocation()
    tool.setDistance((_x - _x1), (_y - _y1))
    tool.clearLocation()
    gtkimage.setPrompt(_('Select the points to move.'))
    tool.setHandler("button_press", stretch_elem_button_press_cb)
    tool.delHandler("entry_event")
    return True

def stretch_xy_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setLocation(_x, _y)
    gtkimage.setPrompt(_('Click another point to define the distance'))
    tool.setHandler("button_press", stretch_xy_second_button_press_cb)
    return True

def stretch_xy_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the x and y distances.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", stretch_xy_first_button_press_cb)
    _tool.setHandler("entry_event", stretch_xy_entry_event)    
    _tool.setHandler("initialize", stretch_xy_init)


#
# rotate objects
#

def rotate_objects(gtkimage, objlist, tool):
    _init_func = tool.getHandler("initialize")
    _cx, _cy = tool.getRotationPoint()
    _angle = tool.getAngle()
    _image = gtkimage.getImage()
    _image.startAction()
    try:
        PythonCAD.Generic.rotate.rotate_objects(objlist, _cx, _cy, _angle)
    finally:
        _image.endAction()
    tool.reset()
    _init_func(gtkimage, tool)

def rotate_end_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _active_layer = _image.getActiveLayer()
    _objlist = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
    rotate_objects(gtkimage, _objlist, tool)
    return True

def rotate_elem_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                _objs.append(_obj)
            rotate_objects(gtkimage, _objs, tool)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", rotate_end_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        _gc = gtkimage.getGC()
        _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        _gc.set_function(gtk.gdk.INVERT)
    return True

def rotate_angle_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = eval(_text, gtkimage.image.getImageVariables())
        tool.setAngle(util.get_float(_angle))
        gtkimage.setPrompt(_('Select the objects to rotate'))
        tool.delHandler("entry_event")
        tool.setHandler("button_press", rotate_elem_button_press_cb)

def rotate_angle_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol)
    _a2 = None
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, HCLine):
                    _a2 = 0.0
                elif isinstance(_obj, VCLine):
                    _a2 = 90.0
                elif isinstance(_obj, ACLine):
                    _a2 = _obj.getAngle()
                elif isinstance(_obj, CLine):
                    _p1, _p2 = _obj.getKeypoints()
                    _a2 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) * (180.0/pi)
                else:
                    pass
                if _a2 is not None:
                    break
    if _a2 is not None:
        _cl = tool.getObject(0)
        if isinstance(_cl, HCLine):
            _a1 = 0.0
        elif isinstance(_cl, VCLine):
            _a1 = 90.0
        elif isinstance(_cl, ACLine):
            _a1 = _cl.getAngle()
        elif isinstance(_cl, CLine):
            _p1, _p2 = _cl.getKeypoints()
            _a1 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) * (180.0/pi)
        else:
            raise RuntimeError, "Unexpected conline type: " + `type(_cl)`
        _angle = _a2 - _a1
        if abs(_angle) > 1e-10:
            tool.setAngle(_angle)
            gtkimage.setPrompt(_('Select the objects to rotate'))
            tool.delHandler("entry_event")
            tool.setHandler("button_press", rotate_elem_button_press_cb)
    return True

def rotate_angle_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (HCLine, VCLine, ACLine, CLine)):
                    tool.pushObject(_obj)
                    tool.setHandler("button_press",
                                    rotate_angle_second_button_press_cb)
                    gtkimage.setPrompt(_('Click on another construction line to define the angle of rotation or enter the rotation angle.'))
                    break
    return True

def rotate_point_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = eval(_text, gtkimage.image.getImageVariables())
        tool.setRotationPoint(util.get_float(_x), util.get_float(_y))
        gtkimage.setPrompt(_('Click on a construction line or enter the rotation angle.'))
        tool.setHandler("entry_event", rotate_angle_entry_event)
        tool.setHandler("button_press", rotate_angle_first_button_press_cb)

def rotate_point_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setRotationPoint(_x, _y)
    gtkimage.setPrompt(_('Click on a construction line or enter the rotation angle'))
    tool.setHandler("button_press", rotate_angle_first_button_press_cb)
    tool.setHandler("entry_event", rotate_angle_entry_event)
    return True

def rotate_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the rotation center coordinates.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", rotate_point_button_press_cb)
    _tool.setHandler("entry_event", rotate_point_entry_event)    
    _tool.setHandler("initialize", rotate_init)


#
# split objects into two pieces or at intersection points
#

def split_end_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _y1 = tool.popObject()
    _x1 = tool.popObject()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    tool.delHandler("motion_notify")
    _active_layer = _image.getActiveLayer()
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax, True)
    if len(_objs):
        _splitable = []
        for _obj in _objs:
            if isinstance(_obj, (Segment, Circle, Arc, Polyline)):
                _splitable.append(_obj)
        if len(_splitable):
            _image.startAction()
            try:
                split.split_objects(_splitable)
            finally:
                _image.endAction()
    gtkimage.setPrompt(_('Click on the objects you want to split.'))
    tool.clearLocation()
    tool.clearCurrentPoint()
    tool.setHandler("button_press", split_object_button_press_cb)
    return True
    
def split_object_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _objlist = _active_layer.mapPoint((_x, _y), _tol, None)
    if len(_objlist):
        for _obj, _pt in _objlist:
            _px, _py = _pt.getCoords()
            if isinstance(_obj, Segment):
                _image.startAction()
                try:
                    _segs = split.split_segment_at(_obj, _px, _py)
                    if _segs is not None:
                        _active_layer.delObject(_obj)
                        _s1, _s2 = _segs
                        _active_layer.addObject(_s1)
                        _active_layer.addObject(_s2)
                finally:
                    _image.endAction()
            elif isinstance(_obj, Arc):
                _image.startAction()
                try:
                    _arcs = split.split_arc_at(_obj, _px, _py)
                    if _arcs is not None:
                        _active_layer.delObject(_obj)
                        _a1, _a2 = _arcs
                        _active_layer.addObject(_a1)
                        _active_layer.addObject(_a2)
                finally:
                    _image.endAction()
            elif isinstance(_obj, Circle):
                _image.startAction()
                try:
                    _arc = split.split_circle_at(_obj, _px, _py)
                    if _arc is not None:
                        _active_layer.delObject(_obj)
                        _active_layer.addObject(_arc)
                finally:
                    _image.endAction()
            elif isinstance(_obj, Polyline):
                _image.startAction()
                try:
                    if split.split_polyline_at(_obj, _px, _py):
                        _obj.erase(gtkimage)
                        _obj.draw(gtkimage)
                finally:
                    _image.endAction()
            else:
                pass
    else:
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", split_end_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        _gc = gtkimage.getGC()
        _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        _gc.set_function(gtk.gdk.INVERT)
    return True
        
def split_object_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the objects you want to split'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("initialize", split_object_init)
    _tool.setHandler("button_press", split_object_button_press_cb)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _splitable = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, (Segment, Circle, Arc, Polyline)):
                _splitable.append(_obj)
        if len(_splitable):
            _image.startAction()
            try:
                split.split_objects(_splitable)
            finally:
                _image.endAction()

#
# transfer objects from one layer to another
#

def transfer_end_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x2, _y2 = _image.getCurrentPoint()
    _y1 = tool.popObject()
    _x1 = tool.popObject()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    tool.delHandler("motion_notify")
    _active_layer = _image.getActiveLayer()
    _layers = [_image.getTopLayer()]
    _objdict = {}
    while len(_layers):
        _layer = _layers.pop()
        if _layer is not _active_layer:
            if _layer.isVisible():
                _objs = _layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
                if len(_objs):
                    _objdict[_layer] = _objs
        _layers.extend(_layer.getSublayers())
    if len(_objdict):
        _image.startAction()
        try:
            for _layer in _objdict:
                if _layer is not _active_layer:
                    _objs = _objdict[_layer]
                    PythonCAD.Generic.transfer.transfer_objects(_objs, _active_layer)
        finally:
            _image.endAction()
    tool.clearLocation()
    tool.clearCurrentPoint()
    tool.setHandler("button_press", transfer_object_button_press_cb)
    return True
    
def transfer_object_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _image.startAction()
        try:
            for _layer in _objdict:
                if _layer is not _active_layer:
                    _objs = []
                    for _obj, _pt in _objdict[_layer]:
                        _objs.append(_obj)
                    PythonCAD.Generic.transfer.transfer_objects(_objs, _active_layer)
        finally:
            _image.endAction()
    else:
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", transfer_end_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        gc = gtkimage.getGC()
        gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                               gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        gc.set_function(gtk.gdk.INVERT)
    return True
        
def transfer_object_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the objects you want to transfer to the active layer'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", transfer_object_button_press_cb)
    
#
# common attribute changing code
#

def _change_attribute(gtkimage, objlist, tool=None):
    _tool = gtkimage.getImage().getTool()
    _init = _tool.getHandler('initialize')
    _attr = _tool.getAttribute()
    _value = _tool.getValue()
    if len(objlist):
        _image = gtkimage.getImage()
        _image.startAction()
        try:
            for _obj in objlist:
                getattr(_obj, _attr)(_value)
        finally:
            _image.endAction()
    _tool.reset()
    _init(gtkimage, _tool)

def change_attr_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pts = _active_layer.find('point', _x, _y)
    if len(_pts) > 0:
        _x, _y = _pts[0].getCoords()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x)
    _ymin = min(_y1, _y)
    _xmax = max(_x1, _x)
    _ymax = max(_y1, _y)
    _objs = []
    _filter = tool.getFilter()
    _objtype = tool.getObjtype()
    for _obj in _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax):
        if _filter is not None:
            _fobj = _filter(tool, _obj)
            if _fobj is not None:
                _objs.append(_fobj)
        elif _objtype is not None:
            if isinstance(_obj, _objtype):
                _objs.append(_obj)
        else:
            _objs.append(_obj)
    _change_attribute(gtkimage, _objs, tool)
    return True

def change_attr_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            _objtype = tool.getObjtype()
            for _obj, _pt in _objdict[_active_layer]:
                if _objtype is None:
                    _objs.append(_obj)
                else:
                    if isinstance(_obj, _objtype):
                        _objs.append(_obj)
            _change_attribute(gtkimage, _objs, tool)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", change_attr_second_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

#
# change color
#

def change_color_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_color_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, GraphicObject):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the items you want the color to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)
    
def change_color_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.ColorSelectionDialog(_('Set Active Color'))
    _dialog.set_transient_for(_window)
    _colorsel = _dialog.colorsel
    _image = gtkimage.getImage()
    _prev_color = _image.getOption('LINE_COLOR')
    _gtk_color = gtkimage.getColor(_prev_color)
    _colorsel.set_previous_color(_gtk_color)
    _colorsel.set_current_color(_gtk_color)
    _colorsel.set_has_palette(True)
    _color = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _gtk_color = _colorsel.get_current_color()
        _r = int(round((_gtk_color.red/65535.0) * 255.0))
        _g = int(round((_gtk_color.green/65535.0) * 255.0))
        _b = int(round((_gtk_color.blue/65535.0) * 255.0))
        for _c in _image.getImageEntities('color'):
            if _c.r == _r and _c.g == _g and _c.b == _b:
                _color = _c
                break
        if _color is None:
            _color = color.Color(_r, _g, _b)
    _dialog.destroy()
    return _color

#
# change linetypes
#

def change_linetype_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_linetype_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, GraphicObject):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the items you want the linetype to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_linetype_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Linetype'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    
    _label = gtk.Label(_('Linetype:'))
    _hbox.pack_start(_label, False, False, 0)
    _image = gtkimage.getImage()
    _clt = _image.getOption('LINE_TYPE')
    _linetypes = _image.getImageEntities('linetype')
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _clt:
                _idx = _i
            _widget.append_text(_lt.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _clt:
                _idx = _i
            _item = gtk.MenuItem(_lt.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _lt = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _lt = _linetypes[_idx]
    _dialog.destroy()
    return _lt

#
# change thickness
#

def change_thickness_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_thickness_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, GraphicObject):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the items you want the thickness to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_thickness_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Thickness'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Thickness:'))
    _hbox.pack_start(_label, False, False, 0)
    _thickness = gtkimage.image.getOption('LINE_THICKNESS')
    _adj = gtk.Adjustment(_thickness, 0.0001, 20.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(1)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _t = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _t = float(_sb.get_value())
    _dialog.destroy()
    return _t

#
# change the style
#

def change_style_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_style_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, GraphicObject):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the items you want the style to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_style_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Style'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Style:'))
    _image = gtkimage.getImage()
    _cst = _image.getOption('LINE_STYLE')
    _styles = _image.getImageEntities('style')
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cst:
                _idx = _i
            _widget.append_text(_s.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cst:
                _idx = _i
            _item = gtk.MenuItem(_s.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _s = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _s = _styles[_idx]
    _dialog.destroy()
    return _s

#
# Change TextBlock properties
#

def change_textblock_size_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_size_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the items you want the size to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_textblock_size_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Text Size'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Text Size:'))
    _hbox.pack_start(_label, False, False, 0)
    _size = gtkimage.image.getOption(key)
    _adj = gtk.Adjustment(_size, 0.0001, 400.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(1)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _size = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _size = float(_sb.get_value())
    _dialog.destroy()
    return _size

def change_textblock_family_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_family_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the objects you want the family to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)
        
def change_textblock_family_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Font Family'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _families = []
    for _family in _window.get_pango_context().list_families():
        _families.append(_family.get_name())
    _families.sort()
    _label = gtk.Label(_('Family:'))
    _family = gtkimage.image.getOption(key)
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _f == _family:
                _idx = _i
            _widget.append_text(_f)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_families)):
            _f = _families[_i]
            if _f == _family:
                _idx = _i
            _item = gtk.MenuItem(_f)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _family = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _family = _families[_idx]
    _dialog.destroy()
    return _family

def change_textblock_weight_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_weight_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the objects you want the weight to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_textblock_weight_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Text Weight'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Text Weight:'))
    _weight = gtkimage.image.getOption(key)
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        _widget.append_text(_('NORMAL'))
        if _weight == TextStyle.WEIGHT_NORMAL:
            _idx = 0
        _widget.append_text(_('LIGHT'))
        if _weight == TextStyle.WEIGHT_LIGHT:
            _idx = 1
        _widget.append_text(_('BOLD'))
        if _weight == TextStyle.WEIGHT_BOLD:
            _idx = 2
        _widget.append_text(_('HEAVY'))
        if _weight == TextStyle.WEIGHT_HEAVY:
            _idx = 3
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        _item = gtk.MenuItem(_('NORMAL'))
        _menu.append(_item)
        if _weight == TextStyle.WEIGHT_NORMAL:
            _idx = 0
        _item = gtk.MenuItem(_('LIGHT'))
        _menu.append(_item)
        if _weight == TextStyle.WEIGHT_LIGHT:
            _idx = 1
        _item = gtk.MenuItem(_('BOLD'))
        _menu.append(_item)
        if _weight == TextStyle.WEIGHT_BOLD:
            _idx = 2
        _item = gtk.MenuItem(_('HEAVY'))
        _menu.append(_item)
        if _weight == TextStyle.WEIGHT_HEAVY:
            _idx = 3
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _weight = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _weight = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _weight = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
    _dialog.destroy()
    return _weight

def change_textblock_style_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_style_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the objects you want the style to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_textblock_style_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Text Style'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Text Style:'))
    _style = gtkimage.image.getOption(key)
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        _widget.append_text(_('NORMAL'))
        if _style == TextStyle.FONT_NORMAL:
            _idx = 0
        _widget.append_text(_('OBLIQUE'))
        if _style == TextStyle.FONT_OBLIQUE:
            _idx = 1
        _widget.append_text(_('ITALIC'))
        if _style == TextStyle.FONT_ITALIC:
            _idx = 2
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        _item = gtk.MenuItem(_('NORMAL'))
        _menu.append(_item)
        if _style == TextStyle.FONT_NORMAL:
            _idx = 0
        _item = gtk.MenuItem(_('OBLIQUE'))
        _menu.append(_item)
        if _style == TextStyle.FONT_OBLIQUE:
            _idx = 1
        _item = gtk.MenuItem(_('ITALIC'))
        _menu.append(_item)
        if _style == TextStyle.FONT_ITALIC:
            _idx = 2
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _style = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _style = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _style = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
    _dialog.destroy()
    return _style

def change_textblock_alignment_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_alignment_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the objects you want the alignment to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_textblock_alignment_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Text Alignment'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Text Alignment:'))
    _align = gtkimage.image.getOption(key)
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        _widget.append_text(_('LEFT'))
        if _align == TextStyle.ALIGN_LEFT:
            _idx = 0
        _widget.append_text(_('CENTER'))
        if _align == TextStyle.ALIGN_CENTER:
            _idx = 1
        _widget.append_text(_('RIGHT'))
        if _align == TextStyle.ALIGN_RIGHT:
            _idx = 2
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        _item = gtk.MenuItem(_('LEFT'))
        _menu.append(_item)
        if _align == TextStyle.ALIGN_LEFT:
            _idx = 0
        _item = gtk.MenuItem(_('CENTER'))
        _menu.append(_item)
        if _align == TextStyle.ALIGN_CENTER:
            _idx = 1
        _item = gtk.MenuItem(_('RIGHT'))
        _menu.append(_item)
        if _align == TextStyle.ALIGN_RIGHT:
            _idx = 2
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _align = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _align = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _align = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
    _dialog.destroy()
    return _align

def change_textblock_color_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_textblock_color_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, TextBlock):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the objects you want the color to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_textblock_color_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.ColorSelectionDialog(_('Change Font Color'))
    _dialog.set_transient_for(_window)
    _colorsel = _dialog.colorsel
    _image = gtkimage.getImage()
    _color = _image.getOption(key)
    _gtk_color = gtkimage.getColor(_color)
    _colorsel.set_previous_color(_gtk_color)
    _colorsel.set_current_color(_gtk_color)
    _colorsel.set_has_palette(True)
    _color = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _gtk_color = _colorsel.get_current_color()
        _r = int(round((_gtk_color.red/65535.0) * 255.0))
        _g = int(round((_gtk_color.green/65535.0) * 255.0))
        _b = int(round((_gtk_color.blue/65535.0) * 255.0))
        for _c in _image.getImageEntities('color'):
            if _c.r == _r and _c.g == _g and _c.b == _b:
                _color = _c
                break
        if _color is None:
            _color = color.Color(_r, _g, _b)
    _dialog.destroy()
    return _color

#
# Change Dimension Properties
#

def change_dim_offset_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_offset_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want the offset to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_offset_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Offset Length'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Length:'))
    _hbox.pack_start(_label, False, False, 0)
    _offset = gtkimage.image.getOption('DIM_OFFSET')
    _adj = gtk.Adjustment(_offset, 0.01, 200.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(2)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _offset = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _offset = float(_sb.get_value())
    _dialog.destroy()
    return _offset

def change_dim_extension_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_extension_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want the extension to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_extension_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Extension Length'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Length:'))
    _hbox.pack_start(_label, False, False, 0)
    _extlen = gtkimage.image.getOption('DIM_EXTENSION')
    _adj = gtk.Adjustment(_extlen, 0.01, 200.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(2)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _extlen = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _extlen = float(_sb.get_value())
    _dialog.destroy()
    return _extlen

def change_dim_endpoint_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_endpoint_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want the endpoint type to change.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_endpoint_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Endpoint Markers'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Endpoints:'))
    _endpt = gtkimage.image.getOption('DIM_ENDPOINT')
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        _widget.append_text(_('None'))
        if _endpt == Dimension.DIM_ENDPT_NONE:
            _idx = 0
        _widget.append_text(_('Arrow'))
        if _endpt == Dimension.DIM_ENDPT_ARROW:
            _idx = 1
        _widget.append_text(_('Filled Arrow'))
        if _endpt == Dimension.DIM_ENDPT_FILLED_ARROW:
            _idx = 2
        _widget.append_text(_('Slash'))
        if _endpt == Dimension.DIM_ENDPT_SLASH:
            _idx = 3
        _widget.append_text(_('Circle'))
        if _endpt == Dimension.DIM_ENDPT_CIRCLE:
            _idx = 4
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        _item = gtk.MenuItem(_('None'))
        _menu.append(_item)
        if _endpt == Dimension.DIM_ENDPT_NONE:
            _idx = 0
        _item = gtk.MenuItem(_('Arrow'))
        _menu.append(_item)
        if _endpt == Dimension.DIM_ENDPT_ARROW:
            _idx = 1
        _item = gtk.MenuItem(_('Filled Arrow'))
        _menu.append(_item)
        if _endpt == Dimension.DIM_ENDPT_FILLED_ARROW:
            _idx = 2
        _item = gtk.MenuItem(_('Slash'))
        _menu.append(_item)
        if _endpt == Dimension.DIM_ENDPT_SLASH:
            _idx = 3
        _item = gtk.MenuItem(_('Circle'))
        _menu.append(_item)
        if _endpt == Dimension.DIM_ENDPT_CIRCLE:
            _idx = 4
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _endpt = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _endpt = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _endpt = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
    _dialog.destroy()
    return _endpt

def change_dim_endpoint_size_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_endpoint_size_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want the endpoint size to change.'))
        tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_endpoint_size_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Endpoint Size'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Length:'))
    _hbox.pack_start(_label, False, False, 0)
    _size = gtkimage.image.getOption('DIM_ENDPOINT_SIZE')
    _adj = gtk.Adjustment(_size, 0.01, 200.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(2)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _size = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _size = float(_sb.get_value())
    _dialog.destroy()
    return _size

def change_dim_dual_mode_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_dual_mode_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want to change the dual dimension display.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_dual_mode_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Dual Mode'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _cb = gtk.CheckButton(_('Display Two Dimension Values'))
    _mode = gtkimage.image.getOption('DIM_DUAL_MODE')
    _cb.set_active(_mode)
    _hbox.pack_start(_cb, True, True, 0)
    _dialog.show_all()
    _mode = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _mode = _cb.get_active()
    _dialog.destroy()
    return _mode

def change_dim_dual_mode_offset_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_dual_mode_offset_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want to change the dual dimension offset value.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_dual_mode_offset_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Dual Mode Offset'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Length:'))
    _hbox.pack_start(_label, False, False, 0)
    _offset = gtkimage.image.getOption('DIM_DUAL_MODE_OFFSET')
    _adj = gtk.Adjustment(_offset, 0.01, 200.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(2)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _offset = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _offset = float(_sb.get_value())
    _dialog.destroy()
    return _offset

def change_dim_thickness_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_thickness_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want to change the thickess.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_thickness_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Dim Thickness'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Thickness:'))
    _hbox.pack_start(_label, False, False, 0)
    _t = gtkimage.image.getOption('DIM_THICKNESS')
    _adj = gtk.Adjustment(_t, 0.01, 200.0, 0.1, 1.0, 1.0)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(2)
    _sb.set_numeric(False)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _t = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _t = float(_sb.get_value())
    _dialog.destroy()
    return _t

def change_dim_color_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dim_color_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                _objs.append(_obj)
        _change_attribute(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the dimension you want to change the color.'))
        _tool.setHandler("button_press", change_attr_first_button_press_cb)

def change_dim_color_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.ColorSelectionDialog(_('Change Dimension Color'))
    _dialog.set_transient_for(_window)
    _colorsel = _dialog.colorsel
    _image = gtkimage.getImage()
    _color = _image.getOption('DIM_COLOR')
    _gtk_color = gtkimage.getColor(_color)
    _colorsel.set_previous_color(_gtk_color)
    _colorsel.set_current_color(_gtk_color)
    _colorsel.set_has_palette(True)
    _color = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _gtk_color = _colorsel.get_current_color()
        _r = int(round((_gtk_color.red/65535.0) * 255.0))
        _g = int(round((_gtk_color.green/65535.0) * 255.0))
        _b = int(round((_gtk_color.blue/65535.0) * 255.0))
        for _c in _image.getImageEntities('color'):
            if _c.r == _r and _c.g == _g and _c.b == _b:
                _color = _c
                break
        if _color is None:
            _color = color.Color(_r, _g, _b)
    _dialog.destroy()
    return _color

#
# Change DimString properties
#

def _dimstring_filter_proc(tool, obj):
    _ds = None
    if isinstance(obj, Dimension):
        if tool.getPrimary():
            _ds = obj.getPrimaryDimstring()
        else:
            _ds = obj.getSecondaryDimstring()
    return _ds

def _ldimstring_filter_proc(tool, obj):
    _ds = None
    if isinstance(obj, (LinearDimension,
                        HorizontalDimension,
                        VerticalDimension)):
        if tool.getPrimary():
            _ds = obj.getPrimaryDimstring()
        else:
            _ds = obj.getSecondaryDimstring()
    return _ds

def _rdimstring_filter_proc(tool, obj):
    _ds = None
    if isinstance(obj, RadialDimension):
        if tool.getPrimary():
            _ds = obj.getPrimaryDimstring()
        else:
            _ds = obj.getSecondaryDimstring()
    return _ds

def _adimstring_filter_proc(tool, obj):
    _ds = None
    if isinstance(obj, AngularDimension):
        if tool.getPrimary():
            _ds = obj.getPrimaryDimstring()
        else:
            _ds = obj.getSecondaryDimstring()
    return _ds

def change_dimstr_prefix_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Prefix'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Prefix:'))
    _hbox.pack_start(_label, True, True, 0)
    _prefix = gtkimage.image.getOption(key)
    _entry = gtk.Entry()
    _entry.set_text(_prefix)
    _hbox.pack_start(_entry, True, True, 0)
    _dialog.show_all()
    _prefix = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _prefix = _entry.get_text()
    _dialog.destroy()
    return _prefix

def change_dimstr_suffix_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Suffix'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Suffix:'))
    _hbox.pack_start(_label, True, True, 0)
    _suffix = gtkimage.image.getOption(key)
    _entry = gtk.Entry()
    _entry.set_text(_suffix)
    _hbox.pack_start(_entry, True, True, 0)
    _dialog.show_all()
    _suffix = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _suffix = _entry.get_text()
    _dialog.destroy()
    return _suffix

def change_dimstr_precision_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Precision'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Precision:'))
    _hbox.pack_start(_label, False, False, 0)
    _prec = gtkimage.image.getOption(key)
    _adj = gtk.Adjustment(_prec, 0, 15, 1, 1, 1)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(0)
    _sb.set_numeric(True)    
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _prec = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _prec = int(_sb.get_value())
    _dialog.destroy()
    return _prec

def change_dimstr_units_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Units'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Units'))
    _hbox.pack_start(_label, False, False, 0)
    _units = [(_('Millimeters'), PythonCAD.Generic.units.MILLIMETERS),
              (_('Micrometers'), PythonCAD.Generic.units.MICROMETERS),
              (_('Meters'), PythonCAD.Generic.units.METERS),
              (_('Kilometers'), PythonCAD.Generic.units.KILOMETERS),
              (_('Inches'), PythonCAD.Generic.units.INCHES),
              (_('Feet'), PythonCAD.Generic.units.FEET),
              (_('Yards'), PythonCAD.Generic.units.YARDS),
              (_('Miles'), PythonCAD.Generic.units.MILES),
              ]
    _unit = gtkimage.image.getOption(key)
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _unit_widget = gtk.combo_box_new_text()
        for _i in range(len(_units)):
            _str, _val = _units[_i]
            if _unit == _val:
                _idx = _i
            _unit_widget.append_text(_str)
        _unit_widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_units)):
            _str, _val = _units[_i]
            if _unit == _val:
                _idx = _i
            _item = gtk.MenuItem(_str)
            _menu.append(_item)
        _unit_widget = gtk.OptionMenu()
        _unit_widget.set_menu(_menu)
        _unit_widget.set_history(_idx)
    _hbox.pack_start(_unit_widget, True, True, 0);
    _dialog.show_all()
    _unit = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
            _idx = _unit_widget.get_active()
        else:
            _idx = _unit_widget.get_history()
        _unit = _units[_idx][1]
    _dialog.destroy()
    return _unit

def change_dimstr_print_decimal_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Print Decimal'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _cb = gtk.CheckButton(_('Print Trailing Decimal'))
    _mode = gtkimage.image.getOption(key)
    _cb.set_active(_mode)
    _hbox.pack_start(_cb, True, True, 0)
    _dialog.show_all()
    _mode = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _mode = _cb.get_active()
    _dialog.destroy()
    return _mode

def change_dimstr_print_zero_dialog(gtkimage, key):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Change Print Zero'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _cb = gtk.CheckButton(_('Print Leading Zero'))
    _mode = gtkimage.image.getOption(key)
    _cb.set_active(_mode)
    _hbox.pack_start(_cb, True, True, 0)
    _dialog.show_all()
    _mode = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _mode = _cb.get_active()
    _dialog.destroy()
    return _mode

def _change_dimstring_init(gtkimage, tool=None):
    _image = gtkimage.getImage()
    _tool = _image.getTool()
    if _image.hasSelection():
        _primary = tool.getPrimary()
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, Dimension):
                if _primary:
                    _objs.append(_obj.getPrimaryDimstring())
                else:
                    _objs.append(_obj.getSecondaryDimstring())
        _change_attribute(gtkimage, _objs, _tool)
    else:
        _tool.setHandler("button_press", change_attr_first_button_press_cb)
    
def change_dimstr_family_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString family.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_family_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_style_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString style.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_style_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_weight_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString weight.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_weight_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_alignment_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString alignment.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_alignment_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_size_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString size.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_size_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_color_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString color.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_color_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_ldimstr_prefix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString prefix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_ldimstr_prefix_init)
    _tool.setFilter(_ldimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_ldimstr_suffix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString suffix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_ldimstr_suffix_init)
    _tool.setFilter(_ldimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_rdimstr_prefix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the RadialDimension you want to change the DimString prefix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_rdimstr_prefix_init)
    _tool.setFilter(_rdimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_rdimstr_suffix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the RadialDimension you want to change the DimString suffix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_rdimstr_suffix_init)
    _tool.setFilter(_rdimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_adimstr_prefix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the AngularDimension you want to change the DimString prefix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_adimstr_prefix_init)
    _tool.setFilter(_adimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_adimstr_suffix_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the AngularDimension you want to change the DimString suffix.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_adimstr_suffix_init)
    _tool.setFilter(_adimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_precision_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString precision.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_precision_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_units_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString units.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_units_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_print_zero_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString print leading zero flag.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_print_zero_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def change_dimstr_print_decimal_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click the dimension you want to change the DimString print trailing decimal flag.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_dimstr_print_decimal_init)
    _tool.setFilter(_dimstring_filter_proc)
    _change_dimstring_init(gtkimage)

def _change_rdim_dia_mode(gtkimage, objlist, tool):
    _init = tool.getHandler('initialize')
    if len(objlist):
        _image = gtkimage.getImage()
        _image.startAction()
        try:
            for _obj in objlist:
                _mode = not _obj.getDiaMode()
                _obj.setDiaMode(_mode)
        finally:
            _image.endAction()
    tool.reset()
    _init(gtkimage)

def _rdim_dia_mode_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pts = _active_layer.find('point', _x, _y)
    if len(_pts) > 0:
        _x, _y = _pts[0].getCoords()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x)
    _ymin = min(_y1, _y)
    _xmax = max(_x1, _x)
    _ymax = max(_y1, _y)
    _objs = []
    for _obj in _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax):
        if isinstance(_obj, RadialDimension):
            _objs.append(_obj)
    _change_rdim_dia_mode(gtkimage, _objs, tool)
    return True

def _rdim_dia_mode_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, RadialDimension):
                    _objs.append(_obj)
            _change_rdim_dia_mode(gtkimage, _objs, tool)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", _rdim_dia_mode_second_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def change_rdim_dia_mode_init(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", change_rdim_dia_mode_init)
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, RadialDimension):
                _objs.append(_obj)
        _change_rdim_dia_mode(gtkimage, _objs, tool)
    else:
        gtkimage.setPrompt(_('Click the RadialDimensions to toggle diameter dimension display'))
        _tool.setHandler("button_press", _rdim_dia_mode_first_button_press_cb)

def _invert_adim(gtkimage, objlist, tool):
    _init = tool.getHandler('initialize')
    if len(objlist):
        _image = gtkimage.getImage()
        _image.startAction()
        try:
            for _obj in objlist:
                _obj.invert()
        finally:
            _image.endAction()
    tool.reset()
    _init(gtkimage)

def _invert_adim_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pts = _active_layer.find('point', _x, _y)
    if len(_pts) > 0:
        _x, _y = _pts[0].getCoords()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x)
    _ymin = min(_y1, _y)
    _xmax = max(_x1, _x)
    _ymax = max(_y1, _y)
    _objs = []
    for _obj in _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax):
        if isinstance(_obj, AngularDimension):
            _objs.append(_obj)
    _invert_adim(gtkimage, _objs, tool)
    return True

def _invert_adim_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, AngularDimension):
                    _objs.append(_obj)
            _invert_adim(gtkimage, _objs, tool)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", _invert_adim_second_button_press_cb)
        gtkimage.setPrompt(_('Click the second point for defining the region'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True
    
def invert_adim_init(gtkimage, tool=None):
    _image = gtkimage.getImage()
    _tool = _image.getTool()
    _tool.setHandler("initialize", invert_adim_init)
    if _image.hasSelection():
        _objs = []
        for _obj in _image.getSelectedObjects():
            if isinstance(_obj, AngularDimension):
                _objs.append()
        _invert_adim(gtkimage, _objs, _tool)
    else:
        gtkimage.setPrompt(_('Click the AngularDimensions to be inverted'))
        _tool.setHandler("button_press", _invert_adim_first_button_press_cb)

#
# arbitrary zoom
#

def zoom_end_button_press_cb(gtkimage, widget, event, tool):
    _xp, _yp = gtkimage.image.getCurrentPoint()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_xp, _x1)
    _ymin = min(_yp, _y1)
    _width, _height = gtkimage.getSize()
    _fw = float(_width)
    _fh = float(_height)
    _wpp = abs(_x1 - _xp)/_fw
    _hpp = abs(_y1 - _yp)/_fh
    if _wpp > _hpp:
        _scale = _wpp
    else:
        _scale = _hpp
    gtkimage.setView(_xmin, _ymin, _scale)
    zoom_init(gtkimage)
    return True

def zoom_motion_notify(gtkimage, widget, event, tool):
    _tx, _ty = tool.getLocation()
    _px, _py = gtkimage.coordToPixTransform(_tx, _ty)
    # width, height = gtkimage.getSize()
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    #
    # it would be nice to draw the rectangle in the current
    # shape of the window ...
    #
    if _cp is not None:
        _xc, _yc = _cp
        _xmin = min(_px, _xc)
        _ymin = min(_py, _yc)
        _rw = abs(_xc - _px)
        _rh = abs(_yc - _py)
        widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    _xmin = min(_x, _px)
    _ymin = min(_y, _py)
    tool.setCurrentPoint(_x, _y)
    _rw = abs(_x - _px)
    _rh = abs(_y - _py)
    widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    return True

def zoom_button_press_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    tool.setLocation(_x, _y)
    tool.setHandler("motion_notify", zoom_motion_notify)
    tool.setHandler("button_press", zoom_end_button_press_cb)
    gtkimage.setPrompt(_('Click a second point to define the zoom window'))
    _gc = gtkimage.getGC()
    _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                            gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
    _gc.set_function(gtk.gdk.INVERT)
    return True

def zoom_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the window.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", zoom_button_press_cb)
#
# Pan Zoom 
#
def zoomPan_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Press Left Mause Button To Make Pan'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", zoomPan_button_press_cb)
def zoomPan_button_press_cb(gtkimage, widget, event, tool):
    gtkimage.setPrompt(_('Press Right Mause Button To Stop Pan'))
    if(gtkimage.isPan()):
        gtkimage.StopPanImage()
    else:    
        gtkimage.StartPanImage()
    return True
