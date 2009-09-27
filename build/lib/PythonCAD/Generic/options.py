#
# Copyright (c) 2002, 2004, 2006 Art Haas
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
# handle setting and retrieving of the various options
# and preferences in an image
#
# none of these functions should be called directly - they
# are all meant as private functions for an Image object

import types

from PythonCAD.Generic import units
from PythonCAD.Generic import dimension
from PythonCAD.Generic import text
from PythonCAD.Generic import style
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype

#
# generic type tests
#

def _test_boolean_value(key, value):
    if not (value is True or value is False):
        raise ValueError, "Invalid boolean for '%s'" + key

def _test_int_value(key, value, min=None, max=None):
    if not isinstance(value, int):
        raise TypeError, "Integer required for '%s'" % key
    if min is not None:
        assert isinstance(min, int), "Invalid minimum value: " + str(min)
        if value < min:
            raise ValueError, "Invalid value: %d < %d (min)" % (value, min)
    if max is not None:
        assert isinstance(max, int), "Invalid maximum value: " + str(max)
        if value > max:
            raise ValueError, "Invalid value: %d > %d (max)" % (value, max)

def _test_float_value(key, value, min=None, max=None):
    if not isinstance(value, float):
        raise TypeError, "Float required for '%s'" % key
    if min is not None:
        assert isinstance(min, float), "Invalid minimum value: " + str(min)
        if value < min:
            raise ValueError, "Invalid value: %g < %g (min)" % (value, min)
    if max is not None:
        assert isinstance(max, float), "Invalid maximum value: " + str(max)
        if value > max:
            raise ValueError, "Invalid value: %g > %g (max)" % (value, max)

def _test_unicode_value(key, value):
    if not isinstance(value, unicode):
        raise TypeError, "Unicode string required for '%s'" % key

def _test_color_value(key, value):
    if not isinstance(value, color.Color):
        raise TypeError, "Color object required for '%s'" % key

def _test_linetype_value(key, value):
    if not isinstance(value, linetype.Linetype):
        raise TypeError, "Invalid line type for '%s'" % key

def _test_linestyle_value(key, value):
    if not isinstance(value, style.Style):
        raise TypeError, "Invalid text style for '%s'" % key
    
def _test_font_family(key, value):
    if not isinstance(value, types.StringTypes):
        raise TypeError, "String required for '%s'" % key
    if value == '':
        raise ValueError, "Non-null string required for '%s'" % key

def _test_dimstyle(key, value):
    if not isinstance(value, dimension.DimStyle):
        raise TypeError, "Invalid DimStyle for '%s'" % key
    
def _test_font_weight(key, value):
    if value not in text.TextStyle.getWeightValues():
        raise ValueError, "Invalid font weight for '%s'" % key

def _test_font_style(key, value):
    if value not in text.TextStyle.getStyleValues():
        raise ValueError, "Invalid font style for '%s'" % key

def _test_units(key, value):
    if value not in units.Unit.getUnitValues():
        raise ValueError, "Invalid unit for '%s'" %  key

#
# dimension related tests
#

def _set_dim_style(opt, ds):
    _test_dimstyle(opt, ds)
    
def _set_dim_primary_font_family(opt, family):
    _test_font_family(opt, family)

def _set_dim_primary_font_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_dim_primary_text_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_dim_primary_font_style(opt, st):
    _test_font_style(opt, st)

def _set_dim_primary_font_weight(opt, weight):
    _test_font_weight(opt, weight)

def _set_dim_primary_font_color(opt, col):
    _test_color_value(opt, col)

def _set_dim_primary_prefix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_dim_primary_suffix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_dim_primary_units(opt, u):
    _test_units(opt, u)

def _set_dim_primary_precision(opt, prec):
    _test_int_value(opt, prec, min=0, max=15)

def _set_dim_primary_print_zero(opt, flag):
    _test_boolean_value(opt, flag)

def _set_dim_primary_trail_decimal(opt, flag):
    _test_boolean_value(opt, flag)

def _set_dim_secondary_font_family(opt, family):
    _test_font_family(opt, family)

def _set_dim_secondary_font_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_dim_secondary_text_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_dim_secondary_font_style(opt, st):
    _test_font_style(opt, st)

def _set_dim_secondary_font_weight(opt, weight):
    _test_font_weight(opt, weight)

def _set_dim_secondary_font_color(opt, col):
    _test_color_value(opt, col)

def _set_dim_secondary_prefix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_dim_secondary_suffix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_dim_secondary_units(opt, u):
    _test_units(opt, u)

def _set_dim_secondary_precision(opt, prec):
    _test_int_value(opt, prec, min=0, max=15)

def _set_dim_secondary_print_zero(opt, flag):
    _test_boolean_value(opt, flag)

def _set_dim_secondary_trail_decimal(opt, flag):
    _test_boolean_value(opt, flag)

def _set_dim_offset(opt, offset):
    _test_float_value(opt, offset, min=0.0)

def _set_dim_extension(opt, ext):
    _test_float_value(opt, ext, min=0.0)

def _set_dim_color(opt, col):
    _test_color_value(opt, col)

def _set_dim_thickness(opt, ext):
    _test_float_value(opt, ext, min=0.0)

def _set_dim_dual_mode(opt, mode):
    _test_boolean_value(opt, mode)

def _set_dim_position_offset(opt, ext):
    _test_float_value(opt, ext, min=0.0)

def _set_dim_dual_mode_offset(opt, ext):
    _test_float_value(opt, ext, min=0.0)

def _set_dim_position(opt, pos):
    if pos not in dimension.Dimension.getPositionValues():
        raise ValueError, "Invalid dimension position: " + str(pos)

def _set_dim_endpoint(opt, ept):
    if ept not in dimension.Dimension.getEndpointTypeValues():
        raise ValueError, "Invalid endpoint value: " + str(ept)

def _set_dim_endpoint_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_radial_dim_primary_prefix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_radial_dim_primary_suffix(opt, sfx):
    _test_unicode_value(opt, sfx)

def _set_radial_dim_secondary_prefix(opt, sfx):
    _test_unicode_value(opt, sfx)

def _set_radial_dim_secondary_suffix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_radial_dim_dia_mode(opt, flag):
    _test_boolean_value(opt, flag)

def _set_angular_dim_primary_prefix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_angular_dim_primary_suffix(opt, sfx):
    _test_unicode_value(opt, sfx)

def _set_angular_dim_secondary_prefix(opt, pfx):
    _test_unicode_value(opt, pfx)

def _set_angular_dim_secondary_suffix(opt, sfx):
    _test_unicode_value(opt, sfx)

def _set_angular_dim_small_angle_mode(opt, flag):
    _test_boolean_value(opt, flag)

#
# text related tests
#

def _set_text_style(opt, textstyle):
    if not isinstance(textstyle, text.TextStyle):
        raise TypeError, "Invalid text style: " + `textstyle`

def _set_font_family(opt, family):
    _test_font_family(opt, family)

def _set_font_style(opt, st):
    _test_font_style(opt, st)

def _set_font_weight(opt, weight):
    _test_font_weight(opt, weight)

def _set_font_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_font_color(opt, col):
    _test_color_value(opt, col)

def _set_text_size(opt, size):
    _test_float_value(opt, size, min=0.0)

def _set_text_angle(opt, angle):
    _test_float_value(opt, angle)

def _set_text_alignment(opt, align):
    if align not in text.TextStyle.getAlignmentValues():
        raise ValueError, "Invalid text alignment: " + str(align)
    
def _set_chamfer_length(opt, length):
    _test_float_value(opt, length, min=0.0)

def _set_fillet_radius(opt, radius):
    _test_float_value(opt, radius)

def _set_line_style(opt, st):
    _test_linestyle_value(opt, st)

def _set_line_color(opt, col):
    _test_color_value(opt, col)

def _set_line_type(opt, lt):
    _test_linetype_value(opt, lt)

def _set_line_thickness(opt, thickness):
    _test_float_value(opt, thickness, min=0.0)

def _set_units(opt, u):
    _test_units(opt, u)

def _set_highlight_points(opt, flag):
    _test_boolean_value(opt, flag)

def _set_inactive_layer_color(opt, col):
    _test_color_value(opt, col)

def _set_background_color(opt, col):
    _test_color_value(opt, col)

def _set_single_point_color(opt, col):
    _test_color_value(opt, col)

def _set_multi_point_color(opt, col):
    _test_color_value(opt, col)
    
def _set_autosplit(opt, col):
    _test_boolean_value(opt, col)

def _leader_arrow_size(opt, size):
    _test_float_value(opt, size, min=0.0)

#
# the keys of this dictionary represent options that have
# tests to validate the option value is suitable
#

_optdict = {
    'DIM_STYLE' : _set_dim_style,
    'DIM_PRIMARY_FONT_FAMILY' : _set_dim_primary_font_family,
    'DIM_PRIMARY_FONT_SIZE' : _set_dim_primary_font_size,
    'DIM_PRIMARY_TEXT_SIZE' : _set_dim_primary_text_size,
    'DIM_PRIMARY_FONT_WEIGHT' : _set_dim_primary_font_weight,
    'DIM_PRIMARY_FONT_STYLE' : _set_dim_primary_font_style,
    'DIM_PRIMARY_FONT_COLOR' : _set_dim_primary_font_color,
    'DIM_PRIMARY_TEXT_ANGLE' : _set_text_angle,
    'DIM_PRIMARY_TEXT_ALIGNMENT' : _set_text_alignment,
    'DIM_PRIMARY_PREFIX' : _set_dim_primary_prefix,
    'DIM_PRIMARY_SUFFIX' : _set_dim_primary_suffix,
    'DIM_PRIMARY_PRECISION' : _set_dim_primary_precision,
    'DIM_PRIMARY_UNITS' : _set_dim_primary_units,
    'DIM_PRIMARY_LEADING_ZERO' : _set_dim_primary_print_zero,
    'DIM_PRIMARY_TRAILING_DECIMAL': _set_dim_primary_trail_decimal,
    'DIM_SECONDARY_FONT_FAMILY' : _set_dim_secondary_font_family,
    'DIM_SECONDARY_FONT_SIZE' : _set_dim_secondary_font_size,
    'DIM_SECONDARY_TEXT_SIZE' : _set_dim_secondary_text_size,
    'DIM_SECONDARY_FONT_WEIGHT' : _set_dim_secondary_font_weight,
    'DIM_SECONDARY_FONT_STYLE' : _set_dim_secondary_font_style,
    'DIM_SECONDARY_FONT_COLOR' : _set_dim_secondary_font_color,
    'DIM_SECONDARY_TEXT_ANGLE' : _set_text_angle,
    'DIM_SECONDARY_TEXT_ALIGNMENT' : _set_text_alignment,
    'DIM_SECONDARY_PREFIX' : _set_dim_secondary_prefix,
    'DIM_SECONDARY_SUFFIX' : _set_dim_secondary_suffix,
    'DIM_SECONDARY_PRECISION' : _set_dim_secondary_precision,
    'DIM_SECONDARY_UNITS' : _set_dim_secondary_units,
    'DIM_SECONDARY_LEADING_ZERO' : _set_dim_secondary_print_zero,
    'DIM_SECONDARY_TRAILING_DECIMAL': _set_dim_secondary_trail_decimal,
    'DIM_OFFSET' : _set_dim_offset,
    'DIM_EXTENSION': _set_dim_extension,
    'DIM_COLOR' : _set_dim_color,
    'DIM_THICKNESS' : _set_dim_thickness,
    'DIM_POSITION': _set_dim_position,
    'DIM_ENDPOINT': _set_dim_endpoint,
    'DIM_ENDPOINT_SIZE' : _set_dim_endpoint_size,
    'DIM_DUAL_MODE' : _set_dim_dual_mode,
    'DIM_POSITION_OFFSET' : _set_dim_position_offset,
    'DIM_DUAL_MODE_OFFSET' : _set_dim_dual_mode_offset,
    'RADIAL_DIM_PRIMARY_PREFIX' : _set_radial_dim_primary_prefix,
    'RADIAL_DIM_PRIMARY_SUFFIX' : _set_radial_dim_primary_suffix,
    'RADIAL_DIM_SECONDARY_PREFIX' : _set_radial_dim_secondary_prefix,
    'RADIAL_DIM_SECONDARY_SUFFIX' : _set_radial_dim_secondary_suffix,
    'RADIAL_DIM_DIA_MODE' : _set_radial_dim_dia_mode,
    'ANGULAR_DIM_PRIMARY_PREFIX' : _set_angular_dim_primary_prefix,
    'ANGULAR_DIM_PRIMARY_SUFFIX' : _set_angular_dim_primary_suffix,
    'ANGULAR_DIM_SECONDARY_PREFIX' : _set_angular_dim_secondary_prefix,
    'ANGULAR_DIM_SECONDARY_SUFFIX' : _set_angular_dim_secondary_suffix,
    'TEXT_STYLE' : _set_text_style,
    'FONT_FAMILY' : _set_font_family,
    'FONT_STYLE' : _set_font_style,
    'FONT_WEIGHT' : _set_font_weight,
    'FONT_SIZE' : _set_font_size,
    'FONT_COLOR' : _set_font_color,
    'TEXT_SIZE' : _set_text_size,
    'TEXT_ANGLE' : _set_text_angle,
    'TEXT_ALIGNMENT' : _set_text_alignment,
    'CHAMFER_LENGTH' : _set_chamfer_length,
    'FILLET_RADIUS' : _set_fillet_radius,
    'UNITS' : _set_units,
    'LINE_STYLE' : _set_line_style,
    'LINE_COLOR' : _set_line_color,
    'LINE_TYPE' : _set_line_type,
    'LINE_THICKNESS': _set_line_thickness,
    'HIGHLIGHT_POINTS' : _set_highlight_points,
    'INACTIVE_LAYER_COLOR' : _set_inactive_layer_color,
    'BACKGROUND_COLOR' : _set_background_color,
    'SINGLE_POINT_COLOR' : _set_single_point_color,
    'MULTI_POINT_COLOR' : _set_multi_point_color,
    'AUTOSPLIT' : _set_autosplit,
    'LEADER_ARROW_SIZE' : _leader_arrow_size,
    }

#
# the test_option() function will return True for tested
# options that validate or for unknown options. Invalid
# tested options will raise an exception that the caller
# must handle
#

def test_option(opt, val):
    _valid = True
    if opt in _optdict:
        _optdict[opt](opt, val)
    return _valid

class OptionManager(object):

    def isDimStyle(obj):
        return isinstance(obj, dimension.DimStyle)

    isDimStyle = staticmethod(isDimStyle)

    def isTextStyle(obj):
        return isinstance(obj, text.TextStyle)

    isTextStyle = staticmethod(isTextStyle)

    def isStyle(obj):
        return isinstance(obj, style.Style)

    isStyle = staticmethod(isStyle)

    def isLinetype(obj):
        return isinstance(obj, linetype.Linetype)

    isLinetype = staticmethod(isLinetype)
    
    def isStringType(obj):
        return isinstance(obj, types.StringTypes)

    isStringType = staticmethod(isStringType)

    def isInt(obj):
        return isinstance(obj, int)

    isInt = staticmethod(isInt)

    def isFloat(obj):
        return isinstance(obj, float)

    isFloat = staticmethod(isFloat)

    def isColor(obj):
        return isinstance(obj, color.Color)

    isColor = staticmethod(isColor)

    def isBoolean(obj):
        return ((hasattr(types, 'BooleanType') and
                 isinstance(obj, types.BooleanType)) or
                (obj is True or obj is False))

    isBoolean = staticmethod(isBoolean)

    def checkEndpointType(obj):
        return obj in dimension.Dimension.getEndpointTypeValues()

    checkEndpointType = staticmethod(checkEndpointType)

    def checkPosition(obj):
        return obj in dimension.Dimension.getPositionValues()
    
    checkPosition = staticmethod(checkPosition)

    def checkFontWeight(obj):
        return obj in text.TextStyle.getWeightValues()

    checkFontWeight = staticmethod(checkFontWeight)

    def checkFontStyle(obj):
        return obj in text.TextStyle.getStyleValues()

    checkFontStyle = staticmethod(checkFontStyle)

    def checkTextAlignment(obj):
        return obj in text.TextStyle.getAlignmentValues()

    checkTextAlignment = staticmethod(checkTextAlignment)

    def checkUnit(obj):
        return obj in units.Unit.getUnitValues()

    checkUnit = staticmethod(checkUnit)

    def checkPrecision(obj):
        return not (obj < 0 or obj > 15)

    checkPrecision = staticmethod(checkPrecision)

    def checkPositiveFloat(obj):
        return not obj < 0.0

    checkPositiveFloat = staticmethod(checkPositiveFloat)
    
    __optdict = {
        'DIM_STYLE' : ('isDimStyle', None),
        'DIM_PRIMARY_FONT_FAMILY' : ('isStringType', None),
        'DIM_PRIMARY_FONT_WEIGHT' : ('isInt', 'checkFontWeight'),
        'DIM_PRIMARY_FONT_STYLE' : ('isInt', 'checkFontStyle'),
        'DIM_PRIMARY_FONT_COLOR' : ('isColor', None),
        'DIM_PRIMARY_TEXT_SIZE' : ('isFloat', 'checkPositiveFloat'),
        'DIM_PRIMARY_TEXT_ANGLE' : ('isFloat', None),
        'DIM_PRIMARY_TEXT_ALIGNMENT' : ('isInt', 'checkTextAlignment'),
        'DIM_PRIMARY_PREFIX' : ('isStringType', None),
        'DIM_PRIMARY_SUFFIX' : ('isStringType', None),
        'DIM_PRIMARY_PRECISION' : ('isInt', 'checkPrecision'),
        'DIM_PRIMARY_UNITS' : ('isInt', 'checkUnit'),
        'DIM_PRIMARY_LEADING_ZERO' : ('isBoolean', None),
        'DIM_PRIMARY_TRAILING_DECIMAL': ('isBoolean', None),
        'DIM_SECONDARY_FONT_FAMILY' : ('isStringType', None),
        'DIM_SECONDARY_FONT_WEIGHT' : ('isInt', 'checkFontWeight'),
        'DIM_SECONDARY_FONT_STYLE' : ('isInt', 'checkFontStyle'),
        'DIM_SECONDARY_FONT_COLOR' : ('isColor', None),
        'DIM_SECONDARY_TEXT_SIZE' : ('isFloat', 'checkPositiveFloat'),
        'DIM_SECONDARY_TEXT_ANGLE' : ('isFloat', None),
        'DIM_SECONDARY_TEXT_ALIGNMENT' : ('isInt', 'checkTextAlignment'),
        'DIM_SECONDARY_PREFIX' : ('isStringType', None),
        'DIM_SECONDARY_SUFFIX' : ('isStringType', None),
        'DIM_SECONDARY_PRECISION' : ('isInt', 'checkPrecision'),
        'DIM_SECONDARY_UNITS' : ('isInt', 'checkUnit'),
        'DIM_SECONDARY_LEADING_ZERO' : ('isBoolean', None),
        'DIM_SECONDARY_TRAILING_DECIMAL': ('isBoolean', None),
        'DIM_OFFSET' : ('isFloat', 'checkPositiveFloat'),
        'DIM_EXTENSION': ('isFloat', 'checkPositiveFloat'),
        'DIM_COLOR' : ('isColor', None),
        'DIM_THICKNESS' : ('isFloat', 'checkPositiveFloat'),
        'DIM_POSITION': ('isInt', 'checkPosition'),
        'DIM_ENDPOINT': ('isInt', 'checkEndpointType'),
        'DIM_ENDPOINT_SIZE' : ('isFloat', 'checkPositiveFloat'),
        'DIM_DUAL_MODE' : ('isBoolean', None),
        'DIM_POSITION_OFFSET' : ('isFloat', None),
        'DIM_DUAL_MODE_OFFSET' : ('isFloat', None),
        'RADIAL_DIM_PRIMARY_PREFIX' : ('isStringType', None),
        'RADIAL_DIM_PRIMARY_SUFFIX' : ('isStringType', None),
        'RADIAL_DIM_SECONDARY_PREFIX' : ('isStringType', None),
        'RADIAL_DIM_SECONDARY_SUFFIX' : ('isStringType', None),
        'RADIAL_DIM_DIA_MODE' : ('isBoolean', None),
        'ANGULAR_DIM_PRIMARY_PREFIX' : ('isStringType', None),
        'ANGULAR_DIM_PRIMARY_SUFFIX' : ('isStringType', None),
        'ANGULAR_DIM_SECONDARY_PREFIX' : ('isStringType', None),
        'ANGULAR_DIM_SECONDARY_SUFFIX' : ('isStringType', None),
        'TEXT_STYLE' : ('isTextStyle', None),
        'FONT_FAMILY' : ('isStringType', None),
        'FONT_STYLE' : ('isInt', 'checkFontStyle'),
        'FONT_WEIGHT' : ('isInt', 'checkFontWeight'),
        'FONT_COLOR' : ('isColor', None),
        'TEXT_SIZE' : ('isFloat', 'checkPositiveFloat'),
        'TEXT_ANGLE' : ('isFloat', None),
        'TEXT_ALIGNMENT' : ('isInt', 'checkTextAlignment'),
        'CHAMFER_LENGTH' : ('isFloat', 'checkPositiveFloat'),
        'FILLET_RADIUS' : ('isFloat', 'checkPositiveFloat'),
        'FILLET_TWO_TRIM_MODE' : ('isStringType', None),
        'UNITS' : ('isInt', 'checkUnit'),
        'LINE_STYLE' : ('isStyle', None),
        'LINE_COLOR' : ('isColor', None),
        'LINE_TYPE' : ('isLinetype', None),
        'LINE_THICKNESS': ('isFloat', 'checkPositiveFloat'),
        'HIGHLIGHT_POINTS' : ('isBoolean', None),
        'AUTOSPLIT' : ('isBoolean', None),
        'INACTIVE_LAYER_COLOR' : ('isColor', None),
        'BACKGROUND_COLOR' : ('isColor', None),
        'SINGLE_POINT_COLOR' : ('isColor', None),
        'MULTI_POINT_COLOR' : ('isColor', None),
        'LEADER_ARROW_SIZE' : ('isFloat', 'checkPositiveFloat'),
    }

    def testOption(cls, opt, value):
        _tests = cls.__optdict.get(opt)
        if _tests is None:
            raise KeyError, "Unknown option: '%s'" % opt
        _ttest, _vtest = _tests
        if not (getattr(cls, _ttest))(value):
            raise TypeError, "Invalid type for option %s: '%s'" % (opt, `type(value)`)
        if _vtest is not None and not (getattr(cls, _vtest))(value):
            raise ValueError, "Invalid value for option %s: '%s'" % (opt, str(value))

    testOption = classmethod(testOption)
