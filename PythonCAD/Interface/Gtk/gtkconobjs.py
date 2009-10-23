#
# Copyright (c) 2002, 2003, 2004, 2006, 2007 Art Haas
#
#               2009 Matteo Boscolo
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
# the event handling bits for construction lines
# and circles
#

import math

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.color import Color
from PythonCAD.Generic import util

from PythonCAD.Interface.Gtk import gtkentities
from PythonCAD.Generic import snap
from PythonCAD.Generic.pyGeoLib import Vector

# horizontal construction lines
#

def hcline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setPoint,_tol,_snapArray)
    gtkentities.create_entity(gtkimage)

def hcline_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _val = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setPoint(0.0, _val)
        gtkentities.create_entity(gtkimage)
            
def hcline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_("Click in the drawing area or enter 'y' coordinate:"))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", hcline_mode_init)
    _tool.setHandler("button_press", hcline_button_press_cb)
    _tool.setHandler("entry_event", hcline_entry_event_cb)

#
# vertical construction lines
#

def vcline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setPoint,_tol,_snapArray)
    gtkentities.create_entity(gtkimage)

def vcline_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _val = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setPoint(_val, 0.0)
        gtkentities.create_entity(gtkimage)

def vcline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_("Click in the drawing area or enter 'x' coordinate:"))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", vcline_mode_init)
    _tool.setHandler("button_press", vcline_button_press_cb)
    _tool.setHandler("entry_event", vcline_entry_event_cb)

#
# common functions for for acline, cline, and ccircle objects
#

def make_tuple(text, gdict):
    _tpl = eval(text, gdict)
    if not isinstance(_tpl, tuple):
        raise TypeError, "Invalid tuple: " + `type(_tpl)`
    if len(_tpl) != 2:
        raise ValueError, "Invalid tuple: " + str(_tpl)
    return _tpl
    
#
# angled construction lines
#

def acline_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _ax, _ay = tool.getPoint().point.getCoords()
    _pax, _pay = gtkimage.coordToPixTransform(_ax, _ay)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_pax, _pay, _xc, _yc))
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setDinamicSnap(gtkimage,tool.setLocation,_snapArray)
    tool.setCurrentPoint(_x, _y)
    _segs.append((_pax, _pay, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True
        
def acline_entry_make_angle(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setAngle(_angle)
        gtkentities.create_entity(gtkimage)

def acline_entry_make_pt(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setPoint(_x, _y)
        tool.setHandler("button_press", acline_second_button_press_cb)
        tool.setHandler("entry_event", acline_entry_make_angle)
        tool.setHandler("motion_notify", acline_motion_notify_cb)
        gtkimage.setPrompt(_('Enter the angle or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def acline_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setLocation,_tol,_snapArray)
    gtkentities.create_entity(gtkimage)
    return True

def acline_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setPoint,_tol,_snapArray)
    tool.setHandler("button_press", acline_second_button_press_cb)
    tool.setHandler("entry_event", acline_entry_make_angle)
    tool.setHandler("motion_notify", acline_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the angle or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def acline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", acline_mode_init)
    _tool.setHandler("button_press", acline_first_button_press_cb)
    _tool.setHandler("entry_event", acline_entry_make_pt)

#
# two point construction line
#

def cline_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x1, _y1 = tool.getFirstPoint().point.getCoords()
    _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px1, _py1, _xc, _yc))
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setDinamicSnap(gtkimage,tool.setSecondPoint,_snapArray)
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px1, _py1, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True

def cline_second_entry_make_pt(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        gtkentities.create_entity(gtkimage)

def cline_first_entry_make_pt(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("button_press", cline_second_button_press_cb)
        tool.setHandler("motion_notify", cline_motion_notify_cb)
        tool.setHandler("entry_event", cline_second_entry_make_pt)
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def cline_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setSecondPoint,_tol,_snapArray)
    gtkentities.create_entity(gtkimage)
    return True

def cline_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setFirstPoint,_tol,_snapArray)
    tool.setHandler("button_press", cline_second_button_press_cb)
    tool.setHandler("entry_event", cline_second_entry_make_pt)
    tool.setHandler("motion_notify", cline_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", cline_mode_init)
    _tool.setHandler("button_press", cline_first_button_press_cb)
    _tool.setHandler("entry_event", cline_first_entry_make_pt)

#
# construction circles
#

def ccircle_cpmode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", gtkentities.circle_center_button_press_cb)
    _tool.setHandler("entry_event", gtkentities.circle_point_entry_event_cb)
    _tool.setHandler("initialize", ccircle_cpmode_init)

#
# two-point construction circle
#

def ccircle_tpmode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", gtkentities.circle_tp_first_button_press_cb)
    _tool.setHandler("entry_event", gtkentities.circle_tp_first_entry_event_cb)
    _tool.setHandler("initialize", ccircle_tpmode_init)

#
# perpendicular construction line creation
#
def perp_cline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _pt,_pc=snap.getSnapPoint(_image,_tol,_snapArray).point.getCoords()
    _active_layer = _image.getActiveLayer()
    _hits = _active_layer.mapPoint((_pt,_pc), _tol, 1)
    if len(_hits):
        _obj, _lp = _hits[0]
        _pcl = None
        if isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            else:
                _slope = (180.0/math.pi) * math.atan2((_p2y - _p1y),
                                                      (_p2x - _p1x)) + 90.0
                _pcl = ACLine(_lp, _slope)
        elif isinstance(_obj, (Circle, Arc, CCircle)):
            _cp = _obj.getCenter()
            _pcl = CLine(_cp, _lp)
        elif isinstance(_obj, HCLine):
            _pcl = VCLine(_lp)
        elif isinstance(_obj, VCLine):
            _pcl = HCLine(_lp)
        elif isinstance(_obj, ACLine):
            _angle = _obj.getAngle()
            if abs(_angle) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            else:
                _slope = _angle + 90.0
                _pcl = ACLine(_lp, _slope)
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            else:
                _slope = (180.0/math.pi) * math.atan2((_p2y - _p1y),
                                                      (_p2x - _p1x)) + 90.0
                _pcl = ACLine(_lp, _slope)
        else:
            pass
        _image.startAction()
        try:
            if _lp.getParent() is None:
                _active_layer.addObject(_lp)
            if _pcl is not None:
                _active_layer.addObject(_pcl)
        finally:
            _image.endAction()
    return True

def perpendicular_cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the object you want a perpendicular to'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", perp_cline_button_press_cb)

#
# tangent cline creation
#

def tangent_cline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'tangent':False}
    _pt=snap.getOnlySnap(_image,_tol,_snapArray)
    if _pt is not None:
        _x, _y = _pt.point.getCoords()
        _layer = _image.getActiveLayer()
        _rtd = 180.0/math.pi
        _cobj = None
        _angle = None
        _circleEnt=_pt.entity
        if isinstance(_circleEnt,(CCircle,Circle,Arc)):
            _cp=_circleEnt.getCenter()
            _rad = _circleEnt.getRadius()
            _v=Vector(_cp,_pt.point).Mag()
            _v.Mult(_rad)
            _vectPoint=_v.Point()
            _x,_y=(_vectPoint+_cp)
            _cx,_cy=_cp.getCoords()
            if abs(math.hypot((_x - _cx), (_y - _cy)) - _rad) < 1e-10:
                _cobj = _circleEnt
                _angle = _rtd * math.atan2((_y - _cy), (_x - _cx))
                if _angle < 0.0:
                    _angle = _angle + 360.0
                _pt=Point(_x,_y)
        if _cobj is not None:
            _image.startAction()
            try:
                if _pt:
                    _layer.addObject(_pt)
                if (abs(_angle) < 1e-6 or
                    abs(_angle - 180.0) < 1e-6 or
                    abs(_angle - 360.0) < 1e-6):
                    _tcl = VCLine(_pt)
                elif (abs(_angle - 90.0) < 1e-6 or
                      abs(_angle - 270.0) < 1e-6):
                    _tcl = HCLine(_pt)
                else:
                    _slope = _angle + 90.0
                    _tcl = ACLine(_pt, _slope)
                _layer.addObject(_tcl)
            finally:
                _image.endAction()
    return True

def tangent_cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the circle object you want a tangent to'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", tangent_cline_button_press_cb)

#
# parallel offset mode
#

def parallel_refpt_button_press_cb(gtkimage, widget, event, tool):
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    tool.setReferencePoint(_x, _y)
    _init_func = tool.getHandler("initialize")
    _image.startAction()
    try:
    	tool.create(gtkimage.image)
    finally:
    	_image.endAction()
    _init_func(gtkimage)
    return True

def parallel_conline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (HCLine, VCLine, ACLine, CLine)):
                    tool.setConstructionLine(_obj)
                    tool.setHandler("button_press", parallel_refpt_button_press_cb)
                    gtkimage.setPrompt(_('Click on the side to place the new construction line.'))

def parallel_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _snp=snap.getSnapPoint(_image,_tol,_snapArray)
    _x,_y=_snp.point.getCoords()
    print "Debug: " + str(tool.getLocation())
    _x1, _y1 = tool.getLocation()
    _offset = math.hypot((_x - _x1), (_y - _y1))
    tool.setOffset(_offset)
    tool.setHandler("button_press", parallel_conline_button_press_cb)
    gtkimage.setPrompt(_('Click on the reference construction line.'))
    return True

def parallel_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _x1,_y1=snap.getSnapPoint(_image,_tol,_snapArray).point.getCoords()
    tool.setLocation(_x1,_y1)
    tool.setHandler("button_press", parallel_second_button_press_cb)
    tool.delHandler("entry_event")
    gtkimage.setPrompt(_('Click another point to define the offset distance.'))
    return True

def parallel_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _dist = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setOffset(_dist)
        tool.delHandler("entry_event")
        tool.setHandler("button_press", parallel_conline_button_press_cb)
        gtkimage.setPrompt(_('Click on the reference construction line.'))

def parallel_offset_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Enter the distance or click in the drawing area.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", parallel_offset_mode_init)
    _tool.setHandler("button_press", parallel_first_button_press_cb)
    _tool.setHandler("entry_event", parallel_entry_event)

#
# construction circle tangent to a construction line
#

def ccircle_single_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _x,_y=snap.getSnapPoint(_image,_tol,_snapArray).point.getCoords()
    tool.setLocation(_x, _y)
    gtkentities.create_entity(gtkimage)
    return True

def ccircle_single_motion_notify_cb(gtkimage, widget, event, tool):
    _gc = gtkimage.getGC()
    _upp = gtkimage.getUnitsPerPixel()
    _rect = tool.getPixelRect()
    if _rect is not None:
        _xmin, _ymin, _width, _height = _rect
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _width, _height,
                               0, 360*64)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    tool.setLocation(_ix, _iy)
    _cx, _cy = tool.getCenter()
    _radius = tool.getRadius()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _width = _height = _pr * 2
    tool.setPixelRect(_xmin, _ymin, _width, _height)
    widget.window.draw_arc(_gc, False, _xmin, _ymin, _width, _height,
                           0, 360*64)
    return True

def ccircle_single_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'tangent':True}
    ent=snap.getOnlySnap(_image,_tol,_snapArray).entity
    if ent is not None:
        _active_layer = _image.getActiveLayer()
        if isinstance(ent, (HCLine, VCLine, ACLine, CLine, CCircle)):
            tool.setConstructionLine(ent)
            tool.setHandler("button_press", ccircle_single_second_button_press_cb)
            tool.setHandler("motion_notify", ccircle_single_motion_notify_cb)
            gtkimage.setPrompt(_('Click where the circle should be drawn.'))
            gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def tangent_ccircle_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the construction object used for tangency.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", tangent_ccircle_mode_init)
    _tool.setHandler("button_press", ccircle_single_first_button_press_cb)

#
# construction circle between two construction lines
#

def two_cline_set_circle_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False}
    _x,_y=snap.getSnapPoint(_image,_tol,_snapArray).point.getCoords()    
    tool.setLocation(_x, _y)
    gtkentities.create_entity(gtkimage)

def two_cline_motion_notify_cb(gtkimage, widget, event, tool):
    _gc = gtkimage.getGC()
    _upp = gtkimage.getUnitsPerPixel()
    _rect = tool.getPixelRect()
    if _rect is not None:
        _xmin, _ymin, _width, _height = _rect
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _width, _height,
                               0, 360*64)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    tool.setLocation(_ix, _iy)
    _radius = tool.getRadius()
    if _radius > 0.0:
        _cx, _cy = tool.getCenter()
        _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
        _pr = int(_radius/_upp)
        _xmin = _pcx - _pr
        _ymin = _pcy - _pr
        _width = _height = _pr * 2
        tool.setPixelRect(_xmin, _ymin, _width, _height)
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _width, _height,
                               0, 360*64)
    return True
    
def two_cline_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _first_conobj = tool.getFirstConObject()
            for _obj, _pt in _objdict[_active_layer]:
                if _obj is _first_conobj:
                    continue
                if isinstance(_obj, (HCLine, VCLine, ACLine, CLine)):
                    tool.setHandler("button_press", two_cline_set_circle_cb)
                    tool.setHandler("motion_notify", two_cline_motion_notify_cb)
                    tool.setSecondConObject(_obj)
                    gtkimage.setPrompt(_('Click where you want the tangent circle to be.'))
                    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def two_cline_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (HCLine, VCLine, ACLine, CLine, CCircle)):
                    tool.setHandler("button_press", two_cline_second_button_press_cb)
                    tool.setFirstConObject(_obj)
                    gtkimage.setPrompt(_('Click on the second construction line for tangency.'))
    return True

def two_cline_tancc_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first construction line or construction circle for tangency.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", two_cline_tancc_mode_init)
    _tool.setHandler("button_press", two_cline_first_button_press_cb)

#
# tangent lines around two circles
#

def two_ccircle_tangent_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    tool.setLocation(_x, _y)
    gtkentities.create_entity(gtkimage)

def _draw_two_circle_tangents(gtkimage, tool):
    _tanpts = tool.getTangentPoints()
    assert len(_tanpts), "No tangent points defined!"
    _gc = gtkimage.getGC()
    _da = gtkimage.getDA()
    #
    # adjust the GC to draw the temporary segments in
    # a distinctive manner
    #
    _gc.set_line_attributes(1, gtk.gdk.LINE_DOUBLE_DASH,
                            gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
    _gc.set_dashes(0, [3, 3])
    _tempcolor = Color('#ffff99') # yellowish color
    _color = gtkimage.getColor(_tempcolor)
    _gc.set_foreground(_color)
    _gc.set_function(gtk.gdk.COPY)
    #
    _segs = []
    for _set in _tanpts:
        _x1, _y1, _x2, _y2 = _set
        # print "x1: %g; y1: %g" % (_x1, _y1)
        # print "x2: %g; y2: %g" % (_x2, _y2)
        _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
        _px2, _py2 = gtkimage.coordToPixTransform(_x2, _y2)
        _segs.append((_px1, _py1, _px2, _py2))
    _da.window.draw_segments(_gc, _segs)

def two_circle_tangent_second_button_press_cb(gtkimage, widget, event, tool):
    # print "in second_button_press_cb() ..."
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, CCircle):
                    tool.setHandler("button_press", two_circle_tangent_second_button_press_cb)
                    tool.setSecondCCircle(_obj)
                    if tool.hasTangentPoints():
                        _draw_two_circle_tangents(gtkimage, tool)
                        gtkimage.setPrompt(_('Click on the segment to keep.'))
                        tool.setHandler("button_press", two_ccircle_tangent_cb)
                    else:
                        tool.reset()
                        two_circle_tangent_line_mode_init(gtkimage, tool)
    return True

def two_circle_tangent_first_button_press_cb(gtkimage, widget, event, tool):
    # print "in first_button_press_cb() ..."
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, CCircle):
                    tool.setHandler("button_press", two_circle_tangent_second_button_press_cb)
                    tool.setFirstCCircle(_obj)
                    gtkimage.setPrompt(_('Click on the second construction circle.'))
    return True

def two_circle_tangent_line_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first construction circle.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", two_circle_tangent_line_mode_init)
    _tool.setHandler("button_press", two_circle_tangent_first_button_press_cb)
