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
# code for adding graphical methods to drawing entities
#

import types
from math import pi
_dtr = (pi/180.0)

import pygtk
pygtk.require('2.0')
#import gtk
#import pango

#from PythonCAD.Generic import color
from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import segjoint
#from PythonCAD.Generic import conobject
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer

# draw imports
from PythonCAD.Interface.Viewport.aclinedraw import _draw_acline, _erase_acline
from PythonCAD.Interface.Viewport.arcdraw import _draw_arc, _erase_arc
from PythonCAD.Interface.Viewport.circledraw import _draw_circle,_erase_circle
from PythonCAD.Interface.Viewport.ccircledraw import _draw_ccircle,_erase_ccircle
from PythonCAD.Interface.Viewport.chamferdraw import _draw_chamfer, _erase_chamfer
from PythonCAD.Interface.Viewport.clinedraw import _draw_cline, _erase_cline
from PythonCAD.Interface.Viewport.dimdraw import _draw_ldim, _draw_rdim, _draw_adim, _draw_dimstrings, _erase_dim
from PythonCAD.Interface.Viewport.filletdraw import _draw_fillet, _erase_fillet
from PythonCAD.Interface.Viewport.hclinedraw import _draw_hcline, _erase_hcline
from PythonCAD.Interface.Viewport.leaderdraw import _draw_leader, _erase_leader
from PythonCAD.Interface.Viewport.pointdraw import _draw_point, _erase_point
from PythonCAD.Interface.Viewport.polylinedraw import _draw_polyline, _erase_polyline
from PythonCAD.Interface.Viewport.segmentdraw import _draw_segment, _erase_segment
from PythonCAD.Interface.Viewport.textblockdraw import _draw_textblock, _erase_textblock, _format_layout
from PythonCAD.Interface.Viewport.vclinedraw import _draw_vcline, _erase_vcline



#from PythonCAD.Interface.Gtk import gtkimage


class ViewportDraw(object):
#----------------------------------------------------------------------------------------------------
    def __init__(self, image):
        # Generic.Image
        self.__image = image
        # cairo context
        self.__ctx = None
        # viewport dimensions
        self.__xmin = 0
        self.__ymin = 0
        self.__xmax = 0
        self.__ymax = 0
        # initialize entity drawing methods
        self.__init_draw_methods()

#----------------------------------------------------------------------------------------------------
    def __init_draw_methods(self):
        """
        Add draw methods to the entity classes
        """
        _class = point.Point
        _class.draw = types.MethodType(_draw_point, None, _class)
        _class.erase = types.MethodType(_erase_point, None, _class)
        _class = segment.Segment
        _class.draw = types.MethodType(_draw_segment, None, _class)
        _class.erase = types.MethodType(_erase_segment, None, _class)
        _class = circle.Circle
        _class.draw = types.MethodType(_draw_circle, None, _class)
        _class.erase = types.MethodType(_erase_circle, None, _class)
        _class = arc.Arc
        _class.draw = types.MethodType(_draw_arc, None, _class)
        _class.erase = types.MethodType(_erase_arc, None, _class)
        _class = leader.Leader
        _class.draw = types.MethodType(_draw_leader, None, _class)
        _class.erase = types.MethodType(_erase_leader, None, _class)
        _class = polyline.Polyline
        _class.draw = types.MethodType(_draw_polyline, None, _class)
        _class.erase = types.MethodType(_erase_polyline, None, _class)
        _class = segjoint.Chamfer
        _class.draw = types.MethodType(_draw_chamfer, None, _class)
        _class.erase = types.MethodType(_erase_chamfer, None, _class)
        _class = segjoint.Fillet
        _class.draw = types.MethodType(_draw_fillet, None, _class)
        _class.erase = types.MethodType(_erase_fillet, None, _class)
        _class = hcline.HCLine
        _class.draw = types.MethodType(_draw_hcline, None, _class)
        _class.erase = types.MethodType(_erase_hcline, None, _class)
        _class = vcline.VCLine
        _class.draw = types.MethodType(_draw_vcline, None, _class)
        _class.erase = types.MethodType(_erase_vcline, None, _class)
        _class = acline.ACLine
        _class.draw = types.MethodType(_draw_acline, None, _class)
        _class.erase = types.MethodType(_erase_acline, None, _class)
        _class = cline.CLine
        _class.draw = types.MethodType(_draw_cline, None, _class)
        _class.erase = types.MethodType(_erase_cline, None, _class)
        _class = ccircle.CCircle
        _class.draw = types.MethodType(_draw_ccircle, None, _class)
        _class.erase = types.MethodType(_erase_ccircle, None, _class)
        _class = text.TextBlock
        _class._formatLayout = types.MethodType(_format_layout, None, _class)
        _class.draw = types.MethodType(_draw_textblock, None, _class)
        _class.erase = types.MethodType(_erase_textblock, None, _class)
        _class = dimension.LinearDimension
        _class.draw = types.MethodType(_draw_ldim, None, _class)
        _class = dimension.RadialDimension
        _class.draw = types.MethodType(_draw_rdim, None, _class)
        _class = dimension.AngularDimension
        _class.draw = types.MethodType(_draw_adim, None, _class)
        _class = dimension.Dimension
        _class.erase = types.MethodType(_erase_dim, None, _class)
        _class._drawDimStrings = types.MethodType(_draw_dimstrings, None, _class)
#        _class = layer.Layer
#        _class.draw = types.MethodType(_draw_layer, None, _class)
#        _class.erase = types.MethodType(_erase_layer, None, _class)
    


#---------------------------------------------------------------------------------------------------
    def __get_image(self):
        return self.__image

    Image = property(__get_image, None, None, "Generic Image")


#---------------------------------------------------------------------------------------------------
    def __get_ctx(self):
        return self.__ctx

    CairoContext = property(__get_ctx, None, None, "Cairo Context")


#---------------------------------------------------------------------------------------------------
    def WorldToViewport(self, x, y):
        return x, y

#---------------------------------------------------------------------------------------------------
    def draw(self, ctx):
        print "ViewportDraw.__draw()"
        # set transformations
#        ctx.translate(self.__cr_translate_x, self.__cr_translate_y)
#        print self.__cr_translate_x, self.__cr_translate_y
#        ctx.scale(self.__cr_scale_x, self.__cr_scale_y)
#        print self.__cr_scale_x, self.__cr_scale_y

        # the cairo context to use
        self.__ctx = ctx
        #
        active_layer = self.__image.getActiveLayer()
        # stack of layers
        layers = [self.__image.getTopLayer()]
        # iterate over stack of layers
        while (len(layers)):
            layer = layers.pop()
            if layer is not active_layer:
                # draw inactive layer
                self.__draw_layer(layer, self.__ctx)
            # add sublayers to the layer stack
            layers.extend(layer.getSublayers())
        # at last draw the active layer
        self.__draw_layer(active_layer)
        #
        # redraw selected entities
        #
        color = Color('#ff7733')
        for obj in self.__image.getSelectedObjects(False):
            obj.draw(self, color)
        self.refresh()

#---------------------------------------------------------------------------------------------------
    def __draw_layer(self, layer):
        print "ViewportDraw.__draw_layer()"
#        # is it a layer object
#        if not isinstance(layer, Layer):
#            raise TypeError, "Invalid layer type: " + `type(layer)`
#        # layer must belong to the image
#        if layer.getParent() is not self.__image:
#            raise ValueError, "Layer not found in Image"
#        # only draw visible layers
#        if layer.isVisible():
#            color = self.__image.getOption('INACTIVE_LAYER_COLOR')
#            if layer is self.__image.getActiveLayer():
#                color = None
#            # draw the points
#            for obj in layer.getLayerEntities("point"):
#                if obj.isVisible():
#                    iobj = IPoint(ctx, obj)
#                    iobj.draw(color)
        if not isinstance(layer, Layer):
            raise TypeError, "Invalid layer type: " + `type(layer)`
        if layer.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        if layer.isVisible():
            _col = self.__image.getOption('INACTIVE_LAYER_COLOR')
            if layer is self.__image.getActiveLayer():
                _col = None
            _cobjs = []
            _objs = []
            _pts = []
            for _obj in layer.objsInRegion(self.__xmin, self.__ymin, self.__xmax, self.__ymax):
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
