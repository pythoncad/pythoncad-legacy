#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo
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
# <Angula Dimension> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command.cmdCommon import *
#
# Init
#
def angular_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the angle vertex point or an arc.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", angular_initial_button_press_cb)
    _tool.setHandler("initialize", angular_mode_init)
#
# Motion Notifie
#
def adim_txt_motion_notify_cb(gtkimage, widget, event, tool):
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _gc = gtkimage.getGC()
    _ex = int(event.x)
    _ey = int(event.y)
    _cp = tool.getCurrentPoint()
    _adim = tool.getDimension()
    _vx, _vy = _adim.getVertexPoint().getCoords()
    _px, _py = gtkimage.coordToPixTransform(_vx, _vy)
    _win = widget.window
    _bar1, _bar2 = _adim.getDimBars()
    _crossarc = _adim.getDimCrossarc()
    _segs = []
    if _cp is not None:
        #
        # draw bars
        #
        _ep1, _ep2 = _bar1.getEndpoints()        
        _p1x, _p1y = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
        _p2x, _p2y = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
        _segs.append((_p1x, _p1y, _p2x, _p2y))
        _ep1, _ep2 = _bar2.getEndpoints()
        _p1x, _p1y = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
        _p2x, _p2y = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
        _segs.append((_p1x, _p1y, _p2x, _p2y))
        _win.draw_segments(_gc, _segs)
        del _segs[:]
        #
        # draw arc
        #
        _sa = _crossarc.getStartAngle()
        _ea = _crossarc.getEndAngle()
        _rad = int(_crossarc.getRadius()/gtkimage.getUnitsPerPixel())
        _pxmin = _px - _rad
        _pymin = _py - _rad
        _cw = _ch = _rad * 2
        if _sa < _ea:
            _sweep = _ea - _sa
        else:
            _sweep = 360.0 - (_sa - _ea)
        _win.draw_arc(_gc, False, _pxmin, _pymin, _cw, _ch,
                      int(_sa * 64), int(_sweep * 64))
    tool.setCurrentPoint(_ex, _ey)
    _adim.setLocation(_ix, _iy)
    _adim.calcDimValues(False)
    #
    # draw bars
    #
    _ep1, _ep2 = _bar1.getEndpoints()        
    _p1x, _p1y = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
    _p2x, _p2y = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
    _segs.append((_p1x, _p1y, _p2x, _p2y))
    _ep1, _ep2 = _bar2.getEndpoints()
    _p1x, _p1y = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
    _p2x, _p2y = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
    _segs.append((_p1x, _p1y, _p2x, _p2y))
    _win.draw_segments(_gc, _segs)
    #
    # draw arc
    #
    _sa = _crossarc.getStartAngle()
    _ea = _crossarc.getEndAngle()
    _rad = int(_crossarc.getRadius()/gtkimage.getUnitsPerPixel())
    _pxmin = _px - _rad
    _pymin = _py - _rad
    _cw = _ch = _rad * 2
    if _sa < _ea:
        _sweep = _ea - _sa
    else:
        _sweep = 360.0 - (_sa - _ea)
    _win.draw_arc(_gc, False, _pxmin, _pymin, _cw, _ch,
                  int(_sa * 64), int(_sweep * 64))
    return True
#
# Button press callBacks
#
def angular_initial_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pt, _arc = _test_layer(_active_layer, _x, _y, _tol)
    if _pt is None and _arc is None:
        _layers = [_image.getTopLayer()]
        while len(_layers):
            _layer = _layers.pop()
            if _layer is not _active_layer and _layer.isVisible():
                _pt, _arc = _test_layer(_layer, _x, _y, _tol)
                if _pt is not None or _arc is not None:
                    break
            _layers.extend(_layer.getSublayers())
    if _pt is not None:
        tool.setVertexPoint(_pt)
        tool.setHandler("button_press", angular_first_button_press_cb)
        gtkimage.setPrompt(_('Click on the first endpoint for the dimension.'))
    elif _arc is not None:
        _cp = _arc.getCenter()
        tool.setVertexPoint(_cp)
        _ep1, _ep2 = _arc.getEndpoints()
        _ex, _ey = _ep1
        _pts = _active_layer.find('point', _ex, _ey)
        assert len(_pts) > 0, "Missing arc first endpoint"
        tool.setFirstPoint(_pts[0])
        _ex, _ey = _ep2
        _pts = _active_layer.find('point', _ex, _ey)
        assert len(_pts) > 0, "Missing arc second endpoint"
        tool.setSecondPoint(_pts[0])
        tool.setDimPosition(_x, _y)
        tool.makeDimension(_image)
        tool.setHandler("button_press", angular_text_button_press_cb)
        tool.setHandler("motion_notify", adim_txt_motion_notify_cb)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
        gtkimage.setPrompt(_('Click where the dimension text should be located.'))
    return True

def angular_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = None
            _pts = _layer.find('point', _x, _y, _tol)
            if len(_pts) > 0:
                _pt = _pts[0]
            if _pt is not None:
                _x, _y = _pt.getCoords()
                tool.setLocation(_x, _y)
                tool.setFirstPoint(_pt)
                tool.setHandler("button_press", angular_second_button_press_cb)
                gtkimage.setPrompt(_('Click on the second point for the dimension.'))
                break
        _layers.extend(_layer.getSublayers())
    return True

def angular_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _layers = [_image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = None
            _pts = _layer.find('point', _x, _y, _tol)
            if len(_pts) > 0:
                _pt = _pts[0]
            if _pt is not None:
                _x, _y = _pt.getCoords()
                tool.setLocation(_x, _y)
                tool.setSecondPoint(_pt)
                tool.setDimPosition(_x, _y)
                tool.makeDimension(_image)
                #
                # set GraphicsContext to Dimension color
                #
                _gc = gtkimage.getGC()
                _gc.set_function(gtk.gdk.INVERT)
                _col = tool.getDimension().getColor()
                _gc.set_foreground(gtkimage.getColor(_col))
                tool.setHandler("button_press", angular_text_button_press_cb)
                tool.setHandler("motion_notify", adim_txt_motion_notify_cb)
                gtkimage.setPrompt(_('Click where the dimension text should be located.'))
                gtkimage.refresh()
                break
        _layers.extend(_layer.getSublayers())
    return True

def angular_text_button_press_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    _adim = tool.getDimension()
    _adim.setLocation(_x, _y)
    _adim.calcDimValues()
    _adim.reset()
    add_dimension(gtkimage)
    return True

def angular_pts_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pt = None
    _pts = _active_layer.find('point',_x, _y, _tol)
    if len(_pts) > 0:
        _pt = _pts[0]
    if _pt is None:
        _layers = [_image.getTopLayer()]
        while(len(_layers)):
            _layer = _layers.pop()
            if _layer is not _active_layer and _layer.isVisible():
                _pts = _layer.find('point', _x, _y, _tol)
                if len(_pts) > 0:
                    _pt = _pts[0]
                    break
            _layers.extend(_layer.getSublayers())
    if _pt is not None:
        _x, _y = _pt.getCoords()
        tool.storeCoords(_x, _y)
        if len(tool) == 2:
            tool.pushObject(_pt)
        else:
            from PythonCAD.Generic.dimension import AngularDimension
            _p1 = tool.popObject()
            _vp = tool.popObject()
            _ds = _image.getOption("DIM_STYLE")
            _adim = AngularDimension(_vp, _p1, _pt, _x, _y, _ds)
            tool.pushObject(_adim)
    return True

#
# Entry callBacks
#

#
# Suport functions
#
def _test_layer(l, x, y, tol):
    _pt = _arc = None
    _pts = l.find('point', x, y)
    if len(_pts) > 0:
        _pt = _pts[0]
    if _pt is None:
        _pts = l.find('point', x, y, tol)
        if len(_pts) > 0:
            _pt = _pts[0]
        if _pt is None:
            _arc_pt = None
            for _arc in l.getLayerEntities("arc"):
                _arc_pt = _arc.mapCoords(x, y, tol)
                if _arc_pt is not None:
                    break
            if _arc_pt is None:
                _arc = None # no hits on any arcs ...
    return _pt, _arc
