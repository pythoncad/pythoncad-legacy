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
# <> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic.dimension import Dimension
from PythonCAD.Generic import snap
from PythonCAD.Interface.Command.cmdCommon import * 
#
# Init for linear,horizontal,vertical
#

def linear_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first point for the dimension.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", linear_first_button_press_cb)
    _tool.setHandler("initialize", linear_mode_init)


def horizontal_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first point for the dimension.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", linear_first_button_press_cb)
    _tool.setHandler("initialize", horizontal_mode_init)

def vertical_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first point for the dimension.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", linear_first_button_press_cb)
    _tool.setHandler("initialize", vertical_mode_init)
#
# Motion Notifie
#
def dim_pts_motion_notify_cb(gtkimage, widget, event, tool):
    _tx, _ty = tool.getLocation()
    _px, _py = gtkimage.coordToPixTransform(_tx, _ty)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    _segs = []
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px, _py, _xc, _yc))
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px, _py, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True

def dim_txt_motion_notify_cb(gtkimage, widget, event, tool):
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _gc = gtkimage.getGC()
    _ex = int(event.x)
    _ey = int(event.y)
    _cp = tool.getCurrentPoint()
    _dim = tool.getDimension()
    _bar1, _bar2 = _dim.getDimBars()
    _crossbar = _dim.getDimCrossbar()
    _segs = []
    if _cp is not None:
        _ep1, _ep2 = _bar1.getEndpoints()
        _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
        _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
        _segs.append((_px1, _py1, _px2, _py2))
        _ep1, _ep2 = _bar2.getEndpoints()
        _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
        _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
        _segs.append((_px1, _py1, _px2, _py2))
        _ep1, _ep2 = _crossbar.getEndpoints()
        _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
        _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
        _segs.append((_px1, _py1, _px2, _py2))
    tool.setCurrentPoint(_ex, _ey)
    _dim.setLocation(_ix, _iy)
    _dim.calcDimValues(False)
    _ep1, _ep2 = _bar1.getEndpoints()
    _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
    _segs.append((_px1, _py1, _px2, _py2))
    _ep1, _ep2 = _bar2.getEndpoints()
    _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
    _segs.append((_px1, _py1, _px2, _py2))
    _ep1, _ep2 = _crossbar.getEndpoints()
    _px1, _py1 = gtkimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gtkimage.coordToPixTransform(_ep2[0], _ep2[1])
    _segs.append((_px1, _py1, _px2, _py2))
    widget.window.draw_segments(_gc, _segs)
    return True
#
# Button press callBacks
#
def linear_first_button_press_cb(gtkimage, widget, event, tool):
    _snapArray={'perpendicular':False,'tangent':False}
    _strPnt=snap.getSnapOnTruePoint(gtkimage,_snapArray)
    if _strPnt is not None:
        _x, _y =_strPnt.point.getCoords()
        tool.setLocation(_x, _y)
        tool.setFirstPoint(_strPnt.point)
        tool.setHandler("button_press", linear_second_button_press_cb)
        tool.setHandler("motion_notify", dim_pts_motion_notify_cb)
        gtkimage.setPrompt(_('Click on the second point for the dimension.'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    else:
        gtkimage.setPrompt(_('Click on the first point for the dimension.'))
        tool.setHandler("button_press", linear_first_button_press_cb)
        tool.setHandler("initialize", linear_mode_init)
    return True

def linear_second_button_press_cb(gtkimage, widget, event, tool):
    _snapArray={'perpendicular':False,'tangent':False}
    _strPnt=snap.getSnapOnTruePoint(gtkimage,_snapArray)
    if _strPnt.point is not None:
        _x, _y = _strPnt.point.getCoords()
        tool.setSecondPoint(_strPnt.point)
        tool.setDimPosition(_x, _y)
        tool.clearCurrentPoint()
        tool.makeDimension(gtkimage.getImage())
        #
        # set GraphicsContext to Dimension color
        #
        _gc = gtkimage.getGC()
        _gc.set_function(gtk.gdk.INVERT)
        _col = tool.getDimension().getColor()
        _gc.set_foreground(gtkimage.getColor(_col))
        tool.setHandler("button_press", linear_text_button_press_cb)
        tool.setHandler("motion_notify", dim_txt_motion_notify_cb)
        gtkimage.setPrompt(_('Click where the dimension text should go.'))
        gtkimage.refresh()
    return True

#
# Entry callBacks
#
def linear_text_button_press_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    _ldim = tool.getDimension()
    _ldim.setLocation(_x, _y)
    _ldim.calcDimValues()
    _ldim.reset()
    add_dimension(gtkimage)
    return True
#
# Suport functions
#


