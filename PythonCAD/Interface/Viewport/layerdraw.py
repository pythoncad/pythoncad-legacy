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


#----------------------------------------------------------------------------------------------------
def _draw_layer(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _image = gimage.getImage()
    if _col is None:
        if self.isVisible() and _image.getActiveLayer() is not self:
            _col = _image.getOption('INACTIVE_LAYER_COLOR')
        else:
            _col = _image.getOption('BACKGROUND_COLOR')
    for _obj in self.getLayerEntities('point'):
        if _obj.isVisible():
            _obj.draw(gimage, _col)
    _ctypes = ['hcline', 'vcline', 'acline', 'cline', 'ccircle']
    for _ctype in _ctypes:
        for _obj in self.getLayerEntities(_ctype):
            if _obj.isVisible():
                _obj.draw(gimage, _col)
    _gtypes = ['segment', 'circle', 'arc', 'leader', 'polyline',
               'chamfer', 'fillet', 'textblock', 'linear_dimension',
               'horizontal_dimension', 'vertical_dimension',
               'radial_dimension', 'angular_dimension']
    for _gtype in _gtypes:
        for _obj in self.getLayerEntities(_gtype):
            if _obj.isVisible():
                _obj.draw(gimage, _col)
                
#----------------------------------------------------------------------------------------------------        
def _erase_layer(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    for _pt in self.getLayerEntities('point'):
        _pt.erase(gimage)
    
