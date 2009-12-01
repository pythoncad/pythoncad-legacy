#
# Copyright (c) 2005, 2006 Art Haas
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
# code for adding graphical methods to drawing entities
#

import types
from math import pi
_dtr = (pi/180.0)

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import conobject
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import layer

from PythonCAD.Interface.Gtk import gtkimage


class ViewportDraw(object):
#----------------------------------------------------------------------------------------------------
    def __init__(self):
        self.init_draw_methods()

#----------------------------------------------------------------------------------------------------
    def init_draw_methods(self):
        """
        Add draw methods to the entity classes
        """
        _class = point.Point
        _class.draw = types.MethodType(_draw_point, None, _class)
        _class.erase = types.MethodType(_erase_point, None, _class)
        _class = segment.Segment
        _class.draw = types.MethodType(_draw_segment, None, _class)
        _class.erase = types.MethodType(_erase_segment, None, _class)
        _class = circle.Circle
        _class.draw = types.MethodType(_draw_circle, None, _class)
        _class.erase = types.MethodType(_erase_circle, None, _class)
        _class = arc.Arc
        _class.draw = types.MethodType(_draw_arc, None, _class)
        _class.erase = types.MethodType(_erase_arc, None, _class)
        _class = leader.Leader
        _class.draw = types.MethodType(_draw_leader, None, _class)
        _class.erase = types.MethodType(_erase_leader, None, _class)
        _class = polyline.Polyline
        _class.draw = types.MethodType(_draw_polyline, None, _class)
        _class.erase = types.MethodType(_erase_polyline, None, _class)
        _class = segjoint.Chamfer
        _class.draw = types.MethodType(_draw_chamfer, None, _class)
        _class.erase = types.MethodType(_erase_chamfer, None, _class)
        _class = segjoint.Fillet
        _class.draw = types.MethodType(_draw_fillet, None, _class)
        _class.erase = types.MethodType(_erase_fillet, None, _class)
        _class = hcline.HCLine
        _class.draw = types.MethodType(_draw_hcline, None, _class)
        _class.erase = types.MethodType(_erase_hcline, None, _class)
        _class = vcline.VCLine
        _class.draw = types.MethodType(_draw_vcline, None, _class)
        _class.erase = types.MethodType(_erase_vcline, None, _class)
        _class = acline.ACLine
        _class.draw = types.MethodType(_draw_acline, None, _class)
        _class.erase = types.MethodType(_erase_acline, None, _class)
        _class = cline.CLine
        _class.draw = types.MethodType(_draw_cline, None, _class)
        _class.erase = types.MethodType(_erase_cline, None, _class)
        _class = ccircle.CCircle
        _class.draw = types.MethodType(_draw_ccircle, None, _class)
        _class.erase = types.MethodType(_erase_ccircle, None, _class)
        _class = text.TextBlock
        _class._formatLayout = types.MethodType(_format_layout, None, _class)
        _class.draw = types.MethodType(_draw_textblock, None, _class)
        _class.erase = types.MethodType(_erase_textblock, None, _class)
        _class = dimension.LinearDimension
        _class.draw = types.MethodType(_draw_ldim, None, _class)
        _class = dimension.RadialDimension
        _class.draw = types.MethodType(_draw_rdim, None, _class)
        _class = dimension.AngularDimension
        _class.draw = types.MethodType(_draw_adim, None, _class)
        _class = dimension.Dimension
        _class.erase = types.MethodType(_erase_dim, None, _class)
        _class._drawDimStrings = types.MethodType(_draw_dimstrings, None, _class)
        _class = layer.Layer
        _class.draw = types.MethodType(_draw_layer, None, _class)
        _class.erase = types.MethodType(_erase_layer, None, _class)
    
    
