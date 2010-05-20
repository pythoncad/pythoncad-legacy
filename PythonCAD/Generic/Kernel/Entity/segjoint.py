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
from Generic.Kernel.Entity.acline           import ACLine
from Generic.Kernel.Entity.arc              import Arc
from Generic.Kernel.Entity.ccircle          import CCircle
from Generic.Kernel.Entity.pygeolib         import Vector

_dtr = 180.0/pi

ALLOW_CHAMFER_ENTITY=(Segment, ACLine)

class ObjectJoint(GeometricalEntityComposed):
    """
        A base class for chamfers and fillets
        A ObjectJoint object has the following methods:
    """
   
    def __init__(self, obj1, obj2):
        from Generic.Kernel.initsetting import DRAWIN_ENTITY
        classNames=tuple(DRAWIN_ENTITY.keys())
        if not isinstance(obj1, classNames):
            raise TypeError, "Invalid first Element for DRAWIN_ENTITY: " + `type(obj1)`
        if not isinstance(obj2, classNames):
            raise TypeError, "Invalid second Element for DRAWIN_ENTITY: " + `type(obj2)`
    
        self._obj1 = obj1
        self._obj2 = obj2
        self._externalIntersectio=False
        spoolIntersection=[Point(x, y) for x, y in find_intersections(obj1, obj2)]
        if not spoolIntersection: #if not intesection is found extend it on cLine
            spoolIntersection=[Point(x, y) for x, y in find_segment_extended_intersection(obj1, obj2)]
            self._externalIntersectio=True
        self._intersectionPoints=spoolIntersection
        
        
    def getConstructionElements(self):
        """
            Return the two Entity Object joined by the ObjectJoint.
            This method returns a tuple holding the two Entity Object joined
            by the ObjectJoint.
        """
        return self._obj1, self._obj2
        
    def getIntersection(self):
        """
            Return the intersection points of the ObjectJoint Entity Object.

            This method returns an array of intersection point 
            [] no intersection
        """
        return self.__intersectionPoints
    
    def getReletedComponent(self):
        """
            return the releted compont of the ObjectJoint
        """
        return self.getConstructionElements()


class Chamfer(ObjectJoint):
    """
        A Chamfer class 
    """
    def __init__(self, obj1, obj2, distance1, distance2, pointClick1=None, pointClick2=None):
        """
            obj1        :(Segment ,ACLine)
            obj2        :(Segment ,ACLine)
            distance1   :Real distance from intersection point to chamfer
            distance2   :Real distance from intersection point to chamfer
            pointClick1 :Clicked point from the u.i near the obj1
            pointClick2 :Clicked point from the u.i near the obj2
        """
        for obj in (obj1, obj2):
            if not isinstance(obj, ALLOW_CHAMFER_ENTITY):
                raise StructuralError, "Bad imput parameter %s"%str(type(obj))
        ObjectJoint.__init__(self, obj1, obj2)
        for dis in (distance1, distance2):
            if dis<0.0:
                raise StructuralError, "Distance parameter must be greater then 0"
        self.__distance1=distance1
        self.__distance2=distance2
        self.__pointClick1=pointClick1
        self.__pointClick2=pointClick2      
        self.__segment=self._UpdateChamferSegment()
        
    def _UpdateChamferSegment(self):           
        """
            Recompute the Chamfer segment
        """
        self._obj1, pc1=self._updateSegment(self._obj1,self.__distance1, self.__pointClick1 )
        self._obj2, pc2=self._updateSegment(self._obj2,self.__distance2, self.__pointClick2 )
        seg=Segment(pc1, pc2)
        return seg
    
    def _updateSegment(self, obj,distance,  clickPoint=None):
        """
            recalculate the segment for the chamfer
            and give the point for the chamfer
        """
        ip=self._intersectionPoints[0]
        if isinstance(obj, Segment):
            p1, p2=obj.getEndpoints()
            if p1==ip:
                mvPoint=p1
                stPoint=p2
            elif p2==ip:
                mvPoint=p2
                stPoint=p1
            elif clickPoint:
                dist1=clickPoint.dist(p1)
                dist2=clickPoint.dist(p2)
                if dist1<dist2:
                    mvPoint=p1
                    stPoint=p2  
                else:
                    mvPoint=p2
                    stPoint=p1           
            else:
                dist1=ip.dist(p1)
                dist2=ip.dist(p2)
                if dist1<dist2:
                    mvPoint=p1
                    stPoint=p2  
                else:
                    mvPoint=p2
                    stPoint=p1   
                    
            v=Vector(mvPoint,stPoint).mag()
            v.mult(distance)
            ePoint=ip+v.point()
            return Segment(ePoint, stPoint), ePoint
            
        
    def getConstructionElements(self):
        """
            retutn the construction element of the object
        """
        outElement=(self._obj1 , 
                    self._obj2 ,
                    self.__distance1, 
                    self.__distance2, 
                    self.__pointClick1, 
                    self.__pointClick2
                    )
        return outElement

    def getLength(self):
        """
            Return the Chamfer length.
        """
        if self.__segment:
            return self.__segment.length()
        else:
            return 0.0

    def setDistance1(self, distance):
        """
            change the value of the distance1
        """
        if distance<=TOL:
            raise StructuralError, "Distance could be greater then 0"
        self.__distance1=distance
        self._UpdateChamferSegment()

    def setDistance2(self, distance):
        """
            change the value of the distance1
        """
        if distance<=TOL:
            raise StructuralError, "Distance could be greater then 0"
        self.__distance2=distance
        self._UpdateChamferSegment()
           
    def clone(self):
        """
            Clone the Chamfer .. 
            I do not why somone whant to clone a chamfer ..
            But Tis is the functionality .. :-)
        """
        newChamfer=Chamfer(self._obj1 , 
                    self._obj2 ,
                    self.__distance1, 
                    self.__distance2, 
                    self.__pointClick1, 
                    self.__pointClick2)
        return newChamfer

    def getReletedComponent(self):
        """
            return the element to be written in the db and used for renderin
        """
        return self._obj1 , self._obj2 ,self.__segment
        
class Fillet(ObjectJoint):
    """
        A fillet is a curved joining of two Entity Object. For a filleted
        joint to be valid, the radius must fall within some distance
        determined by the segment endpoints and segment intersection
        point, and the two Entity Object must be extendable so they can
        share a common endpoint.
        A Fillet is derived from a ObjectJoint, so it shares the methods
        and attributes of that class. 
    """
    
    def __init__(self, obj1, obj2, r):
        ObjectJoint.__init__(obj1, obj2)
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
        return self._obj1 , self._obj2 , self.__radius

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


