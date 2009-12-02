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
# <tangent lines around two circles> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Generic.color import Color
from PythonCAD.Interface.Command import cmdCommon
from PythonCAD.Generic import CCircle,Circle,Arc,Point,ACLine

#
# Init
#
def two_circle_tangent_line_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the first construction circle.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", two_circle_tangent_line_mode_init)
    _tool.setHandler("button_press", two_circle_tangent_first_button_press_cb)
#
# Motion Notifie
#

#
# Button press callBacks
#
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
#
# Entry callBacks
#

#
# Suport functions
#
def two_ccircle_tangent_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    tool.setLocation(_x, _y)
    cmdCommon.create_entity(gtkimage)

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





