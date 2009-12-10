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

import os
import stat
import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms


#from PythonCAD.Interface.Gtk.gtkimage import GTKImage

from PythonCAD.Interface.Gtk import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
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
from PythonCAD.Interface.Gtk import gtkdialog as gtkDialog

from PythonCAD.Interface.Menu.basemenu import IBaseMenu
from PythonCAD.Interface.Menu.basemenu import error_dialog

#############################################################################
#
# local functions
#
#############################################################################


#------------------------------------------------------------
def _get_filename_and_save(gtkimage, fname=None):
    """
        make the save as operation
    """
    _window = gtkimage.getWindow()
    if fname is None:
       fname = _window.get_title()
    _dialog = gtk.FileChooserDialog(title=_('Save As ...'),
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK),
                action=gtk.FILE_CHOOSER_ACTION_SAVE)
    
    _filter = gtk.FileFilter()
    _filter.set_name("Pythoncad")
    _filter.add_mime_type("pythoncad/xml.gz")
    _filter.add_pattern("*.xml.gz")
    _dialog.add_filter(_filter)
       
    _filter = gtk.FileFilter()
    _filter.set_name("Autocad")
    _filter.add_mime_type("autocad/dxf")
    _filter.add_pattern("*.dxf")
    _dialog.add_filter(_filter)

    _filter = gtk.FileFilter()
    _filter.set_name("All files")
    _filter.add_pattern("*")
    _dialog.add_filter(_filter)
    
    _dialog.set_filename(fname)
    _response = _dialog.run()
    fname = _dialog.get_filename()
    _dialog.destroy()
    
    if _response == gtk.RESPONSE_OK:
        if askForOverWrite(gtkimage,fname):
            if fname.endswith('.xml.gz'):
                _save_p_file(gtkimage,fname)
            elif fname.endswith('.dxf'):
                _save_extFormats(gtkimage,fname)
            else:
                fname=fname+".xml.gz"
                _save_p_file(gtkimage,fname)

def _save_p_file(gtkimage,fname):
    """
        save the active file and manage the errors
    """
    gtkimage.image.setFilename(fname)
    _window = gtkimage.getWindow()
    _window.set_title(os.path.basename(fname))
    try:
        _save_file(gtkimage, fname)
    except (IOError, OSError), _e:
        _errmsg = "Error saving '%s' : %s'" % (fname, _e)
        error_dialog(gtkimage, _errmsg)
    except StandardError, _e:
        _errmsg = "Non-system error saving '%s' : %s'" % (fname, _e)
        error_dialog(gtkimage, _errmsg)


def askForOverWrite(gtkimage,fname):
    """
        popUp a menu for overwriting the exsisting file
    """
    if os.path.exists(fname):    
        _msg=_("File " + str(fname) + " Olredy Exsist /n OverWrite ?")
        _res=gtkDialog._yesno_dialog(gtkimage,_msg)
        if _res==gtk.RESPONSE_ACCEPT:
            return True
        else:
            return False
    else:
        return True
    
#------------------------------------------------------------
def _save_file(gtkimage, filename):
    _image = gtkimage.getImage()
    _abs = os.path.abspath(filename)
    _bname = os.path.basename(_abs)
    if _bname.endswith('.gz'):
        _bname = _bname[:-3]
    _newfile = _abs + '.new'
    _handle = fileio.CompFile(_newfile, "w", truename=_bname)
    try:
        imageio.save_image(_image, _handle)
    finally:
        _handle.close()
    _backup = _abs + '~'
    if os.path.exists(_backup):
        os.unlink(_backup)
    _mode = None
    if os.path.exists(_abs):
        _st = os.stat(_abs)
        _mode = stat.S_IMODE(_st.st_mode)
        os.rename(_abs, _backup)
    try:
        os.rename(_newfile, _abs)
    except:
        os.rename(_backup, _abs)
        raise
    if _mode is not None and hasattr(os, 'chmod'):
        os.chmod(_abs, _mode)
    if _image.getFilename() is None:
        _image.setFilename(_abs)
        
def _save_extFormats(gtkimage,fname):
    """
        save the current file as external formats 
    """
    exf=extFormat.ExtFormat(gtkimage)
    try:
        exf.saveFile(fname)  
    except (IOError, OSError), _e:
        _errmsg = "Error saving '%s' : %s'" % (fname, _e)
        error_dialog(gtkimage, _errmsg)
    except StandardError, _e:
        _errmsg = "Non-system error saving '%s' : %s'" % (fname, _e)
        error_dialog(gtkimage, _errmsg)       
#############################################################################
#
# callbacks for the menu items
#
#############################################################################

#----------------------------------------------------------------------------------------------
def file_new_cb(menuitem, data=None):
    _image = Image()
    _gtkimage = GTKImage(_image)
    _background = globals.prefs['BACKGROUND_COLOR']
    _image.setOption('BACKGROUND_COLOR', _background)
    globals.imagelist.append(_image)
    _gtkimage.window.show_all()


#----------------------------------------------------------------------------------------------
def file_open_cb(menuitem, gtkimage):
    _open = False
    _fname = None
    _dialog = gtk.FileChooserDialog(title=_('Open File ...'),
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK),
                action=gtk.FILE_CHOOSER_ACTION_OPEN)
    while not _open:
        _response = _dialog.run()
        if _response == gtk.RESPONSE_OK:
            _fname = _dialog.get_filename()
            if os.path.isdir(_fname):
                _fname += "/"
                _dialog.set_filename(_fname)
                _response = _dialog.run()
            else:
                _open = True
        else:
            break
    _dialog.destroy()
    if _open:
        _image = Image()
        try:
            _handle = fileio.CompFile(_fname, "r")
            try:
                imageio.load_image(_image, _handle)
            finally:
                _handle.close()
        except (IOError, OSError), e:
            _errmsg = "Error opening '%s' : %s'" % (_fname, e)
            error_dialog(gtkimage, _errmsg)
            return
        except StandardError, e:
            _errmsg = "Non-system error opening '%s' : %s'" % (_fname, e)
            error_dialog(gtkimage, _errmsg)
            return
        
        # TODO: fix this
        from PythonCAD.Interface.Gtk.gtkimage import GTKImage
        globals.imagelist.append(_image)
        _image.setFilename(_fname)
        _gtkimage = GTKImage(_image)
        _window = _gtkimage.getWindow()
        _window.set_title(os.path.basename(_fname))
        _window.show_all()
        _gtkimage.fitImage()

#----------------------------------------------------------------------------------------------
def file_inport_cb(menuitem, gtkimage):
    """
        Temporary Call back for testing the import of a dxfDwgFile
    """
    _open = False
    _fname = None
    _dialog = gtk.FileChooserDialog(title=_('Import File ...'),
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK),
                action=gtk.FILE_CHOOSER_ACTION_OPEN)
    # _dialog.hide_fileop_buttons()
    while not _open:
        _response = _dialog.run()
        if _response == gtk.RESPONSE_OK:
            _fname = _dialog.get_filename()
            if os.path.isdir(_fname):
                _fname += "/"
                _dialog.set_filename(_fname)
                _response = _dialog.run()
            else:
                _open = True
        else:
            break
    _dialog.destroy()
    if _open:
        try:
            exf=extFormat.ExtFormat(gtkimage)
            exf.openFile(_fname)
        except (IOError, OSError), e:
            _errmsg = "Error opening '%s' : %s'" % (_fname, e)
            gtkDialog._error_dialog(gtkimage, _errmsg)
            return
        except StandardError, e:
            _errmsg = "Non-system error opening '%s' : %s'" % (_fname, e)
            gtkDialog._error_dialog(gtkimage, _errmsg)
            return
        
#----------------------------------------------------------------------------------------------
def file_close_cb(menuitem, gtkimage):
    """
        Close the application
    """
    for _i in xrange(len(globals.imagelist)):
        _image = globals.imagelist[_i]
        if _image is gtkimage.image:
            if _image.isSaved()==False:
                print "ask for saving" #implement it matteo boscolo
            _log = _image.getLog()
            if _log is not None:
                _log.detatch()
            del globals.imagelist[_i]
            gtkimage.window.destroy()
            if not len(globals.imagelist):
                gtk.main_quit()
            break


#------------------------------------------------------------
def file_save_cb(menuitem, gtkimage):
    _fname = gtkimage.image.getFilename()
    if _fname is None:
        _get_filename_and_save(gtkimage)
    else:
        try:
            _save_file(gtkimage, _fname)
        except (IOError, OSError), _e:
            _errmsg = "Error saving '%s' : %s'" % (_fname, _e)
            error_dialog(gtkimage, _errmsg)
        except StandardError, _e:
            _errmsg = "Non-system error saving '%s' : %s'" % (_fname, _e)
            error_dialog(gtkimage, _errmsg)


#------------------------------------------------------------
def file_save_as_cb(menuitem, gtkimage):
    _fname = gtkimage.image.getFilename()
    if _fname is None:
        _fname = gtkimage.getWindow().get_title()
    _get_filename_and_save(gtkimage, _fname)


#------------------------------------------------------------
def file_save_layer_cb(menuitem, gtkimage):
    # print "called file_save_layer_cb()"
    active = gtkimage.image.getActiveLayer()
    layer_name = active.getName()
    dialog = gtk.FileSelection("Save Layer As ...")
    dialog.set_transient_for(gtkimage.getWindow())
    dialog.set_filename(layer_name)
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        fname = dialog.get_filename()
        print "Saving layer as '%s'" % fname
        #
        # fixme - add the layer saving code ...
        #
    dialog.destroy()


#------------------------------------------------------------
def file_print_screen_cb(menuitem, gtkimage):
    _plot = plotfile.Plot(gtkimage.image)
    _xmin, _ymin, _xmax, _ymax = gtkimage.getView()
    _plot.setBounds(_xmin, _ymin, _xmax, _ymax)
    gtkprinting.print_dialog(gtkimage, _plot)


#------------------------------------------------------------
def file_print_cb(menuitem, gtkimage):
    _tool = tools.PlotTool()
    gtkimage.getImage().setTool(_tool)


#------------------------------------------------------------
def file_quit_cb(menuitem, gtkimage):
    _image=gtkimage.getImage()
    if _image.isSaved() == False:
        _res=gtkDialog._yesno_dialog(gtkimage, "File Unsaved, Wold You Like To Save ?")
        if gtk.RESPONSE_ACCEPT == _res:
            file_save_cb(None, gtkimage)
    gtk.main_quit()



#############################################################################
#
# class IFileMenu
#
#############################################################################

class IFileMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IFileMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('File')
        self.gtkimage.addGroup(group)
        action = gtk.Action('FileMenu', _('_File'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb, self.gtkimage)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "FileMenu object.")


#----------------------------------------------------------------------------------------------
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        #
        # Item File-New
        #
        _act = gtk.Action('New', _('_New'), None, gtk.STOCK_NEW)
        _act.connect('activate', file_new_cb)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item File-Open
        #
        _act = gtk.Action('Open', _('_Open'), None, gtk.STOCK_OPEN)
        _act.connect('activate', file_open_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item File-Inport
        #
        _act = gtk.Action('Inport', _('_Inport'), None, gtk.STOCK_OPEN)
        _act.connect('activate', file_inport_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item File-Close
        #
        _act = gtk.Action('Close', _('_Close'), None, gtk.STOCK_CLOSE)
        _act.connect('activate', file_close_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item Separator
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        # Item File-Save
        #
        _act = gtk.Action('Save', _('_Save'), None, gtk.STOCK_SAVE)
        _act.connect('activate', file_save_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item File-SaveAs
        #
        _act = gtk.Action('SaveAs', _('Save _As ...'), None, None)
        _act.connect('activate', file_save_as_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        # Item File-SaveLayerAs
        #
        _act = gtk.Action('SaveLayerAs', _('Save _Layer As ...'), None, None)
        _act.connect('activate', file_save_layer_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        # Item Separator
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        # Item File-PrintScreen
        #
        _act = gtk.Action('PrintScreen', _('Print Screen'), None, None)
        _act.connect('activate', file_print_screen_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        # Item File-Print
        #
        _act = gtk.Action('Print', _('_Print'), None, gtk.STOCK_PRINT)
        _act.connect('activate', file_print_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, '<control>P')
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        # Item File-Quit
        #
        _act = gtk.Action('Quit', _('_Quit'), None, gtk.STOCK_QUIT)
        _act.connect('activate', file_quit_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        self.__quit_menuitem = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(self.__quit_menuitem)
        #
        return _menu

    # properties
    def __get_quit_menuitem(self):
        return self.__quit_menuitem

    GtkQuitMenuItem = property(__get_quit_menuitem, None, None, "Quit MenuItem object.")


#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem, gtkimage):
        _group = gtkimage.getGroup('File')
        if _group is not None:
            _act = _group.get_action('SaveLayerAs')
            if _act is not None:
                _act.set_property('sensitive', False)


