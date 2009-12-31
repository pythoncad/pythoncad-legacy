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
# <tangent cline creation> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
from PythonCAD.Generic import CCircle,Circle,Arc,Point,ACLine
from PythonCAD.Generic.pyGeoLib import Vector
#
# Init
#
def tangent_cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the circle object you want a tangent to'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", tangent_cline_button_press_cb)
#
# Motion Notifie
#

#
# Button press callBacks
#
def tangent_cline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'tangent':False}
    _pt=snap.getOnlySnap(_image,_tol,_snapArray)
    if _pt is not None:
        _x, _y = _pt.point.getCoords()
        _layer = _image.getActiveLayer()
        _rtd = 180.0/pi
        _cobj = None
        _angle = None
        _circleEnt=_pt.entity
        if isinstance(_circleEnt,(CCircle,Circle,Arc)):
            _cp=_circleEnt.getCenter()
            _rad = _circleEnt.getRadius()
            _v=Vector(_cp,_pt.point).Mag()
            _v.Mult(_rad)
            _vectPoint=_v.Point()
            _x,_y=(_vectPoint+_cp)
            _cx,_cy=_cp.getCoords()
            if abs(hypot((_x - _cx), (_y - _cy)) - _rad) < 1e-10:
                _cobj = _circleEnt
                _angle = _rtd * atan2((_y - _cy), (_x - _cx))
                if _angle < 0.0:
                    _angle = _angle + 360.0
                _pt=Point(_x,_y)
        if _cobj is not None:
            _image.startAction()
            try:
                if _pt:
                    _layer.addObject(_pt)
                if (abs(_angle) < 1e-6 or
                    abs(_angle - 180.0) < 1e-6 or
                    abs(_angle - 360.0) < 1e-6):
                    _tcl = VCLine(_pt)
                elif (abs(_angle - 90.0) < 1e-6 or
                      abs(_angle - 270.0) < 1e-6):
                    _tcl = HCLine(_pt)
                else:
                    _slope = _angle + 90.0
                    _tcl = ACLine(_pt, _slope)
                _layer.addObject(_tcl)
            finally:
                _image.endAction()
    return True
#
# Entry callBacks
#

#
# Suport functions
#