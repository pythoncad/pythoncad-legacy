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
# This module provide basic pythoncadObject
#
from Kernel.GeoEntity.style             import Style
from Kernel.exception                   import EntityMissing

class PyCadObject(object):
    """
        This class provide basic information for all the pythoncad object 
    """
    def __init__(self,objId,style,eType,properties={}):
        from Kernel.initsetting import OBJECT_STATE
        self.OBJECT_STATE=OBJECT_STATE
        self.__entityId=objId
        self.__state="MODIFIE"
        self._index=0
        self.__visible=1
        self.__style=style
        self.__entType=eType
        self.__properties=properties

    
    def addPropertie(self,name,value):
        """
            add a properties to the object
        """
        self.__properties[name]=value
        
    def getPropertie(self,name):
        """
            get the properties with a given name
        """
        if name in self.__properties:
            return self.__properties[name]
        raise EntityMissing("No entity with name %s"%str(name))

    def resetProperty(self):
        """
            reset the property 
        """
        self.__properties={}

    @property
    def properties(self):
        """
            get all the properties from the entity
        """
        return self.__properties
    
    def setVisible(self, visible):
        """
            set the visible value
        """
        self.__visible=visible
    def getVisible(self):
        """
            get the visible value
        """
        return self.__visible
    visible=property(getVisible, setVisible, None,"Set/Get the entity visibiolity")

    def getId(self):
        """
            get the entity id
        """
        return self.__entityId
    
    def getState(self):
        """
            get the active entity state
        """
        return self.__state
        
    def setState(self, state):
        """
            set the active state
        """ 
        if state in self.OBJECT_STATE:
            self.__state=state
        else:
            print "Wrong argunent"
            raise 
            
    state=property(getState, setState, None, "Get/Set the state of the entity")
    
    def getIndex(self):
        """
            get the index of the revision index of the current object
        """
        return self._index
    
    def getNewIndex(self):
        """
            Get the new index of the current entity
        """
        if self._index:
            self._index+=self._index
            self.__state=self.OBJECT_STATE[0]
        else: 
            self._index=0
            self.__state=self.OBJECT_STATE[0]
    
    def setIndex(self,index):
        """
            Set The index of the entity
        """
        if index:
            self._index=index
    index=property(getIndex, setIndex, "Get The new index of the current entity")
    
    def delete(self):
        """
            mark the entity to delete
        """
        self.__state='DELETE'
    
    def relese(self):
        """
            mark the entity as released
        """
        self.__state='RELEASED'
    def getStyle(self):
        """
            get the object EntityStyle
        """
        return self.__style

    def setStyle(self,style):
        """
            set/update the entitystyle
        """
        self.__style=style

    style=property(getStyle,setStyle,None,"Get/Set the entity style")

    def getInnerStyle(self):
        """
            return the inner style of type Style
        """
        if self.style!=None:
            styleEnt=self.style.getConstructionElements() 
            return styleEnt[styleEnt.keys()[0]]
        else:
            return None
            
    def setEntType(self, type):
        """
            Set the entity type
        """
        self.__entType=type
        
    def getEntityType(self):
        """
            Get the entity type
        """
        return self.__entType

    eType=property(getEntityType,setEntType,None,"Get/Set the etity type ")
