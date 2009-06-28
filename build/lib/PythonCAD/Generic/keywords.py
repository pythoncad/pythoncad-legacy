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
# This code sets the global entries for the gtkimage.entry box
# commands text to 'defined' behavior for an application set
# thus simulating a mainstream CAD package at the users need
#
# Author: David Broadwell ( dbroadwell@mindspring.com, 05/26/2003 )
#

"""
Defaultglobals is loaded by default, use it's pattern to make
your own behave like the CAD you are familiar with.

Please note the example below;

exampledefinitions = {
    'foobar' : "quit()",
    'foo' : "segment()",
    'X' : "quit()",
    'O' : "opend()"
}
"""

defaultglobals = {
    'acline' : "acline",
    'acl' : "acline",
    'adim' : "adim",
    'arc' : "arcc",
    'ccir2' : "ccir2p",
    'ccir' : "ccircen",
    'chamfer' : "chamfer",
    'cir2' : "cir2p",
    'cir' : "circen",
    'cl' : "cl",
    'close' : "close",
    'copy' : "copy",
    'cut' : "cut",
    'delete' : "delete",
    'del' : "delete",
    'deselect' : "deselect",
    'dimpref' : "dimpref",
    'exit' : "quit",
    'fillet' : "fillet",
    'hcline' : "hcline",
    'hcl' : "hcline",
    'hdim' : "hdim",
    'ldim' : "ldim",
    'leader' : "leader",
    'lead' : "leader",
    'mirror' : "mirror",
    'mir' : "mirror",
    'move' : "move",
    'mv' : "move",
    'moveh' : "moveh",
    'movev' : "movev",
    'new' : "new",
    'opend' : "opend",
    'paste' : "paste",
    'pcline' : "pcline",
    'point' : "point",
    'polyline' : "polyline",
    'pline' : "polyline",
    'print' : "print",
    'plot' : "print",
    'pref' : "pref",
    'quit' : "quit",
    'rdim' : "rdim",
    'rectangle' : "rect",
    'rect' : "rect",
    'redraw' : "redraw",
    'refresh' : "refresh",
    'r' : "refresh",
    'saa' : "saa",
    'saacl' : "saacl",
    'sac' : "sac",
    'sacc' : "sacc",
    'sacl' : "sacl",
    'sahcl' : "sahcl",
    'sap' : "sap",
    'sas' : "sas",
    'savcl' : "savcl",
    'saveas' : "saveas",
    'savel' : "savel",
    'saves' : "saves",
    'select' : "select",
    'sv' : "saves",
    'segment' : "segment",
    'seg' : "segment",
    'l' : "segment",
    'split' : "split",
    'str' : "str",
    'strh' : "strh",
    'strv' : "strv",
    'tcline' : "tcline",
    'tcl' : "tcline",
    'text' : "text",
    'transfer' : "transfer",
    'unselect' : "deselect",
    'vcline' : "vcline",
    'vcl' : "vcline",
    'vdim' : "vdim",
    'zoomd' : "zoomd",
    'z' : "zoomd",
    'zoomf' : "zoomf",
    'zf' : "zoomf",
    'zoomi' : "zoomi",
    'zi' : "zoomi",
    'zoomo' : "zoomo",
    'zo' : "zoomo"
}

acadglobals = defaultglobals

# me10globals = defaultglobals

