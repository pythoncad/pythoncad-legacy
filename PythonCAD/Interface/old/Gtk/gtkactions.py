#
# Copyright (c) 2005, 2006 Art Haas
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
# GTK Menu building code
#
# In GTK 2.4 the Action and ActionGroup classes were added to simplify,
# and enhance the UI code of GTK. Earlier releases had the ItemFactory
# or just raw MenuBar, MenuItem, and Menu widgets. The code in
# this file is meant to provide some functionality found in the gtk.Action
# and gtk.ActionGroup classes so that PythonCAD can still run on PyGTK
# releases prior to the support of the GTK Action and ActionGroup classes
#
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class stdActionGroup(gobject.GObject):
    __gproperties__ = {
        'name' : (gobject.TYPE_STRING, 'Name', 'Name',
                  '', gobject.PARAM_READWRITE),
        'sensitive' : (gobject.TYPE_BOOLEAN, 'Sensitive',
                  'Sensitivity', True, gobject.PARAM_READWRITE),
        'visible' : (gobject.TYPE_BOOLEAN, 'Visible',
                  'Visibility', True, gobject.PARAM_READWRITE),
        }

    __gsignals__ = {
        'connect-proxy' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
        'disconnect-proxy' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                              (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
        'post-activate' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,)),
        'pre-activate' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                          (gobject.TYPE_PYOBJECT,))
        }
    
    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name
        self.__actions = {}
        self.sensitive = True
        self.visible = True

    def get_name(self):
        return self.name

    def get_sensitive(self):
        return self.sensitive

    def set_sensitive(self, sensitive):
        _s = self.sensitive
        if _s is not sensitive:
            self.sensitive = sensitive

    def get_visible(self):
        return self.visible

    def set_visible(self, visible):
        _v = self.visible
        if _v is not visible:
            self.visible = visible

    def get_action(self, action):
        return self.__actions.get(action)

    def list_actions(self):
        return self.__actions.values()

    def add_action(self, action):
        _name = action.get_name()
        action.set_property('action-group', self)
        self.__actions[_name] = action

    def add_action_with_accel(self, action, accel):
        # print "add_action_with_accel"
        _keyval = None
        _mods = None
        _name = action.get_name()
        _path = "/".join(['<Actions>', self.name, _name])
        if accel is None:
            # print "accel is None"
            _sid = action.get_property('stock-id')
            if _sid != '':
                # print "sid = '%s'" % _sid
                _data = gtk.stock_lookup(_sid)
                if _data is not None and _data[3] != 0:
                    # print "data: " + str(_data)
                    _mods = _data[2]
                    _keyval = _data[3]
        else:
            _k, _m = gtk.accelerator_parse(accel)
            if gtk.accelerator_valid(_k, _m):
                _keyval = _k
                _mods = _m
        if _keyval is not None:
            # print "calling gtk.accel_map_change_entry()"
            # print "Path: " + _path
            # print "Key: " + str(_keyval)
            # print "Mods: " + str(_mods)
            if not gtk.accel_map_change_entry(_path, _keyval, _mods, True):
                print "Failed to change accel_map for '%s'" % _path
        action.set_accel_path(_path)
        self.add_action(action)

    def remove_action(self, action):
        _name = action.get_name()
        del self.__actions[_name]
        action.set_property('action-group', None)

    def do_get_property(self, property):
       if property.name == 'name':
           _val = self.name
       elif property.name == 'sensitive':
           _val = self.sensitive
       elif property.name == 'visible':
           _val = self.visible
       else:
           raise AttributeError, "Unknown property '%s'" % property
       return _val

    def do_set_property(self, property, value):
        if property.name == 'name':
            raise AttributeError, "Property 'name' cannot be changed."
        elif property.name == 'sensitive':
            self.set_sensitive(value)
        elif property.name == 'visible':
            self.set_visible(value)
        else:
            raise AttributeError, "Unknown property '%s'" % property

if not hasattr(gtk, 'ActionGroup'):
    gobject.type_register(stdActionGroup)

class stdAction(gobject.GObject):
    __gproperties__ = {
        'action_group' : (gobject.TYPE_PYOBJECT, 'Action Group',
                          'Action Group', gobject.PARAM_READWRITE),
        'hide_if_empty' : (gobject.TYPE_BOOLEAN, 'Hide', 'Hide',
                           True, gobject.PARAM_READWRITE),
        'is_important' : (gobject.TYPE_BOOLEAN, 'Importance', 'Importance',
                          False, gobject.PARAM_READWRITE),
        'label' : (gobject.TYPE_STRING, 'Label', 'Label',
                   '', gobject.PARAM_READWRITE),
        'name' : (gobject.TYPE_STRING, 'Name', 'Name',
                  '', gobject.PARAM_READWRITE),
        'sensitive' : (gobject.TYPE_BOOLEAN, 'Sensitive',
                  'Sensitivity', True, gobject.PARAM_READWRITE),
        'short_label' : (gobject.TYPE_STRING, 'Short Label', 'Short Label',
                         '', gobject.PARAM_READWRITE),
        'stock_id' : (gobject.TYPE_STRING, 'Stock ID', 'Stock ID',
                      '', gobject.PARAM_READWRITE),
        'tooltip' : (gobject.TYPE_STRING, 'Tooltip', 'Tooltip',
                     '', gobject.PARAM_READWRITE),
        'visible' : (gobject.TYPE_BOOLEAN, 'Visible',
                  'Visibility', True, gobject.PARAM_READWRITE),
        'visible_horizontal' : (gobject.TYPE_BOOLEAN,
                                'Visible Horizontal', 'Visible Horizontal',
                                True, gobject.PARAM_READWRITE),
        'visible_overflown' : (gobject.TYPE_BOOLEAN,
                                'Visible Overflown', 'Visible Overflown',
                                True, gobject.PARAM_READWRITE),
        'visible_vertical' : (gobject.TYPE_BOOLEAN,
                              'Visible Vertical', 'Visible Vertical',
                              True, gobject.PARAM_READWRITE)
        }

    __gsignals__ = {
        'activate' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                      ())
        }
    
    def __init__(self, name, label, tooltip, stock_id):
        gobject.GObject.__init__(self)
        self.name = name
        self.label = label
        self.tooltip = ''
        if tooltip is not None:
            self.tooltip = tooltip
        self.stock_id = ''
        if stock_id is not None:
            self.stock_id = stock_id
        self.action_group = None
        self.hide_if_empty = False
        self.is_important = True
        self.sensitive = True
        self.short_label = None
        self.visible = True
        self.visible_horizontal = True
        self.visible_overflown = True
        self.visible_vertical = True
        self.__lset = False # lab
        self.__slset = False
        self.__accelpath = None
        self.__accelgroup = None
        self.__accelcount = 0
        self.__proxies = []
        self.__hids = {}

    def get_name(self):
        return self.name

    def is_sensitive(self):
        return self.sensitive and (self.action_group is None or
                                   self.action_group.get_sensitive())

    def get_sensitive(self):
        return self.sensitive

    def set_sensitive(self, sensitive):
        _s = self.sensitive
        if _s is not sensitive:
            self.sensitive = sensitive
            self.notify('sensitive')

    def is_visible(self):
        return self.visible and (self.action_group is None or
                                 self.action_group.get_visible())

    def get_visible(self):
        return self.visible

    def set_visible(self, visible):
        _v = self.visible
        if _v is not visible:
            self.visible = visible
            self.notify('visible')

    def activate(self):
        # print "stdAction::activate()"
        if self.is_sensitive():
            _group = self.action_group
            if _group is not None:
                _group.emit('pre-activate', self)
            self.emit('activate')
            if _group is not None:
                _group.emit('post-activate', self)
   
    def create_icon(self, size):
        _icon = None
        if self.stock_id != '':
            _icon = gtk.image_new_from_stock(self.stock_id, size)
        return _icon

    def create_menu_item(self):
        _item = gtk.ImageMenuItem()
        self.connect_proxy(_item)
        return _item

    def create_tool_item(self):
        return None

    def connect_proxy(self, widget):
        _pact = widget.get_data('gtk-action')
        if _pact is not None:
            _pact.disconnect_proxy(widget)
        _hids = self.__hids.setdefault(id(widget),[])
        widget.set_data('gtk-action', self)
        self.__proxies.insert(0, widget)
        _hid = widget.connect('destroy', self._remove_proxy)
        _hids.append(_hid)
        _hid = self.connect_object('notify::sensitive',
                                   self._sync_sensitivity,
                                   widget)
        _hids.append(_hid)
        widget.set_sensitive(self.is_sensitive())
        _hid = self.connect_object('notify::visible',
                                   self._sync_visibility,
                                   widget)
        _hids.append(_hid)
        if self.is_visible():
            widget.show()
        else:
            widget.hide()
        if hasattr(widget, 'set_no_show_all'):
            widget.set_no_show_all(True)
        if isinstance(widget, gtk.MenuItem):
            if self.__accelpath is not None:
                self.connect_accelerator()
                widget.set_accel_path(self.__accelpath)
            _label = widget.child
            if _label is None:
                _label = gtk.AccelLabel('')
                _label.set_property('use_underline', True)
                _label.set_property('xalign', 0.0)
                _label.set_property('visible', True)
                _label.set_property('parent', widget)
                _label.set_accel_widget(widget)
            _label.set_label(self.label)
            _hid = self.connect_object('notify::label',
                                       self._sync_label,
                                       widget)
            _hids.append(_hid)
            if isinstance(widget, gtk.ImageMenuItem):
                _image = widget.get_image()
                if _image is not None and not isinstance(_image, gtk.Image):
                    widget.set_image(None)
                    _image = None
                if _image is None:
                    _image = gtk.image_new_from_stock(self.stock_id,
                                                      gtk.ICON_SIZE_MENU)
                    widget.set_image(_image)
                    _image.show()
                _image.set_from_stock(self.stock_id, gtk.ICON_SIZE_MENU)
                _hid = self.connect_object('notify::stock-id',
                                           self._sync_stock_id,
                                           widget)
                _hids.append(_hid)
            if widget.get_submenu() is None:
                _hid = widget.connect_object('activate',
                                             stdAction.activate,
                                             self)
                _hids.append(_hid)
        else:
            raise TypeError, "Unexpected proxy widget type: " + `type(widget)`
        if self.action_group is not None:
            self.action_group.emit('connect-proxy', self, widget)

    def disconnect_proxy(self, widget):
        if widget.get_data('gtk-action') is not self:
            raise ValueError, "Action not being proxied by widget: " + `widget`
        widget.set_data('gtk-action', None)
        _hids = self.__hids.get(id(widget))
        if _hids is not None:
            for _hid in _hids:
                if self.handler_is_connected(_hid):
                    self.disconnect(_hid)
                    continue
                if widget.handler_is_connected(_hid):
                    widget.disconnect(_hid)
        if self.action_group is not None:
            self.action_group.emit('disconnect-proxy', self, widget)
        
    def get_proxies(self):
        return self.__proxies[:]

    def _accel_cb(self, accelgroup, acceleratable, keyval, mod):
        # print "_accel_cb()"
        pass
        
    def connect_accelerator(self):
        # print "connect_accelerator()"
        if self.__accelgroup is not None and self.__accelpath is not None:
            _count = self.__accelcount
            if _count == 0:
                # print "calling accelgroup.connect_by_path()"
                # print "accelpath: " + self.__accelpath
                if hasattr(self.__accelgroup, 'connect_by_path'):
                    self.__accelgroup.connect_by_path(self.__accelpath,
                                                      self._accel_cb)
            _count = _count + 1

    def disconnect_accelerator(self):
        # print "disconnect_accelerator()"
        if self.__accelgroup is not None and self.__accelpath is not None:
            _count = self.__accelcount
            _count = _count - 1
            if _count > 0:
                self.__accelgroup.disconnect(self._accel_cb)

    def block_activate_from(self, widget):
        pass

    def unblock_activate_from(self, widget):
        pass

    def get_accel_path(self):
        return self.__accelpath

    def set_accel_path(self, path):
        self.__accelpath = path

    def set_accel_group(self, group):
        self.__accelgroup = group
       
    def do_get_property(self, property):
        if property.name == 'name':
            _val = self.name
        elif property.name == 'label':
            _val = self.label
        elif property.name == 'tooltip':
            _val = self.tooltip
        elif property.name == 'stock-id':
            _val = self.stock_id
        elif property.name == 'action-group':
            _val = self.action_group
        elif property.name == 'hide-if-empty':
            _val = self.hide_if_empty
        elif property.name == 'is-important':
            _val = self.is_important
        elif property.name == 'sensitive':
            _val = self.sensitive
        elif property.name == 'short-label':
            _val = self.short_label
        elif property.name == 'visible':
            _val = self.visible
        elif property.name == 'visible-horizontal':
            _val = self.visible_horizontal
        elif property.name == 'visible-overflown':
            _val = self.visible_overflown
        elif property.name == 'visible-vertical':
            _val = self.visible_vertical
        else:
            raise AttributeError, "Unknown property '%s'" % property
        return _val

    def do_set_property(self, property, value):
        if property.name == 'name':
            raise AttributeError, "Property 'name' cannot be changed."
        elif property.name == 'label':
            self.label = value
            self.__lset = self.label != ''
            if not self.__lset and self.stock_id != '':
                _item = gtk.stock_lookup(self.stock_id)
                if _item is not None:
                    self.label = _item[2]
            if not self.__slset:
                self.short_label = self.label
                self.notify('short-label')
        elif property.name == 'tooltip':
            self.tooltip = value
        elif property.name == 'stock-id':
            self.stock_id = value
            if not self.__lset:
                _item = gtk.stock_lookup(self.stock_id)
                if _item is not None:
                    self.label = _item[2]
                else:
                    self.label = ''
                self.notify('label')
            if not self.__slset:
                self.short_label = self.label
                self.notify('short-label')
        elif property.name == 'action-group':
            self.action_group = value
        elif property.name == 'hide-if-empty':
            self.hide_if_empty = value
        elif property.name == 'is-important':
            self.is_important = value
        elif property.name == 'sensitive':
            self.set_sensitive(value)
        elif property.name == 'short-label':
            self.short_label = value
            self.__slset = self.short_label != ''
            if not self.__slset:
                self.__slset = self.label
        elif property.name == 'visible':
            self.set_visible(value)
        elif property.name == 'visible-horizontal':
            self.visible_horizontal = value
        elif property.name == 'visible-overflow':
            self.visible_overflown = value
        elif property.name == 'visible-vertical':
            self.visible_vertical = value
        else:
            raise AttributeError, "Unknown property '%s'" % property

    def do_activate(self):
        #print "do_activate()"
        pass

    def _remove_proxy(self, widget):
        for _p in self.__proxies[:]:
            if _p is widget:
                self.__proxies.remove(_p)
                break

    def _sync_sensitivity(self, widget, data=None):
        widget.set_sensitive(self.is_sensitive())
            
    def _sync_visibility(self, widget, data=None):
        widget.set_visible(self.is_visible())

    def _sync_label(self, widget, data=None):
        _label = widget.child
        if _label is not None and isinstance(_label, gtk.Label):
            _label.set_label(self.label)

    def _sync_stock_id(self, widget, data=None):
        _image = widget.get_image()
        if isinstance(_image, gtk.Image):
            _image.set_from_stock(self.stock_id, gtk.ICON_SIZE_MENU)

if not hasattr(gtk, 'Action'):
    gobject.type_register(stdAction)
