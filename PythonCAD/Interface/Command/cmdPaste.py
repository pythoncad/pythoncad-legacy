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
# handle  paste, selections, etc
#

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.dimension import LinearDimension
from PythonCAD.Generic.dimension import HorizontalDimension
from PythonCAD.Generic.dimension import VerticalDimension
from PythonCAD.Generic.dimension import RadialDimension
from PythonCAD.Generic.dimension import AngularDimension
from PythonCAD.Generic.dimension import DimString
from PythonCAD.Generic import text
import PythonCAD.Generic.globals



def paste_button_press_cb(gtkimage, widget, event, tool):
    # print "called paste_button_press_cb()"
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    # print "x: %g; y: %g" % (_x, _y)
    _active_layer = _image.getActiveLayer()
    _objs = PythonCAD.Generic.globals.selectobj.getObjects()
    _objmap = {}
    _image.startAction()
    try:
        _midx, _midy = determine_center(_objs)
        _dx, _dy = _x - _midx, _y - _midy
        for _obj in _objs:
            if isinstance(_obj, Point):
                if not _objmap.has_key('point'):
                    _objmap['point'] = {}
                _pt = Point(_obj.getx() + _dx, _obj.gety() + _dy)
                _ept = _active_layer.findObject(_pt)
                if _ept is None:
                    _active_layer.addObject(_pt)
                    _objmap['point'][_obj] = _pt
                else:
                    _objmap['point'][_obj] = _ept
            elif isinstance(_obj, Segment):
                if not _objmap.has_key('segment'):
                    _objmap['segment'] = {}
                _cseg = _obj.clone()
                _cseg.move(_dx, _dy)
                _eseg = _active_layer.findObject(_cseg)
                if _eseg is None:
                    _p1, _p2 = _cseg.getEndpoints()
                    _ep = _active_layer.findObject(_p1)
                    if _ep is None:
                        _active_layer.addObject(_p1)
                    else:
                        _cseg.setP1(_ep)
                    _ep = _active_layer.findObject(_p2)
                    if _ep is None:
                        _active_layer.addObject(_p2)
                    else:
                        _cseg.setP2(_ep)
                    _active_layer.addObject(_cseg)
                else:
                    _objmap['segment'][_obj] = _eseg
            elif isinstance(_obj, (Circle, Arc, CCircle)):
                _cc = _obj.clone()
                _cc.move(_dx, _dy)
                _ec = _active_layer.findObject(_cc)
                if _ec is None:
                    _cp = _cc.getCenter()
                    _ep = _active_layer.findObject(_cp)
                    if _ep is None:
                        _active_layer.addObject(_cp)
                    else:
                        _cc.setLocation(_ep)
                    _active_layer.addObject(_cc)
            elif isinstance(_obj, (HCLine, VCLine, ACLine)):
                _ccl = _obj.clone()
                _ccl.move(_dx, _dy)
                _ecl = _active_layer.findObject(_ccl)
                if _ecl is None:
                    _lp = _ccl.getLocation()
                    _ep = _active_layer.findObject(_lp)
                    if _ep is None:
                        _active_layer.addObject(_lp)
                    else:
                        _ccl.setLocation(_ep)
                    _active_layer.addObject(_ccl)
            elif isinstance(_obj, CLine):
                _ccl = _obj.clone()
                _ccl.move(_dx, _dy)
                _ecl = _active_layer.findObject(_ccl)
                if _ecl is None:
                    _p1, _p2 = _ccl.getKeypoints()
                    _ep = _active_layer.findObject(_p1)
                    if _ep is None:
                        _active_layer.addObject(_p1)
                    else:
                        _ccl.setP1(_ep)
                    _ep = _active_layer.findObject(_p2)
                    if _ep is None:
                        _active_layer.addObject(_p2)
                    else:
                        _ccl.setP2(_ep)
                    _active_layer.addObject(_ccl)
            elif isinstance(_obj, LinearDimension):
                #these checks were wrongly placed and seem unecessary...
                #keep them here just in case...
                #if _active_layer.findObject(_obj) is None:
                #_l1, _l2 = _obj.getDimLayers()
                #if _image.hasLayer(_l1) and _image.hasLayer(_l2):
                _p1, _p2 = _obj.getDimPoints()
                dimpoint1 = Point(_p1.getx() + _dx, _p1.gety() + _dy)
                dimpoint2 = Point(_p2.getx() + _dx, _p2.gety() + _dy)
                dimx, dimy = _obj.getLocation()
                
                #check if points already exist in drawing
                _ep = _active_layer.findObject(dimpoint1)
                if _ep is None:
                    _active_layer.addObject(dimpoint1)
                else:
                    dimpoint1 = _ep
                _ep = _active_layer.findObject(dimpoint2)
                if _ep is None:
                    _active_layer.addObject(dimpoint2)
                else:
                    dimpoint2 = _ep
                    
                _ds = _obj.getDimStyle()
                if isinstance(_obj, HorizontalDimension):
                    _dtype = HorizontalDimension
                elif isinstance(_obj, VerticalDimension):
                    _dtype = VerticalDimension
                else:
                    _dtype = LinearDimension
                _dim = _dtype(dimpoint1, dimpoint2, dimx + _dx, dimy + _dy,_ds)
                _active_layer.addObject(_dim)
            elif isinstance(_obj, RadialDimension):
                if _active_layer.findObject(_obj) is None:
                    _lyr = _obj.getDimLayer()
                    if _image.hasLayer(_lyr):
                        _dc = _obj.getDimCircle()
                        _ds = _obj.getDimStyle()
                        _dim = RadialDimension(_lyr, _dc, _x, _y, _ds)
                        _active_layer.addObject(_dim)
            elif isinstance(_obj, AngularDimension):
                if _active_layer.findObject(_obj) is None:
                    _cl, _l1, _l2 = _obj.getDimLayers()
                    if (_image.hasLayer(_cl) and
                        _image.hasLayer(_l1) and
                        _image.hasLayer(_l2)):
                        _cp, _p1, _p2 = _obj.getDimPoints()
                        _ds = _obj.getDimStyle()
                        _dim = AngularDimension(_cl, _cp, _l1, _p1, _l2, _p2, _x, _y, _ds)
                        _active_layer.addObject(_dim)
            elif isinstance(_obj, text.TextBlock):
                _ntb = _obj.clone()
                _origpos = _obj.getLocation()
                _ntb.setLocation(_origpos[0] + _dx, _origpos[1] + _dy)
                _active_layer.addObject(_ntb)
            else:
                print "Unexpected type for pasting: " + `type(_obj)`
    finally:
        _image.endAction()
    
def paste_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click where you want to paste the objects'))
    _tool = gtkimage.getImage().getTool()
    _tool.initialize()
    _tool.setHandler("button_press", paste_button_press_cb)

def determine_center(_objectarray):
    #determine "center" of n points - simplest method: average values of
    #coordinates of center points of each object
    _sumx, _sumy, _objectnumber = 0, 0, 0
    for _obj in _objectarray:
        _objectnumber += 1
        if isinstance(_obj, Point):
            _sumx += _obj.getx()
            _sumy += _obj.gety()
        elif isinstance(_obj, Segment):
            _x, _y = _obj.getMiddlePoint()
            _sumx += _x
            _sumy += _y
        elif isinstance(_obj, (Circle, Arc, CCircle)):
            _center = _obj.getCenter()
            _sumx += _center.getx()
            _sumy += _center.gety()
        elif isinstance(_obj, (HCLine, VCLine, ACLine)):
            _center = _obj.getLocation()
            _sumx += _center.getx()
            _sumy += _center.gety()
        elif isinstance(_obj, CLine):
            _midpoint = _obj.getMiddlePoint()
            _sumx += _midpoint.getx()
            _sumy += _midpoint.gety()
        elif isinstance(_obj, LinearDimension):
            #linear dimensions don't count since they are connected to another
            #object
            _objectnumber -= 1
        #elif isinstance(_obj, RadialDimension):
        #elif isinstance(_obj, AngularDimension):
        elif isinstance(_obj, text.TextBlock):
            _location = _obj.getLocation()
            _sumx += _location[0]
            _sumy += _location[1]
        elif isinstance(_obj, DimString):
            _objectnumber -= 1
        else:
            print "Unexpected type for center determination: " + `type(_obj)`
            _objectnumber -= 1
    return _sumx / _objectnumber, _sumy / _objectnumber
