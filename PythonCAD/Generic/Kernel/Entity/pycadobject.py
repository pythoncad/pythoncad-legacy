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
OBJECT_STATE=['MODIFIE','RELESED', 'DELETE']

class PyCadObject(object):
    """
        This class provide basic information usefoul for the
        db like id for exsample
    """
    def __init__(self,objId,):
        self.__entityId=objId
        self.__state="MODIFIE"
        self.__index=0
        
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
        if state in OBJECT_STATE:
            self.__state=state
        else:
            print "Wrong argunent"
            raise 
            
    state=property(getState, setState, None, "Get/Set the state of the entity")
    
    def getIndex(self):
        """
            get the index of the revision index of the current object
        """
        return self.__index
    
    def getNewIndex(self):
        """
            Get the new index of the current entity
        """
        if index :
            self.__index+=self.__index
            self.__state=OBJECT_STATE[0]
        else: 
            self.__index=0
            self.__state=OBJECT_STATE[0]
    
    def setIndex(self,index):
        """
            Set The index of the entity
        """
        if index:
            self.__index=index
    index=property(getIndex, setIndex, "Get The new index of the current entity")
    
    def delete(self):
        """
            mark the entity to delete
        """
        self.__state='DELETE'
