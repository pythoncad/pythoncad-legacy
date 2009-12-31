#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo
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
# the GTK code for displaying a drawing
#

from __future__ import division

import sys
import math
import types
import warnings

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from PythonCAD.Interface.Gtk import gtkactions
from PythonCAD.Generic.image import Image
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.conobject import ConstructionObject
from PythonCAD.Generic.color import Color
from PythonCAD.Generic.layer import Layer
#from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import globals
from PythonCAD.Generic import keywords
from PythonCAD.Generic import prompt
from PythonCAD.Interface.Gtk import gtkdialog

from PythonCAD.Interface.Gtk import gtkshell

from PythonCAD.Interface.Menu.menubar import IMenuBar
from PythonCAD.Interface.Viewport.viewport import IViewport

# Tools
from PythonCAD.Generic.Tools import *

#
# Global variables
#

_debug = False ##  SDB debug stuff
globals.gtkcolors = {}
globals.gtklinetypes = {}



class GTKImage(object):
    """
        The GTK wrapping around an Image

        The GTKImage class is derived from the Image class, so it shares all
        the attributes and methods of that class. The GTKImage class has the
        following addtional methods:

        close(): Close a GTKImage.
        getWindow(): Get the GTK Window used in the GTKImage.
        getEntry(): Get the GTK Entry used in the GTKImage.
        getDA(): Get the GTK Drawing Area used in the GTKImage.
        {get/set}Pixmap(): Get/Set the GTK Pixmap used in the GTKImage.
        {get/set}Prompt(): Get/Set the prompt.
        {get/set}Tool(): Get/Set the tool used for working in the GTKImage.
        {get/set}UnitsPerPixel(): Get/Set this display parameter.
        {get/set}View(): Get/Set the current view seen in the GTKImage.
        getTolerance(): Get the current drawing tolerance.
        {get/set}GC(): Get/Set the graphic context used in the GTKImage.
        {get/set}Point(): Get/Set the current coordinates of the tool.
        {get/set}Size(): Get/Set the size of the drawing area.
        pixToCoordTransform(): Convert pixels to x/y coordinates.
        coordToPixTransform(): Convert x/y coordinates to pixels.
        refresh(): Redraw the screen using the current pixmap.
        redraw(): Recalculate the visible entities and redraw the screen.
        addGroup(): Add a new ActionGroup to the GTKImage.
        getGroup(): Retrieve an ActionGroup from the GTKImage.
        deleteGroup(): Remove an ActionGroup from the GTKImage.
    """
    
    #
    # class variables
    #
    
    from PythonCAD.Interface.Gtk import gtkmodify
    from PythonCAD.Interface.Gtk import gtkmirror
    from PythonCAD.Interface.Gtk import gtkprinting
    import  PythonCAD.Interface.Command as cmd
    __inittool = {
        tools.PasteTool : cmd.paste_mode_init,
        tools.SelectTool : cmd.select_mode_init,
        tools.DeselectTool : cmd.deselect_mode_init,
        tools.PointTool : cmd.point_mode_init,
        tools.SegmentTool : cmd.segment_mode_init,
        tools.RectangleTool: cmd.rectangle_mode_init,
        tools.CircleTool : cmd.circle_center_mode_init,
        tools.TwoPointCircleTool : cmd.circle_tp_mode_init,
        tools.ArcTool : cmd.arc_center_mode_init,
        tools.ChamferTool : cmd.chamfer_mode_init,
        tools.FilletTool: cmd.fillet_mode_init,
        tools.FilletTwoLineTool: cmd.fillet_two_line_mode_init,
        tools.HatchTool : cmd.hatch_mode_init,
        tools.LeaderTool : cmd.leader_mode_init,
        tools.PolylineTool : cmd.polyline_mode_init,
        tools.PolygonTool : cmd.polygon_mode_init,
        tools.HCLineTool : cmd.hcline_mode_init,
        tools.VCLineTool : cmd.vcline_mode_init,
        tools.ACLineTool : cmd.acline_mode_init,
        tools.CLineTool : cmd.cline_mode_init,
        tools.PerpendicularCLineTool: cmd.perpendicular_cline_mode_init,
        tools.TangentCLineTool : cmd.tangent_cline_mode_init,
        tools.CCircleTangentLineTool : cmd.two_circle_tangent_line_mode_init,
        tools.ParallelOffsetTool : cmd.parallel_offset_mode_init,
        tools.CCircleTool : cmd.ccircle_cpmode_init,
        tools.TwoPointCCircleTool : cmd.ccircle_tpmode_init,
        tools.TangentCCircleTool : cmd.tangent_ccircle_mode_init,
        tools.TwoPointTangentCCircleTool : cmd.two_cline_tancc_mode_init,
        tools.TextTool : cmd.text_add_init,
        tools.HorizontalMoveTool : gtkmodify.move_horizontal_init,
        tools.VerticalMoveTool : gtkmodify.move_vertical_init,
        tools.MoveTool : gtkmodify.move_twopoint_init,
        tools.HorizontalStretchTool : gtkmodify.stretch_horizontal_init,
        tools.VerticalStretchTool : gtkmodify.stretch_vertical_init,
        tools.StretchTool : gtkmodify.stretch_xy_init,
        tools.TransferTool : gtkmodify.transfer_object_init,
        tools.RotateTool : gtkmodify.rotate_init,
        tools.SplitTool : gtkmodify.split_object_init,
        tools.DeleteTool : gtkmodify.delete_mode_init,
        tools.MirrorTool : gtkmirror.mirror_mode_init,
        tools.ZoomTool : gtkmodify.zoom_init,
        tools.LinearDimensionTool : cmd.linear_mode_init,
        tools.HorizontalDimensionTool : cmd.horizontal_mode_init,
        tools.VerticalDimensionTool : cmd.vertical_mode_init,
        tools.RadialDimensionTool : cmd.radial_mode_init,
        tools.AngularDimensionTool : cmd.angular_mode_init,
        tools.PlotTool : gtkprinting.plot_mode_init,
        tools.ZoomPan : gtkmodify.zoomPan_init,
        }
   

    def __init__(self, image):
        debug_print("Initialized another GTKImage class instance...")
        if not isinstance(image, Image):
            raise TypeError, "Invalid Image type: " + `type(image)`
        self.__image = image
        self.__window = gtk.Window()
        self.__window.set_title(image.filename)
        self.__window.set_icon_from_file("gtkpycad.png")
        self.__window.connect("destroy", self.__destroyEvent)
        self.__window.connect("event", self.__windowEvent)
        self.__window.connect("key_press_event", self.__keyPressEvent)
        self.__window.connect("expose_event", self.__exposeWindowEvent)
        #
        # Zooming Moving global Variable Definition
        #
        self.__StartZooming= False
        self.__StartMoving = False
        self.StopMove=False
        self._activateSnap=False
        _width = min(1024, int(0.8 * float(gtk.gdk.screen_width())))
        _height = min(768, int(0.8 * float(gtk.gdk.screen_height())))
        self.__window.set_default_size(_width, _height)

        main_vbox = gtk.VBox(False, 2)
        main_vbox.set_border_width(2)
        self.__window.add(main_vbox)

        #
        # accelerators
        #

        self.__accel = gtk.AccelGroup()
        self.__window.add_accel_group(self.__accel)

        #
        # action group dictionary
        #

        self.__groups = {}

        #
        # menu bar
        #
        self.__menuBar = IMenuBar(self)
        main_vbox.pack_start(self.__menuBar.GtkMenuBar, False, False)

        #
        # drawing window has Horizontal Pane:
        # left side: stuff for layer display
        # right side: drawing area
        #

        pane = gtk.HPaned()
        main_vbox.pack_start(pane)

        frame1 = gtk.Frame()
        pane.pack1(frame1, True, False)
        pane.set_position(100)

        #
        # layer display stuff
        #

        _ld = gtkshell.LayerDisplay(self.__image, self.__window)
        frame1.add(_ld.getWindow())
        self.__layerdisplay = _ld

        #
        # drawing area
        #
        self.__disp_width = None
        self.__disp_height = None
        self.__units_per_pixel = 1.0

        self.__da = gtk.DrawingArea()

        black = gtk.gdk.color_parse('black')
        self.__da.modify_fg(gtk.STATE_NORMAL, black)
        self.__da.modify_bg(gtk.STATE_NORMAL, black)
        pane.pack2(self.__da, True, False)
        self.__da.set_flags(gtk.CAN_FOCUS)
        self.__da.connect("event", self.__daEvent)
        self.__da.connect("expose_event", self.__exposeEvent)
        self.__da.connect("realize", self.__realizeEvent)
        self.__da.connect("configure_event", self.__configureEvent)
        # self.__da.connect("focus_in_event", self.__focusInEvent)
        # self.__da.connect("focus_out_event", self.__focusOutEvent)

        self.__da.set_events(gtk.gdk.EXPOSURE_MASK |
                             gtk.gdk.LEAVE_NOTIFY_MASK |
                             gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.ENTER_NOTIFY_MASK|
                             gtk.gdk.LEAVE_NOTIFY_MASK|
                             gtk.gdk.KEY_PRESS_MASK |
                             gtk.gdk.KEY_RELEASE_MASK |
                             gtk.gdk.FOCUS_CHANGE_MASK |
                             gtk.gdk.POINTER_MOTION_MASK)

        lower_hbox = gtk.HBox(False, 2)
        main_vbox.pack_start(lower_hbox, False, False)

        self.__prompt = gtk.Label(_('Enter Command:'))
        lower_hbox.pack_start(self.__prompt, False, False)

        #
        # where the action is taking place
        #

        self.__coords = gtk.Label('(0,0)')
        lower_hbox.pack_end(self.__coords, False, False)

        self.__image.setCurrentPoint(0.0, 0.0)

        #
        # command entry area
        #

        self.__entry = gtk.Entry()
        main_vbox.pack_start(self.__entry, False, False)
        self.__entry.connect("activate", self.__entryEvent)

        #
        # the Pixmap, GraphicContext, and CairoContext for the drawing
        #

        self.__pixmap = None
        self.__gc = None
        self.__ctx = None
        self.__refresh = True

        #
        # the viewable region and tolerance in the drawing
        #

        self.__xmin = None
        self.__ymin = None
        self.__xmax = None
        self.__ymax = None
        self.__tolerance = 1e-10

        #
        # establish message connections
        #

        _image = self.__image
        _image.connect('selected_object', self.__selectedObject)
        _image.connect('deselected_object', self.__deselectedObject)
        _image.connect('option_changed', self.__optionChanged)
        _image.connect('current_point_changed', self.__currentPointChanged)
        _image.connect('active_layer_changed', self.__activeLayerChanged)
        _image.connect('added_child', self.__imageAddedChild)
        _image.connect('removed_child', self.__imageRemovedChild)
        _image.connect('group_action_started', self.__groupActionStarted)
        _image.connect('group_action_ended', self.__groupActionEnded)
        _image.connect('units_changed', self.__imageUnitsChanged)
        _image.connect('tool_changed', self.__imageToolChanged)

        _layers = [_image.getTopLayer()]
        while len(_layers):
            _layer = _layers.pop()
            _layer.connect('added_child', self.__layerAddedChild)
            _layer.connect('removed_child', self.__layerRemovedChild)
            for _child in _layer.getChildren():
                _child.connect('refresh', self.__refreshObject)
                _child.connect('change_pending', self.__objChangePending)
                _child.connect('change_complete', self.__objChangeComplete)
            _layers.extend(_layer.getSublayers())


    #------------------------------------------------------------------
    def close(self):
        """
            Release the entites stored in the drawing.
        """
        self.__layerdisplay.close()
        self.__layerdisplay = None
        _image = self.__image
        _image.close()
        _image.disconnect(self)
        _log = _image.getLog()
        if _log is not None:
            _log.detatch()
            _image.setLog(None)
        _image.finish()
        self.__window.destroy()
        self.__da = None
        self.__window = None
        self.__entry = None
        self.__accel = None
        self.__menuBar = None
        self.__pixmap = None
        self.__gc = None

    #------------------------------------------------------------------
    def quit(self):
        """
        quit the gtkimage
        """
        self.__destroyEvent(None)
        
    def __destroyEvent(self, widget, data=None):
        """
            Destroy event
        """
        if self.__image.isSaved()== False:
            # TODO ggr: fix this construction
            _image=self.getImage()
            if _image.isSaved() == False:
                _res=gtkdialog._yesno_dialog(self, "File Unsaved, Wold You Like To Save ?")
                if gtk.RESPONSE_ACCEPT == _res:
                    from PythonCAD.Interface.Menu import file_save_cb
                    file_save_cb(None, self)
        self.close()
        for _i in xrange(len(globals.imagelist)):
            _gimage = globals.imagelist[_i]
            if self.__image is _gimage:
                del globals.imagelist[_i]
                if not len(globals.imagelist):
                    gtk.main_quit()
                break
        return False
    
    #------------------------------------------------------------------
    def __keyPressEvent(self, widget, event, data=None):
        #print "__keyPressEvent()"
        _entry = self.__entry
        if _entry.is_focus():
            return False
        _tool = self.__image.getTool()
        if _tool is not None and _tool.hasHandler('entry_event'):
            _entry.grab_focus()            
            return _entry.event(event)
        return False

    #------------------------------------------------------------------
    def __windowEvent(self, widget, event, data=None):
        _type = event.type
        debug_print("__windowEvent: Event type: %d" % _type)
        if _type == gtk.gdk.BUTTON_PRESS:
            _button = event.button
            debug_print("BUTTON_PRESS: %d" % _button)
        elif _type == gtk.gdk.BUTTON_RELEASE:
            _button = event.button
            debug_print("BUTTON_RELEASE: %d" % _button)
        elif _type == gtk.gdk.KEY_PRESS:
            debug_print("KEY_PRESS")
            if event.keyval == gtk.keysyms.Escape:
                debug_print("Got escape key")
                self.reset()
                self._activateSnap=False
                return True
        elif _type == gtk.gdk.KEY_RELEASE:
            debug_print("KEY_RELEASE")
        else:
            pass
        return False


    #------------------------------------------------------------------
    def __entryEvent(self, widget, data=None):
        #
        # The error handling in this function needs work, and probably
        # a rethink as how the commands are implemented is in order. Perhaps
        # the command set should be stored in the image's global dictionary?
        #
        debug_print("__entryEvent()")
        _entry = self.__entry
        _text = _entry.get_text().strip()
        if len(_text):
            _text = _text.lower()
            if _text == 'end' or _text == 'stop':
                _entry.delete_text(0,-1)
                self.reset()
            else:
                _tool = self.__image.getTool()
                if _tool is not None and _tool.hasHandler("entry_event"):
                    _handler = _tool.getHandler("entry_event")
                    try:
                        _handler(self, widget, _tool)
                    except StandardError, e:
                        print "exception called: " + str(e)
                else:
                    _cmds = keywords.defaultglobals
                    _entry.delete_text(0,-1)
                    # print "text is '%s'" % _text
                    if _text in _cmds:
                        # print "valid command"
                        _opt = _cmds[_text]
                        # print "opt: '%s'" % _opt
                        _tooltype = prompt.lookup(_opt)
                        # print "cmd: '%s'" % _cmd
                        if _tooltype is not None:
                            self.__image.setTool(_tooltype())
                    else:
                        # print "Calling exec for '%s'" % _text
                        # print "Command Error; See http://www.pythoncad.org/commands.html for reference page."
                        try:
                            exec _text in self.__image.getImageVariables()
                        except:
                            print "error executing '%s' " % _text
        #
        # set the focus back to the DisplayArea widget
        #
        self.__da.grab_focus()

        return False

    #------------------------------------------------------------------
    def __exposeEvent(self, widget, event, data=None):
        #print "GtkImage.__exposeEvent()"
        _pixmap = self.__pixmap
        _x, _y, _w, _h = event.area
        _gc = widget.get_style().fg_gc[widget.state]
        widget.window.draw_drawable(_gc, _pixmap, _x, _y, _x, _y, _w, _h)
        return True

    #------------------------------------------------------------------
    def __exposeWindowEvent(self, widget, event, data=None):
        # do platform intergation
        self.__menuBar.DoPlatformIntegration()
        return False

    #------------------------------------------------------------------
    def __realizeEvent(self, widget, data=None):
        _win = widget.window
        _width, _height = _win.get_size()
        self.setSize(_width, _height)
        widget.set_size_request(100,100)
        _gc = _win.new_gc()
        _gc.set_exposures(True)
        self.setGC(_gc)

    #------------------------------------------------------------------
    def __configureEvent(self, widget, event, data=None):
        _win = widget.window
        _width, _height = _win.get_size()
        _disp_width, _disp_height = self.getSize()
        if _disp_width != _width or _disp_height != _height:
            self.setSize(_width, _height)
            _pixmap = gtk.gdk.Pixmap(_win, _width, _height)
            _gc = widget.get_style().fg_gc[widget.state]
            _pixmap.draw_rectangle(_gc, True, 0, 0, _width, _height)
            self.setPixmap(_pixmap)
            if hasattr(_pixmap, 'cairo_create'):
                self.__ctx = _pixmap.cairo_create()
            _xmin = self.__xmin
            _ymin = self.__ymin
            if _xmin is None or _ymin is None:
                _xmin = 1.0
                _ymin = 1.0
            _upp = self.__units_per_pixel
            self.setView(_xmin, _ymin, _upp)
        return True
    
    #------------------------------------------------------------------
    def __daEvent(self, widget, event, data=None):
        _rv = False
        _type = event.type
        debug_print("__daEvent(): Event type: %d" % _type)
        _tool = self.__image.getTool()
        if _type==31:
            debug_print("if 31")
            if event.direction == gtk.gdk.SCROLL_UP: 
                debug_print("BUTTON_PRESSS CROLL_UP")
                self.ZoomIn()
            if event.direction == gtk.gdk.SCROLL_DOWN: 
                debug_print("BUTTON_PRESSS SCROLL_DOWN")
                self.ZoomOut()
        if _type == 12:
            debug_print("if 12")
        if _type == gtk.gdk.BUTTON_PRESS:
            debug_print("gtk.gdk.BUTTON_PRESS")
            self.setToolpoint(event)
            _button = event.button
            if _button == 1:
                if _tool is not None and _tool.hasHandler("button_press"):
                    _rv = _tool.getHandler("button_press")(self, widget,
                                                           event, _tool)
            if _button == 3:
                if _tool is not None and _tool.hasHandler("right_button_press"):                 
                    _rv = _tool.getHandler("right_button_press")(self, widget,
                                                           event, _tool)
            
            debug_print("__Move BUTTON_PRESS")
            self.__Move(widget, event)
        elif _type == gtk.gdk.BUTTON_RELEASE:
            debug_print("gtk.gdk.BUTTON_RELEASE")
            self.setToolpoint(event)
            _button = event.button
            if _button == 1:
                if _tool is not None and _tool.hasHandler("button_release"):
                    _rv =_tool.getHandler("button_release")(self, widget,
                                                            event, _tool)
            debug_print("__Move BUTTON_RELEASE")
            self.__Move(widget, event)
        elif _type == gtk.gdk.MOTION_NOTIFY:
            debug_print("gtk.gdk.MOTION_NOTIFY")
            self.setToolpoint(event)
            if _tool is not None and _tool.hasHandler("motion_notify"):
                _rv = _tool.getHandler('motion_notify')(self, widget,
                                                        event, _tool)
            debug_print("__Move MOTION_NOTIFY")
            self.__MakeMove(widget,event)
            self.__ActiveSnapEvent(widget,event)
        elif _type == gtk.gdk.KEY_PRESS:
            debug_print("In __daEvent(), got key press!")
            _key = event.keyval
            if (_key == gtk.keysyms.Page_Up or
                _key == gtk.keysyms.Page_Down or
                _key == gtk.keysyms.Left or
                _key == gtk.keysyms.Right or
                _key == gtk.keysyms.Up or
                _key == gtk.keysyms.Down):
                debug_print("Got Arrow/PageUp/PageDown key")
                #KeyMoveDrawing(_key) # Matteo Boscolo 12-05-2009
                pass # handle moving the drawing in some fashion ...
            elif _key == gtk.keysyms.Escape:
                debug_print("Got escape key")
                self.reset()
                _rv = True
            elif _tool is not None and _tool.hasHandler("key_press"):
                debug_print("gtk.gdk.MOTION_NOTIFY")
                _rv = _tool.getHandler("key_press")(self, widget,
                                                    event, _tool)
            else:
                debug_print("ELSE")
                _entry = self.__entry
                _entry.grab_focus()
                if _key == gtk.keysyms.Tab:
                    _rv = True
                else:
                    _rv = _entry.event(event)
        elif _type == gtk.gdk.ENTER_NOTIFY:
            debug_print("gtk.gdk.ENTER_NOTIFY")
            self.setToolpoint(event)
            _rv = True
        elif _type == gtk.gdk.LEAVE_NOTIFY:
            debug_print("gtk.gdk.LEAVE_NOTIFY")
            self.setToolpoint(event)
            _rv = True
        else:
            debug_print("Got type %d" % _type)
            pass
        return _rv
    
    def KeyMoveDrawing(self,key):
        """Make A Move when the user press arrows keys"""
        self.__MovmentStep=10 #This mast be a global settings that the user can change
        actualStep=self.__MovmentStep
        actualX=self.__activeX
        actualY=self.__activeY
        newX=actualX
        newY=actualY
        if (key == gtk.keysyms.Page_Up):
            print("ZoomUp")
        if (key == gtk.keysyms.Page_Down):
            print("ZoomDown")
        if (key == gtk.keysyms.Left):
            newX=actualX-actualStep
            newY=actualY
        if (key == gtk.keysyms.Right):
            newX=actualX+actualStep
            newY=actualY
        if (key == gtk.keysyms.Up):
            newX=actualX
            newY=actualY+actualStep
        if (key == gtk.keysyms.Down):
            newX=actualX
            newY=actualY-actualStep
        self.MoveFromTo(actualX,actualY,newX,newY)
    #------------------------------------------------------------------
    def __focusInEvent(self, widget, event, data=None):
        debug_print("in GTKImage::__focusInEvent()")
        return False

    #------------------------------------------------------------------
    def __focusOutEvent(self, widget, event, data=None):
        debug_print("in GTKImage::__focusOutEvent()")
        return False

    #------------------------------------------------------------------
    def __selectedObject(self, img, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        if _debug:
            print "Selected object: " + `_obj`
        _parent = _obj.getParent()
        if _parent.isVisible() and _obj.isVisible():
            _color = Color('#ff7733') # FIXME color should be adjustable
            _obj.draw(self, _color)
            self.__refresh = True

    #------------------------------------------------------------------
    def __deselectedObject(self, img, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        if _debug:
            print "Deselected object: " + `_obj`
        _parent = _obj.getParent()
        if _parent.isVisible() and _obj.isVisible():
            _obj.draw(self)
            self.__refresh = True

    #------------------------------------------------------------------
    def __optionChanged(self, img, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _opt = args[0]
        if _debug:
            print "Option changed: '%s'" % _opt
        if _opt == 'BACKGROUND_COLOR':
            _bc = self.__image.getOption('BACKGROUND_COLOR')
            _col = gtk.gdk.color_parse(str(_bc))
            self.__da.modify_fg(gtk.STATE_NORMAL, _col)
            self.__da.modify_bg(gtk.STATE_NORMAL, _col)
            self.redraw()

        elif (_opt == 'HIGHLIGHT_POINTS' or
              _opt == 'INACTIVE_LAYER_COLOR' or
              _opt == 'SINGLE_POINT_COLOR' or
              _opt == 'MULTI_POINT_COLOR'):
            self.redraw()
        else:
            pass

    #------------------------------------------------------------------
    def __currentPointChanged(self, img, *args):
        _x, _y = self.__image.getCurrentPoint()
        self.__coords.set_text("%.4f, %.4f" % (_x, _y))


    #------------------------------------------------------------------
    def __activeLayerChanged(self, img, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _prev_layer = args[0]
        self.drawLayer(_prev_layer)
        _active_layer = self.__image.getActiveLayer()
        self.drawLayer(_active_layer)
        self.refresh()

    #
    def getImage(self):
        """Return the Image being displayed.

getImage()        
        """
        return self.__image

    image = property(getImage, None, None, "Displayed Image")
    
    #------------------------------------------------------------------
    def getAccel(self):
        """Return the gtk.AccelGroup in the GTKImage.

getAccel()
        """
        return self.__accel

    accel = property(getAccel, None, None, "Accel group in the GTKImage.")

    #------------------------------------------------------------------
    def getWindow(self):
        """Return a handle to the gtk.Window in the GTKImage.

getWindow()
        """
        return self.__window

    window = property(getWindow, None, None, "Main GTK Window for a GTKImage.")

    #------------------------------------------------------------------
    def getEntry(self):
        """Return a handle to the gtk.Entry in the GTKImage.

getEntry()
        """
        return self.__entry

    entry = property(getEntry, None, None, "Entry box for a GTKImage.")

    #------------------------------------------------------------------
    def getDA(self):
        """Return the gtk.DrawingArea in the GTKImage.

getDA()
        """
        return self.__da

    da = property(getDA, None, None, "DrawingArea for a GTKImage.")

    #------------------------------------------------------------------
    def getPixmap(self):
        """Return the Pixmap for the GTKImage.

getPixmap()
        """
        return self.__pixmap

    #------------------------------------------------------------------
    def setPixmap(self, pixmap):
        """Set the Pixmap for the GTKImage.

setPixmap(pixmap)
        """
        self.__pixmap = pixmap

    pixmap = property(getPixmap, setPixmap, None, "Pixmap for a GTKImage.")

    #------------------------------------------------------------------
    def getPrompt(self):
        """Return the current prompt string.

getPrompt()
        """
        return self.__prompt.get_label()

    #------------------------------------------------------------------
    def setPrompt(self, p):
        """Set the current prompt string.

setPrompt(p)
        """
        if not isinstance(p, types.StringTypes):
            raise TypeError, "Invalid prompt type: " + `type(p)`
        self.__prompt.set_text(p)

    prompt = property(getPrompt, setPrompt, None, "Prompt string.")

#---------------------------------------------------------------------------------------------------
    def setTool(self, tool):
        """Replace the tool in the image with a new Tool.

setTool(tool)

The argument 'tool' should be an instance of a Tool object.
        """
        warnings.warn("Method setTool() is deprecated - use getImage().setTool()", stacklevel=2)
        self.__image.setTool(tool)

#---------------------------------------------------------------------------------------------------
    def getTool(self):
        """Return the current Tool used in the drawing.

getTool()
        """
        warnings.warn("Method getTool() is deprecated - use getImage().getTool()", stacklevel=2)
        return self.__image.getTool()

    tool = property(getTool, None, None, "Tool for adding/modifying entities.")

#---------------------------------------------------------------------------------------------------
    def getUnitsPerPixel(self):
        """Return the current value of units/pixel.

getUnitsPerPixel()
        """
        return self.__units_per_pixel

#---------------------------------------------------------------------------------------------------
    def setUnitsPerPixel(self, upp):
        """Set the current value of units/pixel.

setUnitsPerPixel(upp)

The argument 'upp' should be a positive float value.
        """
        _upp = upp
        if not isinstance(_upp, float):
            _upp = float(upp)
        if _upp < 1e-10:
            raise ValueError, "Invalid scale value: %g" % _upp
        self.__units_per_pixel = _upp
        self.__tolerance = _upp * 5.0

#---------------------------------------------------------------------------------------------------
    def setView(self, xmin, ymin, scale=None):
        """Set the current visible area in a drawing.

setView(xmin, ymin[, scale])

xmin: Minimum visible x-coordinate
ymin: Minimum visible y-coordinate

The optional argument 'scale' defaults to the current
value of units/pixel (set with getUnitsPerPixel() method.)
This value must be a positive float.
        """
        _xmin = xmin
        if not isinstance(_xmin, float):
            _xmin = float(xmin)
        _ymin = ymin
        if not isinstance(_ymin, float):
            _ymin = float(ymin)
        _scale = scale
        if _scale is None:
            _scale = self.__units_per_pixel
        if not isinstance(_scale, float):
            _scale = float(scale)
        if _scale < 1e-10:
            raise ValueError, "Invalid scale value: %g" % _scale
        _xmax = _xmin + (_scale * self.__disp_width)
        _ymax = _ymin + (_scale * self.__disp_height)
        _recalc = False
        if abs(_scale - self.__units_per_pixel) > 1e-10:
            self.__units_per_pixel = _scale
            _recalc = True
        self.__tolerance = self.__units_per_pixel * 5.0
        self.__xmin = _xmin
        self.__ymin = _ymin
        self.__xmax = _xmax
        self.__ymax = _ymax
        if _recalc:
            self.calcTextWidths()
        self.redraw()

#---------------------------------------------------------------------------------------------------
    def calcTextWidths(self):
        """
            Calculate the width of the text strings in the Image.
        """
        import  PythonCAD.Interface.Command as cmd
        _layers = [self.__image.getTopLayer()]
        while len(_layers):
            _layer = _layers.pop()
            for _tblock in _layer.getLayerEntities('text'):
                cmd.set_textblock_bounds(self, _tblock)
            for _dim in _layer.getLayerEntities('linear_dimension'):
                _ds1, _ds2 = _dim.getDimstrings()
                cmd.set_textblock_bounds(self, _ds1)
                if _dim.getDualDimMode():
                    cmd.set_textblock_bounds(self, _ds2)
            for _dim in _layer.getLayerEntities('horizontal_dimension'):
                _ds1, _ds2 = _dim.getDimstrings()
                cmd.set_textblock_bounds(self, _ds1)
                if _dim.getDualDimMode():
                    cmd.set_textblock_bounds(self, _ds2)
            for _dim in _layer.getLayerEntities('vertical_dimension'):
                _ds1, _ds2 = _dim.getDimstrings()
                cmd.set_textblock_bounds(self, _ds1)
                if _dim.getDualDimMode():
                    cmd.set_textblock_bounds(self, _ds2)
            for _dim in _layer.getLayerEntities('radial_dimension'):
                _ds1, _ds2 = _dim.getDimstrings()
                cmd.set_textblock_bounds(self, _ds1)
                if _dim.getDualDimMode():
                    cmd.set_textblock_bounds(self, _ds2)
            for _dim in _layer.getLayerEntities('angular_dimension'):
                _ds1, _ds2 = _dim.getDimstrings()
                cmd.set_textblock_bounds(self, _ds1)
                if _dim.getDualDimMode():
                    cmd.set_textblock_bounds(self, _ds2)
            _layers.extend(_layer.getSublayers())
        
#---------------------------------------------------------------------------------------------------
    def getView(self):
        """Return the current visible area in a drawing.

getView()

This method returns a tuple with four float values:

(xmin, ymin, xmax, ymax)

If the view has never been set, each of these values
will be None.
        """
        return (self.__xmin, self.__ymin, self.__xmax, self.__ymax)

    view = property(getView, setView, None, "The visible area in a drawing.")

#---------------------------------------------------------------------------------------------------
    def getTolerance(self):
        """Return the current drawing tolerance.

getTolerance()
        """
        return self.__tolerance

    tolerance = property(getTolerance, None, None, "Drawing tolerance.")

#---------------------------------------------------------------------------------------------------
    def getGC(self):
        """Return the GraphicContext allocated for the GTKImage.

getGC()
        """
        return self.__gc

#---------------------------------------------------------------------------------------------------
    def setGC(self, gc):
        """Set the GraphicContext for the GTKImage.

setGC(gc)
        """
        if not isinstance(gc, gtk.gdk.GC):
            raise TypeError, "Invalid GC object: " + `gc`
        if self.__gc is None:
            self.__gc = gc

    gc = property(getGC, None, None, "GraphicContext for the GTKImage.")

#---------------------------------------------------------------------------------------------------
    def getCairoContext(self):
        """Return the CairoContext allocated for the GTKImage.

getCairoContext()
        """
        return self.__ctx

    ctx = property(getCairoContext, None, None, "CairoContext for the GTKImage.")

#---------------------------------------------------------------------------------------------------
    def getSize(self):
        """Return the size of the DrawingArea window.

getSize()
        """
        return (self.__disp_width, self.__disp_height)

#---------------------------------------------------------------------------------------------------
    def setSize(self, width, height):
        """Set the size of the DrawingArea window.

setSize(width, height)
        """
        _width = width
        if not isinstance(_width, int):
            _width = int(width)
        if _width < 0:
            raise ValueError, "Invalid drawing area width: %d" % _width
        _height = height
        if not isinstance(_height, int):
            _height = int(height)
        if _height < 0:
            raise ValueError, "Invalid drawing area height: %d" % _height
        self.__disp_width = _width
        self.__disp_height = _height
       
#---------------------------------------------------------------------------------------------------
    def setToolpoint(self, event):
        _x = event.x
        _y = event.y
        _tx, _ty = self.pixToCoordTransform(_x, _y)
        self.__image.setCurrentPoint(_tx, _ty)

#---------------------------------------------------------------------------------------------------
    def addGroup(self, group):
        """Add an ActionGroup to the GTKImage.

addGroup(group)

Argument 'group' must be either an instance of either
gtk.Action gtk.stdAction.
        """
        if not isinstance(group, gtk.ActionGroup):
            if not isinstance(gtkactions.stdActionGroup):
                raise TypeError, "Invalid group type: " + `type(group)`
        self.__groups[group.get_name()] = group

#---------------------------------------------------------------------------------------------------
    def getGroup(self, name):
        """Return an ActionGroup stored in the GTKImage.

getGroup(name)

Argument 'name' should be the name of the ActionGroup. This method
will return None if no group by that name is stored.
        """
        return self.__groups.get(name)

#---------------------------------------------------------------------------------------------------
    def deleteGroup(self, name):
        """Remove an ActionGroup stored in the GTKImage.

deleteGroup(name)

Argument 'name' should be the name of the ActionGroup to be removed.
        """
        if name in self.__groups:
            del self.__groups[name]

#---------------------------------------------------------------------------------------------------
    def pixToCoordTransform(self, xp, yp):
        """Convert from pixel coordinates to x-y coordinates.

pixToCoordTransform(xp, yp)

The function arguments are:

xp: pixel x value
yp: pixel y value

The function returns a tuple holding two float values
        """
        _upp = self.__units_per_pixel
        _xc = self.__xmin + (xp * _upp)
        _yc = self.__ymax - (yp * _upp)
        return (_xc, _yc)
            
#---------------------------------------------------------------------------------------------------
    def coordToPixTransform(self, xc, yc):
        """Convert from x-y coordinates to pixel coordinates

coordToPixTransform(xc, yc)

The function arguments are:

xc: x coordinate
yp: y coordinate

The function returns a tuple holding two integer values
        """
        _upp = self.__units_per_pixel
        _xp = int((xc - self.__xmin)/_upp)
        _yp = int((self.__ymax - yc)/_upp)
        return _xp, _yp

#---------------------------------------------------------------------------------------------------
    def getColor(self, c):
        """Return an allocated color for a given Color object.

getColor(c)

Argument 'c' must be a Color object. This method will return an
allocated color.
        """
        if not isinstance(c, Color):
            raise TypeError, "Invalid Color object: " + `type(c)`
        _color = globals.gtkcolors.get(c)
        if _color is None:
            # _r = int(round(65535.0 * (c.r/255.0)))
            # _g = int(round(65535.0 * (c.g/255.0)))
            # _b = int(round(65535.0 * (c.b/255.0)))
            # _color = self.__da.get_colormap().alloc_color(_r, _g, _b)
            _color = self.__da.get_colormap().alloc_color(str(c))
                
            globals.gtkcolors[c] = _color
        return _color

#---------------------------------------------------------------------------------------------------
    def fitImage(self):
        """Redraw the image so all entities are visible in the window.

fitImage()
        """
        _fw = float(self.__disp_width)
        _fh = float(self.__disp_height)
        _xmin, _ymin, _xmax, _ymax = self.__image.getExtents()
        _xdiff = abs(_xmax - _xmin)
        _ydiff = abs(_ymax - _ymin)
        _xmid = (_xmin + _xmax)/2.0
        _ymid = (_ymin + _ymax)/2.0
        _xs = _xdiff/_fw
        _ys = _ydiff/_fh
        if _xs > _ys:
            _scale = _xs * 1.05 # make it a little larger
        else:
            _scale = _ys * 1.05 # make it a little larger
        _xm = _xmid - (_fw/2.0) * _scale
        _ym = _ymid - (_fh/2.0) * _scale
        self.setView(_xm, _ym, _scale)

#---------------------------------------------------------------------------------------------------
    def refresh(self):
        """
            This method does a screen refresh.
            If entities in the drawing have been added, removed, or
            modified, use the redraw() method.
        """
        _da = self.__da
        if (_da.flags() & gtk.MAPPED):
            # print "refreshing ..."
            _gc = _da.get_style().fg_gc[gtk.STATE_NORMAL]
            _gc.set_function(gtk.gdk.COPY)
            _da.queue_draw()

 #---------------------------------------------------------------------------------------------------
    def redraw(self):
        #print "GtkImage.redraw"
        """
            This method draws all the objects visible in the window.
        """
        _da = self.__da
        if (_da.flags() & gtk.MAPPED):
            if _debug:
                print "Redrawing image"
            _xmin = self.__xmin
            _ymin = self.__ymin
            _xmax = self.__xmax
            _ymax = self.__ymax
            _gc = _da.get_style().fg_gc[gtk.STATE_NORMAL]
            self.__pixmap.draw_rectangle(_gc, True, 0, 0,
                                         self.__disp_width, self.__disp_height)
            _active_layer = self.__image.getActiveLayer()
            _layers = [self.__image.getTopLayer()]
            while (len(_layers)):
                _layer = _layers.pop()
                if _layer is not _active_layer:
                    self.drawLayer(_layer)
                _layers.extend(_layer.getSublayers())
            self.drawLayer(_active_layer)
            #
            # redraw selected entities
            #
            _color = Color('#ff7733')
            for _obj in self.__image.getSelectedObjects(False):
                _obj.draw(self, _color)
            self.refresh()

 #---------------------------------------------------------------------------------------------------
    def drawLayer(self, l):
        if not isinstance(l, Layer):
            raise TypeError, "Invalid layer type: " + `type(l)`
        if l.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        if l.isVisible():
            _col = self.__image.getOption('INACTIVE_LAYER_COLOR')
            if l is self.__image.getActiveLayer():
                _col = None
            _cobjs = []
            _objs = []
            _pts = []
            for _obj in l.objsInRegion(self.__xmin, self.__ymin, self.__xmax, self.__ymax):
                if _obj.isVisible():
                    if isinstance(_obj, Point):
                        _pts.append(_obj)
                    elif isinstance(_obj, ConstructionObject):
                        _cobjs.append(_obj)
                    else:
                        _objs.append(_obj)
            for _obj in _cobjs:
                _obj.draw(self, _col)
            for _obj in _pts:
                _obj.draw(self, _col)
            for _obj in _objs:
                _obj.draw(self, _col)

#---------------------------------------------------------------------------------------------------
    def ZoomIn(self,scaleFactor=None):
        _xmin, _ymin, _xmax, _ymax = self.getView()
        if(scaleFactor==None):
            _scale = self.getUnitsPerPixel()
        else:
            _scale=scaleFactor
        _xdiff = abs(_xmax - _xmin)
        _ydiff = abs(_ymax - _ymin)
        _xmin = (_xmin + _xmax)/2.0 - _xdiff/4.0
        _ymin = (_ymin + _ymax)/2.0 - _ydiff/4.0
        self.setView(_xmin, _ymin, (_scale/2))

#---------------------------------------------------------------------------------------------------
    def ZoomOut(self,scaleFactor=None):
        _xmin, _ymin, _xmax, _ymax = self.getView()
        if(scaleFactor==None):
            _scale = self.getUnitsPerPixel()
        else:
            _scale=scaleFactor
        _xdiff = abs(_xmax - _xmin)
        _ydiff = abs(_ymax - _ymin)
        _xmin = (_xmin + _xmax)/2.0 - _xdiff
        _ymin = (_ymin + _ymax)/2.0 - _ydiff
        self.setView(_xmin, _ymin, (_scale * 2))

#---------------------------------------------------------------------------------------------------
    def reset(self):
        """
            Set the image to an initial drawing state.
        """
        _tool = self.__image.getTool()
        if _tool is None:
            #
            # If _tool is None, deselect any selected objects in view.
            # This way, if you are currently using a tool, then the
            # first time you hit escape, you just clear the tool.
            # The second time clears all selections.
            debug_print("Entered reset")
            if _tool is None:
                debug_print(".....This is second time to be in reset")
                self.__image.clearSelectedObjects()
        self.__image.setTool()
        self.redraw()
        self.setPrompt(_('Enter command'))
    #
    # Entity drawing operations
    #
#---------------------------------------------------------------------------------------------------
    def __drawObject(self, obj, col=None):
        # print "__drawObject()"
        _col = col
        if self.__xmin is None:
            return
        _xmin, _ymin, _xmax, _ymax = self.getView()
        if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
            _image = self.__image
            if _col is None:
                if obj.getParent() is not _image.getActiveLayer():
                    _col = _image.getOption('INACTIVE_LAYER_COLOR')
            obj.draw(self, _col)
            self.__refresh = True

#---------------------------------------------------------------------------------------------------
    def __eraseObject(self, obj):
        # print "__eraseObject()"
        _xmin, _ymin, _xmax, _ymax = self.getView()
        if self.__xmin is None:
            return
        if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
            obj.erase(self)
            self.__refresh = True
        
#---------------------------------------------------------------------------------------------------
    def __imageAddedChild(self, obj, *args):
        # print "__imageAddedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _layer = args[0]
        if not isinstance(_layer, Layer):
            raise TypeError, "Unexpected child type: " + `type(_layer)`
        _layer.connect('added_child', self.__layerAddedChild)
        _layer.connect('removed_child', self.__layerRemovedChild)

#---------------------------------------------------------------------------------------------------
    def __layerAddedChild(self, obj, *args):
        # print "__layerAddedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _child = args[0] # need some verification test here ...
        _child.connect('refresh', self.__refreshObject)
        _child.connect('change_pending', self.__objChangePending)
        _child.connect('change_complete', self.__objChangeComplete)
        if _child.isVisible() and obj.isVisible():
            self.__drawObject(_child)

#---------------------------------------------------------------------------------------------------
    def __imageRemovedChild(self, obj, *args):
        # print "__imageRemovedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _layer = args[0]
        if not isinstance(_layer, Layer):
            raise TypeError, "Unexpected child type: " + `type(_layer)`
        _layer.disconnect(self)

#---------------------------------------------------------------------------------------------------
    def __layerRemovedChild(self, obj, *args):
        # print "__layerRemovedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _child = args[0] # need some verification test here ...
        if _child.isVisible() and obj.isVisible():
            self.__eraseObject(_child)
        _child.disconnect(self)

#---------------------------------------------------------------------------------------------------
    def __groupActionStarted(self, obj, *args):
        # print "__groupActionStarted()"
        self.__refresh = False

#---------------------------------------------------------------------------------------------------
    def __groupActionEnded(self, obj, *args):
        # print "__groupActionEnded()"
        if self.__refresh:
            self.refresh()
        else:
            self.__refresh = True

#---------------------------------------------------------------------------------------------------
    def __imageUnitsChanged(self, obj, *args):
        # print "__imageUnitsChanged()"
        self.redraw()

#---------------------------------------------------------------------------------------------------
    def __imageToolChanged(self, obj, *args):
        _tool = self.__image.getTool()
        if _tool is not None:
            _init = GTKImage.__inittool.get(type(_tool))
            if _init is not None:
                _init(self)
        
#---------------------------------------------------------------------------------------------------
    def __objChangePending(self, obj, *args):
        # print "__objChangePending()" + `obj`
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _change = args[0]
        if (obj.isVisible() and
            obj.getParent().isVisible() and
            _change != 'added_user' and
            _change != 'removed_user'):
            self.__eraseObject(obj)

#---------------------------------------------------------------------------------------------------
    def __objChangeComplete(self, obj, *args):
        # print "__objChangeComplete()" + `obj`
        if obj.isVisible() and obj.getParent().isVisible():
            self.__drawObject(obj)
            
#---------------------------------------------------------------------------------------------------
    def __refreshObject(self, obj, *args):
        # print "__refreshObject()"
        _col = None
        if not obj.isVisible() or not obj.getParent().isVisible():
            _col = self.__image.getOption('BACKGROUND_COLOR')
        self.__drawObject(obj, _col)


    #++ Matteo Boscolo
#---------------------------------------------------------------------------------------------------
    def __Move(self, widget, event):
        """
            set the Global Variable for controlling the zoom and  moving
            of the drawing
        """
        if(self.StopMove):
            return
        _type = event.type
        _button = event.button
        if(_button==3):
            if(_type==4):
                self.__activeX=event.x
                self.__activeY=event.y
                self.__StartMoving = True
            if(_type==7):
                self.__StartMoving = False
        if(_button==2):
            if(_type==4):
                self.__StartZooming = True
            if(_type==7):
                self.__StartZooming= False
                
#---------------------------------------------------------------------------------------------------
    def __MakeMove(self, widget, event):
        if(self.__StartZooming):
            ActiveScale = self.getUnitsPerPixel()
            midX=abs(self.__xmin-self.__xmax)/2
            midY=abs(self.__ymin-self.__ymax)/2            
            if(self.__activeY>event.y):
                ActiveScale=ActiveScale*1.05
                #self.setView(midX,midY,ActiveScale)
                self.ZoomScale(ActiveScale)
            elif(self.__activeY<event.y):
                ActiveScale=ActiveScale*0.95               
                #self.setView(midX,midY,ActiveScale)
                self.ZoomScale(ActiveScale)
        if(self.__StartMoving):
            self.MoveFromTo(self.__activeX,self.__activeY,event.x,event.y)
        self.__activeX=event.x
        self.__activeY=event.y

#---------------------------------------------------------------------------------------------------
    def ZoomInEx(self):
        self.__da.zoom_in()

#---------------------------------------------------------------------------------------------------
    def ZoomOutEx(self):
        self.__da.zoom_out()
        
#---------------------------------------------------------------------------------------------------
    def ZoomIn(self):
        ActiveScale = self.getUnitsPerPixel()
        ActiveScale=ActiveScale*1.05
        self.ZoomScale(ActiveScale)

#---------------------------------------------------------------------------------------------------
    def ZoomOut(self):
        ActiveScale = self.getUnitsPerPixel()
        ActiveScale=ActiveScale*0.95 
        self.ZoomScale(ActiveScale)

#---------------------------------------------------------------------------------------------------
    def MoveFromTo(self,xFrom,yFrom,xTo,yTo):
        """
            Do the Zoom or Move action  
        """
        deltaX=abs(xFrom-xTo)*self.__units_per_pixel
        deltaY=abs(yFrom-yTo)*self.__units_per_pixel
        if(xFrom>xTo):
            self.__xmin=self.__xmin+deltaX
            self.__xmax=self.__xmax+deltaX
        else:
            self.__xmin=self.__xmin-deltaX
            self.__xmax=self.__xmax-deltaX
        if(yFrom>yTo):
            self.__ymin=self.__ymin-deltaY
            self.__ymax=self.__ymax-deltaY
        else:
            self.__ymin=self.__ymin+deltaY
            self.__ymax=self.__ymax+deltaY                   
        self.redraw()

#---------------------------------------------------------------------------------------------------
    def ZoomScale(self,scale):
        """
            Make a drawing zoom of the scale quantity
        """
        _fw = float(self.__disp_width)
        _fh = float(self.__disp_height)
        _xdiff = abs(self.__xmax-self.__xmin)
        _ydiff = abs(self.__ymax-self.__ymin)
        _xmid = (self.__xmin + self.__xmax)/2.0
        _ymid = (self.__ymin + self.__ymax)/2.0
        _xm = _xmid - (_fw/2.0) * scale
        _ym = _ymid - (_fh/2.0) * scale
        self.setView(_xm, _ym, scale)

#---------------------------------------------------------------------------------------------------
    def StartPanImage(self):
        """
            Start Pan Image
        """
        self.StopMove=True
        self.__StartMoving=True

#---------------------------------------------------------------------------------------------------
    def StopPanImage(self):
        """
            Stop Pan Operation
        """
        self.StopMove=False
        self.__StartMoving=False

#---------------------------------------------------------------------------------------------------
    def isPan(self):
        """ 
            Return the active pan status
        """
        return self.StopMove
    
#---------------------------------------------------------------------------------------------------
    def setCursor(self,drwArea,snObject):
        """
            active Snap cursor shape
        """
        _win=drwArea.get_parent_window()
        if snObject is None or snObject.entity is None: 
            _snapCursor=gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)            
        else:
            _snapCursor=snObject.cursor
        _win.set_cursor(_snapCursor)

#---------------------------------------------------------------------------------------------------
    def __ActiveSnapEvent(self,drwArea,event):
        """
            Snap Event
        """
        cursor=None
        if(self._activateSnap):
            _sobj=self.__image.snapProvider.getSnap(self.__tolerance,globals.snapOption) 
            self.setCursor(drwArea,_sobj)
        else:
            self.setCursor(drwArea,None)
        
#---------------------------------------------------------------------------------------------------
    def activateSnap(self):
        """
            Activate the snap functionality
        """
        self._activateSnap=True


#-- Matteo Boscolo
#------------------------------------------------------------------
def debug_print(string):
    if _debug is True:
        print "SDB Debug: " + string

