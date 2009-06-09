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
# functions for doing mirroring operations
#

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic import mirror

def mirror_objects(gtkimage, tool, objs):
    _mline = tool.getMirrorLine()
    tool.reset()
    _prompt = _('Click on the mirroring construction line.')
    if len(objs):
        _image = gtkimage.getImage()
        _image.startAction()
        try:
            mirror.mirror_objects(_mline, objs)
        finally:
            _image.endAction()
        mirror_mode_init(gtkimage)
    else:
        gtkimage.refresh()
        _prompt = ('Click on an object to mirror')
        tool.setMirrorLine(_mline)
        tool.setHandler("button_press", first_button_press_cb)
    gtkimage.setPrompt(_prompt)
        
    
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

def second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _pts = _active_layer.find('point', _x, _y)
    if len(_pts) > 0:
        _x, _y = _pts[0].getCoords()
    _x1, _y1 = tool.getLocation()
    _xmin = min(_x1, _x)
    _ymin = min(_y1, _y)
    _xmax = max(_x1, _x)
    _ymax = max(_y1, _y)
    _objs = _active_layer.objsInRegion(_xmin, _ymin, _xmax, _ymax, True)
    mirror_objects(gtkimage, tool, _objs)
    return True

def first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            _objs = []
            for _obj, _pt in _objdict[_active_layer]:
                _objs.append(_obj)
            mirror_objects(gtkimage, tool, _objs)
    else:
        _pt, _pc = _image.getClosestPoint(_x, _y, tolerance=_tol)
        if _pt is not None:
            _x, _y = _pt.getCoords()
        else:
            _x, _y = _pc
        tool.setLocation(_x, _y)
        tool.setHandler("motion_notify", select_motion_notify)
        tool.setHandler("button_press", second_button_press_cb)
        gtkimage.setPrompt(_('Enclose objects to mirror with the box'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True
        
def get_mirror_line_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _objdict = _image.mapPoint(_x, _y, _tol)
    if len(_objdict):
        _active_layer = _image.getActiveLayer()
        if _active_layer in _objdict:
            for _obj, _pt in _objdict[_active_layer]:
                if isinstance(_obj, (HCLine, VCLine, ACLine, CLine)):
                    tool.setMirrorLine(_obj)
                    if _image.hasSelection():
                        mirror_objects(gtkimage, tool,
                                       _image.getSelectedObjects())
                    else:
                        tool.setHandler("button_press", first_button_press_cb)
                        gtkimage.setPrompt(_('Click on an object to mirror'))
                    break
    return True

def mirror_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the mirroring construction line'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", get_mirror_line_cb)
