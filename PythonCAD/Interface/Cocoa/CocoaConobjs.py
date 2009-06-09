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
# Handles creation of construction lines, circles, etc
#
# P.L.V. nov 23 05
# import adjustment

from math import hypot, pi, atan2
from Foundation import *

import PythonCAD.Interface.Cocoa.CocoaEntities
import PythonCAD.Generic.cline
import PythonCAD.Generic.acline
import PythonCAD.Generic.conobject


#
# Horizontal/Vertical lines - could really be combined
#

def hcline_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", hcline_mode_init)
    tool.setHandler("left_button_press", hcline_left_button_press_cb)
    tool.setHandler("entry_event", hcline_entry_event_cb)
    
def hcline_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setPoint(_viewLoc.x, _viewLoc.y)
    CocoaEntities.create_entity(doc, tool)
    
def hcline_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = CocoaEntities.make_tuple(text)
        tool.setPoint(_x, _y)
        CocoaEntities.create_entity(doc, tool)
    
def vcline_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", vcline_mode_init)
    tool.setHandler("left_button_press", vcline_left_button_press_cb)
    tool.setHandler("entry_event", vcline_entry_event_cb)

def vcline_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setPoint(_viewLoc.x, _viewLoc.y)
    CocoaEntities.create_entity(doc, tool)
    
def vcline_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = CocoaEntities.make_tuple(text)
        tool.setPoint(_x, _y)
        CocoaEntities.create_entity(doc, tool)

#
# Angled Construction line
#

    
def acline_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", acline_mode_init)
    tool.setHandler("left_button_press", acline_first_left_button_press_cb)
    tool.setHandler("entry_event", acline_first_entry_event_cb)

def acline_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setPoint(_viewLoc.x, _viewLoc.y)
    tool.setHandler("mouse_move", acline_mouse_move_cb)
    tool.setHandler("left_button_press", acline_second_left_button_press_cb)
    tool.setHandler("entry_event", acline_second_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the angle")
    
def acline_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    tool.setLocation(_sp.x, _sp.y)
    CocoaEntities.create_entity(doc, tool)

def acline_mouse_move_cb(doc, np, tool):
    tool.setLocation(np.x, np.y)
    _p1 = tool.getPoint()
    _p2 = (np.x, np.y)
    _s = PythonCAD.Generic.conobject.ConstructionObject._ConstructionObject__defstyle
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2, _s)
    _da = doc.getDA()
    _da.setTempObject(_seg)
    

def acline_first_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = CocoaEntities.make_tuple(text)
        tool.setPoint(_x, _y)
        tool.setHandler("mouse_move", acline_mouse_move_cb)
        tool.setHandler("left_button_press", acline_second_left_button_press_cb)
        tool.setHandler("entry_event", acline_second_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the angle")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))

def acline_second_entry_event_cb(doc, text, tool):
    if len(text):
        _angle = CocoaEntities.make_angle(text)
        tool.setAngle(_angle)
        CocoaEntities.create_entity(doc, tool)

#
# two-point construction line
#

def cline_tp_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the first point as 'x, y'")
    tool.setHandler("initialize", cline_tp_mode_init)
    tool.setHandler("left_button_press", cline_tp_first_left_button_press_cb)
    tool.setHandler("entry_event", cline_tp_first_entry_event_cb)

def cline_tp_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(_viewLoc)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    tool.setHandler("mouse_move", cline_tp_mouse_move_cb)
    tool.setHandler("left_button_press", cline_tp_second_left_button_press_cb)
    tool.setHandler("entry_event", cline_tp_second_entry_event_cb)
    doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")

def cline_tp_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    tool.setSecondPoint(_sp.x, _sp.y)
    CocoaEntities.create_entity(doc, tool)
        
def cline_tp_mouse_move_cb(doc, np, tool):
    _p1 = tool.getFirstPoint()
    _p2 = (np.x, np.y)
    _s = PythonCAD.Generic.conobject.ConstructionObject._ConstructionObject__defstyle
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2, _s)
    _da = doc.getDA()
    _da.setTempObject(_seg)

def cline_tp_first_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = CocoaEntities.make_tuple(text)
        tool.setFirstPoint(_x, _y)
        tool.setHandler("mouse_move", cline_tp_mouse_move_cb)
        tool.setHandler("left_button_press", cline_tp_second_left_button_press_cb)
        tool.setHandler("entry_event", cline_tp_second_entry_event_cb)
        doc.setPrompt("Click in the drawing area or enter the second point as 'x, y'")
        doc.getDA().setTempPoint(NSMakePoint(_x, _y))

def cline_tp_second_entry_event_cb(doc, text, tool):
    if len(text):
        _x, _y = CocoaEntities.make_tuple(text)
        tool.setSecondPoint(_x, _y)
        CocoaEntities.create_entity(doc, tool)
    
#
# Parallel Construction Line
#
    
def cline_par_mode_init(doc, tool):
    doc.setPrompt("Click on the reference construction line")
    tool.setHandler("initialize", cline_par_mode_init)
    tool.setHandler("left_button_press", cline_par_first_left_button_press_cb)

def cline_par_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (PythonCAD.Generic.hcline.HCLine,
                                     PythonCAD.Generic.vcline.VCLine,
                                     PythonCAD.Generic.acline.ACLine,
                                     PythonCAD.Generic.cline.CLine)):
                    tool.setLocation(_viewLoc.x, _viewLoc.y)
                    tool.setConstructionLine(_obj)
                    tool.setHandler("left_button_press", cline_par_second_left_button_press_cb)
                    tool.delHandler("entry_event")
                    doc.setPrompt("Click in the drawing area to place the new construction line")

def cline_par_second_left_button_press_cb(doc, event, tool):
    _x1, _y1 = tool.getLocation()
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _sp = _da.convertPoint_fromView_(_loc, None)
    _x2, _y2 = _sp
    _offset = hypot((_x2 - _x1), (_y2 - _y1))
    tool.setOffset(_offset)
    tool.setReferencePoint(_sp.x, _sp.y)
    CocoaEntities.create_entity(doc, tool)


#
# Perpendicular to object construction line
#
def cline_perp_mode_init(doc, tool):
    doc.setPrompt("Click on the object to which you want a perpendicular")
    tool.setHandler("initialize", cline_perp_mode_init)
    tool.setHandler("left_button_press", cline_perp_left_button_press_cb)

def cline_perp_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layer = _image.getActiveLayer()
    _hits = _layer.mapPoint((_viewLoc.x, _viewLoc.y), _tol, 1)
    if len(_hits):
        _obj, _pt = _hits[0]
        _lp = _layer.findObject(_pt)
        if _lp is None:
            _lp = _pt
            _image.addObject(_lp)
        if isinstance(_obj, PythonCAD.Generic.segment.Segment):
            _p1, _p2 = _obj.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _image.addObject(PythonCAD.Generic.hcline.HCLine(_lp))
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _image.addObject(PythonCAD.Generic.vcline.VCLine(_lp))
            else:
                _slope = (180.0/pi) * atan2((_p2y - _p1y),
                                            (_p2x - _p1x)) + 90.0
                _image.addObject(PythonCAD.Generic.acline.ACLine(_lp, _slope))
        elif isinstance(_obj, PythonCAD.Generic.circle.Circle):
            _cp = _obj.getCenter()
            _image.addObject(PythonCAD.Generic.cline.CLine(_cp, _lp))
        elif isinstance(_obj, PythonCAD.Generic.hcline.HCLine):
            _image.addObject(PythonCAD.Generic.vcline.VCLine(_lp))
        elif isinstance(_obj, PythonCAD.Generic.vcline.VCLine):
            _image.addObject(PythonCAD.Generic.hcline.HCLine(_lp))
        elif isinstance(_obj, PythonCAD.Generic.acline.ACLine):
            _angle = _obj.getAngle()
            if abs(_angle) < 1e-10: # horizontal
                _image.addObject(PythonCAD.Generic.vcline.VCLine(_lp))
            elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
                _image.addObject(PythonCAD.Generic.hcline.HCLine(_lp))
            else:
                _slope = _angle + 90.0
                _image.addObject(PythonCAD.Generic.acline.ACLine(_lp, _slope))
        elif isinstance(_obj, PythonCAD.Generic.cline.CLine):
            _p1, _p2 = _obj.getKeypoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _image.addObject(PythonCAD.Generic.hcline.HCLine(_lp))
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _image.addObject(PythonCAD.Generic.vcline.VCLine(_lp))
            else:
                _slope = (180.0/pi) * atan2((_p2y - _p1y),
                                            (_p2x - _p1x)) + 90.0
                _image.addObject(PythonCAD.Generic.acline.ACLine(_lp, _slope))
        else:
            _image.delObject(_lp)
            return
        # we have to call another function to generate
        # an event to flush out the notification system
        # and draw what we just added.  This one works
        # ok, I guess.
        CocoaEntities.create_entity(doc, tool)

#
# tangent to a circle construction line
#  
def cline_tan_mode_init(doc, tool):
    doc.setPrompt("Click on the circle to which you want a tangent")
    tool.setHandler("initialize", cline_tan_mode_init)
    tool.setHandler("left_button_press", cline_tan_left_button_press_cb)

def cline_tan_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _new_pt = _image.findPoint(_viewLoc.x, _viewLoc.y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
        _layer = _image.getActiveLayer()
        _rtd = 180.0/pi
        # I think this is just supposed to be active layer
        _cobj = None
        _angle = None
        _circles = (_layer.getLayerEntities("circle") +
                    _layer.getLayerEntities("ccircle"))
        for _circle in _circles:
            _cx, _cy = _circle.getCenter().getCoords()
            _rad = _circle.getRadius()
            if hypot((_x - _cx), (_y - _cy)) - _rad < 1e-10:
                _cobj = _circle
                _angle = _rtd * atan2((_y - _cy), (_x - _cx))
                if _angle < 0.0:
                    _angle = _angle + 360.0
                break
        if _cobj is None:
            for _arc in _layer.getLayerEntities("arc"):
                _cx, _cy = _arc.getCenter().getCoords()
                _rad = _arc.getRadius()
                if hypot((_cx - _x), (_cy - _y)) - _rad < 1e-10:
                    _angle = _rtd * atan2((_y - _cy), (_x - _cx))
                    if _angle < 0.0:
                        _angle = _angle + 360.0
                    if _arc.throughAngle(_angle):
                        _cobj = _arc
                        break
        if _cobj is not None:
            if _new_pt:
                _image.addObject(_pt)
            if (abs(_angle) < 1e-6 or
                abs(_angle - 180.0) < 1e-6 or
                abs(_angle - 360.0) < 1e-6):
                _tcl = PythonCAD.Generic.vcline.VCLine(_pt)
            elif (abs(_angle - 90.0) < 1e-6 or
                  abs(_angle - 270.0) < 1e-6):
                _tcl = PythonCAD.Generic.hcline.HCLine(_pt)
            else:
                _slope = _angle + 90.0
                _tcl = PythonCAD.Generic.acline.ACLine(_pt, _slope)
            _image.addObject(_tcl)
            # we have to call another function to generate
            # an event to flush out the notification system
            # and draw what we just added.  This one works
            # ok, I guess.
            CocoaEntities.create_entity(doc, tool)
            return   

#
# tangent to two circle construction line
#
   
def cline_tan_2circ_mode_init(doc, tool):
    doc.setPrompt("Click on the first construction circle")
    tool.setHandler("initialize", cline_tan_2circ_mode_init)
    tool.setHandler("left_button_press", cline_tan_2circ_first_left_button_press_cb)
    
def cline_tan_2circ_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _layer = _image.getActiveLayer()
        if _layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_layer]:
                if isinstance(_obj, PythonCAD.Generic.ccircle.CCircle):
                    tool.setFirstCCircle(_obj)
                    tool.setHandler("left_button_press", cline_tan_2circ_second_left_button_press_cb)
                    doc.setPrompt("Click on the second construction circle")
                    
def cline_tan_2circ_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _layer = _image.getActiveLayer()
        if _layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_layer]:
                if isinstance(_obj, PythonCAD.Generic.ccircle.CCircle):
                    _fc = tool.getFirstCCircle()
                    if _obj is _fc:
                        return
                    tool.setSecondCCircle(_obj)
                    if tool.hasTangentPoints():
                        _draw_two_circle_tangents(doc, tool)
                        tool.setHandler("mouse_move", cline_tan_2circ_mouse_move_cb)
                        tool.setHandler("left_button_press", cline_tan_2circ_third_left_button_press_cb) 
                        doc.setPrompt("Click on the segment to keep")
                    else:
                        tool.reset()
                        cline_tan_2circ_mode_init(doc, tool)

def _draw_two_circle_tangents(doc, tool):
    _tanpts = tool.getTangentPoints()
    assert len(_tanpts), "No tangent points defined!"
    _da = doc.getDA()
    _da.setTempObject() #clear it out
    #
    # Make an interesting line style - should be defined globally?
    #
    _styles = PythonCAD.Generic.globals.prefs['STYLES']
    _s = None
    for _style in _styles:
        if _style.getName() == "Dashed Yellow Line":
            _s = _style
            break
    if _s is None:
        raise TypeError, "Style not found for dashed lines."
    for _set in _tanpts:
        _x1, _y1, _x2, _y2 = _set
        _p1 = (_x1, _y1)
        _p2 = (_x2, _y2)
        _seg = PythonCAD.Generic.segment.Segment(_p1, _p2, _s)
        _da.setTempObject(_seg, False)

# dummy function just for update - needs to only be called once
def cline_tan_2circ_mouse_move_cb(doc, np, tool):
    tool.delHandler("mouse_move")
    
def cline_tan_2circ_third_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setLocation(_viewLoc.x, _viewLoc.y)
    CocoaEntities.create_entity(doc, tool)
    # there's got to be a better way to do this,
    # but I give up.  Just redraw everything.
    _da.setNeedsDisplay_(True)
    
#
# Construction circle - center point
#

def ccircle_center_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", ccircle_center_mode_init)
    tool.setHandler("left_button_press", ccircle_center_first_left_button_press_cb)
    tool.setHandler("entry_event", ccircle_point_entry_event_cb)
    
def ccircle_center_first_left_button_press_cb(doc, event, tool):
    CocoaEntities.circle_center_first_left_button_press_cb(doc, event, tool)
    tool.setHandler("mouse_move", ccircle_center_mouse_move_cb)

def ccircle_center_mouse_move_cb(doc, np, tool):
    _p1 = tool.getCenter()
    _r = hypot((_p1[0] - np.x), (_p1[1] - np.y))
    if _r > 0.0:
        _circle = PythonCAD.Generic.ccircle.CCircle(_p1, _r)
        _da = doc.getDA()
        _da.setTempObject(_circle)

def ccircle_point_entry_event_cb(doc, text, tool):
    if len(text):
        CocoaEntities.circle_point_entry_event_cb(doc, text, tool)
        tool.setHandler("mouse_move", ccircle_center_mouse_move_cb)        
    
#
# Construction circle - 2 point
#

def ccircle_tp_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter a point as 'x, y'")
    tool.setHandler("initialize", ccircle_tp_mode_init)
    tool.setHandler("left_button_press", ccircle_tp_first_left_button_press_cb)
    tool.setHandler("entry_event", ccircle_tp_first_entry_event_cb)

def ccircle_tp_first_left_button_press_cb(doc, event, tool):
    CocoaEntities.circle_tp_first_left_button_press_cb(doc, event, tool)
    tool.setHandler("mouse_move", ccircle_tp_mouse_move_cb)

def ccircle_tp_mouse_move_cb(doc, np, tool):
    _x, _y = tool.getFirstPoint()
    _fp = NSMakePoint(_x, _y)
    if NSEqualPoints(_fp, np):
        return
    tool.setSecondPoint(np.x, np.y)
    _cp = tool.getCenter()
    _r = tool.getRadius()
    if _r is not None and _r > 0:
        _circle = PythonCAD.Generic.ccircle.CCircle(_cp, _r)
        _da = doc.getDA()
        _da.setTempObject(_circle)

def ccircle_tp_first_entry_event_cb(doc, text, tool):
    if len(text):
        CocoaEntities.circle_tp_first_entry_event_cb(doc, text, tool)
        tool.setHandler("mouse_move", ccircle_tp_mouse_move_cb)
    
#
# Construction circle - tangent
#

def ccircle_tan1_mode_init(doc, tool):
    doc.setPrompt("Click on the construction object used for tangency")
    tool.setHandler("initialize", ccircle_tan1_mode_init)
    tool.setHandler("left_button_press", ccircle_tan1_first_left_button_press_cb)

def ccircle_tan1_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (PythonCAD.Generic.hcline.HCLine,
                                     PythonCAD.Generic.vcline.VCLine,
                                     PythonCAD.Generic.acline.ACLine,
                                     PythonCAD.Generic.cline.CLine,
                                     PythonCAD.Generic.ccircle.CCircle)):
                    tool.setConstructionLine(_obj)
                    tool.setHandler("left_button_press", ccircle_final_left_button_press_cb)
                    tool.setHandler("mouse_move", ccircle_tan1_mouse_move_cb)
                    doc.setPrompt("Click in the drawing area to place the new construction line")

def ccircle_final_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_viewLoc.x, _viewLoc.y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
        _viewLoc = NSMakePoint(_x, _y)
    tool.setLocation(_viewLoc.x, _viewLoc.y)
    CocoaEntities.create_entity(doc, tool)
    
def ccircle_tan1_mouse_move_cb(doc, np, tool):
    tool.setLocation(np.x, np.y)
    _cp = tool.getCenter()
    _r = tool.getRadius()
    if _r is not None and _r > 0:
        _circle = PythonCAD.Generic.ccircle.CCircle(_cp, _r)
        _da = doc.getDA()
        _da.setTempObject(_circle)
    
#
# Construction circle - 2 circle tangent
#

def ccircle_tan2_mode_init(doc, tool):
    doc.setPrompt("Click on the first construction line for tangency")
    tool.setHandler("initialize", ccircle_tan2_mode_init)
    tool.setHandler("left_button_press", ccircle_tan2_first_left_button_press_cb)
    
def ccircle_tan2_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (PythonCAD.Generic.hcline.HCLine,
                                     PythonCAD.Generic.vcline.VCLine,
                                     PythonCAD.Generic.acline.ACLine,
                                     PythonCAD.Generic.cline.CLine,
                                     PythonCAD.Generic.ccircle.CCircle)):
                    tool.setFirstConObject(_obj)
                    tool.setHandler("left_button_press", ccircle_tan2_second_left_button_press_cb)
                    doc.setPrompt("Click on the second construction line for tangency")
    
def ccircle_tan2_second_left_button_press_cb(doc, event, tool):  
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_viewLoc.x, _viewLoc.y, _tol, 1)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (PythonCAD.Generic.hcline.HCLine,
                                     PythonCAD.Generic.vcline.VCLine,
                                     PythonCAD.Generic.acline.ACLine,
                                     PythonCAD.Generic.cline.CLine)):
                    tool.setSecondConObject(_obj)
                    tool.setHandler("left_button_press", ccircle_final_left_button_press_cb)
                    tool.setHandler("mouse_move", ccircle_tan2_mouse_move_cb)
                    doc.setPrompt("Click where you want the tangent circle to be")

def ccircle_tan2_mouse_move_cb(doc, np, tool):  
    tool.setLocation(np.x, np.y)
    _cp = tool.getCenter()
    _r = tool.getRadius()
    if _r is not None and _r > 0:
        _circle = PythonCAD.Generic.ccircle.CCircle(_cp, _r)
        _da = doc.getDA()
        _da.setTempObject(_circle)

    
