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
# menu functions for creating entities in drawing
# like segments, circles, etc ...
#

from math import hypot, pi, atan2

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sys

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import color
from PythonCAD.Generic import util
from PythonCAD.Generic import units

def make_tuple(text, gdict):
    _tpl = eval(text, gdict)
    if not isinstance(_tpl, tuple):
        raise TypeError, "Invalid tuple: " + `type(_tpl)`
    if len(_tpl) != 2:
        raise ValueError, "Invalid tuple: " + str(_tpl)
    return _tpl

def create_entity(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _init_func = _tool.getHandler("initialize")
    _image = gtkimage.getImage()
    _image.startAction()
    try:
        _tool.create(_image)
    finally:
        _image.endAction()
    _init_func(gtkimage)

#
# points
#

def point_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pc is not None:
        tool.setPoint(_pc[0], _pc[1])
        create_entity(gtkimage)
    return True

def point_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setPoint(_x, _y)
        create_entity(gtkimage)

def point_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", point_mode_init)
    _tool.setHandler("button_press", point_button_press_cb)
    _tool.setHandler("entry_event", point_entry_event_cb)

#
# segments
#

def segment_motion_notify_cb(gtkimage, widget, event, tool):
    """
        Segment notify motion event
    """
    _segs = []
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    firstPnt=tool.getFirstPoint()
    if firstPnt!=None:
        _x1, _y1 = firstPnt
        _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
        _cp = tool.getCurrentPoint()
        if _cp is not None:
            _xc, _yc = _cp
            _segs.append((_px1, _py1, _xc, _yc))
        tool.setCurrentPoint(_x, _y)
        _segs.append((_px1, _py1, _x, _y))
        widget.window.draw_segments(_gc, _segs)
    else:
        print("FirstPnt")
        print("FirstPnt")
    return True

def segment_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0, -1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        create_entity(gtkimage)

def segment_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("button_press", segment_second_button_press_cb)
        tool.setHandler("motion_notify", segment_motion_notify_cb)
        tool.setHandler("entry_event", segment_second_entry_event_cb)
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def segment_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snap = _image.GetSnapObject()
    _x, _y = _image.getCurrentPoint()
    _x1=0
    _y1=0
    if(_snap.DinamicSnap()):
        _x1,_y1,_x,_y=_snap.GetCoords(_x,_y,_tol)
        tool.setFirstPoint(_x1, _y1)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
    tool.setSecondPoint(_x, _y)
    create_entity(gtkimage)
    _snap.ResetDinamicSnap()    
    return True

def segment_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snap = _image.GetSnapObject()
    _x, _y = _image.getCurrentPoint()
    _snap.SetFirstClick(_x,_y,_tol)
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)    
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    if(_x==None or _y==None):
        _x = int(event.x)
        _y = int(event.y)
        _x,_y=gtkimage.coordToPixTransform(_x, _y)
    tool.setFirstPoint(_x, _y)  
    tool.setHandler("button_press", segment_second_button_press_cb)
    tool.setHandler("entry_event", segment_second_entry_event_cb)
    tool.setHandler("motion_notify", segment_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    _snap.StopOneShutSnap()
    return True

def segment_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    gtkimage.getImage().GetSnapObject().ResetDinamicSnap
    _tool.setHandler("initialize", segment_mode_init)
    _tool.setHandler("button_press", segment_first_button_press_cb)
    _tool.setHandler("entry_event", segment_first_entry_event_cb)

#
# rectangles
#

def rectangle_motion_notify_cb(gtkimage, widget, event, tool):
    _x1, _y1 = tool.getFirstPoint()
    _px, _py = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _xmin = min(_px, _xc)
        _ymin = min(_py, _yc)
        _width = abs(_px - _xc)
        _height = abs(_py - _yc)
        widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _width, _height)
    tool.setCurrentPoint(_x, _y)
    _xmin = min(_px, _x)
    _ymin = min(_py, _y)
    _width = abs(_px - _x)
    _height = abs(_py - _y)
    widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _width, _height)
    return True

def rectangle_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        create_entity(gtkimage)

def rectangle_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("button_press", rectangle_second_button_press_cb)
        tool.setHandler("entry_event", rectangle_second_entry_event_cb)
        tool.setHandler("motion_notify", rectangle_motion_notify_cb)
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def rectangle_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setSecondPoint(_x, _y)
    create_entity(gtkimage)
    return True

def rectangle_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setFirstPoint(_x, _y)
    tool.setHandler("button_press", rectangle_second_button_press_cb)
    tool.setHandler("motion_notify", rectangle_motion_notify_cb)
    tool.setHandler("entry_event", rectangle_second_entry_event_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def rectangle_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", rectangle_mode_init)
    _tool.setHandler("button_press", rectangle_first_button_press_cb)
    _tool.setHandler("entry_event", rectangle_first_entry_event_cb)

#
# circles
#

def circle_center_motion_notify_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _upp = gtkimage.getUnitsPerPixel()
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _radius = tool.getRadius()
    if _radius is not None:
        _pr = int(_radius/_upp)
        _xmin = _pcx - _pr
        _ymin = _pcy - _pr
        _cw = _ch = _pr * 2
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                               0, 360*64)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _radius = hypot((_cx - _ix),(_cy - _iy))
    tool.setRadius(_radius)
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _cw = _ch = _pr * 2
    widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                           0, 360*64)
    return True

def circle_radius_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _r = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        tool.setRadius(_r)
        create_entity(gtkimage)

def circle_point_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        tool.setHandler("button_press", circle_radius_button_press_cb)
        tool.setHandler("motion_notify", circle_center_motion_notify_cb)
        tool.setHandler("entry_event", circle_radius_entry_event_cb)
        gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def circle_radius_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _cx, _cy = tool.getCenter()
    _radius = hypot((_cx - _x), (_cy - _y))
    tool.setRadius(_radius)
    create_entity(gtkimage)
    return True

def circle_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setCenter(_x, _y)
    tool.setHandler("button_press", circle_radius_button_press_cb)
    tool.setHandler("motion_notify", circle_center_motion_notify_cb)
    tool.setHandler("entry_event", circle_radius_entry_event_cb)
    gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def circle_center_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", circle_center_button_press_cb)
    _tool.setHandler("entry_event", circle_point_entry_event_cb)
    _tool.setHandler("initialize", circle_center_mode_init)

#
# circle from two points
#

def circle_tp_motion_notify_cb(gtkimage, widget, event, tool):
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _radius = tool.getRadius()
    _upp = gtkimage.getUnitsPerPixel()
    if _radius is not None:
        _cx, _cy = tool.getCenter()
        _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
        _pr = int(_radius/_upp)
        _xmin = _pcx - _pr
        _ymin = _pcy - _pr
        _cw = _ch = _pr * 2
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                               0, 360*64)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    tool.setSecondPoint(_ix, _iy)
    _cx, _cy = tool.getCenter()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _radius = tool.getRadius()
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _cw = _ch = _pr * 2
    widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                           0, 360*64)
    return True

def circle_tp_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setSecondPoint(_x, _y)
    create_entity(gtkimage)
    return True

def circle_tp_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setFirstPoint(_x, _y)
    tool.setHandler("button_press", circle_tp_second_button_press_cb)
    tool.setHandler("motion_notify", circle_tp_motion_notify_cb)
    tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def circle_tp_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        create_entity(gtkimage)

def circle_tp_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("motion_notify", circle_tp_motion_notify_cb)
        tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
        gtkimage.setPrompt(_('Enter another point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def circle_tp_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", circle_tp_first_button_press_cb)
    _tool.setHandler("entry_event", circle_tp_first_entry_event_cb)
    _tool.setHandler("initialize", circle_tp_mode_init)

#
# arcs
#

def arc_center_end_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    _cx, _cy = tool.getCenter()
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _angle = (180.0/pi) * atan2((_y - _cy),(_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setEndAngle(_angle)
    create_entity(gtkimage)
    return True

def arc_angle_motion_notify_cb(gtkimage, widget, event, tool):
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _cx, _cy = tool.getCenter() # arc center
    _radius = tool.getRadius()
    _sa = tool.getStartAngle()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _upp = gtkimage.getUnitsPerPixel()
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _cw = _ch = _pr * 2
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _ea = tool.getEndAngle()
    _win = widget.window
    if _ea is not None:
        if _sa < _ea:
            _sweep = _ea - _sa
        else:
            _sweep = 360.0 - (_sa - _ea)
        _win.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                      int(_sa * 64), int(_sweep * 64))
    _ea = (180.0/pi) * atan2((_iy - _cy), (_ix - _cx))
    if _ea < 0.0:
        _ea = _ea + 360.0
    tool.setEndAngle(_ea)
    if _sa < _ea:
        _sweep = _ea - _sa
    else:
        _sweep = 360.0 - (_sa - _ea)
    _win.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                  int(_sa * 64), int(_sweep * 64))
    return True

def arc_start_angle_button_press_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter()
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _angle = (180.0/pi) * atan2((_y - _cy), (_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setStartAngle(_angle)
    tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
    tool.setHandler("entry_event", arc_center_ea_entry_event_cb)
    gtkimage.setPrompt(_('Enter the end angle of the arc.'))
    return True

def arc_center_ea_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_c_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setEndAngle(_angle)
        create_entity(gtkimage)

def arc_center_sa_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_c_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setStartAngle(_angle)
        tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
        tool.setHandler("entry_event", arc_center_ea_entry_event_cb)
        gtkimage.setPrompt(_('Enter the end angle of the arc.'))

def arc_center_radius_button_press_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter()
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    _radius = hypot((_x - _cx), (_y - _cy))
    tool.setRadius(_radius)
    _angle = (180.0/pi) * atan2((_y - _cy), (_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setStartAngle(_angle)
    tool.delHandler("entry_event")
    tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
    gtkimage.refresh()
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    tool.setHandler("button_press", arc_center_end_button_press_cb)
    gtkimage.setPrompt(_('Click in the drawing area to finish the arc'))
    return True

def arc_center_radius_entry_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _r = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        tool.setRadius(_r)
        tool.setHandler("entry_event", arc_center_sa_entry_event_cb)
        tool.setHandler("button_press", arc_start_angle_button_press_cb)
        gtkimage.setPrompt(_('Enter the start angle of the arc.'))

def arc_radius_motion_notify_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _radius = tool.getRadius()
    _upp = gtkimage.getUnitsPerPixel()
    if _radius is not None:
        _pr = int(_radius/_upp)
        _xmin = _pcx - _pr
        _ymin = _pcy - _pr
        _cw = _ch = _pr * 2
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                               0, 360*64)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _radius = hypot((_cx - _ix), (_cy - _iy))
    tool.setRadius(_radius)
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _cw = _ch = _pr * 2
    widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,
                           0, 360*64)
    return True

def arc_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setCenter(_x, _y)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    tool.setHandler("motion_notify", arc_radius_motion_notify_cb)
    tool.setHandler("entry_event", arc_center_radius_entry_cb)
    tool.setHandler("button_press", arc_center_radius_button_press_cb)
    gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
    return True

def arc_center_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
        tool.setHandler("motion_notify", arc_radius_motion_notify_cb)
        tool.setHandler("button_press", arc_center_radius_button_press_cb)
        tool.setHandler("entry_event", arc_center_radius_entry_cb)
        gtkimage.setPrompt(_('Enter the arc radius or click in the drawing area'))

def arc_center_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", arc_center_button_press_cb)
    _tool.setHandler("entry_event", arc_center_entry_event_cb)
    _tool.setHandler("initialize", arc_center_mode_init)

#
# chamfers
#

def chamfer_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _new_pt = _image.findPoint(_x, _y, _tol)
    if _pt is not None and not _new_pt:
        _active_layer = _image.getActiveLayer()
        _users = _pt.getUsers()
        if len(_users) != 2:
            return
        _s1 = _s2 = None        
        for _user in _users:
            if not isinstance(_user, Segment):
                return
            if _s1 is None:
                _s1 = _user
            else:
                _s2 = _user
        _len = _image.getOption('CHAMFER_LENGTH')
        _s = _image.getOption('LINE_STYLE')
        _l = _image.getOption('LINE_TYPE')
        _c = _image.getOption('LINE_COLOR')
        _t = _image.getOption('LINE_THICKNESS')
        #
        # the following is a work-around that needs to
        # eventually be replaced ...
        #
        _p1, _p2 = _s1.getEndpoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _slen = _s1.length()
        _factor = 2.0
        _r = (_slen - (_len/_factor))/_slen
        _xn = _x1 + _r * (_x2 - _x1)
        _yn = _y1 + _r * (_y2 - _y1)
        _pts = _active_layer.find('point', _xn, _yn)
        while len(_pts) > 0:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = (_slen - (_len/_factor))/_slen
            _xn = _x1 + _r * (_x2 - _x1)
            _yn = _y1 + _r * (_y2 - _y1)
            _pts = _active_layer.find('point', _xn, _yn)
        if len(_pts) == 0:
            _image.startAction()
            try:
                _pc = Point(_xn, _yn)
                _active_layer.addObject(_pc)
                if _pt is _p1:
                    _s1.setP1(_pc)
                elif _pt is _p2:
                    _s1.setP2(_pc)
                else:
                    raise ValueError, "Unexpected endpoint: " + str(_pc)
                _ptx, _pty = _pt.getCoords()
                _pc.setCoords(_ptx, _pty)
                _chamfer = Chamfer(_s1, _s2, _len, _s)
                if _l != _s.getLinetype():
                    _chamfer.setLinetype(_l)
                if _c != _s.getColor():
                    _chamfer.setColor(_c)
                if abs(_t - _s.getThickness()) > 1e-10:
                    _chamfer.setThickness(_t)
                _active_layer.addObject(_chamfer)
            finally:
                _image.endAction()
    return True

def chamfer_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the points where you want a chamfer.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", chamfer_button_press_cb)

#
# fillet
#

def fillet_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _new_pt = _image.findPoint(_x, _y, _tol)
    if _pt is not None and not _new_pt:
        _active_layer = _image.getActiveLayer()
        _users = _pt.getUsers()
        if len(_users) != 2:
            return
        _s1 = _s2 = None        
        for _user in _users:
            if not isinstance(_user, Segment):
                return
            if _s1 is None:
                _s1 = _user
            else:
                _s2 = _user
        _rad = _image.getOption('FILLET_RADIUS')
        _s = _image.getOption('LINE_STYLE')
        _l = _image.getOption('LINE_TYPE')
        _c = _image.getOption('LINE_COLOR')
        _t = _image.getOption('LINE_THICKNESS')
        #
        # the following is a work-around that needs to
        # eventually be replaced ...
        #
        _p1, _p2 = _s1.getEndpoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _slen = _s1.length()
        _factor = 2.0
        _r = 1.0 - (_slen/_factor)
        _xn = _x1 + _r * (_x2 - _x1)
        _yn = _y1 + _r * (_y2 - _y1)
        _pts = _active_layer.find('point', _xn, _yn)
        while len(_pts) > 0:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = 1.0 - (_slen/_factor)
            _xn = _x1 + _r * (_x2 - _x1)
            _yn = _y1 + _r * (_y2 - _y1)
            _pts = _active_layer.find('point', _xn, _yn)
        if len(_pts) == 0:
            _image.startAction()
            try:
                _pc = Point(_xn, _yn)
                _active_layer.addObject(_pc)
                if _pt is _p1:
                    _s1.setP1(_pc)
                elif _pt is _p2:
                    _s1.setP2(_pc)
                else:
                    raise ValueError, "Unexpected endpoint: " + str(_pc)
                _ptx, _pty = _pt.getCoords()
                _pc.setCoords(_ptx, _pty)
                _fillet = Fillet(_s1, _s2, _rad, _s)
                if _l != _s.getLinetype():
                    _fillet.setLinetype(_l)
                if _c != _s.getColor():
                    _fillet.setColor(_c)
                if abs(_t - _s.getThickness()) > 1e-10:
                    _fillet.setThickness(_t)
                _active_layer.addObject(_fillet)
            finally:
                _image.endAction()
    return True

def fillet_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the points where you want a fillet.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", fillet_button_press_cb)

#
# leader lines
#

def leader_second_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x2, _y2 = tool.getMidPoint()
    _px2, _py2 = gtkimage.coordToPixTransform(_x2, _y2)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px2, _py2, _xc, _yc))
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px2, _py2, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True

def leader_first_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x1, _y1 = tool.getFirstPoint()
    _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px1, _py1, _xc, _yc))
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px1, _py1, _x, _y))
    widget.window.draw_segments(_gc, _segs)

def leader_final_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setFinalPoint(_x, _y)
    create_entity(gtkimage)
    gtkimage.setPrompt(_('Click in the drawing area to place the initial point'))
    return True

def leader_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setMidPoint(_x, _y)
    tool.clearCurrentPoint()
    tool.setHandler("motion_notify", leader_second_motion_notify_cb)
    tool.setHandler("button_press", leader_final_button_press_cb)
    gtkimage.setPrompt(_('Click in the drawing area to place the final point'))
    return True

def leader_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setFirstPoint(_x, _y)
    tool.setHandler("motion_notify", leader_first_motion_notify_cb)
    tool.setHandler("button_press", leader_second_button_press_cb)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    gtkimage.setPrompt(_('Click in the drawing area to place the second point'))
    return True

def leader_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area to enter the first point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", leader_mode_init)
    _tool.setHandler("button_press", leader_first_button_press_cb)

#
# polylines
#

def polyline_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x1, _y1 = tool.getPoint(-1)
    _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px1, _py1, _xc, _yc))
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px1, _py1, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True

def polyline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.clearCurrentPoint()
    tool.storePoint(_x, _y)
    _state = event.state
    if ((_state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK):
        create_entity(gtkimage)
    else:
        tool.setHandler("motion_notify", polyline_motion_notify_cb)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
        gtkimage.setPrompt(_('Click to place the next point. Shift-click to finish polyline'))
    return True

def polyline_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        if _text == 'end':
            create_entity(gtkimage)
        else:
            _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
            tool.setPoint(_x, _y)
            tool.setHandler("motion_notify", polyline_motion_notify_cb)
            gtkimage.getGC().set_function(gtk.gdk.INVERT)
            gtkimage.setPrompt(_('Click to place the next point. Shift-click to finish polyline.'))

def polyline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area to enter the first point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", polyline_mode_init)
    _tool.setHandler("entry_event", polyline_entry_event_cb)
    _tool.setHandler("button_press", polyline_button_press_cb)

#
# polygons
#

def polygon_radius_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setLocation(_x, _y)
    create_entity(gtkimage)
    return True

def polygon_radius_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    _count = tool.getSideCount()
    if _cp is not None:
        _tx0, _ty0 = tool.getCoord(0)
        _px0, _py0 = gtkimage.coordToPixTransform(_tx0, _ty0)
        _px1 = _px0
        _py1 = _py0
        for _i in range(1, _count):
            _txi, _tyi = tool.getCoord(_i)
            _pxi, _pyi = gtkimage.coordToPixTransform(_txi, _tyi)
            _segs.append((_px1, _py1, _pxi, _pyi))
            _px1 = _pxi
            _py1 = _pyi
        _segs.append((_px1, _py1, _px0, _py0))
    tool.setCurrentPoint(_x, _y)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    tool.setLocation(_ix, _iy)
    _tx0, _ty0 = tool.getCoord(0)
    _px0, _py0 = gtkimage.coordToPixTransform(_tx0, _ty0)
    _px1 = _px0
    _py1 = _py0
    for _i in range(1, _count):
        _txi, _tyi = tool.getCoord(_i)
        _pxi, _pyi = gtkimage.coordToPixTransform(_txi, _tyi)
        _segs.append((_px1, _py1, _pxi, _pyi))
        _px1 = _pxi
        _py1 = _pyi
    _segs.append((_px1, _py1, _px0, _py0))
    widget.window.draw_segments(_gc, _segs)
    return True

def polygon_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    else:
        _x, _y = _pc
    tool.setCenter(_x, _y)
    tool.setHandler("motion_notify", polygon_radius_motion_notify_cb)
    tool.setHandler("button_press", polygon_radius_button_press_cb)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    gtkimage.setPrompt(_('Click in the drawing area to place the second point'))
    return True

def polygon_center_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        tool.setHandler("motion_notify", polygon_radius_motion_notify_cb)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)        
        tool.setHandler("button_press", polygon_radius_button_press_cb)
        tool.delHandler("entry_event") # ???
        gtkimage.setPrompt(_('Click in the drawing area to draw the polygon'))

def polygon_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area to define the center'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", polygon_mode_init)
    _tool.setHandler("entry_event", polygon_center_entry_event_cb)
    _tool.setHandler("button_press", polygon_center_button_press_cb)

#
# set the active style
#

def set_active_style(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Active Style'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Style:'))
    _image = gtkimage.getImage()
    _cur_style = _image.getOption('LINE_STYLE')
    _styles = _image.getImageEntities("style")
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cur_style:
                _idx = _i
            _widget.append_text(_s.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cur_style:
                _idx = _i
            _item = gtk.MenuItem(_s.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _image.setOption('LINE_STYLE', _styles[_idx])
    _dialog.destroy()

#
# set the current color
#

def set_active_color(gtkimage):
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
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _gtk_color = _colorsel.get_current_color()
        _r = int(round((_gtk_color.red/65535.0) * 255.0))
        _g = int(round((_gtk_color.green/65535.0) * 255.0))
        _b = int(round((_gtk_color.blue/65535.0) * 255.0))
        _color = None
        for _c in _image.getImageEntities('color'):
            if _c.r == _r and _c.g == _g and _c.b == _b:
                _color = _c
                break
        if _color is None:
            _color = color.Color(_r, _g, _b)
        _image.setOption('LINE_COLOR', _color)
    _dialog.destroy()

#
# set the current linetype
#

def set_active_linetype(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Active Linetype'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)

    _label = gtk.Label(_('Linetype:'))
    _hbox.pack_start(_label, False, False, 0)
    _image = gtkimage.getImage()
    _cur_linetype = _image.getOption('LINE_TYPE')
    _linetypes = _image.getImageEntities("linetype")
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _cur_linetype:
                _idx = _i
            _widget.append_text(_lt.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _cur_linetype:
                _idx = _i
            _item = gtk.MenuItem(_lt.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _image.setOption('LINE_TYPE', _linetypes[_idx])
    _dialog.destroy()

#
# set the current line thickness
#

def move_cursor(entry):
    entry.set_position(-1)
    return False

def thickness_activate(entry): # this probably isn't a good choice ...
    entry.stop_emission("activate")

def thickness_focus_out(entry, event):
    _text = entry.get_text()
    if _text == '-' or _text == '+':
        entry.delete_text(0, -1)
    return False

def thickness_insert_text(entry, new_text, new_text_length, position):
    if (new_text.isdigit() or
        new_text == '.' or
        new_text == '+'):
        _string = entry.get_text() + new_text[:new_text_length]
        _hid = entry.get_data('handlerid')
        entry.handler_block(_hid)
        try:
            _pos = entry.get_position()
            if _string == '+':
                _pos = entry.insert_text(new_text, _pos)
            else:
                try:
                    _val = float(_string)
                    _pos = entry.insert_text(new_text, _pos)
                except StandardError, e:
                    pass
        finally:
            entry.handler_unblock(_hid)
        if hasattr(gobject, 'idle_add'):
            gobject.idle_add(move_cursor, entry)
        else:
            gtk.idle_add(move_cursor, entry)
    entry.stop_emission("insert-text")

def set_line_thickness(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Line Thickness'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK,
                          gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL,
                          gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Thickness:'))
    _hbox.pack_start(_label, False, False, 0)
    _image = gtkimage.getImage()
    _thickness = "%g" % _image.getOption('LINE_THICKNESS')
    _entry = gtk.Entry()
    _entry.set_text(_thickness)
    _entry.connect("focus_out_event", thickness_focus_out)
    _entry.connect("activate", thickness_activate)
    _handlerid = _entry.connect("insert-text", thickness_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _hbox.pack_start(_entry, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _text = _entry.get_text()
        _thickness = float(_text)
        _image.setOption('LINE_THICKNESS', _thickness)
    _dialog.destroy()

#

def _selectColor(button):
    _s = _('Select Color')
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_s)
    _colorsel = _dialog.colorsel
    _colorsel.set_previous_color(_color)
    _colorsel.set_current_color(_color)
    _colorsel.set_has_palette(True)
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _r, _g, _b = _get_rgb_values(_colorsel.get_current_color())
        _str = "#%02x%02x%02x" % (_r, _g, _b)
        _color = gtk.gdk.color_parse(_str)
        _da.modify_bg(gtk.STATE_NORMAL, _color)
    _dialog.destroy()

def _fill_color_dialog(dvbox, widgets):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Color Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Inactive Layer Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['INACTIVE_LAYER_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Background Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['BACKGROUND_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Single Point Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['SINGLE_POINT_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Multi-Point Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['MULTI_POINT_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)    

def _selectColor(button):
    _s = _('Select Color')
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_s)
    _colorsel = _dialog.colorsel
    _colorsel.set_previous_color(_color)
    _colorsel.set_current_color(_color)
    _colorsel.set_has_palette(True)
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _r, _g, _b = _get_rgb_values(_colorsel.get_current_color())
        _str = "#%02x%02x%02x" % (_r, _g, _b)
        _color = gtk.gdk.color_parse(_str)
        _da.modify_bg(gtk.STATE_NORMAL, _color)
    _dialog.destroy()

def _get_color_da():
    _widget = gtk.Button()
    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
    _frame.set_border_width(5)
    _widget.add(_frame)
    _da = gtk.DrawingArea()
    _da.set_size_request(20, 10)
    _widget.connect('clicked', _select_color)
    _frame.add(_da)
    return _widget

def _get_widget(col):
    if hasattr(gtk, 'ColorButton'):
        _widget = gtk.ColorButton()
        _widget.set_color(col)
    else:
        _widget = _get_color_da()
        _widget.modify_bg(gtk.STATE_NORMAL, col)
    return _widget

def _get_color_widgets(opts, im):
    _widgets = {}
    for _opt in opts:
        _color = gtk.gdk.color_parse(str(im.getOption(_opt)))
        _widgets[_opt] = _get_widget(_color)
    return _widgets

def _get_color(widgets, key):
    _widget = widgets[key]
    if hasattr(gtk, 'ColorButton'):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.Button):
        _da = _widget.getChild().getChild()
        _color= _da.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
    return _color
    
def set_colors_dialog(gtkimage):
    _opts = ['INACTIVE_LAYER_COLOR',
             'BACKGROUND_COLOR',
             'SINGLE_POINT_COLOR',
             'MULTI_POINT_COLOR']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Color Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = _get_color_widgets(_opts, _image)
    _fill_color_dialog(_dialog.vbox, _widgets)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _color = _get_color(_widgets, _opt)
            _r = int(round((_color.red/65535.0) * 255.0))
            _g = int(round((_color.green/65535.0) * 255.0))
            _b = int(round((_color.blue/65535.0) * 255.0))
            if (_r, _g, _b) != _image.getOption(_opt).getColors():
                _image.setOption(_opt, color.Color(_r, _g, _b))
    _widgets.clear()
    _dialog.destroy()

#

def _size_move_cursor(entry):
    entry.set_position(-1)
    return False

def _size_entry_activate(entry):
    _text = entry.get_text()
    entry.delete_text(0, -1)
    if len(_text):
        if _text == '-' or _text == '+':
            sys.stderr.write("Incomplete value: '%s'\n" % _text)
        else:
            try:
                _value = float(_text)
            except:
                sys.stderr.write("Invalid float: '%s'\n" % _text)
    else:
        sys.stderr.write("Empty entry box.")

def _size_entry_focus_out(entry, event, text=''):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        _size = entry.get_data('size')
        _hid = entry.get_data('handlerid')
        entry.delete_text(0, -1)
        entry.handler_block(_hid)
        try:
            entry.set_text(_size)
        finally:
            entry.handler_unblock(_hid)
    return False

def _size_entry_insert_text(entry, new_text, new_text_length, position):
    if (new_text.isdigit() or
        new_text == '.' or
        new_text == '+'):
        _string = entry.get_text() + new_text[:new_text_length]
        _hid = entry.get_data('handlerid')
        _move = True
        entry.handler_block(_hid)
        try:
            _pos = entry.get_position()
            if _string == '+':
                _pos = entry.insert_text(new_text, _pos)
            else:
                try:
                    _val = float(_string)
                except StandardError, e:
                    _move = False
                else:
                    _pos = entry.insert_text(new_text, _pos)
        finally:
            entry.handler_unblock(_hid)
        if _move:
            if hasattr(gobject, 'idle_add'):
                gobject.idle_add(_size_move_cursor, entry)
            else:
                gtk.idle_add(_size_move_cursor, entry)
    entry.stop_emission('insert-text')

def _fill_size_dialog(dvbox, widgets):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Size Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Chamfer length:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['CHAMFER_LENGTH']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Fillet Radius:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['FILLET_RADIUS']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Leader Arrow Size:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['LEADER_ARROW_SIZE']
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)    

def set_sizes_dialog(gtkimage):
    _opts = ['CHAMFER_LENGTH',
             'FILLET_RADIUS',
             'LEADER_ARROW_SIZE']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Size Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = {}
    for _opt in _opts:
        _val = _image.getOption(_opt)
        _entry = gtk.Entry()
        _sval = "%f" % _val
        _entry.set_data('size', _sval)
        _entry.set_text(_sval)
        _handlerid = _entry.connect('insert-text', _size_entry_insert_text)
        _entry.set_data('handlerid', _handlerid)
        _entry.connect('activate', _size_entry_activate)
        _entry.connect('focus-out-event', _size_entry_focus_out)
        _widgets[_opt] = _entry
    _fill_size_dialog(_dialog.vbox, _widgets)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _text = _widgets[_opt].get_text()
            _ival = _image.getOption(_opt)
            if len(_text) and _text != '+':
                _value = float(_text)
            else:
                _value = _ival
            if abs(_value - _ival) > 1e-10:
                _image.setOption(_opt, _value)
    _widgets.clear()
    _dialog.destroy()

#

def set_toggle_dialog(gtkimage):
    _opts = ['AUTOSPLIT', 'HIGHLIGHT_POINTS']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Operation Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = {}
    for _opt in _opts:
        _val = _image.getOption(_opt)
        if _opt == 'AUTOSPLIT':
            _str = _('New Points split existing entities')
        else:
            _str = _('Boxes are drawn around Point objects')
        _cb = gtk.CheckButton(_str)
        _cb.set_active(_val)
        _widgets[_opt] = _cb
    _frame = gtk.Frame(_('Operation Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    _vbox.pack_start(_widgets['AUTOSPLIT'], True, True, 2)
    _vbox.pack_start(_widgets['HIGHLIGHT_POINTS'], True, True, 2)
    _dialog.vbox.pack_start(_frame, False, False, 2)            
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _val = _widgets[_opt].get_active()
            _image.setOption(_opt, _val)
    _widgets.clear()
    _dialog.destroy()

def set_units_dialog(gtkimage):
    _units = units.Unit.getUnitStrings()
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Image Units'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _unit = _image.getUnits()
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_units)):
            _ui = _units[_i]
            if _unit == units.Unit.getUnitFromString(_ui):
                _idx = _i
            _widget.append_text(_ui)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_units)):
            _ui = _units[_i]
            if _unit is _units.Unit.getUnitFromString(_ui):
                _idx = _i
            _item = gtk.MenuItem(_ui)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _vbox = _dialog.vbox
    _vbox.set_border_width(5)
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Units:'))
    _hbox.pack_start(_label, False, False, 2)
    _hbox.pack_start(_widget, False, False, 2)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if hasattr(gtk, 'ComboBox'):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget " + `type(_widget)`
        _val = units.Unit.getUnitFromString(_units[_idx])
        if _val != _unit:
            _image.setUnits(_val)
    _dialog.destroy()
