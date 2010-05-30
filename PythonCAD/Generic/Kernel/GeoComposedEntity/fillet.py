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
# code for base for Fillet
#

from Kernel.GeoComposedEntity.objoint import *

class Fillet(ObjectJoint):
    """
        A fillet is a curved joining of two Entity Object. For a filleted
        joint to be valid, the radius must fall within some distance
        determined by the segment endpoints and segment intersection
        point, and the two Entity Object must be extendable so they can
        share a common endpoint.
    """
    def __init__(self, kw):
        """
            "FILLET_0" obj1             :(Segment ,ACLine,Arc,CCircle)
            "FILLET_1" obj2             :(Segment ,ACLine,Arc,CCircle)
            "FILLET_2" radius           :Radius of the Fillet
            "FILLET_3" pointClick1      :Clicked point from the u.i near the obj1
            "FILLET_4" pointClick2      :Clicked point from the u.i near the obj2
            "FILLET_5" str              :Filelt Trim Mode (FIRST,SECOND,BOTH,NO_TRIM)
        """
        wkp={}
        wkp["OBJECTJOINT_0"]=kw["FILLET_0"]
        wkp["OBJECTJOINT_1"]=kw["FILLET_1"]        
        wkp["OBJECTJOINT_3"]=kw["FILLET_5"]
        wkp["OBJECTJOINT_4"]=kw["FILLET_4"]
        wkp["OBJECTJOINT_5"]=kw["FILLET_5"]
        ObjectJoint.__init__(self, wkp)
        for k in kw:
            self[k]=kw[k]
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        self.__center = (0.0, 0.0)
        self._calculateCenter()

    def _getMovingPoint(self, obj, objP):
        """
            Get The point to move
        """
        if not isinstance(obj, (Segment, CLine)):
            raise ArithmeticError, "obj must be of CLine,Segment"
        p1, p2  =   obj.getCoords()
        if objP:
            if p1.dist(objP)>p2.dist(objP):
                return p2
            else:
                return p1
        else:
            pi=self._intersectionPoints[0]
            if p1.dist(pi)>p2.dist(pi):
                return p2
            else:
                return p1

    def _getStaticPoint(selfself, obj, objP):
        """
            Get The static point of the segment/Cline
        """
        if not isinstance(obj, (Segment, CLine)):
            raise ArithmeticError, "obj must be of CLine,Segment"
        p1, p2  =   obj.getCoords()
        if objP:
            if p1.dist(objP)<p2.dist(objP):
                return p2
            else:
                return p1
        else:
            pi=self._intersectionPoints[0]
            if p1.dist(pi)<p2.dist(pi):
                return p2
            else:
                return p1

    def getRadius(self):
        """
            Return the Fillet radius.
        """
        return self['FILLET_2']

    def setRadius(self, r):
        """
            Set the Fillet radius.
            The radius should be a positive float value.
        """
        _r = get_float(r)
        if _r < 0.0:
            raise ValueError, "Invalid fillet radius: %g" % _r
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        _or = self.radius
        if abs(_r - _or) > 1e-10:
            self.radius = _r
            self._calculateCenter()
            self._moveSegmentPoints()

    radius = property(getRadius, setRadius, None, "Fillet radius.")
   
    def _calculateCenter(self):
        """
            Find the center point of the radius
            This method is private to the Fillet object.
        """
        _r = self.radius
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
        _p1=self._getMovingPoint(self.obj1, self.pointClick1)
        _p3=self._getMovingPoint(self.obj2, self.pointClick2)
        _p2=self._getStaticPoint(self.obj1, self.pointClick1)
        _p4=self._getStaticPoint(self.obj2, self.pointClick2)

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
        _xi, _yi = self._intersectionPoints[0]
        _pf2=self._getStaticPoint(self.obj1, self.pointClick1)
        _p4=self._getStaticPoint(self.obj2, self.pointClick2)
        _d1 = hypot((_xi - _pf1.x), (_yi - _pf1.y))
        _d2 = hypot((_xi - _pf2.x), (_yi - _pf2.y))
        _c4 = min(_d1, _d2)
        self.__rmax = _c4 * tan(_acc) + 1e-10
        #print "rmax: %g" % self.__rmax
        _pm1=self._getMovingPoint(self.obj1, self.pointClick1)
        _pm2=self._getMovingPoint(self.obj2, self.pointClick2)
        _d1 = hypot((_xi - _pm1.x), (_yi - _pm1.y))
        _d2 = hypot((_xi - _pm2.x), (_yi - _pm2.y))
        _c4 = max(_d1, _d2)
        self.__rmin = _c4 * tan(_acc) - 1e-10
        #print "rmin: %g" % self.__rmin

    def getRadialLimits(self):
        """
            Return the radial limits of the fillet.
            This method returns a tuple of two floats; the first is
            the minimal radius for the fillet between two Entity Object,
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
        _r = self.radius
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
        return Fillet(self)
