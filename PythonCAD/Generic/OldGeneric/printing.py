#
# Copyright (c) 2004 Art Haas
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

import time

from PythonCAD.Generic import plotfile
from PythonCAD.Generic import units

papersizes = { # see 'gs_statd.ps' from Ghostscript
    'letter' : (612, 792),
    'legal' : (612, 1008),
    'tabloid' : (792, 1224),
    'csheet' : (1224, 1584),
    'dsheet' : (1584, 2448),
    'esheet' : (2448, 3168),
    'a0' : (2384, 3370),
    'a1' : (1684, 2384),
    'a2' : (1191, 1684),
    'a3' : (842, 1191),
    'a4' : (595, 842),
    'a5' : (420, 595),
    'b0' : (2835, 4008),
    'b1' : (2004, 2835),
    'b2' : (1417, 2004),
    'b3' : (1001, 1417),
    'b4' : (709, 1001),
    'b5' : (499, 709),
    'b6' : (354, 499),
    'jisb0' : (2920, 4127),
    'jisb1' : (2064, 2920),
    'jisb2' : (1460, 2064),
    'jisb3' : (1032, 1460),
    'jisb4' : (729, 1032),
    'jisb5' : (516, 729),
    'jisb6' : (363, 516),
    'c0' : (2599, 3677),
    'c1' : (1837, 2599),
    'c2' : (1298, 1837),
    'c3' : (918, 1298),
    'c4' : (649, 918),
    'c5' : (459, 649),
    'c6' : (323, 459),
    'archE' : (2592, 3456),
    'archD' : (1728, 2592),
    'archC' : (1296, 1728),
    'archB' : (864, 1296),
    'archA' : (648, 864),
    }

class PSPlot(object):
    """A class for generating PostScript output
    """
    #
    # all papersizes below are defined for portrait printing
    #
    # some sizes taken from 'gs_statd.ps' Ghostscript file
    #
    __papersizes = {
        'exact' : (0, 0),
        'letter' : (612, 792),
        'legal' : (612, 1008),
        'tabloid' : (792, 1224),
        'csheet' : (1224, 1584),
        'dsheet' : (1584, 2448),
        'esheet' : (2448, 3168),
        'a0' : (2384, 3370),
        'a1' : (1684, 2384),
        'a2' : (1191, 1684),
        'a3' : (842, 1191),
        'a4' : (595, 842),
        'a5' : (420, 595),
        'b0' : (2835, 4008),
        'b1' : (2004, 2835),
        'b2' : (1417, 2004),
        'b3' : (1001, 1417),
        'b4' : (709, 1001),
        'b5' : (499, 709),
        'b6' : (354, 499),
        'jisb0' : (2920, 4127),
        'jisb1' : (2064, 2920),
        'jisb2' : (1460, 2064),
        'jisb3' : (1032, 1460),
        'jisb4' : (729, 1032),
        'jisb5' : (516, 729),
        'jisb6' : (363, 516),
        'c0' : (2599, 3677),
        'c1' : (1837, 2599),
        'c2' : (1298, 1837),
        'c3' : (918, 1298),
        'c4' : (649, 918),
        'c5' : (459, 649),
        'c6' : (323, 459),
        'archE' : (2592, 3456),
        'archD' : (1728, 2592),
        'archC' : (1296, 1728),
        'archB' : (864, 1296),
        'archA' : (648, 864),
    }

    #
    # PostScript units are points : 72 points per inch
    #
    # note: 25.4 mm/inch
    __scale = {
        units.MILLIMETERS : '72 25.4 div',
        units.MICROMETERS : '72 25.4 1000 mul div',
        units.METERS : '72 25.4 1000 div div',
        units.KILOMETERS : '72 25.4 1000 1000 mul mul div',
        units.INCHES : '72',
        units.FEET : '72 12 mul',
        units.YARDS : '72 36 mul',
        units.MILES : '72 12 5280 mul mul'
        }

    def __init__(self, plot):
        if not isinstance(plot, plotfile.Plot):
            raise TypeError, "Invalid Plot object: " + `plot`
        self.__plot = plot
        self.__bounds = None
        self.__size = None
        self.__scale = None
        self.__factor = None

    def finish(self):
        self.__plot = None

    def _getBounds(self):
        if self.__bounds is not None:
            return
        _bounds = self.__plot.getBounds()
        if _bounds is None:
            raise ValueError, "Plot boundary not defined."
        self.__bounds = _bounds

    def setSize(self, size):
        if self.__size is not None:
            return
        if not isinstance(size, str):
            raise TypeError, "Invalid plot size string: " + `size`
        if size not in PSPlot.__papersizes:
            raise KeyError, "Invalid plot size: %s" % size
        self.__size = size

    def getPaperSizes(self):
        return PSPlot.__papersizes.keys()

    def getPaperSize(self):
        if self.__size is None:
            raise ValueError, "Paper size not defined."
        return PSPlot.__papersizes[self.__size]

    def _calcScale(self):
        if self.__scale is not None:
            return
        if self.__size is None:
            raise ValueError, "Paper size not defined."
        _plot = self.__plot
        _bounds = self.__bounds
        if _bounds is None:
            _bounds = _plot.getBounds()
            if _bounds is None:
                raise ValueError, "Plot boundary not defined."
        _xmin, _ymin, _xmax, _ymax = _bounds
        # print "xmin: %g" % _xmin
        #  print "ymin: %g" % _ymin
        # print "xmax: %g" % _xmax
        # print "ymax: %g" % _ymax
        _w, _h = PSPlot.__papersizes[self.__size]
        if _plot.getLandscapeMode():
            _w, _h = _h, _w
        # print "w: %d; h: %d" % (_w, _h)
        _units = _plot.getUnits()
        # print "units: %d" % _units
        if _units == units.MILLIMETERS:
            _fac = 72.0/25.4
        elif _units == units.MICROMETERS:
            _fac = 72.0/(25.4 * 1000.0)
        elif _units == units.METERS:
            _fac = 72.0/(25.4/1000.0)
        elif _units == units.INCHES:
            _fac = 72.0
        elif _units == units.FEET:
            _fac = 72.0 * 12
        elif _units == units.YARDS:
            _fac = 72.0 * 36
        elif _units == units.MILES:
            _fac = 72.0 * 12 * 5280
        else:
            raise ValueError, "Unexpected unit: %s" % _units
        self.__factor = _fac
        # print "factor: %g" % _fac

        if _w == 0 and _h == 0:
            _ymin = 0
            _xmin = 0
            _s = 1
        else:
            _xs = _fac * ((_xmax - _xmin)/float(_w))
            _ys = _fac * ((_ymax - _ymin)/float(_h))
            # print "xs: %g; ys: %g" % (_xs, _ys)
            _s = 1.0/max(_xs, _ys)
        self.__scale = _s
        # print "scale: %g" % self.__scale
        self.__matrix = ((_s * _fac),
                         -(_xmin * _s * _fac),
                         -(_ymin * _s * _fac))
        # print "matrix: " + str(self.__matrix)

    def write(self, f):
        if False and not isinstance(f, file):
            raise TypeError, "Invalid file object: " + `f`
        if self.__size is None:
            raise ValueError, "Plot size not defined"
        self._getBounds()
        _xmin, _ymin, _xmax, _ymax = self.__bounds
        self._calcScale()
        _w, _h = PSPlot.__papersizes[self.__size]
        _plot = self.__plot
        if _plot.getLandscapeMode():
            _w, _h = _h, _w
        #
        # header
        #
        f.write("%!PS-Adobe-1.0\n")
        f.write("%%Creator: PythonCAD\n")
        f.write("%%CreationDate: %s\n" % time.asctime())
        f.write("%%BoundingBox: 0 0 %d %d\n" % (_w, _h))
        f.write("%%EndComments\n")
        # add in Prologue
        _funcs = """%
/m {transform round exch round exch itransform moveto} bind def
/l {transform round exch round exch itransform lineto} bind def
%
/ljust
  { 0 begin
      /s exch def
      /y exch def
      /x exch def
      x y m
      s show
    end
  } def
/ljust load 0 3 dict put
%
/cjust
  { 0 begin
      /s exch def
      /w exch def
      /y exch def
      /x exch def
      /dx {w s stringwidth pop 2 div sub} def
      x dx add y m
      s show
    end
  } def
/cjust load 0 5 dict put
%
/rjust
  { 0 begin
      /s exch def
      /w exch def
      /y exch def
      /x exch def
      /dx {w s stringwidth pop sub} def
      x dx add y m
      s show
    end
  } def
/rjust load 0 5 dict put
"""
        f.write("%s" % _funcs)
        f.write("%\n% Plot specs\n%\n")
        f.write("%% (xmin, ymin): (%g, %g)\n" % (_xmin, _ymin))
        f.write("%% (xmax, ymax): (%g, %g)\n" % (_xmax, _ymax))
        f.write("%%\n%% unit scale factor: %g\n" % self.__factor)
        f.write("%% fit factor: %g\n" % self.__scale)
        f.write("%%EndProlog\n")
        f.write("%\n% Line defaults\n%\n")
        f.write("1 setlinecap\n")
        f.write("1 setlinejoin\n")
        if _plot.getLandscapeMode():
            f.write("%\n% Landscape mode transformation\n%\n")
            f.write("90 rotate\n0 -%d translate\n" % _h)

        #
        # draw entities
        #
        if 'segments' in _plot:
            self._write_segments(f, _plot)
        if 'circles' in _plot:
            self._write_circles(f, _plot)
        if 'arcs' in _plot:
            self._write_arcs(f, _plot)
        if 'leaders' in _plot:
            self._write_leaders(f, _plot)
        if 'polylines' in _plot:
            self._write_polylines(f, _plot)
        if 'chamfers' in _plot:
            self._write_chamfers(f, _plot)
        if 'fillets' in _plot:
            self._write_fillets(f, _plot)
        if 'textblocks' in _plot:
            self._write_textblocks(f, _plot)
        if 'ldims' in _plot:
            self._write_ldims(f, _plot)
        if 'rdims' in _plot:
            self._write_rdims(f, _plot)
        if 'adims' in _plot:
            self._write_adims(f, _plot)
        f.write("showpage\n")
        f.flush()

    def _write_graphic_data(self, f, c, l, t):
        if c is not None:
            if not isinstance(c, tuple):
                raise TypeError, "Color argument not a tuple: " + str(c)
            if len(c) != 3:
                raise ValueError, "Unexpected color tuple length: " + str(c)
            if c[0] != 0 or c[1] != 0 or c[2] != 0:
                _r = c[0]/255.0
                _g = c[1]/255.0
                _b = c[2]/255.0
                f.write("%.06f %.06f %.06f setrgbcolor\n" % (_r, _g, _b))
        if l is not None:
            if not isinstance(l, list):
                raise TypeError, "Linetype argument not a list: " + str(l)
            f.write("[")
            for _i in l:
                if not isinstance(_i, int):
                    raise TypeError, "Invalid dash list type: " + str(_i)
                f.write(" %d " % _i)
            f.write("] 0 setdash\n")
        _th = int(t * self.__factor * self.__scale)
        if _th < 1:
            _th = 1
        f.write("%d setlinewidth\n" % _th)

    def _write_segments(self, f, plot):
        f.write("%\n% segments\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _s in plot.getPlotEntities('segments'):
            _x1, _y1, _x2, _y2, _c, _lt, _t = _s
            f.write("%\n% data:\n")
            f.write("%% (x1, y1): (%g, %g)\n" % (_x1, _y1))
            f.write("%% (x2, y2): (%g, %g)\n" % (_x2, _y2))
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x1 * _sf) + _dx
            _yt = (_y1 * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _xt = (_x2 * _sf) + _dx
            _yt = (_y2 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            f.write("stroke\ngrestore\n")

    def _write_circles(self, f, plot):
        f.write("%\n% circles\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _c in plot.getPlotEntities('circles'):
            _x, _y, _r, _c, _lt, _t = _c
            f.write("%\n% data:\n")
            f.write("%% (xc, yc): (%g, %g)\n" % (_x, _y))
            f.write("%% radius: %g\n" % _r)
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            _rt = _r * _sf
            f.write("%g %g %g 0 360 arc\n" % (_xt, _yt, _rt))
            f.write("stroke\ngrestore\n")

    def _write_arcs(self, f, plot):
        f.write("%\n% arcs\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _a in plot.getPlotEntities('arcs'):
            _x, _y, _r, _sa, _ea, _c, _lt, _t = _a
            f.write("%\n% data:\n")
            f.write("%% (xc, yc): (%g, %g)\n" % (_x, _y))
            f.write("%% radius: %g\n" % _r)
            f.write("%% start angle: %g\n" % _sa)
            f.write("%% end angle: %g\n" % _ea)
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            _rt = _r * _sf
            f.write("%g %g %g %g %g arc\n" % (_xt, _yt, _rt, _sa, _ea))
            f.write("stroke\ngrestore\n")

    def _write_leaders(self, f, plot):
        f.write("%\n% leaders\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _l in plot.getPlotEntities('leaders'):
            _x1, _y1, _x2, _y2, _x3, _y3, _ax1, _ay1, _ax2, _ay2, _c, _lt, _t = _l
            f.write("%\n% data:\n")
            f.write("%% (x1, y1): (%g, %g)\n" % (_x1, _y1))
            f.write("%% (x2, y2): (%g, %g)\n" % (_x2, _y2))
            f.write("%% (x3, y3): (%g, %g)\n" % (_x3, _y3))
            f.write("%\n% arrow pts:%\n")
            f.write("%% (x1, y1): (%g, %g)\n" % (_ax1, _ay1))
            f.write("%% (x2, y2): (%g, %g)\n" % (_ax2, _ay2))
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x1 * _sf) + _dx
            _yt = (_y1 * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _xt = (_x2 * _sf) + _dx
            _yt = (_y2 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            _xt = (_x3 * _sf) + _dx
            _yt = (_y3 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            f.write("currentpoint\nstroke\nmoveto\n")
            _xt = (_ax1 * _sf) + _dx
            _yt = (_ay1 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            _xt = (_ax2 * _sf) + _dx
            _yt = (_ay2 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            f.write("closepath\nfill\ngrestore\n")

    def _write_polylines(self, f, plot):
        f.write("%\n% polylines\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _p in plot.getPlotEntities('polylines'):
            _pts, _c, _lt, _t = _p
            f.write("%\n% data:\n")
            f.write("%% length: %d\n" % len(_pts))
            for _pt in _pts:
                f.write("%% (x, y): (%g, %g)\n" % (_pt[0], _pt[1]))
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _x, _y = _pts[0]
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            for _t in _pts[1:]:
                _x, _y = _t
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\n" % (_xt, _yt))
            f.write("stroke\ngrestore\n")

    def _write_chamfers(self, f, plot):
        f.write("%\n% chamfers\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _c in plot.getPlotEntities('chamfers'):
            _x1, _y1, _x2, _y2, _c, _lt, _t = _c
            f.write("%\n% data:\n")
            f.write("%% (x1, y1): (%g, %g)\n" % (_x1, _y1))
            f.write("%% (x2, y2): (%g, %g)\n" % (_x2, _y2))
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x1 * _sf) + _dx
            _yt = (_y1 * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _xt = (_x2 * _sf) + _dx
            _yt = (_y2 * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            f.write("stroke\ngrestore\n")

    def _write_fillets(self, f, plot):
        f.write("%\n% fillets\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _f in plot.getPlotEntities('fillets'):
            _x, _y, _r, _sa, _ea, _c, _lt, _t = _f
            f.write("%\n% data:\n")
            f.write("%% (xc, yc): (%g, %g)\n" % (_x, _y))
            f.write("%% radius: %g\n" % _r)
            f.write("%% start angle: %g\n" % _sa)
            f.write("%% end angle: %g\n" % _ea)
            f.write("gsave\n")
            self._write_graphic_data(f, _c, _lt, _t)
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            _rt = _r * _sf
            f.write("%g %g %g %g %g arc\n" % (_xt, _yt, _rt, _sa, _ea))
            f.write("stroke\ngrestore\n")

    def _write_tblock(self, f, tbdata):
        _sf, _dx, _dy = self.__matrix
        _font = tbdata['font']
        _size = tbdata['size']
        _fontsize = _size * _sf
        f.write("/%s findfont %g scalefont setfont\n" % (_font, _fontsize))
        _c = tbdata['color']
        if _c is not None:
            if not isinstance(_c, tuple):
                raise TypeError, "Color argument not a tuple: " + str(_c)
            if len(_c) != 3:
                raise ValueError, "Unexpected color tuple length: " + str(_c)
            if _c[0] != 0 or _c[1] != 0 or _c[2] != 0:
                _r = _c[0]/255.0
                _g = _c[1]/255.0
                _b = _c[2]/255.0
                f.write("%.06f %.06f %.06f setrgbcolor\n" % (_r, _g, _b))
        _text = tbdata['text']
        _align = tbdata['align']
        _x, _y = tbdata['location']
        _xt = (_x * _sf) + _dx
        _i = 1
        if len(_text) == 1 or _align == 'left':
            for _t in _text:
                _yt = ((_y - (_i * _size)) * _sf) + _dy
                f.write("%g %g (%s) ljust\n" % (_xt, _yt, _t))
                _i = _i + 1
        else:
            _w, _h = tbdata['bounds']
            _pw = _w * _sf # bounds width in points
            for _t in _text:
                _yt = ((_y - (_i * _size)) * _sf) + _dy
                if _align == 'center':
                    f.write("%g %g %g (%s) cjust\n" % (_xt, _yt, _pw, _t))
                else:
                    f.write("%g %g %g (%s) rjust\n" % (_xt, _yt, _pw, _t))
                _i = _i + 1

    def _write_textblocks(self, f, plot):
        f.write("%\n% textblocks\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _tbdata in plot.getPlotEntities('textblocks'):
            f.write("%\n% TextBlock:\n")
            f.write("%% (x, y): %s\n" % str(_tbdata['location']))
            f.write("%% bounds: %s\n" % str(_tbdata['bounds']))
            f.write("%% font: %s\n" % _tbdata['font'])
            f.write("%% color: %s\n" % str(_tbdata['color']))
            f.write("%% alignment: %s\n" % _tbdata['align'])
            f.write("%% size: %g\n" % _tbdata['size'])
            f.write("%% text\n")
            for _t in _tbdata['text']:
                f.write("%%\t%s\n" % _t)
            f.write("%\n")
            f.write("gsave\n")
            self._write_tblock(f, _tbdata)
            f.write("grestore\n")

    def _write_dim_markers(self, f, mdata):
        _mtype = mdata['type']
        _sf, _dx, _dy = self.__matrix
        if _mtype is not None:
            #
            # if 'rdim' is in the mdata dictionary, then the data
            # is for a RadialDimension and only the second marker
            # should be printed
            #
            _rdim = mdata.get('rdim')
            f.write("%%\n%% marker: %s\n" % _mtype)
            if _mtype == 'arrow':
                f.write("%% p1: %s\n" % str(mdata['p1']))
                f.write("%% p2: %s\n" % str(mdata['p2']))
                f.write("%% v1: %s\n" % str(mdata['v1']))
                f.write("%% p3: %s\n" % str(mdata['p3']))
                f.write("%% p4: %s\n" % str(mdata['p4']))
                f.write("%% v2: %s\n" % str(mdata['v2']))
                if _rdim is None:
                    _x, _y = mdata['p1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g m\n" % (_xt, _yt))
                    _x, _y = mdata['v1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g l\n" % (_xt, _yt))
                    _x, _y = mdata['p2']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g l\nstroke\n" % (_xt, _yt))
                #
                _x, _y = mdata['p3']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g m\n" % (_xt, _yt))
                _x, _y = mdata['v2']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\n" % (_xt, _yt))
                _x, _y = mdata['p4']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\nstroke\n" % (_xt, _yt))
            elif _mtype == 'filled_arrow':
                f.write("%% p1: %s\n" % str(mdata['p1']))
                f.write("%% p2: %s\n" % str(mdata['p2']))
                f.write("%% v1: %s\n" % str(mdata['v1']))
                f.write("%% p3: %s\n" % str(mdata['p3']))
                f.write("%% p4: %s\n" % str(mdata['p4']))
                f.write("%% v2: %s\n" % str(mdata['v2']))
                if _rdim is None:
                    _x, _y = mdata['p1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g m\n" % (_xt, _yt))
                    _x, _y = mdata['p2']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g l\n" % (_xt, _yt))
                    _x, _y = mdata['v1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g l\nclosepath\nfill\n" % (_xt, _yt))
                #
                _x, _y = mdata['p3']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g m\n" % (_xt, _yt))
                _x, _y = mdata['p4']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\n" % (_xt, _yt))
                _x, _y = mdata['v2']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\nclosepath\nfill\n" % (_xt, _yt))
            elif _mtype == 'slash':
                f.write("%% p1: %s\n" % str(mdata['p1']))
                f.write("%% p2: %s\n" % str(mdata['p2']))
                f.write("%% p3: %s\n" % str(mdata['p3']))
                f.write("%% p4: %s\n" % str(mdata['p4']))
                if _rdim is None:
                    _x, _y = mdata['p1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g m\n" % (_xt, _yt))
                    _x, _y = mdata['p2']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    f.write("%g %g l\nstroke\n" % (_xt, _yt))
                #
                _x, _y = mdata['p3']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g m\n" % (_xt, _yt))
                _x, _y = mdata['p4']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                f.write("%g %g l\nstroke\n" % (_xt, _yt))
            elif _mtype == 'circle':
                f.write("%% radius: %g\n" % mdata['radius'])
                f.write("%% c1: %s\n" % str(mdata['c1']))
                f.write("%% c2: %s\n" % str(mdata['c2']))
                _r = mdata['radius']
                if _rdim is None:
                    _x, _y = mdata['c1']
                    _xt = (_x * _sf) + _dx
                    _yt = (_y * _sf) + _dy
                    _rt = _r * _sf
                    f.write("%g %g %g 0 360 arc\nfill\n" % (_xt, _yt, _rt))
                #
                _x, _y = mdata['c2']
                _xt = (_x * _sf) + _dx
                _yt = (_y * _sf) + _dy
                _rt = _r * _sf
                f.write("%g %g %g 0 360 arc\nfill\n" % (_xt, _yt, _rt))
            else:
                raise ValueError, "Unexpected marker type: %s" % _mtype

    def _write_dimstrings(self, f, dimdata):
        _sf, _dx, _dy = self.__matrix
        #
        # erase where the dim text will go
        #
        f.write("gsave\n")
        _tb1 = dimdata['ds1']
        _tb2 = dimdata.get('ds2')
        _x, _y = _tb1['location']
        _w, _h = _tb1['bounds']
        if _tb2 is None:
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            _pw = _w * _sf
            _ph = _h * _sf
            f.write("%g %g m\n" % (_xt, _yt))
            f.write("0 -%g rlineto\n" % _ph)
            f.write("%g 0 rlineto\n" % _pw)
            f.write("0 %g rlineto\n" % _ph)
        else:
            _x2, _y2 = _tb2['location']
            _w2, _h2 = _tb2['bounds']
            _xmin = min(_x, _x2)
            _xmax = max((_x + _w), (_x2 + _w2))
            _ymin = _y2 - _h2
            _ymax = _y
            _xt = (_xmin * _sf) + _dx
            _yt = (_ymin * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _xt = (_xmax * _sf) + _dx
            _yt = (_ymin * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            _xt = (_xmax * _sf) + _dx
            _yt = (_ymax * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
            _xt = (_xmin * _sf) + _dx
            _yt = (_ymax * _sf) + _dy
            f.write("%g %g l\n" % (_xt, _yt))
        f.write("closepath\n1 setgray fill\ngrestore\n")
        #
        # print ds1 dimension
        #
        f.write("%\n% DimString 1:\n")
        f.write("%% (x, y): %s\n" % str(_tb1['location']))
        f.write("%% bounds: %s\n" % str(_tb1['bounds']))
        f.write("%% font: %s\n" % _tb1['font'])
        f.write("%% color: %s\n" % str(_tb1['color']))
        f.write("%% alignment: %s\n" % _tb1['align'])
        f.write("%% size: %g\n" % _tb1['size'])
        f.write("%% text\n")
        for _t in _tb1['text']:
            f.write("%%\t%s\n" % _t)
        f.write("gsave\n")
        self._write_tblock(f, _tb1)
        f.write("grestore\n")
        if _tb2 is not None:
            f.write("%\n% DimString 2:\n")
            f.write("%% (x, y): %s\n" % str(_tb2['location']))
            f.write("%% bounds: %s\n" % str(_tb2['bounds']))
            f.write("%% font: %s\n" % _tb2['font'])
            f.write("%% color: %s\n" % str(_tb2['color']))
            f.write("%% alignment: %s\n" % _tb2['align'])
            f.write("%% size: %g\n" % _tb2['size'])
            f.write("%% text\n")
            for _t in _tb1['text']:
                f.write("%%\t%s\n" % _t)
            f.write("gsave\n")
            self._write_tblock(f, _tb2)
            f.write("grestore\n")

    def _write_ldims(self, f, plot):
        f.write("%\n% linear dimensions\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _dimdata in plot.getPlotEntities('ldims'):
            f.write("%\n% data:\n")
            f.write("% first dimbar:\n")
            f.write("%% (x1, y1): %s\n" % str(_dimdata['ep1']))
            f.write("%% (x2, y2): %s\n" % str(_dimdata['ep2']))
            f.write("% second dimbar:\n")
            f.write("%% (x1, y1): %s\n" % str(_dimdata['ep3']))
            f.write("%% (x2, y2): %s\n" % str(_dimdata['ep4']))
            f.write("% crossbar:\n")
            f.write("%% (x1, y1): %s\n" % str(_dimdata['ep5']))
            f.write("%% (x2, y2): %s\n" % str(_dimdata['ep6']))
            f.write("gsave\n")
            _c = _dimdata['color']
            _t = _dimdata['thickness']
            self._write_graphic_data(f, _c, None, _t)
            _x, _y = _dimdata['ep1']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep2']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            _x, _y = _dimdata['ep3']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep4']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            _x, _y = _dimdata['ep5']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep6']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            self._write_dim_markers(f, _dimdata['markers'])
            f.write("grestore\n")
            self._write_dimstrings(f, _dimdata)

    def _write_rdims(self, f, plot):
        f.write("%\n% radial dimensions\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _dimdata in plot.getPlotEntities('rdims'):
            f.write("%\n% data:\n")
            f.write("% dimbar:\n")
            f.write("%% (x1, y1): %s)\n" % str(_dimdata['ep1']))
            f.write("%% (x2, y2): %s)\n" % str(_dimdata['ep2']))
            f.write("gsave\n")
            _c = _dimdata['color']
            _t = _dimdata['thickness']
            self._write_graphic_data(f, _c, None, _t)
            _x, _y = _dimdata['ep1']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep2']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            self._write_dim_markers(f, _dimdata['markers'])
            f.write("grestore\n")
            self._write_dimstrings(f, _dimdata)

    def _write_adims(self, f, plot):
        f.write("%\n% angular dimensions\n%\n")
        _sf, _dx, _dy = self.__matrix
        for _dimdata in plot.getPlotEntities('adims'):
            f.write("%\n% data:\n")
            f.write("% first dimbar:\n")
            f.write("%% (x1, y1): %s\n" % str(_dimdata['ep1']))
            f.write("%% (x2, y2): %s\n" % str(_dimdata['ep2']))
            f.write("% second dimbar:\n")
            f.write("%% (x1, y1): %s\n" % str(_dimdata['ep3']))
            f.write("%% (x2, y2): %s\n" % str(_dimdata['ep4']))
            f.write("% crossarc:\n")
            f.write("%% (xc, yc): %s\n" % str(_dimdata['vp']))
            f.write("%% radius: %g\n" % _dimdata['r'])
            f.write("%% start angle: %g\n" % _dimdata['sa'])
            f.write("%% end angle: %g\n" % _dimdata['ea'])
            f.write("gsave\n")
            _c = _dimdata['color']
            _t = _dimdata['thickness']
            self._write_graphic_data(f, _c, None, _t)
            _x, _y = _dimdata['ep1']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep2']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            _x, _y = _dimdata['ep3']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g m\n" % (_xt, _yt))
            _x, _y = _dimdata['ep4']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            f.write("%g %g l\nstroke\n" % (_xt, _yt))
            _x, _y = _dimdata['vp']
            _xt = (_x * _sf) + _dx
            _yt = (_y * _sf) + _dy
            _r = _dimdata['r']
            _rt = _r * _sf
            _sa = _dimdata['sa']
            _ea = _dimdata['ea']
            f.write("%g %g %g %g %g arc\nstroke\n" % (_xt, _yt, _rt, _sa, _ea))
            self._write_dim_markers(f, _dimdata['markers'])
            f.write("grestore\n")
            self._write_dimstrings(f, _dimdata)
