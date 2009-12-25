#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo, Gertwin Groen
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the termscl_bo of the GNU General Public License as published by
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


class ViewState(object):
    def __init__(self):
        # different view states
        names = 'None DrawScene CursorMotion RubberBand ZoomPan ZoomWindow'
        for number, name in enumerate(names.split()):
            #print name, "=", number
            setattr(self, name, number)
        # current state
        self.__current = self.None
        # is the view initialized
        self.__initialized = False

    def __set_current(self, value):
        #print "ViewState.__set_current"
        self.__current = value

    def __get_current(self):
        #print "ViewState.__get_current"
        return self.__current

    current = property(__get_current, __set_current, None, "get/set current state")
            
    def __set_initialized(self, value):
        self.__initialized = value

    def __get_initialized(self):
        #print "ViewState.__get_current"
        return self.__initialized

    initialized = property(__get_initialized, __set_initialized, None, "get/set initialized")


    def reset(self):
        #print "ViewState.reset"
        self.__previous = self.__current = self.None

            