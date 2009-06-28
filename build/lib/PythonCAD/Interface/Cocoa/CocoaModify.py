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
# Handles modification of drawing entities and views
#
import string

import objc

import PythonCAD.Generic.segment
import PythonCAD.Generic.split
import PythonCAD.Generic.transfer
import PythonCAD.Generic.mirror
import PythonCAD.Generic.move

from Foundation import NSMakePoint

#
# Generic code - select, make distances, etc
#
def select_mouse_move_cb(doc, np, tool):
    _p1 = tool.getLocation()
    _p2 = (_p1[0],np.y)
    _p3 = (np.x, np.y)
    _p4 = (np.x,_p1[1])
    _da = doc.getDA()
    _s1 = PythonCAD.Generic.segment.Segment(_p1, _p2)
    _s2 = PythonCAD.Generic.segment.Segment(_p2, _p3)
    _s3 = PythonCAD.Generic.segment.Segment(_p3, _p4)
    _s4 = PythonCAD.Generic.segment.Segment(_p4, _p1)
    _da = doc.getDA()
    _da.setTempObject(_s1)
    _da.setTempObject(_s2, False)
    _da.setTempObject(_s3, False)
    _da.setTempObject(_s4, False)


#
# Split
#
def split_init(doc, tool):
    doc.setPrompt("Click on the objects you want to split")
    tool.setHandler("initialize", split_init)
    tool.setHandler("left_button_press", split_first_left_button_press_cb)

def split_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(NSMakePoint(_x, _y))
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _objlist = _active_layer.mapPoint((_x, _y), _tol, None)
    if len(_objlist):
        for _obj, _pt in _objlist:
        
            if isinstance(_obj, PythonCAD.Generic.segment.Segment):
                _p1, _p2 = _obj.getEndpoints()
                _lpt = _active_layer.find('point', _pt.x, _pt.y)
                if _lpt is None:
                    _active_layer.addObject(_pt)
                    _lpt = _pt
                _s1, _s2 = PythonCAD.Generic.split.split_segment(_obj, _pt)
                _image.startAction()
                try:
                    _active_layer.addObject(_s1)
                    _active_layer.addObject(_s2)
                    _active_layer.delObject(_obj)
                finally:
                    _image.endAction()

            elif isinstance(_obj, PythonCAD.Generic.arc.Arc):
                _arc1, _arc2 = PythonCAD.Generic.split.split_arc(_obj, _pt)
                _image.startAction()
                try:
                    _active_layer.addObject(_arc1)
                    _active_layer.addObject(_arc2)
                    _active_layer.delObject(_obj)
                finally:
                    _image.endAction()
                    
            elif isinstance(_obj, PythonCAD.Generic.circle.Circle):
                _arc = PythonCAD.Generic.split.split_circle(_obj, _pt)
                _image.startAction()
                try:
                    _active_layer.addObject(_arc)
                    _active_layer.delObject(_obj)
                finally:
                    _image.endAction()
                    
            elif isinstance(_obj, PythonCAD.Generic.polyline.Polyline):
                _lpt = _active_layer.find('point', _pt.x, _pt.y)
                _image.startAction()
                try:
                    if _lpt is None:
                        _active_layer.addObject(_pt)
                        _lpt = _pt
                    PythonCAD.Generic.split.split_polyline(_obj, _lpt)
                finally:
                    _image.endAction()
            else:
                pass
    else:
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setLocation(_x, _y)
        tool.setHandler("mouse_move", select_mouse_move_cb)
        tool.setHandler("left_button_press", split_second_left_button_press_cb)

def split_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _y1 = tool.popObject()
    _x1 = tool.popObject()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax, True)
    if len(_objs):
        _splitable = []
        for _obj in _objs:
            if isinstance(_obj, (PythonCAD.Generic.segment.Segment,
                                 PythonCAD.Generic.circle.Circle,
                                 PythonCAD.Generic.arc.Arc,
                                 PythonCAD.Generic.polyline.Polyline)):
                _splitable.append(_obj)
        if len(_splitable):
            PythonCAD.Generic.split.split_objects(_active_layer, _splitable)
    tool.reset()
    split_init(doc, tool)
                    




#
# Mirror
#
def mirror_init(doc, tool):
    doc.setPrompt("Click on the mirroring construction line")
    tool.setHandler("initialize", mirror_init)
    tool.setHandler("left_button_press", mirror_first_left_button_press_cb)

def mirror_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (PythonCAD.Generic.hcline.HCLine,
                                     PythonCAD.Generic.vcline.VCLine,
                                     PythonCAD.Generic.acline.ACLine,
                                     PythonCAD.Generic.cline.CLine)):
                    tool.setHandler("left_button_press", mirror_second_left_button_press_cb)
                    tool.setMirrorLine(_obj)
                    doc.setPrompt("Click on or select the objects to mirror")
                    break

def mirror_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(NSMakePoint(_x, _y))
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                _objs.append(_obj)
            _mline = tool.getMirrorLine()
            mirror_objects(doc, tool, _objs)
    else:
        _p, _flag = _image.findPoint(_x, _y, _tol)
        if _p is not None:
            _x, _y = _p.getCoords()
        tool.setLocation(_x, _y)
        tool.setHandler("mouse_move", select_mouse_move_cb)
        tool.setHandler("left_button_press", mirror_third_left_button_press_cb)

def mirror_third_left_button_press_cb(doc, event, tool):
    tool.delHandler("mouse_move")
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _p = _active_layer.find('point', _x2, _y2)
    if _p is not None:
        _x2, _y2 = _p.getCoords()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax, True)
    mirror_objects(doc, tool, _objs)
        
def mirror_objects(doc, tool, objs):
    _mline = tool.getMirrorLine()
    _image = doc.getImage()
    _mobjs = PythonCAD.Generic.mirror.mirror_objects(_image, _mline, objs)
    tool.reset()
    doc.getDA().flushTempObjects()
    mirror_init(doc, tool)

#
# Transfer
#
def transfer_init(doc, tool):
    doc.setPrompt("Click on the objects you want to transfer to the active layer")
    tool.setHandler("initialize", transfer_init)
    tool.setHandler("left_button_press", transfer_first_left_button_press_cb)

def transfer_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(NSMakePoint(_x, _y))
    _tol = _da.pointSize().width
    _image = doc.getImage()
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
                    PythonCAD.Generic.transfer.transfer_objects(_objs, _layer, _active_layer)
        finally:
            _image.endAction()
    else:
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setLocation(_x, _y)
        tool.setHandler("mouse_move", select_mouse_move_cb)
        tool.setHandler("left_button_press", transfer_second_left_button_press_cb)

def transfer_second_left_button_press_cb(doc, event, tool):
    tool.delHandler("mouse_move")
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _y1 = tool.popObject()
    _x1 = tool.popObject()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _image = doc.getImage()
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
                    PythonCAD.Generic.transfer.transfer_objects(_objs, _layer, _active_layer)
        finally:
            _image.endAction()
    else:
        doc.getDA().flushTempObjects()
    tool.reset()
    transfer_init(doc, tool)        
    
#
# Move
#

# functions used by all the move code

def move_objects(doc, objs, tool):
    _init_func = tool.getHandler("initialize")
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _dx, _dy = tool.getDistance()
    _image.startAction()
    try:
        PythonCAD.Generic.move.move_objects(_active_layer, objs, _dx, _dy)
    finally:
        _image.endAction()
    doc.getDA().flushTempObjects()
    tool.reset()
    _init_func(doc, tool)

def make_distance(text):
    try:
        _textrad = eval(text)
    except:
        raise ValueError, "Invalid distance: " + text
    if not isinstance(_textrad, float):
        _textrad = float(_textrad)
    return _textrad

def move_select_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(NSMakePoint(_x, _y))
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _objdict = _image.mapPoint(_x, _y, _tol, None)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                _objs.append(_obj)
            move_objects(doc, _objs, tool)
    else:
        _pt, _flag = _image.findPoint(_x, _y, _tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        tool.setLocation(_x, _y)
        tool.setHandler("mouse_move", select_mouse_move_cb)
        tool.setHandler("left_button_press", move_select_second_left_button_press_cb)
        
def move_select_second_left_button_press_cb(doc, event, tool):
    tool.delHandler("mouse_move")
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax, True)
    move_objects(doc, _objs, tool)



# other functions


def move_horizontal_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the horizontal distance")
    tool.setHandler("initialize", move_horizontal_init)
    tool.setHandler("entry_event", move_horizontal_entry_event_cb)
    tool.setHandler("left_button_press", move_horizontal_first_left_button_press_cb)

def move_horizontal_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x, _y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", move_horizontal_second_left_button_press_cb)
    doc.setPrompt("Click another point to define the distance")
    
def move_horizontal_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x2, _y2, _tol)
    if _pt is not None:
        _x2, _y2 = _pt.getCoords()
    _x1, _y1 = tool.getLocation()
    tool.setDistance((_x2 - _x1), 0.0)
    tool.clearLocation()
    tool.delHandler("entry_event")
    tool.setHandler("left_button_press", move_select_first_left_button_press_cb)
    doc.setPrompt("Click on or select the objects to move")
    
def move_horizontal_entry_event_cb(doc, text, tool):
    if len(text):
        _dist = make_distance(text)
        tool.setDistance(_dist, 0.0)
        doc.setPrompt("Click on or select the objects to move")
        tool.delHandler("entry_event")
        tool.setHandler("left_button_press", move_select_first_left_button_press_cb)

def move_vertical_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the vertical distance")
    tool.setHandler("initialize", move_vertical_init)
    tool.setHandler("entry_event", move_vertical_entry_event_cb)
    tool.setHandler("left_button_press", move_vertical_first_left_button_press_cb)

def move_vertical_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x, _y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", move_vertical_second_left_button_press_cb)
    doc.setPrompt("Click another point to define the distance")
    
def move_vertical_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x2, _y2, _tol)
    if _pt is not None:
        _x2, _y2 = _pt.getCoords()
    _x1, _y1 = tool.getLocation()
    tool.setDistance(0.0, (_y2 - _y1))
    tool.clearLocation()
    tool.delHandler("entry_event")
    tool.setHandler("left_button_press", move_select_first_left_button_press_cb)
    doc.setPrompt("Click on or select the objects to move")

def move_vertical_entry_event_cb(doc, text, tool):
    if len(text):
        _dist = make_distance(text)
        tool.setDistance(0.0, _dist)
        doc.setPrompt("Click on or select the objects to move")
        tool.delHandler("entry_event")
        tool.setHandler("left_button_press", move_select_first_left_button_press_cb)


def move_free_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the distance to move as 'h, v'")
    tool.setHandler("initialize", move_free_init)
    tool.setHandler("left_button_press", move_free_first_left_button_press_cb)
    tool.setHandler("entry_event", move_free_entry_event_cb)

def move_free_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x, _y, _tol)
    if _pt is not None:
        _x, _y = _pt.getCoords()
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", move_free_second_left_button_press_cb)
    doc.setPrompt("Click another point to define the distance")
    
def move_free_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _pt, _flag = _image.findPoint(_x2, _y2, _tol)
    if _pt is not None:
        _x2, _y2 = _pt.getCoords()
    _x1, _y1 = tool.getLocation()
    tool.setDistance((_x2 - _x1), (_y2 - _y1))
    tool.clearLocation()
    tool.setHandler("left_button_press", move_select_first_left_button_press_cb)
    doc.setPrompt("Click on or select the objects to move")

def move_free_entry_event_cb(doc, text, tool):
    if len(text):
        _str = string.split(text, ",")
        if len(_str) != 2:
            raise ValueError, "Invalid distance (must be h, v): " + text
        _hdist = make_distance(_str[0])
        _vdist = make_distance(_str[1])
        tool.setDistance(_hdist, _vdist)
        doc.setPrompt("Click on or select the objects to move")
        tool.delHandler("entry_event")
        tool.setHandler("left_button_press", move_select_first_left_button_press_cb)


#
# Stretch
#

def stretch_select_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _da.setTempPoint(NSMakePoint(_x, _y))
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _pt = _active_layer.find('point', _x, _y, _tol)
    if _pt is not None:
        _dx, _dy = tool.getDistance()
        _pt.move(_dx, _dy)
        # should do this better . . .
        _init_func = tool.getHandler("initialize")
        tool.reset()
        _init_func(doc, tool)
        doc.getDA().setNeedsDisplay_(True) 
        
    else:
        tool.setLocation(_x, _y)
        tool.setHandler("mouse_move", select_mouse_move_cb)
        tool.setHandler("left_button_press", stretch_select_second_left_button_press_cb)
            
def stretch_select_second_left_button_press_cb(doc, event, tool):
    tool.delHandler("mouse_move")
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x2)
    _xmax = max(_x1, _x2)
    _ymin = min(_y1, _y2)
    _ymax = max(_y1, _y2)
    _image = doc.getImage()
    _active_layer = _image.getActiveLayer()
    _dx, _dy = tool.getDistance()
    for _pt in _active_layer.getLayerEntities("point"):
        if _pt.x > _xmax:
            break
        if _pt.inRegion(_xmin, _ymin, _xmax, _ymax):
            _pt.move(_dx, _dy)
    # should do this better . . .
    _init_func = tool.getHandler("initialize")
    tool.reset()
    _init_func(doc, tool)
    _da = doc.getDA()
    _da.flushTempObjects()
    _da.setNeedsDisplay_(True) 

def stretch_horizontal_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the horizontal distance")
    tool.setHandler("initialize", stretch_horizontal_init)
    tool.setHandler("entry_event", stretch_horizontal_entry_event_cb)
    tool.setHandler("left_button_press", stretch_horizontal_first_left_button_press_cb)

def stretch_horizontal_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", stretch_horizontal_second_left_button_press_cb)
    doc.setPrompt("Click a second point to indicate the horizontal distance")

def stretch_horizontal_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    (_x1, _y1) = tool.getLocation()
    tool.setDistance((_x2 - _x1), 0.0)
    tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
    tool.delHandler("entry_event")
    doc.setPrompt("Click on or select the objects to stretch")

def stretch_horizontal_entry_event_cb(doc, text, tool):
    if len(text):
        _dist = make_distance(text)
        tool.setDistance(_dist, 0.0)
        tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
        tool.delHandler("entry_event")
        doc.setPrompt("Click on or select the points to stretch")

def stretch_vertical_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the vertical distance")
    tool.setHandler("initialize", stretch_vertical_init)
    tool.setHandler("entry_event", stretch_vertical_entry_event_cb)
    tool.setHandler("left_button_press", stretch_vertical_first_left_button_press_cb)

def stretch_vertical_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", stretch_vertical_second_left_button_press_cb)
    doc.setPrompt("Click a second point to indicate the vertical distance")

def stretch_vertical_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    (_x1, _y1) = tool.getLocation()
    tool.setDistance(0.0, (_y2 - _y1))
    tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
    tool.delHandler("entry_event")
    doc.setPrompt("Click on or select the points to stretch")

def stretch_vertical_entry_event_cb(doc, text, tool):
    if len(text):
        _dist = make_distance(text)
        tool.setDistance(0.0, _dist)
        tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
        tool.delHandler("entry_event")
        doc.setPrompt("Click on or select the points to stretch")


def stretch_free_init(doc, tool):
    doc.setPrompt("Click in the drawing area or enter the distance to stretch as 'h, v'")
    tool.setHandler("initialize", stretch_free_init)
    tool.setHandler("entry_event", stretch_free_entry_event_cb)
    tool.setHandler("left_button_press", stretch_free_first_left_button_press_cb)

def stretch_free_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    tool.setLocation(_x, _y)
    tool.setHandler("left_button_press", stretch_free_second_left_button_press_cb)
    doc.setPrompt("Click a second point to indicate the vertical distance")

def stretch_free_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    (_x1, _y1) = tool.getLocation()
    tool.setDistance((_x2 - _x1), (_y2 - _y1))
    tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
    tool.delHandler("entry_event")
    doc.setPrompt("Click on or select the points to stretch")

def stretch_free_entry_event_cb(doc, text, tool):
    if len(text):
        _str = string.split(text, ",")
        if len(_str) != 2:
            raise ValueError, "Invalid distance (must be h, v): " + text
        _hdist = make_distance(_str[0])
        _vdist = make_distance(_str[1])
        tool.setDistance(_hdist, _vdist)
        tool.setHandler("left_button_press", stretch_select_first_left_button_press_cb)
        tool.delHandler("entry_event")
        doc.setPrompt("Click on or select the points to stretch")


#
# Zoom stuff
#
def zoom_mode_init(doc, tool):
    doc.setPrompt("Click in the drawing area to set the zoom location")
    tool.setHandler("initialize", zoom_mode_init)
    tool.setHandler("left_button_press", zoom_first_left_button_press_cb)

def zoom_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setFirstPoint(_viewLoc.x, _viewLoc.y)
    tool.setLocation(_viewLoc.x, _viewLoc.y)
    _da.setTempPoint(_viewLoc)
    tool.setHandler("left_button_press", zoom_second_left_button_press_cb)
    tool.setHandler("mouse_move", select_mouse_move_cb)
    doc.setPrompt("Move the mouse to select the zoom location")
    
    
def zoom_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x2, _y2) = _da.convertPoint_fromView_(_loc, None)
    (_x1, _y1) = tool.getFirstPoint()
    _x = min(_x1, _x2)
    _y = min(_y1, _y2)
    _w = abs(_x2 - _x1)
    _h = abs(_y2 - _y1)
    _da.setTempObject()
    _da.zoomToRect(((_x, _y), (_w, _h)))
    tool.reset()
    zoom_mode_init(doc, tool)


    
