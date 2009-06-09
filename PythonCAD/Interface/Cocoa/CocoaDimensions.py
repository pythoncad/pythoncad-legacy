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
# Handles creation of dimensions
#

import PythonCAD.Generic.segment
from PythonCAD.Interface.Cocoa import CocoaEntities

#
# Linear, Horizontal, Vertical dimensions all work the same way.
#
def ldim_mode_init(doc, tool):
    doc.setPrompt("Click on the first point for the dimension.")
    tool.setHandler("initialize", ldim_mode_init)
    tool.setHandler("left_button_press", ldim_first_left_button_press_cb)

def ldim_first_mouse_move_cb(doc, np, tool):
    _l1, _p1 = tool.getFirstPoint()
    _p2 = (np.x, np.y)
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2)
    _da = doc.getDA()
    _da.setTempObject(_seg)

def ldim_second_mouse_move_cb(doc, np, tool):
    _ldim = tool.getDimension()
    _ldim.setLocation(np.x, np.y)
    _ldim.calcDimValues()
    _da = doc.getDA()
    _da.setTempObject(_ldim)

def ldim_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = _layer.find('point', _viewLoc.x, _viewLoc.y, _tol)
            if _pt is not None:
                _x, _y = _pt.getCoords()
                _da.setTempPoint(_viewLoc)
                tool.setLocation(_x, _y)
                tool.setFirstPoint(_layer, _pt)
                tool.setHandler("left_button_press", ldim_second_left_button_press_cb)
                tool.setHandler("mouse_move", ldim_first_mouse_move_cb)
                doc.setPrompt("Click on the second point for the dimension.")
            break
        _layers.extend(_layer.getSublayers())

              
def ldim_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = _layer.find('point', _viewLoc.x, _viewLoc.y, _tol)
            if _pt is not None:
                _x, _y = _pt.getCoords()
                tool.setSecondPoint(_layer, _pt)
                tool.setDimPosition(_x, _y)
                tool.clearCurrentPoint()
                tool.makeDimension(_image)
                tool.setHandler("left_button_press", ldim_third_left_button_press_cb)
                tool.setHandler("mouse_move", ldim_second_mouse_move_cb)
                doc.setPrompt("Click where the dimension text should be placed.")
                break
        _layers.extend(_layer.getSublayers())
            
def ldim_third_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _ldim = tool.getDimension()
    _ldim.setLocation(_viewLoc.x, _viewLoc.y)
    _ldim.calcDimValues()
    _ldim.reset()
    CocoaEntities.create_entity(doc, tool)

#
# Radial
#
def radial_mode_init(doc, tool):
    doc.setPrompt("Click on an arc or a circle to dimension.")
    tool.setHandler("initialize", radial_mode_init)
    tool.setHandler("left_button_press", radial_first_left_button_press_cb)

def radial_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    _dc = _dl = None
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _cobjs = (_layer.getLayerEntities("circle") +
                      _layer.getLayerEntities("arc"))
            for _cobj in _cobjs:
                _mp = _cobj.mapCoords(_viewLoc.x, _viewLoc.y, _tol)
                if _mp is not None:
                    _dc = _cobj
                    _dl = _layer
                    break
        _layers.extend(_layer.getSublayers())
    if _dc is not None:
        _x, _y = _mp
        tool.setDimObject(_dl, _dc)
        tool.setDimPosition(_x, _y)
        tool.makeDimension(_image)
        tool.setHandler("mouse_move", radial_mouse_move_cb)
        tool.setHandler("left_button_press", radial_second_left_button_press_cb)
        doc.setPrompt("Click where the dimension text should be placed.")

def radial_mouse_move_cb(doc, np, tool):
    _rdim = tool.getDimension()
    _rdim.setLocation(np.x, np.y)
    _rdim.calcDimValues()
    _da = doc.getDA()
    _da.setTempObject(_rdim)

def radial_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _ldim = tool.getDimension()
    _ldim.setLocation(_viewLoc.x, _viewLoc.y)
    _ldim.calcDimValues()
    _ldim.reset()
    CocoaEntities.create_entity(doc, tool)
      

#
# Angular
#
def angular_mode_init(doc, tool):
    doc.setPrompt("Click on the angle vertex point or an arc.")
    tool.setHandler("initialize", angular_mode_init)
    tool.setHandler("left_button_press", angular_first_left_button_press_cb)

def angular_first_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    _pt = _arc = None
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt, _arc = _test_layer(_layer, _viewLoc.x, _viewLoc.y, _tol)
            if _pt is not None or _arc is not None:
                break
        _layers.extend(_layer.getSublayers())
    if _pt is not None:
        tool.setVertexPoint(_layer, _pt)
        _da.setTempPoint(_viewLoc)
        tool.setHandler("left_button_press", angular_second_left_button_press_cb)
        tool.setHandler("mouse_move", angular_segment_mouse_move_cb)
        doc.setPrompt("Click on the first endpoint for the dimension.")
    elif _arc is not None:
        _cp = _arc.getCenter()
        tool.setVertexPoint(_layer, _cp)
        _ep1, _ep2 = _arc.getEndpoints()
        _ex, _ey = _ep1
        _p1 = _layer.find('point', _ex, _ey)
        assert _p1 is not None, "Missing arc endpoint"
        tool.setFirstPoint(_layer, _p1)
        _ex, _ey = _ep2
        _p2 = _layer.find('point', _ex, _ey)
        assert _p2 is not None, "Missing arc endpoint"
        tool.setSecondPoint(_layer, _p2)
        tool.setDimPosition(_viewLoc.x, _viewLoc.y)
        tool.makeDimension(_image)
        tool.setHandler("left_button_press", angular_fourth_left_button_press_cb)
        tool.setHandler("mouse_move", angular_text_mouse_move_cb)
        doc.setPrompt("Click where the dimension text should be located.")
       
def angular_second_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = _layer.find('point', _x, _y, _tol)
            if _pt is not None:
                _x, _y = _pt.getCoords()
                tool.setLocation(_x, _y)
                tool.setFirstPoint(_layer, _pt)
                tool.setHandler("left_button_press", angular_third_left_button_press_cb)
                tool.setHandler("mouse_move", angular_segment_mouse_move_cb)
                doc.setPrompt("Click on the second endpoint for the dimension.")
                break
        _layers.extend(_layer.getSublayers())

def angular_third_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _tol = _da.pointSize().width
    _image = doc.getImage()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = _layer.find('point', _x, _y, _tol)
            if _pt is not None:
                _x, _y = _pt.getCoords()
                tool.setLocation(_x, _y)
                tool.setSecondPoint(_layer, _pt)
                tool.setDimPosition(_x, _y)
                tool.makeDimension(_image)
                tool.setHandler("left_button_press", angular_fourth_left_button_press_cb)
                tool.setHandler("mouse_move", angular_text_mouse_move_cb)
                doc.setPrompt("Click where the dimension text should be located.")
                break
        _layers.extend(_layer.getSublayers())
    
def angular_fourth_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    (_x, _y) = _da.convertPoint_fromView_(_loc, None)
    _adim = tool.getDimension()
    _adim.setLocation(_x, _y)
    _adim.calcDimValues()
    _adim.reset()
    CocoaEntities.create_entity(doc, tool)

def angular_segment_mouse_move_cb(doc, np, tool):
    _l1, _p1 = tool.getVertexPoint()
    _l2, _p2 = tool.getFirstPoint()
    _da = doc.getDA()
    _flag = True
    if _p2 is not None:
        _seg = PythonCAD.Generic.segment.Segment(_p1, _p2)
        _da.setTempObject(_seg, _flag)
        _flag = False
    _p2 = (np.x, np.y)
    _seg = PythonCAD.Generic.segment.Segment(_p1, _p2)
    _da.setTempObject(_seg, _flag)
    

def angular_text_mouse_move_cb(doc, np, tool):
    _adim = tool.getDimension()
    _adim.setLocation(np.x, np.y)
    _adim.calcDimValues()
    _da = doc.getDA()
    _da.setTempObject(_adim)
    
        
def _test_layer(layer, x, y, tol):
    _arc = None
    _pt = layer.find('point', x, y)
    if _pt is None:
        _pt = layer.find('point', x, y, tol)
        if _pt is None:
            _arc_pt = None
            for _arc in layer.getLayerEntities("arc"):
                _arc_pt = _arc.mapCoords(x, y, tol)
                if _arc_pt is not None:
                    break
            if _arc_pt is None:
                _arc = None # no hits on any arcs ...
    return _pt, _arc
