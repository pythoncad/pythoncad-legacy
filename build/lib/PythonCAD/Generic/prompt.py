#
# Copyright (c) 2003 Art Haas
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
# This code handles interpreting entries in the gtkimage.entry box
# and calling the apprpriate internal command
#
# Author: David Broadwell ( dbroadwell@mindspring.com, 05/26/2003 )
#

from PythonCAD.Generic import tools

''' defines the internal maping for a human name like circle() to
    an internal function, so that the config file can look all
    clean and pretty. AKA: evalkey interface Release 5/25/03 '''

''' 05/29/03 R2c Complete redesign, no longer does the internal name
    need to be a function, dropped prompt.py filesize from 9.8 to
    5.3Kb! cleaned up the feywords file, no appreciable difference
    Used a dictionary instead of discreet functions for every entry
    and for R3, menus. '''

''' Previous versions of this file defined commands in terms of
    interface specific calls. The new takes advantage of the
    messaging system within PythonCAD and various improvements/cleanups
    in the core code. A command will be associated with a Tool
    subclass, and by installing the tool in an Image the messaging
    system will pass the information to the interface which can then
    install handlers as necessary. '''

def lookup(text):
    """
    Interface to promptdef dictionary, returns code by keyword definition
    lookup(text) or 'None' if no Tool found for command.
    """
    return promptdefs.get(text)

promptdefs = {
    'pcline' : tools.ParallelOffsetTool,
    'tcline' : tools.TangentCLineTool,
    'hcline' : tools.HCLineTool,
    'vcline' : tools.VCLineTool,
    'acline' : tools.ACLineTool,
    'cl' : tools.CLineTool,
    'point' : tools.PointTool,
    'segment' : tools.SegmentTool,
    'circen' : tools.CircleTool,
    'cir2p' : tools.TwoPointCircleTool,
    'ccircen' : tools.CCircleTool,
    'ccir2p' : tools.TwoPointCCircleTool,
    'arcc' : tools.ArcTool,
    'rect' : tools.RectangleTool,
    'leader' : tools.LeaderTool,
    'polyline' : tools.PolylineTool,
    'text' : tools.TextTool,
    'transfer' : tools.TransferTool,
    'split' : tools.SplitTool,
    'mirror' : tools.MirrorTool,
    'delete' : tools.DeleteTool,
    'moveh' : tools.HorizontalMoveTool,
    'movev' : tools.VerticalMoveTool,
    'move' : tools.MoveTool,
    'chamfer' : tools.ChamferTool,
    'fillet' : tools.FilletTool,
    'strh' : tools.HorizontalStretchTool,
    'strv' : tools.VerticalStretchTool,
    'str' : tools.StretchTool,
    'adim' : tools.AngularDimensionTool,
    'rdim' : tools.RadialDimensionTool,
    'ldim' : tools.LinearDimensionTool,
    'hdim' : tools.HorizontalDimensionTool,
    'vdim' : tools.VerticalDimensionTool,
    # 'close' : "gtkmenus.file_close_cb('file_close',self)",
    # 'quit' : "gtkmenus.file_quit_cb('file_quit',self)",
    # 'new' : "gtkmenus.file_new_cb('file_new',self)",
    # 'opend' : "gtkmenus.file_open_cb('file_open',self)",
    # 'saves' : "gtkmenus.file_save_cb('file_save',self)",
    # 'saveas' : "gtkmenus.file_save_as_cb('file_save_as',self)",
    # 'savel' : "gtkmenus.file_save_layer_cb('file_save_layer',self)",
    # 'cut' : "gtkmenus.edit_cut_cb('edit_cut',self)",
    # 'copy' : "gtkmenus.edit_copy_cb('edit_copy',self)",
    'paste' : tools.PasteTool,
    'select' : tools.SelectTool,
    'deselect' : tools.DeselectTool,
    # 'saa' : "gtkmenus.select_all_arcs_cb('select_all_arcs',self)",
    # 'sac' : "gtkmenus.select_all_circles_cb('select_all_circles',self)",
    # 'sacc' : "gtkmenus.select_all_ccircles_cb('select_all_ccircles',self)",
    # 'sacl' : "gtkmenus.select_all_clines_cb('select_all_clines',self)",
    # 'sahcl' : "gtkmenus.select_all_hclines_cb('select_all_hclines',self)",
    # 'savcl' : "gtkmenus.select_all_vclines_cb('select_all_vclines',self)",
    # 'saacl' : "gtkmenus.select_all_aclines_cb('select_all_aclines',self)",
    # 'sap' : "gtkmenus.select_all_points_cb('select_all_points',self)",
    # 'sas' : "gtkmenus.select_all_segments_cb('select_all_segments',self)",
    # 'redraw' : "self.redraw()",
    # 'refresh' : "self.refresh()",
    # 'pref' : "gtkmenus.prefs_cb('prefs',self)",
    # 'dimpref' : "gtkmenus.dimension_prefs_cb('dimension_prefs',self)",
    'zoomd' : tools.ZoomTool,
    'print' : tools.PlotTool,
    # 'zoomi' : "gtkmenus.zoom_in_cb('zoom_in',self)",
    # 'zoomo' : "gtkmenus.zoom_out_cb('zoom_out',self)",
    # 'zoomf' : "gtkmenus.zoom_fit_cb('zoom_fit',self)"
}
