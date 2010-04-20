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
# <chamfers> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segjoint import Chamfer
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def chamfer_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the points where you want a chamfer.'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", chamfer_button_press_cb)
#
# Motion Notifie
#

#
# Button press callBacks
#
def chamfer_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint().getCoords()
    _pt, _new_pt = _image.findPoint(_x, _y, _tol)
    if _pt is not None and not _new_pt:
        _active_layer = _image.getActiveLayer()
        _users = _pt.getUsers()
        if len(_users) != 2:
            return
        _s1 = _s2 = None        
        for _user in _users:
            if not isinstance(_user, Segment):
                return
            if _s1 is None:
                _s1 = _user
            else:
                _s2 = _user
        _len = _image.getOption('CHAMFER_LENGTH')
        _s = _image.getOption('LINE_STYLE')
        _l = _image.getOption('LINE_TYPE')
        _c = _image.getOption('LINE_COLOR')
        _t = _image.getOption('LINE_THICKNESS')
        #
        # the following is a work-around that needs to
        # eventually be replaced ...
        #
        _p1, _p2 = _s1.getEndpoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _slen = _s1.length()
        _factor = 2.0
        _r = (_slen - (_len/_factor))/_slen
        _xn = _x1 + _r * (_x2 - _x1)
        _yn = _y1 + _r * (_y2 - _y1)
        _pts = _active_layer.find('point', _xn, _yn)
        while len(_pts) > 0:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = (_slen - (_len/_factor))/_slen
            _xn = _x1 + _r * (_x2 - _x1)
            _yn = _y1 + _r * (_y2 - _y1)
            _pts = _active_layer.find('point', _xn, _yn)
        if len(_pts) == 0:
            _image.startAction()
            try:
                _pc = Point(_xn, _yn)
                _active_layer.addObject(_pc)
                if _pt is _p1:
                    _s1.setP1(_pc)
                elif _pt is _p2:
                    _s1.setP2(_pc)
                else:
                    raise ValueError, "Unexpected endpoint: " + str(_pc)
                _ptx, _pty = _pt.getCoords()
                _pc.setCoords(_ptx, _pty)
                _chamfer = Chamfer(_s1, _s2, _len, _s)
                if _l != _s.getLinetype():
                    _chamfer.setLinetype(_l)
                if _c != _s.getColor():
                    _chamfer.setColor(_c)
                if abs(_t - _s.getThickness()) > 1e-10:
                    _chamfer.setThickness(_t)
                _active_layer.addObject(_chamfer)
            finally:
                _image.endAction()
                gtkimage.redraw()
    return True
#
# Entry callBacks
#

#
# Suport functions
#