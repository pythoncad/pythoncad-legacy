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


''' 05/29/03 R2c Complete redesign, no longer does the internal name
    need to be a function, dropped prompt.py filesize from 9.8 to
    5.3Kb! cleaned up the feywords file, no appreciable difference
    Used a dictionary instead of discreet functions for every entry
    and for R3, menus. '''


def lookup(text):
    """Interface to promptdef dictionary, returns code by keyword definition

lookup(text)    
    """
    assert text in promptdefs, "No command for %s" % str(text)
    return promptdefs[text]

promptdefs = {
    'acline' : "NSApp.sendAction_to_from_(\"drawACLine:\", None, self)",
    'arcc' : "NSApp.sendAction_to_from_(\"drawArc:\", None, self)",
    'ccircen' : "NSApp.sendAction_to_from_(\"drawCCircleCenter:\", None, self)",
    'ccir2p' : "NSApp.sendAction_to_from_(\"drawCCircle2Point:\", None, self)",
    'chamfer' : "NSApp.sendAction_to_from_(\"drawChamfer:\", None, self)",
    'close' : "NSApp.sendAction_to_from_(\"performClose:\", None, self)",
    'circen' : "NSApp.sendAction_to_from_(\"drawCircleCentered:\", None, self)",
    'cir2p' : "NSApp.sendAction_to_from_(\"drawCircle2Point:\", None, self)",
    'cl' : "NSApp.sendAction_to_from_(\"draw2PointCLine:\", None, self)",
    'cut' : "NSApp.sendAction_to_from_(\"cut:\", None, self)",
    'copy' : "NSApp.sendAction_to_from_(\"copy:\", None, self)",
    'delete' : "NSApp.sendAction_to_from_(\"delete:\", None, self)",
    'dimpref' : "NSApp.sendAction_to_from_(\"dimension_prefs_cb(None)",
    'fillet' : "NSApp.sendAction_to_from_(\"drawFillet:\", None, self)",
    'hcline' : "NSApp.sendAction_to_from_(\"drawHCLine:\", None, self)",
    'leader' : "NSApp.sendAction_to_from_(\"drawLeader:\", None, self)",
    'mirror' : "NSApp.sendAction_to_from_(\"modifyMirror:\", None, self)",
    'moveh' : "NSApp.sendAction_to_from_(\"modifyMoveHorizontal:\", None, self)",
    'movev' : "NSApp.sendAction_to_from_(\"modifyMoveVertical:\", None, self)",
    'move' : "NSApp.sendAction_to_from_(\"modifyMoveFree:\", None, self)",
    'new' : "NSApp.sendAction_to_from_(\"newDocument:\", None, self)",
    'opend' : "NSApp.sendAction_to_from_(\"openDocument:\", None, self)",
    'paste' : "NSApp.sendAction_to_from_(\"paste:\", None, self)",
    'pcline' : "NSApp.sendAction_to_from_(\"drawPerpendicularCLine:\", None, self)",
    'point' : "NSApp.sendAction_to_from_(\"drawPoint:\", None, self)",
    'polyline' : "NSApp.sendAction_to_from_(\"drawPolyline:\", None, self)",
    'polygon' : "NSApp.sendAction_to_from_(\"drawPolygon:\", None, self)", 
    'polygonext' : "NSApp.sendAction_to_from_(\"drawPolygonExternal:\", None, self)", 
    'pref' : "NSApp.sendAction_to_from_(\"prefs_cb(None)",
    'rect' : "NSApp.sendAction_to_from_(\"drawRect:\", None, self)",
    'redraw' : "self.document().getDA().setNeedsDisplay_(True)",
    'redo ' : "NSApp.delegate().redo_(None)",
    'refresh' : "self.document().getDA().setNeedsDisplay_(True)",
    'saa' : "NSApp.sendAction_to_from_(\"select_all_arcs_cb(None)",
    'saacl' : "NSApp.sendAction_to_from_(\"select_all_aclines_cb(None)",
    'sac' : "NSApp.sendAction_to_from_(\"select_all_circles_cb(None)",
    'sacc' : "NSApp.sendAction_to_from_(\"select_all_ccircles_cb(None)",
    'sacl' : "NSApp.sendAction_to_from_(\"select_all_clines_cb(None)",
    'sahcl' : "NSApp.sendAction_to_from_(\"select_all_hclines_cb(None)",
    'sap' : "NSApp.sendAction_to_from_(\"select_all_points_cb(None)",
    'sas' : "NSApp.sendAction_to_from_(\"select_all_segments_cb(None)",
    'savcl' : "NSApp.sendAction_to_from_(\"select_all_vclines_cb(None)",
    'saveas' : "NSApp.sendAction_to_from_(\"saveDocumentAs:\", None, self)",
    'saves' : "NSApp.sendAction_to_from_(\"saveDocument:\", None, self)",
    'savel' : "NSApp.sendAction_to_from_(\"saveLayerAs:\", None, self)",
    'segment' : "NSApp.sendAction_to_from_(\"drawSegment:\", None, self)",
    'split' : "NSApp.sendAction_to_from_(\"modifySplit:\", None, self)",
    'strh' : "NSApp.sendAction_to_from_(\"modifyStretchHorizontal:\", None, self)",
    'strv' : "NSApp.sendAction_to_from_(\"modifyStretchVertical:\", None, self)",
    'str' : "NSApp.sendAction_to_from_(\"modifyStretchFree:\", None, self)",
    'tcline' : "NSApp.sendAction_to_from_(\"drawTanCLine:\", None, self)",
    'text' : "NSApp.sendAction_to_from_(\"drawText:\", None, self)",
    'transfer' : "NSApp.sendAction_to_from_(\"modifyTransfer:\", None, self)",
    'undo' : "NSApp.delegate().undo_(None)",
    'vcline' : "NSApp.sendAction_to_from_(\"drawVCLine:\", None, self)",
    'quit' : "NSApp.sendAction_to_from_(\"terminate:\", None, self)",
    'zoomd' : "NSApp.sendAction_to_from_(\"windowZoom:\", None, self)",
    'zoomi' : "NSApp.sendAction_to_from_(\"windowZoomIn:\", None, self)",
    'zoomo' : "NSApp.sendAction_to_from_(\"windowZoomOut:\", None, self)",
    'zoomf' : "NSApp.sendAction_to_from_(\"windowZoomFit:\", None, self)"
}
