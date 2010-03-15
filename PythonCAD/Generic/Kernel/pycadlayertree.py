#!/usr/bin/env python
#
# Copyright (c) 2010 Matteo Boscolo
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
# This  module all the interface to store the layer
#
from Entity.layer import Layer

class PyCadLayerTree(object):
    """
        this class rappresent the layer tree strucrute
    """
    def __init__(self, mainLayer):
        layerId=mainLayer.getId()
        layerName=self._getLayerName(mainLayer)
        layer={'id':layerId,'name':layerName,'child':{}}
        self.__index={layerId:layer}
        self.mainLayer=layer
    
    def insert(self, layer, parentLayer):
        """
            Insert a new object in the class
        """
        layerId=layer.getId()
        layerName=self._getLayerName(layer)
        newLayer={'id':layerId,'name':layerName,'child':{}}
        self.__index[layerId]=newLayer
        parentId=parentLayer.getId()
        parentLayer=self.__index[parentId]
        parentChilds=parentLayer['child']
        parentChilds[layerId]=newLayer
    
    def _getLayerName(self, pyCadEnt):
        """
            Retrive the layer name from the given pycadent
        """
        unpickleLayers=pyCadEnt.getConstructionElements()
        for key in unpickleLayers:
            return unpickleLayers[key].name
        return None
        
    def getLayerChildren(self, layerId=None, layerName=None):
        """
            get the layer children
        """
        objDic={}
        if layerId:
            objDic=self.__index[layerId]
        if layerName:
            keyFound=[keyId for keyId in self.__index if self.__index[keyId]['name']==layerName]
            if len(keyFound):
                objDic=self.__index[keyFound[0]]
        if objDic:
            return Layer(objDic['id'],objDic['name'])
        return None   
    
    def __repr__(self): 
        return '(%s @@ %s)'%(`self.__index`, `self.mainLayer`)

def testLayerClass():
    la=Layer(1, 'Main')
    lt=LayerTree(la)
    la1=Layer(2, 'Layer_1')
    la2=Layer(3, 'Layer_2')
    la3=Layer(4, 'Layer_3')
    la4=Layer(5, 'Layer_4')
    lt.insert(la1, la)
    lt.insert(la2,  la)
    
    lr2= lt.getLayerChildren(layerName='Layer_2')
    lt.insert(la3,lr2)
    lt.insert(la4,lr2)

    print "lt", str(lt)
    print "cildren", lt.getLayerChildren(1).getName()
    print "cildren", lt.getLayerChildren(layerName='Layer_4').getName()
    
    


class Layer(object):
    def __init__(self, idl, name):
        self.idl=idl
        self.name=name
    def getId(self):
        return self.idl
    def getName(self):
        return self.name
        
if __name__=='__main__':    
    testLayerClass()
