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

import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms

#from PythonCAD.Interface.Gtk.gtkimage import GTKImage

from PythonCAD.Interface.Gtk import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
from PythonCAD.Interface.Gtk import gtktext
from PythonCAD.Interface.Gtk import gtkprinting
from PythonCAD.Interface.Gtk import gtkactions
from PythonCAD.Generic import globals
from PythonCAD.Generic import fileio
from PythonCAD.Generic import imageio
from PythonCAD.Generic import tools
from PythonCAD.Generic import plotfile
from PythonCAD.Generic import text
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import dimension
from PythonCAD.Generic import extFormat

from PythonCAD.Generic.image import Image
from PythonCAD.Interface.Gtk import gtkdimprefs
from PythonCAD.Interface.Gtk import gtktextprefs
from PythonCAD.Interface.Gtk import gtkstyleprefs
from PythonCAD.Interface.Gtk import gtkDialog

from PythonCAD.Interface.Menu.basemenu import IBaseMenu

select_menu = [
    ('SelectAllPoints', 'point',_('_Points')),
    ('SelectAllSegments','segment',_('_Segments')),
    ('SelectAllCircles','circle',_('_Circles')),
    ('SelectAllArcs','arc',_('_Arcs')),
    ('SelectAllLeaders','leader',_('_Leaders')),
    ('SelectAllPolylines','polyline',_('_Polylines')),
    ('SelectAllChamfers','chamfer',_('Cha_mfers')),
    ('SelectAllFillets','fillet',_('_Fillets')),
    (None, None, None),
    ('SelectAllHCLines','hcline',_('_HCLines')),
    ('SelectAllVCLines','vcline',_('_VCLines')),
    ('SelectAllACLines','acline',_('_ACLines')),
    ('SelectAllCLines','cline',_('C_Lines')),
    ('SelectAllCCircles','ccircle',_('CCircles')),
    (None, None, None),
    ('SelectAllTextBlocks','textblock',_('TextBlocks')),
    (None, None, None),
    ('SelectAllLDims','linear_dimension',_('Linear Dim.')),
    ('SelectAllHDims','horizontal_dimension',_('Horiz. Dim.')),
    ('SelectAllVDims','vertical_dimension',_('Vert. Dim.')),
    ('SelectAllRDims','radial_dimension',_('Radial Dim.')),
    ('SelectAllADims','angular_dimension',_('Angular Dim.')),
    ]


#############################################################################
#
# callbacks for the menu items
#
#############################################################################

#------------------------------------------------------------
def _select_all_cb(menuitem, gtkimage):
    _group = gtkimage.getGroup('Edit')
    if _group is not None:
        _layer = gtkimage.image.getActiveLayer()
        for _action, _entity, _menuitem in select_menu:
            if _action is None: continue
            _act = _group.get_action(_action)
            if _act is not None:
                _act.set_property('sensitive',
                                  _layer.getEntityCount(_entity) > 0)

#------------------------------------------------------------
def edit_undo_cb(menuitem, gtkimage):
    gtkimage.image.doUndo()

#------------------------------------------------------------
def edit_redo_cb(menuitem, gtkimage):
    gtkimage.image.doRedo()

#------------------------------------------------------------
def edit_copy_cb(menuitem, gtkimage):
    for _obj in gtkimage.image.getSelectedObjects():
        if _obj.getParent() is not None:
            globals.selectobj.storeObject(_obj)

#------------------------------------------------------------
def edit_cut_cb(menuitem, gtkimage):
    _image = gtkimage.getImage()
    _image.startAction()
    try:
        for _obj in _image.getSelectedObjects():
            globals.selectobj.storeObject(_obj)
            #
            # check that the object parent is not None - if it
            # is then the object was deleted as a result of the
            # deletion of an earlier object (i.e. dimension)
            #
            _layer = _obj.getParent()
            if _layer is not None:
                _layer.delObject(_obj)
    finally:
        _image.endAction()

#------------------------------------------------------------
def edit_paste_cb(menuitem, gtkimage):
    _tool = tools.PasteTool()
    gtkimage.getImage().setTool(_tool)

#------------------------------------------------------------
def edit_select_cb(menuitem, gtkimage):
    _tool = tools.SelectTool()
    gtkimage.getImage().setTool(_tool)

#------------------------------------------------------------
def edit_deselect_cb(menuitem, gtkimage):
    _tool = tools.DeselectTool()
    gtkimage.getImage().setTool(_tool)

#------------------------------------------------------------
def select_all_objects_cb(menuitem, ge):
    _gtkimage, _entity = ge
    _image = _gtkimage.getImage()
    _active_layer = _image.getActiveLayer()
    _image.sendMessage('group_action_started')
    try:
        for _obj in _active_layer.getLayerEntities(_entity):
            _image.selectObject(_obj)
    finally:
        _image.sendMessage('group_action_ended')

def prefs_cb(menuitem, gtkimage):
    gtkprefs.prefs_dialog(gtkimage)

    
    
#############################################################################
#
# class IEditMenu
#
#############################################################################

class IEditMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IEditMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Edit')
        self.gtkimage.addGroup(group)
        action = gtk.Action('EditMenu', _('_Edit'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "EditMenu object.")


#----------------------------------------------------------------------------------------------
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        #
        _act = gtk.Action('Undo', _('_Undo'), None, gtk.STOCK_UNDO)
        _act.connect('activate', edit_undo_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, '<control>Z')
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('Redo', _('_Redo'), None, gtk.STOCK_REDO)
        _act.connect('activate', edit_redo_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, '<control><shift>Z')
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Cut', _('Cut'), None, gtk.STOCK_CUT)
        _act.connect('activate', edit_cut_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('Copy', _('Copy'), None, gtk.STOCK_COPY)
        _act.connect('activate', edit_copy_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('Paste', _('Paste'), None, gtk.STOCK_PASTE)
        _act.connect('activate', edit_paste_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('Select', _('_Select'), None, None)
        _act.connect('activate', edit_select_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('SelectAll', _('Select _All'), None, None)
        _act.connect('activate', _select_all_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _submenu = self.__create_select_all_menu(actiongroup, self.gtkimage)
        _item.set_submenu(_submenu)
        _menu.append(_item)
        #
        _act = gtk.Action('Deselect', _('_Deselect'), None, None)
        _act.connect('activate', edit_deselect_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        self.__sep_item2 = gtk.SeparatorMenuItem()
        self.__sep_item2.show()
        _menu.append(self.__sep_item2)
        #
        _act = gtk.Action('Prefs', _('_Preferences'), None, gtk.STOCK_PREFERENCES)
        _act.connect('activate', prefs_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        self.__prefs_menuitem = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(self.__prefs_menuitem)
        return _menu

    # properties
    def __get_prefs_sepitem(self):
        return self.__sep_item2

    GtkPrefsSepItem = property(__get_prefs_sepitem, None, None, "Preferences Seperator object.")

    def __get_prefs_menuitem(self):
        return self.__prefs_menuitem

    GtkPrefsMenuItem = property(__get_prefs_menuitem, None, None, "Preferences MenuItem object.")


    #############################################################################
    #  Edit -> select all submenu
    #############################################################################
    def __create_select_all_menu(self, actiongroup, gtkimage):
        _accel = gtkimage.accel
        _menu = gtk.Menu()
        for _action, _entity, _menuitem in select_menu:
            if _action is not None:
                _act = gtk.Action(_action, _menuitem, None, None)
                _act.connect('activate', select_all_objects_cb,
                             (gtkimage, _entity))
                _act.set_accel_group(_accel)
                actiongroup.add_action(_act)
                _menu.append(_act.create_menu_item())
            else:
                _item = gtk.SeparatorMenuItem()
                _item.show()
                _menu.append(_item)
        return _menu
        

#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem):
        _group = self.gtkimage.getGroup('Edit')
        if _group is not None:
            _image = self.gtkimage.getImage()
            _act = _group.get_action('Undo')
            if _act is not None:
                _act.set_property('sensitive', _image.canUndo())
            _act = _group.get_action('Redo')
            if _act is not None:
                _act.set_property('sensitive', _image.canRedo())
            _act = _group.get_action('Cut')
            if _act is not None:
                _act.set_property('sensitive', _image.hasSelection())
            _act = _group.get_action('Copy')
            if _act is not None:
                _act.set_property('sensitive', _image.hasSelection())
            _act = _group.get_action('Paste')
            if _act is not None:
                _act.set_property('sensitive', globals.selectobj.hasObjects())
            _act = _group.get_action('Select')
            if _act is not None:
                _act.set_property('sensitive', _image.getActiveLayer().hasEntities())
            _act = _group.get_action('SelectAll')
            if _act is not None:
                _act.set_property('sensitive', _image.getActiveLayer().hasEntities())
            _act = _group.get_action('Deselect')
            if _act is not None:
                _act.set_property('sensitive', _image.hasSelection())
