#
# Copyright (c) 2002, 2004, 2006 Art Haas 2009 Matteo Boscolo
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

import math
import types
import warnings

from PythonCAD.Generic import util
from PythonCAD.Generic import intersections

class Snap:
    """
        define a class used to find intersection point 
    """
    def __init__(self,topLayer,snapOption):
        """
            Default Constructor
        """
        self._topLayer=topLayer
        self._sn=snapOption
        self._oneShutSnap=snapOption.copy() 
        self._computeOneShutSnap=False

    def GetSnap(self,x,y,tollerance):
        """
            Get the snap point 
        """
        _x=util.get_float(x)
        _y=util.get_float(y)
        t=util.get_float(tollerance)
        if(self._computeOneShutSnap):
            sn=self._oneShutSnap
        else:
            sn=self._sn
        if t < 0.0:
            raise ValueError, "Invalid negative tolerance: %f" % t
        if('mid' in  sn):
            if(sn['mid']):
                _X,_Y,found=self.GetMid(_x,_y,t)
                if(found):
                    return _X,_Y,found
        if('end' in  sn):
            if(sn['end']):
                _X,_Y,found=self.GetEnd(_x,_y,t)
                if(found):
                    return _X,_Y,found
        if('intersection' in  sn):
            if(sn['intersection']):
                _X,_Y,found=self.GetIntersection(_x,_y,t)
                if(found):
                    return _X,_Y,found
        return None,None,False
        if('origin' in  sn):
            if(sn['origin']):
                _X,_Y,found=self.GetOrigin()
                if(found):
                    return _X,_Y,found
        return None,None,False
    
    def GetMid(self,x,y,_t):
        """"
            Calculate the mid point 
        """
        _types = {'segment' : True}
        _tl=[self._topLayer]
        while len(_tl):
            _layer = _tl.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    _ix,_iy=_obj.getMiddlePoint()
                    if ((abs(_ix - x) < _t) and
                        (abs(_iy - y) < _t)):
                        return _ix,_iy,True
        return None,None,False
    
    def GetEndPoint(self,x,y,entityHits):
        """
            Looking for a specifiePoint             
        """
        _sep = None
        if len(entityHits) > 0:
            for _obj, _pt in entityHits:
                _px,_py = _obj.getCoords()
                _sqlen = pow((x - _px), 2) + pow((y - _py), 2)
                if _sep is None or _sqlen < _sep:
                    _sep = _sqlen
                    return _px, _py ,True
        return None,None,False
    
    def GetEnd(self,x,y,_t):
        """
            Calculate the end point
        """
        _types = {'point' : True}
        _active_layer = self._topLayer
        _sep = None
        _hits = _active_layer.mapCoords(x, y, tolerance=_t, types=_types)
        retX,retY,validate=self.GetEndPoint(x,y,_hits)
        if(validate):
            return retX,retY,validate
        #
        # See if any other Layer contains a Point ...
        #
        _layers = [self._topLayer]
        while len(_layers):
            _layer = _layers.pop()
            if _layer is not _active_layer:
                _hits = _layer.mapCoords(_x, _y, tolerance=_t, types=_types)
                retX,retY,validate=self.GetEndPoint(x,y,_hits)
                if(validate):
                    return retX,retY,validate
            _layers.extend(_layer.getSublayers())
        return None,None,False
    
    def GetIntersection(self,x,y,_t):
        """
            Calculate the intersection point
        """
        _objlist = []
        _intlist = []
        _types = {'point' : False,
                  'segment' : True,
                  'circle' : True,
                  'arc' : True,
                  'polyline' : True,
                  'hcline' : True,
                  'vcline' : True,
                  'acline' : True,
                  'cline' : True,
                  'ccircle' : True,
                  }
        _layers = [self._topLayer]
        while len(_layers):
            _layer = _layers.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    for _tobj, _mp in _objlist:
                        for _ix, _iy in intersections.find_intersections(_tobj, _obj):
                            if ((abs(_ix - x) < _t) and
                                (abs(_iy - y) < _t)):
                                _sqlen = pow((x - _ix), 2) + pow((y - _iy), 2)
                                _intlist.append((_sqlen, (_ix, _iy)))
                    _objlist.append((_obj, _pt))
            _layers.extend(_layer.getSublayers())
        #
        # use the nearest intersection point if one is available
        #
        if len(_intlist):
            _intlist.sort()
            _cp = _intlist[0][1]
            if _cp is not None:
                return _cp[0],_cp[1],True
        return None,None,False
    
    def GetOrigin(self):
        """
            Return the drawing origin point 
        """
        return 0.0,0.0,True
    
    def SetOneShutSnap(self,activeSnap):
        """
            Set One Shot snap 
        """       
        for key in self._oneShutSnap.keys():
            if(key==activeSnap):
                self._oneShutSnap[key]=True
            else:
                self._oneShutSnap[key]=False
        self.ComputeOneShutSnap()

    def ComputeOneShutSnap(self):
        """
            Activate Compute One ShotSnap
        """
        self._computeOneShutSnap=True

    def StopOneShutSnap(self):
        """
            Stop Computetion One ShutSnap
        """
        self._computeOneShutSnap=False
