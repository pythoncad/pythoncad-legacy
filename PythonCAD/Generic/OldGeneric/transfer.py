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
# Transfer objects from one layer to another
#

from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import layer

def _dest_pt(lyr, pt):
    _x, _y = pt.getCoords()
    _pts = lyr.find('point', _x, _y)
    if len(_pts) == 0:
        _lpt = pt.clone()
        _lpt.setVisibility(False)
        lyr.addObject(_lpt)
    else:
        _lpt = _pts.pop()
        _max = _lpt.countUsers()
        for _pt in _pts:
            _count = _pt.countUsers()
            if _count > _max:
                _max = _count
                _lpt = _pt
        _lpt.setVisibility(False)                
    return _lpt

def _adjust_users(obj, cobjs):
    _oid = id(obj)
    for _user in obj.getUsers():
        if isinstance(_user, dimension.Dimension):
            if isinstance(_user, dimension.LinearDimension):
                _p1, _p2 = _user.getDimPoints()
                if obj is _p1:
                    _user.setP1(cobjs[_oid])
                elif obj is _p2:
                    _user.setP2(cobjs[_oid])
                else:
                    raise RuntimeError, "Point not in linear dimension: " + `_user`
            elif isinstance(_user, dimension.RadialDimension):
                _c = _user.getDimCircle()
                if obj is _c:
                    _user.setDimCircle(cobjs[_oid])
                else:
                    raise RuntimeError, "Circle/Arc not in RadialDimension: " + `_user`
            elif isinstance(_user, dimension.AngularDimension):
                _vp, _p1, _p2 = _user.getDimPoints()
                if obj is _vp:
                    _user.setVertexPoint(cobjs[_oid])
                elif obj is _p1:
                    _user.setP1(cobjs[_oid])
                elif obj is _p2:
                    _user.setP2(cobjs[_oid])
                else:
                    raise RuntimeError, "Point not in AngularDimension: " + `_user`
            else:
                raise TypeError, "Unexpected dimension type:" + `type(_user)`
    
def transfer_objects(objlist, dest):
    """Transfer objects from one layer to another.

transfer_objects(objlist, dest)

objlist: A tuple/list of objects to transfer.
dest: The Layer which will now contain the objects.
    """
    if not isinstance(objlist, (tuple, list)):
        raise TypeError, "Invalid object list: " + `type(objlist)`
    if not isinstance(dest, layer.Layer):
        raise TypeError, "Invalid Layer type: " + `type(dest)`
    #
    # find the valid transferrable entities
    #
    _tlist = []
    for _obj in objlist:
        if _obj.getParent() is not dest and dest.canParent(_obj):
            _tlist.append(_obj)
    #
    # add non-Dimension users of Point objects and
    # connected Segments on Chamfers and Fillets
    #
    _xferlist = []
    _objdict = {}
    while len(_tlist) > 0:
        _obj = _tlist.pop()
        _xferlist.append(_obj)
        _objdict[id(_obj)] = True
        if isinstance(_obj, point.Point):
            for _user in _obj.getUsers():
                if (not isinstance(_user, dimension.Dimension) and
                    id(_user) not in _objdict):
                    _tlist.append(_obj)
        elif isinstance(_obj, (segjoint.Chamfer, segjoint.Fillet)):
            _s1, _s2 = _obj.getSegments()
            if id(_s1) not in _objdict:
                _tlist.append(_s1)
            if id(_s2) not in _objdict:
                _tlist.append(_s2)
        else:
            pass
    #
    # clone objects
    #
    _cobjs = {}
    _dobjs = {}
    for _obj in _xferlist:
        _oid = id(_obj)
        if isinstance(_obj, point.Point):
            if _oid not in _cobjs:
                _cobjs[_oid] = _dest_pt(dest, _obj)
            if _oid not in _dobjs:
                _dobjs[_oid] = _obj
        elif isinstance(_obj, segment.Segment):
            _p1, _p2 = _obj.getEndpoints()
            _pid = id(_p1)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p1)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p1
            _pid = id(_p2)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p2)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p2
            _cobjs[_oid] = _obj.clone()
        elif isinstance(_obj, (circle.Circle, ccircle.CCircle)):
            _cp = _obj.getCenter()
            _pid = id(_cp)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _cp)
            if _pid not in _dobjs:
                _dobjs[_pid] = _cp
            _cobjs[_oid] = _obj.clone()
            if isinstance(_obj, circle.Circle) and _oid not in _dobjs:
                _dobjs[_oid] = _obj
        elif isinstance(_obj, arc.Arc):
            _cp = _obj.getCenter()
            _pid = id(_cp)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _cp)
            if _pid not in _dobjs:
                _dobjs[_pid] = _cp
            _cobjs[_oid] = _obj.clone()
            if  _oid not in _dobjs:
                _dobjs[_oid] = _obj
            _layer = _obj.getParent()
            for _ep in _obj.getEndpoints():
                _pts = layer.find('point', _ep[0], _ep[1])
                if len(_pts) == 0:
                    raise RuntimeError, "No points at arc endpoint: " + str(_ep)
                _ept = None
                for _pt in _pts:
                    for _user in _pt.getUsers():
                        if _user is _obj:
                            _ept = _pt
                            break
                if _ept is None:
                    raise RuntimeError, "No Arc endpoint at: " + str(_ep)
                _pid = id(_ept)
                if _pid not in _cobjs:
                    _cobjs[_pid] = _dest_pt(dest, _ept)
                if _pid not in _dobjs:
                    _dobjs[_pid] = _ept
        elif isinstance(_obj, leader.Leader):
            _p1, _p2, _p3 = _obj.getPoints()
            _pid = id(_p1)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p1)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p1
            _pid = id(_p2)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p2)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p2
            _pid = id(_p3)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p3)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p3
            _cobjs[_oid] = _obj.clone()
        elif isinstance(_obj, polyline.Polyline):
            for _pt in _obj.getPoints():
                _pid = id(_pt)
                if _pid not in _cobjs:
                    _cobjs[_pid] = _dest_pt(dest, _pt)
                if _pid not in _dobjs:
                    _dobjs[_pid] = _pt
            _cobjs[_oid] = _obj.clone()
        elif isinstance(_obj, (hcline.HCLine,
                               vcline.VCLine,
                               acline.ACLine)):
            _pt = _obj.getLocation()
            _pid = id(_pt)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _pt)
            if _pid not in _dobjs:
                _dobjs[_pid] = _pt
            _cobjs[_oid] = _obj.clone()
        elif isinstance(_obj, cline.CLine):
            _p1, _p2 = _obj.getKeypoints()
            _pid = id(_p1)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p1)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p1
            _pid = id(_p2)
            if _pid not in _cobjs:
                _cobjs[_pid] = _dest_pt(dest, _p2)
            if _pid not in _dobjs:
                _dobjs[_pid] = _p2
            _cobjs[_oid] = _obj.clone()
        elif isinstance(_obj, (segjoint.Chamfer, segjoint.Fillet)):
            pass
        elif isinstance(_obj, (text.TextBlock,
                               dimension.LinearDimension,
                               dimension.RadialDimension,
                               dimension.AngularDimension)):
            _cobjs[id(_obj)] = _obj.clone()
        else:
            print "Skipping object type" + `type(_obj)`
    #
    # adjust cloned objects
    #
    _aobjs = []
    for _obj in _xferlist:
        _cobj = _cobjs.get(id(_obj))
        if isinstance(_obj, point.Point):
            continue
        elif isinstance(_obj, segment.Segment):
            _p1, _p2 = _obj.getEndpoints()
            _cobj.setP1(_cobjs[id(_p1)])
            _cobj.setP2(_cobjs[id(_p2)])
        elif isinstance(_obj, (circle.Circle, arc.Arc, ccircle.CCircle)):
            _cp = _obj.getCenter()
            _cobj.setCenter(_cobjs[id(_cp)])
            if isinstance(_cobj, (circle.Circle, arc.Arc)):
                #
                # the following are hacks to handle the case where
                # a RadialDimension is attached to the Circle/Arc
                #
                # A RadialDimension in an Image (currently) cannot be
                # modified to point to a Circle/Arc without a parent
                #
                _obj.setVisibility(False)
                _cobj.setVisibility(False)
                dest.addObject(_cobj)
        elif isinstance(_obj, leader.Leader):
            _p1, _p2, _p3 = _obj.getPoints()
            _cobj.setP1(_cobjs[id(_p1)])
            _cobj.setP2(_cobjs[id(_p2)])
            _cobj.setP3(_cobjs[id(_p3)])
        elif isinstance(_obj, polyline.Polyline):
            _pts = _obj.getPoints()
            for _i in range(len(_pts)):
                _pt = _pts[_i]
                _cobj.setPoint(_i, _cobjs[id(_pt)])
        elif isinstance(_obj, (hcline.HCLine,
                               vcline.VCLine,
                               acline.ACLine)):
            _pt = _obj.getLocation()
            _cobj.setLocation(_cobjs[id(_pt)])
        elif isinstance(_obj, cline.CLine):
            _p1, _p2 = _obj.getKeypoints()
            _cobj.setP1(_cobjs[id(_p1)])
            _cobj.setP2(_cobjs[id(_p2)])
        elif isinstance(_obj, (segjoint.Chamfer,
                               segjoint.Fillet)):
            _s1, _s2 = _obj.getSegments()
            _cs1 = _cobjs[id(_s1)]
            _cs2 = _cobjs[id(_s2)]
            _s = _obj.getStyle()
            if isinstance(_obj, segjoint.Chamfer):
                _l = _obj.getLength()
                _cobj = segjoint.Chamfer(_cs1, _cs2, _l, _s)
            else:
                _r = _obj.getRadius()
                _cobj = segjoint.Fillet(_cs1, _cs2, _r, _s)
            _cobj.setColor(_obj.getColor())
            _cobj.setLinetype(_obj.getLinetype())
            _cobj.setThickness(_obj.getThickness())
        elif isinstance(_obj, dimension.LinearDimension):
            _p1, _p2 = _obj.getDimPoints()
            _pid = id(_p1)
            if _pid in _cobjs:
                _cobj.setP1(_cobjs[_pid])
            _pid = id(_p2)
            if _pid in _cobjs:
                _cobj.setP2(_cobjs[_pid])
        elif isinstance(_obj, dimension.RadialDimension):
            _dc = _obj.getDimCircle()
            _dcid = id(_dc)
            if _dcid in _cobjs:
                _cobj.setDimCircle(_cobjs[_dcid])
        elif isinstance(_obj, dimension.AngularDimension):
            _vp, _p1, _p2 = _obj.getDimPoints()
            _pid = id(_vp)
            if _pid in _cobjs:
                _cobj.setVertexPoint(_cobjs[_pid])
            _pid = id(_p1)
            if _pid in _cobjs:
                _cobj.setP1(_cobjs[_pid])
            _pid = id(_p2)
            if _pid in _cobjs:
                _cobj.setP2(_cobjs[_pid])
        elif isinstance(_obj, text.TextBlock):
            pass
        else:
            print "Skipping object type " + `type(_obj)`
            continue
        _aobjs.append(_cobj)
    #
    # adjust dimensions
    #
    for _obj in _dobjs.values():
        _adjust_users(_obj, _cobjs)
    #
    # delete the old objects
    #
    for _obj in _xferlist:
        _layer = _obj.getParent()
        if _layer is not None:
            _layer.delObject(_obj)
    #
    # set visibility of points in destination layer
    #
    for _obj in _cobjs.values():
        if isinstance(_obj, point.Point):
            _obj.setVisibility(True)
    #
    # add the new objects
    #
    for _obj in _aobjs:
        if _obj.getParent() is None:
            dest.addObject(_obj)
        else:
            _obj.setVisibility(True)
