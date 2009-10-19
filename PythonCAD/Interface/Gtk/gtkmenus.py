#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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

################################################################
#
# This file contains the GTK Menu building code
#
################################################################

import os
import stat
import sys

_debug = False

if _debug:
    try:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
    except ImportError:
        pass

import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms

from PythonCAD.Interface.Gtk.gtkimage import GTKImage
from PythonCAD.Interface.Gtk import gtkentities
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

if not hasattr(gtk, 'Action'):
    gtk.Action = gtkactions.stdAction
    gtk.ActionGroup = gtkactions.stdActionGroup


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
def file_new_cb(menuitem, data=None):
    _image = Image()
    _gtkimage = GTKImage(_image)
    _background = globals.prefs['BACKGROUND_COLOR']
    _image.setOption('BACKGROUND_COLOR', _background)
    globals.imagelist.append(_image)
    _gtkimage.window.show_all()

#------------------------------------------------------------
def file_open_cb(menuitem, gtkimage):
    _open = False
    _fname = None
    _dialog = gtk.FileSelection(_('Open File ...'))
    _dialog.set_transient_for(gtkimage.getWindow())
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
        _image = Image()
        try:
            _handle = fileio.CompFile(_fname, "r")
            try:
                imageio.load_image(_image, _handle)
            finally:
                _handle.close()
        except (IOError, OSError), e:
            _errmsg = "Error opening '%s' : %s'" % (_fname, e)
            _error_dialog(gtkimage, _errmsg)
            return
        except StandardError, e:
            _errmsg = "Non-system error opening '%s' : %s'" % (_fname, e)
            _error_dialog(gtkimage, _errmsg)
            return
        globals.imagelist.append(_image)
        _image.setFilename(_fname)
        _gtkimage = GTKImage(_image)
        _window = _gtkimage.getWindow()
        _window.set_title(os.path.basename(_fname))
        _window.show_all()
        _gtkimage.fitImage()
#------------------------------------------------------------
def file_inport_cb(menuitem, gtkimage):
    """
        Temporary Call back for testing the import of a dxfDwgFile
    """
    _open = False
    _fname = None
    _dialog = gtk.FileSelection(_('Import File ...'))
    _dialog.set_transient_for(gtkimage.getWindow())
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
            exf.Open(_fname)
        except (IOError, OSError), e:
            _errmsg = "Error opening '%s' : %s'" % (_fname, e)
            _error_dialog(gtkimage, _errmsg)
            return     
        except StandardError, e:
            _errmsg = "Non-system error opening '%s' : %s'" % (_fname, e)
            _error_dialog(gtkimage, _errmsg)
            return
#------------------------------------------------------------
def file_close_cb(menuitem, gtkimage):
    for _i in xrange(len(globals.imagelist)):
        _image = globals.imagelist[_i]
        if _image is gtkimage.image:
            _log = _image.getLog()
            if _log is not None:
                _log.detatch()
            del globals.imagelist[_i]
            gtkimage.window.destroy()
            if not len(globals.imagelist):
                gtk.main_quit()
            break

#------------------------------------------------------------
def _error_dialog(gtkimage, errmsg):
    _window = gtkimage.getWindow()
    _dialog = gtk.MessageDialog( _window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 gtk.MESSAGE_ERROR,
                                 gtk.BUTTONS_CLOSE,
                                 errmsg)
    _dialog.run()
    _dialog.destroy()

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

#------------------------------------------------------------
def _writecopy(src, dst):
    if sys.platform == 'win32':
        _rmode = 'rb'
        _wmode = 'wb'
    else:
        _rmode = 'r'
        _wmode = 'w'
    _from = file(src, _rmode)
    try:
        _to = file(dst, _wmode)
        try:
            while True:
                _data = _from.read(8192)
                if _data == '':
                    break
                _to.write(_data)
        finally:
            _to.close()
    finally:
        _from.close()

#------------------------------------------------------------
def _save_file_by_copy(gtkimage, filename):
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
    # print "saved new file %s" % _newfile
    _backup = _abs + '~'
    if os.path.exists(_abs):
        _writecopy(_abs, _backup)
        # print "writing existing to backup %s" % _backup
    try:
        _writecopy(_newfile, _abs)
    except:
        _writecopy(_backup, _abs)
        raise
    # print "writing new file to filename %s" % _abs
    os.unlink(_newfile)
    # print "removing temporary new file %s" % _abs
    if _image.getFilename() is None:
        _image.setFilename(_abs)
    
#------------------------------------------------------------
def _get_filename_and_save(gtkimage, fname=None):
    _window = gtkimage.getWindow()
    _fname = fname
    if _fname is None:
        _fname = _window.get_title()
    _fname = _window.get_title()
    _dialog = gtk.FileSelection(_('Save As ...'))
    _dialog.set_transient_for(gtkimage.getWindow())
    _dialog.set_filename(_fname)
    _response = _dialog.run()
    _save = False
    if _response == gtk.RESPONSE_OK:
        _save = True
        _fname = _dialog.get_filename()
        if _fname == "":
            _fname = 'Untitled.xml'
        if not _fname.endswith('.xml.gz'):
            if not _fname.endswith('.xml'):
                _fname = _fname + '.xml'
        #
        # if the filename already exists see that the user
        # really wants to overwrite it ...
        #
        # test for the filename + '.gz'
        #
        if _fname.endswith('.xml.gz'):
            _gzfile = _fname
        else:
            _gzfile = _fname + '.gz'
        if os.path.exists(_gzfile):
            _save = False
            _dialog2 = gtk.Dialog(_('Overwrite Existing File'), _window,
                                  gtk.DIALOG_MODAL,
                                  (gtk.STOCK_OK, gtk.RESPONSE_OK,
                                   gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            _hbox = gtk.HBox(False, 10)
            _hbox.set_border_width(10)
            _dialog2.vbox.pack_start(_hbox, False, False, 0)
            _stock = gtk.image_new_from_stock(gtk.STOCK_DIALOG_QUESTION,
                                              gtk.ICON_SIZE_DIALOG)
            _hbox.pack_start(_stock, False, False, 0)
            _label = gtk.Label(_('File already exists. Delete it?'))
            _hbox.pack_start(_label, False, False, 0)
            _dialog2.show_all()
            _response = _dialog2.run()
            if _response == gtk.RESPONSE_OK:
                _save = True
            _dialog2.destroy()
    _dialog.destroy()
    if _save:
        # print "name: " + _gzfile
        gtkimage.image.setFilename(_gzfile)
        _window.set_title(os.path.basename(_gzfile))
        try:
            _save_file(gtkimage, _gzfile)
        except (IOError, OSError), _e:
            _errmsg = "Error saving '%s' : %s'" % (_gzfile, _e)
            _error_dialog(gtkimage, _errmsg)
        except StandardError, _e:
            _errmsg = "Non-system error saving '%s' : %s'" % (_gzfile, _e)
            _error_dialog(gtkimage, _errmsg)

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
            _error_dialog(gtkimage, _errmsg)
        except StandardError, _e:
            _errmsg = "Non-system error saving '%s' : %s'" % (_fname, _e)
            _error_dialog(gtkimage, _errmsg)

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
    gtk.main_quit()

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
    gtkimage.redraw()

#------------------------------------------------------------
def edit_redo_cb(menuitem, gtkimage):
    gtkimage.image.doRedo()
    gtkimage.redraw()

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

def units_cb(menuitem, gtkimage):
    gtkentities.set_units_dialog(gtkimage)
    
def toggle_cb(menuitem, gtkimage):
    gtkentities.set_toggle_dialog(gtkimage)
    
def prefs_cb(menuitem, gtkimage):
    gtkprefs.prefs_dialog(gtkimage)

def colors_cb(menuitem, gtkimage):
    gtkentities.set_colors_dialog(gtkimage)

def sizes_cb(menuitem, gtkimage):
    gtkentities.set_sizes_dialog(gtkimage)
    
def style_cb(menuitem, gtkimage):
    gtkstyleprefs.style_dialog(gtkimage, globals.prefs['STYLES'],
                               globals.prefs['LINETYPES'])
    
def textstyle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    gtktextprefs.textstyle_dialog(gtkimage, globals.prefs['TEXTSTYLES'])

def dimstyle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    gtkdimprefs.dimstyle_dialog(gtkimage, globals.prefs['DIMSTYLES'])

def draw_point_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PointTool()
    gtkimage.getImage().setTool(_tool)

def draw_segment_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.SegmentTool()
    gtkimage.getImage().setTool(_tool)

def draw_rectangle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.RectangleTool()
    gtkimage.getImage().setTool(_tool)

def draw_circle_center_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_circle_tp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_arc_center_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ArcTool()
    gtkimage.getImage().setTool(_tool)

def draw_hcl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_vcl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_acl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ACLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_cl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_perpendicular_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PerpendicularCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TangentCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_two_ccircles_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CCircleTangentLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_poffset_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ParallelOffsetTool()
    gtkimage.getImage().setTool(_tool)

def draw_ccirc_cp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_ccirc_tp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_single_conobj_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TangentCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_two_conobjs_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointTangentCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_chamfer_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ChamferTool()
    gtkimage.getImage().setTool(_tool)

def draw_fillet_cb(menuitem, gtkimage):
    """
        Start Point fillet comand
    """
    gtkimage.activateSnap()
    _tool = tools.FilletTool()
    gtkimage.getImage().setTool(_tool)
def draw_fillet_two_cb(menuitem, gtkimage):
    """
        Start two line fillet comand
    """
    _tool = tools.FilletTwoLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_leader_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.LeaderTool()
    gtkimage.getImage().setTool(_tool)

def draw_polyline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PolylineTool()
    gtkimage.getImage().setTool(_tool)

def _get_polygon_side_count(gtkimage):
    gtkimage.activateSnap()
    _sides = 0
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Polygon Sides'), _window,
                         gtk.DIALOG_MODAL,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 10)
    _hbox.set_border_width(10)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _stock = gtk.image_new_from_stock(gtk.STOCK_DIALOG_QUESTION,
                                      gtk.ICON_SIZE_DIALOG)
    _hbox.pack_start(_stock, False, False, 0)
    _label = gtk.Label(_('Number of sides:'))
    _hbox.pack_start(_label, False, False, 0)
    _adj = gtk.Adjustment(3, 3, 3600, 1, 1, 1) # arbitrary max ...
    _sb = gtk.SpinButton(_adj)
    _sb.set_numeric(True)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _sides = _sb.get_value()
    _dialog.destroy()
    return _sides

def draw_polygon_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _sides = _get_polygon_side_count(gtkimage)
    if _sides > 0:
        _tool = tools.PolygonTool()
        _tool.setSideCount(_sides)
        gtkimage.getImage().setTool(_tool)

def draw_ext_polygon_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _sides = _get_polygon_side_count(gtkimage)
    if _sides > 0:
        _tool = tools.PolygonTool()
        _tool.setExternal()
        _tool.setSideCount(_sides)
        gtkimage.getImage().setTool(_tool)

def draw_set_style_cb(menuitem, gtkimage):
    gtkentities.set_active_style(gtkimage)

def draw_set_linetype_cb(menuitem, gtkimage):
    gtkentities.set_active_linetype(gtkimage)

def draw_set_color_cb(menuitem, gtkimage):
    gtkentities.set_active_color(gtkimage)

def draw_set_thickness_cb(menuitem, gtkimage):
    gtkentities.set_line_thickness(gtkimage)

def draw_text_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _text = gtktext.text_add_dialog(gtkimage)
    if _text is not None:
        _tool = tools.TextTool()
        _tool.setText(_text)
        gtkimage.getImage().setTool(_tool)

def move_horizontal_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HorizontalMoveTool()
    gtkimage.getImage().setTool(_tool)

def move_vertical_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VerticalMoveTool()
    gtkimage.getImage().setTool(_tool)

def move_twopoint_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.MoveTool()
    gtkimage.getImage().setTool(_tool)

def stretch_horiz_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HorizontalStretchTool()
    gtkimage.getImage().setTool(_tool)

def stretch_vert_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VerticalStretchTool()
    gtkimage.getImage().setTool(_tool)

def stretch_twopoint_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.StretchTool()
    gtkimage.getImage().setTool(_tool)

def transfer_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TransferTool()
    gtkimage.getImage().setTool(_tool)

def rotate_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.RotateTool()
    gtkimage.getImage().setTool(_tool)
    
def split_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.SplitTool()
    gtkimage.getImage().setTool(_tool)

def mirror_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.MirrorTool()
    gtkimage.getImage().setTool(_tool)

def delete_cb(menuitem, gtkimage):
    _tool = tools.DeleteTool()
    gtkimage.getImage().setTool(_tool)

def change_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_style_dialog(gtkimage)
    if _st is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setStyle')
        _tool.setValue(_st)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_style_init(gtkimage)

def change_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_color_dialog(gtkimage)
    if _color is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_color_init(gtkimage)

def change_linetype_cb(menuitem, gtkimage):
    _lt = gtkmodify.change_linetype_dialog(gtkimage)
    if _lt is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setLinetype')
        _tool.setValue(_lt)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_linetype_init(gtkimage)

def change_thickness_cb(menuitem, gtkimage):
    _t = gtkmodify.change_thickness_dialog(gtkimage)
    if _t is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setThickness')
        _tool.setValue(_t)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_thickness_init(gtkimage)

def change_textblock_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'FONT_STYLE')
    if _st is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setStyle')
        _tool.setValue(_st)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_style_init(gtkimage)

def change_textblock_weight_cb(menuitem, gtkimage):
    _w = gtkmodify.change_textblock_weight_dialog(gtkimage, 'FONT_WEIGHT')
    if _w is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setWeight')
        _tool.setValue(_w)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_weight_init(gtkimage)

def change_textblock_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'TEXT_ALIGNMENT')
    if _align is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setAlignment')
        _tool.setValue(_align)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_alignment_init(gtkimage)

def change_textblock_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'TEXT_SIZE')
    if _size is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setSize')
        _tool.setValue(_size)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_size_init(gtkimage)

def change_textblock_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'FONT_FAMILY')
    if _family is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setFamily')
        _tool.setValue(_family)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_family_init(gtkimage)

def change_textblock_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'FONT_COLOR')
    if _color is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_color_init(gtkimage)

def change_dim_endpoint_cb(menuitem, gtkimage):
    _et = gtkmodify.change_dim_endpoint_dialog(gtkimage)
    if _et is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setEndpointType')
        _tool.setValue(_et)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_endpoint_init(gtkimage)

def change_dim_endpoint_size_cb(menuitem, gtkimage):
    _es = gtkmodify.change_dim_endpoint_size_dialog(gtkimage)
    if _es is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setEndpointSize')
        _tool.setValue(_es)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_endpoint_size_init(gtkimage)

def change_dim_offset_cb(menuitem, gtkimage):
    _offset = gtkmodify.change_dim_offset_dialog(gtkimage)
    if _offset is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setOffset')
        _tool.setValue(_offset)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_offset_init(gtkimage)

def change_dim_extension_cb(menuitem, gtkimage):
    _ext = gtkmodify.change_dim_extension_dialog(gtkimage)
    if _ext is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setExtension')
        _tool.setValue(_ext)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_extension_init(gtkimage)

def change_dim_dual_mode_cb(menuitem, gtkimage):
    _ddm = gtkmodify.change_dim_dual_mode_dialog(gtkimage)
    if _ddm is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setDualDimMode')
        _tool.setValue(_ddm)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_dual_mode_init(gtkimage)

def change_dim_dual_mode_offset_cb(menuitem, gtkimage):
    _dmo = gtkmodify.change_dim_dual_mode_offset_dialog(gtkimage)
    if _dmo is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setDualModeOffset')
        _tool.setValue(_dmo)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_dual_mode_offset_init(gtkimage)

def change_dim_thickness_cb(menuitem, gtkimage):
    _t = gtkmodify.change_dim_thickness_dialog(gtkimage)
    if _t is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setThickness')
        _tool.setValue(_t)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_thickness_init(gtkimage)

def change_dim_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_dim_color_dialog(gtkimage)
    if _color is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_color_init(gtkimage)

def _change_dimstring_style_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setStyle')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_style_init(gtkimage)

def change_dim_primary_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'DIM_PRIMARY_FONT_STYLE')
    if _st is not None:
        _change_dimstring_style_cb(gtkimage, _st, True)

def change_dim_secondary_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'DIM_SECONDARY_FONT_STYLE')
    if _st is not None:
        _change_dimstring_style_cb(gtkimage, _st, False)

def _change_dimstring_family_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setFamily')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_family_init(gtkimage)

def change_dim_primary_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'DIM_PRIMARY_FONT_FAMILY')
    if _family is not None:
        _change_dimstring_family_cb(gtkimage, _family, True)

def change_dim_secondary_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'DIM_SECONDARY_FONT_FAMILY')
    if _family is not None:
        _change_dimstring_family_cb(gtkimage, _family, False)

def _change_dimstring_weight_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setWeight')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_weight_init(gtkimage)

def change_dim_primary_weight_cb(menuitem, gtkimage):
    _weight = gtkmodify.change_textblock_weight_dialog(gtkimage, 'DIM_PRIMARY_FONT_WEIGHT')
    if _weight is not None:
        _change_dimstring_weight_cb(gtkimage, _weight, True)

def change_dim_secondary_weight_cb(menuitem, gtkimage):
    _weight = gtkmodify.change_textblock_weight_dialog(gtkimage, 'DIM_SECONDARY_FONT_WEIGHT')
    if _weight is not None:
        _change_dimstring_weight_cb(gtkimage, _weight, False)

def _change_dimstring_size_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setSize')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_size_init(gtkimage)

def change_dim_primary_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'DIM_PRIMARY_TEXT_SIZE')
    if _size is not None:
        _change_dimstring_size_cb(gtkimage, _size, True)

def change_dim_secondary_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'DIM_SECONDARY_TEXT_SIZE')
    if _size is not None:
        _change_dimstring_size_cb(gtkimage, _size, False)

def _change_dimstring_color_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setColor')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_color_init(gtkimage)

def change_dim_primary_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'DIM_PRIMARY_FONT_COLOR')
    if _color is not None:
        _change_dimstring_color_cb(gtkimage, _color, True)

def change_dim_secondary_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'DIM_SECONDARY_FONT_COLOR')
    if _color is not None:
        _change_dimstring_color_cb(gtkimage, _color, False)

def _change_dimstring_alignment_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setAlignment')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_alignment_init(gtkimage)

def change_dim_primary_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'DIM_PRIMARY_TEXT_ALIGNMENT')
    if _align is not None:
        _change_dimstring_alignment_cb(gtkimage, _align, True)

def change_dim_secondary_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'DIM_SECONDARY_TEXT_ALIGNMENT')
    if _align is not None:
        _change_dimstring_alignment_cb(gtkimage, _align, False)

def _change_dimstring_prefix_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrefix')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)

def change_ldim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_ldimstr_prefix_init(gtkimage)

def change_ldim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_ldimstr_prefix_init(gtkimage)

def change_rdim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'RADIAL_DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_rdimstr_prefix_init(gtkimage)

def change_rdim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'RADIAL_DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_rdimstr_prefix_init(gtkimage)

def change_adim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'ANGULAR_DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_adimstr_prefix_init(gtkimage)

def change_adim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'ANGULAR_DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_adimstr_prefix_init(gtkimage)

def _change_dimstring_suffix_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setSuffix')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)

def change_ldim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_ldimstr_suffix_init(gtkimage)

def change_ldim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_ldimstr_suffix_init(gtkimage)

def change_rdim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'RADIAL_DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_rdimstr_suffix_init(gtkimage)

def change_rdim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'RADIAL_DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_rdimstr_suffix_init(gtkimage)

def change_adim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'ANGULAR_DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_adimstr_suffix_init(gtkimage)

def change_adim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'ANGULAR_DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_adimstr_suffix_init(gtkimage)

def _change_dimstring_precision_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrecision')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_precision_init(gtkimage)

def change_dim_primary_precision_cb(menuitem, gtkimage):
    _prec = gtkmodify.change_dimstr_precision_dialog(gtkimage, 'DIM_PRIMARY_PRECISION')
    if _prec is not None:
        _change_dimstring_precision_cb(gtkimage, _prec, True)

def change_dim_secondary_precision_cb(menuitem, gtkimage):
    _prec = gtkmodify.change_dimstr_precision_dialog(gtkimage, 'DIM_SECONDARY_PRECISION')
    if _prec is not None:
        _change_dimstring_precision_cb(gtkimage, _prec, False)

def _change_dimstring_units_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setUnits')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_units_init(gtkimage)

def change_dim_primary_units_cb(menuitem, gtkimage):
    _unit = gtkmodify.change_dimstr_units_dialog(gtkimage, 'DIM_PRIMARY_UNITS')
    if _unit is not None:
        _change_dimstring_units_cb(gtkimage, _unit, True)

def change_dim_secondary_units_cb(menuitem, gtkimage):
    _unit = gtkmodify.change_dimstr_units_dialog(gtkimage, 'DIM_SECONDARY_UNITS')
    if _unit is not None:
        _change_dimstring_units_cb(gtkimage, _unit, False)

def _change_dimstring_print_zero_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrintZero')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_print_zero_init(gtkimage)

def change_dim_primary_print_zero_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_zero_dialog(gtkimage, 'DIM_PRIMARY_LEADING_ZERO')
    if _flag is not None:
        _change_dimstring_print_zero_cb(gtkimage, _flag, True)

def change_dim_secondary_print_zero_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_zero_dialog(gtkimage, 'DIM_SECONDARY_LEADING_ZERO')
    if _flag is not None:
        _change_dimstring_print_zero_cb(gtkimage, _flag, False)

def _change_dimstring_print_decimal_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrintDecimal')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_print_decimal_init(gtkimage)

def change_dim_primary_print_decimal_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_decimal_dialog(gtkimage, 'DIM_PRIMARY_TRAILING_DECIMAL')
    if _flag is not None:
        _change_dimstring_print_decimal_cb(gtkimage, _flag, True)

def change_dim_secondary_print_decimal_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_decimal_dialog(gtkimage, 'DIM_SECONDARY_TRAILING_DECIMAL')
    if _flag is not None:
        _change_dimstring_print_decimal_cb(gtkimage, _flag, False)

def change_rdim_dia_mode_cb(menuitem, gtkimage):
    _tool = tools.EditDimensionTool()
    _tool.setObjtype(dimension.RadialDimension)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_rdim_dia_mode_init(gtkimage)

def change_adim_invert_cb(menuitem, gtkimage):
    _tool = tools.EditDimensionTool()
    _tool.setObjtype(dimension.AngularDimension)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.invert_adim_init(gtkimage)
    
def zoom_cb(menuitem, gtkimage):
    _tool = tools.ZoomTool()
    gtkimage.getImage().setTool(_tool)

def zoom_in_cb(menuitem, gtkimage):
    #_xmin, _ymin, _xmax, _ymax = gtkimage.getView()
    #_scale = gtkimage.getUnitsPerPixel()
    #_xdiff = abs(_xmax - _xmin)
    #_ydiff = abs(_ymax - _ymin)
    #_xmin = (_xmin + _xmax)/2.0 - _xdiff/4.0
    #_ymin = (_ymin + _ymax)/2.0 - _ydiff/4.0
    #gtkimage.setView(_xmin, _ymin, (_scale/2.0))
    ActiveScale = gtkimage.getUnitsPerPixel()
    ActiveScale = ActiveScale*0.5 #This Value here could be a global variable to put in the application option
    gtkimage.ZoomScale(ActiveScale)
    
def zoom_out_cb(menuitem, gtkimage):
    #_xmin, _ymin, _xmax, _ymax = gtkimage.getView()
    #_scale = gtkimage.getUnitsPerPixel()
    #_xdiff = abs(_xmax - _xmin)
    #_ydiff = abs(_ymax - _ymin)
    #_xmin = (_xmin + _xmax)/2.0 - _xdiff
    #_ymin = (_ymin + _ymax)/2.0 - _ydiff
    #gtkimage.setView(_xmin, _ymin, (_scale * 2.0))
    ActiveScale = gtkimage.getUnitsPerPixel()
    ActiveScale = ActiveScale*2 #This Value here could be a global variable to put in the application option
    gtkimage.ZoomScale(ActiveScale)
    
def zoom_fit_cb(menuitem, gtkimage):
    gtkimage.fitImage()
def zoom_pan_cb(menuitem, gtkimage):
    _tool = tools.ZoomPan()
    gtkimage.getImage().setTool(_tool)
def oneShotMidSnap(menuitem, gtkimage):
    """
        Activate one shot snap mid
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('mid')
def oneShotEndSnap(menuitem, gtkimage):
    """
        Activate one shot snap end
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('end')
def oneShotIntersectionSnap(menuitem, gtkimage):
    """
        Activate one shot snap intersection
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('intersection')
def oneShotOriginSnap(menuitem, gtkimage):
    """
        Activate one shot snap origin
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('origin')

def oneShotPerpendicularSnap(menuitem, gtkimage):
    """
        Activate one shot snap Perpendicular
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('perpendicular')
def oneShotTangentSnap(menuitem, gtkimage):
    """
        Activate one shot snap Tangent
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('tangent')
def oneShotPointSnap(menuitem, gtkimage):
    """
        Activate one shot snap Point
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('point')

def oneShutCenterSnap(menuitem, gtkimage):
    """
        Activate one shut snap Center
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('center')
    
def dimension_linear_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.LinearDimensionTool()
    gtkimage.getImage().setTool(_tool)

def dimension_horizontal_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HorizontalDimensionTool()
    gtkimage.getImage().setTool(_tool)

def dimension_vertical_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VerticalDimensionTool()
    gtkimage.getImage().setTool(_tool)

def dimension_radial_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.RadialDimensionTool()
    gtkimage.getImage().setTool(_tool)

def dimension_angular_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.AngularDimensionTool()
    gtkimage.getImage().setTool(_tool)

def get_focus_widget_cb(menuitem, gtkimage):
    _widget = gtkimage.getWindow().get_focus()
    print "Focus widget: " + str(_widget)

def get_undo_stack_cb(menuitem, gtkimage):
    _layer = gtkimage.image.getActiveLayer()
    _log = _layer.getLog()
    if _log is not None:
        _log.printUndoData()

def get_redo_stack_cb(menuitem, gtkimage):
    _layer = gtkimage.image.getActiveLayer()
    _log = _layer.getLog()
    if _log is not None:
        _log.printRedoData()

def get_image_undo_cb(menuitem, gtkimage):
    gtkimage.image.printStack(True)

def get_image_redo_cb(menuitem, gtkimage):
    gtkimage.image.printStack(False)

def collect_garbage_cb(menuitem, gtkimage):
    if 'gc' in sys.modules:
        _lost = gc.collect()
        print "%d lost objects: " % _lost


def _debug_cb(action, *args):
    print "_debug_cb()"
    print "action: " + `action`
    print "args: " + str(args)
    _group = action.get_property('action-group')
    if _group is not None:
        for _act in _group.list_actions():
            _name = _act.get_name()
            print "Action name: %s" % _name

def _std_cb(action, *args):
    print "_std_cb()"
    _name = action.get_name()
    print "Action name: %s" % _name

def _add_accelerators(action, menuitem, accelgroup):
    _path = action.get_accel_path()
    if _path is not None:
        _data = gtk.accel_map_lookup_entry(_path)
        if _data is not None:
            _k, _m = _data
            if gtk.accelerator_valid(_k, _m):
                menuitem.add_accelerator('activate', accelgroup,
                                         _k, _m, gtk.ACCEL_VISIBLE)



#############################################################################
#
# Menu item definitions -- These define the individual menu items,
# and the actions taken (callbacks invoked) when they are selected.
#
#############################################################################

######################  File menu  ##########################
def _file_menu_init(menuitem, gtkimage):
    _group = gtkimage.getGroup('File')
    if _group is not None:
        _act = _group.get_action('SaveLayerAs')
        if _act is not None:
            _act.set_property('sensitive', False)
            
#------------------------------------------------------------
def _make_file_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
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
    _act = gtk.Action('Open', _('_Open'), None, gtk.STOCK_OPEN)
    _act.connect('activate', file_open_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Inport', _('_Inport'), None, gtk.STOCK_OPEN)
    _act.connect('activate', file_inport_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Close', _('_Close'), None, gtk.STOCK_CLOSE)
    _act.connect('activate', file_close_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Save', _('_Save'), None, gtk.STOCK_SAVE)
    _act.connect('activate', file_save_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('SaveAs', _('Save _As ...'), None, None)
    _act.connect('activate', file_save_as_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('SaveLayerAs', _('Save _Layer As ...'), None, None)
    _act.connect('activate', file_save_layer_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('PrintScreen', _('Print Screen'), None, None)
    _act.connect('activate', file_print_screen_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Print', _('_Print'), None, gtk.STOCK_PRINT)
    _act.connect('activate', file_print_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, '<control>P')
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Quit', _('_Quit'), None, gtk.STOCK_QUIT)
    _act.connect('activate', file_quit_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    return _menu

#######################  Edit menu  ###########################
def _edit_menu_init(menuitem, gtkimage):
    _group = gtkimage.getGroup('Edit')
    if _group is not None:
        _image = gtkimage.getImage()
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
            

#############################################################################
#  Edit -> select all submenu
#############################################################################
def _make_select_all_menu(actiongroup, gtkimage):
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
#  Edit menu
#############################################################################
def _make_edit_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
    #
    _act = gtk.Action('Undo', _('_Undo'), None, gtk.STOCK_UNDO)
    _act.connect('activate', edit_undo_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, '<control>Z')
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Redo', _('_Redo'), None, gtk.STOCK_REDO)
    _act.connect('activate', edit_redo_cb, gtkimage)
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
    _act.connect('activate', edit_cut_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Copy', _('Copy'), None, gtk.STOCK_COPY)
    _act.connect('activate', edit_copy_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Paste', _('Paste'), None, gtk.STOCK_PASTE)
    _act.connect('activate', edit_paste_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('Select', _('_Select'), None, None)
    _act.connect('activate', edit_select_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('SelectAll', _('Select _All'), None, None)
    _act.connect('activate', _select_all_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _submenu = _make_select_all_menu(actiongroup, gtkimage)
    _item.set_submenu(_submenu)
    _menu.append(_item)
    #
    _act = gtk.Action('Deselect', _('_Deselect'), None, None)
    _act.connect('activate', edit_deselect_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Prefs', _('_Preferences'), None, gtk.STOCK_PREFERENCES)
    _act.connect('activate', prefs_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    return _menu

#############################################################################
#  Draw -> basic sub-menu
#############################################################################
def _make_draw_basic_menu(actiongroup, gtkimage):
    # _accel = gtkimage.accel
    _menu = gtk.Menu()
    #
    _act = gtk.Action('Points', _('_Point'), None, None)
    _act.connect('activate', draw_point_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Segments', _('_Segment'), None, None)
    _act.connect('activate', draw_segment_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Rectangles', _('_Rectangle'), None, None)
    _act.connect('activate', draw_rectangle_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Circles', _('_Circle'), None, None)
    _act.connect('activate', draw_circle_center_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('CirclesTwoPoints', _('Circle (_2 Pts)'), None, None)
    _act.connect('activate', draw_circle_tp_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Arcs', _('_Arc'), None, None)
    _act.connect('activate', draw_arc_center_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Draw -> lines sub-menu
#############################################################################
def _make_draw_conlines_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('HCLines', _('_Horizontal'), None, None)
    _act.connect('activate', draw_hcl_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('VCLines', _('_Vertical'), None, None)
    _act.connect('activate', draw_vcl_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ACLines', _('_Angled'), None, None)
    _act.connect('activate', draw_acl_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('CLines', _('_Two-Point'), None, None)
    _act.connect('activate', draw_cl_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('PerpConLines', _('Per_pendicular'), None, None)
    _act.connect('activate', draw_perpendicular_cline_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ParallelConLines', _('Para_llel'), None, None)
    _act.connect('activate', draw_poffset_cline_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('TangentConLines', _('_Tangent'), None, None)
    _act.connect('activate', draw_tangent_cline_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('TangentTwoCirclesConLines', _('Tangent _2 Circ'),
                      None, None)
    _act.connect('activate', draw_tangent_two_ccircles_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Draw -> concentric circles sub-menu
#############################################################################
def _make_draw_concircs_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('CCircles', _('_Center Pt.'), None, None)
    _act.connect('activate', draw_ccirc_cp_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('CCirclesTwoPoints', _('_Two Pts.'), None, None)
    _act.connect('activate', draw_ccirc_tp_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #    
    _act = gtk.Action('CCircleTangentSingle', _('_Single Tangency'),
                      None, None)
    _act.connect('activate', draw_tangent_single_conobj_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #    
    _act = gtk.Action('CCircleTangentDual', _('_Dual Tangency'), None, None)
    _act.connect('activate', draw_tangent_two_conobjs_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Draw set style sub-menu
#############################################################################
def _make_draw_set_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    # _act = gtk.Action('SetStyle', _('_Style'), None, None)
    # _act.connect('activate', draw_set_style_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    # _act = gtk.Action('SetLinetype', _('_Linetype'), None, None)
    # _act.connect('activate', draw_set_linetype_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    # _act = gtk.Action('SetColor', _('_Color'), None, None)
    # _act.connect('activate', draw_set_color_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    # _act = gtk.Action('SetThickness', _('_Thickness'), None, None)
    # _act.connect('activate', draw_set_thickness_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    # _item = gtk.SeparatorMenuItem()
    # _item.show()
    # _menu.append(_item)
    #
    _act = gtk.Action('SetImageColors', _('_Colors'), None, None)
    _act.connect('activate', colors_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('SetImageSizes', _('_Sizes'), None, None)
    _act.connect('activate', sizes_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('SetGraphicsStyle', _('_Style'), None, None)
    _act.connect('activate', style_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('SetTextStyle', _('_TextStyle'), None, None)
    _act.connect('activate', textstyle_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('SetDimStyle', _('_DimStyle'), None, None)
    _act.connect('activate', dimstyle_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('SetImageOps', _('_Display'), None, None)
    _act.connect('activate', toggle_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('SetImageUnits', _('_Units'), None, None)
    _act.connect('activate', units_cb, gtkimage)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    return _menu
#############################################################################
#  Draw-> Fillet sub menu .  .
#############################################################################
def _make_draw_fillets_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('PointFillet', _('_Point..'), None, None)
    _act.connect('activate', draw_fillet_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('TwoLineFillet', _('_Two Line'), None, None)
    _act.connect('activate', draw_fillet_two_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    return _menu


#############################################################################
#  Draw . . .  .
#############################################################################
def _make_add_new_menu(actiongroup, gtkimage):
    #
    # These currently do nothing but are present to encourage
    # the development of code to make the ability to add and
    # save new styles and linetypes in drawings ...
    #
    _menu = gtk.Menu()
    #
    _act = gtk.Action('AddStyle', _('Style'), None, None)
    _act.set_property('sensitive', False)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('AddLinetype', _('Linetype'), None, None)
    _act.set_property('sensitive', False)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu
    
#############################################################################
#  Top level draw menu
#############################################################################
def _make_draw_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('Basic', _('_Basic'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_draw_basic_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('ConLines', _('Con. _Lines'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_draw_conlines_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('ConCircs', _('Con. _Circs.'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_draw_concircs_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('Chamfers', _('Cha_mfer'), None, None)
    _act.connect('activate', draw_chamfer_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    # 
    _act = gtk.Action('Fillets', _('_Fillets'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_draw_fillets_menu(actiongroup, gtkimage))
    _menu.append(_item)
    # 
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Leaders', _('Lea_der'), None, None)
    _act.connect('activate', draw_leader_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Polylines', _('_Polyline'), None, None)
    _act.connect('activate', draw_polyline_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('InternalPolygon', _('Poly_gon (Int.)'), None, None)
    _act.connect('activate', draw_polygon_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ExternalPolygon', _('Polygon (E_xt.)'), None, None)
    _act.connect('activate', draw_ext_polygon_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Textblocks', _('_Text'), None, None)
    _act.connect('activate', draw_text_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('SetProperties', _('_Set ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_draw_set_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('AddNew', _('Add _New ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_add_new_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    return _menu

#############################################################################
#  Modify -> move sub-menu
#############################################################################
def _make_modify_move_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('MoveHoriz', _('_Horizontal'), None, None)
    _act.connect('activate', move_horizontal_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('MoveVert', _('_Vertical'), None, None)
    _act.connect('activate', move_vertical_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('MoveTwoPt', _('_Two-Point Move'), None, None)
    _act.connect('activate', move_twopoint_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> stretch sub-menu
#############################################################################
def _make_modify_stretch_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('StretchHoriz', _('_Horizontal'), None, None)
    _act.connect('activate', stretch_horiz_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('StretchVert', _('_Vertical'), None, None)
    _act.connect('activate', stretch_vert_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('StretchTwoPt', _('_Two-Point Stretch'), None, None)
    _act.connect('activate', stretch_twopoint_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> change sub-sub-menu 
#############################################################################
def _make_change_text_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeTextBlockFamily', _('_Family'), None, None)
    _act.connect('activate', change_textblock_family_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeTextBlockWeight', _('_Weight'), None, None)
    _act.connect('activate', change_textblock_weight_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeTextBlockStyle', _('_Style'), None, None)
    _act.connect('activate', change_textblock_style_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeTextBlockColor', _('_Color'), None, None)
    _act.connect('activate', change_textblock_color_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeTextBlockSize', _('Si_ze'), None, None)
    _act.connect('activate', change_textblock_size_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeTextBlockAlignment', _('_Alignment'), None, None)
    _act.connect('activate', change_textblock_alignment_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> change -> Dimension -> Primary DimString sub-sub-menu 
#############################################################################
def _make_change_primary_dimstring_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangePDimStringFamily', _('Family'), None, None)
    _act.connect('activate', change_dim_primary_family_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringWeight', _('Weight'), None, None)
    _act.connect('activate', change_dim_primary_weight_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringStyle', _('Style'), None, None)
    _act.connect('activate', change_dim_primary_style_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringSize', _('Size'), None, None)
    _act.connect('activate', change_dim_primary_size_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringColor', _('Color'), None, None)
    _act.connect('activate', change_dim_primary_color_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringAlignment', _('Alignment'), None, None)
    _act.connect('activate', change_dim_primary_alignment_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringPrefix', _('Prefix'), None, None)
    _act.connect('activate', change_ldim_pds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringSuffix', _('Suffix'), None, None)
    _act.connect('activate', change_ldim_pds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringPrecision', _('Precision'), None, None)
    _act.connect('activate', change_dim_primary_precision_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringUnits', _('Units'), None, None)
    _act.connect('activate', change_dim_primary_units_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringPrintZero', _('Print Zero'), None, None)
    _act.connect('activate', change_dim_primary_print_zero_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangePDimStringPrintDecimal', _('Print Decimal'),
                      None, None)
    _act.connect('activate', change_dim_primary_print_decimal_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> change -> Dimension -> Secondary DimString sub-sub-menu 
#############################################################################
def _make_change_secondary_dimstring_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeSDimStringFamily', _('Family'), None, None)
    _act.connect('activate', change_dim_secondary_family_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringWeight', _('Weight'), None, None)
    _act.connect('activate', change_dim_secondary_weight_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringStyle', _('Style'), None, None)
    _act.connect('activate', change_dim_secondary_style_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringSize', _('Size'), None, None)
    _act.connect('activate', change_dim_secondary_size_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringColor', _('Color'), None, None)
    _act.connect('activate', change_dim_secondary_color_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringAlignment', _('Alignment'), None, None)
    _act.connect('activate', change_dim_secondary_alignment_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringPrefix', _('Prefix'), None, None)
    _act.connect('activate', change_ldim_sds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringSuffix', _('Suffix'), None, None)
    _act.connect('activate', change_ldim_sds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringPrecision', _('Precision'), None, None)
    _act.connect('activate', change_dim_secondary_precision_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringUnits', _('Units'), None, None)
    _act.connect('activate', change_dim_secondary_units_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringPrintZero', _('Print Zero'), None, None)
    _act.connect('activate', change_dim_secondary_print_zero_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeSDimStringPrintDecimal', _('Print Decimal'),
                      None, None)
    _act.connect('activate', change_dim_secondary_print_decimal_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

def _make_change_rdim_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeRDimPDSPrefix', _('Primary Prefix'), None, None)
    _act.connect('activate', change_rdim_pds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeRDimPDSSuffix', _('Primary Suffix'), None, None)
    _act.connect('activate', change_rdim_pds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeRDimSDSPrefix', _('Secondary Prefix'), None, None)
    _act.connect('activate', change_rdim_sds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeRDimSDSSuffix', _('Secondary Suffix'), None, None)
    _act.connect('activate', change_rdim_sds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeRDimDiaMode', _('Dia. Mode'), None, None)
    _act.connect('activate', change_rdim_dia_mode_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

def _make_change_adim_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeADimPDSPrefix', _('Primary Prefix'), None, None)
    _act.connect('activate', change_adim_pds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeADimPDSSuffix', _('Primary Suffix'), None, None)
    _act.connect('activate', change_adim_pds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeADimSDSPrefix', _('Secondary Prefix'), None, None)
    _act.connect('activate', change_adim_sds_prefix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeADimSDSSuffix', _('Secondary Suffix'), None, None)
    _act.connect('activate', change_adim_sds_suffix_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeADimInvert', _('Invert'), None, None)
    _act.connect('activate', change_adim_invert_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> change -> dimension sub-sub-menu 
#############################################################################
def _make_change_dimension_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeDimEndpointType', _('Endpoint _Type'), None, None)
    _act.connect('activate', change_dim_endpoint_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimEndpointSize', _('Endpoint _Size'), None, None)
    _act.connect('activate', change_dim_endpoint_size_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimOffset', _('_Offset Length'), None, None)
    _act.connect('activate', change_dim_offset_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimExtension', _('E_xtension Length'), None, None)
    _act.connect('activate', change_dim_extension_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimDualMode', _('_Dual Mode'), None, None)
    _act.connect('activate', change_dim_dual_mode_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimDualModeOffset', _('Dual Mode O_ffset'),
                      None, None)
    _act.connect('activate', change_dim_dual_mode_offset_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimThickness', _('_Thickness'), None, None)
    _act.connect('activate', change_dim_thickness_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeDimColor', _('_Color'), None, None)
    _act.connect('activate', change_dim_color_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangePDimStrMenu', _('_Primary DimString'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_primary_dimstring_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeSDimStrMenu', _('_Secondary DimString'), None, None)
    actiongroup.add_action(_act)

    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_secondary_dimstring_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeRDimMenu', _('RadialDim ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_rdim_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeADimMenu', _('AngularDim ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_adim_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    # _act = gtk.Action('ChangeDimPrimaryDS', '_Primary DimString', None, None)
    # _act.connect('activate', change_primary_dim_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    # _act = gtk.Action('ChangeDimSecondaryDS', '_Secondary DimString', None, None)
    # _act.connect('activate', change_secondary_dim_cb, gtkimage)
    # actiongroup.add_action(_act)
    # _menu.append(_act.create_menu_item())
    #
    return _menu

#############################################################################
#  Modify -> change sub-menu 
#############################################################################
def _make_modify_change_menu(actiongroup, gtkimage):
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ChangeStyle', _('_Style'), None, None)
    _act.connect('activate', change_style_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeLinetype', _('_Linetype'), None, None)
    _act.connect('activate', change_linetype_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeColor', _('_Color'), None, None)
    _act.connect('activate', change_color_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ChangeThickness', _('_Thickness'), None, None)
    _act.connect('activate', change_thickness_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeTextMenu', _('Text_Block ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_text_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('ChangeDimMenu', _('_Dimension ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_change_dimension_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    return _menu

#############################################################################
#  Initialize Modify -> change sub menu
#############################################################################
def _change_menu_init(menuitem, gtkimage):
    # print "_change_menu_init()"
    _group = gtkimage.getGroup('Modify')
    if _group is not None:
        _image = gtkimage.getImage()
        _objlist = []
        _active = _image.getActiveLayer()
        _gflag = _tflag = _dflag = False
        for _obj in _image.getSelectedObjects(False):
            if isinstance(_obj, graphicobject.GraphicObject):
                _goflag = True
                continue
            if isinstance(_obj, text.TextBlock):
                _tflag = True
                continue
            if isinstance(_obj, dimension.Dimension):
                _dflag = True
            if _gflag and _tflag and _dflag:
                break
        if not _gflag or not _tflag or not _dflag:
            for _obj in _active.getChildren():
                if not _gflag and isinstance(_obj,
                                             graphicobject.GraphicObject):
                    _gflag = True
                    continue
                if not _tflag and isinstance(_obj, text.TextBlock):
                    _tflag = True
                    continue
                if not _dflag and isinstance(_obj, dimension.Dimension):
                    _dflag = True
                if _gflag and _tflag and _dflag:
                    break
        _act = _group.get_action('ChangeStyle')
        if _act is not None:
            _act.set_property('sensitive', _gflag)
        _act = _group.get_action('ChangeLinetype')
        if _act is not None:
            _act.set_property('sensitive', _gflag)
        _act = _group.get_action('ChangeColor')
        if _act is not None:
            _act.set_property('sensitive', _gflag)
        _act = _group.get_action('ChangeThickness')
        if _act is not None:
            _act.set_property('sensitive', _gflag)
        _act = _group.get_action('ChangeTextMenu')
        if _act is not None:
            _act.set_property('sensitive', _tflag)
        _act = _group.get_action('ChangeDimMenu')
        if _act is not None:
            _act.set_property('sensitive', _dflag)
        
#############################################################################
#  Initialize top level modify menu -- this handles greying out non-active items.
#############################################################################
def _modify_menu_init(menuitem, gtkimage):
    _group = gtkimage.getGroup('Modify')
    if _group is not None:
        _image = gtkimage.getImage()
        _active = _image.getActiveLayer()
        _act = _group.get_action('Move')
        if _act is not None:
            _act.set_property('sensitive', (_active.hasEntities() or
                                            _image.hasSelection()))
        _act = _group.get_action('Stretch')
        if _act is not None:
            _act.set_property('sensitive', _active.hasEntities())
        _act = _group.get_action('Split')
        if _act is not None:
            _flag = ((_active.getEntityCount('segment') > 0) or
                     (_active.getEntityCount('circle') > 0) or
                     (_active.getEntityCount('arc') > 0) or
                     (_active.getEntityCount('polyline') > 0))
            _act.set_property('sensitive', _flag)
        _act = _group.get_action('Mirror')
        if _act is not None:
            _flag = ((_active.hasEntities() or _image.hasSelection()) and
                     ((_active.getEntityCount('hcline') > 0) or
                      (_active.getEntityCount('vcline') > 0) or
                      (_active.getEntityCount('acline') > 0) or
                      (_active.getEntityCount('cline') > 0)))
            _act.set_property('sensitive', _flag)
        _act = _group.get_action('Transfer')
        if _act is not None:
            _flag = False
            _layers = [_image.getTopLayer()]
            while len(_layers):
                _layer = _layers.pop()
                if _layer is not _active:
                    _flag = _layer.hasEntities()
                if _flag:
                    break
                _layers.extend(_layer.getSublayers())
            _act.set_property('sensitive', _flag)
        _act = _group.get_action('Rotate')
        if _act is not None:
            _act.set_property('sensitive', (_active.hasEntities() or
                                            _image.hasSelection()))
        _act = _group.get_action('Delete')
        if _act is not None:
            _act.set_property('sensitive', _active.hasEntities())
        _act = _group.get_action('Change')
        if _act is not None:
            _act.set_property('sensitive', (_image.hasSelection() or
                                            _active.hasEntities()))
        _act = _group.get_action('ZoomFit')
        if _act is not None:
            _act.set_property('sensitive', _active.hasEntities())
#############################################################################
#  Top level modify menu
#############################################################################
def _make_modify_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
    #
    _act = gtk.Action('Move', _('_Move ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_modify_move_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('Stretch', _('S_tretch ...'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_modify_stretch_menu(actiongroup, gtkimage))
    _menu.append(_item)
    #
    _act = gtk.Action('Split', _('S_plit'), None, None)
    _act.connect('activate', split_object_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Mirror', _('_Mirror'), None, None)
    _act.connect('activate', mirror_object_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('Transfer', _('Trans_fer'), None, None)
    _act.connect('activate', transfer_object_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Rotate', _('_Rotate'), None, None)
    _act.connect('activate', rotate_object_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Delete', _('_Delete'), None, None)
    _act.connect('activate', delete_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _item = gtk.SeparatorMenuItem()
    _item.show()
    _menu.append(_item)
    #
    _act = gtk.Action('Change', _('_Change'), None, None)
    _act.connect('activate', _change_menu_init, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_modify_change_menu(actiongroup, gtkimage))
    _menu.append(_item)
    return _menu
#############################################################################
#  Initialize top level view menu -- this handles greying out non-active items.
#############################################################################
def _view_menu_init(menuitem, gtkimage):
    _group = gtkimage.getGroup('View')
    if _group is not None:
        _image = gtkimage.getImage()
        _active = _image.getActiveLayer()
        _act = _group.get_action('ZoomFit')
        if _act is not None:
            _act.set_property('sensitive', _active.hasEntities())
#############################################################################
#  Top level view menu
#############################################################################
def _make_view_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
    #
    _act = gtk.Action('ZoomIn', _('_Zoom In'), None, gtk.STOCK_ZOOM_IN)
    _act.connect('activate', zoom_in_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('ZoomOut', _('Zoom _Out'), None, gtk.STOCK_ZOOM_OUT)
    _act.connect('activate', zoom_out_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('ZoomFit', _('Zoom _Fit'), None, gtk.STOCK_ZOOM_FIT)
    _act.connect('activate', zoom_fit_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, None)
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('ZoomPan', _('Zoom _Pan'), None, None)
    _act.connect('activate', zoom_pan_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('ZoomWindow', _('Zoom _Window'), None, None)
    _act.connect('activate', zoom_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    return _menu
#############################################################################
#  Initialize top level snap menu -- this handles greying out non-active items.
#############################################################################
def _snap_menu_init(menuitem, gtkimage):
    return
    
#############################################################################
#   Top level snap menu
#############################################################################
def _make_snap_menu(actiongroup, gtkimage):
    _group = gtkimage.getGroup('Snap')
    _menu = gtk.Menu()
    #
    _act = gtk.Action('OneShotSnap', _('_One Shot Snap'), None, None)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _item.set_submenu(_make_snap_oneshot_menu(actiongroup, gtkimage))
    _menu.append(_item)
    return _menu

def _make_snap_oneshot_menu(actiongroup, gtkimage):
    _group = gtkimage.getGroup('SnapOneShot')
    _menu = gtk.Menu()
    #
    _act = gtk.Action('MidPoint', _('_Mid Point'), None, None)
    _act.connect('activate', oneShotMidSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('Point', _('_Point'), None, None)
    _act.connect('activate', oneShotPointSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('Center', _('_Center'), None, None)
    _act.connect('activate', oneShutCenterSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)    
    #
    _act = gtk.Action('EndPoint', _('_End Point'), None, None)
    _act.connect('activate', oneShotEndSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('IntersectionPoint', _('_Intersection Point'), None, None)
    _act.connect('activate', oneShotIntersectionSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('OriginPoint', _('_Origin Point'), None, None)
    _act.connect('activate', oneShotOriginSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('PerpendicularPoint', _('_Perpendicular Point'), None, None)
    _act.connect('activate', oneShotPerpendicularSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)
    #
    _act = gtk.Action('TangentPoint', _('_Tangent Point'), None, None)
    _act.connect('activate', oneShotTangentSnap, gtkimage)
    actiongroup.add_action(_act)
    _item = _act.create_menu_item()
    _menu.append(_item)    
    return _menu
#############################################################################
#  Init top level Dimensions menu
#############################################################################
def _dimension_menu_init(menuitem, gtkimage):
    _group = gtkimage.getGroup('Dimension')
    if _group is not None:
        _ldim = _hdim = _vdim = _rdim = _adim = False
        _count = 0
        _layers = [gtkimage.image.getTopLayer()]
        for _layer in _layers:
            _pc = _layer.getEntityCount('point')
            if _pc > 0:
                _count = _count + _pc
                if _count > 1:
                    _ldim = _hdim = _vdim = True
                if _count > 2:
                    _adim = True
            if _layer.getEntityCount('circle') > 0:
                _rdim = True
            if _layer.getEntityCount('arc') > 0:
                _rdim = _adim = True
            if _ldim and _hdim and _vdim and _rdim and _adim:
                break
            _layers.extend(_layer.getSublayers())
        _act = _group.get_action('Linear')
        if _act is not None:
            _act.set_property('sensitive', _ldim)
        _act = _group.get_action('Horizontal')
        if _act is not None:
            _act.set_property('sensitive', _hdim)
        _act = _group.get_action('Vertical')
        if _act is not None:
            _act.set_property('sensitive', _vdim)
        _act = _group.get_action('Radial')
        if _act is not None:
            _act.set_property('sensitive', _rdim)
        _act = _group.get_action('Angular')
        if _act is not None:
            _act.set_property('sensitive', _adim)

#############################################################################
#  Top level Dimensions menu
#############################################################################
def _make_dimension_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
    _act = gtk.Action('Linear', _('_Linear'), None, None)
    _act.connect('activate', dimension_linear_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('Horizontal', _('_Horizontal'), None, None)
    _act.connect('activate', dimension_horizontal_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('Vertical', _('_Vertical'), None, None)
    _act.connect('activate', dimension_vertical_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('Radial', _('_Radial'), None, None)
    _act.connect('activate', dimension_radial_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('Angular', _('_Angular'), None, None)
    _act.connect('activate', dimension_angular_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    return _menu

#############################################################################
#  Top level debug menu
#############################################################################
def _make_debug_menu(actiongroup, gtkimage):
    _accel = gtkimage.accel
    _menu = gtk.Menu()
    _act = gtk.Action('Focus', _('Focus'), None, None)
    _act.connect('activate', get_focus_widget_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    #
    _act = gtk.Action('UndoStack', _('Undo Stack'), None, None)
    _act.connect('activate', get_undo_stack_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, '<alt>Z')
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('RedoStack', _('Redo Stack'), None, None)
    _act.connect('activate', get_redo_stack_cb, gtkimage)
    _act.set_accel_group(_accel)
    actiongroup.add_action_with_accel(_act, '<alt><shift>Z')
    _item = _act.create_menu_item()
    if isinstance(_act, gtkactions.stdAction):
        _add_accelerators(_act, _item, _accel)
    _menu.append(_item)
    #
    _act = gtk.Action('ImageUndo', _('Image Undo'), None, None)
    _act.connect('activate', get_image_undo_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('ImageRedo', _('Image Redo'), None, None)
    _act.connect('activate', get_image_redo_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    _act = gtk.Action('GC', 'GC', None, None)
    _act.connect('activate', collect_garbage_cb, gtkimage)
    actiongroup.add_action(_act)
    _menu.append(_act.create_menu_item())
    return _menu
    
#############################################################################
#  Fill out top menubar with menu items.
#############################################################################
def fill_menubar(mb, gtkimage):
    if not isinstance(mb, gtk.MenuBar):
        raise TypeError, "Invalid gtk.MenuBar object: " + `mb`
    # File menu
    _group = gtk.ActionGroup('File')
    gtkimage.addGroup(_group)
    _act = gtk.Action('FileMenu', _('_File'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _file_menu_init, gtkimage)
    _menu = _make_file_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Edit menu
    _group = gtk.ActionGroup('Edit')
    gtkimage.addGroup(_group)
    _act = gtk.Action('EditMenu', _('_Edit'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _edit_menu_init, gtkimage)
    _menu = _make_edit_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Draw menu
    _group = gtk.ActionGroup('Draw')
    gtkimage.addGroup(_group)
    _act = gtk.Action('DrawMenu', _('_Draw'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _menu = _make_draw_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Modifying
    _group = gtk.ActionGroup('Modify')
    gtkimage.addGroup(_group)
    _act = gtk.Action('ModifyMenu', _('_Modify'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _modify_menu_init, gtkimage)
    _menu = _make_modify_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # View
    _group = gtk.ActionGroup('View')
    gtkimage.addGroup(_group)
    _act = gtk.Action('ViewMenu', _('_View'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _view_menu_init, gtkimage)
    _menu = _make_view_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Snap
    _group = gtk.ActionGroup('Snap')
    gtkimage.addGroup(_group)
    _act = gtk.Action('SnapMenu', _('_Snap'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _snap_menu_init, gtkimage)
    _menu = _make_snap_oneshot_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Dimensioning
    _group = gtk.ActionGroup('Dimension')
    gtkimage.addGroup(_group)
    _act = gtk.Action('DimensionMenu', _('Dime_nsions'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    _act.connect('activate', _dimension_menu_init, gtkimage)
    _menu = _make_dimension_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
    # Debug
    _group = gtk.ActionGroup('Debug')
    gtkimage.addGroup(_group)
    _act = gtk.Action('DebugMenu', _('De_bug'), None, None)
    _group.add_action(_act)
    _item = gtk.MenuItem()
    _act.connect_proxy(_item)
    # _act.connect('activate', _debug_cb)
    _menu = _make_debug_menu(_group, gtkimage)
    _item.set_submenu(_menu)
    mb.append(_item)
