#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# code to handle moving objects
#

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.text import TextBlock
from PythonCAD.Generic.dimension import Dimension, DimString
from PythonCAD.Generic.dimension import LinearDimension
from PythonCAD.Generic.dimension import AngularDimension
from PythonCAD.Generic import util

def _adjust_dimensions(op, np):
    _users = op.getUsers()
    for _user in _users:
        if isinstance(_user, Dimension):
            if isinstance(_user, LinearDimension):
                _p1, _p2 = _user.getDimPoints()
                if _p1 is op:
                    _user.setP1(np)
                elif _p2 is op:
                    _user.setP2(np)
            elif isinstance(_user, AngularDimension):
                _vp, _p1, _p2 = _user.getDimPoints()
                if _vp is op:
                    _user.setVertexPoint(np)
                elif _p1 is op:
                    _user.setP1(np)
                elif _p2 is op:
                    _user.setP2(np)
            else:
                raise TypeError, "Unknown dimension type: " + `type(_user)`

def _most_used(plist):
    _pmax = plist.pop()
    _max = _pmax.countUsers()
    for _pt in plist:
        _count = _pt.countUsers()
        if _count > _max:
            _max = _count
            _pmax = _pt
    return _pmax

def _used_by(obj, plist):
    _objpt = None
    for _pt in plist:
        for _user in _pt.getUsers():
            if _user is obj:
                _objpt = _pt
                break
        if _objpt is not None:
            break
    return _objpt
    
def _can_move(obj, objdict):
    for _user in obj.getUsers():
        if id(_user) not in objdict:
            return False
    return True

def _copy_spcline(obj, objdict, dx, dy):
    _lp = obj.getLocation()
    _pid = id(_lp)
    _layer = obj.getParent()
    _x, _y = _lp.getCoords()
    _nx = _x + dx
    _ny = _y + dy
    _pts = _layer.find('point', _nx, _ny)
    if len(_pts) == 0:
        _np = Point(_nx, _ny)
        _layer.addObject(_np)
    else:
        _np = _most_used(_pts)
    obj.setLocation(_np)
    _adjust_dimensions(_lp, _np)
    _layer.delObject(_lp)
    if objdict.get(_pid) is not False:
        objdict[_pid] = False

def _move_spcline(obj, objdict, dx, dy):
    if isinstance(obj, HCLine):
        _objtype = 'HCLine'
    elif isinstance(obj, VCLine):
        _objtype = 'VCLine'
    elif isinstance(obj, ACLine):
        _objtype = 'ACLine'
    else:
        raise TypeError, "Unexpected object type: " + `type(obj)`
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "%s parent is None" % _objtype
    _lp = obj.getLocation()
    if _lp.getParent() is not _layer:
        raise RuntimeError, "%s/point parent object conflict!" % _objtype
    if _can_move(_lp, objdict):
        _pid = id(_lp)
        if _pid in objdict:
            if objdict[_pid]:
                _lp.move(dx, dy)
        else:
            obj.move(dx, dy)
        if objdict.get(_pid) is not False:
            objdict[_pid] = False
    else:
        _copy_spcline(obj, objdict, dx, dy)

def _copy_polyline(obj, objdict, dx, dy):
    _pts = obj.getPoints()
    _mp = {}
    for _pt in _pts:
        _pid = id(_pt)
        _mp[_pid] = False
    if _can_move(obj, objdict):
        for _pt in _pts:
            _pid = id(_pt)
            if _can_move(_pt, objdict) and objdict.get(_pid) is not False:
                _mp[_pid] = True
    _layer = obj.getParent()
    for _i in range(len(_pts)):
        _pt = _pts[_i]
        _pid = id(_pt)
        if _mp[_pid]:
            _pt.move(dx, dy)
        else:
            _x, _y = _pt.getCoords()
            _nx = _x + dx
            _ny = _y + dy
            _lpts = _layer.find('point', _nx, _ny)
            if len(_lpts) == 0:
                _np = Point(_nx, _ny)
                _layer.addObject(_np)
            else:
                _np = _most_used(_lpts)
            obj.setPoint(_i, _np)                
            _adjust_dimensions(_pt, _np)
            _layer.delObject(_pt)
        if objdict.get(_pid) is not False:
            objdict[_pid] = False

def _move_polyline(obj, objdict, dx, dy):
    _pts = obj.getPoints()
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "Polyline parent is None"
    for _pt in _pts:
        if _pt.getParent() is not _layer:
            raise RuntimeError, "Polyline/point parent object conflict!"
    _use_move = _can_move(obj, objdict)
    if _use_move:
        for _pt in _pts:
            if not _can_move(_pt, objdict):
                _use_move = False
                break
    if _use_move:
        _objmove = True
        _seen = False
        _used = True
        for _pt in _pts:
            _pid = id(_pt)
            if _pid in objdict:
                _seen = True
                if not objdict[_pid]:
                    _used = False
            if _seen and not _used:
                _objmove = False
                break
        if _objmove:
            obj.move(dx, dy)
        else:
            for _pt in _pts:
                _pid = id(_pt)
                if objdict.get(_pid) is not False:
                    _pt.move(dx, dy)
        for _pt in _pts:
            _pid = id(_pt)
            if objdict.get(_pid) is not False:
                objdict[_pid] = False
    else:
        _copy_polyline(obj, objdict, dx, dy)

def _copy_leader(obj, objdict, dx, dy):
    _p1, _p2, _p3 = obj.getPoints()
    _p1id = id(_p1)
    _p2id = id(_p2)
    _p3id = id(_p3)
    _layer = obj.getParent()
    if _can_move(_p1, objdict) and objdict.get(_p1id) is not False:
        _p1.move(dx, dy)
    else:
        _x, _y = _p1.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        obj.setP1(_np)
        _adjust_dimensions(_p1, _np)
        _layer.delObject(_p1)
    if _can_move(_p2, objdict) and objdict.get(_p2id) is not False:
        _p2.move(dx, dy)
    else:
        _x, _y = _p2.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        obj.setP2(_np)
        _adjust_dimensions(_p2, _np)
        _layer.delObject(_p2)
    if _can_move(_p3, objdict) and objdict.get(_p3id) is not False:
        _p3.move(dx, dy)
    else:
        _x, _y = _p3.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        obj.setP3(_np)
        _adjust_dimensions(_p3, _np)
        _layer.delObject(_p3)
    if objdict.get(_p1id) is not False:
        objdict[_p1id] = False
    if objdict.get(_p2id) is not False:
        objdict[_p2id] = False
    if objdict.get(_p3id) is not False:
        objdict[_p3id] = False

def _move_leader(obj, objdict, dx, dy):
    _p1, _p2, _p3 = obj.getPoints()
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "Leader parent is None"
    if _p1.getParent() is not _layer:
        raise RuntimeError, "Leader/P1 parent object conflict!"
    if _p2.getParent() is not _layer:
        raise RuntimeError, "Leader/P2 parent object conflict!"
    if _p3.getParent() is not _layer:
        raise RuntimeError, "Leader/P3 parent object conflict!"
    if (_can_move(_p1, objdict) and
        _can_move(_p2, objdict) and
        _can_move(_p3, objdict)):
        _p1id = id(_p1)
        _p2id = id(_p2)
        _p3id = id(_p3)
        if (objdict.get(_p1id) is not False and
            objdict.get(_p2id) is not False and
            objdict.get(_p3id) is not False):
            obj.move(dx, dy)
        else:
            if objdict.get(_p1id) is not False:
                _p1.move(dx, dy)
            if objdict.get(_p2id) is not False:
                _p2.move(dx, dy)
            if objdict.get(_p3id) is not False:
                _p3.move(dx, dy)
        if objdict.get(_p1id) is not False:
            objdict[_p1id] = False
        if objdict.get(_p2id) is not False:
            objdict[_p2id] = False
        if objdict.get(_p3id) is not False:
            objdict[_p3id] = False
    else:
        _copy_leader(obj, objdict, dx, dy)

def _adjust_endpoint(arc, pt, objdict, dx, dy):
    _layer = arc.getParent()
    if pt.getParent() is not _layer:
        raise RuntimeError, "Arc/Endpoint parent object conflict!"
    _pid = id(pt)
    _users = []
    for _user in pt.getUsers():
        _users.append(_user)
    if len(_users) == 1 and _users[0] is arc:
        if objdict.get(_pid) is not False:
            pt.move(dx, dy)
    else:
        pt.freeUser(arc)
        _x, _y = pt.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        _np.storeUser(arc)
        _adjust_dimensions(pt, _np)
        _layer.delObject(pt)
    if objdict.get(_pid) is not False:
        objdict[_pid] = False
    
def _copy_arc(obj, objdict, dx, dy):
    _cp = obj.getCenter()
    _pid = id(_cp)
    _layer = obj.getParent()
    _ep1, _ep2 = obj.getEndpoints()
    _pts = _layer.find('point', _ep1[0], _ep1[1])
    _lp1 = _used_by(obj, _pts)
    if _lp1 is None:
        raise RuntimeError, "Lost Arc first endpoint: " + str(_ep1)
    _adjust_endpoint(obj, _lp1, objdict, dx, dy)
    _pts = _layer.find('point', _ep2[0], _ep2[1])
    _lp2 = _used_by(obj, _pts)
    if _lp2 is None:
        raise RuntimeError, "Lost Arc second endpoint: " + str(_ep2)
    _adjust_endpoint(obj, _lp2, objdict, dx, dy)
    _x, _y = _cp.getCoords()
    _nx = _x + dx
    _ny = _y + dy
    _pts = _layer.find('point', _nx, _ny)
    if len(_pts) == 0:
        _np = Point(_nx, _ny)
        _layer.addObject(_np)
    else:
        _np = _most_used(_pts)
    obj.setCenter(_np)
    _adjust_dimensions(_cp, _np)
    _layer.delObject(_cp)
    if objdict.get(_pid) is not False:
        objdict[_pid] = False

def _move_arc(obj, objdict, dx, dy):
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "Arc parent is None"
    _cp = obj.getCenter()    
    if _cp.getParent() is not _layer:
        raise RuntimeError, "Arc/center parent object conflict!"
    if _can_move(obj, objdict) and _can_move(_cp, objdict):
        _ep1, _ep2 = obj.getEndpoints()
        _pts = _layer.find('point', _ep1[0], _ep1[1])
        _lp1 = _used_by(obj, _pts)
        if _lp1 is None:
            raise RuntimeError, "Lost Arc first endpoint: " + str(_ep1)
        _adjust_endpoint(obj, _lp1, objdict, dx, dy)
        _pts = _layer.find('point', _ep2[0], _ep2[1])
        _lp2 = _used_by(obj, _pts)
        if _lp2 is None:
            raise RuntimeError, "Lost Arc second endpoint: " + str(_ep2)
        _adjust_endpoint(obj, _lp2, objdict, dx, dy)
        _pid = id(_cp)
        if _pid in objdict:
            if objdict[_pid]:
                _cp.move(dx, dy)
        else:
            obj.move(dx, dy)
        if objdict.get(_pid) is not False:
            objdict[_pid] = False
    else:
        _copy_arc(obj, objdict, dx, dy)

def _copy_circ_ccirc(obj, objdict, dx, dy):
    _cp = obj.getCenter()
    _pid = id(_cp)
    _layer = obj.getParent()
    _x, _y = _cp.getCoords()
    _nx = _x + dx
    _ny = _y + dy
    _pts = _layer.find('point', _nx, _ny)
    if len(_pts) == 0:
        _np = Point(_nx, _ny)
        _layer.addObject(_np)
    else:
        _np = _most_used(_pts)
    obj.setCenter(_np)
    _adjust_dimensions(_cp, _np)
    _layer.delObject(_cp)
    if objdict.get(_pid) is not False:
        objdict[_pid] = False

def _move_circle(obj, objdict, dx, dy):
    if isinstance(obj, Circle):
        _objtype = 'Circle'
    elif isinstance(obj, CCircle):
        _objtype = 'CCircle'
    else:
        raise TypeError, "Unexpected object type: " + `type(obj)`
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "%s parent is None" % _objtype
    _cp = obj.getCenter()    
    if _cp.getParent() is not _layer:
        raise RuntimeError, "%s/center parent object conflict!" % _objtype
    if _can_move(obj, objdict) and _can_move(_cp, objdict):
        _pid = id(_cp)
        if _pid in objdict:
            if objdict[_pid]:
                _cp.move(dx, dy)
        else:
            obj.move(dx, dy)
        if objdict.get(_pid) is not False:
            objdict[_pid] = False
    else:
        _copy_circ_ccirc(obj, objdict, dx, dy)

def _copy_seg_cline(obj, objdict, dx, dy):
    if isinstance(obj, Segment):
        _p1, _p2 = obj.getEndpoints()
    elif isinstance(obj, CLine):
        _p1, _p2 = obj.getKeypoints()
    else:
        raise TypeError, "Unexpected object type: " + `type(obj)`
    _p1id = id(_p1)
    _p2id = id(_p2)
    _mp1 = _mp2 = False
    if _can_move(obj, objdict):
        _mp1 = _can_move(_p1, objdict) and objdict.get(_p1id) is not False
        _mp2 = _can_move(_p2, objdict) and objdict.get(_p2id) is not False
    _layer = obj.getParent()
    if _mp1:
        _p1.move(dx, dy)
    else:
        _x, _y = _p1.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        obj.setP1(_np)
        _adjust_dimensions(_p1, _np)
        _layer.delObject(_p1)
    if _mp2:
        _p2.move(dx, dy)
    else:
        _x, _y = _p2.getCoords()
        _nx = _x + dx
        _ny = _y + dy
        _pts = _layer.find('point', _nx, _ny)
        if len(_pts) == 0:
            _np = Point(_nx, _ny)
            _layer.addObject(_np)
        else:
            _np = _most_used(_pts)
        obj.setP2(_np)
        _adjust_dimensions(_p2, _np)
        _layer.delObject(_p2)
    if objdict.get(_p1id) is not False:
        objdict[_p1id] = False
    if objdict.get(_p2id) is not False:
        objdict[_p2id] = False
        
def _move_seg_cline(obj, objdict, dx, dy):
    if isinstance(obj, Segment):
        _p1, _p2 = obj.getEndpoints()
        _objtype = 'Segment'
    elif isinstance(obj, CLine):
        _p1, _p2 = obj.getKeypoints()
        _objtype = 'CLine'
    else:
        raise TypeError, "Unexpected object type: " + `type(obj)`
    _layer = obj.getParent()
    if _layer is None:
        raise RuntimeError, "%s parent is None" % _objtype
    if _p1.getParent() is not _layer:
        raise RuntimeError, "%s/P1 parent object conflict!" % _objtype
    if _p2.getParent() is not _layer:
        raise RuntimeError, "%s/P2 parent object conflict!" % _objtype
    if (_can_move(obj, objdict) and
        _can_move(_p1, objdict) and
        _can_move(_p2, objdict)):
        _p1id = id(_p1)
        _p2id = id(_p2)
        if (objdict.get(_p1id) is not False and
            objdict.get(_p2id) is not False):
            obj.move(dx, dy)
        else:
            if objdict.get(_p1id) is not False:
                _p1.move(dx, dy)
            if objdict.get(_p2id) is not False:
                _p2.move(dx, dy)
        if objdict.get(_p1id) is not False:
            objdict[_p1id] = False
        if objdict.get(_p2id) is not False:
            objdict[_p2id] = False
    else:
        _copy_seg_cline(obj, objdict, dx, dy)

def move_objects(objs, dx, dy):
    """Move a list of objects.

move_objects(objs, dx, dy)

objs: A list or tuple containing the objects to move.
dx: The displacement along the x-axis
dy: The displacement along the y-axis
    """
    if not isinstance(objs, (list, tuple)):
        raise TypeError, "Invalid object list/tuple: " + `type(objs)`
    _dx = util.get_float(dx)
    _dy = util.get_float(dy)
    if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
        _objdict = {}
        _fillets = []
        for _obj in objs:
            if not isinstance(_obj, DimString):
                _objdict[id(_obj)] = True
        for _obj in objs:
            _oid = id(_obj)
            if _oid not in _objdict:
                continue
            if _objdict[_oid]:
                if isinstance(_obj, Point):
                    _obj.move(_dx, _dy)
                    for _user in _obj.getUsers():
                        _uid = id(_user)
                        if (_uid in _objdict and
                            not isinstance(_user, Dimension)):
                            _objdict[_uid] = False
                elif isinstance(_obj, (Segment, CLine)):
                    _move_seg_cline(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, (Circle, CCircle)):
                    _move_circle(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, Arc):
                    _move_arc(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, Leader):
                    _move_leader(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, Polyline):
                    _move_polyline(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, (TextBlock, Dimension)):
                    _obj.move(_dx, _dy)
                elif isinstance(_obj, (HCLine, VCLine, ACLine)):
                    _move_spcline(_obj, _objdict, _dx, _dy)
                elif isinstance(_obj, (Chamfer, Fillet)):
                    _s1, _s2 = _obj.getSegments()
                    if id(_s1) not in _objdict or id(_s2) not in _objdict:
                        _layer = _obj.getParent()
                        _layer.delObject(_obj)
                    if isinstance(_obj, Fillet):
                        _fillets.append(_obj)
                else:
                    print "Unexpected entity type: " + `type(_obj)`
            _objdict[_oid] = False
        for _obj in _fillets:
            _obj._calculateCenter() # FIXME
