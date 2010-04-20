#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# the GTK code for displaying a drawing
#

import types

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from PythonCAD.Generic import image
from PythonCAD.Generic import layer
from PythonCAD.Generic import util

_debug = False

class LayerDisplay(object):
    def __init__(self, im, win):
        """
        This class defines the layer display graphic on the left side of
        the window.  The calling arg should be a member of the image class.
        """
        if _debug is True:
            print "SDB debug: instantiated another LayerDisplay class instance"
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        if not isinstance(win, gtk.Window):
            raise TypeError, "Invalid Window type: " + `type(win)`
        _sw = gtk.ScrolledWindow()
        _sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        _model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        # _model.connect("rows-reordered", self.__reordered)
        _iter = _model.append(None)
        _layer = im.getTopLayer()
        _layer.connect('visibility_changed', self.__layerVisibilityChanged)
        _layer.connect('name_changed', self.__layerNameChanged)
        _model.set(_iter, 0, _layer.getName())
        _model.set(_iter, 1, _layer)
        _tv = gtk.TreeView(_model)
        _tv.set_reorderable(True) # drag-and-drop
        _tv.set_search_column(0)
        _tv.connect("button_press_event", self.__treeViewButtonPress)
        _select = _tv.get_selection()
        _select.set_mode(gtk.SELECTION_SINGLE)
        _select.connect("changed", self.__selectionChanged)

        _renderer = gtk.CellRendererText()
        # _renderer.set_property("editable", True)
        _renderer.connect("edited", self.__cellEdited)

        _column = gtk.TreeViewColumn(_('Layers'), _renderer, text=0)
        _tv.append_column(_column)
        _sw.add(_tv)
        self.__image = im
        self.__window = win
        self.__sw = _sw
        self.__model = _model
        self.__treeview = _tv
        self.__layer = None

        #
        # establish messages connections
        #

        im.connect('active_layer_changed', self.__activeLayerChanged)
        im.connect('added_child', self.__imageAddedChild)
        im.connect('removed_child', self.__imageRemovedChild)

        _layers = [im.getTopLayer()]
        while len(_layers):
            _layer = _layers.pop()
            self.__layer = _layer
            self.__model.foreach(self.__modelAddLayer)
            _layer.connect('visibility_changed', self.__layerVisibilityChanged)
            _layer.connect('name_changed', self.__layerNameChanged)
            _layers.extend(_layer.getSublayers())

    def __treeViewButtonPress(self, widget, event, data=None):
        _button = event.button
        _x = int(event.x)
        _y = int(event.y)
        _rv = event.window is widget.get_bin_window() and _button == 3
        if _rv:
            _menu = self.__makePopupMenu(widget, _x, _y)
            if _menu is not None:
                _menu.popup(None, None, None, _button, event.time)
        return _rv

    def __makePopupMenu(self, widget, x, y):
        # print "Entered LayerDisplay._makePopupMenu"
        _data = widget.get_path_at_pos(x, y)
        if _data is None:
            return None
        _path, _col, _cx, _cy = _data
        _model = widget.get_model()
        _iter = _model.get_iter(_path)
        _layer = _model.get_value(_iter, 1)
        #
        _menu = gtk.Menu()
        _item = gtk.MenuItem(_('Rename'))
        _item.connect("activate", self.__renameLayer)
        _menu.append(_item)
        if _layer.isVisible():
            _item = gtk.MenuItem(_('Hide'))
            _flag = False
        else:
            _item = gtk.MenuItem(_('Show'))
            _flag = True
        _item.connect("activate", self.__setLayerVisibility, _flag)
        _menu.append(_item)
        _item = gtk.MenuItem(_('Add Child Layer'))
        _item.connect("activate", self.__addChildLayer)
        _menu.append(_item)
        if _layer.hasSublayers():
            _item = gtk.MenuItem(_('Hide Children'))
            _item.connect("activate", self.__setChildrenVisibility, False)
            _menu.append(_item)
            _item = gtk.MenuItem(_('Show Children'))
            _item.connect("activate", self.__setChildrenVisibility, True)
            _menu.append(_item)
        else:
            if _layer.getParentLayer() is not None:
                if not _layer.hasSublayers():
                    _item = gtk.MenuItem(_('Delete'))
                    _item.connect("activate", self.__deleteLayer)
                    _menu.append(_item)
        _item = gtk.MenuItem(_('Clear Layer'))
        _item.connect("activate", self.__clearLayer)
        _menu.append(_item)
        _menu.show_all()
        self.__layer = _layer
        return _menu

    def __selectionChanged(self, selection, data=None):
        if selection is not None:
            _model, _iter = selection.get_selected()
            if _iter is not None:
                _layer = _model.get_value(_iter, 1)
                self.__image.setActiveLayer(_layer)

    def __cellEdited(self, cell_renderer, path, text):
        _model = self.__model
        _iter = _model.get_iter_from_string(path)
        _layer = _model.get_value(_iter, 1)
        _layer.setName(text)
        _model.set(_iter, 0, text)

    def __reordered(self, model, path, iter, new_order):
        print "in reordered()"
        print "model: " + `model`
        print "path: " + `path`
        print "iter: " + `iter`
        print "new_order: " + `new_order`

    def __modelFindLayer(self, iter=None):
        # print "_modelFindLayer() ..."
        _model = self.__model
        _iter = iter
        if _iter is None:
            _iter = _model.get_iter_first()
        _layer = self.__layer
        _path = None
        _mlayer = _model.get_value(_iter, 1)
        if _mlayer is _layer:
            _path = _model.get_path(_iter)
        else:
            if _model.iter_has_child(_iter):
                _child = _model.iter_children(_iter)
                while _child is not None:
                    _path = self.__modelFindLayer(_child)
                    if _path is not None:
                        break
                    _child = _model.iter_next(_child)
        return _path


    def __modelAddLayer(self, model, path, iter):
        # print "_modelAddLayer() ..."
        _layer = self.__layer
        _mlayer = model.get_value(iter, 1)
        _val = _mlayer is _layer.getParentLayer()
        if _val:
            _iter = model.append(iter)
            model.set(_iter, 0, _layer.getName())
            model.set(_iter, 1, _layer)
        return _val

    def __imageAddedChild(self, obj, *args):
        # print "__imageAddedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _newlayer = args[0]
        self.__layer = _newlayer
        self.__model.foreach(self.__modelAddLayer)
        _path = self.__modelFindLayer()
        if _path is None:
            raise ValueError, "Layer not found in model!"
        _ppath = _path[:-1]
        _tv = self.__treeview
        while len(_ppath):
            if not _tv.row_expanded(_ppath):
                _tv.expand_row(_ppath, False)
            _ppath = _ppath[:-1]
        _tv.get_selection().select_path(_path)
        _newlayer.connect('visibility_changed', self.__layerVisibilityChanged)
        _newlayer.connect('name_changed', self.__layerNameChanged)

    def __modelDeleteLayer(self, model, path, iter):
        # print "_modelDeleteLayer() ..."
        _mlayer = model.get_value(iter, 1)
        _val = _mlayer is self.__layer
        if _val:
            model.remove(iter)
        return _val

    def __imageRemovedChild(self, obj, *args):
        # print "__imageRemovedChild()"
        _path = self.__modelFindLayer()
        if _path is None:
            raise ValueError, "Layer not found in model!"
        _ppath = _path[:-1]
        _tv = self.__treeview
        while len(_ppath):
            if not _tv.row_expanded(_ppath):
                _tv.expand_row(_ppath, False)
            _ppath = _ppath[:-1]
        self.__model.foreach(self.__modelDeleteLayer)
        self.__layer.disconnect(self)
        _tv.get_selection().select_path(_path[:-1])        

    def __modelDisconnectLayer(self, model, path, iter):
        # print "__modelDisconnnectLayer() ..."
        _layer = model.get_value(iter, 1)
        _layer.disconnect(self)
        return False

    def __activeLayerChanged(self, obj, *args):
        # print "_activeLayerChanged()"
        self.__layer = obj.getActiveLayer()
        _path = self.__modelFindLayer()
        if _path is None:
            raise ValueError, "Layer not found in model!"
        _ppath = _path[:-1]
        _tv = self.__treeview
        while len(_ppath):
            if not _tv.row_expanded(_ppath):
                _tv.expand_row(_ppath, False)
            _ppath = _ppath[:-1]
        _tv.get_selection().select_path(_path)

    def __layerVisibilityChanged(self, obj, *args):
        # print "_layerVisibilityChanged()"
        for _obj in obj.getLayerEntities('point'):
            if _obj.isVisible():
                _obj.sendMessage('refresh')
        _ctypes = ['hcline', 'vcline', 'acline', 'cline', 'ccircle']
        for _ctype in _ctypes:
            for _obj in obj.getLayerEntities(_ctype):
                if _obj.isVisible():
                    _obj.sendMessage('refresh')
        _gtypes = ['segment', 'circle', 'arc', 'leader', 'polyline',
                   'chamfer', 'fillet', 'textblock', 'linear_dimension',
                   'horizontal_dimension', 'vertical_dimension',
                   'radial_dimension', 'angular_dimension']
        for _gtype in _gtypes:
            for _obj in obj.getLayerEntities(_gtype):
                if _obj.isVisible():
                    _obj.sendMessage('refresh')

    def __modelRenameLayer(self, model, path, iter):
        _layer = self.__layer
        _mlayer = model.get_value(iter, 1)
        _val = _mlayer is _layer
        if _val:
            model.set(iter, 0, _layer.getName())
        return _val

    def __layerNameChanged(self, obj, *args):
        self.__layer = obj
        self.__model.foreach(self.__modelRenameLayer)
        
    def __setLayerVisibility(self, menuitem, data=None):
        _image = self.__image
        _image.startAction()
        try:
            self.__layer.setVisibility(data)
        finally:
            _image.endAction()
        return False

    def __setChildrenVisibility(self, menuitem, data=None):
        _image = self.__image
        _image.startAction()
        try:
            _layers = self.__layer.getSublayers()
            while len(_layers):
                _layer = _layers.pop()
                _layer.setVisibility(data)
                _layers.extend(_layer.getSublayers())
        finally:
            _image.endAction()
        return False

    def __deleteLayer(self, menuitem, data=None):
        _image = self.__image
        _layer = self.__layer
        _image.startAction()
        try:
            if _layer.hasChildren():
                _layer.clear()
            _image.delLayer(_layer)
            _layer.finish()
        finally:
            _image.endAction()
        self.__layer = None
        return False

    def __clearLayer(self, menuitem, data=None):
        _image = self.__image
        _image.startAction()
        try:
            self.__layer.clear()
        finally:
            _image.endAction()
        return False

    def __addChildLayer(self, menuitem, data=None):
        if _debug is True:
            print "SDB Debug: entered LayerDisplay.addChildLayer()..."
        _window = self.__window
        _dialog = gtk.Dialog(_('Add New Child Layer'), _window,
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_OK, gtk.RESPONSE_OK,
                              gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        _hbox = gtk.HBox(False, 2)
        _hbox.set_border_width(2)
        _dialog.vbox.pack_start(_hbox, False, False, 0)
        _label = gtk.Label(_('Name:'))
        _hbox.pack_start(_label, False, False, 0)
        _entry = gtk.Entry()
        _entry.set_text(_('NewChildLayer'))
        _hbox.pack_start(_entry, True, True, 0)
        _dialog.show_all()
        _response = _dialog.run()
        if _response == gtk.RESPONSE_OK:
            _name = _entry.get_text()
            if len(_name):
                _new_layer = layer.Layer(_name)
                _image = self.__image
                _image.startAction()
                try:
                    _image.addChildLayer(_new_layer, self.__layer)
                finally:
                    _image.endAction()
        _dialog.destroy()
        return False

    def __renameLayer(self, menuitem, data=None):
        if _debug is True:
            print "SDB debug: entered _renameLayer()"
        _layer = self.__layer
        _name = _layer.getName()
        _window = self.__window
        _dialog = gtk.Dialog(_('Rename Layer'), _window,
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_OK, gtk.RESPONSE_OK,
                              gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        _hbox = gtk.HBox(False, 2)
        _hbox.set_border_width(2)
        _dialog.vbox.pack_start(_hbox, False, False, 0)
        _label = gtk.Label(_('Name:'))
        _hbox.pack_start(_label, False, False, 0)
        _entry = gtk.Entry()
        _entry.set_text(_name)
        _hbox.pack_start(_entry, True, True, 0)
        _dialog.show_all()
        _response = _dialog.run()
        if _response == gtk.RESPONSE_OK:
            _new_name = _entry.get_text()
            if len(_new_name):
                _image = self.__image
                _image.startAction()
                try:
                    _layer.setName(_new_name)
                finally:
                    _image.endAction()
        _dialog.destroy()
        return False

    def close(self):
        self.__model.foreach(self.__modelDisconnectLayer)
        self.__image.disconnect(self)
        self.__image = None
        self.__window = None
        self.__sw = None
        self.__model = None
        self.__treeview = None
        self.__layer = None

    def getWindow(self):
        return self.__sw

class ImageView(object):
    def __init__(self, im, xmin=0.0, ymax=0.0, upp=1.0):
        if _debug is True:
            print "SDB debug: Created new ImageView class instance"
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        _xmin = util.get_float(xmin)
        _ymax = util.get_float(ymax)
        _upp = util.get_float(upp)
        if not _upp > 0.0:
            raise ValueError, "Invalid units-per-pixel value: %g" % _upp
        self.__image = im
        self.__pixmap = None
        self.__gc = None
        self.__width = None
        self.__height = None
        _da = gtk.DrawingArea()
        _da.set_size_request(100, 100)
        _black = gtk.gdk.color_parse('black')
        _da.modify_fg(gtk.STATE_NORMAL, _black)
        _da.modify_bg(gtk.STATE_NORMAL, _black)
        _da.set_flags(gtk.CAN_FOCUS)

        _da.connect("expose_event", self.__exposeEvent)
        _da.connect("realize", self.__realizeEvent)
        _da.connect("configure_event", self.__configureEvent)
        _da.connect("key_press_event", self.__keyPressEvent)
        _da.connect("key_release_event", self.__keyPressEvent)
        _da.connect("enter_notify_event", self.__elNotifyEvent)
        _da.connect("leave_notify_event", self.__elNotifyEvent)
        _da.connect("focus_in_event", self.__focusChangedEvent)
        _da.connect("focus_out_event", self.__focusChangedEvent)

        _da.set_events(gtk.gdk.EXPOSURE_MASK |
                       gtk.gdk.LEAVE_NOTIFY_MASK |
                       gtk.gdk.BUTTON_PRESS_MASK |
                       gtk.gdk.BUTTON_RELEASE_MASK |
                       gtk.gdk.ENTER_NOTIFY_MASK|
                       gtk.gdk.LEAVE_NOTIFY_MASK|
                       gtk.gdk.KEY_PRESS_MASK |
                       gtk.gdk.KEY_RELEASE_MASK |
                       gtk.gdk.FOCUS_CHANGE_MASK |
                       gtk.gdk.POINTER_MOTION_MASK)
        self.__da = _da
        self.__xmin = _xmin
        self.__ymax = _ymax
        self.__upp = _upp
        self.__view = None
        im.connect('added_child', self.__imageAddedChild)
        im.connect('removed_child', self.__imageRemovedChild)
        im.connect('modified', self.__objModified)

    def __realizeEvent(self, widget, data=None):
        _win = widget.window
        _w, _h = _win.get_size()
        self.__width = _w
        self.__height = _h
        _gc = _win.new_gc()
        _gc.set_exposures(True)
        self.__gc = _gc

    def __exposeEvent(self, widget, event, data=None):
        _pixmap = self.__pixmap
        _x, _y, _w, _h = event.area
        _gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
        widget.window.draw_drawable(_gc, _pixmap, _x, _y, _x, _y, _w, _h)
        return True

    def __configureEvent(self, widget, event, data=None):
        _win = widget.window
        _w, _h = _win.get_size()
        if self.__width != _w or self.__height != _h:
            self.__view = None
            self.__width = _w
            self.__height = _h
            _pixmap = gtk.gdk.Pixmap(_win, _w, _h)
            _gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
            _pixmap.draw_rectangle(_gc, True, 0, 0, _w, _h)
            self.__pixmap = _pixmap
        return True

    def __focusChangedEvent(self, widget, event, data=None):
        return False

    def __buttonPressEvent(self, widget, event, data=None):
        _rv = False
        _tool = gtkimage.getTool()
        gtkimage.setToolpoint(event)
        if (event.button == 1 and
            _tool is not None and
            _tool.hasHandler('button_press')):
            _rv = _tool.getHandler('button_press')(gtkimage, widget,
                                                   event, _tool)
        return _rv

    def __buttonReleaseEvent(self, widget, event, data=None):
        _rv = False
        _tool = gtkimage.getTool()
        gtkimage.setToolpoint(event)
        if (event.button == 1 and
            _tool is not None and
            _tool.hasHandler('button_release')):
            _rv = _tool.getHandler('button_release')(gtkimage, widget,
                                                     event, _tool)
        return _rv

    def __keyPressEvent(self, widget, event, data=None):
        _key = event.keyval
        _rv = (_key == gtk.keysyms.Left or
               _key == gtk.keysyms.Right or
               _key == gtk.keysyms.Up or
               _key == gtk.keysyms.Down)
        if _rv:
            _mods = event.state & gtk.accelerator_get_default_mod_mask()
            _dx = _dy = None
            if (_key == gtk.keysyms.Left):
                _dx = -1.0
            elif (_key == gtk.keysyms.Right):
                _dx = 1.0
            elif (_key == gtk.keysyms.Up):
                _dy = 1.0
            elif (_key == gtk.keysyms.Down):
                _dy = -1.0
            else:
                raise ValueError, "Unexpected keyval: %d" % _key
            if (_mods == gtk.gdk.CONTROL_MASK):
                _scale = 0.25
            elif (_mods == gtk.gdk.SHIFT_MASK):
                _scale = 0.5
            elif (_mods == gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK):
                _scale = 1.0
            else:
                _scale = 0.05
        if not _rv:
            _tool = gtkimage.getTool()
            if _tool is not None and _tool.hasHandler('key_press'):
                _rv = _tool.getHandler('key_press')(gtkimage, widget,
                                                    event, _tool)
        return _rv

    def __keyReleaseEvent(self, widget, event, data=None):
        _rv = False
        _tool = gtkimage.getTool()
        if _tool is not None and _tool.hasHandler('key_release'):
            _rv = _tool.getHandler('key_release')(gtkimage, widget,
                                                  event, _tool)
        return _rv

    def __motionNotifyEvent(self, widget, event, data=None):
        _rv = False
        _tool = gtkimage.getTool()
        gtkimage.setToolpoint(event)
        if _tool is not None and _tool.hasHandler('motion_notify'):
            _rv = _tool.getHandler('motion_notify')(gtkimage, widget,
                                                    event, _tool)
        return _rv
    
    def __elNotifyEvent(self, widget, event, data=None):
        gtkimage.setToolpoint(event)
        return True
                          
    def __drawObject(self, obj, col=None):
        _col = col
        _xmin, _ymin, _xmax, _ymax = self.getView()
        if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
            _image = self.__image
            if _col is None:
                if obj.getParent() is not _image.getActiveLayer():
                    _col = _image.getOption('INACTIVE_LAYER_COLOR')
            obj.draw(self, _col)

    def __imageAddedChild(self, obj, *args):
        # print "_imageAddedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _layer = args[0]
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Unexpected child type: " + `type(_layer)`
        _layer.connect('added_child', self.__layerAddedChild)
        _layer.connect('removed_child', self.__layerRemovedChild)

    def __layerAddedChild(self, obj, *args):
        # print "__layerAddedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _child = args[0] # need some verification test here ...
        _child.connect('modified', self.__objModified)
        _child.connect('visibility_changed', self.__objVisibilityChanged)
        _child.connect('refresh', self.__refreshObject)
        _child.connect('change_pending', self.__objChanging)
        if _child.isVisible() and obj.isVisible():
            self.__drawObject(_child)

    def __imageRemovedChild(self, obj, *args):
        # print "__imageRemovedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _layer = args[0]
        if not isinstance(_layer, layer.Layer):
            raise TypeError, "Unexpected child type: " + `type(_layer)`
        _layer.disconnect(self)

    def __layerRemovedChild(self, obj, *args):
        # print "__layerDeletedChild()"
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _child = args[0] # need some verification test here ...
        if _child.isVisible() and obj.isVisible():
            _color = self.__image.getOption('BACKGROUND_COLOR')
            self.__drawObject(_child, _color)
        _child.disconnect(self)

    def __objModified(self, obj, *args):
        # print "__objModified()"
        if obj.isVisible() and obj.getParent().isVisible():
            self.__drawObject(obj)

    def __objChanging(self, obj, *args):
        # print "__objChanging()"
        if obj.isVisible() and obj.getParent().isVisible():
            self.__drawObject(obj, self.__image.getOption('BACKGROUND_COLOR'))
            
    def __objVisibilityChanged(self, obj, *args):
        # print "__objVisibilityChanged()"
        if obj.getParent().isVisible():
            _col = None
            if not obj.isVisible():
                _col = self.__image.getOption('BACKGROUND_COLOR')
            self.__drawObject(obj, _col)

    def __refreshObject(self, obj, *args):
        # print "__refreshObject()"
        _col = None
        if not obj.isVisible() or not obj.getParent().isVisible():
            _col = self.__image.getOption('BACKGROUND_COLOR')
        self.__drawObject(obj, _col)

    def getView(self):
        """Get the region of space the ImageView draws

getRegion()

This method returns a tuple of four values: xmin, ymin, xmax, ymax
        """
        if self.__view is None:
            _xmin = self.__xmin
            _ymax = self.__ymax
            _upp = self.__upp
            _w = self.__width
            _h = self.__height
            _xmax = _xmin + (_upp * _w)
            _ymin = _ymax - (_upp * _h)
            self.__view = (_xmin, _ymin, _xmax, _ymax)
        return self.__view

    def getPixmap(self):
        """Return the gtk.gdk.Pixmap for this ImageView.

getPixmap()
        """
        return self.__pixmap

    def getUnitsPerPixel(self):
        """Return the units-per-pixel scaling factor for the ImageView.

getUnitsPerPixel()
        """
        return self.__upp

    def setUnitsPerPixel(self, upp):
        """Set the units-per-pixel scaling factor for the ImageView.

setUnitsPerPixel(upp)

Argument 'upp' should be a float value greater
        """
        _upp = util.get_float(upp)
        if not _upp > 0.0:
            raise ValueError, "Invalid units-per-pixel value: %g" % _upp
        self.__upp = _upp
        self.__view = None

    def pixelsToCoords(self, x, y):
        """Convert from pixel coordinates to x-y coordinates.

pixelsToCoords(x, y)

Arguments 'x' and 'y' should be positive integers. This method
returns a tuple of two float values
        """
        if not isinstance(x, int):
            raise TypeError, "Invalid 'x' type: " + `type(x)`
        if x < 0:
            raise ValueError, "Invalid 'x' value: %d" % x
        if not isinstance(y, int):
            raise TypeError, "Invalid 'y' type: " + `type(y)`
        if y < 0:
            raise ValueError, "Invalid 'y' value: %d" % y
        _upp = self.__upp
        _xc = self.__xmin + (x * _upp)
        _yc = self.__ymax - (y * _upp)
        return _xc, _yc

    def coordsToPixels(self, x, y):
        """Convert from x-y coordinates to pixel coordinates

coordsToPixels(x, y)

Arguments 'x' and 'y' should be float values. This method
returns a tuple holding two integer values
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _upp = self.__upp
        _xp = int((x - self.__xmin)/_upp)
        _yp = int((self.__ymax - y)/_upp)
        return _xp, _yp

    def close(self):
        self.__image.disconnect(self)

    def redraw(self):
        """This method draws all the objects visible in the ImageView.

redraw()
        """
        _da = self.__da
        if (_da.flags() & gtk.MAPPED):
            _image = self.__image
            _w = self.__width
            _h = self.__height
            _gc = _da.get_style().fg_gc[gtk.STATE_NORMAL]
            self.__pixmap.draw_rectangle(_gc, True, 0, 0, _w, _h)
            _active = _image.getActiveLayer()
            _layers = [_image.getTopLayer()]
            while (len(_layers)):
                _layer = _layers.pop()
                if _layer is not _active:
                    self.drawLayer(_layer)
                _layers.extend(_layer.getSublayers())
            self.drawLayer(_active)
            _da.queue_draw() # generate an expose event

    def drawLayer(self, l):
        if not isinstance(l, layer.Layer):
            raise TypeError, "Invalid layer type: " + `type(l)`
        if l.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        if l.isVisible():
            _xmin = self.__xmin
            _ymax = self.__ymax
            _upp = self.__upp
            _xmax = _xmin + (_upp * _w)
            _ymin = _ymax - (_upp * _h)
            _col = self.getOption('INACTIVE_LAYER_COLOR')
            if l is self.getActiveLayer():
                _col = None
            _cobjs = []
            _objs = []
            _pts = []
            for _obj in l.objsInRegion(_xmin, _ymin, _xmax, _ymax):
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


class ImageWindow(object):
    def __init__(self, im):
        if _debug is True:
            print "SDB debug: instantiated another ImageWindow class instance"
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        self.__image = im
        #
        # Display window
        #
        _window = gtk.Window()
        _window.set_title("Untitled")
        _window.connect("destroy", self._closeImage)
        _width = min(1024, int(0.8 * float(gtk.gdk.screen_width())))
        _height = min(768, int(0.8 * float(gtk.gdk.screen_height())))
        _window.set_default_size(_width, _height)
        #
        _vbox = gtk.VBox(False, 2)
        _vbox.set_border_width(2)
        _window.add(_vbox)
        self.__ldisp = LayerDisplay(im)

    def getImage(self):
        """Return the Image stored in the ImageDisplay.

getImage()
        """
        return self.__image

    image = property(getImage, None, None, "The Image used for visualizing.")

    def closeImage(self, widget):
        """Close a window containing a Image.

closeImage()
        """
        _image = self.__image
        _image.close()
        _image.disconnect(self)
        self.__ldisp(close)
        for _i in xrange(len(globals.imagelist)):
            _gimage = globals.imagelist[_i]
            if _image is _gimage:
                del globals.imagelist[_i]
                _gimage.window.destroy()
                if not len(globals.imagelist):
                    gtk.main_quit()
                break
        return False
