#
# Copyright (c) 2002, 2003, 2004, 2006 Art Haas
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
# available units
#

import types
import util

MILLIMETERS = 0
MICROMETERS = 1
METERS = 2
KILOMETERS = 3
INCHES = 4
FEET = 5
YARDS = 6
MILES = 7

def get_all_units():
    unitlist = []
    unitlist.append(_('Millimeters'))
    unitlist.append(_('Micrometers'))
    unitlist.append(_('Meters'))
    unitlist.append(_('Kilometers'))
    unitlist.append(_('Inches'))
    unitlist.append(_('Feet'))
    unitlist.append(_('Yards'))
    unitlist.append(_('Miles'))
    return unitlist

class Unit(object):
    """A class defining a unit for linear dimensions.

The Unit class is used to establish what unit to
assign distances between points. The class contains
two methods used to scale distance value to and from
an equivalent distance in millimeters.

A Unit instance has the following methods:

getStringUnit(): Get the instance unit string as a string value.
setStringUnit(): Set the instance unit value based on a string
{set/set}Unit(): Get/Set the instance unit.
toMillimeters(): Convert a distance to millimeters
fromMillimeters(): Convert a distance from millimeters

The Unit class has the following classmethods:

getUnitAsString(): Return a text string for a unit value.
getUnitFromString(): Return a unit value for a given text string.
getUnitStrings(): Return the available unit options as strings.
getUnitValues(): Return the availbable unit values.
    """
    MILLIMETERS = 0
    MICROMETERS = 1
    METERS = 2
    KILOMETERS = 3
    INCHES = 4
    FEET = 5
    YARDS = 6
    MILES = 7
    
    def __init__(self, unit=None):
        _unit = unit
        if _unit is None:
            _unit = Unit.MILLIMETERS
        if (_unit != Unit.MILLIMETERS and
            _unit != Unit.MICROMETERS and
            _unit != Unit.METERS and
            _unit != Unit.KILOMETERS and
            _unit != Unit.INCHES and
            _unit != Unit.FEET and
            _unit != Unit.YARDS and
            _unit != Unit.MILES):
            raise ValueError, "Invalid unit choice: " + str(unit)
        self.__unit = _unit

    def getUnitAsString(cls, u):
        """Return a text string for the unit value.

getUnitAsString(u)

This classmethod returns 'millimeters', 'micrometers', 'meters',
'kilometers', 'inches', 'feet', 'yards', or 'miles'. Passing
an invalid unit value will raise a ValueError exception.
        """
        if not isinstance(u, int):
            raise TypeError, "Invalid argument type: " + `type(u)`
        if u == Unit.MILLIMETERS:
            _str = 'millimeters'
        elif u == Unit.MICROMETERS:
            _str = 'micrometers'
        elif u == Unit.METERS:
            _str = 'meters'
        elif u == Unit.KILOMETERS:
            _str = 'kilometers'
        elif u == Unit.INCHES:
            _str = 'inches'
        elif u == Unit.FEET:
            _str = 'feet'
        elif u == Unit.YARDS:
            _str = 'yards'
        elif u == Unit.MILES:
            _str = 'miles'
        else:
            raise ValueError, "Unexpected unit value: %d" % u
        return _str

    getUnitAsString = classmethod(getUnitAsString)

    def getUnitFromString(cls, s):
        """Return a unit value for a given text string.

getUnitFromString(s)

This classmethod returns a value based on the string argument:

'millimeters' -> Unit.MILLIMETERS
'micrometers' -> Unit.MICROMETERS
'meters' -> Unit.METERS
'kilometers' -> Unit.KILOMETERS
'inches' -> Unit.INCHES
'feet' -> Unit.FEET
'yards' -> 'Unit.YARDS
'miles' -> Unit.MILES 

If the string is not listed above a ValueError execption is raised.
        """
        if not isinstance(s, str):
            raise TypeError, "Invalid argument type: " + `type(s)`
        _ls = s.lower()
        if _ls == 'millimeters':
            _u = Unit.MILLIMETERS
        elif _ls == 'micrometers':
            _u = Unit.MICROMETERS
        elif _ls == 'meters':
            _u = Unit.METERS
        elif _ls == 'kilometers':
            _u = Unit.KILOMETERS
        elif _ls == 'inches':
            _u = Unit.INCHES
        elif _ls == 'feet':
            _u = Unit.FEET
        elif _ls == 'yards':
            _u = Unit.YARDS
        elif _ls == 'miles':
            _u = Unit.MILES
        else:
            raise ValueError, "Unexpected unit string: " + s
        return _u

    getUnitFromString = classmethod(getUnitFromString)

    def getUnitStrings(cls):
        """Return the available unit values as strings.

getUnitStrings()

This classmethod returns a list of strings.
        """
        return [_('Millimeters'),
                _('Micrometers'),
                _('Meters'),
                _('Kilometers'),
                _('Inches'),
                _('Feet'),
                _('Yards'),
                _('Miles')
                ]

    getUnitStrings = classmethod(getUnitStrings)

    def getUnitValues(cls):
        """Return the available unit values.

getUnitValues()

This classmethod returns a list of unit values.
        """
        return [Unit.MILLIMETERS,
                Unit.MICROMETERS,
                Unit.METERS,
                Unit.KILOMETERS,
                Unit.INCHES,
                Unit.FEET,
                Unit.YARDS,
                Unit.MILES
                ]

    getUnitValues = classmethod(getUnitValues)
    
    def getUnit(self):
        return self.__unit

    def getStringUnit(self):
        _u = self.__unit
        if _u == Unit.MILLIMETERS:
            _str = 'millimeters'
        elif _u == Unit.MICROMETERS:
            _str = 'micrometers'
        elif _u == Unit.METERS:
            _str = 'meters'
        elif _u == Unit.KILOMETERS:
            _str = 'kilometers'
        elif _u == Unit.INCHES:
            _str = 'inches'
        elif _u == Unit.FEET:
            _str = 'feet'
        elif _u == Unit.YARDS:
            _str = 'yards'
        elif _u == Unit.MILES:
            _str = 'miles'
        else:
            raise ValueError, "Unexpected unit: %d" % _u
        return _str

    def setStringUnit(self, unit):
        if not isinstance(unit, types.StringTypes):
            raise TypeError, "Unexpected unit string: " + str(unit)
        _ul = str(unit.lower())
        if _ul == 'millimeters':
            _unit = MILLIMETERS
        elif _ul == 'micrometers':
            _unit = MICROMETERS
        elif _ul == 'meters':
            _unit = METERS
        elif _ul == 'kilometers':
            _unit = KILOMETERS
        elif _ul == 'inches':
            _unit = INCHES
        elif _ul == 'feet':
            _unit = FEET
        elif _ul == 'yards':
            _unit = YARDS
        elif _ul == 'miles':
            _unit = MILES
        else:
            raise ValueError, "Unexpected unit string: %s" % unit
        self.__unit = _unit
            
    def setUnit(self, unit):
        if (unit != Unit.MILLIMETERS and
            unit != Unit.MICROMETERS and
            unit != Unit.METERS and
            unit != Unit.KILOMETERS and
            unit != Unit.INCHES and
            unit != Unit.FEET and
            unit != Unit.YARDS and
            unit != Unit.MILES):
            raise ValueError, "Invalid unit choice: " + str(unit)
        self.__unit = unit

    unit = property(getUnit, setUnit, None, "Basic unit.")

    def toMillimeters(self, value):
        """Scale a value to the equivalent distance in millimeters.

toMillimeters(value)
        """
        _v = util.get_float(value)
        if self.__unit == Unit.MILLIMETERS:
            _sv = _v
        elif self.__unit == Unit.MICROMETERS:
            _sv = _v * 1e-3
        elif self.__unit == Unit.METERS:
            _sv = _v * 1e3
        elif self.__unit == Unit.KILOMETERS:
            _sv = _v * 1e6
        elif self.__unit == Unit.INCHES:
            _sv = _v * 25.4
        elif self.__unit == Unit.FEET:
            _sv = _v * 304.8
        elif self.__unit == Unit.YARDS:
            _sv = _v * 914.4
        elif self.__unit == Unit.MILES:
            _sv = _v * 1609344.4
        else:
            raise ValueError, "Undefined unit value! " + str(self.__unit)
        return _sv

    def fromMillimeters(self, value):
        """Scale a value from an equivalent distance in millimeters.

fromMillimeters(value)
        """
        _v = util.get_float(value)
        if self.__unit == Unit.MILLIMETERS:
            _sv = _v
        elif self.__unit == Unit.MICROMETERS:
            _sv = _v * 1e3
        elif self.__unit == Unit.METERS:
            _sv = _v * 1e-3
        elif self.__unit == Unit.KILOMETERS:
            _sv = _v * 1e-6
        elif self.__unit == Unit.INCHES:
            _sv = _v / 25.4
        elif self.__unit == Unit.FEET:
            _sv = _v / 304.8
        elif self.__unit == Unit.YARDS:
            _sv = _v / 914.4
        elif self.__unit == Unit.MILES:
            _sv = _v / 1609344.4
        else:
            raise ValueError, "Undefined unit value! " + str(self.__unit)
        return _sv

def unit_string(value):
    """Return a text string for the integer unit value.

unit_string(value)
    """
    if value == MILLIMETERS:
        _str = 'millimeters'
    elif value == MICROMETERS:
        _str = 'micrometers'
    elif value == METERS:
        _str = 'meters'
    elif value == KILOMETERS:
        _str = 'kilometers'
    elif value == INCHES:
        _str = 'inches'
    elif value == FEET:
        _str = 'feet'
    elif value == YARDS:
        _str = 'yards'
    elif value == MILES:
        _str = 'miles'
    else:
        raise ValueError, "Unexpected unit: " + str(value)
    return _str
        
        
