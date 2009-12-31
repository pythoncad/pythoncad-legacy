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
# <Fillet> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.segjoint import  Fillet

#
# Init
#
def fillet_mode_init(gtkimage, tool=None):
    """
        Init function for the fillet comand
    """
    _image = gtkimage.getImage()
    if tool!= None and tool.rad!=None:
        _rad = tool.rad
    else:        
        _rad = _image.getOption('FILLET_RADIUS') 
        _tool = gtkimage.getImage().getTool()
    _msg  =  'Click on the points where you want a fillet( ) or enter the Radius.'
    _tool.initialize()
    _tool.rad=_rad 
    fillet_prompt_message(gtkimage,_tool,_msg)
    _tool.setHandler("initialize", fillet_mode_init)
    _tool.setHandler("button_press", fillet_button_press_cb)
    _tool.setHandler("entry_event", fillet_entry_event_cb)
#
# Motion Notifie
#

#
# Button press callBacks
#
def fillet_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
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
        if(tool.rad!=None):
            _rad = tool.rad
        else:        
            _rad = _image.getOption('FILLET_RADIUS')
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
        _r = 1.0 - (_slen/_factor)
        _xn = _x1 + _r * (_x2 - _x1)
        _yn = _y1 + _r * (_y2 - _y1)
        _pts = _active_layer.find('point', _xn, _yn)
        while len(_pts) > 0:
            _factor = _factor + 1.0
            if _factor > 1000:
                break
            _r = 1.0 - (_slen/_factor)
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
                _fillet = Fillet(_s1, _s2, _rad, _s)
                if _l != _s.getLinetype():
                    _fillet.setLinetype(_l)
                if _c != _s.getColor():
                    _fillet.setColor(_c)
                if abs(_t - _s.getThickness()) > 1e-10:
                    _fillet.setThickness(_t)
                _active_layer.addObject(_fillet)
            finally:
                _image.endAction()
                gtkimage.redraw()
    return True
#
# Entry callBacks
#
def fillet_entry_event_cb(gtkimage, widget, tool):
    """
        Manage the radius entered from the entry
    """
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text)>3:
        if _text.find(':') >0 :
            cmdArgs=_text.split(':')
            if len(cmdArgs)==2:
                _firstArgs=cmdArgs[0].strip().lower()
                if _firstArgs == 'r' :
                    setFilletRadius(gtkimage,tool,cmdArgs[1])
                    return
                elif _firstArgs == 'tm':
                    setTrimMode(gtkimage,tool,cmdArgs[1])
                    return
    if _text.find('?') >= 0:
        gtkDialog._help_dialog(gtkimage,"FilletTwoPoint")
        return
    gtkDialog._error_dialog(gtkimage,"Wrong command")

#
# Suport functions
#
def setFilletRadius(gtkimage,tool,radius):
    """
        set the fillet radius in to the tool
    """
    _r=radius.strip()
    rad=float(_r)
    tool.rad=rad
    fillet_prompt_message(gtkimage,tool)
    
def fillet_prompt_message(gtkimage,tool,startMessage=None):
    """
        set the fillet message
    """
    if startMessage == None:
        _oldMsg=gtkimage.getPrompt()    
    else:
        _oldMsg=startMessage
    if isinstance(tool,FilletTool):
        _msg =_oldMsg.split('(')[0] + '( r: ' + str(tool.rad) + ' )' + _oldMsg.split(')')[1]
    if isinstance(tool,FilletTwoLineTool):
        _msg=_oldMsg.split('(')[0] + '( r: ' + str(tool.rad) + ' tm: ' + str(tool.TrimMode) + ' )' + _oldMsg.split(')')[1]
    gtkimage.setPrompt(_msg)

def setTrimMode(gtkimage,tool,mode):
    """
        set the trim fillet mode 
    """
    _mode=mode.strip().lower()
    if _mode=='f' : 
        tool.TrimMode="f"
    elif _mode=='s' :
        tool.TrimMode="s"
    elif _mode=='b' :
        tool.TrimMode="b"        
    elif _mode=='n' :
        tool.TrimMode="n"
    else:
        gtkDialog._error_dialog(gtkimage,"Wrong command")
        return
    fillet_prompt_message(gtkimage,tool)