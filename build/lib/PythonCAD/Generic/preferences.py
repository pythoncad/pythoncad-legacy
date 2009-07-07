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
# This code handles loading the global and user preference
# files
#

import imp
import string
import types
import sys
import os

from PythonCAD.Generic import globals
from PythonCAD.Generic import units
from PythonCAD.Generic import text
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic import dimension
from PythonCAD.Generic import graphicobject

#
# global variables
#

pref_file = '/etc/pythoncad/prefs.py'

#

def _test_font_weight(val):
    _weight = None
    try:
        _weight = text.TextStyle.getWeightFromString(val)
    except:
        sys.stderr.write("invalid font weight: '" + str(val) + "'\n")
    return _weight

def _test_font_style(val):
    _style = None
    try:
        _style = text.TextStyle.getStyleFromString(val)
    except:
        sys.stderr.write("Invalid font style: '" + str(val) + "'\n")
    return _style

def _test_color(val):
    _color = None
    try:
        _c = color.Color(val)
        if _c in globals.colors:
            _color = globals.colors[_c]
        else:
            globals.colors[_c] = _c            
        if _color is None:
            _color = _c
    except:
        sys.stderr.write("Invalid color: '%s'\n" % val)
    return _color

def _test_dim_position(val):
    _pos = None
    try:
        _pos = dimension.Dimension.getPositionFromString(val)
    except:
        sys.stderr.write("Invalid dimension position: '" + str(val) + "'\n")
    return _pos

def _test_dim_endpoint(val):
    _ept = None
    try:
        _ept = dimension.Dimension.getEndpointTypeFromString(val)
    except:
        sys.stderr.write("Invalid dimension endpoint: '" + str(val) + "'\n")
    return _ept

def _test_units(val):
    _unit = None
    try:
        _unit = units.Unit.getUnitFromString(val)
    except:
        sys.stderr.write("Invalid unit: '" + str(val) + "'\n")
    return _unit

def _test_boolean(val):
    _bool = None
    if val is True or val is False:
        _bool = val
    else:
        sys.stderr.write("Invalid boolean flag: '%s'\n" % val)
    return _bool

def _test_float(val):
    _float = None
    if isinstance(val, float):
        _float = val
    else:
        try:
            _float = float(val)
        except:
            sys.stderr.write("Invalid float value: '%s'\n" % val)
    return _float

def _test_int(val):
    _int = None
    if isinstance(val, int):
        _int = val
    else:
        try:
            _int = int(val)
        except:
            sys.stderr.write("Invalid integer value: '%s'\n" % val)
    return _int

def _test_unicode(val):
    _uni = None
    if isinstance(val, unicode):
        _uni = val
    else:
        try:
            _uni = unicode(val)
        except:
            sys.stderr.write("Invalid unicode string: '%s'\n" % val)
    return _uni

def initialize_prefs():
    """This method sets the initial default value for image variables.

initialize_prefs()
    """
    #
    # default dimension parameters
    #
    globals.prefs['DIMSTYLES'] = [dimension.Dimension.getDefaultDimStyle()]
    globals.prefs['DEFAULT_DIMSTYLE'] = None
    #
    # drawing and text parameters
    #
    _textstyles = [text.TextBlock.getDefaultTextStyle()]
    _textstyles.append(dimension.DimString.getDefaultTextStyle())
    globals.prefs['TEXTSTYLES'] = _textstyles
    globals.prefs['DEFAULT_TEXTSTYLE'] = None
    #
    # miscellaneous things
    #
    globals.prefs['USER_PREFS'] = True
    #
    # colors
    #
    # these will be replaced ...
    #
    _colors = []
    _red = color.Color(255,0,0)
    _colors.append(_red)
    _green = color.Color(0,255,0)
    _colors.append(_green)
    _blue = color.Color(0,0,255)
    _colors.append(_blue)
    _violet = color.Color(255,0,255)
    _colors.append(_violet)
    _yellow = color.Color(255,255,0)
    _colors.append(_yellow)
    _cyan = color.Color(0,255,255)
    _colors.append(_cyan)
    _white = color.Color(255,255,255)
    _colors.append(_white)
    _black = color.Color(0,0,0)
    _colors.append(_black)
    globals.prefs['COLORS'] = _colors
    #
    # linetypes
    #
    # these will be replaced
    #
    _linetypes = []
    _solid = linetype.Linetype(u'Solid')
    _linetypes.append(_solid)
    _dash1 = linetype.Linetype(u'Dash1', [4,1])
    _linetypes.append(_dash1)
    _dash2 = linetype.Linetype(u'Dash2', [8,2])
    _linetypes.append(_dash2)
    _dash3 = linetype.Linetype(u'Dash3', [12,2])
    _linetypes.append(_dash3)
    _dash4 = linetype.Linetype(u'Dash4', [10,2,2,2])
    _linetypes.append(_dash4)
    _dash5 = linetype.Linetype(u'Dash5', [15,5,5,5])
    _linetypes.append(_dash5)
    globals.prefs['LINETYPES'] = _linetypes
    #
    # line styles
    #
    # these will be replaced
    #
    _styles = []
    _dst = graphicobject.GraphicObject.getDefaultStyle()
    _styles.append(_dst)
    globals.prefs['STANDARD_STYLE'] = _dst
    _st = style.Style('Solid White Line', _solid, _white, 1.0)    
    _styles.append(_st)
    _st = style.Style('Solid Black Line', _solid, _black, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Red Line', _dash1, _red, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Green Line', _dash1, _green, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Blue Line', _dash1, _blue, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Yellow Line', _dash2, _yellow, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Violet Line', _dash2, _violet, 1.0)
    _styles.append(_st)
    _st = style.Style('Dashed Cyan Line', _dash2, _cyan, 1.0)
    _styles.append(_st)
    globals.prefs['STYLES'] = _styles
    globals.prefs['DEFAULT_STYLE'] = _dst

#
# validate the available options and set them if they seem alright
#

def _set_units(prefmod):
    _unit = _test_units(prefmod.units)
    if _unit is not None:
        globals.prefs['UNITS'] = _unit

def _set_user_prefs(prefmod):
    _flag = _test_boolean(prefmod.user_prefs)
    if _flag is not None:
        globals.prefs['USER_PREFS'] = _flag

def _set_dim_style(prefmod):
    _obj = prefmod.dim_style
    if isinstance(_obj, dict):
        try:
            _dstyle = _parse_dimstyle(_obj)
            globals.prefs['DIM_STYLE'] = _dstyle
            for _key in _dstyle.getOptions():
                _value = _dstyle.getOption(_key)
                globals.prefs[_key] = _value
            _color = _dstyle.getOption('DIM_COLOR')
            _colors = globals.prefs['COLORS']
            if _color not in _colors:
                _colors.append(_color)
        except StandardError, _e:
            sys.stderr.write("Invalid DimStyle: " + _e + "\n")
    else:
        sys.stderr.write("Invalid DimStyle: " + str(_obj) +"\n")

def _set_primary_font_family(prefmod):
    _family = prefmod.dim_primary_font_family
    if isinstance(_family, types.StringTypes) and _family != "":
        globals.prefs['DIM_PRIMARY_FONT_FAMILY'] = _family
    else:
        sys.stderr.write("Invalid primary font family: " + str(_family) + "\n")

def _set_primary_font_size(prefmod):
    sys.stderr.write("Variable 'dim_primary_font_size' is obsolete - use 'dim_primary_text_size'\n")

def _set_primary_text_size(prefmod):
    _size = _test_float(prefmod.dim_primary_text_size)
    if _size is not None:
        if _size > 0.0:
            globals.prefs['DIM_PRIMARY_TEXT_SIZE'] = _size
        else:
            sys.stderr.write("Invalid primary text size: %g\n" % _size)

def _set_primary_font_weight(prefmod):
    _weight = _test_font_weight(prefmod.dim_primary_font_weight)
    if _weight is not None:
        globals.prefs['DIM_PRIMARY_FONT_WEIGHT'] = _weight

def _set_primary_font_style(prefmod):
    _style = _test_font_style(prefmod.dim_primary_font_style)
    if _style is not None:
        globals.prefs['DIM_PRIMARY_FONT_STYLE'] = _style

def _set_primary_font_color(prefmod):
    _color = _test_color(prefmod.dim_primary_font_color)
    if _color is not None:
        globals.prefs['DIM_PRIMARY_FONT_COLOR'] = _color
        _colors = globals.prefs['COLORS']
        if _color not in _colors:
            _colors.append(_color)

def _set_primary_text_angle(prefmod):
    _angle = _test_float(prefmod.dim_primary_text_angle)
    if _angle is not None:
        globals.prefs['DIM_PRIMARY_TEXT_ANGLE'] = _angle
    else:
        sys.stderr.write("Invalid primary text angle: %g\n" % _angle)

def _set_primary_text_alignment(prefmod):
    _pta = prefmod.dim_primary_text_alignment
    try:
        _align = text.TextStyle.getAlignmentFromString(_pta)
        globals.prefs['DIM_PRIMARY_TEXT_ALIGNMENT'] = _align
    except:
        sys.stederr.write("Invalid primary text alignment: " + str(_pta))

def _set_primary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.dim_primary_prefix)
    if _prefix is not None:
        globals.prefs['DIM_PRIMARY_PREFIX'] = _prefix

def _set_primary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.dim_primary_suffix)
    if _suffix is not None:
        globals.prefs['DIM_PRIMARY_SUFFIX'] = _suffix

def _set_primary_precision(prefmod):
    _prec = _test_int(prefmod.dim_primary_precision)
    if _prec is not None:
        if _prec < 0 or _prec > 15:
            sys.stderr.write("Invalid primary dimension precision: %d\n" % _prec)
        else:
            globals.prefs['DIM_PRIMARY_PRECISION'] = _prec

def _set_primary_units(prefmod):
    _unit = _test_units(prefmod.dim_primary_units)
    if _unit is not None:
        globals.prefs['DIM_PRIMARY_UNITS'] = _unit

def _set_primary_print_zero(prefmod):
    _flag = _test_boolean(prefmod.dim_primary_print_zero)
    if _flag is not None:
        globals.prefs['DIM_PRIMARY_LEADING_ZERO'] = _flag

def _set_primary_trail_decimal(prefmod):
    _flag = _test_boolean(prefmod.dim_primary_trailing_decimal)
    if _flag is not None:
        globals.prefs['DIM_PRIMARY_TRAILING_DECIMAL'] = _flag

def _set_secondary_font_family(prefmod):
    _family = prefmod.dim_secondary_font_family
    if isinstance(_family, types.StringTypes) and _family != "":
        globals.prefs['DIM_SECONDARY_FONT_FAMILY'] = _family
    else:
        sys.stderr.write("Invalid secondary font family: " + str(_family) + "\n")

def _set_secondary_font_size(prefmod):
    sys.stderr.write("Variable 'dim_secondary_font_size' is obsolete - use 'dim_secondary_text_size'\n")

def _set_secondary_text_size(prefmod):
    _size = _test_float(prefmod.dim_secondary_text_size)
    if _size is not None:
        if _size > 0.0:
            globals.prefs['DIM_SECONDARY_TEXT_SIZE'] = _size
        else:
            sys.stderr.write("Invalid secondary text size: %g\n" % _size)

def _set_secondary_font_weight(prefmod):
    _weight = _test_font_weight(prefmod.dim_secondary_font_weight)
    if _weight is not None:
        globals.prefs['DIM_SECONDARY_FONT_WEIGHT'] = _weight

def _set_secondary_font_style(prefmod):
    _style = _test_font_style(prefmod.dim_secondary_font_style)
    if _style is not None:
        globals.prefs['DIM_SECONDARY_FONT_STYLE'] = _style

def _set_secondary_font_color(prefmod):
    _color = _test_color(prefmod.dim_secondary_font_color)
    if _color is not None:
        globals.prefs['DIM_SECONDARY_FONT_COLOR'] = _color
        _colors = globals.prefs['COLORS']
        if _color not in _colors:
            _colors.append(_color)

def _set_secondary_text_angle(prefmod):
    _angle = _test_float(prefmod.dim_secondary_text_angle)
    if _angle is not None:
        globals.prefs['DIM_SECONDARY_TEXT_ANGLE'] = _angle
    else:
        sys.stderr.write("Invalid secondary text angle: %g\n" % _angle)

def _set_secondary_text_alignment(prefmod):
    _sta = prefmod.dim_secondary_text_alignment
    try:
        _align = text.TextStyle.getAlignmentFromString(_sta)
        globals.prefs['DIM_SECONDARY_TEXT_ALIGNMENT'] = _align
    except:
        sys.stederr.write("Invalid secondary text alignment: " + str(_sta))

def _set_secondary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.dim_secondary_prefix)
    if _prefix is not None:
        globals.prefs['DIM_SECONDARY_PREFIX'] = _prefix

def _set_secondary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.dim_secondary_suffix)
    if _suffix is not None:
        globals.prefs['DIM_SECONDARY_SUFFIX'] = _suffix

def _set_secondary_precision(prefmod):
    _prec = _test_int(prefmod.dim_secondary_precision)
    if _prec is not None:
        if _prec < 0 or _prec > 15:
            sys.stderr.write("Invalid secondary dimension precision: %d\n" % _prec)
        else:
            globals.prefs['DIM_SECONDARY_PRECISION'] = _prec

def _set_secondary_units(prefmod):
    _unit = _test_units(prefmod.dim_secondary_units)
    if _unit is not None:
        globals.prefs['DIM_SECONDARY_UNITS'] = _unit

def _set_secondary_print_zero(prefmod):
    _flag = _test_boolean(prefmod.dim_secondary_print_zero)
    if _flag is not None:
        globals.prefs['DIM_SECONDARY_LEADING_ZERO'] = _flag

def _set_secondary_trail_decimal(prefmod):
    _flag = _test_boolean(prefmod.dim_secondary_trailing_decimal)
    if _flag is not None:
        globals.prefs['DIM_SECONDARY_TRAILING_DECIMAL'] = _flag

def _set_dim_offset(prefmod):
    _offset = _test_float(prefmod.dim_offset)
    if _offset is not None:
        if _offset < 0.0:
            sys.stderr.write("Invalid dimension offset: %g\n" % _offset)
        else:
            globals.prefs['DIM_OFFSET'] = _offset

def _set_dim_extension(prefmod):
    _ext = _test_float(prefmod.dim_extension)
    if _ext is not None:
        if _ext < 0.0:
            sys.stderr.write("Invalid dimension extension: %g\n" % _ext)
        else:
            globals.prefs['DIM_EXTENSION'] = _ext

def _set_dim_color(prefmod):
    _color = _test_color(prefmod.dim_color)
    if _color is not None:
        globals.prefs['DIM_COLOR'] = _color
        _colors = globals.prefs['COLORS']
        if _color not in _colors:
            _colors.append(_color)

def _set_dim_thickness(prefmod):
    _t = _test_float(prefmod.dim_thickness)
    if _t is not None:
        if _t < 0.0:
            sys.stderr.write("Invalid dimension thickness %g\n" % _t)
        else:
            globals.prefs['DIM_THICKNESS'] = _t

def _set_dim_position(prefmod):
    _pos = _test_dim_position(prefmod.dim_position)
    if _pos is not None:
        globals.prefs['DIM_POSITION'] = _pos

def _set_dim_position_offset(prefmod):
    _offset = _test_float(prefmod.dim_position_offset)
    if _offset is not None:
        globals.prefs['DIM_POSITION_OFFSET'] = _offset
    else:
        sys.stderr.write("Invalid dim position offset: '%s'\n" % str(prefmod.dim_position_offset))

def _set_dim_endpoint(prefmod):
    _ept = _test_dim_endpoint(prefmod.dim_endpoint)
    if _ept is not None:
        globals.prefs['DIM_ENDPOINT'] = _ept

def _set_dim_endpoint_size(prefmod):
    _epsize = _test_float(prefmod.dim_endpoint_size)
    if _epsize is not None:
        if _epsize < 0.0:
            sys.stderr.write("Invalid endpoint size: %g\n" % _epsize)
        else:
            globals.prefs['DIM_ENDPOINT_SIZE'] = _epsize

def _set_dim_dual_mode(prefmod):
    _flag = _test_boolean(prefmod.dim_dual_mode)
    if _flag is not None:
        globals.prefs['DIM_DUAL_MODE'] = _flag

def _set_dim_dual_mode_offset(prefmod):
    _offset = _test_float(prefmod.dim_dual_mode_offset)
    if _offset is not None:
        globals.prefs['DIM_DUAL_MODE_OFFSET'] = _offset
    else:
        sys.stderr.write("Invalid dim dual mode offset: '%s'\n" % str(prefmod.dim_dual_mode_offset))

def _set_radial_dim_primary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.radial_dim_primary_prefix)
    if _prefix is not None:
        globals.prefs['RADIAL_DIM_PRIMARY_PREFIX'] = _prefix

def _set_radial_dim_primary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.radial_dim_primary_suffix)
    if _suffix is not None:
        globals.prefs['RADIAL_DIM_PRIMARY_SUFFIX'] = _suffix

def _set_radial_dim_secondary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.radial_dim_secondary_prefix)
    if _prefix is not None:
        globals.prefs['RADIAL_DIM_SECONDARY_PREFIX'] = _prefix

def _set_radial_dim_secondary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.radial_dim_secondary_suffix)
    if _suffix is not None:
        globals.prefs['RADIAL_DIM_SECONDARY_SUFFIX'] = _suffix

def _set_radial_dim_dia_mode(prefmod):
    _flag = _test_boolean(prefmod.radial_dim_dia_mode)
    if _flag is not None:
        globals.prefs['RADIAL_DIM_DIA_MODE'] = _flag

def _set_angular_dim_primary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.angular_dim_primary_prefix)
    if _prefix is not None:
        globals.prefs['ANGULAR_DIM_PRIMARY_PREFIX'] = _prefix

def _set_angular_dim_primary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.angular_dim_primary_suffix)
    if _suffix is not None:
        globals.prefs['ANGULAR_DIM_PRIMARY_SUFFIX'] = _suffix

def _set_angular_dim_secondary_prefix(prefmod):
    _prefix = _test_unicode(prefmod.angular_dim_secondary_prefix)
    if _prefix is not None:
        globals.prefs['ANGULAR_DIM_SECONDARY_PREFIX'] = _prefix

def _set_angular_dim_secondary_suffix(prefmod):
    _suffix = _test_unicode(prefmod.angular_dim_secondary_suffix)
    if _suffix is not None:
        globals.prefs['ANGULAR_DIM_SECONDARY_SUFFIX'] = _suffix

def _set_text_style(prefmod):
    _obj = prefmod.text_style
    if isinstance(_obj, dict):
        try:
            _tstyle = _parse_textstyle(_obj)
            globals.prefs['TEXT_STYLE'] = _tstyle
            globals.prefs['FONT_WEIGHT'] = _tstyle.getWeight()
            globals.prefs['FONT_STYLE'] = _tstyle.getStyle()
            globals.prefs['FONT_FAMILY'] = _tstyle.getFamily()
            globals.prefs['TEXT_SIZE'] = _tstyle.getSize()
            globals.prefs['TEXT_ANGLE'] = _tstyle.getAngle()
            globals.prefs['TEXT_ALIGNMENT'] = _tstyle.getAlignment()
            _color = _tstyle.getColor()
            _colors = globals.prefs['COLORS']
            if _color not in _colors:
                _colors.append(_color)
            globals.prefs['FONT_COLOR'] = _color
        except StandardError, _e:
            sys.stderr.write("Invalid TextStyle: " + _e + "\n")
    else:
        sys.stderr.write("Invalid TextStyle: " + str(_obj) +"\n")

def _set_font_family(prefmod):
    _family = prefmod.font_family
    if isinstance(_family, types.StringTypes) and _family != "":
        globals.prefs['FONT_FAMILY'] = _family
    else:
        sys.stderr.write("Invalid font family: " + str(_family) + "\n")

def _set_font_style(prefmod):
    _style = _test_font_style(prefmod.font_style)
    if _style is not None:
        globals.prefs['FONT_STYLE'] = _style

def _set_font_weight(prefmod):
    _weight = _test_font_weight(prefmod.font_weight)
    if _weight is not None:
        globals.prefs['FONT_WEIGHT'] = _weight

def _set_font_size(prefmod):
    sys.stderr.write("Variable 'font_size' is obsolete - use 'text_size'\n")

def _set_text_size(prefmod):
    _size = _test_float(prefmod.text_size)
    if _size is not None:
        if _size > 0.0:
            globals.prefs['TEXT_SIZE'] = _size
        else:
            sys.stderr.write("Invalid text size: %g\n" % _size)

def _set_font_color(prefmod):
    _color = _test_color(prefmod.font_color)
    if _color is not None:
        globals.prefs['FONT_COLOR'] = _color
        _colors = globals.prefs['COLORS']
        if _color not in _colors:
            _colors.append(_color)

def _set_text_angle(prefmod):
    _angle = _test_float(prefmod.text_size)
    if _angle is not None:
        globals.prefs['TEXT_ANGLE'] = _angle
    else:
        sys.stderr.write("Invalid text angle: %g\n" % _angle)

def _set_text_alignment(prefmod):
    _ta = prefmod.text_alignment
    try:
        _align = text.TextStyle.getAlignmentFromString(_ta)
        globals.prefs['TEXT_ALIGNMENT'] = _align
    except:
        sys.stederr.write("Invalid text alignment: " + str(_ta))

def _set_chamfer_length(prefmod):
    _length = _test_float(prefmod.chamfer_length)
    if _length is not None:
        if _length < 0.0:
            sys.stderr.write("Invalid chamfer length: %g\n" % _length)
        else:
            globals.prefs['CHAMFER_LENGTH'] = _length

def _set_fillet_radius(prefmod):
    _radius = _test_float(prefmod.fillet_radius)
    if _radius is not None:
        if _radius < 0.0:
            sys.stderr.write("Invalid fillet radius: %g\n" % _radius)
        else:
            globals.prefs['FILLET_RADIUS'] = _radius

def _set_line_style(prefmod):
    _obj = prefmod.line_style
    if isinstance(_obj, dict):
        try:
            _style = _parse_style(_obj)
            globals.prefs['LINE_STYLE'] = _style
            _lt = _style.getLinetype()
            globals.prefs['LINE_TYPE'] = _lt
            _lts = globals.prefs['LINETYPES']
            if _lt not in _lts:
                _lts.append(_linetype)
            _color = _style.getColor()
            globals.prefs['LINE_COLOR'] = _color
            _colors = globals.prefs['COLORS']
            if _color not in _colors:
                _colors.append(_color)
            globals.prefs['LINE_THICKNESS'] = _style.getThickness()
        except StandardError, _e:
            sys.stderr.write("Invalid Style: " + _e + "\n")
    else:
        sys.stderr.write("Invalid Style: " + str(_obj) +"\n")
        
def _set_line_type(prefmod):
    _obj = prefmod.line_type
    if isinstance(_obj, tuple) and len(_obj) == 2:
        _name, _dlist = _obj
        try:
            _lt = linetype.Linetype(_name, _dlist)
            globals.prefs['LINE_TYPE'] = _lt
            _lts = globals.prefs['LINETYPES']
            if _lt not in _lt:
                _lts.append(_linetype)
        except:
            sys.stderr.write("Invalid linetype: '" + str(_obj) + "'\n")
    else:
        sys.stderr.write("Invalid linetype tuple: '" + str(_obj) + "'\n")

def _set_line_color(prefmod):
    _color = _test_color(prefmod.line_color)
    if _color is not None:
        globals.prefs['LINE_COLOR'] = _color
        _colors = globals.prefs['COLORS']
        if _color not in _colors:
            _colors.append(_color)

def _set_line_thickness(prefmod):
    _t = _test_float(prefmod.line_thickness)
    if _t is not None:
        if _t < 0.0:
            sys.stderr.write("Invalid line thickness: %g\n" % _t)
        else:
            globals.prefs['LINE_THICKNESS'] = _t

def _set_highlight_points(prefmod):
    _flag = _test_boolean(prefmod.highlight_points)
    if _flag is not None:
        globals.prefs['HIGHLIGHT_POINTS'] = _flag

def _set_inactive_layer_color(prefmod):
    _color = _test_color(prefmod.inactive_layer_color)
    if _color is not None:
        globals.prefs['INACTIVE_LAYER_COLOR'] = _color

def _set_background_color(prefmod):
    _color = _test_color(prefmod.background_color)
    if _color is not None:
        globals.prefs['BACKGROUND_COLOR'] = _color

def _set_single_point_color(prefmod):
    _color = _test_color(prefmod.single_point_color)
    if _color is not None:
        globals.prefs['SINGLE_POINT_COLOR'] = _color

def _set_multi_point_color(prefmod):
    _color = _test_color(prefmod.multi_point_color)
    if _color is not None:
        globals.prefs['MULTI_POINT_COLOR'] = _color

def _set_autosplit(prefmod):
    _flag = _test_boolean(prefmod.autosplit)
    if _flag is not None:
        globals.prefs['AUTOSPLIT'] = _flag

def _set_leader_arrow_size(prefmod):
    _size = _test_float(prefmod.leader_arrow_size)
    if _size is not None:
        if _size < 0.0:
            sys.stderr.write("Invalid leader arrow size: %g\n" % _size)
        else:
            globals.prefs['LEADER_ARROW_SIZE'] = _size

def _set_linetypes(prefmod):
    _ltlist = prefmod.linetypes
    _linetypes = globals.prefs['LINETYPES']
    if isinstance(_ltlist, list):
        for _obj in _ltlist:
            if not isinstance(_obj, tuple) or len(_obj) != 2:
                sys.stderr.write("Invalid linetype tuple: '" + str(_obj) + "'\n")
                continue
            _name, _dlist = _obj
            try:
                _linetype = linetype.Linetype(_name, _dlist)
                if _linetype not in _linetypes:
                    _linetypes.append(_linetype)
            except:
                sys.stderr.write("Invalid linetype: '" + str(_obj) + "'\n")
    else:
        sys.stderr.write("Invalid line type list: '" + str(_ltlist) + "'\n")

def _set_colors(prefmod):
    _clist = prefmod.colors
    if isinstance(_clist, list):
        for _obj in _clist:
            _color = None
            if isinstance(_obj, str):
                _color = _test_color(_obj)
            elif isinstance(_obj, tuple) and len(_obj) == 3:
                _r, _g, _b = _obj
                try:
                    _color = color.Color(_r, _g, _b)
                except:
                    sys.stderr.write("Invalid color: '" + str(_obj) + "'\n")
            else:
                sys.stderr.write("Invalid color: '" + str(_obj) + "'\n")
            if _color is not None and _color not in globals.colors:
                globals.colors[_color] = _color
    else:
        sys.stderr.write("Invalid color list: '" + str(_clist) + "'\n")

def _parse_dimstyle(sd):
    if not isinstance(sd, dict):
        raise TypeError, "Invalid style dictionary: " + `type(sd)`
    _name = None
    _ds = {}
    for _key in sd.keys():
        _v = sd[_key]
        _k = _key.lower()
        if _k == 'name':
            if not isinstance(_v, types.StringTypes):
                raise TypeError, "Invalid DimStyle name type: " + `type(_v)`
            _name = _v
        elif (_k == 'dim_color' or
              _k == 'dim_primary_font_color' or
              _k == 'dim_secondary_font_color'):
            _col = _test_color(_v)
            if _col is None:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'" % (str(_v), _k)
            _v = _col
        elif (_k == 'dim_primary_font_family' or
              _k == 'dim_secondary_font_family'):
            if not isinstance(_v, types.StringTypes):
                raise TypeError, "Invalid type '%s' for DimStyle key '%s'\n " % (`type(_v)`, _k)
            if _v == "":
                raise ValueError, "Font family for '%s' cannot be empty" % _k
        elif (_k == 'dim_offset' or
              _k == 'dim_dual_mode_offset' or
              _k == 'dim_position_offset' or
              _k == 'dim_thickness' or
              _k == 'dim_endpoint_size' or
              _k == 'dim_primary_text_size' or
              _k == 'dim_secondary_text_size' or
              _k == 'dim_extension'):
            if not isinstance(_v, float):
                raise TypeError, "Invalid type '%s' for DimStyle key '%s'\n " % (`type(_v)`, _k)
            if _v < 0.0:
                raise ValueError, "Invalid value %f for DimStyle key '%s'\n " % (_v, _k)
        elif (_k == 'dim_primary_precision' or
              _k == 'dim_secondary_precision'):
            if not isinstance(_v, int):
                raise TypeError, "Invalid type '%s' for DimStyle key '%s'\n " % (`type(_v)`, _k)
            if _v < 0 or _v > 15:
                raise ValueError, "Invalid value %d for DimStyle key '%s'\n " % (_v, _k)
        elif (_k == 'dim_primary_font_weight' or
              _k == 'dim_secondary_font_weight'):
            try:
                _weight = text.TextStyle.getWeightFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _weight
        elif (_k == 'dim_primary_text_alignment' or
              _k == 'dim_secondary_text_alignment'):
            try:
                _align = text.TextStyle.getAlignmentFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _align
        elif (_k == 'dim_primary_font_style' or
              _k == 'dim_secondary_font_style'):
            try:
                _style = text.TextStyle.getStyleFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _style
        elif (_k == 'dim_primary_text_angle' or
              _k == 'dim_secondary_text_angle'):
            _angle = _test_float(_v)
            if _angle is None:
                raise ValueError, "Invalid value %d for DimStyle key '%s'\n " % (_v, _k)
            _v = _angle
        elif (_k == 'dim_primary_units' or
              _k == 'dim_secondary_units'):
            try:
                _unit = units.Unit.getUnitFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _unit
        elif _k == 'dim_position':
            try:
                _pos = dimension.Dimension.getPositionFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _pos
        elif _k == 'dim_endpoint':
            try:
                _ept = dimension.Dimension.getEndpointTypeFromString(_v)
            except:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (_v, _k)
            _v = _ept
        elif (_k == 'dim_primary_leading_zero' or
              _k == 'dim_secondary_leading_zero' or
              _k == 'dim_primary_trailing_decimal' or
              _k == 'dim_secondary_trailing_decimal' or
              _k == 'dim_dual_mode' or
              _k == 'radial_dim_dia_mode'):
            _flag = _test_boolean(_v)
            if _flag is None:
                raise ValueError, "Invalid value '%s' for DimStyle key '%s'\n " % (str(_v), _k)
            _v = _flag
        elif (_k == 'dim_primary_prefix' or
              _k == 'dim_primary_suffix' or
              _k == 'dim_secondary_prefix' or
              _k == 'dim_secondary_suffix' or
              _k == 'radial_dim_primary_prefix' or
              _k == 'radial_dim_primary_suffix' or
              _k == 'radial_dim_secondary_prefix' or
              _k == 'radial_dim_secondary_suffix' or
              _k == 'angular_dim_primary_prefix' or
              _k == 'angular_dim_primary_suffix' or
              _k == 'angular_dim_secondary_prefix' or
              _k == 'angular_dim_secondary_suffix'):
            if not isinstance(_v, types.StringTypes):
                raise TypeError, "Invalid type '%s' for DimStyle key '%s'\n " % (`type(_v)`, _k)
        elif _k == 'dim_primary_font_size':
            sys.stderr.write("Key 'dim_primary_font_size' obsoleted by 'dim_primary_text_size'\n")
            continue
        elif _k == 'dim_secondary_font_size':
            sys.stderr.write("Key 'dim_secondary_font_size' obsoleted by 'dim_secondary_text_size'\n")
            continue
        else:
            raise ValueError, "Unknown DimStyle option: %s" % _k
        if _k != 'name':
            _ds[_key.upper()] = _v
    if _name is None:
        raise ValueError, "DimStyle missing 'name' field: " + str(sd)
    return dimension.DimStyle(_name, _ds)
    
def _parse_textstyle(sd):
    if not isinstance(sd, dict):
        raise TypeError, "Invalid style dictionary: " + `type(sd)`
    _name = sd.get('name')
    if _name is None:
        raise ValueError, "TextStyle missing 'name' field: " + str(sd)
    if not isinstance(_name, types.StringTypes):
        raise TypeError, "Invalid textstyle name type: " + `type(_name)`
    _family = sd.get('family')
    if _family is None:
        raise ValueError, "TextStyle missing 'family' field: " + str(sd)
    if not isinstance(_family, types.StringTypes):
        raise TypeError, "Invalid textstyle family type: " + `type(_family)`
    _val = sd.get('style')
    if _val is None:
        raise TypeError, "TextStyle missing 'style' field: " + str(sd)
    _style = text.TextStyle.getStyleFromString(_val)
    _val = sd.get('weight')
    if _val is None:
        raise TypeError, "TextStyle missing 'weight' field: " + str(sd)
    _weight = text.TextStyle.getWeightFromString(_val)
    _val = sd.get('color')
    if _val is None:
        raise ValueError, "Style missing 'color' field: " + str(sd)
    _color = _test_color(_val)
    if _color is None:
        raise ValueError, "Invalid TextStyle color: " + str(_val)
    _size = sd.get('size')
    if _size is None:
        raise ValueError, "TextStyle missing 'size' field: " + str(sd)
    _angle = sd.get('angle')
    if _angle is None:
        raise ValueError, "TextSytle missing 'angle' field: " + str(sd)
    _val = sd.get('alignment')
    if _val is None:
        raise TypeError, "TextStyle missing 'alignment' field: " + str(sd)
    _align = text.TextStyle.getAlignmentFromString(_val)
    return text.TextStyle(_name, family=_family, style=_style,
                          weight=_weight, color=_color, size=_size,
                          angle=_angle, align=_align)

def _parse_style(sd):
    if not isinstance(sd, dict):
        raise TypeError, "Invalid style dictionary: " + `type(sd)`
    _n = sd.get('name')
    if _n is None:
        raise ValueError, "Style missing 'name' field: " + str(sd)
    if not isinstance(_n, types.StringTypes):
        raise TypeError, "Invalid style name type: " + `type(_n)`
    _l =  sd.get('linetype')
    if _l is None:
        raise ValueError, "Style missing 'linetype' field: " + str(sd)
    if not isinstance(_l, tuple):
        raise TypeError, "Invalid linetype tuple: " + `type(_l)`
    if len(_l) != 2:
        raise ValueError, "Invalid linetype tuple length: " + str(_l)
    _ln = _l[0]
    if not isinstance(_ln, types.StringTypes):
        raise TypeError, "Invalid style linetype name type: " + `type(_ln)`
    _ld = _l[1]
    if _ld is not None and not isinstance(_ld, list):
        raise TypeError, "Invalid style linetype dashlist type: " + `type(_ld)`
    _lt = linetype.Linetype(_ln, _ld)
    _c = sd.get('color')
    if _c is None:
        raise ValueError, "Style missing 'color' field: " + str(sd)
    _col = _test_color(_c)
    if _col is None:
        raise ValueError, "Invalid Style color: " + str(_c)
    _t = sd.get('thickness')
    if _t is None:
        raise ValueError, "Style missing 'thickness' field: " + str(sd)
    return style.Style(_n, _lt, _col, _t)
    
def _set_styles(prefmod):
    _slist = prefmod.styles
    _styles = globals.prefs['STYLES']
    _linetypes = globals.prefs['LINETYPES']
    if isinstance(_slist, list):
        for _obj in _slist:
            _style = None
            if isinstance(_obj, dict):
                try:
                    _style = _parse_style(_obj)
                except:
                    sys.stderr.write("Invalid style: %s\n" % str(_obj))
            elif isinstance(_obj, tuple):
                sys.stderr.write("Tuple based Style definition is deprecated: '" + str(_obj) + "'\n")
                if len(_obj) != 4:
                    sys.stderr.write("Invalid tuple-based style entry: '" + str(_obj) + "'\n")
                    continue
                _sd =  {
                    'name' : _obj[0],
                    'linetype' : _obj[1],
                    'color' : _obj[2],
                    'thickness' : _obj[3]
                    }
                try:
                    _style = _parse_style(_sd)
                except StandardError, _e:
                    sys.stderr.write("Invalid style: %s, %e\n" % (str(_obj), _e))
            else:
                sys.stderr.write("Unexpected style type: %s" % `type(_obj)`)
            if _style is None:
                continue
            if _style not in _styles:
                _styles.append(_style)
            _linetype = _style.getLinetype()
            if _linetype not in _linetypes:
                _linetypes.append(_linetype)
    else:
        sys.stderr.write("Invalid style list: '" + str(_slist) + "'\n")

def _set_dimstyles(prefmod):
    _dslist = prefmod.dimstyles
    _dimstyles = globals.prefs['DIMSTYLES']
    if isinstance(_dslist, list):
        for _obj in _dslist:
            _dimstyle = None
            if not isinstance(_obj, tuple) or len(_obj) != 2:
                sys.stderr.write("Invalid DimStyle entry: '" + str(_obj) + "'\n")
                continue
            _name, _dsdict = _obj
            if not isinstance(_name, types.StringTypes):
                sys.stderr.write("Invalid DimStyle name: '" + str(_name) + "'\n")
                continue
            if not isinstance(_dsdict, dict):
                sys.stderr.write("Invalid DimStyle dictionary: '" + str(_dsdict) + "'\n")
                continue
            _dsdict['name'] = _name
            try:
                _dimstyle = _parse_dimstyle(_dsdict)
            except StandardError, _e:
                sys.stderr.write("Invalid DimStyle: " + _e)
            if _dimstyle is not None and _dimstyle not in _dimstyles:
                _dimstyles.append(_dimstyle)
    else:
        sys.stderr.write("Invalid dimension style list: '" + str(_dslist) + "'\n")

def _set_textstyles(prefmod):
    _tslist = prefmod.textstyles
    _textstyles = globals.prefs['TEXTSTYLES']
    if isinstance(_tslist, list):
        for _obj in _tslist:
            _textstyle = None
            if isinstance(_obj, dict):
                try:
                    _textstyle = _parse_textstyle(_obj)
                except StandardError, _e:
                    sys.stderr.write("Invalid TextStyle: " + _e)
            elif isinstance(_obj, tuple):
                sys.stderr.write("Tuple based TextStyle definition is deprecated: '" + str(_obj) + "'\n")                
                if len(_obj) != 6:
                    sys.stderr.write("Invalid tuple based TextStyle entry: '" + str(_obj) + "'\n")
                    continue
                #
                # tuple-based definition lacked angle and alignment fields,
                # so we add them with reasonable values
                #
                _td = {
                    'name' : _obj[0],
                    'family' : _obj[1],
                    'size' : _obj[2],
                    'style' : _obj[3],
                    'weight' : _obj[4],
                    'color' : _obj[5],
                    'angle' : 0.0, 
                    'alignment' : 'left'
                    }
                try:
                    _textstyle = _parse_textstyle(_td)
                except StandardError, _e:
                    sys.stderr.write("Invalid TextSyle: %s, %e\n" % (str(_obj), _e))
            if _textstyle is not None and _textstyle not in _textstyles:
                _textstyles.append(_textstyle)
    else:
        sys.stderr.write("Invalid text style list: '" + str(_tslist) + "'\n")

#
# this list of tuples stores the tested attributes in the 'prefs.py' module(s)
# and the function used to validate the value given by the user
#

_preflist = [
    #
    # booleans
    #
    ('user_prefs', _set_user_prefs),
    ('autosplit', _set_autosplit),
    ('highlight_points', _set_highlight_points),
    #
    # floats
    #
    ('leader_arrow_size', _set_leader_arrow_size),
    ('chamfer_length', _set_chamfer_length),
    ('fillet_radius', _set_fillet_radius),
    #
    # display colors
    #
    ('inactive_layer_color', _set_inactive_layer_color),
    ('background_color', _set_background_color),
    ('single_point_color', _set_single_point_color),
    ('multi_point_color', _set_multi_point_color),
    #
    # units
    #
    ('units', _set_units),
    #
    # GraphicObject entity parameters
    #
    ('line_style', _set_line_style),
    ('line_type', _set_line_type),
    ('line_color', _set_line_color),
    ('line_thickness', _set_line_thickness),
    #
    # TextBlock parameters
    #
    ('text_style', _set_text_style),
    ('font_family', _set_font_family),
    ('font_style', _set_font_style),
    ('font_weight', _set_font_weight),
    ('font_size', _set_font_size),
    ('text_size', _set_text_size),
    ('font_color', _set_font_color),
    ('text_angle', _set_text_angle),
    ('text_alignment', _set_text_alignment),
    #
    # Dimension paramters
    #
    ('dim_style', _set_dim_style),
    ('dim_primary_font_family', _set_primary_font_family),
    ('dim_primary_font_size', _set_primary_font_size),
    ('dim_primary_text_size', _set_primary_text_size),
    ('dim_primary_font_weight', _set_primary_font_weight),
    ('dim_primary_font_style', _set_primary_font_style),
    ('dim_primary_font_color', _set_primary_font_color),
    ('dim_primary_text_angle', _set_primary_text_angle),
    ('dim_primary_text_alignment',_set_primary_text_alignment),
    ('dim_primary_prefix', _set_primary_prefix),
    ('dim_primary_suffix', _set_primary_suffix),
    ('dim_primary_precision', _set_primary_precision),
    ('dim_primary_units', _set_primary_units),
    ('dim_primary_leading_zero', _set_primary_print_zero),
    ('dim_primary_trailing_decimal', _set_primary_trail_decimal),
    ('dim_secondary_font_family', _set_secondary_font_family),
    ('dim_secondary_font_size', _set_secondary_font_size),
    ('dim_secondary_text_size', _set_secondary_text_size),
    ('dim_secondary_font_weight', _set_secondary_font_weight),
    ('dim_secondary_font_style', _set_secondary_font_style),
    ('dim_secondary_font_color', _set_secondary_font_color),
    ('dim_secondary_text_angle', _set_secondary_text_angle),
    ('dim_secondary_text_alignment', _set_secondary_text_alignment),
    ('dim_secondary_prefix', _set_secondary_prefix),
    ('dim_secondary_suffix', _set_secondary_suffix),
    ('dim_secondary_precision', _set_secondary_precision),
    ('dim_secondary_units', _set_secondary_units),
    ('dim_secondary_leading_zero', _set_secondary_print_zero),
    ('dim_secondary_trailing_decimal', _set_secondary_trail_decimal),
    ('dim_offset', _set_dim_offset),
    ('dim_extension', _set_dim_extension),
    ('dim_color', _set_dim_color),
    ('dim_thickness', _set_dim_thickness),
    ('dim_position', _set_dim_position),
    ('dim_position_offset', _set_dim_position_offset),
    ('dim_endpoint', _set_dim_endpoint),
    ('dim_endpoint_size', _set_dim_endpoint_size),
    ('dim_dual_mode', _set_dim_dual_mode),
    ('dim_dual_mode_offset', _set_dim_dual_mode_offset),
    ('radial_dim_primary_prefix', _set_radial_dim_primary_prefix),
    ('radial_dim_primary_suffix', _set_radial_dim_primary_suffix),
    ('radial_dim_secondary_prefix', _set_radial_dim_secondary_prefix),
    ('radial_dim_secondary_suffix', _set_radial_dim_secondary_suffix),
    ('radial_dim_dia_mode', _set_radial_dim_dia_mode),
    ('angular_dim_primary_prefix', _set_angular_dim_primary_prefix),
    ('angular_dim_primary_suffix', _set_angular_dim_primary_suffix),
    ('angular_dim_secondary_prefix', _set_angular_dim_secondary_prefix),
    ('angular_dim_secondary_suffix', _set_angular_dim_secondary_suffix),
    #
    # lists of object types to be loaded in at startup
    #
    ('colors', _set_colors),
    ('linetypes', _set_linetypes),
    ('styles', _set_styles),
    ('textstyles', _set_textstyles),
    ('dimstyles', _set_dimstyles)
    ]

def _set_defaults(prefmod):
    if hasattr(prefmod, 'default_dimstyle'):
        _dsname = prefmod.default_dimstyle
        if isinstance(_dsname, types.StringTypes):
            _set = False
            for _dimstyle in globals.prefs['DIMSTYLES']:
                _name = _dimstyle.getName()
                if _name == _dsname:
                    globals.prefs['DEFAULT_DIMSTYLE'] = _dimstyle
                    _set = True
                    break
            if not _set:
                sys.stderr.write("No DimStyle found with name '%s'\n" % _dsname)
        elif _dsname is None:
            pass # accept default
        else:
            sys.stderr.write("Invalid default dimension style: '%s'\n" % str(_dsname))
    if hasattr(prefmod, 'default_textstyle'):
        _tsname = prefmod.default_textstyle
        if isinstance(_tsname, types.StringTypes):
            _set = False
            for _textstyle in globals.prefs['TEXTSTYLES']:
                _name = _textstyle.getName()
                if _name == _tsname:
                    globals.prefs['DEFAULT_TEXTSTYLE'] = _textstyle
                    _set = True
                    break
            if not _set:
                sys.stderr.write("No TextStyle found with name '%s'\n" % _tsname)
        elif _tsname is None:
            pass # accept default
        else:
            sys.stderr.write("Invalid default TextStyle: '%s'\n" % str(_tsname))
    if hasattr(prefmod, 'default_style'):
        _sname = prefmod.default_style
        if isinstance(_sname, types.StringTypes):
            _set =  False
            for _style in globals.prefs['STYLES']:
                if _style.getName() == _sname:
                    globals.prefs['DEFAULT_STYLE'] = _style
                    _set = True
                    break
            if not _set:
                sys.stderr.write("No Style found with name '%s'\n" % _sname)
        elif _sname is None:
            pass # accept default
        else:
            sys.stderr.write("Invalid default Style: '%s'\n" % str(_sname))
    
def load_global_prefs():
    """Try and load the preferences stored in the global preferences file

load_global_prefs()

If the preferences file '/etc/pythoncad/prefs.py' exists and can
be read without errors, the global preferences will be set to
the values read from the file.
    """
    try:
        _f, _p, _d = imp.find_module('prefs', ['/etc/pythoncad'])
        if _f is not None:
            try:
                try:
                    _mod = imp.load_module('prefs', _f, _p, _d)
                finally:
                    _f.close()
                for _attr, _func in _preflist:
                    if hasattr(_mod, _attr):
                        _func(_mod)
                _set_defaults(_mod)
                del sys.modules['prefs']
            except StandardError, _e: # should print the error out
                sys.stderr.write("Syntax error in %s: %s\n" % (_p, _e))
    except ImportError:
        pass
    except StandardError, _e:
        sys.stderr.write("Error loading global preferences: %s" % _e)

def load_user_prefs():
    """Try and load the preferences stored in the user's preference file

load_user_prefs()

If the file '$HOME/.pythoncad/prefs.py' ('$APPDATA/PythonCAD/prefs.py' on
Windows) exists and can be read without errors, the preferences given in
that file will be used to set the global preferences. Reading this file
is conditioned upon the 'USER_PREFS' variable being set to True.
    """
    _flag = True
    if globals.prefs.has_key('USER_PREFS'):
        _flag = globals.prefs['USER_PREFS']
    _pdir = None
    if sys.platform == 'win32' and os.environ.has_key('APPDATA'):
        _pdir = os.path.join(os.environ.get('APPDATA'), 'PythonCAD')
    else:
        if os.environ.has_key('HOME'):
            _pdir = os.path.join(os.environ['HOME'], '.pythoncad')
    if _flag and _pdir is not None:
        try:
            _f, _p, _d = imp.find_module('prefs',[_pdir])
            if _f is not None:
                try:
                    try:
                        _mod = imp.load_module('prefs', _f, _p, _d)
                    finally:
                        _f.close()
                    for _attr, _func in _preflist:
                        if hasattr(_mod, _attr):
                            _func(_mod)
                    del sys.modules['prefs']
                except StandardError, _e: # should print the error out
                    sys.stderr.write("Syntax error in %s: %s\n" % (_p, _e))
        except ImportError:
            pass
        except StandardError, _e:
            sys.stderr.write("Error loading user preferences: %s" % _e)

def _save_dimstyle_values(f):
    f.write("#\n# Standard Dimension parameters\n#\n")
    _gp = globals.prefs
    _tc = text.TextStyle
    _dim = dimension.Dimension
    _uc = units.Unit
    _ds = _gp['DIM_STYLE']
    f.write("dim_style = {\n")
    f.write("    'name' : '%s',\n" % _ds.getName())
    _val = _ds.getOption('DIM_PRIMARY_FONT_FAMILY')
    f.write("    'dim_primary_font_family' : '%s',\n" % _val)
    _val = _ds.getOption('DIM_PRIMARY_TEXT_SIZE')
    f.write("    'dim_primary_text_size' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_PRIMARY_FONT_WEIGHT')
    f.write("    'dim_primary_font_weight': '%s',\n" % _tc.getWeightAsString(_val))
    _val = _ds.getOption('DIM_PRIMARY_FONT_STYLE')
    f.write("    'dim_primary_font_style' : '%s',\n" % _tc.getStyleAsString(_val))
    _val = _ds.getOption('DIM_PRIMARY_FONT_COLOR')
    f.write("    'dim_primary_font_color' : '%s',\n" % str(_val))
    _val = _ds.getOption('DIM_PRIMARY_TEXT_ANGLE')
    f.write("    'dim_primary_text_angle' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_PRIMARY_TEXT_ALIGNMENT')
    f.write("    'dim_primary_text_alignment' : '%s',\n" % _tc.getAlignmentAsString(_val))
    _val = _ds.getOption('DIM_PRIMARY_PREFIX')
    f.write("    'dim_primary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_PRIMARY_SUFFIX')
    f.write("    'dim_primary_suffix' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_PRIMARY_PRECISION')
    f.write("    'dim_primary_precision' : %d,\n" % _val)
    _val = _ds.getOption('DIM_PRIMARY_UNITS')
    f.write("    'dim_primary_units' : '%s',\n" % _uc.getUnitAsString(_val))
    _val = _ds.getOption('DIM_PRIMARY_LEADING_ZERO')
    f.write("    'dim_primary_leading_zero' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_PRIMARY_TRAILING_DECIMAL')
    f.write("    'dim_primary_trailing_decimal' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_FONT_FAMILY')
    f.write("    'dim_secondary_font_family' : '%s',\n" % _val)
    _val = _ds.getOption('DIM_SECONDARY_TEXT_SIZE')
    f.write("    'dim_secondary_text_size' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_FONT_WEIGHT')
    f.write("    'dim_secondary_font_weight' : '%s',\n" % _tc.getWeightAsString(_val))
    _val = _ds.getOption('DIM_SECONDARY_FONT_STYLE')
    f.write("    'dim_secondary_font_style' : '%s',\n" % _tc.getStyleAsString(_val))
    _val = _ds.getOption('DIM_SECONDARY_FONT_COLOR')
    f.write("    'dim_secondary_font_color' : '%s',\n" % str(_val))
    _val = _ds.getOption('DIM_SECONDARY_TEXT_ANGLE')
    f.write("    'dim_secondary_text_angle' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_TEXT_ALIGNMENT')
    f.write("    'dim_secondary_text_alignment' : '%s',\n" % _tc.getAlignmentAsString(_val))
    _val = _ds.getOption('DIM_SECONDARY_PREFIX')
    f.write("    'dim_secondary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_SUFFIX')
    f.write("    'dim_secondary_suffix' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_PRECISION')
    f.write("    'dim_secondary_precision' : %d,\n" % _val)
    _val = _ds.getOption('DIM_SECONDARY_UNITS')
    f.write("    'dim_secondary_units' : '%s',\n" % _uc.getUnitAsString(_val))
    _val = _ds.getOption('DIM_SECONDARY_LEADING_ZERO')
    f.write("    'dim_secondary_leading_zero' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_SECONDARY_TRAILING_DECIMAL')
    f.write("    'dim_secondary_trailing_decimal' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_OFFSET')
    f.write("    'dim_offset' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_EXTENSION')
    f.write("    'dim_extension' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_COLOR')
    f.write("    'dim_color' : '%s',\n" % str(_val))
    _val = _ds.getOption('DIM_THICKNESS')
    f.write("    'dim_thickness' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_POSITION')
    f.write("    'dim_position' : '%s',\n" % _dim.getPositionAsString(_val))
    _val = _ds.getOption('DIM_ENDPOINT')
    f.write("    'dim_endpoint' : '%s',\n" % _dim.getEndpointTypeAsString(_val))
    _val = _ds.getOption('DIM_ENDPOINT_SIZE')
    f.write("    'dim_endpoint_size' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_DUAL_MODE')
    f.write("    'dim_dual_mode' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_POSITION_OFFSET')
    f.write("    'dim_position_offset' : %s,\n" % repr(_val))
    _val = _ds.getOption('DIM_DUAL_MODE_OFFSET')
    f.write("    'dim_dual_mode_offset' : %s,\n" % repr(_val))
    _val = _ds.getOption('RADIAL_DIM_PRIMARY_PREFIX')
    f.write("    'radial_dim_primary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('RADIAL_DIM_PRIMARY_SUFFIX')
    f.write("    'radial_dim_primary_suffix' : %s,\n" % repr(_val))
    _val = _ds.getOption('RADIAL_DIM_SECONDARY_PREFIX')
    f.write("    'radial_dim_secondary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('RADIAL_DIM_SECONDARY_SUFFIX')
    f.write("    'radial_dim_secondary_suffix' : %s,\n" % repr(_val))
    _val = _ds.getOption('RADIAL_DIM_DIA_MODE')
    f.write("    'radial_dim_dia_mode' : %s,\n" % repr(_val))
    _val = _ds.getOption('ANGULAR_DIM_PRIMARY_PREFIX')
    f.write("    'angular_dim_primary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('ANGULAR_DIM_PRIMARY_SUFFIX')
    f.write("    'angular_dim_primary_suffix' : %s,\n" % repr(_val))
    _val = _ds.getOption('ANGULAR_DIM_SECONDARY_PREFIX')
    f.write("    'angular_dim_secondary_prefix' : %s,\n" % repr(_val))
    _val = _ds.getOption('ANGULAR_DIM_SECONDARY_SUFFIX')
    f.write("    'angular_dim_secondary_suffix' : %s\n" % repr(_val))
    f.write("}\n")
    #
    # save overriden values
    #
    _val = _gp['DIM_PRIMARY_FONT_FAMILY']
    if _val != _ds.getOption('DIM_PRIMARY_FONT_FAMILY'):
        f.write("dim_primary_font_family = '%s'\n" % _val)
    _val = _gp['DIM_PRIMARY_TEXT_SIZE']
    if abs(_val - _ds.getOption('DIM_PRIMARY_TEXT_SIZE')) > 1e-10:
        f.write("dim_primary_text_size = %s\n" % repr(_val))
    _val = _gp['DIM_PRIMARY_FONT_WEIGHT']
    if _val != _ds.getOption('DIM_PRIMARY_FONT_WEIGHT'):
        f.write("dim_primary_font_weight = '%s'\n" % _tc.getWeightAsString(_val))
    _val = _gp['DIM_PRIMARY_FONT_STYLE']
    if _val != _ds.getOption('DIM_PRIMARY_FONT_STYLE'):
        f.write("dim_primary_font_style = '%s'\n" % _tc.getStyleAsString(_val))
    _val = _gp['DIM_PRIMARY_FONT_COLOR']
    if _val != _ds.getOption('DIM_PRIMARY_FONT_COLOR'):
        f.write("dim_primary_font_color = '%s'\n" % str(_val))
    _val = _gp['DIM_PRIMARY_TEXT_ANGLE']
    if abs(_val - _ds.getOption('DIM_PRIMARY_TEXT_ANGLE')) > 1e-10:
        f.write("dim_primary_text_angle = %s\n" % repr(_val))
    _val = _gp['DIM_PRIMARY_TEXT_ALIGNMENT']
    if _val != _ds.getOption('DIM_PRIMARY_TEXT_ALIGNMENT'):
        f.write("dim_primary_text_alignment = '%s'\n" % _tc.getAlignmentAsString(_val))
    _val = _gp['DIM_PRIMARY_PREFIX']
    if _val != _ds.getOption('DIM_PRIMARY_PREFIX'):
        f.write("dim_primary_prefix = %s\n" % repr(_val))
    _val = _gp['DIM_PRIMARY_SUFFIX']
    if _val != _ds.getOption('DIM_PRIMARY_SUFFIX'):
        f.write("dim_primary_suffix = %s\n" % repr(_val))
    _val = _gp['DIM_PRIMARY_PRECISION']
    if _val != _ds.getOption('DIM_PRIMARY_PRECISION'):
        f.write("dim_primary_precision = %d\n" % _val)
    _val = _gp['DIM_PRIMARY_UNITS']
    if _val != _ds.getOption('DIM_PRIMARY_UNITS'):
        f.write("dim_primary_units = '%s'\n" % _uc.getUnitAsString(_val))
    _val = _gp['DIM_PRIMARY_LEADING_ZERO']
    if _val is not _ds.getOption('DIM_PRIMARY_LEADING_ZERO'):
        f.write("dim_primary_leading_zero = %s\n" % repr(_val))
    _val = _gp['DIM_PRIMARY_TRAILING_DECIMAL']
    if _val is not _ds.getOption('DIM_PRIMARY_TRAILING_DECIMAL'):
        f.write("dim_primary_trailing_decimal = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_FONT_FAMILY']
    if _val != _ds.getOption('DIM_SECONDARY_FONT_FAMILY'):
        f.write("dim_secondary_font_family = '%s'\n" % _val)
    _val = _gp['DIM_SECONDARY_TEXT_SIZE']
    if abs(_val - _ds.getOption('DIM_SECONDARY_TEXT_SIZE')) > 1e-10:
        f.write("dim_secondary_text_size = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_FONT_WEIGHT']
    if _val != _ds.getOption('DIM_SECONDARY_FONT_WEIGHT'):
        f.write("dim_secondary_font_weight = '%s'\n" % _tc.getWeightAsString(_val))
    _val = _gp['DIM_SECONDARY_FONT_STYLE']
    if _val != _ds.getOption('DIM_SECONDARY_FONT_STYLE'):
        f.write("dim_secondary_font_style = '%s'\n" % _tc.getStyleAsString(_val))
    _val = _gp['DIM_SECONDARY_FONT_COLOR']
    if _val != _ds.getOption('DIM_SECONDARY_FONT_COLOR'):
        f.write("dim_secondary_font_color = '%s'\n" % str(_val))
    _val = _gp['DIM_SECONDARY_TEXT_ANGLE']
    if abs(_val - _ds.getOption('DIM_SECONDARY_TEXT_ANGLE')) > 1e-10:
        f.write("dim_secondary_text_angle = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_TEXT_ALIGNMENT']
    if _val != _ds.getOption('DIM_SECONDARY_TEXT_ALIGNMENT'):
        f.write("dim_secondary_text_alignment = '%s'\n" % _tc.getAlignmentAsString(_val))
    _val = _gp['DIM_SECONDARY_PREFIX']
    if _val != _ds.getOption('DIM_SECONDARY_PREFIX'):
        f.write("dim_secondary_prefix = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_SUFFIX']
    if _val != _ds.getOption('DIM_SECONDARY_SUFFIX'):
        f.write("dim_secondary_suffix = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_PRECISION']
    if _val != _ds.getOption('DIM_SECONDARY_PRECISION'):
        f.write("dim_secondary_precision = %d\n" % _val)
    _val = _gp['DIM_SECONDARY_UNITS']
    if _val != _ds.getOption('DIM_SECONDARY_UNITS'):
        f.write("dim_secondary_units = '%s'\n" % _uc.getUnitAsString(_val))
    _val = _gp['DIM_SECONDARY_LEADING_ZERO']
    if _val is not _ds.getOption('DIM_SECONDARY_LEADING_ZERO'):
        f.write("dim_secondary_leading_zero = %s\n" % repr(_val))
    _val = _gp['DIM_SECONDARY_TRAILING_DECIMAL']
    if _val is not _ds.getOption('DIM_SECONDARY_TRAILING_DECIMAL'):
        f.write("dim_secondary_trailing_decimal = %s\n" % repr(_val))
    _val = _gp['DIM_OFFSET']
    if abs(_val - _ds.getOption('DIM_OFFSET')) > 1e-10:
        f.write("dim_offset = %s\n" % repr(_val))
    _val = _gp['DIM_EXTENSION']
    if abs(_val - _ds.getOption('DIM_EXTENSION')) > 1e-10:
        f.write("dim_extension = %s\n" % repr(_val))
    _val = _gp['DIM_COLOR']
    if _val != _ds.getOption('DIM_COLOR'):
        f.write("dim_color = '%s'\n" % str(_val))
    _val = _gp['DIM_THICKNESS']
    if abs(_val - _ds.getOption('DIM_THICKNESS')) > 1e-10:
        f.write("dim_thickness = %s\n" % repr(_val))
    _val = _gp['DIM_POSITION']
    if _val != _ds.getOption('DIM_POSITION'):
        f.write("dim_position = '%s'\n" % _dim.getPositionAsString(_val))
    _val = _gp['DIM_ENDPOINT']
    if _val != _ds.getOption('DIM_ENDPOINT'):
        f.write("dim_endpoint = '%s'\n" % _dim.getEndpointTypeAsString(_val))
    _val = _gp['DIM_ENDPOINT_SIZE']
    if abs(_val - _ds.getOption('DIM_ENDPOINT_SIZE')) > 1e-10:
        f.write("dim_endpoint_size = %s\n" % repr(_val))
    _val = _gp['DIM_DUAL_MODE']
    if _val is not _ds.getOption('DIM_DUAL_MODE'):
        f.write("dim_dual_mode = %s\n" % repr(_val))
    _val = _gp['DIM_POSITION_OFFSET']
    if abs(_val - _ds.getOption('DIM_POSITION_OFFSET')) > 1e-10:
        f.write("dim_position_offset = %s\n" % repr(_val))
    _val = _gp['DIM_DUAL_MODE_OFFSET']
    if abs(_val - _ds.getOption('DIM_DUAL_MODE_OFFSET')) > 1e-10:
        f.write("dim_dual_mode_offset = %s\n" % repr(_val))
    _val = _gp['RADIAL_DIM_PRIMARY_PREFIX']
    if _val != _ds.getOption('RADIAL_DIM_PRIMARY_PREFIX'):
        f.write("radial_dim_primary_prefix = %s\n" % repr(_val))
    _val = _gp['RADIAL_DIM_PRIMARY_SUFFIX']
    if _val != _ds.getOption('RADIAL_DIM_PRIMARY_SUFFIX'):
        f.write("radial_dim_primary_suffix = %s\n" % repr(_val))
    _val = _gp['RADIAL_DIM_SECONDARY_PREFIX']
    if _val != _ds.getOption('RADIAL_DIM_SECONDARY_PREFIX'):
        f.write("radial_dim_secondary_prefix = %s\n" % repr(_val))
    _val = _gp['RADIAL_DIM_SECONDARY_SUFFIX']
    if _val != _ds.getOption('RADIAL_DIM_SECONDARY_SUFFIX'):
        f.write("radial_dim_secondary_suffix = %s\n" % repr(_val))
    _val = _gp['RADIAL_DIM_DIA_MODE']
    if _val is not _ds.getOption('RADIAL_DIM_DIA_MODE'):
        f.write("radial_dim_dia_mode = %s\n" % repr(_val))
    _val = _gp['ANGULAR_DIM_PRIMARY_PREFIX']
    if _val != _ds.getOption('ANGULAR_DIM_PRIMARY_PREFIX'):
        f.write("angular_dim_primary_prefix = %s\n" % repr(_val))
    _val = _gp['ANGULAR_DIM_PRIMARY_SUFFIX']
    if _val != _ds.getOption('ANGULAR_DIM_PRIMARY_SUFFIX'):
        f.write("angular_dim_primary_suffix = %s\n" % repr(_val))
    _val = _gp['ANGULAR_DIM_SECONDARY_PREFIX']
    if _val != _ds.getOption('ANGULAR_DIM_SECONDARY_PREFIX'):
        f.write("angular_dim_secondary_prefix = %s\n" % repr(_val))
    _val = _gp['ANGULAR_DIM_SECONDARY_SUFFIX']
    if _val != _ds.getOption('ANGULAR_DIM_SECONDARY_SUFFIX'):
        f.write("angular_dim_secondary_suffix = %s\n" % repr(_val))
    
def _save_textstyle_values(f):
    f.write("#\n# Standard TextBlock parameters\n#\n")
    _gp = globals.prefs
    _ts = _gp['TEXT_STYLE']
    _tsn = _ts.getName()
    _tsf = _ts.getFamily()
    _tsz = _ts.getSize()
    _tss = _ts.getStyle()
    _tsw = _ts.getWeight()
    _tsc = _ts.getColor()
    _tsa = _ts.getAngle()
    _tsl = _ts.getAlignment()
    _tc = text.TextStyle
    f.write("text_style = {\n")
    f.write("    'name' : '%s',\n" % _tsn)
    f.write("    'family' : '%s',\n" % _tsf)
    f.write("    'size' : %s,\n" % repr(_tsz))
    f.write("    'angle' : %s,\n" % repr(_tsa))
    f.write("    'color' : '%s',\n" % str(_tsc))
    f.write("    'weight' : '%s',\n" % _tc.getWeightAsString(_tsw))
    f.write("    'style' : '%s',\n" % _tc.getStyleAsString(_tss))
    f.write("    'alignment' : '%s'\n" % _tc.getAlignmentAsString(_tsl))
    f.write("}\n")
    #
    # save overriden values
    #
    _val = _gp['FONT_FAMILY']
    if _val != _tsf:
        f.write("font_family = '%s'\n" % _val)
    _val = _gp['TEXT_SIZE']
    if abs(_val - _tsz) > 1e-10:
        f.write("text_size = %s\n" % repr(_val))
    _val = _gp['TEXT_ALIGNMENT']
    if _val != _tsl:
        f.write("text_alignment = '%s'\n" % _tc.getAlignmentAsString(_val))
    _val = _gp['FONT_COLOR']
    if _val != _tsc:
        f.write("font_color = '%s'\n" % str(_val))
    _val = _gp['FONT_STYLE']
    if _val != _tss:
        f.write("font_style = '%s'\n" % _tc.getStyleAsString(_val))
    _val = _gp['FONT_WEIGHT']
    if _val != _tsw:
        f.write("font_weight = '%s'\n" % _tc.getWeightAsString(_val))
    _val = _gp['TEXT_ANGLE']
    if abs(_val - _tsa) > 1e-10:
        f.write("text_angle = %s\n" % repr(_val))
    
def _save_style_values(f):
    f.write("#\n# Standard GraphicObject parameters\n#\n")
    _gp = globals.prefs
    _s = _gp['LINE_STYLE']
    _sn = _s.getName()
    _sl = _s.getLinetype()
    _ln = _sl.getName()
    _ll = _sl.getList()
    _sc = _s.getColor()
    _st = _s.getThickness()
    f.write("line_style = {\n")
    f.write("    'name' : '%s',\n" % _sn)
    f.write("    'linetype' : ('%s', %s),\n" % (_ln, repr(_ll)))
    f.write("    'color' : '%s',\n" % str(_sc))
    f.write("    'thickness' : %s\n" % repr(_st))
    f.write("}\n")
    _lt = _gp['LINE_TYPE']
    if _lt != _sl:
        _n = _v.getName()
        _l = _v.getList()
        f.write("line_type = ('%s', %s)\n" % (_n, repr(_l)))
    _c = _gp['LINE_COLOR']
    if _c != _sc:
        f.write("line_color = '%s'\n" % str(_c))
    _t = _gp['LINE_THICKNESS']
    if abs(_t - _st) > 1e-10:
        f.write("line_thickness = %s\n" % repr(_t))
    
def save_user_prefs():
    """Store the current user settings in $HOME/.pythoncad/prefs.py on
    Unix machines, $APPDATA/PythonCAD/prefs.py on Windows.

save_user_prefs()
    """
    if sys.platform == 'win32':
        _home = os.environ.get('APPDATA')
        if _home is None:
            raise ValueError, "Unable to determine APPDATA directory."
        _pdir = os.path.join(_home, 'PythonCAD')
    else:
        _home = os.environ.get('HOME')
        if _home is None:
            raise ValueError, "Unable to determine HOME directory"
        _pdir = os.path.join(_home, '.pythoncad')
    if not os.path.isdir(_pdir):
        os.mkdir(_pdir, 0755)
    _pfile = os.path.join(_pdir, 'prefs.py')
    _f = open(_pfile, "w")
    try:
        _gp = globals.prefs
        _top = """#
# PythonCAD user preferences
#
# If you edit this file manually, be careful!
#
"""
        _f.write("%s" % _top)
        _f.write("#\n# Boolean variables\n#\n")
        _v = _gp['AUTOSPLIT']
        _f.write("autosplit = %s\n" % repr(_v))
        _v = _gp['HIGHLIGHT_POINTS']
        _f.write("highlight_points = %s\n" % repr(_v))
        #
        _f.write("#\n# Size variables (float values)\n#\n")
        _v = _gp['CHAMFER_LENGTH']
        _f.write("chamfer_length = %s\n" %  repr(_v))
        _v = _gp['FILLET_RADIUS']
        _f.write("fillet_radius = %s\n" % repr(_v))
        _v = _gp['LEADER_ARROW_SIZE']
        _f.write("leader_arrow_size = %s\n" % repr(_v))
        #
        _f.write("#\n# Display color settings\n#\n")
        _v = _gp['INACTIVE_LAYER_COLOR']
        _f.write("inactive_layer_color = '%s'\n" % str(_v))
        _v = _gp['BACKGROUND_COLOR']
        _f.write("background_color = '%s'\n" % str(_v))
        _v = _gp['SINGLE_POINT_COLOR']
        _f.write("single_point_color = '%s'\n" % str(_v))
        _v = _gp['MULTI_POINT_COLOR']
        _f.write("multi_point_color = '%s'\n" % str(_v))
        #
        _f.write("#\n# Units\n#\n")
        _v = _gp['UNITS']
        _f.write("units = '%s'\n" % units.Unit.getUnitAsString(_v))
        #
        _save_style_values(_f)
        _save_textstyle_values(_f)
        _save_dimstyle_values(_f)
    finally:
        _f.close()
        
