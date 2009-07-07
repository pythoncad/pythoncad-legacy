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
# code for doing file saves/loads
#

import sys

#
# the 'import xml.dom' and 'import xml.parsers.expat' statements
# are not directly necessary but adding them seems to fix some
# Python XML parsing bugs. Very odd ...
#

import xml.dom
import xml.dom.minidom
import xml.parsers.expat

from PythonCAD.Generic import layer
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import units
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import fileio
from PythonCAD.Generic import globals

def _save_graph_bits(obj, node, doc, map):
    _st = obj.getStyle()
    assert _st in map, "Object %s style %s not in map!" % (str(obj), `_st`)
    _attr = doc.createAttributeNS("image", "style")
    node.setAttributeNodeNS(_attr)
    node.setAttributeNS("image", "style", `map[_st]`)
    _color = obj.getColor()
    if _color != _st.getColor():
        assert _color in map, "Object %s color not in map!" % str(obj)
        _attr = doc.createAttributeNS("image", "color")
        node.setAttributeNodeNS(_attr)
        node.setAttributeNS("image", "color", `map[_color]`)
    _linetype = obj.getLinetype()
    if _linetype != _st.getLinetype():
        assert _linetype in map, "Object %s linetype not in map!" % str(obj)
        _attr = doc.createAttributeNS("image", "linetype")
        node.setAttributeNodeNS(_attr)
        node.setAttributeNS("image", "linetype", `map[_linetype]`)
    _thickness = obj.getThickness()
    _tdiff = _thickness - _st.getThickness()
    if abs(_tdiff) > 1e-10:
        _attr = doc.createAttributeNS("image", "thickness")
        node.setAttributeNodeNS(_attr)
        node.setAttributeNS("image", "thickness", `_thickness`)

def _save_state_bits(obj, node, doc):
    if not obj.isVisible():
        _attr = doc.createAttributeNS("image", "visibility")
        node.setAttributeNodeNS(_attr)
        node.setAttributeNS("image", "visibility", "False")
    if obj.isLocked():
        _attr = doc.createAttributeNS("image", "locked")
        node.setAttributeNodeNS(_attr)
        node.setAttributeNS("image", "locked", "True")
        
def _save_leaders(lyr, node, doc, map):
    _leaders = lyr.getLayerEntities("leader")
    if len(_leaders):
        _leads = doc.createElementNS("image", "image:Leaders")
        node.appendChild(_leads)
        _i = 0
        for _lead in _leaders:
            _p1, _p2, _p3 = _lead.getPoints()
            _i1 = id(_p1)
            _i2 = id(_p2)
            _i3 = id(_p3)
            assert _i1 in map, "Leader %s p1 not in map!" % str(_lead)
            assert _i2 in map, "Leader %s p2 not in map!" % str(_lead)
            assert _i3 in map, "Leader %s p3 not in map!" % str(_lead)
            _child = doc.createElementNS("image", "image:Leader")
            _leads.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "p1")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p1", `map[_i1]`)
            _attr = doc.createAttributeNS("image", "p2")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p2", `map[_i2]`)
            _attr = doc.createAttributeNS("image", "p3")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p3", `map[_i3]`)
            _attr = doc.createAttributeNS("image", "size")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "size", `_lead.getArrowSize()`)
            _save_graph_bits(_lead, _child, doc, map)
            _save_state_bits(_lead, _child, doc)
            _i = _i + 1

def _save_polylines(lyr, node, doc, map):
    _polylines = lyr.getLayerEntities("polyline")
    if len(_polylines):
        _polys = doc.createElementNS("image", "image:Polylines")
        node.appendChild(_polys)
        _i = 0
        for _polyline in _polylines:
            _pts = _polyline.getPoints()
            _mpts = []
            for _pt in _pts:
                _ip = id(_pt)
                assert _ip in map, "Polyline point not in map: " + str(_pt)
                _mpts.append(map[_ip])
            _child = doc.createElementNS("image", "image:Polyline")
            _polys.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "points")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "points", `_mpts`)
            _save_graph_bits(_polyline, _child, doc, map)
            _save_state_bits(_polyline, _child, doc)
            _i = _i + 1

def _save_textblocks(lyr, node, doc, map):
    _textblocks = lyr.getLayerEntities("text")
    if len(_textblocks):
        _tbs = doc.createElementNS("image", "image:TextBlocks")
        node.appendChild(_tbs)
        _i = 0
        for _textblock in _textblocks:
            _x, _y = _textblock.getLocation()
            _text = _textblock.getText()
            _style = _textblock.getTextStyle()
            assert _style in map, "TextBlock textstyle not in map: " + `_style`
            _child = doc.createElementNS("image", "image:TextBlock")
            _tbs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "x")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "x", `_x`)
            _attr = doc.createAttributeNS("image", "y")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "y", `_y`)
            _attr = doc.createAttributeNS("image", "tsid")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "tsid", `map[_style]`)
            _save_state_bits(_textblock, _child, doc)
            #
            # save any override values as attributes
            #
            _tbfamily = _textblock.getFamily()
            if _tbfamily != _style.getFamily():
                assert _tbfamily in map, "Missing font family in map: " + _tbfamily
                _attr = doc.createAttributeNS("image", "fid")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "fid", `map[_tbfamily]`)
            _weight = _textblock.getWeight()
            if _weight != _style.getWeight():
                _tbweight = text.font_weight_string(_weight)
                _attr = doc.createAttributeNS("image", "weight")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "weight", _tbweight)
            _st = _textblock.getStyle()
            if _st != _style.getStyle():
                _tbstyle = text.font_style_string(_st)
                _attr = doc.createAttributeNS("image", "style")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "style", _tbstyle)
            _tbsize = _textblock.getSize()
            if _tbsize != _style.getSize():
                _attr = doc.createAttributeNS("image", "size")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "size", `_tbsize`)
            _tbcolor = _textblock.getColor()
            if _tbcolor != _style.getColor():
                assert _tbcolor in map, "Missing font color in map: " + str(_tbcolor)
                _attr = doc.createAttributeNS("image", "cid")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "cid", `map[_tbcolor]`)
            _tbangle = _textblock.getAngle()
            if abs(_tbangle - _style.getAngle()) > 1e-10:
                _attr = doc.createAttributeNS("image", "angle")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "angle", `_tbangle`)
            _tbalign = _textblock.getAlignment()
            if _tbalign != _style.getAlignment():
                _attr = doc.createAttributeNS("image", "halign")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "halign", `_tbalign`)
            for _line in _text.splitlines():
                _textline = doc.createElementNS("image", "image:TextLine")
                _child.appendChild(_textline)
                _attr = doc.createAttributeNS("image", "text")
                _textline.setAttributeNodeNS(_attr)
                _textline.setAttributeNS("image", "text", _line)
                #
                # I'd really rather not use an attribute to store
                # the text - using a TextNode would be better so
                # the file would look like the following:
                #
                # ...
                # <image:TextLine>blah blah blah</image:TextLine>
                # <image:TextLine>foo bar blah</image:TextLine>
                # ...
                #
                # minidom adds in newlines and spaces though
                # is there a known workaround or a magic call to
                # have it not do this?
                #
                # _textnode = doc.createTextNode(_line)
                # _textline.appendChild(_textnode)
            _i = _i + 1

def _save_chamfers(lyr, node, doc, map):
    _chamferlist = lyr.getLayerEntities("chamfer")
    if len(_chamferlist):
        _chs = doc.createElementNS("image", "image:Chamfers")
        node.appendChild(_chs)
        _i = 0
        for _ch in _chamferlist:
            _s1, _s2 = _ch.getSegments()
            _i1 = id(_s1)
            _i2 = id(_s2)
            assert _i1 in map, "Chamfer %s seg1 not in map!" % `_ch`
            assert _i2 in map, "Chamfer %s seg2 not in map!" % `_ch`
            _child = doc.createElementNS("image", "image:Chamfer")
            _chs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "s1")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "s1", `map[_i1]`)
            _attr = doc.createAttributeNS("image", "s2")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "s2", `map[_i2]`)
            _attr = doc.createAttributeNS("image", "length")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "length", `_ch.getLength()`)
            _save_graph_bits(_ch, _child, doc, map)
            _save_state_bits(_ch, _child, doc)
            _i = _i + 1

def _save_fillets(lyr, node, doc, map):
    _filletlist = lyr.getLayerEntities("fillet")
    if len(_filletlist):
        _flts = doc.createElementNS("image", "image:Fillets")
        node.appendChild(_flts)
        _i = 0
        for _flt in _filletlist:
            _s1, _s2 = _flt.getSegments()
            _i1 = id(_s1)
            _i2 = id(_s2)
            assert _i1 in map, "Fillet %s seg1 not in map!" % `_flt`
            assert _i2 in map, "Fillet %s seg2 not in map!" % `_flt`
            _child = doc.createElementNS("image", "image:Fillet")
            _flts.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "_s1")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "s1", `map[_i1]`)
            _attr = doc.createAttributeNS("image", "s2")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "s2", `map[_i2]`)
            _attr = doc.createAttributeNS("image", "radius")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "radius", `_flt.getRadius()`)
            _save_graph_bits(_flt, _child, doc, map)
            _save_state_bits(_flt, _child, doc)
            _i = _i + 1

def _save_dim_override(node, doc, map, stkey, value):
    _child = doc.createElementNS("image", "image:DimOption")
    node.appendChild(_child)
    _attr = doc.createAttributeNS("image", "opt")
    _child.setAttributeNodeNS(_attr)
    _child.setAttributeNS("image", "opt", stkey)
    if (stkey == 'DIM_COLOR' or
        stkey == 'DIM_PRIMARY_FONT_COLOR' or
        stkey == 'DIM_SECONDARY_FONT_COLOR'):
        _attr = doc.createAttributeNS("image", "cid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "cid", `map[value]`)
    elif (stkey == 'DIM_PRIMARY_FONT_FAMILY' or
          stkey == 'DIM_SECONDARY_FONT_FAMILY'):
        _attr = doc.createAttributeNS("image", "fid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "fid", `map[value]`)
    else:
        _attr = doc.createAttributeNS("image", "val")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "val", str(value))

def _save_dim_common(dim, node, doc, map):
    _ds = dim.getDimStyle()
    _offset = dim.getOffset()
    if abs(_ds.getValue('DIM_OFFSET') - _offset) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_OFFSET', _offset)
    _ext = dim.getExtension()
    if abs(_ds.getValue('DIM_EXTENSION') - _ext) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_EXTENSION', _ext)
    _endpt = dim.getEndpointType()
    if _ds.getValue('DIM_ENDPOINT') != _endpt:
        _save_dim_override(node, doc, map, 'DIM_ENDPOINT', _endpt)
    _size = dim.getEndpointSize()
    if abs(_ds.getValue('DIM_ENDPOINT_SIZE') - _size) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_ENDPOINT_SIZE', _size)
    _color = dim.getColor()
    if _ds.getValue('DIM_COLOR') != _color:
        _save_dim_override(node, doc, map, 'DIM_COLOR', _color)
    _dual_mode = dim.getDualDimMode()
    if _ds.getValue('DIM_DUAL_MODE') != _dual_mode:
        _save_dim_override(node, doc, map, 'DIM_DUAL_MODE', _dual_mode)
    _poff = dim.getPositionOffset()
    if abs(_ds.getValue('DIM_POSITION_OFFSET') - _poff) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_POSITION_OFFSET', _poff)
    _dmo = dim.getDualModeOffset()
    if abs(_ds.getValue('DIM_DUAL_MODE_OFFSET') - _dmo) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_DUAL_MODE_OFFSET', _dmo)
    _t = dim.getThickness()
    if abs(_ds.getValue('DIM_THICKNESS') - _t) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_THICKNESS', _ext)
    #
    # primary dimension string
    #
    _pds = dim.getPrimaryDimstring()
    _prefix = _pds.getPrefix()
    if isinstance(dim, dimension.LinearDimension):
        if _ds.getValue('DIM_PRIMARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'DIM_PRIMARY_PREFIX', _prefix)
    elif isinstance(dim, dimension.RadialDimension):
        if _ds.getValue('RADIAL_DIM_PRIMARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'RADIAL_DIM_PRIMARY_PREFIX', _prefix)
    elif isinstance(dim, dimension.AngularDimension):
        if _ds.getValue('ANGULAR_DIM_PRIMARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'ANGULAR_DIM_PRIMARY_PREFIX', _prefix)
    else:
        raise TypeError, "Unexpected dimension type: " + `dim`
    _suffix = _pds.getSuffix()
    if isinstance(dim, dimension.LinearDimension):
        if _ds.getValue('DIM_PRIMARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'DIM_PRIMARY_SUFFIX', _suffix)
    elif isinstance(dim, dimension.RadialDimension):
        if _ds.getValue('RADIAL_DIM_PRIMARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'RADIAL_DIM_PRIMARY_SUFFIX', _suffix)
    elif isinstance(dim, dimension.AngularDimension):
        if _ds.getValue('ANGULAR_DIM_PRIMARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'ANGULAR_DIM_PRIMARY_SUFFIX', _prefix)
    else:
        raise TypeError, "Unexpected dimension type: " + `dim`
    _unit = _pds.getUnits()
    if _ds.getValue('DIM_PRIMARY_UNITS') != _unit:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_UNITS', _unit)
    _precision = _pds.getPrecision()
    if _ds.getValue('DIM_PRIMARY_PRECISION') != _precision:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_PRECISION',
                           _precision)
    _print_zero = _pds.getPrintZero()
    if _ds.getValue('DIM_PRIMARY_LEADING_ZERO') != _print_zero:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_LEADING_ZERO',
                           _print_zero)
    _print_dec = _pds.getPrintDecimal()
    if _ds.getValue('DIM_PRIMARY_TRAILING_DECIMAL') != _print_dec:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_TRAILING_DECIMAL',
                           _print_dec)
    _family = _pds.getFamily()
    if _ds.getValue('DIM_PRIMARY_FONT_FAMILY') != _family:
        assert _family in map, "Font family %s missing in map" % _family
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_FONT_FAMILY', _family)
    _font_style = _pds.getStyle()
    if _ds.getValue('DIM_PRIMARY_FONT_STYLE') != _font_style:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_FONT_STYLE',
                           _font_style)
    _weight = _pds.getWeight()
    if _ds.getValue('DIM_PRIMARY_FONT_WEIGHT') != _weight:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_FONT_WEIGHT', _weight)
    _font_color = _pds.getColor()
    if _ds.getValue('DIM_PRIMARY_FONT_COLOR') != _font_color:
        assert _font_color in map, "Font color missing in map: " + `_font_color`
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_FONT_COLOR',
                           _font_color)
    _size = _pds.getSize()
    if abs(_ds.getValue('DIM_PRIMARY_TEXT_SIZE') - _size) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_TEXT_SIZE', _size)
    _angle = _pds.getAngle()
    if abs(_ds.getValue('DIM_PRIMARY_TEXT_ANGLE') - _angle) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_TEXT_ANGLE', _angle)
    _align = _pds.getAlignment()
    if _ds.getValue('DIM_PRIMARY_TEXT_ALIGNMENT') != _align:
        _save_dim_override(node, doc, map, 'DIM_PRIMARY_TEXT_ALIGN', _align)
    #
    # secondary dimension string
    #
    _sds = dim.getSecondaryDimstring()
    _prefix = _sds.getPrefix()
    if isinstance(dim, dimension.LinearDimension):
        if _ds.getValue('DIM_SECONDARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'DIM_SECONDARY_PREFIX', _prefix)
    elif isinstance(dim, dimension.RadialDimension):
        if _ds.getValue('RADIAL_DIM_SECONDARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'RADIAL_DIM_SECONDARY_PREFIX', _prefix)
    elif isinstance(dim, dimension.AngularDimension):
        if _ds.getValue('ANGULAR_DIM_SECONDARY_PREFIX') != _prefix:
            _save_dim_override(node, doc, map,
                               'ANGULAR_DIM_SECONDARY_PREFIX', _prefix)
    else:
        raise TypeError, "Unexpected dimension type: " + `dim`
    _suffix = _sds.getSuffix()
    if isinstance(dim, dimension.LinearDimension):
        if _ds.getValue('DIM_SECONDARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'DIM_SECONDARY_SUFFIX', _suffix)
    elif isinstance(dim, dimension.RadialDimension):
        if _ds.getValue('RADIAL_DIM_SECONDARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'RADIAL_DIM_SECONDARY_SUFFIX', _suffix)
    elif isinstance(dim, dimension.AngularDimension):
        if _ds.getValue('ANGULAR_DIM_SECONDARY_SUFFIX') != _suffix:
            _save_dim_override(node, doc, map,
                               'ANGULAR_DIM_SECONDARY_SUFFIX', _prefix)
    else:
        raise TypeError, "Unexpected dimension type: " + `dim`
    _unit = _sds.getUnits()
    if _ds.getValue('DIM_SECONDARY_UNITS') != _unit:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_UNITS', _unit)
    _precision = _sds.getPrecision()
    if _ds.getValue('DIM_SECONDARY_PRECISION') != _precision:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_PRECISION',
                           _precision)
    _print_zero = _sds.getPrintZero()
    if _ds.getValue('DIM_SECONDARY_LEADING_ZERO') != _print_zero:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_LEADING_ZERO',
                           _print_zero)
    _print_dec = _sds.getPrintDecimal()
    if _ds.getValue('DIM_SECONDARY_TRAILING_DECIMAL') != _print_dec:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_TRAILING_DECIMAL',
                           _print_dec)
    _family = _sds.getFamily()
    if _ds.getValue('DIM_SECONDARY_FONT_FAMILY') != _family:
        assert _family in map, "Font family %s missing in map" % _family
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_FONT_FAMILY', _family)
    _font_style = _sds.getStyle()
    if _ds.getValue('DIM_SECONDARY_FONT_STYLE') != _font_style:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_FONT_STYLE',
                           _font_style)
    _weight = _sds.getWeight()
    if _ds.getValue('DIM_SECONDARY_FONT_WEIGHT') != _weight:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_FONT_WEIGHT', _weight)
    _font_color = _sds.getColor()
    if _ds.getValue('DIM_SECONDARY_FONT_COLOR') != _font_color:
        assert _font_color in map, "Font color missing in map: " + `_font_color`
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_FONT_COLOR',
                           _font_color)
    _size = _sds.getSize()
    if abs(_ds.getValue('DIM_SECONDARY_TEXT_SIZE') - _size) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_TEXT_SIZE', _size)
    _angle = _sds.getAngle()
    if abs(_ds.getValue('DIM_SECONDARY_TEXT_ANGLE') - _angle) > 1e-10:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_TEXT_ANGLE', _angle)
    _align = _sds.getAlignment()
    if _ds.getValue('DIM_SECONDARY_TEXT_ALIGNMENT') != _align:
        _save_dim_override(node, doc, map, 'DIM_SECONDARY_TEXT_ALIGN', _align)

def _save_linear_dims(l, node, doc, map, entmap, dimtype):
    if dimtype == 'linear_dimension':
        _tag = 'image:LDims'
    elif dimtype == 'horizontal_dimension':
        _tag = 'image:HDims'
    elif dimtype == 'vertical_dimension':
        _tag = 'image:VDims'
    else:
        raise ValueError, "Unexpected linear dimension type: " + `dimtype`
    _ldimlist = l.getLayerEntities(dimtype)
    if len(_ldimlist):
        _item_tag = _tag[:-1]
        _block = doc.createElementNS("image", _tag)
        node.appendChild(_block)
        _i = 0
        for _dim in _ldimlist:
            _p1, _p2 = _dim.getDimPoints()
            _l1 = _p1.getParent()
            if _l1 is None:
                raise ValueError, "Dimension P1 point not in a Layer"
            _l2 = _p2.getParent()
            if _l2 is None:
                raise ValueError, "Dimension P2 point not in a Layer"
            _x, _y = _dim.getLocation()
            _ds = _dim.getDimStyle()
            _child = doc.createElementNS("image", _item_tag)
            _block.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "l1")
            _child.setAttributeNodeNS(_attr)
            _il = id(_l1)
            if _il in map:
                _child.setAttributeNS("image", "l1", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l1', _l1)
            _attr = doc.createAttributeNS("image", "p1")
            _child.setAttributeNodeNS(_attr)
            _ip = id(_p1)
            if _ip in map:
                _child.setAttributeNS("image", "p1", `map[_ip]`)
            else:
                entmap.saveEntity(_child, 'p1', _p1)
            _attr = doc.createAttributeNS("image", "l2")
            _child.setAttributeNodeNS(_attr)
            _il = id(_l2)
            if _il in map:
                _child.setAttributeNS("image", "l2", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l2', _l2)
            _attr = doc.createAttributeNS("image", "p2")
            _child.setAttributeNodeNS(_attr)
            _ip = id(_p2)
            if _ip in map:
                _child.setAttributeNS("image", "p2", `map[_ip]`)
            else:
                entmap.saveEntity(_child, 'p2', _p2)
            _attr = doc.createAttributeNS("image", "x")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "x", `_x`)
            _attr = doc.createAttributeNS("image", "y")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "y", `_y`)
            _attr = doc.createAttributeNS("image", "ds")
            assert _ds in map, "Missing DimStyle in map: " + `_ds`
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "ds", `map[_ds]`)
            _save_dim_common(_dim, _child, doc, map)
            _save_state_bits(_dim, _child, doc)

def _save_radial_dims(lyr, node, doc, map, entmap):
    _rdimlist = lyr.getLayerEntities("radial_dimension")
    if len(_rdimlist):
        _rdims = doc.createElementNS("image", "image:RDims")
        node.appendChild(_rdims)
        _i = 0
        for _rdim in _rdimlist:
            _dc = _rdim.getDimCircle()
            _dl = _dc.getParent()
            if _dl is None:
                raise ValueError, "RadialDimension Circle/Arc not in a Layer"
            _x, _y = _rdim.getLocation()
            _ds = _rdim.getDimStyle()
            _child = doc.createElementNS("image", "image:RDim")
            _rdims.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "l")
            _child.setAttributeNodeNS(_attr)
            _il = id(_dl)
            if _il in map:
                _child.setAttributeNS("image", "l", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l', _dl)
            _attr = doc.createAttributeNS("image", "c")
            _child.setAttributeNodeNS(_attr)
            _ic = id(_dc)
            if _ic in map:
                _child.setAttributeNS("image", "c", `map[_ic]`)
            else:
                entmap.saveEntity(_child, 'c', _dc)
            _attr = doc.createAttributeNS("image", "x")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "x", `_x`)
            _attr = doc.createAttributeNS("image", "y")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "y", `_y`)
            _attr = doc.createAttributeNS("image", "ds")
            assert _ds in map, "Missing DimStyle in map: " + `_ds`
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "ds", `map[_ds]`)
            _save_dim_common(_rdim, _child, doc, map)
            _save_state_bits(_rdim, _child, doc)
            _dia_mode = _rdim.getDiaMode()
            if _ds.getValue('RADIAL_DIM_DIA_MODE') != _dia_mode:
                _opt = doc.createElementNS("image", "image:DimOption")
                _child.appendChild(_opt)
                _attr = doc.createAttributeNS("image", "opt")
                _opt.setAttributeNodeNS(_attr)
                _opt.setAttributeNS("image", "opt", 'RADIAL_DIM_DIA_MODE')
                _attr = doc.createAttributeNS("image", "val")
                _opt.setAttributeNodeNS(_attr)
                _opt.setAttributeNS("image", "val", `_dia_mode`)

def _save_angular_dims(lyr, node, doc, map, entmap):
    _adimlist = lyr.getLayerEntities("angular_dimension")
    if len(_adimlist):
        _adims = doc.createElementNS("image", "image:ADims")
        node.appendChild(_adims)
        _i = 0
        for _adim in _adimlist:
            _p1, _p2, _p3 = _adim.getDimPoints()
            _l1 = _p1.getParent()
            _l2 = _p2.getParent()
            _l3 = _p3.getParent()
            if _l1 is None:
                raise ValueError, "Dimension vertex point not in a Layer"
            _l2 = _p2.getParent()
            if _l2 is None:
                raise ValueError, "Dimension P1 point not in a Layer"
            _l3 = _p3.getParent()
            if _l3 is None:
                raise ValueError, "Dimension P2 point not in a Layer"
            _x, _y = _adim.getLocation()
            _ds = _adim.getDimStyle()
            _child = doc.createElementNS("image", "image:ADim")
            _adims.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "l1")
            _child.setAttributeNodeNS(_attr)
            _il = id(_l1)
            if _il in map:
                _child.setAttributeNS("image", "l1", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l1', _l1)
            _attr = doc.createAttributeNS("image", "p1")
            _child.setAttributeNodeNS(_attr)
            _ip = id(_p1)
            if _ip in map:
                _child.setAttributeNS("image", "p1", `map[_ip]`)
            else:
                entmap.saveEntity(_child, 'p1', _p1)
            _attr = doc.createAttributeNS("image", "l2")
            _child.setAttributeNodeNS(_attr)
            _il = id(_l2)
            if _il in map:
                _child.setAttributeNS("image", "l2", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l2', _l2)
            _attr = doc.createAttributeNS("image", "p2")
            _child.setAttributeNodeNS(_attr)
            _ip = id(_p2)
            if _ip in map:
                _child.setAttributeNS("image", "p2", `map[_ip]`)
            else:
                entmap.saveEntity(_child, 'p2', _p2)
            _attr = doc.createAttributeNS("image", "l3")
            _child.setAttributeNodeNS(_attr)
            _il = id(_l3)
            if _il in map:
                _child.setAttributeNS("image", "l3", `map[_il]`)
            else:
                entmap.saveEntity(_child, 'l3', _l3)
            _attr = doc.createAttributeNS("image", "p3")
            _child.setAttributeNodeNS(_attr)
            _ip = id(_p3)
            if _ip in map:
                _child.setAttributeNS("image", "p3", `map[_ip]`)
            else:
                entmap.saveEntity(_child, 'p3', _p3)
            _attr = doc.createAttributeNS("image", "x")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "x", `_x`)
            _attr = doc.createAttributeNS("image", "y")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "y", `_y`)
            _attr = doc.createAttributeNS("image", "ds")
            assert _ds in map, "Missing DimStyle in map: " + `_ds`
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "ds", `map[_ds]`)
            _save_dim_common(_adim, _child, doc, map)
            _save_state_bits(_adim, _child, doc)

def _save_ccircles(lyr, node, doc, map):
    _cclist = lyr.getLayerEntities("ccircle")
    if len(_cclist):
        _ccircs = doc.createElementNS("image", "image:CCircles")
        node.appendChild(_ccircs)
        _i = 0
        for _cc in _cclist:
            _cp = _cc.getCenter()
            _ic = id(_cp)
            assert _ic in map, "CCircle %s center not in map!" % str(_cc)
            _child = doc.createElementNS("image", "image:CCircle")
            _ccircs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "cp")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "cp", `map[_ic]`)
            _attr = doc.createAttributeNS("image", "r")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "r", `_cc.getRadius()`)
            _save_state_bits(_cc, _child, doc)
            _i = _i + 1

def _save_clines(lyr, node, doc, map):
    _cllist = lyr.getLayerEntities("cline")
    if len(_cllist):
        _clines = doc.createElementNS("image", "image:CLines")
        node.appendChild(_clines)
        _i = 0
        for _cl in _cllist:
            _p1, _p2 = _cl.getKeypoints()
            _i1 = id(_p1)
            _i2 = id(_p2)
            assert _i1 in map, "CLine %s p1 not in map!" % str(_cl)
            assert _i2 in map, "CLine %s p2 not in map!" % str(_cl)
            _child = doc.createElementNS("image", "image:CLine")
            _clines.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "p1")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p1", `map[_i1]`)
            _attr = doc.createAttributeNS("image", "p2")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p2", `map[_i2]`)
            _save_state_bits(_cl, _child, doc)
            _i = _i + 1

def _save_aclines(lyr, node, doc, map):
    _acllist = lyr.getLayerEntities("acline")
    if len(_acllist):
        _acls = doc.createElementNS("image", "image:ACLines")
        node.appendChild(_acls)
        _i = 0
        for _acl in _acllist:
            _loc = _acl.getLocation()
            _il = id(_loc)
            assert _il in map, "ACline %s point not in map!" % str(_acl)
            _child = doc.createElementNS("image", "image:ACLine")
            _acls.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "angle")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "angle", `_acl.getAngle()`)
            _attr = doc.createAttributeNS("image", "location")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "location", `map[_il]`)
            _save_state_bits(_acl, _child, doc)
            _i = _i + 1

def _save_vclines(lyr, node, doc, map):
    _vcllist = lyr.getLayerEntities("vcline")
    if len(_vcllist):
        _vcls = doc.createElementNS("image", "image:VCLines")
        node.appendChild(_vcls)
        _i = 0
        for _vcl in _vcllist:
            _loc = _vcl.getLocation()
            _il = id(_loc)
            assert _il in map, "VCline %s point not in map!" % str(_vcl)
            _child = doc.createElementNS("image", "image:VCLine")
            _vcls.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "location")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "location", `map[_il]`)
            _save_state_bits(_vcl, _child, doc)
            _i = _i + 1

def _save_hclines(lyr, node, doc, map):
    _hcllist = lyr.getLayerEntities("hcline")
    if len(_hcllist):
        _hcls = doc.createElementNS("image", "image:HCLines")
        node.appendChild(_hcls)
        _i = 0
        for _hcl in _hcllist:
            _loc = _hcl.getLocation()
            _il = id(_loc)
            assert _il in map, "HCline %s point not in map!" % str(_hcl)
            _child = doc.createElementNS("image", "image:HCLine")
            _hcls.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "location")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "location", `map[_il]`)
            _save_state_bits(_hcl, _child, doc)
            _i = _i + 1

def _save_arcs(lyr, node, doc, map):
    _arclist = lyr.getLayerEntities("arc")
    if len(_arclist):
        _arcs = doc.createElementNS("image", "image:Arcs")
        node.appendChild(_arcs)
        _i = 0
        for _arc in _arclist:
            _cp = _arc.getCenter()
            _ic = id(_cp)
            assert _ic in map, "Arc %s center not in map!" % str(_arc)
            _child = doc.createElementNS("image", "image:Arc")
            _arcs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "cp")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "cp", `map[_ic]`)
            _attr = doc.createAttributeNS("image", "r")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "r", `_arc.getRadius()`)
            _attr = doc.createAttributeNS("image", "sa")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "sa", `_arc.getStartAngle()`)
            _attr = doc.createAttributeNS("image", "ea")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "ea", `_arc.getEndAngle()`)
            _save_graph_bits(_arc, _child, doc, map)
            _save_state_bits(_arc, _child, doc)
            if _arc.hasUsers():
                map[id(_arc)] = _i
            _i = _i + 1

def _save_circles(lyr, node, doc, map):
    _circles = lyr.getLayerEntities("circle")
    if len(_circles):
        _circs = doc.createElementNS("image", "image:Circles")
        node.appendChild(_circs)
        _i = 0
        for _circle in _circles:
            _cp = _circle.getCenter()
            _ic = id(_cp)
            assert _ic in map, "Circle %s center not in map!" % str(_circle)
            _child = doc.createElementNS("image", "image:Circle")
            _circs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "cp")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "cp", `map[_ic]`)
            _attr = doc.createAttributeNS("image", "r")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "r", `_circle.getRadius()`)
            _save_graph_bits(_circle, _child, doc, map)
            _save_state_bits(_circle, _child, doc)
            if _circle.hasUsers():
                map[id(_circle)] = _i
            _i = _i + 1

def _save_segments(lyr, node, doc, map):
    _segments = lyr.getLayerEntities("segment")
    if len(_segments):
        _segs = doc.createElementNS("image", "image:Segments")
        node.appendChild(_segs)
        _i = 0
        for _seg in _segments:
            _p1, _p2 = _seg.getEndpoints()
            _i1 = id(_p1)
            _i2 = id(_p2)
            assert _i1 in map, "Segment %s p1 not in map!" % str(_seg)
            assert _i2 in map, "Segment %s p2 not in map!" % str(_seg)
            _child = doc.createElementNS("image", "image:Segment")
            _segs.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "p1")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p1", `map[_i1]`)
            _attr = doc.createAttributeNS("image", "p2")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "p2", `map[_i2]`)
            _save_graph_bits(_seg, _child, doc, map)
            _save_state_bits(_seg, _child, doc)
            if _seg.hasUsers():
                map[id(_seg)] = _i
            _i = _i + 1

def _save_points(lyr, node, doc, map):
    _points = lyr.getLayerEntities("point")
    if len(_points):
        _pts = doc.createElementNS("image", "image:Points")
        node.appendChild(_pts)
        _i = 0
        for _pt in _points:
            _x, _y = _pt.getCoords()
            _child = doc.createElementNS("image", "image:Point")
            _pts.appendChild(_child)
            _attr = doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = doc.createAttributeNS("image", "x")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "x", `_x`)
            _attr = doc.createAttributeNS("image", "y")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "y", `_y`)
            _save_state_bits(_pt, _child, doc)
            if _pt.hasUsers():
                map[id(_pt)] = _i
            _i = _i + 1

def _make_xml_doc():
    _newdoc = xml.dom.minidom.Document()
    _root = _newdoc.createElementNS("image", "image:Image")
    _newdoc.appendChild(_root)
    _attr = _newdoc.createAttributeNS("xmlns", "xmlns:image")
    _root.setAttributeNodeNS(_attr)
    _root.setAttributeNS("xmlns", "xmlns:image", "http://www.pythoncad.org")
    _attr = _newdoc.createAttributeNS("xmlns", "xmlns:xsi")
    _root.setAttributeNodeNS(_attr)
    _root.setAttributeNS("xmlns", "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    _attr = _newdoc.createAttributeNS("xsi", "xsi:schemaLocation")
    _root.setAttributeNodeNS(_attr)
    _root.setAttributeNS("xmlns", "xsi:schemaLocation", "http://www.pythoncad.org")
    return _newdoc

def _save_dimstyles(attmap, node, doc, map):
    _dimstyles = doc.createElementNS("image", "image:DimStyles")
    node.appendChild(_dimstyles)
    _dslist = attmap['dimstyles']
    _i = 0
    for _ds in _dslist:
        _child = doc.createElementNS("image", "image:DimStyle")
        _dimstyles.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "name")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "name", _ds.getName())
        _stkeys = _ds.getOptions()
        _stkeys.sort()
        for _stkey in _stkeys:
            _value = _ds.getValue(_stkey)
            _dsfield = doc.createElementNS("image", "image:DimOption")
            _child.appendChild(_dsfield)
            _attr = doc.createAttributeNS("image", "opt")
            _dsfield.setAttributeNodeNS(_attr)
            _dsfield.setAttributeNS("image", "opt", _stkey)
            if (_stkey == 'DIM_COLOR' or
                _stkey == 'DIM_PRIMARY_FONT_COLOR' or
                _stkey == 'DIM_SECONDARY_FONT_COLOR'):
                assert _value in map, "color %s not found in map!" % str(_value)
                _attr = doc.createAttributeNS("image", "cid")
                _dsfield.setAttributeNodeNS(_attr)
                _dsfield.setAttributeNS("image", "cid", `map[_value]`)
            elif (_stkey == 'DIM_PRIMARY_FONT_FAMILY' or
                  _stkey == 'DIM_SECONDARY_FONT_FAMILY'):
                assert _value in map, "font %s not found in map!" % str(_value)
                _attr = doc.createAttributeNS("image", "fid")
                _dsfield.setAttributeNodeNS(_attr)
                _dsfield.setAttributeNS("image", "fid", `map[_value]`)
            elif (_stkey == 'DIM_PRIMARY_PREFIX' or
                  _stkey == 'DIM_PRIMARY_SUFFIX' or
                  _stkey == 'DIM_SECONDARY_PREFIX' or
                  _stkey == 'DIM_SECONDARY_SUFFIX' or
                  _stkey == 'RADIAL_DIM_PRIMARY_PREFIX' or
                  _stkey == 'RADIAL_DIM_PRIMARY_SUFFIX' or
                  _stkey == 'RADIAL_DIM_SECONDARY_PREFIX' or
                  _stkey == 'RADIAL_DIM_SECONDARY_SUFFIX' or
                  _stkey == 'ANGULAR_DIM_PRIMARY_PREFIX' or
                  _stkey == 'ANGULAR_DIM_PRIMARY_SUFFIX' or
                  _stkey == 'ANGULAR_DIM_SECONDARY_PREFIX' or
                  _stkey == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
                _attr = doc.createAttributeNS("image", "val")
                _dsfield.setAttributeNodeNS(_attr)
                _dsfield.setAttributeNS("image", "val", str(_value))
            else:
                _attr = doc.createAttributeNS("image", "val")
                _dsfield.setAttributeNodeNS(_attr)
                _dsfield.setAttributeNS("image", "val", `_value`)
        map[_ds] = _i
        _i = _i + 1

def _save_textstyles(attmap, node, doc, map):
    _textstyles = doc.createElementNS("image", "image:TextStyles")
    node.appendChild(_textstyles)
    _tslist = attmap['textstyles']
    _i = 0
    for _ts in _tslist:
        _child = doc.createElementNS("image", "image:TextStyle")
        _textstyles.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "name")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "name", _ts.getName())
        _family = _ts.getFamily()
        assert _family in map, "Missing font family in map: " + _family
        _attr = doc.createAttributeNS("image", "fid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "fid", `map[_family]`)
        _weight = text.font_weight_string(_ts.getWeight())
        _attr = doc.createAttributeNS("image", "weight")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "weight", _weight)
        _style = text.font_style_string(_ts.getStyle())
        _attr = doc.createAttributeNS("image", "style")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "style", _style)
        _size = _ts.getSize()
        _attr = doc.createAttributeNS("image", "size")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "size", `_size`)
        _angle = _ts.getAngle()
        _attr = doc.createAttributeNS("image", "angle")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "angle", `_angle`)
        _align = _ts.getAlignment()
        _attr = doc.createAttributeNS("image", "halign")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "halign", `_align`)
        _color = _ts.getColor()
        assert _color in map, "Missing font color in map: " + str(_color)
        _attr = doc.createAttributeNS("image", "cid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "cid", `map[_color]`)
        map[_ts] = _i
        _i = _i + 1

def _save_font_families(attmap, node, doc, map):
    _families = doc.createElementNS("image", "image:FontFamilies")
    node.appendChild(_families)
    _i = 0
    _fontlist = attmap['fonts']
    for _font in _fontlist:
        _child = doc.createElementNS("image", "image:FontFamily")
        _families.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "name")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "name", _font)
        map[_font] = _i
        _i = _i + 1

def _save_styles(attmap, node, doc, map):
    _styles = doc.createElementNS("image", "image:Styles")
    node.appendChild(_styles)
    _i = 0
    _stylelist = attmap['styles']
    for _style in _stylelist:
        _child = doc.createElementNS("image", "image:Style")
        _styles.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "name")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "name", _style.getName())
        _color = _style.getColor()
        assert _color in map, "Color not found in map!"
        _attr = doc.createAttributeNS("image", "cid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "cid", `map[_color]`)
        _linetype = _style.getLinetype()
        assert _linetype in map, "Linetype not found in map!"
        _attr = doc.createAttributeNS("image", "ltid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "ltid", `map[_linetype]`)
        _attr = doc.createAttributeNS("image", "thickness")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "thickness", `_style.getThickness()`)
        map[_style] = _i
        _i = _i + 1

def _save_colors(attmap, node, doc, map):
    _colors = doc.createElementNS("image", "image:Colors")
    node.appendChild(_colors)
    _i = 0
    _colorlist = attmap['colors']
    for _color in _colorlist:
        _r, _g, _b = _color.getColors()
        _child = doc.createElementNS("image", "image:Color")
        _colors.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "r")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "r", `_r`)
        _attr = doc.createAttributeNS("image", "g")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "g", `_g`)
        _attr = doc.createAttributeNS("image", "b")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "b", `_b`)
        #
        # save color as hex string as well
        #
        # It may be better to save colors like ...
        #
        # <image:Color>#ffffff</image:Color>
        #
        _attr = doc.createAttributeNS("image", "color")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "color", str(_color))
        map[_color] = _i
        _i = _i + 1

def _save_linetypes(attmap, node, doc, map):
    _linetypes = doc.createElementNS("image", "image:Linetypes")
    node.appendChild(_linetypes)
    _i = 0
    _linetypelist = attmap['linetypes']
    for _linetype in _linetypelist:
        _child = doc.createElementNS("image", "image:Linetype")
        _linetypes.appendChild(_child)
        _attr = doc.createAttributeNS("image", "id")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "id", `_i`)
        _attr = doc.createAttributeNS("image", "name")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "name", _linetype.getName())
        _attr = doc.createAttributeNS("image", "pattern")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "pattern", `_linetype.getList()`)
        map[_linetype] = _i
        _i = _i + 1

def _save_units(image, node, doc):
    _uts = doc.createElementNS("image", "image:Units")
    node.appendChild(_uts)
    _attr = doc.createAttributeNS("image", "unit")
    _uts.setAttributeNodeNS(_attr)
    _ustr = units.unit_string(image.getUnits())
    _uts.setAttributeNS("image", "unit", _ustr)

def _save_globals(attmap, node, doc, map):
#
# for now, assumes globals are ONLY colors
#
    _globals = doc.createElementNS("image", "image:Globals")
    node.appendChild(_globals)
    _globaldict = attmap['globals']
    _keylist = _globaldict.keys()
    for _key in _keylist:
        _child = doc.createElementNS("image", "image:Global")
        _globals.appendChild(_child)
        _attr = doc.createAttributeNS("image", "key")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "key", _key)
        _val = _globaldict[_key]
        assert _val in map, "Color not found in map!"
        _attr = doc.createAttributeNS("image", "cid")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("image", "cid", `map[_val]`)



_entlist = [
    'segment',
    'circle',
    'arc',
    'chamfer',
    'fillet',
    'leader',
    'polyline',
    ]

_conobjs = [
    'hcline',
    'vcline',
    'acline',
    'cline',
    'ccircle',
    ]

_dimlist = [
    'linear_dimension',
    'horizontal_dimension',
    'vertical_dimension',
    'radial_dimension',
    'angular_dimension',
    ]

def _get_image_attributes(image):
    _attmap = {}
    _styles = []
    _attmap['styles'] = _styles
    _colors = []
    _attmap['colors'] = _colors
    _linetypes = []
    _attmap['linetypes'] = _linetypes
    _fonts = []
    _attmap['fonts'] = _fonts
    _dimstyles = []
    _attmap['dimstyles'] = _dimstyles
    _textstyles = []
    _attmap['textstyles'] = _textstyles
    _globals = {}
    _attmap['globals'] = _globals
    #
    # Get global properties
    #
    for _key in ['BACKGROUND_COLOR', 'INACTIVE_LAYER_COLOR', 'SINGLE_POINT_COLOR', 'MULTI_POINT_COLOR']:
        _val = _globals[_key] = image.getOption(_key)
        if _val not in _colors:
            _colors.append(_val)
    _check_conobjs = True
    _layers = [image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        for _ent in _entlist:
            for _obj in _layer.getLayerEntities(_ent):
                #
                # get style properties
                #
                _style = _obj.getStyle()
                if _style not in _styles:
                    _styles.append(_style)
                _color = _style.getColor() # style color
                if _color not in _colors:
                    _colors.append(_color)
                _linetype = _style.getLinetype() # style linetype
                if _linetype not in _linetypes:
                    _linetypes.append(_linetype)
                #
                # object may have overridden style values
                #
                _color = _obj.getColor()
                if _color not in _colors:
                    _colors.append(_color)
                _linetype = _obj.getLinetype()
                if _linetype not in _linetypes:
                    _linetypes.append(_linetype)
        if _check_conobjs:
            for _conobj in _conobjs:
                for _obj in _layer.getLayerEntities(_conobj):
                    _check_conobjs = False
                    _style = _obj.getStyle()
                    if _style not in _styles:
                        _styles.append(_style)
                    _color = _style.getColor()
                    if _color not in _colors:
                        _colors.append(_color)
                    _linetype = _style.getLinetype()
                    if _linetype not in _linetypes:
                        _linetypes.append(_linetype)
                    break
                if not _check_conobjs:
                    break
        for _dim in _dimlist:
            for _obj in _layer.getLayerEntities(_dim):
                #
                # get style properties
                #
                _ds = _obj.getDimStyle()
                if _ds not in _dimstyles:
                    _dimstyles.append(_ds)
                _color = _ds.getOption('DIM_COLOR')
                if _color not in _colors:
                    _colors.append(_color)
                _color = _ds.getOption('DIM_PRIMARY_FONT_COLOR')
                if _color not in _colors:
                    _colors.append(_color)
                _color = _ds.getOption('DIM_SECONDARY_FONT_COLOR')
                if _color not in _colors:
                    _colors.append(_color)
                _font = _ds.getOption('DIM_PRIMARY_FONT_FAMILY')
                if _font not in _fonts:
                    _fonts.append(_font)
                _font = _ds.getOption('DIM_SECONDARY_FONT_FAMILY')
                if _font not in _fonts:
                    _fonts.append(_font)
                #
                # object may have overridden style values
                #
                _color = _obj.getColor()
                if _color not in _colors: # dimension bar colors
                    _colors.append(_color)
                _pds = _obj.getPrimaryDimstring()
                _color = _pds.getColor() # primary dim text color
                if _color not in _colors:
                    _colors.append(_color)
                _font = _pds.getFamily() # primary dim font
                if _font not in _fonts:
                    _fonts.append(_font)
                _style = _pds.getTextStyle()
                if _style not in _textstyles:
                    # print "Adding PDS textstyle: " + `_pds`
                    # print "Dimension: " + `_obj`
                    # print "TextStyle: " + `_style`
                    _textstyles.append(_style)
                _sds = _obj.getSecondaryDimstring()
                _color = _sds.getColor() # secondary dim color
                if _color not in _colors:
                    _colors.append(_color)
                _font = _sds.getFamily() # secondary dim font
                if _font not in _fonts:
                    _fonts.append(_font)
                _style = _sds.getTextStyle()
                if _style not in _textstyles:
                    # print "Adding SDS textstyle: " + `_sds`
                    # print "Dimension: " + `_obj`
                    # print "TextStyle: " + `_style`
                    _textstyles.append(_style)
        for _textblock in _layer.getLayerEntities("textblock"):
            # print "Testing textblock: " + `_textblock`
            # print "Text: '%s'" % _textblock.getText()
            _style = _textblock.getTextStyle()
            # print "TextStyle: " + `_style`
            if _style not in _textstyles:
                # print "Adding TextBlock textstyle: " + `_textblock`
                # print "TextStyle: " + `_style`
                _textstyles.append(_style)
            _font = _style.getFamily()
            if _font not in _fonts:
                _fonts.append(_font)
            _color = _style.getColor()
            if _color not in _colors:
                _colors.append(_color)
            #
            # objects may have overridden the styles
            #
            _font = _textblock.getFamily()
            if _font not in _fonts:
                _fonts.append(_font)
            _color = _textblock.getColor()
            if _color not in _colors:
                _colors.append(_color)
        if _layer.hasSublayers():
            _layers.extend(_layer.getSublayers())
    _colors.sort()
    _styles.sort()
    _linetypes.sort()
    _fonts.sort()
    _dimstyles.sort()
    return _attmap

class EntityMap(object):
    def __init__(self):
        self.__elements = {}
        self.__entities = {}

    def __nonzero__(self):
        return len(self.__elements) != 0

    def saveEntity(self, elem, key, entity):
        _eid = id(elem)
        if _eid not in self.__elements:
            self.__elements[_eid] = elem
        if _eid not in self.__entities:
            self.__entities[_eid] = {}
        _edict = self.__entities[_eid]
        if key in _edict:
            raise KeyError, "Key '%s' already stored for element" % key
        _edict[key] = entity

    def getElements(self):
        return self.__elements.values()

    def getElementKeys(self, element):
        _eid = id(element)
        return self.__entities[_eid].keys()

    def getEntity(self, element, key):
        _eid = id(element)
        return self.__entities[_eid][key]

def save_image(image, filehandle):
    """Save a file.

save_image(image, filehandle)

Argument 'image' should be an Image instance, and 'filehandle'
should be an opened file, pipe, or writeable object.
    """
    _map = {}
    _entmap = EntityMap()
    _doc = xml.dom.minidom.Document()
    try:
        _child = _doc.createElementNS("image", "image:Image")
        _doc.appendChild(_child)
        _attr = _doc.createAttributeNS("xmlns", "xmlns:image")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("xmlns",
                              "xmlns:image",
                              "http://www.pythoncad.org")
        _attr = _doc.createAttributeNS("xmlns", "xmlns:xsi")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("xmlns",
                              "xmlns:xsi",
                              "http://www.w3.org/2001/XMLSchema-instance")
        _attr = _doc.createAttributeNS("xsi", "xsi:schemaLocation")
        _child.setAttributeNodeNS(_attr)
        _child.setAttributeNS("xmlns",
                              "xsi:schemaLocation",
                              "http://www.pythoncad.org")
        _root = _doc.documentElement
        #
        # to only save colors, linetypes, etc. actually used
        # in the drawing, the get_image_attributes() scans
        # the image and stores them and returns them in a
        # dictionary, then the image entities are written out.
        # this approach requires two passes over the image, and
        # it would be nice if these two passes could be combined
        # into a single pass.
        #
        _attmap = _get_image_attributes(image)
        _save_colors(_attmap, _root, _doc, _map)
        _save_linetypes(_attmap, _root, _doc, _map)
        _save_styles(_attmap, _root, _doc, _map)
        _save_font_families(_attmap, _root, _doc, _map)
        _save_dimstyles(_attmap, _root, _doc, _map)
        _save_textstyles(_attmap, _root, _doc, _map)
        _save_units(image, _root, _doc)
        _save_globals(_attmap, _root, _doc, _map)
        _lyrs = _doc.createElementNS("image", "image:Layers")
        _root.appendChild(_lyrs)
        _layers = [image.getTopLayer()]
        _i = 0
        while len(_layers):
            _layer = _layers.pop()
            _map[id(_layer)] = _i
            _child = _doc.createElementNS("image", "image:Layer")
            _lyrs.appendChild(_child)
            _attr = _doc.createAttributeNS("image", "id")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "id", `_i`)
            _attr = _doc.createAttributeNS("image", "name")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "name", _layer.getName())
            _attr = _doc.createAttributeNS("image", "scale")
            _child.setAttributeNodeNS(_attr)
            _child.setAttributeNS("image", "scale", `_layer.getScale()`)
            _parent = _layer.getParentLayer()
            if _parent is not None:
                _pid = id(_parent)
                assert _pid in _map, "Layer %s parent not in map!" % _layer.getName()
                _attr = _doc.createAttributeNS("image", "parent")
                _child.setAttributeNodeNS(_attr)
                _child.setAttributeNS("image", "parent", `_map[_pid]`)
            _save_points(_layer, _child, _doc, _map)
            _save_segments(_layer, _child, _doc, _map)
            _save_circles(_layer, _child, _doc, _map)
            _save_arcs(_layer, _child, _doc, _map)
            _save_hclines(_layer, _child, _doc, _map)
            _save_vclines(_layer, _child, _doc, _map)
            _save_aclines(_layer, _child, _doc, _map)
            _save_clines(_layer, _child, _doc, _map)
            _save_ccircles(_layer, _child, _doc, _map)
            _save_chamfers(_layer, _child, _doc, _map)
            _save_fillets(_layer, _child, _doc, _map)
            _save_leaders(_layer, _child, _doc, _map)
            _save_polylines(_layer, _child, _doc, _map)
            _save_textblocks(_layer, _child, _doc, _map)
            _save_linear_dims(_layer, _child, _doc, _map,
                              _entmap, 'linear_dimension')
            _save_linear_dims(_layer, _child, _doc, _map,
                              _entmap, 'horizontal_dimension')
            _save_linear_dims(_layer, _child, _doc, _map,
                              _entmap, 'vertical_dimension')
            _save_radial_dims(_layer, _child, _doc, _map, _entmap)
            _save_angular_dims(_layer, _child, _doc, _map, _entmap)
            _save_state_bits(_layer, _child, _doc)
            _i = _i + 1
            if _layer.hasSublayers():
                _layers.extend(_layer.getSublayers())
        if _entmap:
            for _elem in _entmap.getElements():
                for _key in _entmap.getElementKeys(_elem):
                    _obj = _entmap.getEntity(_elem, _key)
                    _oid = id(_obj)
                    assert _oid in _map, "Missing object in map: " + `_obj`
                    #if _oid not in _map:
                    # print "missing object in map:"
                    # print "id(): " + `_oid`
                    # print "obj: " + str(_obj)
                    # raise KeyError, "Missing object key"
                    _elem.setAttributeNS("image", _key, `_map[_oid]`)
        #
        # write it out
        #
        _doc.writexml(filehandle, "  ", "  ", "\n")
    finally:
        _doc.unlink()

#
# reload an image
#

class DimMap(object):
    def __init__(self):
        self.__layers = {}
        self.__dims = {}

    def __nonzero__(self):
        return len(self.__layers) != 0

    def saveDim(self, lyr, dtype, dim):
        _lid = id(lyr)
        if _lid not in self.__layers:
            self.__layers[_lid] = lyr
        if _lid not in self.__dims:
            self.__dims[_lid] = {}
        _dtdict = self.__dims[_lid]
        if dtype not in _dtdict:
            _dtdict[dtype] = []
        _dtdict[dtype].append(dim)

    def getLayers(self):
        return self.__layers.values()

    def getLayerDimTypes(self, lyr):
        _lid = id(lyr)
        return self.__dims[_lid].keys()

    def getLayerDims(self, lyr, key):
        _lid = id(lyr)
        return self.__dims[_lid][key][:]

def _apply_dim_overrides(dim, overrides):
    # print "in _apply_dim_overrides()"
    for _key in overrides:
        _val = overrides[_key]
        if _key == 'DIM_OFFSET':
            dim.setOffset(_val)
        elif _key == 'DIM_EXTENSION':
            dim.setExtension(_val)
        elif _key == 'DIM_COLOR':
            dim.setColor(_val)
        elif _key == 'DIM_POSITION':
            dim.setPosition(_val)
        elif _key == 'DIM_ENDPOINT':
            dim.setEndpointType(_val)
        elif _key == 'DIM_ENDPOINT_SIZE':
            dim.setEndpointSize(_val)
        elif _key == 'DIM_DUAL_MODE':
            dim.setDualDimMode(_val)
        elif _key == 'DIM_POSITION_OFFSET':
            dim.setPositionOffset(_val)
        elif _key == 'DIM_DUAL_MODE_OFFSET':
            dim.setDualModeOffset(_val)
        elif _key == 'DIM_PRIMARY_FONT_FAMILY':
            dim.getPrimaryDimstring().setFamily(_val)
        elif _key == 'DIM_PRIMARY_FONT_WEIGHT':
            dim.getPrimaryDimstring().setWeight(_val)
        elif _key == 'DIM_PRIMARY_FONT_STYLE':
            dim.getPrimaryDimstring().setStyle(_val)
        elif _key == 'DIM_PRIMARY_FONT_COLOR':
            dim.getPrimaryDimstring().setColor(_val)
        elif (_key == 'DIM_PRIMARY_PREFIX' or
              _key == 'RADIAL_DIM_PRIMARY_PREFIX' or
              _key == 'ANGULAR_DIM_PRIMARY_PREFIX'):
            dim.getPrimaryDimstring().setPrefix(_val)
        elif (_key == 'DIM_PRIMARY_SUFFIX' or
              _key == 'RADIAL_DIM_PRIMARY_SUFFIX' or
              _key == 'ANGULAR_DIM_PRIMARY_SUFFIX'):
            dim.getPrimaryDimstring().setSuffix(_val)
        elif _key == 'DIM_PRIMARY_PRECISION':
            dim.getPrimaryDimstring().setPrecision(_val)
        elif _key == 'DIM_PRIMARY_UNITS':
            dim.getPrimaryDimstring().setUnits(_val)
        elif _key == 'DIM_PRIMARY_LEADING_ZERO':
            dim.getPrimaryDimstring().setPrintZero(_val)
        elif _key == 'DIM_PRIMARY_TRAILING_DECIMAL':
            dim.getPrimaryDimstring().setPrintDecimal(_val)
        elif _key == 'DIM_PRIMARY_TEXT_SIZE':
            dim.getPrimaryDimstring().setSize(_val)
        elif _key == 'DIM_PRIMARY_TEXT_ANGLE':
            dim.getPrimaryDimstring().setAngle(_val)
        elif _key == 'DIM_PRIMARY_TEXT_ALIGNMENT':
            dim.getPrimaryDimstring().setAlignment(_val)
        elif _key == 'DIM_SECONDARY_FONT_FAMILY':
            dim.getSecondaryDimstring().setFamily(_val)
        elif _key == 'DIM_SECONDARY_FONT_WEIGHT':
            dim.getSecondaryDimstring().setWeight(_val)
        elif _key == 'DIM_SECONDARY_FONT_STYLE':
            dim.getSecondaryDimstring().setStyle(_val)
        elif _key == 'DIM_SECONDARY_FONT_COLOR':
            dim.getSecondaryDimstring().setColor(_val)
        elif (_key == 'DIM_SECONDARY_PREFIX' or
              _key == 'RADIAL_DIM_SECONDARY_PREFIX' or
              _key == 'ANGULAR_DIM_SECONDARY_PREFIX'):
            dim.getSecondaryDimstring().setPrefix(_val)
        elif (_key == 'DIM_SECONDARY_SUFFIX' or
              _key == 'RADIAL_DIM_SECONDARY_SUFFIX' or
              _key == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
            dim.getSecondaryDimstring().setSuffix(_val)
        elif _key == 'DIM_SECONDARY_PRECISION':
            dim.getSecondaryDimstring().setPrecision(_val)
        elif _key == 'DIM_SECONDARY_UNITS':
            dim.getSecondaryDimstring().setUnits(_val)
        elif _key == 'DIM_SECONDARY_LEADING_ZERO':
            dim.getSecondaryDimstring().setPrintZero(_val)
        elif _key == 'DIM_SECONDARY_TRAILING_DECIMAL':
            dim.getSecondaryDimstring().setPrintDecimal(_val)
        elif _key == 'DIM_SECONDARY_TEXT_SIZE':
            dim.getSecondaryDimstring().setSize(_val)
        elif _key == 'DIM_SECONDARY_TEXT_ANGLE':
            dim.getSecondaryDimstring().setAngle(_val)
        elif _key == 'DIM_SECONDARY_TEXT_ALIGNMENT':
            dim.getSecondaryDimstring().setAlignment(_val)
        elif _key == 'RADIAL_DIM_DIA_MODE':
            dim.setDiaMode(_val)
        else:
            pass # unused key ...

def _load_dim_options(node, map):
    # print "in _load_dim_options()"
    _options = {}
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == 'image:DimOption':
                _opt = str(_child.getAttribute('opt'))
                if (_opt == 'DIM_COLOR' or
                    _opt == 'DIM_PRIMARY_FONT_COLOR' or
                    _opt == 'DIM_SECONDARY_FONT_COLOR'):
                    _cid = int(_child.getAttribute('cid'))
                    assert _cid in map['color'], 'Color index %d missing' % _cid
                    _val = map['color'][_cid]
                elif (_opt == 'DIM_PRIMARY_FONT_FAMILY' or
                      _opt == 'DIM_SECONDARY_FONT_FAMILY'):
                    _fid = int(_child.getAttribute('fid'))
                    assert _fid in map['family'], 'Font index %d missing' % _fid
                    _val = map['family'][_fid]
                elif (_opt == 'DIM_OFFSET' or
                      _opt == 'DIM_ENDPOINT_SIZE' or
                      _opt == 'DIM_EXTENSION' or
                      _opt == 'DIM_PRIMARY_TEXT_SIZE' or
                      _opt == 'DIM_SECONDARY_TEXT_SIZE' or
                      _opt == 'DIM_DUAL_MODE_OFFSET' or
                      _opt == 'DIM_POSITION_OFFSET' or
                      _opt == 'DIM_THICKNESS' or
                      _opt == 'DIM_PRIMARY_TEXT_ANGLE' or
                      _opt == 'DIM_SECONDARY_TEXT_ANGLE'):
                    _val = float(_child.getAttribute('val'))
                elif (_opt == 'DIM_PRIMARY_PRECISION' or
                      _opt == 'DIM_SECONDARY_PRECISION' or
                      _opt == 'DIM_PRIMARY_UNITS' or
                      _opt == 'DIM_SECONDARY_UNITS' or
                      _opt == 'DIM_PRIMARY_FONT_WEIGHT' or
                      _opt == 'DIM_SECONDARY_FONT_WEIGHT' or
                      _opt == 'DIM_PRIMARY_FONT_STYLE' or
                      _opt == 'DIM_SECONDARY_FONT_STYLE' or
                      _opt == 'DIM_POSITION' or
                      _opt == 'DIM_ENDPOINT' or
                      _opt == 'DIM_PRIMARY_TEXT_ALIGNMENT' or
                      _opt == 'DIM_SECONDARY_TEXT_ALIGNMENT'):
                    _val = int(_child.getAttribute('val'))
                elif (_opt == 'DIM_PRIMARY_LEADING_ZERO' or
                      _opt == 'DIM_SECONDARY_LEADING_ZERO' or
                      _opt == 'DIM_PRIMARY_TRAILING_DECIMAL' or
                      _opt == 'DIM_SECONDARY_TRAILING_DECIMAL' or
                      _opt == 'DIM_DUAL_MODE' or
                      _opt == 'RADIAL_DIM_DIA_MODE'):
                    _val = _child.getAttribute('val')
                    if _val == 0 or _val == u'0' or _val == u'False':
                        _val = False
                    elif _val == 1 or _val == u'1' or _val == u'True':
                        _val = True
                elif (_opt == 'ANGULAR_DIM_SMALL_ANGLE_MODE' or
                      _opt == 'DIM_PRIMARY_FONT_SIZE' or
                      _opt == 'DIM_SECONDARY_FONT_SIZE'): # obsolete
                    _opt = None
                else:
                    _val = _child.getAttribute('val')
                if _opt is not None:
                    _options[_opt] = _val
        _child = _child.nextSibling
    return _options

def _load_linear_dimensions(node, map):
    # print "in _load_linear_dimensions()"
    _dims = []
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            ((_child.nodeName == "image:LDim") or
             (_child.nodeName == "image:HDim") or
             (_child.nodeName == "image:VDim"))):
            _dimopts = {}
            _id = int(_child.getAttribute("id"))
            _dimopts['id'] = _id
            _ds = int(_child.getAttribute("ds"))
            _dimopts['ds'] = _ds
            assert _ds in map['dimstyle'], "Missing style %d in map" % _ds
            _l1 = int(_child.getAttribute("l1"))
            _dimopts['l1'] = _l1
            _p1 = int(_child.getAttribute("p1"))
            _dimopts['p1'] = _p1
            _l2 = int(_child.getAttribute("l2"))
            _dimopts['l2'] = _l2
            _p2 = int(_child.getAttribute("p2"))
            _dimopts['p2'] = _p2
            _x = float(_child.getAttribute("x"))
            _dimopts['x'] = _x
            _y = float(_child.getAttribute("y"))
            _dimopts['y'] = _y
            _overrides = _load_dim_options(_child, map)
            for _key in _overrides:
                _dimopts[_key] = _overrides[_key]
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _dimopts['hidden'] = True
            if _locked:
                _dimopts['locked'] = True
            _dims.append(_dimopts)
        _child = _child.nextSibling
    return _dims

def _load_radial_dimensions(node, map):
    # print "in _load_radial_dimensions()"
    _rdims = []
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:RDim")):
            _dimopts = {}
            _id = int(_child.getAttribute("id"))
            _dimopts['id'] = _id
            _ds = int(_child.getAttribute("ds"))
            assert _ds in map['dimstyle'], "Missing style %d in map" % _ds
            _dimopts['ds'] = _ds
            _l = int(_child.getAttribute("l"))
            _dimopts['l'] = _l
            _c = int(_child.getAttribute("c"))
            _dimopts['c'] = _c
            _x = float(_child.getAttribute("x"))
            _dimopts['x'] = _x
            _y = float(_child.getAttribute("y"))
            _dimopts['y'] = _y
            _overrides = _load_dim_options(_child, map)
            for _key in _overrides:
                _dimopts[_key] = _overrides[_key]
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _dimopts['hidden'] = True
            if _locked:
                _dimopts['locked'] = True
            _rdims.append(_dimopts)
        _child = _child.nextSibling
    return _rdims

def _load_angular_dimensions(node, map):
    # print "in _load_angular_dimensions()"
    _adims = []
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:ADim")):
            _dimopts = {}
            _id = int(_child.getAttribute("id"))
            _dimopts['id'] = _id
            _ds = int(_child.getAttribute("ds"))
            assert _ds in map['dimstyle'], "Missing style %d in map" % _ds
            _dimopts['ds'] = _ds
            _l1 = int(_child.getAttribute("l1"))
            _dimopts['l1'] = _l1
            _p1 = int(_child.getAttribute("p1"))
            _dimopts['p1'] = _p1
            _l2 = int(_child.getAttribute("l2"))
            _dimopts['l2'] = _l2
            _p2 = int(_child.getAttribute("p2"))
            _dimopts['p2'] = _p2
            _l3 = int(_child.getAttribute("l3"))
            _dimopts['l3'] = _l3
            _p3 = int(_child.getAttribute("p3"))
            _dimopts['p3'] = _p3
            _x = float(_child.getAttribute("x"))
            _dimopts['x'] = _x
            _y = float(_child.getAttribute("y"))
            _dimopts['y'] = _y
            _overrides = _load_dim_options(_child, map)
            for _key in _overrides:
                _dimopts[_key] = _overrides[_key]
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _dimopts['hidden'] = True
            if _locked:
                _dimopts['locked'] = True
            _adims.append(_dimopts)
        _child = _child.nextSibling
    return _adims

def _set_graphic_attrs(obj, node, map):
    _ltid = node.getAttribute("linetype")
    if _ltid != "":
        _ltid = int(_ltid)
        assert _ltid in map['linetype'], "Object linetype index %d not in map: %s" % (_ltid, str(obj))
        _lt = map['linetype'][_ltid]
        obj.setLinetype(_lt)
    _cid = node.getAttribute("color")
    if _cid != "":
        _cid = int(_cid)
        assert _cid in map['color'], "Object color index %d not in map: %s" % (_cid, str(obj))
        _c = map['color'][_cid]
        obj.setColor(_c)
    _th = node.getAttribute("thickness")
    if _th != "":
        _th = float(_th)
        obj.setThickness(_th)

def _get_state_bits(node):
    _vis = True
    _locked = False
    _attr = node.getAttribute("visibility")
    if _attr != "":
        if _attr == 0 or _attr == u'0' or _attr == u'False':
            _vis = False
    _attr = node.getAttribute("locked")
    if _attr != "":
        if _attr == 1 or _attr == u'1' or _attr == u'True':
            _locked = True
    return _vis, _locked
            
def _load_textblocks(image, node, map):
    _layer = image.getActiveLayer()
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:TextBlock")):
            # _id = int(_child.getAttribute("id"))
            _tsid = int(_child.getAttribute("tsid"))
            assert _tsid in map['textstyle'], "TextBlock textstyle id not in map: %d" % _tsid
            _style = map['textstyle'][_tsid]
            _x = float(_child.getAttribute("x"))
            _y = float(_child.getAttribute("y"))
            _text = u''
            if _child.hasChildNodes():
                _lines = []
                _linenode = _child.firstChild
                while _linenode is not None:
                    if ((_linenode.nodeType == xml.dom.Node.ELEMENT_NODE) and
                        (_linenode.nodeName == "image:TextLine")):
                        _text = _linenode.getAttribute("text")
                        _lines.append(unicode(_text))
                    _linenode = _linenode.nextSibling
                #
                # this is lame ...
                #
                if sys.platform == 'mac':
                    _sep = '\r'
                else:
                    _sep = '\n'
                _text = _sep.join(_lines)
            _textblock = text.TextBlock(_x, _y, _text, _style)
            #
            # get any possibly overriden style values
            #
            _attr = _child.getAttribute("fid")
            if _attr != "":
                _fid = int(_attr)
                _family = map['family'][_fid]
                _textblock.setFamily(_family)
            _attr = _child.getAttribute("cid")
            if _attr != "":
                _cid = int(_attr)
                _color = map['color'][_cid]
                _textblock.setColor(_color)
            _attr = _child.getAttribute("weight")
            if _attr != "":
                _weight = text.TextStyle.WEIGHT_NORMAL
                if _attr == 'normal' or _attr == '0':
                    _weight = text.TextStyle.WEIGHT_NORMAL
                elif _attr == 'light' or _attr == '1':
                    _weight = text.TextStyle.WEIGHT_LIGHT
                elif _attr == 'bold' or _attr == '2':
                    _weight = text.TextStyle.WEIGHT_BOLD
                elif _attr == 'heavy' or _attr == '3':
                    _weight = text.TextStyle.WEIGHT_HEAVY
                else:
                    sys.stderr.write("Unknown font weight '%s' - using NORMAL\n" % _attr)
                _textblock.setWeight(_weight)
            _attr = _child.getAttribute("style")
            if _attr != "":
                _style = text.TextStyle.FONT_NORMAL
                if _attr == 'normal' or _attr == '0':
                    _style = text.TextStyle.FONT_NORMAL
                elif _attr == 'oblique' or _attr == '1':
                    _style = text.TextStyle.FONT_OBLIQUE
                elif _attr == 'italic' or _attr == '2':
                    _style = text.TextStyle.FONT_ITALIC
                else:
                    sys.stderr.write("Unknown font style '%s' - using NORMAL\n" % _attr)
                _textblock.setStyle(_style)
            _attr = _child.getAttribute("size")
            if _attr != "":
                _size = float(_attr)
                _textblock.setSize(_size)
            _attr = _child.getAttribute("angle")
            if _attr != "":
                _angle = float(_attr)
                _textblock.setAngle(_angle)
            _attr = _child.getAttribute("halign")
            if _attr != "":
                _align = text.TextStyle.ALIGN_LEFT
                if _attr == 'left' or _attr == '0':
                    _align = text.TextStyle.ALIGN_LEFT
                elif _attr == 'center' or _attr == '1':
                    _align = text.TextStyle.ALIGN_CENTER
                elif _attr == 'right' or _attr == '2':
                    _align = text.TextStyle.ALIGN_RIGHT
                else:
                    sys.stderr.write("Unknown alignment %s - using ALIGN_LEFT\n" % _attr)
                _textblock.setAlignment(_align)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _textblock.setVisibility(False)
            if _locked:
                _locked.append(_textblock)
            _layer.addObject(_textblock)
        _child = _child.nextSibling

def _load_leaders(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Leader")):
            # _id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("p1"))
            assert _pid in _pmap, "Leader p1 index %d not in map!" % _pid
            _p1 = _pmap[_pid]
            _pid = int(_child.getAttribute("p2"))
            assert _pid in _pmap, "Leader p2 index %d not in map!" % _pid
            _p2 = _pmap[_pid]
            _pid = int(_child.getAttribute("p3"))
            assert _pid in _pmap, "Leader p3 index %d not in map!" % _pid
            _p3 = _pmap[_pid]
            _sid = int(_child.getAttribute("style"))
            _size = float(_child.getAttribute("size"))
            assert _sid in map['style'], "Leader style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _leader = leader.Leader(_p1, _p2, _p3, _size, _style)
            _set_graphic_attrs(_leader, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _leader.setVisibility(False)
            if _locked:
                _locked.append(_leader)
            _layer.addObject(_leader)
        _child = _child.nextSibling

def _load_polylines(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Polyline")):
            # _id = int(_child.getAttribute("id"))
            _mpts = eval(_child.getAttribute("points"))
            _pts = []
            for _mpt in _mpts:
                assert _mpt in _pmap, "Polyline point %d not in map!" % _mpt
                _pts.append(_pmap[_mpt])
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Polyline style index %d not in map!" % _sid
            _st = map['style'][_sid]
            _polyline = polyline.Polyline(_pts, _st)
            _set_graphic_attrs(_polyline, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _polyline.setVisibility(False)
            if _locked:
                _locked.append(_polyline)
            _layer.addObject(_polyline)
        _child = _child.nextSibling

def _load_fillets(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _smap = map[_lid]['segment']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Fillet")):
            # _id = int(_child.getAttribute("id"))
            _sid = int(_child.getAttribute("s1"))
            assert _sid in _smap, "Fillet segment s1 %d not in map!" % _sid
            _s1 = _smap[_sid]
            _sid = int(_child.getAttribute("s2"))
            assert _sid in _smap, "Fillet segment s2 %s not in map!" % _sid
            _s2 = _smap[_sid]
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Fillet style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _radius = float(_child.getAttribute("radius"))
            _fillet = segjoint.Fillet(_s1, _s2, _radius, _style)
            _set_graphic_attrs(_fillet, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _fillet.setVisibility(False)
            if _locked:
                _locked.append(_fillet)
            _layer.addObject(_fillet)
        _child = _child.nextSibling

def _load_chamfers(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _smap = map[_lid]['segment']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Chamfer")):
            # _id = int(_child.getAttribute("id"))
            _sid = int(_child.getAttribute("s1"))
            assert _sid in _smap, "Chamfer segment s1 %d not in map!" % _sid
            _s1 = _smap[_sid]
            _sid = int(_child.getAttribute("s2"))
            assert _sid in _smap, "Chamfer segment s2 %s not in map!" % _sid
            _s2 = _smap[_sid]
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Chamfer style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _length = float(_child.getAttribute("length"))
            _chamfer = segjoint.Chamfer(_s1, _s2, _length, _style)
            _set_graphic_attrs(_chamfer, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _chamfer.setVisibility(False)
            if _locked:
                _locked.append(_chamfer)
            _layer.addObject(_chamfer)
        _child = _child.nextSibling

def _load_ccircles(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:CCircle")):
            # _id = int(_child.getAttribute("id"))
            _cid = int(_child.getAttribute("cp"))
            assert _cid in _pmap, "CCircle center index %d not in map!" % _cid
            _cen = _pmap[_cid]
            _rad = float(_child.getAttribute("r"))
            _cc = ccircle.CCircle(_cen, _rad)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _cc.setVisibility(False)
            if _locked:
                _locked.append(_cc)
            _layer.addObject(_cc)
        _child = _child.nextSibling

def _load_clines(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:CLine")):
            # _id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("p1"))
            assert _pid in _pmap, "CLine p1 index %d not in map!" % _pid
            _p1 = _pmap[_pid]
            _pid = int(_child.getAttribute("p2"))
            assert _pid in _pmap, "CLine p2 index %d not in map!" % _pid
            _p2 = _pmap[_pid]
            _cl = cline.CLine(_p1, _p2)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _cl.setVisibility(False)
            if _locked:
                _locked.append(_cl)
            _layer.addObject(_cl)
        _child = _child.nextSibling

def _load_aclines(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:ACLine")):
            #_id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("location"))
            _angle = float(_child.getAttribute("angle"))
            assert _pid in _pmap, "ACLine location index %d not in map!" % _pid
            _loc = _pmap[_pid]
            _acl = acline.ACLine(_loc, _angle)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _acl.setVisibility(False)
            if _locked:
                _locked.append(_acl)
            _layer.addObject(_acl)
        _child = _child.nextSibling

def _load_vclines(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:VCLine")):
            # _id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("location"))
            assert _pid in _pmap, "VCLine location index %d not in map!" % _pid
            _loc = _pmap[_pid]
            _vcl = vcline.VCLine(_loc)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _vcl.setVisibility(False)
            if _locked:
                _locked.append(_vcl)
            _layer.addObject(_vcl)
        _child = _child.nextSibling

def _load_hclines(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:HCLine")):
            # _id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("location"))
            assert _pid in _pmap, "HCLine location index %d not in map!" % _pid
            _loc = _pmap[_pid]
            _hcl = hcline.HCLine(_loc)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _hcl.setVisibility(False)
            if _locked:
                _locked.append(_hcl)
            _layer.addObject(_hcl)
        _child = _child.nextSibling

def _load_arcs(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _amap = {}
    map[_lid]['arc'] = _amap
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Arc")):
            _id = int(_child.getAttribute("id"))
            _cid = int(_child.getAttribute("cp"))
            assert _cid in _pmap, "Arc center index %d not in map!" % _cid
            _cen = _pmap[_cid]
            _rad = float(_child.getAttribute("r"))
            _sa = float(_child.getAttribute("sa"))
            _ea = float(_child.getAttribute("ea"))
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Arc style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _arc = arc.Arc(_cen, _rad, _sa, _ea, _style)
            _set_graphic_attrs(_arc, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _arc.setVisibility(False)
            if _locked:
                _locked.append(_arc)
            _amap[_id] = _arc
            _layer.addObject(_arc)
        _child = _child.nextSibling

def _load_circles(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _cmap = {}
    map[_lid]['circle'] = _cmap
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Circle")):
            _id = int(_child.getAttribute("id"))
            _cid = int(_child.getAttribute("cp"))
            assert _cid in _pmap, "Circle center index %d not in map!" % _cid
            _cen = _pmap[_cid]
            _rad = float(_child.getAttribute("r"))
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Circle style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _circle = circle.Circle(_cen, _rad, _style)
            _set_graphic_attrs(_circle, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _circle.setVisibility(False)
            if _locked:
                _locked.append(_circle)
            _layer.addObject(_circle)
            _cmap[_id] = _circle
        _child = _child.nextSibling

def _load_segments(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = map[_lid]['point']
    _smap = {}
    map[_lid]['segment'] = _smap
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Segment")):
            _id = int(_child.getAttribute("id"))
            _pid = int(_child.getAttribute("p1"))
            assert _pid in _pmap, "Segment p1 index %d not in map!" % _pid
            _p1 = _pmap[_pid]
            _pid = int(_child.getAttribute("p2"))
            assert _pid in _pmap, "Segment p2 index %d not in map!" % _pid
            _p2 = _pmap[_pid]
            _sid = int(_child.getAttribute("style"))
            assert _sid in map['style'], "Segment style index %d not in map!" % _sid
            _style = map['style'][_sid]
            _seg = segment.Segment(_p1, _p2, _style)
            _set_graphic_attrs(_seg, _child, map)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _seg.setVisibility(False)
            if _locked:
                _locked.append(_seg)
            _layer.addObject(_seg)
            _smap[_id] = _seg
        _child = _child.nextSibling

def _load_points(image, node, map):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    _pmap = {}
    map[_lid]['point'] = _pmap
    _locked = map['locked']
    _child = node.firstChild
    while _child is not None:
        if ((_child.nodeType == xml.dom.Node.ELEMENT_NODE) and
            (_child.nodeName == "image:Point")):
            _id = int(_child.getAttribute("id"))
            _x = float(_child.getAttribute("x"))
            _y = float(_child.getAttribute("y"))
            _p = point.Point(_x, _y)
            _vis, _locked = _get_state_bits(_child)
            if not _vis:
                _p.setVisibility(False)
            if _locked:
                _locked.append(_p)
            _layer.addObject(_p)                
            _pmap[_id] = _p
        _child = _child.nextSibling

def _load_layer(image, node, map, dimmap):
    _layer = image.getActiveLayer()
    _lid = id(_layer)
    map[_lid] = {}
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            _name = _child.nodeName
            if _name == "image:Points":
                _load_points(image, _child, map)
            elif _name == "image:Segments":
                _load_segments(image, _child, map)
            elif _name == "image:Circles":
                _load_circles(image, _child, map)
            elif _name == "image:Arcs":
                _load_arcs(image, _child, map)
            elif _name == "image:HCLines":
                _load_hclines(image, _child, map)
            elif _name == "image:VCLines":
                _load_vclines(image, _child, map)
            elif _name == "image:ACLines":
                _load_aclines(image, _child, map)
            elif _name == "image:CLines":
                _load_clines(image, _child, map)
            elif _name == "image:CCircles":
                _load_ccircles(image, _child, map)
            elif _name == "image:Fillets":
                _load_fillets(image, _child, map)
            elif _name == "image:Chamfers":
                _load_chamfers(image, _child, map)
            elif _name == "image:Leaders":
                _load_leaders(image, _child, map)
            elif _name == "image:Polylines":
                _load_polylines(image, _child, map)
            elif _name == "image:TextBlocks":
                _load_textblocks(image, _child, map)
            elif _name == "image:LDims":
                for _dim in _load_linear_dimensions(_child, map):
                    dimmap.saveDim(_layer, 'linear', _dim)
            elif _name == "image:HDims":
                for _dim in _load_linear_dimensions(_child, map):
                    dimmap.saveDim(_layer, 'horizontal', _dim)
            elif _name == "image:VDims":
                for _dim in _load_linear_dimensions(_child, map):
                    dimmap.saveDim(_layer, 'vertical', _dim)
            elif _name == "image:RDims":
                for _dim in _load_radial_dimensions(_child, map):
                    dimmap.saveDim(_layer, 'radial', _dim)
            elif _name == "image:ADims":
                for _dim in _load_angular_dimensions(_child, map):
                    dimmap.saveDim(_layer, 'angular', _dim)
        _child = _child.nextSibling

def _add_linear_dimension(dim, map, dimtype, image, lyr):
    assert 'ds' in dim, "Dim missing key 'ds': " + `dim`
    _dsid = dim['ds']
    assert _dsid in map['dimstyle'], "Missing dimstyle id %d" % _dsid
    _ds = map['dimstyle'][_dsid]
    del dim['ds']
    assert 'l1' in dim, "Dim missing key 'l1': " + `dim`
    _lid = dim['l1']
    del dim['l1']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _l1 = map['layer'][_lid]
    assert 'p1' in dim, "Dim missing key 'p1': " + `dim`
    _pid = dim['p1']
    del dim['p1']
    _lid = id(_l1)
    assert _pid in map[_lid]['point'], "Missing p1 key %d in map" % _pid
    _p1 = map[_lid]['point'][_pid]
    assert 'l2' in dim, "Dim missing key 'l2': " + `dim`
    _lid = dim['l2']
    del dim['l2']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _l2 = map['layer'][_lid]
    assert 'p2' in dim, "Dim missing key 'p2': " + `dim`
    _pid = dim['p2']
    del dim['p2']
    _lid = id(_l2)
    assert _pid in map[_lid]['point'], "Missing p2 key %d in map" % _pid
    _p2 = map[_lid]['point'][_pid]
    assert 'x' in dim, "Dim missing key 'x': " + `dim`
    _x = dim['x']
    del dim['x']
    assert 'y' in dim, "Dim missing key 'y': " + `dim`
    _y = dim['y']
    del dim['y']
    _ldim = dimtype(_p1, _p2, _x, _y, _ds)
    if 'id' in dim:
        del dim['id']
    # print "remaining keys ..."
    # for _key in dim:
        # print "key: %s" % _key
        # print "value: " + `dim[_key]`
    if len(dim):
        _apply_dim_overrides(_ldim, dim)
    if 'hidden' in dim:
        _ldim.setVisibility(False)
    if 'locked' in dim:
        _ldim.setLock(True)
    image.ignore('modified')
    try:
        image.addObject(_ldim, lyr)
    finally:
        image.receive('modified')
    _log = lyr.getLog() # fixme - this will go away
    if _log is not None:
        _log.clear()

def _add_radial_dimension(dim, map, image, lyr):
    assert 'id' in dim, "Dim missing key 'id': " + `dim`
    assert 'ds' in dim, "Dim missing key 'ds': " + `dim`
    _dsid = dim['ds']
    assert _dsid in map['dimstyle'], "Missing dimstyle id %d" % _dsid
    _ds = map['dimstyle'][_dsid]
    del dim['ds']
    assert 'l' in dim, "Dim missing key 'l': " + `dim`
    _lid = dim['l']
    del dim['l']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _cl = map['layer'][_lid]
    assert 'c' in dim, "Dim missing key 'c': " + `dim`
    _cid = dim['c']
    del dim['c']
    _lid = id(_cl)
    assert _cid in map[_lid]['circle'], "Missing circle key %d" % _cid
    _circ = map[_lid]['circle'][_cid]
    assert 'x' in dim, "Dim missing key 'x': " + `dim`
    _x = dim['x']
    del dim['x']
    assert 'y' in dim, "Dim missing key 'y': " + `dim`
    _y = dim['y']
    del dim['y']
    _rdim = dimension.RadialDimension(_circ, _x, _y, _ds)
    if 'id' in dim:
        del dim['id']
    # print "remaining keys ..."
    # for _key in dim:
        # print "key: %s" % key
        # print "value: " + `dim[_key]`
    if len(dim):
        _apply_dim_overrides(_rdim, dim)
    if 'hidden' in dim:
        _rdim.setVisibility(False)
    if 'locked' in dim:
        _rdim.setLock(True)
    image.ignore('modified')
    try:
        image.addObject(_rdim, lyr)
    finally:
        image.receive('modified')
    _log = lyr.getLog() # fixme - this will go away
    if _log is not None:
        _log.clear()

def _add_angular_dimension(dim, map, image, lyr):
    assert 'id' in dim, "Dim missing key 'id': " + `dim`
    assert 'ds' in dim, "Dim missing key 'ds': " + `dim`
    _dsid = dim['ds']
    assert _dsid in map['dimstyle'], "Missing dimstyle id %d" % _dsid
    _ds = map['dimstyle'][_dsid]
    del dim['ds']
    assert 'l1' in dim, "Dim missing key 'l1': " + `dim`
    _lid = dim['l1']
    del dim['l1']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _l1 = map['layer'][_lid]
    assert 'p1' in dim, "Dim missing key 'p1': " + `dim`
    _pid = dim['p1']
    del dim['p1']
    _lid = id(_l1)
    assert _pid in map[_lid]['point'], "Missing p1 id %d" % _pid
    _p1 = map[_lid]['point'][_pid]
    assert 'l2' in dim, "Dim missing key 'l2': " + `dim`
    _lid = dim['l2']
    del dim['l2']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _l2 = map['layer'][_lid]
    assert 'p2' in dim, "Dim missing key 'p2': " + `dim`
    _pid = dim['p2']
    del dim['p2']
    _lid = id(_l2)
    assert _pid in map[_lid]['point'], "Missing p2 id %d" % _pid
    _p2 = map[_lid]['point'][_pid]
    assert 'l3' in dim, "Dim missing key 'l3': " + `dim`
    _lid = dim['l3']
    del dim['l3']
    assert _lid in map['layer'], "Missing layer id %d" % _lid
    _l3 = map['layer'][_lid]
    assert 'p3' in dim, "Dim missing key 'p3': " + `dim`
    _pid = dim['p3']
    del dim['p3']
    _lid = id(_l3)
    assert _pid in map[_lid]['point'], "Missing p3 id %d" % _pid
    _p3 = map[_lid]['point'][_pid]
    assert 'x' in dim, "Dim missing key 'x': " + `dim`
    _x = dim['x']
    del dim['x']
    assert 'y' in dim, "Dim missing key 'y': " + `dim`
    _y = dim['y']
    del dim['y']
    _adim = dimension.AngularDimension(_p1, _p2, _p3, _x, _y, _ds)
    if 'id' in dim:
        del dim['id']
    # print "remaining keys ..."
    # for _key in dim:
        # print "key: %s" % _key
        # print "value: " + `dim[_key]`
    if len(dim):
        _apply_dim_overrides(_adim, dim)
    if 'hidden' in dim:
        _adim.setVisibility(False)
    if 'locked' in dim:
        _adim.setLock(True)
    image.ignore('modified')
    try:
        image.addObject(_adim, lyr)
    finally:
        image.receive('modified')
    _log = lyr.getLog() # fixme - this will go away
    if _log is not None:
        _log.clear()

def _load_layers(image, node, map):
    _lmap = {}
    map['layer'] = _lmap
    map['locked'] = []
    _dimmap = DimMap()
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:Layer":
                _id = int(_child.getAttribute("id"))
                _name = str(_child.getAttribute("name"))
                _scale = float(_child.getAttribute("scale"))
                _pid = _child.getAttribute("parent")
                if _pid == "": # top layer created with image
                    _layer = image.getTopLayer()
                    _layer.setName(_name)
                else:
                    _pid = int(_pid)
                    assert _pid in _lmap, "Layer parent id %d missing in map!" % _pid
                    _parent = _lmap[_pid]
                    _layer = layer.Layer(_name)
                    image.muteMessage('modified')
                    try:
                        image.addChildLayer(_layer, _parent)
                    finally:
                        image.unmuteMessage('modified')
                _layer.setScale(_scale)
                _vis, _locked = _get_state_bits(_child)
                if not _vis:
                    _layer.setVisibility(False)
                if _locked:
                    _locked.append(_layer)
                image.setActiveLayer(_layer)
                _lmap[_id] = _layer
                image.ignore('modified')
                try:
                    _load_layer(image, _child, map, _dimmap)
                finally:
                    image.receive('modified')
                _log = _layer.getLog() # fixme - this will go away
                if _log is not None:
                    _log.clear()
        _child = _child.nextSibling
    if _dimmap:
        for _layer in _dimmap.getLayers():
            for _dimtype in _dimmap.getLayerDimTypes(_layer):
                for _dim in _dimmap.getLayerDims(_layer, _dimtype):
                    if _dimtype == 'linear':
                        _add_linear_dimension(_dim, map,
                                              dimension.LinearDimension,
                                              image, _layer)
                    elif _dimtype == 'horizontal':
                        _add_linear_dimension(_dim, map,
                                              dimension.HorizontalDimension,
                                              image, _layer)
                    elif _dimtype == 'vertical':
                        _add_linear_dimension(_dim, map,
                                              dimension.VerticalDimension,
                                              image, _layer)
                    elif _dimtype == 'radial':
                        _add_radial_dimension(_dim, map, image, _layer)
                    elif _dimtype == 'angular':
                        _add_angular_dimension(_dim, map, image, _layer)
                    else:
                        raise TypeError, "Unknown dimension type %s" % _dimtype

def _load_textstyles(image, node, map):
    map['textstyle'] = {}
    _gts = globals.prefs['TEXTSTYLES']
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:TextStyle":
                _id = int(_child.getAttribute("id"))
                _name= _child.getAttribute("name")
                _cid = int(_child.getAttribute("cid"))
                assert _cid in map['color'], "Color ID missing from map: %d" % _cid
                _color = map['color'][_cid]
                _fid = int(_child.getAttribute("fid"))
                assert _fid in map['family'], "Font ID missing from map: %d" % _fid
                _family = map['family'][_fid]
                _attr = _child.getAttribute("weight")
                _weight = text.TextStyle.WEIGHT_NORMAL
                if _attr == 'normal' or _attr == '0':
                    _weight = text.TextStyle.WEIGHT_NORMAL
                elif _attr == 'light' or _attr == '1':
                    _weight = text.TextStyle.WEIGHT_LIGHT
                elif _attr == 'bold' or _attr == '2':
                    _weight = text.TextStyle.WEIGHT_BOLD
                elif _attr == 'heavy' or _attr == '3':
                    _weight = text.TextStyle.WEIGHT_HEAVY
                else:
                    sys.stderr.write("Unknown font weight '%s' - using NORMAL\n" % _attr)
                #
                # size used to be integer in older TextStyles
                #
                _size = float(_child.getAttribute("size"))
                _attr = _child.getAttribute("style")
                _style = text.TextStyle.FONT_NORMAL
                if _attr == 'normal' or _attr == '0':
                    _style = text.TextStyle.FONT_NORMAL
                elif _attr == 'oblique' or _attr == '1':
                    _style = text.TextStyle.FONT_OBLIQUE
                elif _attr == 'italic' or _attr == '2':
                    _style = text.TextStyle.FONT_ITALIC
                else:
                    sys.stderr.write("Unknown font style '%s' - using NORMAL\n" % _attr)
                #
                # angle not present in older TextStyles
                #
                _angle = 0.0
                _attr = _child.getAttribute("angle")
                if _attr != "":
                    _angle = float(_attr)
                #
                # alignment not present in older TextStyles
                #
                _align = text.TextStyle.ALIGN_LEFT
                _attr = _child.getAttribute("halign")
                if _attr != "":
                    if _attr == 'left' or _attr == '0':
                        _align = text.TextStyle.ALIGN_LEFT
                    elif _attr == 'center' or _attr == '1':
                        _align = text.TextStyle.ALIGN_CENTER
                    elif _attr == 'right' or _attr == '2':
                        _align = text.TextStyle.ALIGN_RIGHT
                    else:
                        sys.stderr.write("Unknown alignment %s - using ALIGN_LEFT\n" % _attr)
                _textstyle = None
                for _ts in _gts:
                    # print "Testing global TextStyle '%s'" % _ts.getName()
                    if ((_ts.getName() == _name) and
                        (_ts.getFamily() == _family) and
                        (abs(_ts.getSize() - _size) < 1e-10) and
                        (_ts.getStyle() == _style) and
                        (_ts.getWeight() == _weight) and
                        (_ts.getColor() == _color) and
                        (abs(_ts.getAngle() - _angle) < 1e-10) and
                        (_ts.getAlignment() == _align)):
                        # print "TextStyle/global match"
                        # print "Global TextStyle: " + `_ts`
                        _textstyle = _ts
                        break
                if _textstyle is None:
                    # print "No matching TextStyle"
                    # print "Name: %s" % _name
                    # print "Family: %s" % _family
                    # print "Size: %f" % _size
                    # print "Style: %d" % _style
                    # print "Weight: %d" % _weight
                    # print "Angle: %f" % _angle
                    # print "Align: %d" % _align
                    # print "Color: %s" % str(_color)
                    _textstyle = text.TextStyle(_name,
                                                family=_family,
                                                size=_size,
                                                style=_style,
                                                weight=_weight,
                                                color=_color,
                                                angle=_angle,
                                                align=_align)
                image.addTextStyle(_textstyle)
                map['textstyle'][_id] = _textstyle
        _child = _child.nextSibling

def _load_dimstyles(image, node, map):
    map['dimstyle'] = {}
    _gds = globals.prefs['DIMSTYLES']
    _dsk = dimension.DimStyle.getDimStyleOptions()
    _dds = dimension.Dimension.getDefaultDimStyle()
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:DimStyle":
                _id = int(_child.getAttribute("id"))
                _name = _child.getAttribute("name")
                _dsopts = _load_dim_options(_child, map)
                # print "print keys ..."
                # _dskeys = _dsopts.keys()
                # _dskeys.sort()
                # for key in dskeys:
                    # print "key: " + key + "; value: " + `dsopts[key]`
                _dimstyle = None
                for _ds in _gds:
                    _match = False
                    if _name == _ds.getName():
                        _match = True
                        for _k in _dsk:
                            if _k in _dsopts:
                                _v = _dsopts[_k]
                            else:
                                _v = _dds.getOption(_k)
                            _dv = _ds.getOption(_k)
                            if ((_k == 'DIM_PRIMARY_TEXT_SIZE') or
                                (_k == 'DIM_PRIMARY_TEXT_ANGLE') or
                                (_k == 'DIM_SECONDARY_TEXT_SIZE') or
                                (_k == 'DIM_SECONDARY_TEXT_ANGLE') or
                                (_k == 'DIM_OFFSET') or
                                (_k == 'DIM_EXTENSION') or
                                (_k == 'DIM_THICKNESS') or
                                (_k == 'DIM_ENDPOINT_SIZE') or
                                (_k == 'DIM_POSITION_OFFSET') or
                                (_k == 'DIM_DUAL_MODE_OFFSET')):
                                if abs(_v - _dv) > 1e-10:
                                    _match = False
                            else:
                                if _v != _dv:
                                    _match = False
                            if not _match:
                                break
                    if _match:
                        _dimstyle = _ds
                        break
                if _dimstyle is None:
                    _dimstyle = dimension.DimStyle(_name, _dsopts)
                image.addDimStyle(_dimstyle)
                map['dimstyle'][_id] = _dimstyle
        _child = _child.nextSibling

def _load_font_families(image, node, map):
    map['family'] = {}
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:FontFamily":
                _id = int(_child.getAttribute("id"))
                _family = str(_child.getAttribute("name"))
                image.addFont(_family)
                map['family'][_id] = _family
        _child = _child.nextSibling

def _load_styles(image, node, map):
    map['style'] = {}
    _gs = globals.prefs['STYLES']
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:Style":
                _id = int(_child.getAttribute("id"))
                _cid = int(_child.getAttribute("cid"))
                assert _cid in map['color'], "Color index %d missing" % _cid
                _color = map['color'][_cid]
                _ltid = int(_child.getAttribute("ltid"))
                assert _ltid in map['linetype'], "Linetype index %d missing" % _ltid
                _lt = map['linetype'][_ltid]
                _name = _child.getAttribute("name")
                _th = float(_child.getAttribute("thickness"))
                _style = None
                for _st in _gs:
                    if ((_name == _st.getName()) and
                        (_color == _st.getColor()) and
                        (_lt == _st.getLinetype()) and
                        (abs(_th - _st.getThickness()) < 1e-10)):
                        _style = _st
                        break
                if _style is None:
                    _style = style.Style(_name, _lt, _color, _th)
                image.addStyle(_style)
                map['style'][_id] = _style
        _child = _child.nextSibling

def _load_globals(image, node, map):
#
# for now, assumes globals are ONLY colors
#
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:Global":
                _key = str(_child.getAttribute("key"))
                _cid = int(_child.getAttribute("cid"))
                assert _cid in map['color'], "Color index %d missing" % _cid
                _color = map['color'][_cid]
                image.setOption(_key, _color)
        _child = _child.nextSibling


def _load_linetypes(image, node, map):
    map['linetype'] = {}
    _glt = globals.prefs['LINETYPES']
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:Linetype":
                _id = int(_child.getAttribute("id"))
                _name = _child.getAttribute("name")
                _attr = _child.getAttribute("pattern")
                _list = None
                if _attr != "None":
                    _list = eval(_attr) # can this be done without eval()?
                _linetype = None
                for _lt in _glt:
                    if _name == _lt.getName():
                        _dlist = _lt.getList()
                        if ((_list is None and _dlist is None) or
                            ((type(_list) == type(_dlist)) and
                             (_list == _dlist))):
                            _linetype = _lt
                            break
                if _linetype is None:
                    _linetype = linetype.Linetype(_name, _list)
                image.addLinetype(_linetype)
                map['linetype'][_id] = _linetype
        _child = _child.nextSibling

def _load_colors(image, node, map):
    map['color'] = {}
    _gc = globals.prefs['COLORS']
    _child = node.firstChild
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            if _child.nodeName == "image:Color":
                _id = int(_child.getAttribute("id"))
                _r = int(_child.getAttribute("r"))
                _g = int(_child.getAttribute("g"))
                _b = int(_child.getAttribute("b"))
                _color = None
                for _c in _gc:
                    if _r == _c.r and _g == _c.g and _b == _c.b:
                        _color = _c
                        break
                if _color is None:
                    _color = color.Color(_r, _g, _b)
                image.addColor(_color)
                map['color'][_id] = _color
        _child = _child.nextSibling

def load_image(image, filehandle):
    """Load an image from a filename or standard input

load_image(image, filehandle)

The argument image should be an empty image. The
filehandle argument should be an opened file object
that can be passed to the XML parser.
    """
    _objmap = {}
    _doc = xml.dom.minidom.parse(filehandle)
    _root = _doc.documentElement
    if _root.nodeName != "image:Image":
        _doc.unlink()
        raise ValueError, "Expected 'image:Image' but got '%s' as document root!" % _root.name
    _child = _root.firstChild
    while _child.nodeType == xml.dom.Node.TEXT_NODE:
        _child = _child.nextSibling
    if _child.nodeName != "image:Colors":
        _doc.unlink()
        raise ValueError, "Expected 'image:Colors' but got '%s'" % _child.nodeName
    _load_colors(image, _child, _objmap)
    _child = _child.nextSibling
    while _child.nodeType == xml.dom.Node.TEXT_NODE:
        _child = _child.nextSibling
    if _child.nodeName != "image:Linetypes":
        raise ValueError, "Expected 'image:Linetypes' but got '%s'" % _child.nodeName
    _load_linetypes(image, _child, _objmap)
    _child = _child.nextSibling
    while _child.nodeType == xml.dom.Node.TEXT_NODE:
        _child = _child.nextSibling
    if _child.nodeName != "image:Styles":
        _doc.unlink()
        raise ValueError, "Expected 'image:Styles' but got '%s'" % _child.nodeName
    _load_styles(image, _child, _objmap)
    _child = _child.nextSibling
    while _child is not None:
        if _child.nodeType == xml.dom.Node.ELEMENT_NODE:
            _name = _child.nodeName
            if _name == "image:Units":
                _attr = _child.getAttribute("unit")
                if _attr == 'millimeters' or _attr == '0':
                    _unit = units.MILLIMETERS
                elif _attr == 'micrometers' or _attr == '1':
                    _unit = units.MICROMETERS
                elif _attr == 'meters' or _attr == '2':
                    _unit = units.METERS
                elif _attr == 'kilometers' or _attr == '3':
                    _unit = units.KILOMETERS
                elif _attr == 'inches' or _attr == '4':
                    _unit = units.INCHES
                elif _attr == 'feet' or _attr == '5':
                    _unit = units.FEET
                elif _attr == 'yards' or _attr == '6':
                    _unit = units.YARDS
                elif _attr == 'miles' or _attr == '7':
                    _unit = units.MILES
                else:
                    sys.stderr.write("Unknown unit '%s' - using MILLIMETERS\n" % _attr)
                    _unit = units.MILLIMETERS
                image.setUnits(_unit)
            elif _name == "image:FontFamilies":
                _load_font_families(image, _child, _objmap)
            elif _name == "image:DimStyles":
                _load_dimstyles(image, _child, _objmap)
            elif _name == "image:TextStyles":
                _load_textstyles(image, _child, _objmap)
            elif _name == "image:Globals":
                _load_globals(image, _child, _objmap)
            elif _name == "image:Layers":
                _load_layers(image, _child, _objmap)
                for _obj in _objmap['locked']:
                    _obj.setLock(True)
        _child = _child.nextSibling
    _doc.unlink()
