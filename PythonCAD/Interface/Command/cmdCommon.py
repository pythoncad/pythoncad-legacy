#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
#
#               2009 Matteo Boscolo
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
# Usefoul functions for commands
#

from math import hypot, pi, atan2

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import math

import sys

from PythonCAD.Generic import globals
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import color
from PythonCAD.Generic import util
from PythonCAD.Generic import units
from PythonCAD.Interface.Gtk import gtkDialog
from PythonCAD.Generic import tools   
from PythonCAD.Generic import snap

def make_tuple(text, gdict):
    _tpl = eval(text, gdict)
    if not isinstance(_tpl, tuple):
        raise TypeError, "Invalid tuple: " + `type(_tpl)`
    if len(_tpl) != 2:
        raise ValueError, "Invalid tuple: " + str(_tpl)
    return _tpl

def create_entity(gtkimage, tool=None):
    _tool = gtkimage.getImage().getTool()
    _init_func = _tool.getHandler("initialize")
    _image = gtkimage.getImage()
    _image.startAction()
    try:
        _tool.create(_image)
    finally:
        _image.endAction()
    _init_func(gtkimage)

