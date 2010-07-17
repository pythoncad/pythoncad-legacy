#
# Copyright (c) 2003, 2004, 2005, 2006 Art Haas
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
# mirror operations
#

import math

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle

def _test_point(layer, x, y):
    _pts = layer.find('point', x, y)
    if len(_pts) == 0:
        _p = Point(x, y)
        layer.addObject(_p)
    else:
        _p = _pts.pop()
        _max = _p.countUsers()
        for _pt in _pts:
            _count = _pt.countUsers()
            if _count > _max:
                _max = _count
                _p = _pt
    return _p

def _horizontal_mirror(hy, objlist):
    for _obj in objlist:
        _layer = _obj.getParent()
        if _layer is None:
            continue
        _mobj = None
        if isinstance(_obj, Point):
            _x, _y = _obj.getCoords()
            _ym = _y + (2.0 * (hy - _y))
            _mp = _test_point(_layer, _x, _ym)
        elif isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()            
            if ((abs(hy - _p1y) > 1e-10) or
                (abs(hy - _p2y) > 1e-10)):
                _y1m = _p1y + (2.0 * (hy - _p1y))
                _mp1 = _test_point(_layer, _p1x, _y1m)
                _y2m = _p2y + (2.0 * (hy - _p2y))
                _mp2 = _test_point(_layer, _p2x, _y2m)
                _mobj = _obj.clone()
                _mobj.setP1(_mp1)
                _mobj.setP2(_mp2)
        elif isinstance(_obj, Arc):
            _x, _y = _obj.getCenter().getCoords()
            _ym = _y + (2.0 * (hy - _y))
            _mp = _test_point(_layer, _x, _ym)
            _mobj = _obj.clone()
            _mobj.setCenter(_mp)
            _mobj.setStartAngle(360.0 - _obj.getEndAngle())
            _mobj.setEndAngle(360.0 - _obj.getStartAngle())
        elif isinstance(_obj, (Circle, CCircle)):
            _x, _y = _obj.getCenter().getCoords()
            if abs(hy - _y) > 1e-10:
                _ym = _y + (2.0 * (hy - _y))
                _mp = _test_point(_layer, _x, _ym)
                _mobj = _obj.clone()
                _mobj.setCenter(_mp)
        elif isinstance(_obj, HCLine):
            _x, _y = _obj.getLocation().getCoords()
            if abs(hy - _y) > 1e-10:
                _ym = _y + (2.0 * (hy - _y))
                _mp = _test_point(_layer, _x, _ym)
                _mobj = _obj.clone()
                _mobj.setLocation(_mp)
        elif isinstance(_obj, VCLine):
            pass
        elif isinstance(_obj, ACLine):
            _angle = _obj.getAngle()
            if abs(abs(_angle) - 90.0) > 1e-10: # not vertical
                _x, _y = _obj.getLocation().getCoords()
                _ym = _y + (2.0 * (hy - _y))
                _mp = _test_point(_layer, _x, _ym)
                _mobj = _obj.clone()
                if abs(_angle) > 1e-10: # not horizontal
                    _mobj.setAngle(-1.0 * _angle)
                _mobj.setLocation(_mp)
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _x1, _y1 = _p1.getCoords()
            _x2, _y2 = _p2.getCoords()
            if abs(_x2 - _x1) > 1e-10: # not vertical
                _ym = _y1 + (2.0 * (hy - _y1))
                _mp1 = _test_point(_layer, _x1, _ym)
                _ym = _y2 + (2.0 * (hy - _y2))
                _mp2 = _test_point(_layer, _x2, _ym)
                _mobj = CLine(_mp1, _mp2)
        elif isinstance(_obj, Leader):
            _p1, _p2, _p3 = _obj.getPoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            _p3x, _p3y = _p3.getCoords()
            if (abs(_p1y - hy) > 1e-10 or
                abs(_p2y - hy) > 1e-10 or
                abs(_p3y - hy) > 1e-10):
                _ym = _p1y + (2.0 * (hy - _p1y))
                _mp1 = _test_point(_layer, _p1x, _ym)
                _ym = _p2y + (2.0 * (hy - _p2y))
                _mp2 = _test_point(_layer, _p2x, _ym)
                _ym = _p3y + (2.0 * (hy - _p3y))
                _mp3 = _test_point(_layer, _p3x, _ym)
                _mobj = _obj.clone()
                _mobj.setP1(_mp1)
                _mobj.setP2(_mp2)
                _mobj.setP3(_mp3)
        elif isinstance(_obj, Polyline):
            _mobj = _obj.clone()
            for _i in range(len(_mobj)):
                _pt = _mobj.getPoint(_i)
                _x, _y = _pt.getCoords()
                _ym = _y + (2.0 * (hy - _y))
                _mp = _test_point(_layer, _x, _ym)
                _mobj.setPoint(_i, _mp)
        else:
            print "skipping obj: " + `_obj`
        if _mobj is not None:
            _layer.addObject(_mobj)

def _vertical_mirror(vx, objlist):
    for _obj in objlist:
        _layer = _obj.getParent()
        if _layer is None:
            continue
        _mobj = None
        if isinstance(_obj, Point):
            _x, _y = _obj.getCoords()
            _xm = _x + (2.0 * (vx - _x))
            _mp = _test_point(_layer, _xm, _y)
        elif isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()            
            if ((abs(vx - _p1x) > 1e-10) or
                (abs(vx - _p2x) > 1e-10)):
                _x1m = _p1x + (2.0 * (vx - _p1x))
                _mp1 = _test_point(_layer, _x1m, _p1y)
                _x2m = _p2x + (2.0 * (vx - _p2x))
                _mp2 = _test_point(_layer, _x2m, _p2y)
                _mobj = _obj.clone()
                _mobj.setP1(_mp1)
                _mobj.setP2(_mp2)
        elif isinstance(_obj, Arc):
            _x, _y = _obj.getCenter().getCoords()
            _xm = _x + (2.0 * (vx - _x))
            _mp = _test_point(_layer, _xm, _y)
            _mobj = _obj.clone()
            _mobj.setCenter(_mp)
            _mobj.setStartAngle(180.0 - _obj.getEndAngle())
            _mobj.setEndAngle(180.0 - _obj.getStartAngle())
        elif isinstance(_obj, (Circle, CCircle)):
            _x, _y = _obj.getCenter().getCoords()
            if abs(vx - _x) > 1e-10:
                _xm = _x + (2.0 * (vx - _x))
                _mp = _test_point(_layer, _xm, _y)
                _mobj = _obj.clone()
                _mobj.setCenter(_mp)
        elif isinstance(_obj, HCLine):
            pass
        elif isinstance(_obj, VCLine):
            _x, _y = _obj.getLocation().getCoords()
            if abs(vx - _x) > 1e-10:
                _xm = _x + (2.0 * (vx - _x))
                _mp = _test_point(_layer, _xm, _y)
                _mobj = _obj.clone()
                _mobj.setLocation(_mp)
        elif isinstance(_obj, ACLine):
            _angle = _obj.getAngle()
            if abs(_angle) > 1e-10: # not horizontal
                _x, _y = _obj.getLocation().getCoords()
                _xm = _x + (2.0 * (vx - _x))
                _mp = _test_point(_layer, _xm, _y)
                _mobj = _obj.clone()
                if abs(abs(_angle) - 90.0) > 1e-10: # not vertical
                    _mobj.setAngle(-1.0 * _angle)
                _mobj.setLocation(_mp)
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _x1, _y1 = _p1.getCoords()
            _x2, _y2 = _p2.getCoords()
            if abs(_y2 - _y1) > 1e-10: # not horizontal
                _xm = _x1 + (2.0 * (vx - _x1))
                _mp1 = _test_point(_layer, _xm, _y1)
                _xm = _x2 + (2.0 * (vx - _x2))
                _mp2 = _test_point(_layer, _xm, _y2)
                _mobj = CLine(_mp1, _mp2)
        elif isinstance(_obj, Leader):
            _p1, _p2, _p3 = _obj.getPoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            _p3x, _p3y = _p3.getCoords()
            if (abs(_p1x - vx) > 1e-10 or
                abs(_p2x - vx) > 1e-10 or
                abs(_p3x - vx) > 1e-10):
                _xm = _p1x + (2.0 * (vx - _p1x))
                _mp1 = _test_point(_layer, _xm, _p1y)
                _xm = _p2x + (2.0 * (vx - _p2x))
                _mp2 = _test_point(_layer, _xm, _p2y)
                _xm = _p3x + (2.0 * (vx - _p3x))
                _mp3 = _test_point(_layer, _xm, _p3y)
                _mobj = _obj.clone()
                _mobj.setP1(_mp1)
                _mobj.setP2(_mp2)
                _mobj.setP3(_mp3)
        elif isinstance(_obj, Polyline):
            _mobj = _obj.clone()
            for _i in range(len(_mobj)):
                _pt = _mobj.getPoint(_i)
                _x, _y = _pt.getCoords()
                _xm = _x + (2.0 * (vx - _x))
                _mp = _test_point(_layer, _xm, _y)
                _mobj.setPoint(_i, _mp)
        else:
            print "skipping obj: " + `_obj`
        if _mobj is not None:
            _layer.addObject(_mobj)

def _reflect_point(t1, t2, t3, yint, x, y):
    #
    # reflect point in coordinate frame with
    # origin at mirror line y-intersection, then
    # convert reflected point back to global
    # coordinates
    #
    _nx = (t1 * x) + (t3 * (y - yint))
    _ny = (t3 * x) + (t2 * (y - yint)) + yint
    return _nx, _ny

def _angled_mirror(slope, yint, objlist):
    _angle = math.atan(slope)
    #
    # linear algebra reflection matrix coefficients
    #
    if abs(abs(_angle) - 45.0) < 1e-10:
        _t1 = 0.0
        _t2 = 0.0
        _t3 = 1.0
    else:
        _cosine = math.cos(_angle)
        _sine = math.sin(_angle)
        _t1 = (2.0 * _cosine * _cosine) - 1.0
        _t2 = (2.0 * _sine * _sine) - 1.0
        _t3 = 2.0 * _cosine * _sine
    for _obj in objlist:
        _layer = _obj.getParent()
        if _layer is None:
            continue
        _mobj = None
        if isinstance(_obj, Point):
            _x, _y = _obj.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _np = _test_point(_layer, _rx, _ry)
        elif isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _x, _y = _p1.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp1 = _test_point(_layer, _rx, _ry)
            _x, _y = _p2.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp2 = _test_point(_layer, _rx, _ry)
            _mobj = _obj.clone()
            _mobj.setP1(_mp1)
            _mobj.setP2(_mp2)
        elif isinstance(_obj, Arc):
            _x, _y = _obj.getCenter().getCoords()
            _rcx, _rcy = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp = _test_point(_layer, _rcx, _rcy)
            _ep1, _ep2 = _obj.getEndpoints()
            _x, _y = _ep1
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _rtd = 180.0/math.pi
            _ea = _rtd * math.atan2((_ry - _rcy), (_rx - _rcx))
            if _ea < 0.0:
                _ea = _ea + 360.0
            _x, _y = _ep2
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _sa = _rtd * math.atan2((_ry - _rcy), (_rx - _rcx))
            if _sa < 0.0:
                _sa = _sa + 360.0
            _mobj = _obj.clone()
            _mobj.setCenter(_mp)
            _mobj.setStartAngle(_sa)
            _mobj.setEndAngle(_ea)
        elif isinstance(_obj, (Circle, CCircle)):
            _x, _y = _obj.getCenter().getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp = _test_point(_layer, _rx, _ry)
            _mobj = _obj.clone()
            _mobj.setCenter(_mp)
        elif isinstance(_obj, HCLine):
            _x, _y = _obj.getLocation().getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp = _test_point(_layer, _rx, _ry)
            if abs(abs(_angle) - 45.0) < 1e-10:
                _mobj = VCLine(_mp)
            else:
                _xi = (_y - yint)/slope
                _mang = 180.0/math.pi * math.atan2((_ry - _y), (_rx - _xi))
                if _mang < 0.0:
                    _mang = _mang + 360.0
                _mobj = ACLine(_mp, _mang)
        elif isinstance(_obj, VCLine):
            _x, _y = _obj.getLocation().getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp = _test_point(_layer, _rx, _ry)
            if abs(abs(_angle) - 45.0) < 1e-10:
                _mobj = HCLine(_mp)
            else:
                _yi = (slope * _x) + yint 
                _mang = 180.0/math.pi * math.atan2((_ry - _yi), (_rx - _x))
                if _mang < 0.0:
                    _mang = _mang + 360.0
                _mobj = ACLine(_mp, _mang)
        elif isinstance(_obj, ACLine):
            _at45 = False
            if abs(abs(_angle) - 45.0) < 1e-10:
                _at45 = True
            _x, _y = _obj.getLocation().getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp = _test_point(_layer, _rx, _ry)
            _acl_angle = _obj.getAngle()
            if _at45 and abs(_acl_angle) < 1e-10:
                _mobj = VCLine(_mp)
            elif _at45 and abs(abs(_acl_angle) - 90.0) < 1e-10:
                _mobj = HCLine(_mp)
            else:
                if abs(_acl_angle) < 1e-10: # horizontal
                    _xi = (_y - yint)/slope
                    _yi = _y
                elif abs(abs(_acl_angle) - 90.0) < 1e-10: # vertical
                    _xi = _x
                    _yi = (slope * _x) + yint
                else:
                    _asl = math.tan((math.pi/180.0) * _acl_angle)
                    if abs(_asl - slope) < 1e-10: # parallel
                        _mang = _acl_angle
                    else:
                        _ayi = _y - (_asl * _x)                        
                        _xi = (_ayi - yint)/(slope - _asl)
                        _yi = (slope * _xi) + yint
                        _mang = 180.0/math.pi * math.atan2((_ry - _yi), (_rx - _xi))
                        if _mang < 0.0:
                            _mang = _mang + 360.0
                _mobj = ACLine(_mp, _mang)
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _x, _y = _p1.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp1 = _test_point(_layer, _rx, _ry)
            _x, _y = _p2.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp2 = _test_point(_layer, _rx, _ry)
            _mobj = CLine(_mp1, _mp2)
        elif isinstance(_obj, Leader):
            _p1, _p2, _p3 = _obj.getPoints()
            _x, _y = _p1.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp1 = _test_point(_layer, _rx, _ry)
            _x, _y = _p2.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp2 = _test_point(_layer, _rx, _ry)
            _x, _y = _p3.getCoords()
            _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
            _mp3 = _test_point(_layer, _rx, _ry)
            _mobj = _obj.clone()
            _mobj.setP1(_mp1)
            _mobj.setP2(_mp2)
            _mobj.setP3(_mp3)
        elif isinstance(_obj, Polyline):
            _mpts = []
            for _i in range(len(_obj)):
                _x, _y = _obj.getPoint(_i).getCoords()
                _rx, _ry = _reflect_point(_t1, _t2, _t3, yint, _x, _y)
                _mp = _test_point(_layer, _rx, _ry)
                _mpts.append(_mp)
            _s = _obj.getStyle()
            _mobj = Polyline(_mpts, _s)
            _l = _obj.getLinetype()
            if _l != _s.getLinetype():
                _mobj.setLinetype(_l)
            _c = _obj.getColor()
            if _c != _s.getColor():
                _mobj.setColor(_c)
            _t = _obj.getThickness()
            if abs(_t - _s.getThickness()) > 1e-10:
                _mobj.setThickness(_t)
        else:
            print "Skipping object: " + `_obj`
        if _mobj is not None:
            _layer.addObject(_mobj)

def mirror_objects(mline, objlist):
    if not isinstance(mline, (HCLine, VCLine, ACLine, CLine)):
        raise TypeError, "Invalid mirror line type: " + `type(mline)`
    if not isinstance(objlist, (list, tuple)):
        raise TypeError, "Invalid object list: " + `type(objlist)`
    if isinstance(mline, HCLine):
        _x, _y = mline.getLocation().getCoords()
        _horizontal_mirror(_y, objlist)
    elif isinstance(mline, VCLine):
        _x, _y = mline.getLocation().getCoords()
        _vertical_mirror(_x, objlist)
    elif isinstance(mline, ACLine):
        _x, _y = mline.getLocation().getCoords()
        _angle = mline.getAngle()
        if abs(_angle) < 1e-10: # horizontal:
            _horizontal_mirror(_y, objlist)
        elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
            _vertical_mirror(_x, objlist)
        else:
            _slope = math.tan(_angle * (math.pi/180.0))
            _yint = _y - (_slope * _x)
            _angled_mirror(_slope, _yint, objlist)
    elif isinstance(mline, CLine):
        _p1, _p2 = mline.getKeypoints()
        _p1x, _p1y = _p1.getCoords()
        _p2x, _p2y = _p2.getCoords()
        if abs(_p2y - _p1y) < 1e-10: # horizontal
            _horizontal_mirror(_p1y, objlist)
        elif abs(_p2x - _p1x) < 1e-10: # vertical
            _vertical_mirror(_p1x, objlist)
        else:
            _slope = (_p2y - _p1y)/(_p2x - _p1x)
            _yint = _p1y - (_slope * _p1x)
            _angled_mirror(_slope, _yint, objlist)
    else:
        raise TypeError, "Unexpected mirror line type: " + `type(mline)`
