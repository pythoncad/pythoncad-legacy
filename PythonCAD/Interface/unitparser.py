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
# This module provide a parser for the imput interface
#
from sympy.physics  import units
from sympy          import Rational

#from Generic.Kernel.GeoEntity.point import Point

class UnitParser(object):
    cad_leng=units.Unit('cad_leng','mm')
    converter={units.m: cad_leng*Rational(1000)}
    @staticmethod
    def decodePoint(self, value, previusPoint=None):
        """
            this static method decode an imput and return a point(mm,mm)
        """
        pass
    @staticmethod
    def decodeSingleValueLengh(value):
        """
            this static method decode an imput and return a value in mm
        """
        args, v=str(value).split(' ')
        unitsValue=float(args)*units.m
        if unitsValue:
            cad_mm=unitsValue.subs(UnitParser.converter)
            return_value=float(str(cad_mm.evalf()).split('*')[0])
            return return_value
        return None

if __name__ == '__main__':
    print UnitParser.decodeSingleValueLengh('10 m')
    
    
