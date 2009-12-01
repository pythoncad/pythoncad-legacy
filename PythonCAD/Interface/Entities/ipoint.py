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

from PythonCAD.Generic import point


class IPoint(object):

    def __init__(self, ctx, gpoint):
        self.__ctx = ctx
        self.__gpoint = gpoint

    def draw(self, color):
        print "IPoint.draw()"
        # position
        x = self.__gpoint.getx()
        y = self.__gpoint.gety()
        print x, y
        # set linewidth 2 pixels
        self.__ctx.set_line_width(2)
        # set color
        print color
        self.__ctx.set_source_rgb(1, 0, 0)
        # draw rectangle
<<<<<<< HEAD
        self.__ctx.rectangle(-8, -8, 8, 8)
        self.__ctx.translate(x, y)
=======
        self.__ctx.rectangle(x-8, y-8, x+8, y+8)
        #self.__ctx.translate(x, y)
>>>>>>> ee1bf5e10f88608da6191a17e1f65ffeec3d3ca1
        self.__ctx.stroke()

        
        