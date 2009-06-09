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
# handle cut, copy, paste, selections, etc
#

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
from PythonCAD.Generic.dimension import LinearDimension
from PythonCAD.Generic.dimension import HorizontalDimension
from PythonCAD.Generic.dimension import VerticalDimension
from PythonCAD.Generic.dimension import RadialDimension
from PythonCAD.Generic.dimension import AngularDimension
from PythonCAD.Generic import text
import PythonCAD.Generic.globals

def select_region_end_cb(gtkimage, widget, event, tool):
    # print "called select_region_end_callback()"
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
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
    if len(_objs):
        _image.sendMessage('group_action_started')
        try:
            for _obj in _objs:
                _image.selectObject(_obj)
        finally:
            _image.sendMessage('group_action_ended')
    gtkimage.setPrompt(_('Click on the items you want to select.'))
    select_mode_init(gtkimage)

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

def select_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    # print "x: %g; y: %g" % (_x, _y)
    _active_layer = _image.getActiveLayer()
    _pts = _active_layer.find('point', _x, _y, _tol)
    if len(_pts) > 0:
        _image.sendMessage('group_action_started')
        try:
            for _pt in _pts:
                _image.selectObject(_pt)
        finally:
            _image.sendMessage('group_action_ended')
    else:
        _objs = []
        for _tb in _active_layer.getLayerEntities('text'):
            # print "testing tb: " + `_tb`
            _tx, _ty = _tb.getLocation()
            # print "tx: %g; ty: %g" % (_tx, _ty)
            _bounds = _tb.getBounds()
            if _bounds is not None:
                # print "has bounds ..."
                _w, _h = _bounds
                _align = _tb.getAlignment()
                if _align == text.TextStyle.ALIGN_LEFT:
                    _txmin = _tx
                    _txmax = _tx + _w
                elif _align == text.TextStyle.ALIGN_CENTER:
                    _off = _w/2.0
                    _txmin = _tx - _off 
                    _txmax = _tx + _off
                elif _align == text.TextStyle.ALIGN_RIGHT:
                    _txmin = _tx - _w
                    _txmax = _tx
                else:
                    raise ValueError, "Unexpected alignment: %d" % _align
                _tymin = _ty - _h
                _tymax = _ty
                # print "txmin: %g" % _txmin
                # print "tymin: %g" % _tymin
                # print "txmax: %g" % _txmax
                # print "tymax: %g" % _tymax
                if _txmin < _x < _txmax and _tymin < _y < _tymax:
                    _objs.append(_tb)
        for _obj, _pt in _active_layer.mapPoint((_x, _y), _tol):
            _objs.append(_obj)
        if len(_objs):
            _image.sendMessage('group_action_started')
            try:
                for _obj in _objs:
                    _image.selectObject(_obj)
            finally:
                _image.sendMessage('group_action_ended')
        else:
            # print "no objects ..."
            gtkimage.setPrompt(_('Click on another point to select the region.'))
            gc = gtkimage.getGC()
            gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                   gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
            gc.set_function(gtk.gdk.INVERT)
            tool.setLocation(_x, _y)
            tool.pushObject(_x)
            tool.pushObject(_y)
            tool.setHandler("motion_notify", select_motion_notify)
            tool.setHandler("button_press", select_region_end_cb)

def select_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the items you want to select.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", select_button_press_cb)

def deselect_region_end_cb(gtkimage, widget, event, tool):
    # print "called deselect_region_end_callback()"
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
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
    if len(_objs):
        _sobjs = {}
        for _obj in _image.getSelectedObjects(False):
            if _obj.getParent() is _active_layer:
                _sobjs[id(_obj)] = True
        _image.sendMessage('group_action_started')
        try:
            for _obj in _objs:
                if id(_obj) in _sobjs:
                    _image.deselectObject(_obj)
        finally:
            _image.sendMessage('group_action_ended')
    gtkimage.setPrompt(_('Click on the items you want to deselect.'))
    deselect_mode_init(gtkimage)

def deselect_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    # print "x: %g; y: %g" % (_x, _y)
    _active_layer = _image.getActiveLayer()
    _objs = []
    for _obj in _image.getSelectedObjects(False):
        if _obj.getParent() is _active_layer:
            if isinstance(_obj, Point):
                if abs(_obj.x - _x) < _tol and abs(_obj.y - _y) < _tol:
                    _objs.append(_obj)
            elif isinstance(_obj, text.TextBlock):
                _tx, _ty = _obj.getLocation()
                _bounds = _obj.getBounds()
                if _bounds is not None:
                    _w, _h = _bounds
                    _align = _obj.getAlignment()
                    if _align == text.TextStyle.ALIGN_LEFT:
                        _txmin = _tx
                        _txmax = _tx + _w
                    elif _align == text.TextStyle.ALIGN_CENTER:
                        _off = _w/2.0
                        _txmin = _tx - _off 
                        _txmax = _tx + _off
                    elif _align == text.TextStyle.ALIGN_RIGHT:
                        _txmin = _tx - _w
                        _txmax = _tx
                    else:
                        raise ValueError, "Unexpected alignment: %d" % _align
                    _tymin = _ty - _h
                    _tymax = _ty
                    if _txmin < _x < _txmax and _tymin < _y < _tymax:
                        _objs.append(_obj)
            elif _obj.mapCoords(_x, _y, _tol) is not None:
                _objs.append(_obj)
            else:
                pass
    if len(_objs):
        _image.sendMessage('group_action_started')
        try:
            for _obj in _objs:
                _image.deselectObject(_obj)
        finally:
            _image.sendMessage('group_action_ended')
    else:
        gtkimage.setPrompt(_('Click on another point to select the region.'))
        gc = gtkimage.getGC()
        gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                               gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        gc.set_function(gtk.gdk.INVERT)
        tool.setLocation(_x, _y)
        tool.pushObject(_x)
        tool.pushObject(_y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", deselect_region_end_cb)

def deselect_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the items you want to deselect.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", deselect_button_press_cb)

def paste_button_press_cb(gtkimage, widget, event, tool):
    # print "called paste_button_press_cb()"
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    # print "x: %g; y: %g" % (_x, _y)
    _active_layer = _image.getActiveLayer()
    _objs = PythonCAD.Generic.globals.selectobj.getObjects()
    _objmap = {}
    _image.startAction()
    try:
        for _obj in _objs:
            if isinstance(_obj, Point):
                if not _objmap.has_key('point'):
                    _objmap['point'] = {}
                _pt = Point(_x, _y)
                _ept = _active_layer.findObject(_pt)
                if _ept is None:
                    _active_layer.addObject(_pt)
                    _objmap['point'][_obj] = _pt
                else:
                    _objmap['point'][_obj] = _ept
            elif isinstance(_obj, Segment):
                if not _objmap.has_key('segment'):
                    _objmap['segment'] = {}
                _cseg = _obj.clone()
                _cseg.move(_x, _y)
                _eseg = _active_layer.findObject(_cseg)
                if _eseg is None:
                    _p1, _p2 = _cseg.getEndpoints()
                    _ep = _active_layer.findObject(_p1)
                    if _ep is None:
                        _active_layer.addObject(_p1)
                    else:
                        _cseg.setP1(_ep)
                    _ep = _active_layer.findObject(_p2)
                    if _ep is None:
                        _active_layer.addObject(_p2)
                    else:
                        _cseg.setP2(_ep)
                    _active_layer.addObject(_cseg)
                else:
                    _objmap['segment'][_obj] = _eseg
            elif isinstance(_obj, (Circle, Arc, CCircle)):
                _cc = _obj.clone()
                _cc.move(_x, _y)
                _ec = _active_layer.findObject(_cc)
                if _ec is None:
                    _cp = _cc.getCenter()
                    _ep = _active_layer.findObject(_cp)
                    if _ep is None:
                        _active_layer.addObject(_cp)
                    else:
                        _cc.setLocation(_ep)
                    _active_layer.addObject(_cc)
            elif isinstance(_obj, (HCLine, VCLine, ACLine)):
                _ccl = _obj.clone()
                _ccl.move(_x, _y)
                _ecl = _active_layer.findObject(_ccl)
                if _ecl is None:
                    _lp = _ccl.getLocation()
                    _ep = _active_layer.findObject(_lp)
                    if _ep is None:
                        _active_layer.addObject(_lp)
                    else:
                        _ccl.setLocation(_ep)
                    _active_layer.addObject(_ccl)
            elif isinstance(_obj, CLine):
                _ccl = _obj.clone()
                _ccl.move(_x, _y)
                _ecl = _active_layer.findObject(_ccl)
                if _ecl is None:
                    _p1, _p2 = _ccl.getKeypoints()
                    _ep = _active_layer.findObject(_p1)
                    if _ep is None:
                        _active_layer.addObject(_p1)
                    else:
                        _ccl.setP1(_ep)
                    _ep = _active_layer.findObject(_p2)
                    if _ep is None:
                        _active_layer.addObject(_p2)
                    else:
                        _ccl.setP2(_ep)
                    _active_layer.addObject(_ccl)
            elif isinstance(_obj, LinearDimension):
                if _active_layer.findObject(_obj) is None:
                    _l1, _l2 = _obj.getDimLayers()
                    if _image.hasLayer(_l1) and _image.hasLayer(_l2):
                        _p1, _p2 = _obj.getDimPoints()
                        _ds = _obj.getDimStyle()
                        if isinstance(_obj, HorizontalDimension):
                            _dtype = HorizontalDimension
                        elif isinstance(_obj, VerticalDimension):
                            _dtype = VerticalDimension
                        else:
                            _dtype = LinearDimension
                        _dim = _dtype(_l1, _p1, _l2, _p2, _x, _y, _ds)
                        _active_layer.addObject(_dim)
            elif isinstance(_obj, RadialDimension):
                if _active_layer.findObject(_obj) is None:
                    _lyr = _obj.getDimLayer()
                    if _image.hasLayer(_lyr):
                        _dc = _obj.getDimCircle()
                        _ds = _obj.getDimStyle()
                        _dim = RadialDimension(_lyr, _dc, _x, _y, _ds)
                        _active_layer.addObject(_dim)
            elif isinstance(_obj, AngularDimension):
                if _active_layer.findObject(_obj) is None:
                    _cl, _l1, _l2 = _obj.getDimLayers()
                    if (_image.hasLayer(_cl) and
                        _image.hasLayer(_l1) and
                        _image.hasLayer(_l2)):
                        _cp, _p1, _p2 = _obj.getDimPoints()
                        _ds = _obj.getDimStyle()
                        _dim = AngularDimension(_cl, _cp, _l1, _p1, _l2, _p2, _x, _y, _ds)
                        _active_layer.addObject(_dim)
            elif isinstance(_obj, text.TextBlock):
                _ntb = _obj.clone()
                _ntb.setLocation(_x, _y)
                _active_layer.addObject(_ntb)
            else:
                print "Unexpected type for pasting: " + `type(_obj)`
    finally:
        _image.endAction()
    
def paste_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click where you want to paste the objects'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", paste_button_press_cb)
