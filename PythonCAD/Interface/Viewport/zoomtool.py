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

#import math
#import types
import pygtk
pygtk.require('2.0')
#import gtk
#from gtk import gdk

#import cairo

from PythonCAD.Generic.point import Point
#from PythonCAD.Interface.Viewport.viewport import IViewport


class ZoomTool(object):

#---------------------------------------------------------------------------------------------------
    def __init__(self, viewport):
        self.__viewport = viewport
        self.__anchor_x = 0
        self.__anchor_y = 0
        self.__x = 0
        self.__y = 0

#---------------------------------------------------------------------------------------------------
    def window_init(self, x, y):
        self.__anchor_x = x
        self.__anchor_y = y
        self.__x = self.__anchor_x
        self.__y = self.__anchor_y
        self.__viewport.view_state.current = self.__viewport.view_state.ZoomWindow

#---------------------------------------------------------------------------------------------------
    def window_drag(self):
        # show the scene on the new position
        self.__viewport.show_scene()
        # convert to view coordinates
        px1, py1 = self.__viewport.world_to_view(self.__anchor_x, self.__anchor_y)
        px2, py2 = self.__viewport.world_to_view(self.__x, self.__y)
        # create a cairo context for the cursor
        ctx = self.__viewport.window.cairo_create()
        # white transparent zoom window
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
        ctx.set_line_width(1.0)
        # draw a rectangle
        ctx.rectangle(px1, py1, px2 - px1, py2 - py1)
        ctx.fill()
        ctx.stroke()

#---------------------------------------------------------------------------------------------------
    def pan_init(self, x, y):
        self.__anchor_x = x
        self.__anchor_y = y
        self.__x = self.__anchor_x
        self.__y = self.__anchor_y
        self.__viewport.view_state.current = self.__viewport.view_state.ZoomPan

#---------------------------------------------------------------------------------------------------
    def pan_drag(self):
        # convert to view coordinates
        px1, py1 = self.__viewport.world_to_view(self.__anchor_x, self.__anchor_y)
        px2, py2 = self.__viewport.world_to_view(self.__x, self.__y)
        # show the scene on the new position
        self.__viewport.show_scene(px2 - px1, py2 - py1)

#---------------------------------------------------------------------------------------------------
    def drag_point(self, x, y):
        # current dragpoint
        self.__x, self.__y = self.__viewport.view_to_world(x, y)
        # redraw
        self.__viewport.invalidate()

#---------------------------------------------------------------------------------------------------
    def set(self):
        # wich action
        if self.__viewport.view_state.current == self.__viewport.view_state.ZoomPan:
            self.__set_pan()
        elif self.__viewport.view_state.current == self.__viewport.view_state.ZoomWindow:
            self.__set_window()

#---------------------------------------------------------------------------------------------------
    def __set_window(self):
        xmin = min(self.__anchor_x, self.__x)
        xmax = max(self.__anchor_x, self.__x)
        ymin = min(self.__anchor_y, self.__y)
        ymax = max(self.__anchor_y, self.__y)
        # set new world window
        self.__viewport.world_x_min = xmin
        self.__viewport.world_x_max = xmax
        self.__viewport.world_y_min = ymin
        self.__viewport.world_y_max = ymax
        # zoom to new world window
        self.__viewport.regenerate()

#---------------------------------------------------------------------------------------------------
    def __set_pan(self):
        dx = self.__anchor_x - self.__x
        dy = self.__anchor_y - self.__y
        # calculate new world window
        self.__viewport.world_x_min += dx
        self.__viewport.world_x_max += dx
        self.__viewport.world_y_min += dy
        self.__viewport.world_y_max += dy
        # zoom to new world window
        self.__viewport.regenerate()

#---------------------------------------------------------------------------------------------------
    def __set_anchor(self, point):
        self.__anchor_x, self.__anchor_y = point.getCoords()

    def __get_anchor(self, point):
        return Point(self.__anchor_x, self.__anchor_y)

    anchor_point = property(__get_anchor, __set_anchor, None, "get/set anchor point")

#---------------------------------------------------------------------------------------------------
    def __set_point(self, point):
        self.__x, self.__y = point.getCoords()

    def __get_point(self, point):
        return Point(self.__x, self.__y)

    point = property(__get_point, __set_point, None, "get/set point")

