#
# Copyright (c) 2002-2004 Art Haas
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
# Handles creation of drawing entities (circles, lines, chamfers, etc)
#
# P.L.V. nov 23 05
# import adjustment

import string
from math import hypot, pi, atan2

import objc

from PythonCAD.Interface.Cocoa import Globals
import PythonCAD.Interface.Cocoa.ImageDocument
import PythonCAD.Generic.tools
import PythonCAD.Generic.util

from Foundation import *
from AppKit import NSShiftKeyMask

#
# Helper functions
#
def make_tuple(text):
    
    try:
        _tpl = eval(text)
    except:
        raise StandardError, "Invalid point: " + text
    if not isinstance(_tpl, tuple):
        raise TypeError, "Invalid point: " + str(_tpl)
    if len(_tpl) != 2:
        raise ValueError, "Invalid point: " + str(_tpl)
    return _tpl

def make_radius(text):
    try:
        _textrad = eval(text)
    except:
        raise ValueError, "Invalid radius: " + text
    _rad = _textrad
    if not isinstance(_rad, float):
        _rad = float(_textrad)
    if _rad < 1e-10:
        raise ValueError, "Invalid radius: %g" % _rad
    return _rad

def make_angle(text):
    try:
        _textangle = eval(text)
    except:
        raise StandardError, "Invalid angle: " + text
    return PythonCAD.Generic.util.make_c_angle(_textangle)

def create_entity(doc, tool):
    _init_func = tool.getHandler("initialize")
    _image = doc.getImage()
    _image.startAction()
    try:
        tool.create(_image)
    finally:
        _image.endAction()
    _init_func(doc, tool)

Globals.s = None
Globals.l = None
Globals.c = None
Globals.t = None
#
# Points
#
     
def point_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the point as 'x, y'")
    tool.setHandler("initialize", point_mode_init)
    tool.setHandler("left_button_press", point_left_button_press_cb)
    tool.setHandler("entry_event", point_entry_event_cb)

def point_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setPoint(_viewLoc.x, _viewLoc.y)
    create_entity(doc, tool)

def point_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setPoint(_x, _y)
        create_entity(doc, tool)

#
# Segments
#
def segment_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", segment_mode_init)
    tool.setHandler("left_button_press", segment_first_left_button_press_cb)
    tool.setHandler("entry_event", segment_first_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')

def segment_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    _da.setTempPoint(_viewLoc)
    tool.setHandler("left_button_press", segment_second_left_button_press_cb)
    tool.setHandler("mouse_move", segment_mouse_move_cb)
    doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")

def segment_mouse_move_cb(doc, np, tool):
    _p1 = tool.getFirstPoint()
    _p2 = (np.x, np.y)
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2, Globals.s, Globals.l, Globals.c, Globals.t)
    _da = doc.getDA()
    _da.setTempObject(_seg)
   
def segment_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    tool.setSecondPoint(_sp.x, _sp.y)
    create_entity(doc, tool)

def segment_first_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setFirstPoint(_x, _y)
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))
        tool.setHandler("left_button_press", segment_second_left_button_press_cb)
        tool.setHandler("mouse_move", segment_mouse_move_cb)
        tool.setHandler("entry_event", segment_second_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")

def segment_second_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setSecondPoint(_x, _y)
        create_entity(doc, tool)
        
#
# rectangles
#
def rectangle_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", rectangle_mode_init)
    tool.setHandler("left_button_press", rectangle_first_left_button_press_cb)
    tool.setHandler("entry_event", rectangle_first_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')

def rectangle_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    _da.setTempPoint(_viewLoc)
    tool.setHandler("left_button_press", rectangle_second_left_button_press_cb)
    tool.setHandler("mouse_move", rectangle_mouse_move_cb)
    tool.setHandler("entry_event", rectangle_second_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")

def rectangle_mouse_move_cb(doc, np, tool):
    _p1 = tool.getFirstPoint()
    _p2 = (_p1[0],np.y)
    _p3 = (np.x, np.y)
    _p4 = (np.x,_p1[1])
    _da = doc.getDA()
    _s1 = PythonCAD.Generic.segment.Segment(_p1, _p2, Globals.s, Globals.l, Globals.c, Globals.t)
    _s2 = PythonCAD.Generic.segment.Segment(_p2, _p3, Globals.s, Globals.l, Globals.c, Globals.t)
    _s3 = PythonCAD.Generic.segment.Segment(_p3, _p4, Globals.s, Globals.l, Globals.c, Globals.t)
    _s4 = PythonCAD.Generic.segment.Segment(_p4, _p1, Globals.s, Globals.l, Globals.c, Globals.t)
    _da = doc.getDA()
    _da.setTempObject(_s1)
    _da.setTempObject(_s2, False)
    _da.setTempObject(_s3, False)
    _da.setTempObject(_s4, False)
    
def rectangle_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    tool.setSecondPoint(_sp.x, _sp.y)
    create_entity(doc, tool)

def rectangle_first_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setFirstPoint(_x, _y)
        tool.setHandler("left_button_press", rectangle_second_left_button_press_cb)
        tool.setHandler("mouse_move", rectangle_mouse_move_cb)
        tool.setHandler("entry_event", rectangle_second_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))

def rectangle_second_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setSecondPoint(_x, _y)
        create_entity(doc, tool)

#
# Circles
#


# center point
def circle_center_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", circle_center_mode_init)
    tool.setHandler("left_button_press", circle_center_first_left_button_press_cb)
    tool.setHandler("entry_event", circle_point_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')
    
def circle_center_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setCenter(_viewLoc.x, _viewLoc.y)
    tool.setHandler("left_button_press", circle_center_second_left_button_press_cb)
    tool.setHandler("mouse_move", circle_center_mouse_move_cb)
    tool.setHandler("entry_event", circle_radius_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the radius")
    _da.setTempPoint(_viewLoc)
    
def circle_center_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    _cx, _cy = tool.getCenter()
    _radius = hypot((_cx - _sp.x), (_cy - _sp.y))
    tool.setRadius(_radius)
    create_entity(doc, tool)
    
def circle_center_mouse_move_cb(doc, np, tool):
    _p1 = tool.getCenter()
    _r = hypot((_p1[0] - np.x), (_p1[1] - np.y))
    if _r > 0.0:
        _circle = PythonCAD.Generic.circle.Circle(_p1, _r, Globals.s, Globals.l, Globals.c, Globals.t)
        _da = doc.getDA()
        _da.setTempObject(_circle)
    
def circle_point_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setCenter(_x, _y)
        tool.setHandler("left_button_press", circle_center_second_left_button_press_cb)
        tool.setHandler("mouse_move", circle_center_mouse_move_cb)
        tool.setHandler("entry_event", circle_radius_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the radius")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))
    
def circle_radius_entry_event_cb(doc, text, tool):
    if len(text):
        _r = make_radius(text)
        tool.setRadius(_r)
        create_entity(doc, tool)
 
# 2 point
def circle_tp_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", circle_tp_mode_init)
    tool.setHandler("left_button_press", circle_tp_first_left_button_press_cb)
    tool.setHandler("entry_event", circle_tp_first_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')

def circle_tp_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    tool.setHandler("left_button_press", circle_tp_second_left_button_press_cb)
    tool.setHandler("mouse_move", circle_tp_mouse_move_cb)
    tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")
    
def circle_tp_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    tool.setSecondPoint(_sp.x, _sp.y)
    create_entity(doc, tool)

def circle_tp_mouse_move_cb(doc, np, tool):
    _x, _y = tool.getFirstPoint()
    _fp = NSMakePoint(_x, _y)
    if NSEqualPoints(_fp, np):
        return
    tool.setSecondPoint(np.x, np.y)
    _cp = tool.getCenter()
    _r = tool.getRadius()
    if _r is not None and _r > 0:
        _circle = PythonCAD.Generic.circle.Circle(_cp, _r, Globals.s, Globals.l, Globals.c, Globals.t)
        _da = doc.getDA()
        _da.setTempObject(_circle)
    
def circle_tp_first_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setFirstPoint(_x, _y)
        tool.setHandler("left_button_press", circle_tp_second_left_button_press_cb)
        tool.setHandler("mouse_move", circle_tp_mouse_move_cb)
        tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))
        

def circle_tp_second_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setSecondPoint(_x, _y)
        create_entity(doc, tool)

#
# Arcs
#

def arc_center_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", arc_center_mode_init)
    tool.setHandler("left_button_press", arc_center_first_left_button_press_cb)
    tool.setHandler("entry_event", arc_center_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')
    
def arc_center_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setCenter(_viewLoc.x, _viewLoc.y)
    tool.setHandler("left_button_press", arc_center_second_left_button_press_cb)
    tool.setHandler("mouse_move", arc_radius_mouse_move_cb)
    tool.setHandler("entry_event", arc_radius_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the radius")
    
def arc_center_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    _cx, _cy = tool.getCenter()
    _radius = hypot((_sp.x - _cx), (_sp.y - _cy))
    if _radius > 0.0:
        tool.setRadius(_radius)
        _angle = (180.0/pi) * atan2((_sp.y - _cy), (_sp.x - _cx))
        if _angle < 0.0:
            _angle = _angle + 360.0
        tool.setStartAngle(_angle)
        tool.delHandler("entry_event")
        tool.setHandler("left_button_press", arc_center_third_left_button_press_cb)
        tool.setHandler("mouse_move", arc_angle_mouse_move_cb)
        doc.setPrompt("Click in the drawing area to finish the arc")
    
def arc_center_third_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _tp = _da.convertPoint_fromView_(_loc, None)
    _cx, _cy = tool.getCenter()
    _angle = (180.0/pi) * atan2((_tp.y - _cy), (_tp.x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setEndAngle(_angle)
    create_entity(doc, tool)
    
def arc_start_angle_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x, _y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    _cx, _cy = tool.getCenter()
    _angle = (180.0/pi) * atan2((_y - _cy), (_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setStartAngle(_angle)
    tool.setHandler("mouse_move", arc_angle_mouse_move_cb)
    tool.setHandler("left_button_press", arc_center_third_left_button_press_cb)
    tool.setHandler("entry_event", arc_end_angle_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the end angle of the arc")
    

def arc_radius_mouse_move_cb(doc, np, tool):
    _p1 = tool.getCenter()
    _p2 = (np.x, np.y)
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2, Globals.s, Globals.l, Globals.c, Globals.t)
    _da = doc.getDA()
    _da.setTempObject(_seg)

def arc_angle_mouse_move_cb(doc, np, tool):
    _cp = tool.getCenter()
    _cx, _cy = _cp
    _r = tool.getRadius()
    _sa = tool.getStartAngle()
    _ea = (180.0/pi) * atan2((np.y - _cy), (np.x - _cx))
    if _ea < 0.0:
        _ea = _ea + 360.0
    _arc = PythonCAD.Generic.arc.Arc(_cp, _r, _sa, _ea, Globals.s, Globals.l, Globals.c, Globals.t)
    _da = doc.getDA()
    _da.setTempObject(_arc)
    
def arc_center_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setCenter(_x, _y)
        tool.setHandler("left_button_press", arc_center_second_left_button_press_cb)
        tool.setHandler("mouse_move", arc_radius_mouse_move_cb)
        tool.setHandler("entry_event", arc_radius_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the radius")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))

def arc_radius_entry_event_cb(doc, text, tool):
    if len(text):
        _r = make_radius(text)
        tool.setRadius(_r)
        tool.delHandler("mouse_move")
        tool.setHandler("left_button_press", arc_start_angle_left_button_press_cb)
        tool.setHandler("entry_event", arc_start_angle_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the start angle of the arc")
        
def arc_start_angle_entry_event_cb(doc, text, tool):
    if len(text):
        _angle = make_angle(text)
        tool.setStartAngle(_angle)
        tool.setHandler("mouse_move", arc_angle_mouse_move_cb)
        tool.setHandler("left_button_press", arc_center_third_left_button_press_cb)
        tool.setHandler("entry_event", arc_end_angle_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the end angle of the arc")
        
def arc_end_angle_entry_event_cb(doc, text, tool):
    if len(text):
        _angle = make_angle(text)
        tool.setEndAngle(_angle)
        create_entity(doc, tool)

        

#
# Chamfers
#
def chamfer_mode_init(doc, tool):
    doc.setPrompt("Click on the points where you want a chamfer")
    tool.setHandler("initialize", chamfer_mode_init)
    tool.setHandler("left_button_press", chamfer_left_button_press_cb)

def chamfer_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _new_pt = _image.findPoint(_viewLoc.x, _viewLoc.y, _tol)
    if _pt is not None and not _new_pt:
        _active_layer = _image.getActiveLayer()
        _urefs = _pt.getUsers()
        if len(_urefs) != 2:
            return
        _s1 = _s2 = None        
        for _uref in _urefs:
            _user = _uref()
            if _user is None:
                return
            if not isinstance(_user, PythonCAD.Generic.segment.Segment):
                return
            if _s1 is None:
                _s1 = _user
            else:
                _s2 = _user
        _len = _image.getOption('CHAMFER_LENGTH')
        Globals.s = _image.getOption('LINE_STYLE')
        Globals.l = _image.getOption('LINE_TYPE')
        Globals.c = _image.getOption('LINE_COLOR')
        Globals.t = _image.getOption('LINE_THICKNESS')
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
        _pc = _active_layer.find('point', _xn, _yn)
        while _pc is not None:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = (_slen - (_len/_factor))/_slen
            _xn = _x1 + _r * (_x2 - _x1)
            _yn = _y1 + _r * (_y2 - _y1)
            _pc = _active_layer.find('point', _xn, _yn)
        if _pc is None:
            _pc = PythonCAD.Generic.point.Point(_xn, _yn)
            _image.addObject(_pc)
            if _pt is _p1:
                _s1.setP1(_pc)
            else:
                _s1.setP2(_pc)
            _ptx, _pty = _pt.getCoords() 
            _pc.setx(_ptx)
            _pc.sety(_pty)
            _chamfer = PythonCAD.Generic.segjoint.Chamfer(_s1, _s2, _len, Globals.s, Globals.l, Globals.c, Globals.t)
            _image.addObject(_chamfer)
            # force a redraw of the segments, too.
#            _msgr = doc.getMessenger()
#            _msgr.added_object_event(_image,_active_layer,_s1)
#            _msgr.added_object_event(_image,_active_layer,_s2)
            # we have to call another function to generate
            # an event to flush out the notification system
            # and draw what we just added.  This one works
            # ok, I guess.
            create_entity(doc, tool)
            return   
    
# 
# Fillets
#
def fillet_mode_init(doc, tool):
    doc.setPrompt("Click on the points where you want a fillet")
    tool.setHandler("initialize", fillet_mode_init)
    tool.setHandler("left_button_press", fillet_left_button_press_cb)
    
def fillet_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _new_pt = _image.findPoint(_viewLoc.x, _viewLoc.y, _tol)
    if _pt is not None and not _new_pt:
        _active_layer = _image.getActiveLayer()
        _urefs = _pt.getUsers()
        if len(_urefs) != 2:
            return
        _s1 = _s2 = None        
        for _uref in _urefs:
            _user = _uref()
            if _user is None:
                return
            if not isinstance(_user, PythonCAD.Generic.segment.Segment):
                return
            if _s1 is None:
                _s1 = _user
            else:
                _s2 = _user
        _rad = _image.getOption('FILLET_RADIUS')
        Globals.s = _image.getOption('LINE_STYLE')
        Globals.l = _image.getOption('LINE_TYPE')
        Globals.c = _image.getOption('LINE_COLOR')
        Globals.t = _image.getOption('LINE_THICKNESS')
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
        _pc = _active_layer.find('point', _xn, _yn)
        while _pc is not None:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = 1.0 - (_slen/_factor)
            _xn = _x1 + _r * (_x2 - _x1)
            _yn = _y1 + _r * (_y2 - _y1)
            _pc = _active_layer.find('point', _xn, _yn)
        if _pc is None:
            _pc = PythonCAD.Generic.point.Point(_xn, _yn)
            _image.addObject(_pc)
            if _pt is _p1:
                _s1.setP1(_pc)
            else:
                _s1.setP2(_pc)
            _ptx, _pty = _pt.getCoords()
            _pc.setx(_ptx)
            _pc.sety(_pty)
            _fillet = PythonCAD.Generic.segjoint.Fillet(_s1, _s2, _rad, Globals.s, Globals.l, Globals.c, Globals.t)
            _image.addObject(_fillet)
            # we have to call another function to generate
            # an event to flush out the notification system
            # and draw what we just added.  This one works
            # ok, I guess.
            create_entity(doc, tool)
            return   
    
   
# 
# Leaders
#
def leader_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area to enter the first point")
    tool.setHandler("initialize", leader_mode_init)
    tool.setHandler("left_button_press", leader_first_left_button_press_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')
    
def leader_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    tool.setHandler("mouse_move", leader_mouse_move_cb)
    tool.setHandler("left_button_press", leader_second_left_button_press_cb)
    doc.setPrompt("Click in the drawing area to place the second point")
    
def leader_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setMidPoint(_viewLoc.x, _viewLoc.y)
    tool.setHandler("mouse_move", leader_mouse_move_cb)
    tool.setHandler("left_button_press", leader_third_left_button_press_cb)
    doc.setPrompt("Click in the drawing area to place the final point")
    
def leader_third_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setFinalPoint(_viewLoc.x, _viewLoc.y)
    create_entity(doc, tool)

def leader_mouse_move_cb(doc, np, tool):
    _x1, _y1 = tool.getFirstPoint()
    _da = doc.getDA()
    _p2 = tool.getMidPoint()
    _flag = True
    if _p2 is not None:
        _s1 = PythonCAD.Generic.segment.Segment((_x1, _y1), _p2, Globals.s, Globals.l, Globals.c, Globals.t)
        _da.setTempObject(_s1, _flag)
        _flag = False
        (_x1, _y1) = _p2
    (_x2, _y2) = np
    _s1 = PythonCAD.Generic.segment.Segment((_x1, _y1), (_x2, _y2), Globals.s, Globals.l, Globals.c, Globals.t)
    _da.setTempObject(_s1, _flag)
    

#
# Polyline
#
def polyline_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", polyline_mode_init)
    tool.setHandler("left_button_press", polyline_left_button_press_cb)
    tool.setHandler("entry_event", polyline_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')
    
def polyline_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.storePoint(_viewLoc.x, _viewLoc.y)
    if ((event.modifierFlags() & NSShiftKeyMask) != 0):
        create_entity(doc, tool)
    else:
        tool.setHandler("mouse_move", polyline_mouse_move_cb)
        doc.setPrompt("Click or enter as 'x, y' the next point. Shift-click or type 'last' to finish")

def polyline_mouse_move_cb(doc, np, tool):
    _pts = tool.getPoints()
    (_x1, _y1) = _pts[0]
    _count = len(_pts)
    _da = doc.getDA()
    _flag = True
    for _i in range(1, _count):
        (_x2, _y2) = _pts[_i]
        _s1 = PythonCAD.Generic.segment.Segment((_x1, _y1), (_x2, _y2), Globals.s, Globals.l, Globals.c, Globals.t)
        _da.setTempObject(_s1, _flag)
        _flag = False
        _x1 = _x2
        _y1 = _y2
    (_x2, _y2) = np
    _s1 = PythonCAD.Generic.segment.Segment((_x1, _y1), (_x2, _y2), Globals.s, Globals.l, Globals.c, Globals.t)
    _da.setTempObject(_s1, _flag)
        
def polyline_entry_event_cb(doc, text, tool):
    if len(text):
        if text == 'done':
            create_entity(doc, tool)
        else:
            _x, _y = make_tuple(text)
            tool.storePoint(_x, _y)
            tool.setHandler("mouse_move", polyline_mouse_move_cb)
            doc.setPrompt("Click or enter as 'x, y' the next point. Shift-click or type 'done' to finish")
            doc.getDA().setTempPoint(NSMakePoint(_x, _y))
        


#
# Polygon & External Polygon
#
def polygon_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", polygon_mode_init)
    tool.setHandler("left_button_press", polygon_first_left_button_press_cb)
    tool.setHandler("entry_event", polygon_point_entry_event_cb)
    _image = doc.getImage()
    Globals.s = _image.getOption('LINE_STYLE')
    Globals.l = _image.getOption('LINE_TYPE')
    Globals.c = _image.getOption('LINE_COLOR')
    Globals.t = _image.getOption('LINE_THICKNESS')

def polygon_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setCenter(_viewLoc.x, _viewLoc.y)
    tool.setHandler("left_button_press", polygon_second_left_button_press_cb)
    tool.setHandler("mouse_move", polygon_mouse_move_cb)
    tool.setHandler("entry_event", polygon_radius_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the apparent radius")
    _da.setTempPoint(_viewLoc)
    
def polygon_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    (_cx, _cy) = tool.getCenter()
    if (_cx != _x) or (_cy != _y):
        tool.setLocation(_x, _y)
        create_entity(doc, tool)
   
def polygon_mouse_move_cb(doc, np, tool):
    _segs = []
    (_x, _y) = np
    tool.setLocation(_x, _y)
    _count = tool.getSideCount()
    _flag = True
    _da = doc.getDA()
    (_x0, _y0) = (_x1, _y1) = tool.getCoord(0)
    for _i in range(1, _count):
        (_x2, _y2) = tool.getCoord(_i)
        _s1 = PythonCAD.Generic.segment.Segment((_x1, _y1), (_x2, _y2), Globals.s, Globals.l, Globals.c, Globals.t)
        _da.setTempObject(_s1, _flag)
        _x1 = _x2
        _y1 = _y2
        _flag = False
    _s1 = PythonCAD.Generic.segment.Segment((_x0, _y0), (_x1, _y1), Globals.s, Globals.l, Globals.c, Globals.t)
    _da.setTempObject(_s1, False)

def polygon_point_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = make_tuple(text)
        tool.setCenter(_x, _y)
        tool.setHandler("left_button_press", polygon_second_left_button_press_cb)
        tool.setHandler("mouse_move", polygon_mouse_move_cb)
        tool.delHandler("entry_event")
        doc.setPrompt("Click in the drawing area to complete the polygon")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))
    
def polygon_radius_entry_event_cb(doc, text, tool):
    if len(text):
        _r = make_radius(text)
        (_cx, _cy) = tool.getCenter()
        tool.setLocation(_cx+_r, _cy)
        create_entity(doc, tool)

