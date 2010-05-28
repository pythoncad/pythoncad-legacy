#
# Copyright (c) 2002, 2003, 2006 Art Haas
#
# Copyright (c) 2010 Matteo Boscolo
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

from Kernel.GeoEntity.point       import Point
from Kernel.GeoEntity.segment     import Segment
from Kernel.GeoEntity.arc         import Arc
from Kernel.GeoEntity.acline      import ACLine
from Kernel.GeoEntity.ccircle     import CCircle
from Kernel.GeoEntity.polyline    import Polyline
from Kernel.GeoEntity.ellipse     import Ellipse
from Kernel.GeoUtil.geolib        import Vector
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
    if not isinstance(p1, Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p1)`
    if not isinstance(p2, Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p2)`
    if not isinstance(p3, Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p3)`
    if not isinstance(p4, Point):
        raise TypeError, "Invalid argument to denom(): " + `type(p4)`
    _p1x, _p1y = p1.getCoords()
    _p2x, _p2y = p2.getCoords()
    _p3x, _p3y = p3.getCoords()
    _p4x, _p4y = p4.getCoords()
    return ((_p2x - _p1x)*(_p4y - _p3y)) - ((_p2y - _p1y)*(_p4x - _p3x))

def rnum(p1, p2, p3, p4):
    if not isinstance(p1, Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p1)`
    if not isinstance(p2, Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p2)`
    if not isinstance(p3, Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p3)`
    if not isinstance(p4, Point):
        raise TypeError, "Invalid argument to rnum(): " + `type(p4)`
    _p1x, _p1y = p1.getCoords()
    _p2x, _p2y = p2.getCoords()
    _p3x, _p3y = p3.getCoords()
    _p4x, _p4y = p4.getCoords()
    return ((_p1y - _p3y)*(_p4x - _p3x)) - ((_p1x - _p3x)*(_p4y - _p3y))

def snum(p1, p2, p3, p4):
    if not isinstance(p1, Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p1)`
    if not isinstance(p2, Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p2)`
    if not isinstance(p3, Point):
        raise TypeError, "Invalid argument to snum(): " + `type(p3)`
    if not isinstance(p4, Point):
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
    if not isinstance(_circ, (Arc,CCircle)):
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
    if isinstance(obja, Segment):
        _seg = obja
        _circ = objb
    else:
        _seg = objb
        _circ = obja
    if isinstance(_circ, Arc):
        if _circ.isCircle:
            _p1, _p2 = _seg.getEndpoints()
            _p1x, _p1y = _p1.getCoords()
            _p2x, _p2y = _p2.getCoords()
            for _ip in sc_intersection(_p1x, _p1y, _p2x, _p2y, _circ):
                ipts.append(_ip)
        else:
            _seg_arc_intersection(ipts, obja, objb)
#
# segment - arc intersection
#

def _seg_arc_intersection(ipts, obja, objb):
    if isinstance(obja, Segment):
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
# segment - angled construction line intersection
#

def _seg_acl_intersection(ipts, obja, objb):
    if isinstance(obja, Segment):
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
    if isinstance(obja, Arc) and not obja.isCircle:
        _arc = obja
        _circ = objb
    else:
        _circ = obja
        _arc = objb
    _cp = _arc.getCenter()
    _r = _arc.getRadius()
    _ipts = []
    _circ_circ_intersection(_ipts, _circ, _arc)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)




#
# circle - angled construction line intersection
#

def _circ_acl_intersection(ipts, obja, objb):
    if isinstance(obja, (Arc, CCircle)):
        _circ = obja
        _acl = objb
    else:
        _circ = objb
        _acl = obja
    
    if _circ.isCircle:
        _p1x, _p1y = _acl.getLocation().getCoords()
        _angle = _acl.getAngle() * _dtr
        _xt = _p1x + math.cos(_angle)
        _yt = _p1y + math.sin(_angle)
        for _ip in sc_intersection(_p1x, _p1y, _xt, _yt, _circ, True):
            ipts.append(_ip)
    else:
        _arc_hcl_intersection(ipts, obja, objb)
 
#
# arc - arc intersection
#

def _arc_arc_intersection(ipts, arc1, arc2):
    _ipts = []
    _circ_circ_intersection(_ipts, arc1, arc2)
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

#
# arc - angled construction line intersection
#

def _arc_acl_intersection(ipts, obja, objb):
    if isinstance(obja, Arc):
        _arc = obja
        _acl = objb
    else:
        _arc = objb
        _acl = obja
    _ipts = []
    _circ_acl_intersection(_ipts, _arc, _acl)
    if len(_ipts): # may have intersection points ...
        _cx, _cy = _cp.getCoords()
        for _ip in _ipts:
            _x, _y = _ip
            _angle = math.atan2((_y - _cy),(_x - _cx)) * _rtd
            if _angle < 0.0:
                _angle = _angle + 360.0
            if _arc.throughAngle(_angle):
                ipts.append(_ip)

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
# Ellipse intersection function
#
def _seg_eli_intersection(ipts, pol, seg):
    """
        calculate the intersection beteen polyline and segment
    """
    #TODO: Calculate the ellipse segment intersection
    pass
    tempIpts=[]
    ipts=tempIpts
def _arc_eli_intersection(ipts,eli, arc):
    """
        calculate the intersection beteen polyline and arc
    """
    pass
    #TODO: Calculate the ellipse arc intersection
    tempIpts=[]
    ipts=tempIpts
def _circ_eli_intersection(ipts,eli, cci):
    """
        calculate the intersection beteen polyline and construction circle
    """
    pass
    #TODO:  Calculate the ellipse ccircle intersection 
    tempIpts=[]
    ipts=tempIpts
def _acl_eli_intersection(ipts, eli, acl):
    """
        calculate the intersection beteen polyline and angular construction line
    """
    pass
    #TODO: calculate the ellipse acline intersection
    tempIpts=[]
    ipts=tempIpts
def _pol_eli_intersection(ipts, pol, eli):
    """
        calculate the intersection beteen polyline and ellipse
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_eli_intersection(tempipts,  seg,  eli)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break
def _eli_eli_intersection(ipts, eli1, eli2):
    """
        found an intersection between polyline and other object
    """
    pass
    if isinstance(eli1, Ellipse):
        if isinstance(eli2, Ellipse):
            #todo:calculate the ellipse ellipse intersection
            tempIpts=[]
            if len(tempIpts)>0: 
                ipts=tempIpts
#
# Poliline intersect functions def _seg_pol_intersection(ipts, pol, seg):
#
def _seg_pol_intersection(ipts, pol, arc):
    """
        calculate the intersection beteen polyline and segment
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_seg_intersection(tempipts,  seg, seg)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break
            
def _arc_pol_intersection(ipts, pol, arc):
    """
        calculate the intersection beteen polyline and arc
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_arc_intersection(tempipts,  seg, arc)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break
def _ccir_pol_intersection(ipts, pol, cci):
    """
        calculate the intersection beteen polyline and construction circle
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_cci_intersection(tempipts,  seg, cci)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break
    
def _acl_pol_intersection(ipts, pol, acl):
    """
        calculate the intersection beteen polyline and angular construction line
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_acl_intersection(tempipts,  seg,  acl)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break

def _eli_pol_intersection(ipts, pol, eli):
    """
        calculate the intersection beteen polyline and ellipse
    """
    for seg in pol.getSegments():
        tempIpts=[]
        _seg_eli_intersection(tempipts,  seg,  eli)
        if len(tempIpts)>0: 
            ipts=tempIpts
            break

def _pol_pol_intersection(ipts, pol1, pol2):
    """
        found an intersection between polyline and other object
    """
    if isinstance(pol1, Polyline):
        if isinstance(pol2, Polyline):
            for seg1 in pol1.getSegments():
                for seg2 in pol2.getSegments():
                    tempIpts=[]
                    _seg_seg_intersection(tempipts,  seg1,  seg2)
                    if len(tempIpts)>0: 
                        ipts=tempIpts
                        break
#
# set segment intersecting function
#

def _segment_intfuncs(objb):
    if isinstance(objb, Segment):
        _func = _seg_seg_intersection
    elif isinstance(objb, Arc):
        _func = _seg_arc_intersection
    elif isinstance(objb, CCircle):
        _func = _seg_circ_intersection
    elif isinstance(objb, ACLine):
        _func = _seg_acl_intersection
    elif isinstance(objb, Ellipse):
        _func = _seg_eli_intersection
    elif isinstance(objb, Polyline):
        _func = _seg_pol_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set circle intersecting function
#

def _circ_intfuncs(objb):
    if isinstance(objb, Segment):
        _func = _seg_circ_intersection
    elif isinstance(objb, Arc):
        _func = _circ_arc_intersection
    elif isinstance(objb, ACLine):
        _func = _circ_acl_intersection
    elif isinstance(objb, Ellipse):
        _func = _circ_eli_intersection
    elif isinstance(objb, Polyline):
        _func = _circ_pol_intersection
    elif isinstance(objb, CCircle):
        _func = _circ_circ_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set arc intersecting function
#

def _arc_intfuncs(objb):
    if isinstance(objb, Segment):
        _func  = _seg_arc_intersection
    elif isinstance(objb, ccircle.CCircle):
        _func = _circ_arc_intersection
    elif isinstance(objb, ACLine):
        _func = _arc_acl_intersection
    elif isinstance(objb, Ellipse):
        _func = _arc_eli_intersection
    elif isinstance(objb, Polyline):
        _func = _arc_pol_intersection
    elif isinstance(objb, Arc):
        _func = _arc_arc_intersection
    else:
        _func = _null_intfunc
    return _func

#
# set acline intersecting function
#

def _acline_intfuncs(objb):
    if isinstance(objb, segment.Segment):
        _func  = _seg_acl_intersection
    elif isinstance(objb, Arc):
        _func = _arc_acl_intersection
    elif isinstance(objb, CCircle):
        _func = _circ_acl_intersection
    elif isinstance(objb, Ellipse):
        _func = _acl_eli_intersection
    elif isinstance(objb, Polyline):
        _func = _acl_pol_intersection
    elif isinstance(objb, ACLine):
        _func = _acl_acl_intersection
    else:
        _func = _null_intfunc
    return _func
#
# Intersection with ellipse
#

def  _ellipse_intfuncs(objb):
    if isinstance(objb, Segment):
        _func = _seg_eli_intersection
    elif isinstance(objb, Arc):
        _func = _arc_eli_intersection
    elif isinstance(objb, CCircle):
        _func = _circ_eli_intersection
    elif isinstance(objb, ACLine):
        _func = _acl_eli_intersection
    elif isinstance(objb,Polyline):
        _func = _pol_eli_intersection
    elif isinstance(objb,Polyline):
        _func = _eli_eli_intersection
    else:
        _func = _null_intfunc
    return _func
#
# intersection functions for polylines
#
def  _polyline_intfuncs(objb):
    if isinstance(objb, Segment):
        _func = _seg_pol_intersection
    elif isinstance(objb, Arc):
        _func = _arc_pol_intersection
    elif isinstance(objb, CCircle):
        _func = _ccir_pol_intersection
    elif isinstance(objb, ACLine):
        _func = _acl_pol_intersection
    elif isinstance(objb, Ellipse):
        _func = _eli_pol_intersection
    elif isinstance(objb,Polyline):
        _func = _pol_pol_intersection
    else:
        _func = _null_intfunc
    return _func

def _get_intfunc(obja, objb):
    if isinstance(obja, Segment):
        _intfunc = _segment_intfuncs(objb)
    elif isinstance(obja, Arc):
        _intfunc = _arc_intfuncs(objb)
    elif isinstance(obja, CCircle):
        _intfunc = _circ_intfuncs(objb)
    elif isinstance(obja, ACLine):
        _intfunc = _acline_intfuncs(objb)
    elif isinstance(obja, Polyline):
        _intfunc = _polyline_intfuncs(objb)
    elif isinstance(obja, Ellipse):
        _intfunc = _ellipse_intfuncs(objb)
    else:
        _intfunc = _null_intfunc
    return _intfunc

def find_intersections(obja, objb):
    """
        Find intersection points`
        Return an array of tuple point[(x,y),(x,y)]
    """
    _ipts = []
    _intfunc = _get_intfunc(obja, objb)
    _intfunc(_ipts, obja, objb)
    return _ipts

def find_segment_extended_intersection(obja, objb):
    """
        Extend the segment intersection on a cline intersection
    """
    if isinstance(obja, Segment):
        p1, p2=obja.getEndpoints()
        v=Vector(p1, p2)
        obja=ACLine(p1, v.ang())
    if isinstance(objb, Segment):
        p1, p2=objb.getEndpoints()
        v=Vector(p1, p2)
        objb=ACLine(p1, v.ang())
    return find_intersections(obja, objb)
