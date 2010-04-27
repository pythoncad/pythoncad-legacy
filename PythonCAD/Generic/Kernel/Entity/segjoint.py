#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# code for chamfer and fillet objects
#

from math import hypot, pi, sin, cos, tan, atan2

from geometricalentity                      import *
from Generic.Kernel.Entity.util             import *
from Generic.Kernel.intersection            import *
from Generic.Kernel.Entity.segment          import Segment

_dtr = 180.0/pi

class SegJoint(GeometricalEntityComposed):
    """
        A base class for chamfers and fillets
        A SegJoint object has the following methods:
    """
    #
    # The default style for the Segjoint class
    #
    __defstyle = None
    
    def __init__(self, s1, s2):
        if not isinstance(s1, Segment):
            raise TypeError, "Invalid first Segment for SegJoint: " + `type(s1)`
        if not isinstance(s2, Segment):
            raise TypeError, "Invalid second Segment for SegJoint: " + `type(s2)`
        self.__s1 = s1
        self.__s2 = s2
        self.__xi = None # segment intersection x-coordinate
        self.__yi = None # segment intersection y-coordinate
        self.__s1_float = None # s1 endpoint at joint
        self.__s1_fixed = None # s1 other endpoint
        self.__s2_float = None # s2 endpoint at joint
        self.__s2_fixed = None # s2 other endpoint

    def getConstructionElements(self):
        """
            Return the two segments joined by the SegJoint.
            This method returns a tuple holding the two segments joined
            by the SegJoint.
        """
        return self.__s1, self.__s2
        
    def getReletedComponent(self):
        """
            return the releted component 
        """
        return self.__s1, self.__s2
        
    def getMovingPoints(self):
        """
            Return the joined segment points used by the SegJoint.
            This method returns a tuple of two points, the first point is the
            used point on the SegJoint initial segment, and the second point
            is the used point on the SegJoint secondary segment.
        """
        return self.__s1_float, self.__s2_float

    def getFixedPoints(self):
        """
            Return the joined segment points not used by the SegJoint.
            This method returns a tuple of two points, the first point is the
            unused point on the SegJoint initial segment, and the second point
            is the unused point on the SegJoint secondary segment.
        """
        return self.__s1_fixed, self.__s2_fixed

    def getIntersection(self):
        """
            Return the intersection points of the SegJoint segments.

            This method returns a tuple of two floats; the first is the
            intersection 'x' coordinate, and the second is the 'y' coordinate.
        """
        return self.__xi, self.__yi

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not a segjoint exists with a region.
            The four arguments define the boundary of an area, and the
            function returns True if the joint lies within that area.
            Otherwise, the function returns False.
        """
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        test_boolean(fully)
        _mp1, _mp2 = self.getMovingPoints()
        _mx1, _my1 = _mp1.getCoords()
        _mx2, _my2 = _mp2.getCoords()
        _fxmin = min(_mx1, _mx2)
        _fymin = min(_my1, _my2)
        _fxmax = max(_mx1, _mx2)
        _fymax = max(_my1, _my2)
        if ((_fxmax < _xmin) or
            (_fymax < _ymin) or
            (_fxmin > _xmax) or
            (_fymin > _ymax)):
            return False
        if fully:
            if ((_fxmin > _xmin) and
                (_fymin > _ymin) and
                (_fxmax < _xmax) and
                (_fymax < _ymax)):
                return True
            return False
        return in_region(_mx1, _my1, _mx2, _my2,
                              _xmin, _ymin, _xmax, _ymax)


class Chamfer(SegJoint):
    """
        A Chamfer class

        A chamfer is a small distance taken off a sharp
        corner in a drawing. For the chamfer to be valid,
        the chamfer length must be less than the length of
        either segment, and the two segments must be extendable
        so they could share a common endpoint.

        A Chamfer is derived from a SegJoint, so it shares all
        the methods and attributes of that class. A Chamfer has
        the following additional methods:
        A Chamfer has the following attributes:

        length: The Chamfer length.
    """
    
    def __init__(self, s1, s2, l):
    
        _len = get_float(l)
        if _len < 0.0:
            raise ValueError, "Invalid chamfer length: %g" % _len
        if _len > s1.length():
            raise ValueError, "Chamfer is longer than first Segment."
        if _len > s2.length():
            raise ValueError, "Chamfer is longer than second Segment."
        _xi, _yi = getIntersection(self)
        SegJoint.__init__(self, s1, s2)
        # print "xi: %g; yi: %g" % (_xi, _yi)
        _xp, _yp = _sp1.getCoords()
        _sep = hypot((_yp - _yi), (_xp - _xi))
        if _sep > (_len + 1e-10):
            # print "sep: %g" % _sep
            # print "xp: %g; yp: %g" % (_xp, _yp)
            raise ValueError, "First segment too far from intersection point."
        _xp, _yp = _sp2.getCoords()
        _sep = hypot((_yp - _yi), (_xp - _xi))
        if _sep > (_len + 1e-10):
            # print "sep: %g" % _sep
            # print "xp: %g; yp: %g" % (_xp, _yp)
            raise ValueError, "Second segment too far from intersection point."
        self.__length = _len
        
    def __eq__(self, obj):
        if not isinstance(obj, Chamfer):
            return False
        if obj is self:
            return True
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 == _os1 and _s2 == _os2) or
                 (_s1 == _os2 and _s2 == _os1)) and
                abs(self.__length - obj.getLength()) < 1e-10)

    def __ne__(self, obj):
        if not isinstance(obj, Chamfer):
            return True
        if obj is self:
            return False
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 != _os1 or _s2 == _os2) and
                 (_s1 != _os2 or _s2 == _os1)) or
                abs(self.__length - obj.getLength()) > 1e-10)

    def getConstructionElements(self):
        """
            retutn the construction element of the object
        """
        return self.__s1 , self.__s2 , self.__length

    def getLength(self):
        """
            Return the Chamfer length.
        """
        return self.__length

    def setLength(self, l):
        """
            Set the Chamfer length.
            The length should be a positive float value.
        """
        _s1, _s2 = self.getSegments()        
        _l = get_float(l)
        if _l < 0.0:
            raise ValueError, "Invalid chamfer length: %g" % _l
        if _l > _s1.length():
            raise ValueError, "Chamfer is larger than first Segment."
        if _l > _s2.length():
            raise ValueError, "Chamfer is larger than second Segment."
        _ol = self.__length
        if abs(_l - _ol) > 1e-10:
            self.__length = _l


    length = property(getLength, setLength, None, "Chamfer length.")
    def _moveSegmentPoints(self, dist):
        """
            Set the Chamfer endpoints at the correct location
            The argument 'dist' is the chamfer length. This method is private
            the the Chamfer object.
        """
        _d = util.get_float(dist)
        #
        # process segment 1
        #
        _xi, _yi = self.getIntersection()
        # print "xi: %g; yi: %g" % (xi, yi)
        _mp1, _mp2 = self.getMovingPoints()
        _sp1, _sp2 = self.getFixedPoints()
        _sx, _sy = _sp1.getCoords()
        _slen = hypot((_yi - _sy), (_xi - _sx))
        # print "slen: %g" % slen
        _newlen = (_slen - _d)/_slen
        # print "newlen: %g" % _newlen
        _xs, _ys = _sp1.getCoords()
        _xm, _ym = _mp1.getCoords()
        _xn = _xs + _newlen * (_xi - _xs)
        _yn = _ys + _newlen * (_yi - _ys)
        # print "xn: %g; yn: %g" % (_xn, _yn)
        _mp1.setCoords(_xn, _yn)
        #
        # process segment 2
        #
        _sx, _sy = _sp2.getCoords()
        _slen = hypot((_yi - _sy), (_xi - _sx))
        # print "slen: %g" % _slen
        _newlen = (_slen - _d)/_slen
        # print "newlen: %g" % _newlen
        _xs, _ys = _sp2.getCoords()
        _xm, _ym = _mp2.getCoords()
        _xn = _xs + _newlen * (_xi - _xs)
        _yn = _ys + _newlen * (_yi - _ys)
        # print "xn: %g; yn: %g" % (_xn, _yn)
        _mp2.setCoords(_xn, _yn)
        
    def clone(self):
        _s1, _s2 = self.getSegments()
        _l = self.__length
        _s = self.getStyle()
        _ch = Chamfer(_s1, _s2, _l, _s)
        _ch.setColor(self.getColor())
        _ch.setLinetype(self.getLinetype())
        _ch.setThickness(self.getThickness())
        return _ch


class Fillet(SegJoint):
    """
        A fillet is a curved joining of two segments. For a filleted
        joint to be valid, the radius must fall within some distance
        determined by the segment endpoints and segment intersection
        point, and the two segments must be extendable so they can
        share a common endpoint.
        A Fillet is derived from a SegJoint, so it shares the methods
        and attributes of that class. 
    """
    
    def __init__(self, s1, s2, r):
        SegJoint.__init__(s1, s2)
        _r = get_float(r)
        if _r < 0.0:
            raise ValueError, "Invalid fillet radius: %g" % _r
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        self.__radius = _r
        self.__center = (0.0, 0.0)
        self._calculateCenter()

    def __eq__(self, obj):
        if not isinstance(obj, Fillet):
            return False
        if obj is self:
            return True
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 == _os1 and _s2 == _os2) or
                 (_s1 == _os2 and _s2 == _os1)) and
                abs(self.__radius - obj.getRadius()) < 1e-10)

    def __ne__(self, obj):
        if not isinstance(obj, Fillet):
            return True
        if obj is self:
            return False
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 != _os1 or _s2 != _os2) and
                 (_s1 != _os2 or _s2 != _os1)) or
                abs(self.__radius - obj.getRadius()) > 1e-10)
        
    def getConstructionElements(self):
        """
            retutn the construction element of the object
        """
        return self.__s1 , self.__s2 , self.__radius

    def getRadius(self):
        """
            Return the Fillet radius.
        """
        return self.__radius

    def setRadius(self, r):
        """
            Set the Fillet radius.
            The radius should be a positive float value.
        """
        _s1, _s2 = self.getSegments()        
        _r = get_float(r)
        if _r < 0.0:
            raise ValueError, "Invalid fillet radius: %g" % _r
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        _or = self.__radius
        if abs(_r - _or) > 1e-10:
            self.__radius = _r
            self._calculateCenter()
            self._moveSegmentPoints()

    radius = property(getRadius, setRadius, None, "Chamfer radius.")

    def _calculateCenter(self):
        """
            Find the center point of the radius
            This method is private to the Fillet object.
        """
        _r = self.__radius
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _as1 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) # _as1 in radians
        _as2 = atan2((_p4.y - _p3.y), (_p4.x - _p3.x)) # _as2 in radians
        if abs(abs(_as1) - pi) < 1e-10:
            if _as1 > 0.0 and _as2 < 0.0:
                _as1 = -pi
            if _as1 < 0.0 and _as2 > 0.0:
                _as1 = pi
        if abs(abs(_as2) - pi) < 1e-10:
            if _as2 > 0.0 and _as2 < 0.0:
                _as2 = -pi
            if _as2 < 0.0 and _as1 > 0.0:
                _as2 = pi
        _acl = (_as1 + _as2)/2.0
        _acc = abs(_as1 - _as2)/2.0
        if (_as1 > 0.0 and _as2 < 0.0) or (_as1 < 0.0 and _as2 > 0.0):
            _amin = min(_as1, _as2)
            _amax = max(_as1, _as2)
            #print "_amax: %g" % _amax
            #print "_amin: %g" % _amin
            if _amax - _amin > pi: # radians
                if _acl < 0.0:
                    _acl = _acl + pi
                else:
                    _acl = _acl - pi
                _acc = ((pi - _amax) + (_amin + pi))/2.0
        #print "_acl: %g" % (_acl * _dtr)
        #print "_acc: %g" % (_acc * _dtr)
        _rc = hypot((_r/tan(_acc)), _r)
        #print "_rc: %g" % _rc
        _xi, _yi = self.getIntersection()
        _xc = _xi + _rc * cos(_acl)
        _yc = _yi + _rc * sin(_acl)
        self.__center = (_xc, _yc)
        #print "center: %s" % str(self.__center)

    def getCenter(self):
        """
            Return the center location of the Fillet.
            This method returns a tuple of two floats; the first is the
            center 'x' coordinate, the second is the 'y' coordinate.
        """
        return self.__center

    def _calculateLimits(self):
        """
            Determine the radial limits of the fillet.
            This method is private to the Fillet.
        """
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _as1 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) # radians
        _as2 = atan2((_p4.y - _p3.y), (_p4.x - _p3.x)) # radians
        if abs(abs(_as1) - pi) < 1e-10:
            if _as1 > 0.0 and _as2 < 0.0:
                _as1 = -pi
            if _as1 < 0.0 and _as2 > 0.0:
                _as1 = pi
        if abs(abs(_as2) - pi) < 1e-10:
            if _as2 > 0.0 and _as2 < 0.0:
                _as2 = -pi
            if _as2 < 0.0 and _as1 > 0.0:
                _as2 = pi
        #print "_as1: %g" % (_as1 * _dtr)
        #print "_as2: %g" % (_as2 * _dtr)
        _acl = (_as1 + _as2)/2.0
        _acc = abs(_as1 - _as2)/2.0
        if (_as1 > 0.0 and _as2 < 0.0) or (_as1 < 0.0 and _as2 > 0.0):
            _amin = min(_as1, _as2)
            _amax = max(_as1, _as2)
            #print "_amax: %g" % _amax
            #print "_amin: %g" % _amin
            if _amax - _amin > pi: # radians
                if _acl < 0.0:
                    _acl = _acl + pi
                else:
                    _acl = _acl - pi
                _acc = ((pi - _amax) + (_amin + pi))/2.0
        #print "_acl: %g" % (_acl * _dtr)
        #print "_acc: %g" % (_acc * _dtr)
        _xi, _yi = self.getIntersection()
        _pf1, _pf2 = self.getFixedPoints()
        _d1 = hypot((_xi - _pf1.x), (_yi - _pf1.y))
        _d2 = hypot((_xi - _pf2.x), (_yi - _pf2.y))
        _c4 = min(_d1, _d2)
        self.__rmax = _c4 * tan(_acc) + 1e-10
        #print "rmax: %g" % self.__rmax
        _pm1, _pm2 = self.getMovingPoints()
        _d1 = hypot((_xi - _pm1.x), (_yi - _pm1.y))
        _d2 = hypot((_xi - _pm2.x), (_yi - _pm2.y))
        _c4 = max(_d1, _d2)
        self.__rmin = _c4 * tan(_acc) - 1e-10
        #print "rmin: %g" % self.__rmin

    def getRadialLimits(self):
        """
            Return the radial limits of the fillet.
            This method returns a tuple of two floats; the first is
            the minimal radius for the fillet between two segments,
            and the second is the maximum radius.
        """
        return self.__rmin, self.__rmax

    def _moveSegmentPoints(self):
        """
            Position the segment endpoints used in the Fillet.
            This method is private to the Fillet.
        """
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _xc, _yc = self.__center
        #
        # segment 1
        #
        _l = _p2 - _p1
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _r = ((_xc - _x1)*(_x2 - _x1) + (_yc - _y1)*(_y2 - _y1))/pow(_l, 2)
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        _p1.setCoords(_px, _py)
        #
        # segment 2
        #
        _l = _p4 - _p3
        _x1, _y1 = _p3.getCoords()
        _x2, _y2 = _p4.getCoords()
        _r = ((_xc - _x1)*(_x2 - _x1) + (_yc - _y1)*(_y2 - _y1))/pow(_l, 2)
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        _p3.setCoords(_px, _py)

    def getAngles(self):
        """
            Return the angles that the fillet sweeps through.

            This method returns a tuple of two floats, the first is the
            start angle of the fillet, and the second is the end angle.
        """
        _ms1, _ms2 = self.getMovingPoints()
        _xc, _yc = self.__center
        _x, _y = _ms1.getCoords()
        _as1 = _dtr * atan2((_y - _yc), (_x - _xc))
        if _as1 < 0.0:
            _as1 = _as1 + 360.0
        _x, _y = _ms2.getCoords()
        _as2 = _dtr * atan2((_y - _yc), (_x - _xc))
        if _as2 < 0.0:
            _as2 = _as2 + 360.0
        return _as1, _as2

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not a fillet exists with a region.
            The four arguments define the boundary of an area, and the
            function returns True if the joint lies within that area.
            Otherwise, the function returns False.
        """
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        test_boolean(fully)
        _mp1, _mp2 = self.getMovingPoints()
        _mx1, _my1 = _mp1.getCoords()
        _mx2, _my2 = _mp2.getCoords()
        _r = self.__radius
        _xc, _yc = self.__center
        _a1, _a2 = self.getAngles()
        _xl = [_mx1, _mx2, _xc]
        _yl = [_my1, _my2, _yc]
        if fully:
            if ((min(_xl) > _xmin) and
                (min(_yl) > _ymin) and
                (max(_xl) < _xmax) and
                (max(_yl) < _ymax)):
                return True
            return False
        #
        # fixme - need to use the arc and endpoints and not
        # a line connecting the endpoints ...
        #
        return in_region(_mx1, _my1, _mx2, _my2,
                              _xmin, _ymin, _xmax, _ymax)

    def clone(self):
        _s1, _s2 = self.getSegments()
        _r = self.__radius
        _f = Fillet(_s1, _s2, _r)
        return _f


