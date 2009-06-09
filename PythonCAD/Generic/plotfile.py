#
# Copyright (c) 2004, 2005 Art Haas
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

import sys

from PythonCAD.Generic.image import Image
from PythonCAD.Generic.util import make_region
from PythonCAD.Generic.graphicobject import GraphicObject
from PythonCAD.Generic.color import Color
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
#from PythonCAD.Generic.ellipse import Ellipse
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic.conobject import ConstructionObject
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import dimension
from PythonCAD.Generic import util

class Plot(object):
    
    __white = Color(255, 255, 255)
    
    def __init__(self, image):
        if not isinstance(image, Image):
            raise TypeError, "Invalid image argument: " + `image`
        self.__image = image
        self.__bounds = None
        self.__landscape = False
        self.__invert = False
        self.__color = False
        self.__units = None
        self.__data = {}

    def __contains__(self, objtype):
        if not isinstance(objtype, str):
            raise TypeError, "Invalid object type string: " + `objtype`
        return objtype in self.__data
    
    def finish(self):
        self.__image = self.__bounds = self.__units = None
        self.__data.clear()
        
    def setBounds(self, xmin, ymin, xmax, ymax):
        self.__bounds = make_region(xmin, ymin, xmax, ymax)

    def getBounds(self):
        return self.__bounds
    
    def setLandscapeMode(self, flag):
        util.test_boolean(flag)
        self.__landscape = flag
        
    def getLandscapeMode(self):
        return self.__landscape
    
    def invertWhite(self, flag):
        util.test_boolean(flag)
        self.__invert = flag

    def setColorMode(self, flag):
        util.test_boolean(flag)
        self.__color = flag

    def setUnits(self):
        self.__units = self.__image.getUnits()

    def getUnits(self):
        if self.__units is None:
            self.setUnits()
        return self.__units
    
    def _getGraphicValues(self, obj):
        if not isinstance(obj, GraphicObject):
            raise TypeError, "Invalid GraphicObject: " + `obj`
        _col = None
        if self.__color:
            _c = obj.getColor()
            if self.__invert and _c == Plot.__white:
                _col = (0, 0, 0) # black
            else:
                _col = _c.getColors() # r, g, b
        _lt = obj.getLinetype().getList()
        _t = obj.getThickness()
        return _col, _lt, _t

    def getPlotData(self):
        if self.__bounds is None:
            raise ValueError, "Plot boundary not defined."
        if self.__units is None:
            self.setUnits()
        _xmin, _ymin, _xmax, _ymax = self.__bounds
        _image = self.__image
        _layers = [_image.getTopLayer()]
        while len(_layers):
            _layer = _layers.pop()
            if _layer.isVisible():
                for _obj in _layer.objsInRegion(_xmin, _ymin, _xmax, _ymax):
                    if isinstance(_obj, ConstructionObject):
                        continue # do not plot these
                    if not _obj.isVisible():
                        continue
                    if isinstance(_obj, Point):
                        continue # print points as dots?
                    elif isinstance(_obj, Segment):
                        _p1, _p2 = _obj.getEndpoints()
                        _x1, _y1 = _p1.getCoords()
                        _x2, _y2 = _p2.getCoords()
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('segments', [])
                        _data.append((_x1, _y1, _x2, _y2, _col, _lt, _t))
                    elif isinstance(_obj, Circle):
                        _x, _y = _obj.getCenter().getCoords()
                        print "x: %g; y: %g" % (_x, _y)
                        _r = _obj.getRadius()
                        print "r: %g" % _r
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('circles', [])
                        _data.append((_x, _y, _r, _col, _lt, _t))
                    elif isinstance(_obj, Arc):
                        _x, _y = _obj.getCenter().getCoords()
                        _r = _obj.getRadius()
                        _sa = _obj.getStartAngle()
                        _ea = _obj.getEndAngle()
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('arcs', [])
                        _data.append((_x, _y, _r, _sa, _ea, _col, _lt, _t))
                    elif isinstance(_obj, Leader):
                        _p1, _p2, _p3 = _obj.getPoints()
                        _x1, _y1 = _p1.getCoords()
                        _x2, _y2 = _p2.getCoords()
                        _x3, _y3 = _p3.getCoords()
                        _ax1 = _ax2 = _x3
                        _ay1 = _ay2 = _y3
                        if _obj.getArrowSize() > 1e-10:
                            _pts = _obj.getArrowPoints()
                            _ax1 = _pts[0]
                            _ay1 = _pts[1]
                            _ax2 = _pts[2]
                            _ay2 = _pts[3]
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('leaders', [])
                        _data.append((_x1, _y1, _x2, _y2, _x3, _y3,
                                      _ax1, _ay1, _ax2, _ay2,
                                      _col, _lt, _t))
                    elif isinstance(_obj, Polyline):
                        _pts = []
                        for _pt in _obj.getPoints():
                            _pts.append(_pt.getCoords())
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('polylines', [])
                        _data.append((_pts, _col, _lt, _t))
                    elif isinstance(_obj, Chamfer):
                        _p1, _p2 = _obj.getMovingPoints()
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('chamfers', [])
                        _data.append((_p1.x, _p1.y, _p2.x, _p2.y,
                                      _col, _lt, _t))
                    elif isinstance(_obj, Fillet):
                        _x, _y = _obj.getCenter()
                        _r = _obj.getRadius()
                        _sa, _ea = _obj.getAngles()
                        _col, _lt, _t = self._getGraphicValues(_obj)
                        _data = self.__data.setdefault('fillets', [])
                        _data.append((_x, _y, _r, _sa, _ea, _col, _lt, _t))
                    elif isinstance(_obj, dimension.Dimension):
                        self._saveDimensionData(_obj)
                    elif isinstance(_obj, TextBlock):
                        _tbdata = self._getTextBlockData(_obj)
                        if _tbdata is not None:
                            _data = self.__data.setdefault('textblocks', [])
                            _data.append(_tbdata)
                    else: # fixme
                        pass
            _layers.extend(_layer.getSublayers())

    def _getTextBlockData(self, tblock):
        _bounds = tblock.getBounds()
        if _bounds is None: # raise Exception?
            return
        _tbdata = {}
        _tbdata['bounds'] = _bounds
        _tbdata['location'] = tblock.getLocation()
        _family = tblock.getFamily()
        if _family.find(' ') != -1:
            _family = _family.replace(' ', '-')
        _val = tblock.getWeight()
        _weight = None
        if _val != TextStyle.WEIGHT_NORMAL:
            if _val == TextStyle.WEIGHT_LIGHT:
                _weight = 'light'
            elif _val == TextStyle.WEIGHT_BOLD:
                _weight = 'bold'
            elif _val == TextStyle.WEIGHT_HEAVY:
                _weight = 'heavy'
            else:
                raise ValueError, "Unexpected font weight: %d" % _val
        _val = tblock.getStyle()
        _style = None
        if _val != TextStyle.FONT_NORMAL:
            if _val == TextStyle.FONT_OBLIQUE:
                _style = 'oblique'
            elif _val == TextStyle.FONT_ITALIC:
                _style = 'italic'
            else:
                raise ValueError, "Unexpected font style: %d" % _val
        if _weight is None and _style is None:
            _font = _family
        else:
            if _weight is None:
                _font = "%s-%s" % (_family, _style)
            elif _style is None:
                _font = "%s-%s" % (_family, _weight)
            else:
                _font = "%s-%s%s" % (_family, _style, _weight)
        _tbdata['font'] = _font
        _col = None
        if self.__color:
            _c = tblock.getColor()
            if self.__invert and _c == Plot.__white:
                _col = (0, 0, 0) # black
            else:
                _col = _c.getColors() # r, g, b
        _tbdata['color'] = _col
        _val = tblock.getAlignment()
        if _val == TextStyle.ALIGN_LEFT:
            _align = 'left'
        elif _val == TextStyle.ALIGN_CENTER:
            _align = 'center'
        elif _val == TextStyle.ALIGN_RIGHT:
            _align = 'right'
        else:
            raise ValueError, "Unexpected alignment: %d" % _val
        _tbdata['align'] = _align
        _tbdata['size'] = tblock.getSize()
        _tbdata['angle'] = tblock.getAngle()
        _tbdata['text'] = tblock.getText().splitlines()
        # return (_x, _y, _bounds, _font, _col, _align, _size, _angle, _text)
        return _tbdata
        
    def _saveDimensionData(self, dim):
        if isinstance(dim, dimension.LinearDimension):
            self._saveLDimData(dim)
        elif isinstance(dim, dimension.RadialDimension):
            self._saveRDimData(dim)
        elif isinstance(dim, dimension.AngularDimension):
            self._saveADimData(dim)
        else:
            raise TypeError, "Unexpected dimension type: " + `dim`

    def _getDimGraphicData(self, dim):
        _col = None
        if self.__color:
            _c = dim.getColor()
            if self.__invert and _c == Plot.__white:
                _col = (0, 0, 0) # black
            else:
                _col = _c.getColors() # r, g, b
        return _col

    def _getDimMarkers(self, dim):
        _data = {}
        _etype = dim.getEndpointType()
        if isinstance(dim, dimension.AngularDimension):
            _crossbar = dim.getDimCrossarc()
        else:
            _crossbar = dim.getDimCrossbar()
        _mp1, _mp2 = _crossbar.getCrossbarPoints()
        if (_etype == dimension.Dimension.DIM_ENDPT_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_SLASH):
            _epts = _crossbar.getMarkerPoints()
            _data['p1'] = _epts[0]
            _data['p2'] = _epts[1]
            _data['p3'] = _epts[2]
            _data['p4'] = _epts[3]
            _data['v1'] = _mp1
            _data['v2'] = _mp2
            if _etype == dimension.Dimension.DIM_ENDPT_ARROW:
                _data['type'] = 'arrow'
            elif _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW:
                _data['type'] = 'filled_arrow'
            elif _etype == dimension.Dimension.DIM_ENDPT_SLASH:
                _data['type'] = 'slash'
        elif _etype == dimension.Dimension.DIM_ENDPT_CIRCLE:
            _data['type'] = 'circle'
            _data['radius'] = dim.getEndpointSize()
            _data['c1'] = _mp1
            _data['c2'] = _mp2
        elif _etype == dimension.Dimension.DIM_ENDPT_NONE:
            _data['type'] = None
        else:
            raise ValueError, "Unexpected endpoint type: %d" % _etype
        return _data
        
    def _saveLDimData(self, dim):
        _dimdata = {}
        _bar1, _bar2 = dim.getDimBars()
        _ep1, _ep2 = _bar1.getEndpoints()
        _dimdata['ep1'] = _ep1
        _dimdata['ep2'] = _ep2
        _ep3, _ep4 = _bar2.getEndpoints()
        _dimdata['ep3'] = _ep3
        _dimdata['ep4'] = _ep4
        _ep5, _ep6 = dim.getDimCrossbar().getEndpoints()
        _dimdata['ep5'] = _ep5
        _dimdata['ep6'] = _ep6
        _eptype = dim.getEndpointType()
        _dimdata['eptype'] = _eptype
        _dimdata['color'] = self._getDimGraphicData(dim)
        _dimdata['thickness'] = dim.getThickness()
        _ds1, _ds2 = dim.getDimstrings()
        _dimdata['ds1'] = self._getTextBlockData(_ds1)
        if dim.getDualDimMode():
            _dimdata['ds2'] = self._getTextBlockData(_ds2)
        _dimdata['markers'] = self._getDimMarkers(dim)
        _data = self.__data.setdefault('ldims', [])
        _data.append(_dimdata)

    def _saveRDimData(self, dim):
        _dimdata = {}
        _ep1, _ep2 = dim.getDimCrossbar().getEndpoints()
        _dimdata['ep1'] = _ep1
        _dimdata['ep2'] = _ep2
        _dimdata['color'] = self._getDimGraphicData(dim)
        _dimdata['thickness'] = dim.getThickness()
        _ds1, _ds2 = dim.getDimstrings()
        _dimdata['dia_mode'] = dim.getDiaMode()
        _dimdata['ds1'] = self._getTextBlockData(_ds1)
        if dim.getDualDimMode():
            _dimdata['ds2'] = self._getTextBlockData(_ds2)
        _mdata = self._getDimMarkers(dim)
        if not dim.getDiaMode() and _mdata['type'] is not None:
            _mdata['rdim'] = True
        _dimdata['markers'] = _mdata
        _data = self.__data.setdefault('rdims', [])
        _data.append(_dimdata)

    def _saveADimData(self, dim):
        _dimdata = {}        
        _bar1, _bar2 = dim.getDimBars()
        _ep1, _ep2 = _bar1.getEndpoints()
        _dimdata['ep1'] = _ep1
        _dimdata['ep2'] = _ep2
        _ep3, _ep4 = _bar2.getEndpoints()
        _dimdata['ep3'] = _ep3
        _dimdata['ep4'] = _ep4
        _dimdata['vp'] = dim.getVertexPoint().getCoords()
        _crossarc = dim.getDimCrossarc()
        _r = _crossarc.getRadius()
        _dimdata['r'] = _r
        _sa = _crossarc.getStartAngle()
        _dimdata['sa'] = _sa
        _ea = _crossarc.getEndAngle()
        _dimdata['ea'] = _ea
        _dimdata['color'] = self._getDimGraphicData(dim)
        _dimdata['thickness'] = dim.getThickness()
        _ds1, _ds2 = dim.getDimstrings()        
        _dimdata['ds1'] = self._getTextBlockData(_ds1)
        if dim.getDualDimMode():
            _dimdata['ds2'] = self._getTextBlockData(_ds2)
        _dimdata['markers'] = self._getDimMarkers(dim)
        _data = self.__data.setdefault('adims', [])
        _data.append(_dimdata)
        
    def getPlotEntities(self, entity):
        return self.__data[entity]
        
