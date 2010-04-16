#
# Copyright (c) 2003, 2004, 2006 Art Haas
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
# functions for splitting entities in a drawing

import math

from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic import util
from PythonCAD.Generic import intersections

_rtd = (180.0/math.pi)

def _most_used(plist):
    _pmax = plist.pop()
    _max = _pmax.countUsers()
    for _pt in plist:
        _count = _pt.countUsers()
        if _count > _max:
            _max = _count
            _pmax = _pt
    return _pmax

def _get_point(l, x, y):
    _pts = l.find('point', x, y)
    if len(_pts) == 0:
        _lp = Point(x, y)
        l.setAutosplit(False)
        l.addObject(_lp)
    else:
        _lp = _most_used(_pts)
    return _lp
    
def split_segment_at(seg, x, y):
    if not isinstance(seg, Segment):
        raise TypeError, "Invalid Segment: " + `type(seg)`
    _x = util.get_float(x)
    _y = util.get_float(y)
    _layer = seg.getParent()
    if _layer is None:
        return None
    _p = seg.getProjection(_x, _y)
    if _p is None:
        return None
    _px, _py = _p
    if abs(_px - _x) > 1e-10 or abs(_py - _y) > 1e-10:
        return None
    _lp = _get_point(_layer, _px, _py)
    _p1, _p2 = seg.getEndpoints()
    if _lp == _p1 or _lp == _p2:
        return None
    _s = seg.getStyle()
    _l = seg.getLinetype()
    _c = seg.getColor()
    _t = seg.getThickness()
    _s1 = Segment(_p1, _lp, _s, _l, _c, _t)
    _s2 = Segment(_lp, _p2, _s, _l, _c, _t)
    return _s1, _s2

def split_circle_at(circ, x, y):
    if not isinstance(circ, Circle):
        raise TypeError, "Invalid Circle: " + `type(circ)`
    _x = util.get_float(x)
    _y = util.get_float(y)
    _layer = circ.getParent()
    if _layer is None:
        return None
    _p = circ.mapCoords(_x, _y)
    if _p is None:
        return None
    _px, _py = _p
    if abs(_px - _x) > 1e-10 or abs(_py - _y) > 1e-10:
        return None
    _lp = _get_point(_layer, _px, _py)
    _s = circ.getStyle()
    _cp = circ.getCenter()
    _angle = _rtd * math.atan2((_lp.y - _cp.y),(_lp.x - _cp.x))
    _l = circ.getLinetype()
    _c = circ.getColor()
    _t = circ.getThickness()
    _arc = Arc(_cp, circ.getRadius(), _angle, _angle, _s, _l, _c, _t)
    return _arc

def split_arc_at(arc, x, y):
    if not isinstance(arc, Arc):
        raise TypeError, "Invalid Arc: " + `type(arc)`
    _x = util.get_float(x)
    _y = util.get_float(y)
    _layer = arc.getParent()
    if _layer is None:
        return None
    _p = arc.mapCoords(_x, _y)
    if _p is None:
        return None
    _px, _py = _p
    if abs(_px - _x) > 1e-10 or abs(_py - _y) > 1e-10:
        return None
    _lp = _get_point(_layer, _px, _py)
    _s = arc.getStyle()
    _cp = arc.getCenter()
    _r = arc.getRadius()
    _sa = arc.getStartAngle()
    _ea = arc.getEndAngle()
    _angle = _rtd * math.atan2((_lp.y - _cp.y),(_lp.x - _cp.x))
    _l = arc.getLinetype()
    _c = arc.getColor()
    _t = arc.getThickness()
    _a1 = Arc(_cp, _r, _sa, _angle, _s, _l, _c, _t)
    _a2 = Arc(_cp, _r, _angle, _ea, _s, _l, _c, _t)
    return _a1, _a2

def split_polyline_at(pl, x, y):
    if not isinstance(pl, Polyline):
        raise TypeError, "Invalid Polyline: " + `type(pl)`
    _x = util.get_float(x)
    _y = util.get_float(y)
    _layer = pl.getParent()
    if _layer is None:
        return False
    _pts = pl.getPoints()
    for _i in range(len(_pts) - 1):
        _p1x, _p1y = _pts[_i].getCoords()
        _p2x, _p2y = _pts[_i + 1].getCoords()
        _p = util.map_coords(_x, _y, _p1x, _p1y, _p2x, _p2y)
        if _p is None:
            continue
        _px, _py = _p
        if ((abs(_px - _p1x) < 1e-10 and abs(_py - _p1y) < 1e-10) or
            (abs(_px - _p2x) < 1e-10 and abs(_py - _p2y) < 1e-10)):
            continue
        _lp = _get_point(_layer, _px, _py)
        pl.addPoint((_i + 1), _lp)
        return True
    return False

def split_segment(seg, pt):
    """Split a segment into two segments at a point.

split_segment(seg, pt)

seg: The segment to split
pt: The point used to split the segment.

There is presently no check to test that the point lies
on the segment.
    """
    if not isinstance(seg, Segment):
        raise TypeError, "Invalid Segment: " + `type(seg)`
    if not isinstance(pt, Point):
        raise TypeError, "Invalid Point: " + `type(pt)`
    _sp = seg.getParent()
    _pp = pt.getParent()
    if _sp is not None and _pp is not None and _sp is not _pp:
        raise RuntimeError, "Invalid Point for Segment splitting."
    _p1, _p2 = seg.getEndpoints()
    _s = seg.getStyle()
    _l = seg.getLinetype()
    _c = seg.getColor()
    _t = seg.getThickness()
    _s1 = Segment(_p1, pt, _s, _l, _c, _t)
    _s2 = Segment(pt, _p2, _s, _l, _c, _t)
    return _s1, _s2

def split_circle(circle, pt):
    """Split a circle into a single arc.

split_circle(circle, pt)

circle: The circle to split
pt: The point used to determine the start/end angles of the arc.
    """
    if not isinstance(circle, Circle):
        raise TypeError, "Invalid Circle: " + `type(circle)`
    if not isinstance(pt, Point):
        raise TypeError, "Invalid Point: " + `type(pt)`
    _cp = circle.getParent()
    _pp = pt.getParent()
    if _cp is not None and _pp is not None and _cp is not _pp:
        raise RuntimeError, "Invalid Point for Circle splitting."
    _cp = circle.getCenter()
    _rad = circle.getRadius()
    _cx, _cy = _cp.getCoords()
    _px, _py = pt.getCoords()
    _angle = _rtd * math.atan2((_py - _cy), (_px - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    return Arc(_cp, _rad, _angle, _angle,
                           circle.getStyle(), circle.getLinetype(),
                           circle.getColor(), circle.getThickness())

def split_arc(arc, pt):
    """Split an arc into two connected arcs.

split_arc(arc, pt)

arc: The arc to split.
pt: The point used to determine the angle at which to split the arc.
    """
    if not isinstance(arc, Arc):
        raise TypeError, "Invalid Arc: " + `type(arc)`
    if not isinstance(pt, Point):
        raise TypeError, "Invalid Point: " + `type(pt)`
    _ap = arc.getParent()
    _pp = pt.getParent()
    if _ap is not None and _pp is not None and _ap is not _pp:
        raise RuntimeError, "Invalid Point for Arc splitting."
    _cp = arc.getCenter()
    _cx, _cy = _cp.getCoords()
    _px, _py = pt.getCoords()
    _angle = _rtd * math.atan2((_py - _cy), (_px - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    if not arc.throughAngle(_angle):
        raise ValueError, "Arc does not exist at angle %g" % _angle
    _rad = arc.getRadius()
    _sa = arc.getStartAngle()
    _ea = arc.getEndAngle()
    _style = arc.getStyle()
    _linetype = arc.getLinetype()
    _color = arc.getColor()
    _thickness = arc.getThickness()
    _arc1 = Arc(_cp, _rad, _sa, _angle,
                            _style, _linetype, _color, _thickness)
    _arc2 = Arc(_cp, _rad, _angle, _ea,
                            _style, _linetype, _color, _thickness)
    return _arc1, _arc2

def split_polyline(polyline, pt):
    if not isinstance(polyline, Polyline):
        raise TypeError, "Invalid Polyline: " + `type(polyline)`
    if not isinstance(pt, Point):
        raise TypeError, "Invalid Point: " + `type(pt)`
    _plp = polyline.getParent()
    _pp = pt.getParent()
    if _plp is not None and _pp is not None and _plp is not _pp:
        raise RuntimeError, "Invalid Point for Polyline splitting."
    _px, _py = pt.getCoords()
    _count = len(polyline)
    for _i in range(_count - 1):
        _hit = False
        _p1x, _p1y = polyline.getPoint(_i).getCoords()
        _p2x, _p2y = polyline.getPoint(_i + 1).getCoords()
        if abs(_p2x - _p1x) < 1e-10: # vertical
            if (abs(_p2x - _px) < 1e-10 and
                min(_p1y, _p2y) < _py < max(_p1y, _p2y)):
                _hit = True
        elif abs(_p2y - _p1y) < 1e-10: # horizontal
            if (abs(_p2y - _py) < 1e-10 and
                min(_p1x, _p2x) < _px < max(_p1x, _p2x)):
                _hit = True
        else:
            _slope = (_p2y - _p1y)/(_p2x - _p1x)
            _yint = _p2y - (_slope * _p2x)
            _ytest = (_slope * _px) + _yint
            if abs(_ytest - _py) < 1e-10:
                _hit = True
        if _hit:
            polyline.addPoint((_i + 1), pt)
            break

class SplitManager(object):
    def __init__(self, layer):
        if not isinstance(layer, Layer):
            raise TypeError, "Invalid Layer: " + `type(layer)`
        self.__layer = layer
        self.__segs = []
        self.__circs = []
        self.__arcs = []
        self.__plines = []
        self.__rects = {}

    def segBounds(s):
        if not isinstance(s, Segment):
            raise TypeError, "Invalid Segment: " + `type(s)`
        _p1, _p2 = s.getEndpoints()
        _x, _y = _p1.getCoords()
        _xmin = _xmax = _x
        _ymin = _ymax = _y
        _x, _y = _p2.getCoords()
        if _x < _xmin:
            _xmin = _x
        if _y < _ymin:
            _ymin = _y
        if _x > _xmax:
            _xmax = _x
        if _y > _ymax:
            _ymax = _y
        return _xmin, _ymin, _xmax, _ymax

    segBounds = staticmethod(segBounds)

    def circBounds(c):
        if not isinstance(c, Circle):
            raise TypeError, "Invalid Circle: " + `type(c)`
        _x, _y = c.getCenter().getCoords()
        _r = c.getRadius()
        return ((_x - _r), (_y - _r), (_x + _r), (_y + _r))

    circBounds = staticmethod(circBounds)

    def canIntersect(r1, r2):
        if not isinstance(r1, tuple):
            raise TypeError, "Invalid R1 tuple: " + `type(r1)`
        if len(r1) != 4:
            raise ValueError, "R1 length error: " + str(r1)
        if not isinstance(r2, tuple):
            raise TypeError, "Invalid R2 tuple: " + `type(r2)`
        if len(r2) != 4:
            raise ValueError, "R2 length error: " + str(r2)
        return not ((r1[2] < r2[0]) or # r1 xmax < r2 xmin
                    (r1[0] > r2[2]) or # r1 xmin > r2 xmax
                    (r1[3] < r2[1]) or # r1 ymax < r2 ymin
                    (r1[1] > r2[3])) # r1 ymin > r2 ymax

    canIntersect = staticmethod(canIntersect)

    def splitSegTwoPts(seg, pt1, pt2):
        _p1, _p2 = seg.getEndpoints()
        _s = seg.getStyle()
        _l = seg.getLinetype()
        _c = seg.getColor()
        _t = seg.getThickness()
        _s1 = Segment(_p1, pt1, _s, _l, _c, _t)
        _s2 = Segment(pt1, pt2, _s, _l, _c, _t)
        _s3 = Segment(pt2, _p2, _s, _l, _c, _t)
        return _s1, _s2, _s3

    splitSegTwoPts = staticmethod(splitSegTwoPts)

    def splitCircTwoPts(circ, p1, p2):
        _cp = circ.getCenter()
        _r = circ.getRadius()
        _cx, _cy = _cp.getCoords()
        _px, _py = p1.getCoords()
        _a1 = _rtd * math.atan2((_py - _cy),(_px - _cx))
        if _a1 < 0.0:
            _a1 = _a1 + 360.0
        _px, _py = p2.getCoords()
        _a2 = _rtd * math.atan2((_py - _cy),(_px - _cx))
        if _a2 < 0.0:
            _a2 = _a2 + 360.0
        _s = circ.getStyle()
        _c = circ.getColor()
        _l = circ.getLinetype()
        _t = circ.getThickness()
        _arc1 = Arc(_cp, _r, _a1, _a2, _s, _l, _c, _t)
        _arc2 = Arc(_cp, _r, _a2, _a1, _s, _l, _c, _t)
        return _arc1, _arc2

    splitCircTwoPts = staticmethod(splitCircTwoPts)

    def splitArcTwoPts(arc, p1, p2):
        _cp = arc.getCenter()
        _r = arc.getRadius()
        _sa = arc.getStartAngle()
        _ea = arc.getEndAngle()
        _cx, _cy = _cp.getCoords()
        _px, _py = p1.getCoords()
        _ap1 = _rtd * math.atan2((_py - _cy), (_px - _cx))
        if _ap1 < 0.0:
            _ap1 = _ap1 + 360.0
        _px, _py = p2.getCoords()
        _ap2 = _rtd * math.atan2((_py - _cy), (_px - _cx))
        if _ap2 < 0.0:
            _ap2 = _ap2 + 360.0
        if _sa < _ea:
            _a1 = min(_ap1, _ap2)
            _a2 = max(_ap1, _ap2)
        else:
            _d1 = _ap1 - _sa
            if _d1 < 0.0:
                _d1 = _ap1 + _sa
            _d2 = _ap2 - _sa
            if _d2 < 0.0:
                _d2 = _ap2 + _sa
            if _d1 < _d2:
                _a1 = _ap1
                _a2 = _ap2
            else:
                _a1 = _ap2
                _a2 = _ap1
        _s = arc.getStyle()
        _l = arc.getLinetype()
        _c = arc.getColor()
        _t = arc.getThickness()
        _arc1 = Arc(_cp, _r, _sa, _a1, _s, _l, _c, _t)
        _arc2 = Arc(_cp, _r, _a1, _a2, _s, _l, _c, _t)
        _arc3 = Arc(_cp, _r, _a2, _ea, _s, _l, _c, _t)
        return _arc1, _arc2, _arc3

    splitArcTwoPts = staticmethod(splitArcTwoPts)
    
    def addObject(self, obj):
        if obj.getParent() is not self.__layer:
            raise ValueError, "Invalid object parent: " + `obj`
        _olist = None
        if isinstance(obj, Segment):
            _olist = self.__segs
        elif isinstance(obj, Circle):
            _olist = self.__circs
        elif isinstance(obj, Arc):
            _olist = self.__arcs
        elif isinstance(obj, Polyline):
            _olist = self.__plines
        else:
            raise TypeError, "Unexpected object: " + `type(obj)`
        _seen = False
        for _obj in _olist:
            if _obj is obj:
                _seen = True
                break
        if _seen:
            raise RuntimeError, "Object already stored: " + `obj`
        _olist.append(obj)

    def delObject(self, obj):
        _olist = None
        if isinstance(obj, Segment):
            _olist = self.__segs
        elif isinstance(obj, Circle):
            _olist = self.__circs
        elif isinstance(obj, Arc):
            _olist = self.__arcs
        elif isinstance(obj, Polyline):
            _olist= self.__plines
        else:
            raise TypeError, "Unexpected object: " + `type(obj)`
        for _i in range(len(_olist)):
            if _olist[_i] is obj:
                del _olist[_i]
                break

    def getSegments(self):
        return self.__segs

    def getCircles(self):
        return self.__circs

    def getArcs(self):
        return self.__arcs

    def getPolylines(self):
        return self.__plines

    def splitObjects(self):
        if len(self.__segs):
            self.__splitSegSeg()
            if len(self.__circs):
                self.__splitSegCircle()
            if len(self.__arcs):
                self.__splitSegArc()
            if len(self.__plines):
                self.__splitSegPolyline()
        if len(self.__circs):
            self.__splitCircCirc()
        if len(self.__circs) and len(self.__arcs):
            self.__splitCircArc()
        if len(self.__circs) and len(self.__plines):
            self.__splitCircPolyline()
        if len(self.__arcs):
            self.__splitArcArc()
            if len(self.__plines):
                self.__splitArcPolyline()
        if len(self.__plines):
            self.__splitPolyPoly()

    def __getPoint(self, x, y):
        _layer = self.__layer
        _pts = _layer.find('point', x, y)
        if len(_pts) == 0:
            _ip = Point(x, y)
            _layer.setAutosplit(False)
            _layer.addObject(_ip)
        else:
            _ip = _most_used(_pts)
        return _ip

    def __splitSegSeg(self):
        _layer = self.__layer
        _segs = self.__segs
        _rects = self.__rects
        _slist = []
        _sdict = {}
        while len(_segs):
            _seg = _segs.pop()
            _slist.append(_seg)
            _segid = id(_seg)
            if _segid in _sdict and not _sdict[_segid]:
                continue
            _p1, _p2 = _seg.getEndpoints()
            if (_p1.getParent() is not _layer or
                _p2.getParent() is not _layer):
                raise RuntimeError, "Invalid Segment endpoints: " + `_seg`
            _sdict[_segid] = True
            _rseg = _rects.get(_segid)
            if _rseg is None:
                _rseg = SplitManager.segBounds(_seg)
                _rects[_segid] = _rseg
            for _s in _segs:
                _sid = id(_s)
                if _sid in _sdict and not _sdict[_sid]:
                    continue
                _p3, _p4 = _s.getEndpoints()
                if (_p3.getParent() is not _layer or
                    _p4.getParent() is not _layer):
                    raise RuntimeError, "Invalid Segment endpoints: " + `_s`
                if _p1 == _p3 or _p1 == _p4 or _p2 == _p3 or _p2 == _p4:
                    continue
                _rs = _rects.get(_sid)
                if _rs is None:
                    _rs = SplitManager.segBounds(_s)
                    _rects[_sid] = _rs
                if not SplitManager.canIntersect(_rseg, _rs):
                    continue
                _ipts = intersections.find_intersections(_s, _seg)
                if len(_ipts):
                    _x, _y = _ipts[0]
                    _ip = self.__getPoint(_x, _y)
                    if _ip != _p3 and _ip != _p4:
                        _s1, _s2 = split_segment(_s, _ip)
                        _segs.append(_s1)
                        _segs.append(_s2)
                        _sdict[_sid] = False
                    if _ip != _p1 and _ip != _p2:
                        _s1, _s2 = split_segment(_seg, _ip)
                        _segs.append(_s1)
                        _segs.append(_s2)
                        _sdict[_segid] = False
                        break
        _nseg = []
        _dseg = []
        for _seg in _slist:
            _status = _sdict.get(id(_seg))
            if _status is None:
                raise RuntimeError, "No status for Segment: " + `_seg`
            elif _status:
                _nseg.append(_seg)
            else:
                _dseg.append(_seg)
        for _seg in _dseg:
            del self.__rects[id(_seg)]
            if _seg.getParent() is not None:
                _layer.delObject(_seg)
            else:
                _seg.finish()
        for _seg in _nseg:
            if _seg.getParent() is None:
                _layer.addObject(_seg)
        self.__segs = _nseg

    def __splitSegCircle(self):
        _segs = self.__segs
        _circs = self.__circs
        _layer = self.__layer
        _rects = self.__rects
        _slist = []
        _alist = []
        _odict = {}
        while len(_segs):
            _seg = _segs.pop()
            _slist.append(_seg)
            _sid = id(_seg)
            if _sid in _odict and not _odict[_sid]:
                continue
            _p1, _p2 = _seg.getEndpoints()
            if (_p1.getParent() is not _layer or
                _p2.getParent() is not _layer):
                raise RuntimeError, "Invalid Segment endpoints: " + `_seg`
            _odict[_sid] = True
            _rs = _rects.get(_sid)
            if _rs is None:
                _rs = SplitManager.segBounds(_seg)
                _rects[_sid] = _rs
            for _circ in _circs:
                _cid = id(_circ)
                if _cid in _odict and not _odict[_cid]:
                    continue
                _odict[_cid] = True
                _rc = _rects.get(_cid)
                if _rc is None:
                    _rc = SplitManager.circBounds(_circ)
                    _rects[_cid] = _rc
                if not SplitManager.canIntersect(_rs, _rc):
                    continue
                _ipts = intersections.find_intersections(_seg, _circ)
                if len(_ipts):
                    _s1 = _s2 = _s3 = _a1 = _a2 = None
                    _p1, _p2 = _seg.getEndpoints()
                    _count = len(_ipts)
                    if _count == 1:
                        _x, _y = _ipts[0]
                        _ip = self.__getPoint(_x, _y)
                        _a1 = split_circle(_circ, _ip)
                        if _ip != _p1 and _ip != _p2:
                            _s1, _s2 = split_segment(_seg, _ip)
                    elif _count == 2:
                        _x, _y = _ipts[0]
                        _ip1 = self.__getPoint(_x, _y)
                        _x, _y = _ipts[1]
                        _ip2 = self.__getPoint(_x, _y)
                        _a1, _a2 = SplitManager.splitCircTwoPts(_circ, _ip1, _ip2)
                        if (_ip1 != _p1 and
                            _ip1 != _p2 and
                            _ip2 != _p1 and
                            _ip2 != _p2):
                            if ((_p1 - _ip1) < (_p1 - _ip2)):
                                _m1 = _ip1
                                _m2 = _ip2
                            else:
                                _m1 = _ip2
                                _m2 = _ip1
                            _s1, _s2, _s3 = SplitManager.splitSegTwoPts(_seg, _m1, _m2)
                        elif ((_ip1 == _p1 or _ip1 == _p2) and
                              (_ip2 != _p1 and _ip2 != _p2)):
                            _s1, _s2 = split_segment(_seg, _ip2)
                        elif ((_ip2 == _p1 or _ip2 == _p2) and
                              (_ip1 != _p1 and _ip1 != _p2)):
                            _s1, _s2 = split_segment(_seg, _ip1)
                        else:
                            pass
                    else:
                        raise ValueError, "Unexpected count: %d" % _count
                    #
                    # if _a1 is not None the circle was split
                    #
                    if _a1 is not None:
                        _odict[_cid] = False
                        _alist.append(_a1)
                        if _a2 is not None:
                            _alist.append(_a2)
                    #
                    # if _s1 is not None the segment was split
                    #
                    if _s1 is not None:
                        _odict[_sid] = False
                        _segs.append(_s1)
                        if _s2 is not None:
                            _segs.append(_s2)
                        if _s3 is not None:
                            _segs.append(_s3)
                        break
        #
        # handle circles
        #
        _dcirc = []
        for _obj in _circs:
            _oid = id(_obj)
            _status = _odict.get(_oid)
            if _status is None:
                raise RuntimeError, "No status for Circle: " + `_obj`
            else:
                if not _status:
                    _dcirc.append(_obj)
        for _obj in _dcirc:
            self.delObject(_obj)
            del self.__rects[id(_obj)]
            _layer.delObject(_obj)
        #
        # handle arcs
        #
        for _obj in _alist:
            _layer.addObject(_obj)
            self.addObject(_obj)
        #
        # handle segments
        #
        _nseg = []
        _dseg = []
        for _obj in _slist:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Segment: " + `_obj`
            elif _status:
                _nseg.append(_obj)
            else:
                _dseg.append(_obj)
        for _obj in _dseg:
            del self.__rects[id(_obj)]
            if _obj.getParent() is not None:
                _layer.delObject(_obj)
            else:
                _obj.finish()
        for _obj in _nseg:
            if _obj.getParent() is None:
                _layer.addObject(_obj)
        self.__segs = _nseg

    def __splitSegArc(self):
        _segs = self.__segs
        _arcs = self.__arcs
        _layer = self.__layer
        _rects = self.__rects
        _slist = []
        _odict = {}
        while len(_segs):
            _seg = _segs.pop()
            _slist.append(_seg)
            _sid = id(_seg)
            if _sid in _odict and not _odict[_sid]:
                continue
            _p1, _p2 = _seg.getEndpoints()
            if (_p1.getParent() is not _layer or
                _p2.getParent() is not _layer):
                raise RuntimeError, "Invalid Segment endpoints: " + `_seg`
            _odict[_sid] = True
            _rs = _rects.get(_sid)
            if _rs is None:
                _rs = SplitManager.segBounds(_seg)
                _rects[_sid] = _rs
            for _arc in _arcs:
                _aid = id(_arc)
                if _aid in _odict and not _odict[_aid]:
                    continue
                _odict[_aid] = True
                _ra = _rects.get(_aid)
                if _ra is None:
                    _ra = _arc.getBounds()
                    _rects[_aid] = _ra
                if not SplitManager.canIntersect(_rs, _ra):
                    continue
                _ipts = intersections.find_intersections(_seg, _arc)
                if len(_ipts):
                    _s1 = _s2 = _s3 = _a1 = _a2 = _a3 = None
                    _p1, _p2 = _seg.getEndpoints()
                    _ep1, _ep2 = _arc.getEndpoints()
                    _count = len(_ipts)
                    if _count == 1:
                        _x, _y = _ipts[0]
                        _ip = self.__getPoint(_x, _y)
                        if _ip != _ep1 and _ip != _ep2:
                            _a1, _a2 = split_arc(_arc, _ip)
                        if _ip != _p1 and _ip != _p2:
                            _s1, _s2 = split_segment(_seg, _ip)
                    elif _count == 2:
                        _x, _y = _ipts[0]
                        _ip1 = self.__getPoint(_x, _y)
                        _x, _y = _ipts[1]
                        _ip2 = self.__getPoint(_x, _y)
                        if (_ip1 != _ep1 and
                            _ip1 != _ep2 and
                            _ip2 != _ep1 and
                            _ip2 != _ep2):
                            _a1, _a2, _a3 = SplitManager.splitArcTwoPts(_arc, _ip1, _ip2)
                        elif ((_ip1 == _ep1 or _ip1 == _ep2) and
                              (_ip2 != _ep1 and _ip2 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip2)
                        elif ((_ip2 == _ep1 or _ip2 == _ep2) and
                              (_ip1 != _ep1 and _ip1 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip1)
                        else:
                            pass
                        if (_ip1 != _p1 and
                            _ip1 != _p2 and
                            _ip2 != _p1 and
                            _ip2 != _p2):
                            if ((_p1 - _ip1) < (_p1 - _ip2)):
                                _m1 = _ip1
                                _m2 = _ip2
                            else:
                                _m1 = _ip2
                                _m2 = _ip1
                            _s1, _s2, _s3 = SplitManager.splitSegTwoPts(_seg, _m1, _m2)
                        elif ((_ip1 == _p1 or _ip1 == _p2) and
                              (_ip2 != _p1 and _ip2 != _p2)):
                            _s1, _s2 = split_segment(_seg, _ip2)
                        elif ((_ip2 == _p1 or _ip2 == _p2) and
                              (_ip1 != _p1 and _ip1 != _p2)):
                            _s1, _s2 = split_segment(_seg, _ip1)
                        else:
                            pass
                    else:
                        raise ValueError, "Unexpected count: %d" % _count
                    #
                    # if _a1 is not None the arc was split
                    #
                    if _a1 is not None:
                        _odict[_aid] = False
                        _arcs.append(_a1)
                        if _a2 is not None:
                            _arcs.append(_a2)
                        if _a3 is not None:
                            _arcs.append(_a3)
                    #
                    # if _s1 is not None the segment was split
                    #
                    if _s1 is not None:
                        _odict[_sid] = False
                        _segs.append(_s1)
                        if _s2 is not None:
                            _segs.append(_s2)
                        if _s3 is not None:
                            _segs.append(_s3)
                        break
        #
        # handle arcs
        #
        _narc = []
        _darc = []
        for _obj in _arcs:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Arc: " + `_obj`
            elif _status:
                _narc.append(_obj)
            else:
                _darc.append(_obj)
        for _obj in _darc:
            del self.__rects[id(_obj)]
            if _obj.getParent() is not None:
                _layer.delObject(_obj)
            else:
                _obj.finish()
        for _obj in _narc:
            if _obj.getParent() is None:
                _layer.addObject(_obj)
        self.__arcs = _narc
        #
        # handle segments
        #
        _nseg = []
        _dseg = []
        for _obj in _slist:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Segment: " + `_obj`
            elif _status:
                _nseg.append(_obj)
            else:
                _dseg.append(_obj)
        for _obj in _dseg:
            del self.__rects[id(_obj)]
            if _obj.getParent() is not None:
                _layer.delObject(_obj)
            else:
                _obj.finish()
        for _obj in _nseg:
            if _obj.getParent() is None:
                _layer.addObject(_obj)
        self.__segs = _nseg

    def __splitSegPolyline(self):
        _segs = self.__segs
        _plines = self.__plines
        _layer = self.__layer
        _rects = self.__rects
        _slist = []
        _odict = {}
        while len(_segs):
            _seg = _segs.pop()
            _slist.append(_seg)
            _sid = id(_seg)
            if _sid in _odict and not _odict[_sid]:
                continue
            _p1, _p2 = _seg.getEndpoints()
            if (_p1.getParent() is not _layer or
                _p2.getParent() is not _layer):
                raise RuntimeError, "Invalid Segment endpoints: " + `_seg`
            _odict[_sid] = True
            _rs = _rects.get(_sid)
            if _rs is None:
                _rs = SplitManager.segBounds(_seg)
                _rects[_sid] = _rs
            _ip = None
            for _pl in _plines:
                _pid = id(_pl)
                _rp = _rects.get(_pid)
                if _rp is None:
                    _rp = _pl.getBounds()
                    _rects[_pid] = _rp
                if not SplitManager.canIntersect(_rs, _rp):
                    continue
                _pts = _pl.getPoints()
                _i = 0
                while (_i < (len(_pts) - 1)):
                    _lp1 = _pts[_i]
                    _lp2 = _pts[_i + 1]
                    if (_p1 == _lp1 or
                        _p1 == _lp2 or
                        _p2 == _lp1 or
                        _p2 == _lp2):
                        _i = _i + 1
                        continue
                    _ts = Segment(_lp1, _lp2)
                    _ipts = intersections.find_intersections(_seg, _ts)
                    _ts.finish()
                    if len(_ipts):
                        _count = len(_ipts)
                        if _count == 1:
                            _x, _y = _ipts[0]
                            _ip = self.__getPoint(_x, _y)
                            _pl.addPoint((_i + 1), _ip)
                            _pts = _pl.getPoints()
                            if _ip != _p1 and _ip != _p2:
                                _s1, _s2 = split_segment(_seg, _ip)
                                _odict[_sid] = False
                                _segs.append(_s1)
                                _segs.append(_s2)
                            else:
                                _ip = None
                        else:
                            raise ValueError, "Unexpected count: %d" % _count
                    _i = _i + 1
                    if _ip is not None:
                        break
                if _ip is not None:
                    break
        #
        # handle segments
        #
        _nseg = []
        _dseg = []
        for _obj in _slist:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Segment: " + `_obj`
            elif _status:
                _nseg.append(_obj)
            else:
                _dseg.append(_obj)
        for _obj in _dseg:
            del self.__rects[id(_obj)]
            if _obj.getParent() is not None:
                _layer.delObject(_obj)
            else:
                _obj.finish()
        for _obj in _nseg:
            if _obj.getParent() is None:
                _layer.addObject(_obj)
        self.__segs = _nseg

    def __splitCircCirc(self):
        _layer = self.__layer
        _circs = self.__circs
        _rects = self.__rects
        _olist = []
        _cdict = {}
        while len(_circs):
            _circ = _circs.pop()
            _olist.append(_circ)
            _circid = id(_circ)
            if _circid in _cdict and not _cdict[_circid]:
                continue
            _cdict[_circid] = True
            _rcirc = _rects.get(_circid)
            if _rcirc is None:
                _rcirc = SplitManager.circBounds(_circ)
                _rects[_circid] = _rcirc
            for _c in _circs:
                _cid = id(_c)
                if _cid in _cdict and not _cdict[_cid]:
                    continue
                _rc = _rects.get(_cid)
                if _rc is None:
                    _rc = SplitManager.circBounds(_c)
                    _rects[_cid] = _rc
                if not SplitManager.canIntersect(_rcirc, _rc):
                    continue
                _ipts = intersections.find_intersections(_c, _circ)
                if len(_ipts):
                    _count = len(_ipts)
                    if _count == 1:
                        _x, _y = _ipts[0]
                        _ip = self.__getPoint(_x, _y)
                        _arc = split_circle(_circ, _ip)
                        _olist.append(_arc)
                        _cdict[_circid] = False
                        _arc = split_circle(_c, _ip)
                        _olist.append(_arc)
                        _cdict[_cid] = False
                    elif _count == 2:
                        _x, _y = _ipts[0]
                        _ip1 = self.__getPoint(_x, _y)
                        _x, _y = _ipts[1]
                        _ip2 = self.__getPoint(_x, _y)
                        _arc1, _arc2 = SplitManager.splitCircTwoPts(_circ, _ip1, _ip2)
                        _cdict[_circid] = False
                        _olist.append(_arc1)
                        _olist.append(_arc2)
                        _arc1, _arc2 = SplitManager.splitCircTwoPts(_c, _ip1, _ip2)
                        _olist.append(_arc1)
                        _olist.append(_arc2)
                        _cdict[_cid] = False
                    else:
                        raise ValueError, "Unexpected count: %d" % _count
                    break
        _alist = []
        _dlist = []
        for _obj in _olist:
            _status = _cdict.get(id(_obj))
            if _status is None:
                _alist.append(_obj)
            elif _status:
                _circs.append(_obj)
            else:
                _dlist.append(_obj)
        for _obj in _dlist:
            self.delObject(_obj)
            del self.__rects[id(_obj)]
            _layer.delObject(_obj)
        for _obj in _alist:
            _layer.addObject(_obj)
            self.addObject(_obj)

    def __splitCircArc(self):
        _layer = self.__layer
        _circs = self.__circs
        _arcs = self.__arcs
        _rects = self.__rects
        _clist = []
        _odict = {}
        while len(_circs):
            _circ = _circs.pop()
            _clist.append(_circ)
            _circid = id(_circ)
            if _circid in _odict and not _odict[_circid]:
                continue
            _odict[_circid] = True
            _rcirc = _rects.get(_circid)
            if _rcirc is None:
                _rcirc = SplitManager.circBounds(_circ)
                _rects[_circid] = _rcirc
            for _arc in _arcs:
                _arcid = id(_arc)
                if _arcid in _odict and not _odict[_arcid]:
                    continue
                _odict[_arcid] = True
                _rarc = _rects.get(_arcid)
                if _rarc is None:
                    _rarc = _arc.getBounds()
                    _rects[_arcid] = _rarc
                if not SplitManager.canIntersect(_rcirc, _rarc):
                    continue
                _ipts = intersections.find_intersections(_circ, _arc)
                if len(_ipts):
                    _ep1, _ep2 = _arc.getEndpoints()
                    _ca1 = _ca2 = _a1 = _a2 = _a3 = None
                    _count = len(_ipts)
                    if _count == 1:
                        _x, _y = _ipts[0]
                        _ip = self.__getPoint(_x, _y)
                        _ca1 = split_circle(_circ, _ip)
                        if _ip != _ep1 and _ip != _ep2:
                            _a1, _a2 = split_arc(_arc, _ip)
                    elif _count == 2:
                        _x, _y = _ipts[0]
                        _ip1 = self.__getPoint(_x, _y)
                        _x, _y = _ipts[1]
                        _ip2 = self.__getPoint(_x, _y)
                        _ca1, _ca2 = SplitManager.splitCircTwoPts(_circ, _ip1, _ip2)
                        if (_ip1 != _ep1 and
                            _ip1 != _ep2 and
                            _ip2 != _ep1 and
                            _ip2 != _ep2):
                            _a1, _a2, _a3 = SplitManager.splitArcTwoPts(_arc, _ip1, _ip2)
                        elif ((_ip1 == _ep1 or _ip1 == _ep2) and
                              (_ip2 != _ep1 and _ip2 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip2)
                        elif ((_ip2 == _ep1 or _ip2 == _ep2) and
                              (_ip1 !=_ep1 and _ip1 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip1)
                        else:
                            pass
                    else:
                        raise ValueError, "Unexpected count: %d" % _count
                    #
                    # if _a1 is not None then the arc was split
                    #
                    if _a1 is not None:
                        _odict[_arcid] = False
                        _arcs.append(_a1)
                        if _a2 is not None:
                            _arcs.append(_a2)
                        if _a3 is not None:
                            _arcs.append(_a3)
                    #
                    # if _ca1 is not none then the circle was split
                    #
                    if _ca1 is not None:
                        _odict[_circid] = False
                        _arcs.append(_ca1)
                        if _ca2 is not None:
                            _arcs.append(_ca2)
                        break
        #
        # handle circles
        #
        _dlist = []
        for _obj in _clist:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Circle: " + `_obj`
            elif _status:
                _circs.append(_obj)
            else:
                _dlist.append(_obj)
        for _obj in _dlist:
            self.delObject(_obj)
            del self.__rects[id(_obj)]
            _layer.delObject(_obj)
        #
        # handle arcs
        #
        _narc = []
        _darc = []
        for _obj in _arcs:
            _status = _odict.get(id(_obj))
            #
            # states:
            # None - Arc untested - created during split of final circle
            # True - Arc survived all split attempts
            # False - Arc was split
            #
            if _status is None or _status:
                _narc.append(_obj)
            else:
                _darc.append(_obj)
        for _obj in _darc:
            del self.__rects[id(_obj)]
            if _obj.getParent() is not None:
                _layer.delObject(_obj)
            else:
                _obj.finish()
        for _obj in _narc:
            if _obj.getParent() is None:
                _layer.addObject(_obj)
        self.__arcs = _narc

    def __splitCircPolyline(self):
        _circs = self.__circs
        _plines = self.__plines
        _layer = self.__layer
        _rects = self.__rects
        _alist = []
        _clist = []
        _odict = {}
        while len(_circs):
            _circ = _circs.pop()
            _clist.append(_circ)
            _circid = id(_circ)
            if _circid in _odict and not _odict[_circid]:
                continue
            _odict[_circid] = True
            _rcirc = _rects.get(_circid)
            if _rcirc is None:
                _rcirc = SplitManager.circBounds(_circ)
                _rects[_circid] = _rcirc
            _hit = False                
            for _pl in _plines:
                _pid = id(_pl)
                _rp = _rects.get(_pid)
                if _rp is None:
                    _rp = _pl.getBounds()
                    _rects[_pid] = _rp
                if not SplitManager.canIntersect(_rcirc, _rp):
                    continue
                _pts = _pl.getPoints()
                for _i in range(len(_pts) - 1):
                    _lp1 = _pts[_i]
                    _lp2 = _pts[_i + 1]
                    _seg = Segment(_lp1, _lp2)
                    _ipts = intersections.find_intersections(_circ, _seg)
                    _seg.finish()
                    if len(_ipts):
                        _a1 = _a2 = None
                        _count = len(_ipts)
                        if _count == 1:
                            _x, _y = _ipts[0]
                            _ip = self.__getPoint(_x, _y)
                            _a1 = split_circle(_circ, _ip)
                            if _ip != _lp1 and _ip != _lp2:
                                _pl.addPoint((_i + 1), _ip)
                        elif _count == 2:
                            _x, _y = _ipts[0]
                            _ip1 = self.__getPoint(_x, _y)
                            _x, _y = _ipts[1]
                            _ip2 = self.__getPoint(_x, _y)
                            _a1, _a2 = SplitManager.splitCircTwoPts(_circ, _ip1, _ip2)
                            if (_ip1 - _lp1) < (_ip2 - _lp1):
                                _p1 = _ip1
                                _p2 = _ip2
                            else:
                                _p1 = _ip2
                                _p2 = _ip1
                            if _p1 != _lp1 and _p1 != _lp2:
                                _pl.addPoint((_i + 1), _p1)
                                _i = _i + 1
                            if _p2 != _lp1 and _p2 != _lp2:
                                _pl.addPoint((_i + 1), _p2)
                        else:
                            raise ValueError, "Unexpected count: %d" % _count
                        #
                        # if _a1 is not None the circle was split
                        #
                        if _a1 is not None:
                            _odict[_circid] = False
                            _alist.append(_a1)
                            if _a2 is not None:
                                _alist.append(_a2)
                            _hit = True
                            break
                if _hit:
                    break
        #
        # handle circles
        #
        _dlist = []
        for _obj in _clist:
            _status = _odict.get(id(_obj))
            if _status is None:
                raise RuntimeError, "No status for Circle: " + `_obj`
            elif _status:
                _circs.append(_obj)
            else:
                _dlist.append(_obj)
        for _obj in _dlist:
            self.delObject(_obj)
            del self.__rects[id(_obj)]
            _layer.delObject(_obj)
        #
        # handle arcs
        #
        for _obj in _alist:
            _layer.addObject(_obj)
            self.addObject(_obj)

    def __splitArcArc(self):
        _arcs = self.__arcs
        _layer = self.__layer
        _rects = self.__rects
        _alist = []
        _adict = {}
        while len(_arcs):
            _arc = _arcs.pop()
            _alist.append(_arc)
            _arcid = id(_arc)
            if _arcid in _adict and not _adict[_arcid]:
                continue
            _adict[_arcid] = True
            _rarc = _rects.get(_arcid)
            if _rarc is None:
                _rarc = _arc.getBounds()
                _rects[_arcid] = _rarc
            _ep1, _ep2 = _arc.getEndpoints()
            for _a in _arcs:
                _aid = id(_a)
                if _aid in _adict and not _adict[_aid]:
                    continue
                _ra = _rects.get(_aid)
                if _ra is None:
                    _ra = _a.getBounds()
                    _rects[_aid] = _ra
                if not SplitManager.canIntersect(_rarc, _ra):
                    continue
                _ep3, _ep4 = _a.getEndpoints()
                _ipts = intersections.find_intersections(_arc, _a)
                if len(_ipts):
                    _a1 = _a2 = _a3 = _a4 = _a5 = _a6 = None
                    _count = len(_ipts)
                    if _count == 1:
                        _x, _y = _ipts[0]
                        _ip = self.__getPoint(_x, _y)
                        if _ip != _ep1 and _ip != _ep2:
                            _a1, _a2 = split_arc(_arc, _ip)
                        if _ip != _ep3 and _ip != _ep4:
                            _a4, _a5 = split_arc(_a, _ip)
                    elif _count == 2:
                        _x, _y = _ipts[0]
                        _ip1 = self.__getPoint(_x, _y)
                        _x, _y = _ipts[1]
                        _ip2 = self.__getPoint(_x, _y)
                        if (_ip1 != _ep1 and
                            _ip1 != _ep2 and
                            _ip2 != _ep1 and
                            _ip2 != _ep2):
                            _a1, _a2, _a3 = SplitManager.splitArcTwoPts(_arc, _ip1, _ip2)
                        elif ((_ip1 == _ep1 or _ip1 == _ep2) and
                              (_ip2 != _ep1 and _ip2 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip2)
                        elif ((_ip2 == _ep1 or _ip2 == _ep2) and
                              (_ip1 != _ep1 and _ip1 != _ep2)):
                            _a1, _a2 = split_arc(_arc, _ip1)
                        else:
                            pass
                        if (_ip1 != _ep3 and
                            _ip1 != _ep4 and
                            _ip2 != _ep3 and
                            _ip2 != _ep4):
                            _a4, _a5, _a6 = SplitManager.splitArcTwoPts(_a, _ip1, _ip2)
                        elif ((_ip1 == _ep3 or _ip1 == _ep4) and
                              (_ip2 != _ep3 and _ip2 != _ep4)):
                            _a4, _a5 = split_arc(_a, _ip2)
                        elif ((_ip2 == _ep3 or _ip2 == _ep4) and
                              (_ip1 != _ep3 and _ip1 != _ep4)):
                            _a4, _a5 = split_arc(_a, _ip1)
                        else:
                            pass
                    else:
                        raise ValueError, "Unexpected count: %d" % _count
                    #
                    # if _a4 is not None then _a was split
                    #
                    if _a4 is not None:
                        _adict[_aid] = False
                        _arcs.append(_a4)
                        if _a5 is not None:
                            _arcs.append(_a5)
                        if _a6 is not None:
                            _arcs.append(_a6)
                    #
                    # if _a1 is not None then _arc was split
                    #
                    if _a1 is not None:
                        _adict[_arcid] = False
                        _arcs.append(_a1)
                        if _a2 is not None:
                            _arcs.append(_a2)
                        if _a3 is not None:
                            _arcs.append(_a3)
                        break
        _narc = []
        _darc = []
        for _arc in _alist:
            _status = _adict.get(id(_arc))
            if _status is None:
                raise RuntimeError, "No status for Arc: " + `_arc`
            elif _status:
                _narc.append(_arc)
            else:
                _darc.append(_arc)
        for _arc in _darc:
            del self.__rects[id(_arc)]
            if _arc.getParent() is not None:
                _layer.delObject(_arc)
            else:
                _arc.finish()
        for _arc in _narc:
            if _arc.getParent() is None:
                _layer.addObject(_arc)
        self.__arcs = _narc

    def __splitArcPolyline(self):
        _arcs = self.__arcs
        _plines = self.__plines
        _layer = self.__layer
        _rects = self.__rects
        _alist = []
        _adict = {}
        while len(_arcs):
            _arc = _arcs.pop()
            _alist.append(_arc)
            _arcid = id(_arc)
            if _arcid in _adict and not _adict[_arcid]:
                continue
            _adict[_arcid] = True
            _rarc = _rects.get(_arcid)
            if _rarc is None:
                _rarc = _arc.getBounds()
                _rects[_arcid] = _rarc
            _ep1, _ep2 = _arc.getEndpoints()
            _hit = False
            for _pl in _plines:
                _pid = id(_pl)
                _rp = _rects.get(_pid)
                if _rp is None:
                    _rp = _pl.getBounds()
                    _rects[_pid] = _rp
                if not SplitManager.canIntersect(_rarc, _rp):
                    continue
                _pts = _pl.getPoints()
                for _i in range(len(_pts) - 1):
                    _lp1 = _pts[_i]
                    _lp2 = _pts[_i + 1]
                    _seg = Segment(_lp1, _lp2)
                    _ipts = intersections.find_intersections(_arc, _seg)
                    _seg.finish()
                    if len(_ipts):
                        _a1 = _a2 = _a3 = None
                        _count = len(_ipts)
                        if _count == 1:
                            _x, _y = _ipts[0]
                            _ip = self.__getPoint(_x, _y)
                            if _ip != _ep1 and _ip != _ep2:
                                _a1, _a2 = split_arc(_arc, _ip)
                            if _ip != _lp1 and _ip != _lp2:
                                _pl.addPoint((_i + 1), _ip)
                        elif _count == 2:
                            _x, _y = _ipts[0]
                            _ip1 = self.__getPoint(_x, _y)
                            _x, _y = _ipts[1]
                            _ip2 = self.__getPoint(_x, _y)
                            if (_ip1 != _ep1 and
                                _ip1 != _ep2 and
                                _ip2 != _ep1 and
                                _ip2 != _ep2):
                                _a1, _a2, _a3 = SplitManager.splitArcTwoPts(_arc, _ip1, _ip2)
                            elif ((_ip1 == _ep1 or _ip1 == _ep2) and
                                  (_ip2 != _ep1 and _ip2 != _ep2)):
                                _a1, _a2 = split_arc(_arc, _ip2)
                            elif ((_ip2 == _ep1 or _ip2 == _ep2) and
                                  (_ip1 != _ep1 and _ip1 != _ep2)):
                                _a1, _a2 = split_arc(_arc, _ip1)
                            else:
                                pass
                            if (_lp1 - _ip1) < (_lp1 -_ip2):
                                _p1 = _ip1
                                _p2 = _ip2
                            else:
                                _p1 = _ip2
                                _p2 = _ip1
                            if _p1 != _lp1 and _p1 != _lp2:
                                _pl.addPoint((_i + 1), _p1)
                                _i = _i + 1
                            if _p2 != _lp1 and _p2 != _lp2:
                                _pl.addPoint((_i + 1), _p2)
                        else:
                            raise ValueError, "Unexpected count: %d" % _count
                        #
                        # if _a1 is not None then _arc was split
                        #
                        if _a1 is not None:
                            _hit = True
                            _adict[_arcid] = False
                            _arcs.append(_a1)
                            if _a2 is not None:
                                _arcs.append(_a2)
                            if _a3 is not None:
                                _arcs.append(_a3)
                    if _hit:
                        break
                if _hit:
                    break
        _narc = []
        _darc = []
        for _arc in _alist:
            _status = _adict.get(id(_arc))
            if _status is None:
                raise RuntimeError, "No status for Arc: " + `_arc`
            elif _status:
                _narc.append(_arc)
            else:
                _darc.append(_arc)
        for _arc in _darc:
            del self.__rects[id(_arc)]
            if _arc.getParent() is not None:
                _layer.delObject(_arc)
            else:
                _arc.finish()
        for _arc in _narc:
            if _arc.getParent() is None:
                _layer.addObject(_arc)
        self.__arcs = _narc

    def __splitPolyPoly(self):
        _plines = self.__plines
        _rects = self.__rects
        _pdict = {}
        _zero = (0.0 - 1e-10)
        _one = (1.0 + 1e-10)
        while len(_plines):
            _pl = _plines.pop()
            _plid = id(_pl)
            if _plid in _pdict and not _pdict[_plid]:
                continue
            _pdict[_plid] = True
            _rpl = _rects.get(_plid)
            if _rpl is None:
                _rpl = _pl.getBounds()
                _rects[_plid] = _rpl
            _maxi = len(_pl) - 1
            _ip = None
            for _p in _plines:
                _pid = id(_p)
                if _pid in _pdict and not _pdict[_pid]:
                    continue
                _rp = _rects.get(_pid)
                if _rp is None:
                    _rp = _p.getBounds()
                    _rects[_pid] = _rp
                if not SplitManager.canIntersect(_rpl, _rp):
                    continue
                for _i in range(_maxi):
                    _p1 = _pl.getPoint(_i)
                    _p2 = _pl.getPoint(_i + 1)
                    _x1, _y1 = _p1.getCoords()
                    _x2, _y2 = _p2.getCoords()
                    _maxj = len(_p) - 1
                    for _j in range(_maxj):
                        _p3 = _p.getPoint(_j)
                        _p4 = _p.getPoint(_j + 1)
                        if (_p1 == _p3 or
                            _p1 == _p4 or
                            _p2 == _p3 or
                            _p2 == _p4):
                            continue
                        _d = intersections.denom(_p1, _p2, _p3, _p4)
                        if abs(_d) > 1e-10: # NOT parallel
                            _r = intersections.rnum(_p1, _p2, _p3, _p4)/_d
                            _s = intersections.snum(_p1, _p2, _p3 ,_p4)/_d
                            if (not (_r < _zero or _r > _one) and
                                not (_s < _zero or _s > _one)):
                                _xi = _x1 + _r * (_x2 - _x1)
                                _yi = _y1 + _r * (_y2 - _y1)
                                _ip = self.__getPoint(_xi, _yi)
                                _pl.addPoint((_i + 1), _ip)
                                _p.addPoint((_j + 1), _ip)
                        if _ip is not None:
                            break
                    if _ip is not None:
                        break
                if _ip is not None:
                    break
            if _ip is not None:
                _plines.append(_pl)

def split_objects(objlist):
    """Split a list of objects at their intersection points.

split_objects(objlist):

objlist: A list or tuple of objects to split
    """
    if not isinstance(objlist, (list, tuple)):
        raise TypeError, "Invalid object list/tuple: " + `type(objlist)`
    _ldict = {}
    for _obj in objlist:
        _layer = _obj.getParent()
        if _layer is not None:
            _mgr = _ldict.setdefault(id(_layer), SplitManager(_layer))
            _mgr.addObject(_obj)
    for _mgr in _ldict.values():
        _mgr.splitObjects()
