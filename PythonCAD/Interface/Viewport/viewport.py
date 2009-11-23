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

import math
import pygtk
pygtk.require('2.0')
import gtk


class IViewport(gtk.DrawingArea):

#-------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IViewport, self).__init__()
        #
        self.__gtkimage = parent
        self.__image = self.__gtkimage.getImage()

#        black = gtk.gdk.color_parse('black')
#        self.__da.modify_fg(gtk.STATE_NORMAL, black)
#        self.__da.modify_bg(gtk.STATE_NORMAL, black)
#        pane.pack2(self.__da, True, False)
#        self.__da.set_flags(gtk.CAN_FOCUS)
#        self.__da.connect("event", self.__daEvent)
#        self.__da.connect("expose_event", self.__exposeEvent)
#        self.__da.connect("realize", self.__realizeEvent)
#        self.__da.connect("configure_event", self.__configureEvent)
#        # self.__da.connect("focus_in_event", self.__focusInEvent)
#        # self.__da.connect("focus_out_event", self.__focusOutEvent)
#
#        self.__da.set_events(gtk.gdk.EXPOSURE_MASK |
#                             gtk.gdk.LEAVE_NOTIFY_MASK |
#                             gtk.gdk.BUTTON_PRESS_MASK |
#                             gtk.gdk.BUTTON_RELEASE_MASK |
#                             gtk.gdk.ENTER_NOTIFY_MASK|
#                             gtk.gdk.LEAVE_NOTIFY_MASK|
#                             gtk.gdk.KEY_PRESS_MASK |
#                             gtk.gdk.KEY_RELEASE_MASK |
#                             gtk.gdk.FOCUS_CHANGE_MASK |
#                             gtk.gdk.POINTER_MOTION_MASK)


        # event handlers
        #self.connect("expose_event", self.__exposeEvent)

#-------------------------------------------------------------------------------
    def refresh(self, area):
        print "IViewport.refresh()"
        # refresh area
        x, y, width, height = area
        print x, y, width, height
        # 
        self.__ctx = self.window.cairo_create()
        # set a clip region for the expose event
        self.__ctx.rectangle(x, y, width, height)
        self.__ctx.clip()
        # draw background
        self.__ctx.set_source_rgb(0.5, 0.5, 0.5)
        #self.__ctx.rectangle(x, y, width, height)
        self.__ctx.fill()
        # draw the entities
        self.draw(self.__ctx)

#-------------------------------------------------------------------------------
    def draw(self, ctx):
        rect = self.get_allocation()
        x = rect.x + rect.width / 2
        y = rect.y + rect.height / 2

        radius = min(rect.width / 2, rect.height / 2) - 5

        # clock back
        ctx.arc(x, y, radius, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()

        # clock ticks
        for i in xrange(12):
            ctx.save()

            if i % 3 == 0:
                inset = 0.2 * radius
            else:
                inset = 0.1 * radius
                ctx.set_line_width(0.5 * ctx.get_line_width())

            ctx.move_to(x + (radius - inset) * math.cos(i * math.pi / 6),
                            y + (radius - inset) * math.sin(i * math.pi / 6))
            ctx.line_to(x + radius * math.cos(i * math.pi / 6),
                            y + radius * math.sin(i * math.pi / 6))
            ctx.stroke()
            ctx.restore()

#-------------------------------------------------------------------------------
    def draw_layer(self, layer):
        if not isinstance(layer, Layer):
            raise TypeError, "Invalid layer type: " + `type(layer)`
        
        if layer.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        
        if layer.isVisible():
            color = self.__image.getOption('INACTIVE_LAYER_COLOR')
            if layer is self.__image.getActiveLayer():
                color = None
                
            _cobjs = []
            _objs = []
            _pts = []
            
            for _obj in layer.objsInRegion(self.__xmin, self.__ymin, self.__xmax, self.__ymax):
                if _obj.isVisible():
                    if isinstance(_obj, Point):
                        _pts.append(_obj)
                    elif isinstance(_obj, ConstructionObject):
                        _cobjs.append(_obj)
                    else:
                        _objs.append(_obj)
                        
            for _obj in _cobjs:
                _obj.draw(self, color)
            for _obj in _pts:
                _obj.draw(self, color)
            for _obj in _objs:
                _obj.draw(self, color)
    
    