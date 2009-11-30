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
# <perpendicular construction line creation> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def perpendicular_cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the object you want a perpendicular to'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", perp_cline_button_press_cb)
#
# Motion Notifie
#

#
# Button press callBacks
#
def perp_cline_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _pt,_pc=snap.getSnapPoint(_image,_tol,_snapArray).point.getCoords()
    _active_layer = _image.getActiveLayer()
    _hits = _active_layer.mapPoint((_pt,_pc), _tol, 1)
    if len(_hits):
        _obj, _lp = _hits[0]
        _pcl = None
        if isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            else:
                _slope = (180.0/math.pi) * math.atan2((_p2y - _p1y),
                                                      (_p2x - _p1x)) + 90.0
                _pcl = ACLine(_lp, _slope)
        elif isinstance(_obj, (Circle, Arc, CCircle)):
            _cp = _obj.getCenter()
            _pcl = CLine(_cp, _lp)
        elif isinstance(_obj, HCLine):
            _pcl = VCLine(_lp)
        elif isinstance(_obj, VCLine):
            _pcl = HCLine(_lp)
        elif isinstance(_obj, ACLine):
            _angle = _obj.getAngle()
            if abs(_angle) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            else:
                _slope = _angle + 90.0
                _pcl = ACLine(_lp, _slope)
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            if abs(_p1x - _p2x) < 1e-10: # vertical
                _pcl = HCLine(_lp)
            elif abs(_p1y - _p2y) < 1e-10: # horizontal
                _pcl = VCLine(_lp)
            else:
                _slope = (180.0/math.pi) * math.atan2((_p2y - _p1y),
                                                      (_p2x - _p1x)) + 90.0
                _pcl = ACLine(_lp, _slope)
        else:
            pass
        _image.startAction()
        try:
            if _lp.getParent() is None:
                _active_layer.addObject(_lp)
            if _pcl is not None:
                _active_layer.addObject(_pcl)
        finally:
            _image.endAction()
    return True

#
# Entry callBacks
#

#
# Suport functions
#


