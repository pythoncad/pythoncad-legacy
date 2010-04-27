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
# This is the base class for all the geometrical entitys
#

class GeometricalEntity(object):
    """
        This class provide the basic interface for all the geometrical entitys
    """
    def getConstructionElements(self):
        """
            Get the construction element of ..
            This must return a tuple of object better if there are point
        """
        pass

class GeometricalEntityComposed(object):
    """
        this class provide the basic object for composed entity 
    """
    def getConstructionElements(self):
        """
            Get the construction element of ..
            This must return a tuple of object better if there are point
        """
        pass
    def getReletedComponent(self):
        """
            Get The releted object to be updated
        """
        pass
