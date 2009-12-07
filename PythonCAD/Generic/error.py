#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo
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
# <Error Class> command functions/Class 
#

class pythonCadError(Exception): pass

class pythonCadEntityCreatioError(Exception): 
    def __init__(self,command,msg):
        self.__command=command
        self.__msg=msg
        
    def getMessage(self):
        """
            get The message error
        """
        return self.__msg
        
    def getCommand(self):
        """
            get the command that throw the exception
        """
        return self.__command