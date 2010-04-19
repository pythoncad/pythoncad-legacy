#
# Copyright (c) 2002, 2003, 2006 Art Haas
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
# code to calculate if or where two objects intersect
#

# from __future__ import division

import math

from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle

#
# common constants
#

_dtr = math.pi/180.0
_rtd = 180.0/math.pi

_zero = 0.0 - 1e-10
_one = 1.0 + 1e-10

#
# the following functions are used to calculate the
# intersection of two line segments
#
# see comp.graphics.algorithms FAQ for details
#

def denom(p1, p2, p3, p4):
    if not isinstance(p1, point.Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p1)`
    if not isinstance(p2, point.Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p2)`
    if not isinstance(p3, point.Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p3)`
    if not isinstance(p4, point.Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p4)`
    _p1x, _p1y = p1.getCoords()
    _p2x, _p2y = p2.getCoords()
    _p3x, _p3y = p3.getCoords()
    _p4x, _p4y = p4.getCoords()
    return ((_p2x - _p1x)*(_p4y - _p3y)) - ((_p2y - _p1y)*(_p4x - _p3x))

def rnum(p1, p2, p3, p4):
    if not isinstance(p1, point.Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p1)`
    if not isinstance(p2, point.Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p2)`
    if not isinstance(p3, point.Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p3)`
    if not isinstance(p4, point.Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p4)`
    _p1x, _p1y = p1.getCoords()
    _p2x, _p2y = p2.getCoords()
    _p3x, _p3y = p3.getCoords()
    _p4x, _p4y = p4.getCoords()
    return ((_p1y - _p3y)*(_p4x - _p3x)) - ((_p1x - _p3x)*(_p4y - _p3y))

def snum(p1, p2, p3, p4):
    if not isinstance(p1, point.Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p1)`
    if not isinstance(p2, point.Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p2)`
    if not isinstance(p3, point.Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p3)`
    if not isinstance(p4, point.Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p4)`
    _p1x, _p1y = p1.getCoords()
    _p2x, _p2y = p2.getCoords()
    _p3x, _p3y = p3.getCoords()
    _p4x, _p4y = p4.getCoords()
    return ((_p1y - _p3y)*(_p2x - _p1x)) - ((_p1x - _p3x)*(_p2y - _p1y))

#
# the following function is used to calculate the intersection
# of a circle and a segment or a circle and an infite length line
#
# see Paul Bourke's web pages for details
#

def sc_intersection(x1, y1, x2, y2 ,_circ, skiptest=False):
    if not isinstance(x1, float):
        raise TypeError, "Invalid argument: " + `type(x1)`
    if not isinstance(y1, float):
        raise TypeError, "Invalid argument: " + `type(y1)`
    if not isinstance(x2, float):
        raise TypeError, "Invalid argument: " + `type(x2)`
    if not isinstance(y2, float):
        raise TypeError, "Invalid argument: " + `type(y2)`
    if not isinstance(_circ, (circle.Circle,
                              arc.Arc,
                              ccircle.CCircle)):
        raise TypeError, "Invalid circle for sc_intersection(): " + `type(_circ)`
    _plist = []
    _xdiff = x2 - x1
    _ydiff = y2 - y1
    _xc, _yc = _circ.getCenter().getCoords()
    _r = _circ.getRadius()
    _u = ((_xc - x1)*(_xdiff) + (_yc - y1)*(_ydiff))/(pow(_xdiff, 2) + pow(_ydiff, 2))
    _xp = x1 + (_u * _xdiff)
    _yp = y1 + (_u * _ydiff)
    _dist = math.hypot((_yp - _yc), (_xp - _xc))
    if abs(_dist - _r) < 1e-10:
        if skiptest or not (_u < _zero or _u > _one):
            _plist.append((_xp, _yp))
    else:
        if _dist < _r:
            _a = pow(_xdiff, 2) + pow(_ydiff, 2)
            _b = 2.0 * ((_xdiff * (x1 - _xc)) + (_ydiff * (y1 - _yc)))
            _c = (pow(_xc, 2) + pow(_yc, 2) + pow(x1, 2) + pow(y1, 2) -
                  2.0 * ((_xc*x1) + (_yc*y1)) - pow(_r,2))
            _det = pow(_b, 2) - (4.0 * _a * _c)
            if _det > 1e-10:
                _dsq = math.sqrt(_det)
                _u = (-_b - _dsq)/(2.0 * _a)
                if skiptest or not (_u < _zero or _u > _one):
                    _x = x1 + (_u * _xdiff)
                    _y = y1 + (_u * _ydiff)
                    _plist.append((_x, _y))
                _u = (-_b + _dsq)/(2.0 * _a)
                if skiptest or not (_u < _zero or _u > _one):
                    _x = x1 + (_u * _xdiff)
                    _y = y1 + (_u * _ydiff)
                    _plist.append((_x, _y))
    return _plist

#
# intersection functions
#

def _null_intfunc(ipts, obja, objb):
    print "invoked _null_intfunc()"
    print "obja: " + `obja`
    print "objb: " + `objb`

def _non_intersecting(ipts, obja, objb):
    pass

#
# segment - segment intersection
#

def _seg_seg_intersection(ipts, seg1, seg2):
    _p1, _p2 = seg1.getEndpoints()
    _p3, _p4 = seg2.getEndpoints()
    _xi = _yi = None
    if _p1 == _p3:
        _x, _y = _p4.getCoords()
        _proj = seg1.getProjection(_x, _y)
        if _proj is None:
            _xi, _yi = _p1.getCoords()
        else:
            _px, _py = _proj
            if math.hypot((_px - _x), (_py - _y)) > 1e-10:
                _xi, _yi = _p1.getCoords()
    elif _p1 == _p4:
        _x, _y = _p3.getCoords()
        _proj = seg1.getProjection(_x, _y)
        if _proj is None:
            _xi, _yi = _p1.getCoords()
        else:
            _px, _py = _proj
            if math.hypot((_px - _x), (_py - _y)) > 1e-10:
                _xi, _yi = _p1.getCoords()
    elif _p2 == _p3:
        _x, _y = _p4.getCoords()
        _proj = seg1.getProjection(_x, _y)
        if _proj is None:
            _xi, _yi = _p2.getCoords()
        else:
            _px, _py = _proj
            if math.hypot((_px - _x), (_py - _y)) > 1e-10:
                _xi, _yi = _p2.getCoords()
    elif _p2 == _p4:
        _x, _y = _p3.getCoords()
        _proj = seg1.getProjection(_x, _y)
        if _proj is None:
            _xi, _yi = _p2.getCoords()
        else:
            _px, _py = _proj
            if math.hypot((_px - _x), (_py - _y)) > 1e-10:
                _xi, _yi = _p2.getCoords()
    else:
        _d = denom(_p1, _p2, _p3, _p4)
        if abs(_d) > 1e-10: # NOT parallel
            _r = rnum(_p1, _p2, _p3, _p4)/_d
            _s = snum(_p1, _p2, _p3 ,_p4)/_d
            if (not (_r < _zero or _r > _one) and
                not (_s < _zero or _s > _one)):
                _p1x, _p1y = _p1.getCoords()
                _p2x, _p2y = _p2.getCoords()
                _xi = _p1x + _r * (_p2x - _p1x)
                _yi = _p1y + _r * (_p2y - _p1y)
    if _xi is not None and _yi is not None:
        ipts.append((_xi, _yi))

#
# segment - circle intersection
#

def _seg_circ_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _circ = objb
    else:
        _seg = objb
        _circ = obja
    assert not isinstance(_circ, arc.Arc), "Arc found!"
    _p1, _p2 = _seg.getEndpoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    for _ip in sc_intersection(_p1x, _p1y, _p2x, _p2y, _circ):
        ipts.append(_ip)

#
# segment - arc intersection
#

def _seg_arc_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _arc = objb
    else:
        _seg = objb
        _arc = obja
    _p1, _p2 = _seg.getEndpoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    _ax, _ay = _arc.getCenter().getCoords()
    for _ip in sc_intersection(_p1x, _p1y, _p2x, _p2y, _arc):
        _x, _y = _ip
        _angle = math.atan2((_y - _ay),(_x - _ax)) * _rtd
        if _angle < 0.0:
            _angle = _angle + 360.0
        if _arc.throughAngle(_angle):
            ipts.append(_ip)

#
# segment - horizontal construction line intersection
#

def _seg_hcl_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _hcl = objb
    else:
        _seg = objb
        _hcl = obja
    _p1, _p2 = _seg.getEndpoints()
    _hp = _hcl.getLocation()
    _hx, _hy = _hp.getCoords()
    _xi = _yi = None
    if _hp == _p1:
        _p2x, _p2y = _p2.getCoords()
        if abs(_hy - _p2y) > 1e-10:
            _xi, _yi = _p1.getCoords()
    elif _hp == _p2:
        _p1x, _p1y = _p1.getCoords()
        if abs(_hy - _p1y) > 1e-10:
            _xi, _yi = _p2.getCoords()
    else:
        _p1x, _p1y = _p1.getCoords()
        _p2x, _p2y = _p2.getCoords()
        _miny = min(_p1y, _p2y)
        _maxy = max(_p1y, _p2y)
        if abs(_p1y - _p2y) > 1e-10 and _miny < _hy < _maxy:
            _xi = _p1x + ((_hy - _p1y)*(_p2x - _p1x))/(_p2y - _p1y)
            _yi = _hy
    if _xi is not None and _yi is not None:
        ipts.append((_xi, _yi))

#
# segment - vertical construction line intersection
#

def _seg_vcl_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _vcl = objb
    else:
        _seg = objb
        _vcl = obja
    _p1, _p2 = _seg.getEndpoints()
    _vp = _vcl.getLocation()
    _vx, _vy = _vp.getCoords()
    _xi = _yi = None
    if _vp == _p1:
        _p2x, _p2y = _p2.getCoords()
        if abs(_vx - _p2x) > 1e-10:
            _xi, _yi = _p1.getCoords()
    elif _vp == _p2:
        _p1x, _p1y = _p1.getCoords()
        if abs(_vx - _p1x) > 1e-10:
            _xi, _yi = _p2.getCoords()
    else:
        _p1x, _p1y = _p1.getCoords()
        _p2x, _p2y = _p2.getCoords()
        _vx, _vy = _vp.getCoords()
        _minx = min(_p1x, _p2x)
        _maxx = max(_p1x, _p2x)
        if abs(_p1x - _p2x) > 1e-10 and _minx < _vx < _maxx:
            _xi = _vx
            _yi = _p1y + ((_p2y - _p1y)*(_vx - _p1x))/(_p2x - _p1x)
    if _xi is not None and _yi is not None:
        ipts.append((_xi, _yi))

#
# segment - angled construction line intersection
#

def _seg_acl_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _acl = objb
    else:
        _seg = objb
        _acl = obja
    _p1, _p2 = _seg.getEndpoints()
    _ap = _acl.getLocation()
    _xi = _yi = None
    if _p1 == _ap:
        _x, _y = _p2.getCoords()
        _px, _py = _acl.getProjection(_x, _y)
        if math.hypot((_px - _x), (_py - _y)) > 1e-10:
            _xi, _yi = _p1.getCoords()
    elif _p2 == _ap:
        _x, _y = _p1.getCoords()
        _px, _py = _acl.getProjection(_x, _y)
        if math.hypot((_px - _x), (_py - _y)) > 1e-10:
            _xi, _yi = _p2.getCoords()
    else:
        _ax, _ay = _ap.getCoords()
        _angle = _acl.getAngle() * _dtr
        _xt = _ax + math.cos(_angle)
        _yt = _ay + math.sin(_angle)
        _tp = point.Point(_xt, _yt)
        _d = denom(_p1, _p2, _ap, _tp)
        if abs(_d) > 1e-10: # NOT parallel
            _r = rnum(_p1, _p2, _ap, _tp)/_d
            if not (_r < _zero or _r > _one):
                _p1x, _p1y = _p1.getCoords()
                _p2x, _p2y = _p2.getCoords()
                _xi = _p1x + _r * (_p2x - _p1x)
                _yi = _p1y + _r * (_p2y - _p1y)
    if _xi is not None and _yi is not None:
        ipts.append((_xi, _yi))

#
# segment - 2-point construction line intersection
#

def _seg_cl_intersection(ipts, obja, objb):
    if isinstance(obja, segment.Segment):
        _seg = obja
        _cl = objb
    else:
        _seg = objb
        _cl = obja
    _p1, _p2 = _seg.getEndpoints()
    _p3, _p4 = _cl.getKeypoints()
    _xi = _yi = None
    if _p1 == _p3 or _p1 == _p4:
        _x, _y = _p2.getCoords()
        _px, _py = _cl.getProjection(_x, _y)
        if math.hypot((_px - _x), (_py - _y)) > 1e-10:
            _xi, _yi = _p1.getCoords()
    elif _p2 == _p3 or _p2 == _p4:
        _x, _y = _p1.getCoords()
        _px, _py = _cl.getProjection(_x, _y)
        if math.hypot((_px - _x), (_py - _y)) > 1e-10:
            _xi, _yi = _p2.getCoords()
    else:
        _d = denom(_p1, _p2, _p3, _p4)
        if abs(_d) > 1e-10: # NOT parallel
            _r = rnum(_p1, _p2, _p3, _p4)/_d
            if not (_r < _zero or _r > _one):
                _p1x, _p1y = _p1.getCoords()
                _p2x, _p2y = _p2.getCoords()
                _xi = _p1x + _r * (_p2x - _p1x)
                _yi = _p1y + _r * (_p2y - _p1y)
    if _xi is not None and _yi is not None:
        ipts.append((_xi, _yi))

#
# circle - circle intersection
#
# see Paul Bourke's web pages for algorithm
#

def _circ_circ_intersection(ipts, circ1, circ2):
    _c1x, _c1y = circ1.getCenter().getCoords()
    _r1 = circ1.getRadius()
    _c2x, _c2y = circ2.getCenter().getCoords()
    _r2 = circ2.getRadius()
    _xdiff = _c2x - _c1x
    _ydiff = _c2y - _c1y
    if not (abs(_xdiff) < 1e-10 and abs(_ydiff) < 1e-10): # NOT concentric
        _sep = math.hypot(_xdiff, _ydiff)
        _maxsep = _r1 + _r2 + 1e-10
        _minsep = abs(_r1 - _r2) - 1e-10
        # print "sep: %g; maxsep: %g; minsep: %g" % (_sep, _maxsep, _minsep)
        if _minsep < _sep < _maxsep:
            _a = (pow(_r1, 2) - pow(_r2, 2) + pow(_sep, 2))/(2*_sep)
            _pcx = _c1x + _a * (_xdiff/_sep)
            _pcy = _c1y + _a * (_ydiff/_sep)
            # print "a: %g; pcx: %g; pcy: %g" % (_a, _pcx, _pcy)
            if abs(abs(_a) - _r1) < 1e-10: # single contact point
                ipts.append((_pcx, _pcy))
            else: # two contact points
                _h = math.sqrt(pow(_r1, 2) - pow(_a, 2))
                _x = _pcx + _h * (_ydiff/_sep)
                _y = _pcy - _h * (_xdiff/_sep)
                ipts.append((_x, _y))
                _x = _pcx - _h * (_ydiff/_sep)
                _y = _pcy + _h * (_xdiff/_sep)
                ipts.append((_x, _y))

#
# circle - arc intersection
#

def _circ_arc_intersection(ipts, obja, objb):
    if isinstance(obja, arc.Arc):
        _arc = obja
        _circ = objb
    else:
        _circ = obja
        _arc = objb
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _tempcirc = circle.Circle(_cp, _r)
    _ipts = []
    _circ_circ_intersection(_ipts, _circ, _tempcirc)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)
    _tempcirc.finish()

#
# circle - horizontal contruction line intersection
#

def _circ_hcl_intersection(ipts, obja, objb):
    if isinstance(obja, (circle.Circle, ccircle.CCircle)):
        _circ = obja
        _hcl = objb
    else:
        _circ = objb
        _hcl = obja
    _cp = _circ.getCenter()
    _r = _circ.getRadius()
    _hp = _hcl.getLocation()
    _hx, _hy = _hp.getCoords()
    if _hp == _cp:
        ipts.append(((_hx - _r), _hy))
        ipts.append(((_hx + _r), _hy))
    else:
        _cx, _cy = _circ.getCenter().getCoords()
        _ymin = _cy - _r
        _ymax = _cy + _r
        if abs(_ymin - _hy) < 1e-10:
            ipts.append((_cx, _ymin))
        elif abs(_ymax - _hy) < 1e-10:
            ipts.append((_cx, _ymax))
        elif _ymin < _hy < _ymax:
            _offset = math.sqrt(pow(_r, 2) - pow((_cy - _hy), 2))
            ipts.append(((_cx - _offset), _hy))
            ipts.append(((_cx + _offset), _hy))
        else:
            pass
#
# circle - vertical contruction line intersection
#

def _circ_vcl_intersection(ipts, obja, objb):
    if isinstance(obja, (circle.Circle, ccircle.CCircle)):
        _circ = obja
        _vcl = objb
    else:
        _circ = objb
        _vcl = obja
    _cp = _circ.getCenter()
    _r = _circ.getRadius()
    _vp = _vcl.getLocation()
    _vx, _vy = _vp.getCoords()
    if _vp == _cp:
        ipts.append((_vx, (_vy - _r)))
        ipts.append((_vx, (_vy + _r)))
    else:
        _cx, _cy = _circ.getCenter().getCoords()
        _xmin = _cx - _r
        _xmax = _cx + _r
        if abs(_xmin - _vx) < 1e-10:
            ipts.append((_xmin, _cy))
        elif abs(_xmax - _vx) < 1e-10:
            ipts.append((_xmax, _cy))
        elif _xmin < _vx < _xmax:
            _offset = math.sqrt(pow(_r, 2) - pow((_vx - _cx), 2))
            ipts.append((_vx, (_cy - _offset)))
            ipts.append((_vx, (_cy + _offset)))
        else:
            pass

#
# circle - angled construction line intersection
#

def _circ_acl_intersection(ipts, obja, objb):
    if isinstance(obja, (circle.Circle, ccircle.CCircle)):
        _circ = obja
        _acl = objb
    else:
        _circ = objb
        _acl = obja
    assert not isinstance(_circ, arc.Arc), "Arc found!"
    _p1x, _p1y = _acl.getLocation().getCoords()
    _angle = _acl.getAngle() * _dtr
    _xt = _p1x + math.cos(_angle)
    _yt = _p1y + math.sin(_angle)
    for _ip in sc_intersection(_p1x, _p1y, _xt, _yt, _circ, True):
        ipts.append(_ip)

#
# circle - 2-point construction line intersection
#

def _circ_cl_intersection(ipts, obja, objb):
    if isinstance(obja, (circle.Circle, ccircle.CCircle)):
        _circ = obja
        _cl = objb
    else:
        _circ = objb
        _cl = obja
    assert not isinstance(_circ, arc.Arc), "Arc found!"
    _p1, _p2 = _cl.getKeypoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    for _ip in sc_intersection(_p1x, _p1y, _p2x, _p2y, _circ, True):
        ipts.append(_ip)

#
# arc - arc intersection
#

def _arc_arc_intersection(ipts, arc1, arc2):
    _cp1 = arc1.getCenter()
    _r1 = arc1.getRadius()
    _tempcirc1 = circle.Circle(_cp1, _r1)
    _cp2 = arc2.getCenter()
    _r2 = arc2.getRadius()
    _tempcirc2 = circle.Circle(_cp2, _r2)
    _ipts = []
    _circ_circ_intersection(_ipts, _tempcirc1, _tempcirc2)
    if len(_ipts): # may have intersection points ...
        for _ip in _ipts:
            _cx, _cy = _cp1.getCoords()
            _x, _y = _ip
            _angle = math.atan2((_y - _cy), (_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if arc1.throughAngle(_angle):
                _cx, _cy = _cp2.getCoords()
                _angle = math.atan2((_y - _cy), (_x - _cx)) * _rtd
                if _angle < 0.0:
                    _angle = _angle + 360.0
                if arc2.throughAngle(_angle):
                    ipts.append(_ip)
    _tempcirc1.finish()
    _tempcirc2.finish()

#
# arc - horizontal construction line intersection
#

def _arc_hcl_intersection(ipts, obja, objb):
    if isinstance(obja, arc.Arc):
        _arc = obja
        _hcl = objb
    else:
        _arc = objb
        _hcl = obja
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _tempcirc = circle.Circle(_cp, _r)
    _ipts = []
    _circ_hcl_intersection(_ipts, _tempcirc, _hcl)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)
    _tempcirc.finish()

#
# arc - vertical construction line intersection
#

def _arc_vcl_intersection(ipts, obja, objb):
    if isinstance(obja, arc.Arc):
        _arc = obja
        _vcl = objb
    else:
        _arc = objb
        _vcl = obja
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _tempcirc = circle.Circle(_cp, _r)
    _ipts = []
    _circ_vcl_intersection(_ipts, _tempcirc, _vcl)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)
    _tempcirc.finish()

#
# arc - angled construction line intersection
#

def _arc_acl_intersection(ipts, obja, objb):
    if isinstance(obja, arc.Arc):
        _arc = obja
        _acl = objb
    else:
        _arc = objb
        _acl = obja
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _tempcirc = circle.Circle(_cp, _r)
    _ipts = []
    _circ_acl_intersection(_ipts, _tempcirc, _acl)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)
    _tempcirc.finish()

#
# arc - 2-point construction line intersection
#

def _arc_cl_intersection(ipts, obja, objb):
    if isinstance(obja, arc.Arc):
        _arc = obja
        _cl = objb
    else:
        _arc = objb
        _cl = obja
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _tempcirc = circle.Circle(_cp, _r)
    _ipts = []
    _circ_cl_intersection(_ipts, _tempcirc, _cl)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)
    _tempcirc.finish()

#
# horizontal construction line - vertical construction line intersection
#

def _hcl_vcl_intersection(ipts, obja, objb):
    if isinstance(obja, hcline.HCLine):
        _hcl = obja
        _vcl = objb
    else:
        _hcl = objb
        _vcl = obja
    _hx, _hy = _hcl.getLocation().getCoords()
    _vx, _vh = _vcl.getLocation().getCoords()
    ipts.append((_vx, _hy))

#
# horizontal construction line - angled construction line intersection
#

def _hcl_acl_intersection(ipts, obja, objb):
    if isinstance(obja, hcline.HCLine):
        _hcl = obja
        _acl = objb
    else:
        _hcl = objb
        _acl = obja
    _angle = _acl.getAngle()
    if abs(_angle) > 1e-10: # acl is NOT horizontal
        _xi = _yi = None
        _hp = _hcl.getLocation()
        _ap = _acl.getLocation()
        if _hp == _ap:
            _xi, _yi = _hp.getCoords()
        else:
            _hx, _hy = _hp.getCoords()
            _yi = _hy
            _ax, _ay = _ap.getCoords()
            if abs(abs(_angle) - 90.0) < 1e-10: # acl is vertical
                _xi = _ax
            else:
                _slope = math.tan(_angle * _dtr)
                _yint = _ay - _slope*_ax
                _xi = (_hy - _yint)/_slope
        ipts.append((_xi, _yi))

#
# horizontal construction line - 2-point construction line intersection
#

def _hcl_cl_intersection(ipts, obja, objb):
    if isinstance(obja, hcline.HCLine):
        _hcl = obja
        _cl = objb
    else:
        _hcl = objb
        _cl = obja
    _p1, _p2 = _cl.getKeypoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    _ydiff = _p2y - _p1y
    if abs(_ydiff) > 1e-10: # cline is NOT horizontal
        _xi = _yi = None
        _hp = _hcl.getLocation()
        if _hp == _p1:
            _xi, _yi = _p1.getCoords()
        elif _hp == _p2:
            _xi, _yi = _p2.getCoords()
        else:
            _hx, _hy = _hp.getCoords()
            _yi = _hy
            _xdiff = _p2x - _p1x
            if abs(_xdiff) < 1e-10: # cline is vertical
                _xi = _p1x
            else:
                _slope = _ydiff/_xdiff
                _yint = _p1y - _slope*_p1x
                _xi = (_hy - _yint)/_slope
        ipts.append((_xi, _yi))

#
# vertical construction line - angled construction line intersection
#

def _vcl_acl_intersection(ipts, obja, objb):
    if isinstance(obja, vcline.VCLine):
        _vcl = obja
        _acl = objb
    else:
        _vcl = objb
        _acl = obja
    _angle = _acl.getAngle()
    if abs(abs(_angle) - 90.0) > 1e-10: # acl is NOT vertical

        _vp = _vcl.getLocation()
        _ap = _acl.getLocation()
        if _vp == _ap:
            _xi, _yi = _vp.getCoords()
        else:
            _vx, _vy = _vp.getCoords()
            _xi = _vx
            _ax, _ay = _ap.getCoords()
            _slope = math.tan(_angle * _dtr)
            _yint = _ay - _slope*_ax
            _yi = _slope*_vx + _yint
        ipts.append((_xi, _yi))

#
# vertical construction line - 2-point construction line intersection
#

def _vcl_cl_intersection(ipts, obja, objb):
    if isinstance(obja, vcline.VCLine):
        _vcl = obja
        _cl = objb
    else:
        _vcl = objb
        _cl = obja
    _p1, _p2 = _cl.getKeypoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    _xdiff = _p2x - _p1x
    if abs(_xdiff) > 1e-10: # cline is NOT vertical
        _xi = _yi = None
        _vp = _vcl.getLocation()
        if _vp == _p1:
            _xi, _yi = _p1.getCoords()
        elif _vp == _p2:
            _xi, _yi = _p2.getCoords()
        else:
            _vx, _vy = _vp.getCoords()
            _xi = _vx
            _ydiff = _p2y - _p1y
            if abs(_ydiff) < 1e-10: # cline is horizontal
                _yi = _p1y
            else:
                _slope = _ydiff/_xdiff
                _yint = _p1y - _slope*_p1x
                _yi = _slope*_vx + _yint
        ipts.append((_xi, _yi))

#
# angled construction line - angled construction line intersection
#

def _acl_acl_intersection(ipts, acl1, acl2):
    _ap1 = acl1.getLocation()
    _ap1x, _ap1y = _ap1.getCoords()
    _angle1 = acl1.getAngle() * _dtr
    _xt1 = _ap1x + math.cos(_angle1)
    _yt1 = _ap1y + math.sin(_angle1)
    _t1 = point.Point(_xt1, _yt1)
    _ap2 = acl2.getLocation()
    _ap2x, _ap2y = _ap2.getCoords()
    _angle2 = acl2.getAngle() * _dtr
    _xt2 = _ap2x + math.cos(_angle2)
    _yt2 = _ap2y + math.sin(_angle2)
    _t2 = point.Point(_xt2, _yt2)
    _d = denom(_ap1, _t1, _ap2, _t2)
    if abs(_d) > 1e-10: # NOT parallel
        _xi = _yi = None
        if _ap1 == _ap2:
            _xi, _yi = _ap1.getCoords()
        else:
            _rn = rnum(_ap1, _t1, _ap2, _t2)
            if abs(_rn) > 1e-10: # NOT colinear
                _r = _rn/_d
                _xi = _ap1x + _r * (_xt1 - _ap1x)
                _yi = _ap1y + _r * (_yt1 - _ap1y)
        if _xi is not None and _yi is not None:
            ipts.append((_xi, _yi))

#
# angled construction line - 2-point construction line intersection
#

def _acl_cl_intersection(ipts, obja, objb):
    if isinstance(obja, acline.ACLine):
        _acl = obja
        _cl = objb
    else:
        _acl = objb
        _cl = obja
    _ap = _acl.getLocation()
    _apx, _apy = _ap.getCoords()
    _angle = _acl.getAngle() * _dtr
    _xt = _apx + math.cos(_angle)
    _yt = _apy + math.sin(_angle)
    _t1 = point.Point(_xt, _yt)
    _p1, _p2 = _cl.getKeypoints()
    _d = denom(_ap, _t1, _p1, _p2)
    if abs(_d) > 1e-10: # NOT parallel
        _xi = _yi = None
        if _ap == _p1:
            _xi, _yi = _p1.getCoords()
        elif _ap == _p2:
            _xi, _yi = _p2.getCoords()
        else:
            _rn = rnum(_ap, _t1, _p1, _p2)
            if abs(_rn) > 1e-10: # NOT colinear
                _r = _rn/_d
                _xi = _apx + _r * (_xt - _apx)
                _yi = _apy + _r * (_yt - _apy)
        if _xi is not None and _yi is not None:
            ipts.append((_xi, _yi))

#
# 2-point construction line - 2-point construction line intersection
#

def _cl_cl_intersection(ipts, cl1, cl2):
    _p1, _p2 = cl1.getKeypoints()
    _p3, _p4 = cl2.getKeypoints()
    _d = denom(_p1, _p2, _p3, _p4)
    if abs(_d) > 1e-10: # NOT parallel
        _xi = _yi = None
        if _p1 == _p3 or _p2 == _p3:
            _xi, _yi = _p3.getCoords()
        elif _p1 == _p4 or _p2 == _p4:
            _xi, _yi = _p4.getCoords()
        else:
            _rn = rnum(_p1, _p2, _p3, _p4)
            if abs(_rn) > 1e-10: # NOT colinear
                _r = _rn/_d
                _p1x, _p1y = _p1.getCoords()
                _p2x, _p2y = _p2.getCoords()
                _xi = _p1x + _r * (_p2x - _p1x)
                _yi = _p1y + _r * (_p2y - _p1y)
        if _xi is not None and _yi is not None:
            ipts.append((_xi, _yi))
#
# set segment intersecting function
#

def _segment_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func = _seg_seg_intersection
    elif isinstance(objb, arc.Arc):
        _func = _seg_arc_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _seg_circ_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _seg_hcl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _seg_vcl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _seg_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _seg_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set circle intersecting function
#

def _circ_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func = _seg_circ_intersection
    elif isinstance(objb, arc.Arc):
        _func = _circ_arc_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_circ_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _circ_hcl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _circ_vcl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _circ_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _circ_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set arc intersecting function
#

def _arc_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_arc_intersection
    elif isinstance(objb, arc.Arc):
        _func = _arc_arc_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_arc_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _arc_hcl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _arc_vcl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _arc_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _arc_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set hcline intersecting function
#

def _hcline_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_hcl_intersection
    elif isinstance(objb, arc.Arc):
        _func = _arc_hcl_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_hcl_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _non_intersecting
    elif isinstance(objb, vcline.VCLine):
        _func =_hcl_vcl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _hcl_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _hcl_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set vcline intersecting function
#

def _vcline_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_vcl_intersection
    elif isinstance(objb, arc.Arc):
        _func = _arc_vcl_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_vcl_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _hcl_vcl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _non_intersecting
    elif isinstance(objb, acline.ACLine):
        _func = _vcl_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _vcl_cl_intersection
    return _func

#
# set acline intersecting function
#

def _acline_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_acl_intersection
    elif isinstance(objb, arc.Arc):
        _func = _arc_acl_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_acl_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _hcl_acl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _vcl_acl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _acl_acl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _acl_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set cline intersecting function
#

def _cline_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_cl_intersection
    elif isinstance(objb, arc.Arc):
        _func = _arc_cl_intersection
    elif isinstance(objb, (circle.Circle, ccircle.CCircle)):
        _func = _circ_cl_intersection
    elif isinstance(objb, hcline.HCLine):
        _func = _hcl_cl_intersection
    elif isinstance(objb, vcline.VCLine):
        _func = _vcl_cl_intersection
    elif isinstance(objb, acline.ACLine):
        _func = _acl_cl_intersection
    elif isinstance(objb, cline.CLine):
        _func = _cl_cl_intersection
    else:
        _func = _null_intfunc
    return _func

#
# intersection functions for polylines
#

def _get_intfunc(obja, objb):
    if isinstance(obja, segment.Segment):
        _intfunc = _segment_intfuncs(objb)
    elif isinstance(obja, arc.Arc):
        _intfunc = _arc_intfuncs(objb)
    elif isinstance(obja, (circle.Circle, ccircle.CCircle)):
        _intfunc = _circ_intfuncs(objb)
    elif isinstance(obja, hcline.HCLine):
        _intfunc = _hcline_intfuncs(objb)
    elif isinstance(obja, vcline.VCLine):
        _intfunc = _vcline_intfuncs(objb)
    elif isinstance(obja, acline.ACLine):
        _intfunc = _acline_intfuncs(objb)
    elif isinstance(obja, cline.CLine):
        _intfunc = _cline_intfuncs(objb)
    else:
        _intfunc = _null_intfunc
    return _intfunc

def find_intersections(obja, objb):
    _ipts = []
    _intfunc = _get_intfunc(obja, objb)
    _intfunc(_ipts, obja, objb)
    return _ipts
