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
# <Parallel Construction Line> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle  import Circle 
from PythonCAD.Generic.arc     import Arc
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.util import *
from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def parallel_offset_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Enter the distance or click in the drawing area.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", parallel_offset_mode_init)
    _tool.setHandler("button_press", parallel_first_button_press_cb)
    _tool.setHandler("entry_event", parallel_entry_event)
#
# Motion Notifie
#

#
# Button press callBacks
#
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

def parallel_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _snp=snap.getSnapPoint(_image,_tol,_snapArray)
    _x,_y=_snp.point.getCoords()
    print "Debug: " + str(tool.getLocation())
    _x1, _y1 = tool.getLocation()
    _offset = hypot((_x - _x1), (_y - _y1))
    tool.setOffset(_offset)
    tool.setHandler("button_press", parallel_conline_button_press_cb)
    gtkimage.setPrompt(_('Click on the reference construction line.'))
    return True
#
# Entry callBacks
#
def parallel_entry_event(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _dist = get_float(eval(_text, gtkimage.image.getImageVariables()))
        tool.setOffset(_dist)
        tool.delHandler("entry_event")
        tool.setHandler("button_press", parallel_conline_button_press_cb)
        gtkimage.setPrompt(_('Click on the reference construction line.'))
#
# Suport functions
#












