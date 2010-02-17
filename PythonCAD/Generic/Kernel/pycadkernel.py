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
# This  module all the interface needed to talk with pythoncad database
#

import os
import sys
import cPickle
import logging
from  pycadundodb import PyCadUndoDb

PY_CAD_ENT=['POINT','SEGMENT']

LEVELS = {'PyCad_Debug': logging.DEBUG,
          'PyCad_Info': logging.INFO,
          'PyCad_Warning': logging.WARNING,
          'PyCad_Error': logging.ERROR,
          'PyCad_Critical': logging.CRITICAL}

#set the debug level 
level = LEVELS.get('PyCad_Error', logging.NOTSET) 
logging.basicConfig(level=level)
#



class PyCadPoint(object):
    """
        this class implement a geometrical point structure
        x: is a float
        y: is a float
        z: is a float
    """
    def __init__(self,x,y,z=None):
        self.__x=x
        self.__y=y
        self.__z=z
        
    def getXYCoords(self):
        """
            return a tuple of x,y point 
        """
        return (self.__x,self.__y)
    def setXY(self,x,y):
        """
            reassing the xy coords
        """    
        self.__x=x
        self.__y=y
    
   

class PyCadDbKernel(object):
    """
        this class provide basic operation on the pycad db database
        dbPath: is the path the database if None look in the some directory.
    """
    def __init__(self,dbPath=None):
        """
            init of the kernel
        """
        self.__logger=logging.getLogger('PyCadDbKernel')
        self.__logger.debug('__init__')
        if dbPath is None:
           dbPath='pythoncad.pdr' 
        if not os.path.exists(dbPath):
                self.__logger.error('Unable lo get the db %s'%str(dbPath))
                sys.exit()
        self.__logger.debug('Connect db')
        self.__connection = sql.connect(dbPath)
        #Check the database structure
        self.__logger.debug('check entity tables')
        self.checkEntityTable()
        #
        self.__activeStyleObj=PyCadStyle(0)
        # write all the entity 
        self.__logger.debug('set events')
        self.saveEntityEvent=PyCadkernelEvent()
        self.deleteEntityEvent=PyCadkernelEvent()
        self.__logger.debug('Done inizialization')

    def checkEntityTable(self):
        """
            check the structure of the entity table 
        """
        self.__logger.debug('checkEntityTable')
        #in case of empty db create the entity table
        #pycad_undo_index
        #pycad_entity_id
        #pycad_id
        #pycad_object_type
        #pycad_object_definition
        #pycad_style_id
        #pycad_security_id
        #pycad_locked
        return
        
    def getEntity(self,entityId):
        """
            get the entity from a given id
        """
        self.__logger.debug('getEntity')
        try:
            _cursor = self.__connection.cursor()
            _statement = """SELECT 
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                            FROM pycadent 
                            WHERE pycad_entity_id=%s"""%str(entityId)
            _rows = _cursor.execute(_statement)
            _row = _rows.fetchone()
            if _row is None:
                return None
            else:
                _pycadObjectDefinition=_row[2]
                _objUnpickle=cPickle.loads(_pycadObjectDefinition)
                _obj=PyCadEnt(_pycadObjectDefinition,_objUnpickle)
                return _obj
        except sql.Error, _e:
            self.__logger.error("Sql Error: %s"%str( _e.args[0] ))
        except :
            self.__logger.error("Generic Error: %s"%str( sys.args[0] ))

    def saveEntity(self,entity):
        """
            save the entity into the database
        """
        self.__logger.debug('saveEntity')
        try:
            self.__logger.debug('get entity id')
            _idParent=entity.getId()
            self.__logger.debug('id is %s'%str(_idParent))
            if _idParent is None:                               # Create a brand new entity
                self.saveEntIntoDb(_idParent,entity)            # Write the entity on the table
            else:                                               # The entity is on the db 
                # this implements the undo  progress
                # add new entity with the some entity id
                # incremente the undo index
                _entityType=type(entity)
                _constructionAttributes=entity.getInitAttributes()
                _dbEnt=self.getEntity(_idParent)
        except sql.Error, _e:
            self.__logger.error("Sql Error: %s"%str( _e.args[0] ))      
        except :
            for s in sys.exc_info():
                self.__logger.error("Generic Error: %s"%str(s))
            

    def saveEntIntoDb(self,entity_id,entity):
        """
            save the entity into the db
            entity_id id : of the entity
            entity       : entity to erite in the db
        """
        self.__logger.debug('saveEntIntoDb')
        _newUndoId=self.getNewUndoId()
        _newEnityId=self.getNewEntityId()
        _entityDump=cPickle.dumps(entity.getConstructionPoint(),2)
        _statement = """INSERT INTO pycadent
                    (pycad_entity_id,
                    pycad_object_type,
                    pycad_undo_index,
                    pycad_object_definition,pycad_style_id)
                    VALUES(%s,\"%s\",%s,\"%s\",%s)"""%(
            str(_newEnityId),
            str(type(entity)),
            str(_newUndoId),
            str(_entityDump),
            str(self.__activeStyleObj.getId())
            )      
        try:
            _res=self.makeSqlInsertUpdate(_statement)
        except:
            # Go back with the undo id 
            # so we do not have index hole douring undo
            # or think at a different way to store the undo sequence
            # may be is better to add a new row at the undo table 
            # and and in case of error just remove that index
            # so when we look at the undo index we need just to 
            # get the maximun undo value
            # may be the undo list could be :
            # idRow,EntityId,isActive max()
            pass

    def makeSqlInsertUpdate(self,sqlPhrase):
        """
            exec a sql phrase and manage all the errors
        """
        self.__logger.debug('makeSqlInsertUpdate')
        try:
            _cursor = self.__connection.cursor()    
            _cursor.execute(sqlPhrase)
            self.__connection.commit()
            return True
        except sql.Error, _e:
            self.__logger.error("Sql Phrase: %s"%str(sqlPhrase))       
            self.__logger.error("Sql Error: %s"%str( _e.args[0] ))
            return False
        except e:
            for s in sys.exc_info():
                self.__logger.error("Generic Error: %s"%str(s))
            return False
        
    def getNewUndoId(self):
        """
            get the new undo id from the db
        """
        self.__logger.debug('getNewUndoId')
        _cursor = self.__connection.cursor()
        _statement = """SELECT pycad_id from pycadundo""" 
        _rows = _cursor.execute(_statement)
        _row = _rows.fetchone()
        if _row is None:
            _undoId=0
            self.setUndoId(0)
        else:
            _undoId=_row[0]
            _undoId=_undoId+1
            self.setUndoId(_undoId)
        return _undoId
    
    def setUndoId(self,objId):
        """
            set the undo id in the table
        """
        self.__logger.debug('setUndoId')
        _statement="DELETE FROM pycadundo"
        _res=self.makeSqlInsertUpdate(_statement)
        if _res:
            _statement="INSERT INTO pycadundo (pycad_id) VALUES (%s)"%str(objId)
            _res=self.makeSqlInsertUpdate(_statement)

    def getNewEntityId(self):
        """
            get the new entity id reading from the entity table end
            gert the lasst id + 1
        """
        return 1
    def getActiveStyle(self):
        """
            Get the current style
        """
        self.__logger.debug('getActiveStyle')
        #return the id of the active style
        if self.__activeStyleObj==None:
            self.setActiveStyle(0) # in this case get the first style 
        return self.__activeStyleObj

    def setActiveStyle(self,id,name=None):
        """
            set the current style
        """
        self.__logger.debug('setActiveStyle')
        # check if the style id is in the db
        # if not create the style in the db with default settings
        # get from db the object style pickled
        # set in a global variable self.__activeStyleObj=_newStyle
        pass
        
    def getStyle(self,id,name=None):
        """
            get the style object 
        """
        #get the style object of the give id
        pass
    def getStyleList(self):
        """
            get all the style from the db
        """
        self.__logger.debug('getStyleList')
        # Make a query at the style Table and return an array of (stylesName,id)
        # this method is used for populate the style form ..
        pass
        
    activeStyleId=property(getActiveStyle,setActiveStyle)
 
class PyCadkernelEvent(object):
    """
        this class fire the envent from the python kernel
    """
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handler.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("PythonCad Handler is not handling this event.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount


def pyCadEntDb(PyCadBaseDb):
    """
        this class provide the besic operation for the entity
    """
    def __init__(self,dbConnection):
        PyCadBaseDb.__init__(self)
        if dbConnection is None:
            self.createConnection()
        else:
            self.setConnection(dbConnection)
        self.__logger=logging.getLogger('PyCadUndoDb')
        self.__logger.debug('__init__')
       
        _sqlCheck="""select * from sqlite_master where name like 'pycadent'"""
        _table=self.makeSelect(_sqlCheck).fetchone()
        if _table is None:
            self.__logger.info("create undo table")
            _sqlCreation="""CREATE TABLE pycadent(
                    pycad_id INTEGER PRIMARY KEY,
                    pycad_entity_id NUMERIC,
                    pycad_object_type TEXT,
                    pycad_object_definition BLOB,
                    pycad_style_id INTEGER,
                    pycad_security_id INTEGER,
                    pycad_locked INTEGER)"""
            self.makeUpdateInsert(_sqlCreation)
            
    def saveEntity(self,entityObj):
        """
            this method save the entity in the db
            entityObj = object that we whant to store
        """
        _entityId=entity.getId()
        _entityDump=cPickle.dumps(entity.getConstructionPoint(),2)
        _entityType=entity.getEntityType()
        _styleId=entityObj.getStyle().getId()
        _sqlInsert="""INSERT INTO pycadent (
                    pycad_entity_id,
                    pycad_object_type,
                    pycad_object_definition,
                    pycad_style_id) VALUES
                    (%s,%s,%s,%s)"""%(str(_entityId),str(_entityType),str(_entityDump),str(_styleId))
        self.makeUpdateInsert(_sqlInsert)
        
    def getEntity(self,entityTableId):
        """
            Get the entity object from the database Univoc id
        """
        _outObj=None
        _sqlGet="""SELECT   pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_id=%s"""%str(entityTableId)
        _dbEntRow=self.makeSelect(_sqlCheck).fetchone()
        if _dbEntRow is not None:
            _style=_dbEntRow[3]
            _dumpObj=cPickle.loads(_dbEntRow[2])
            _outObj=PyCadEnt(_dbEntRow[1],_dumpObj,_style,_dbEntRow[0])
        return _outObj
    
    def getEntitys(self,entityId):
        """
            get all the entity with the entity id
            remarcs:
            this method return all the history of the entity
        """
        _outObj={}
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_entity_id=%s ORDER BY pycad_id"""%str(entityId)
        _dbEntRow=self.makeSelect(_sqlCheck)
        for _row in _dbEntRow: 
            _style=_row[4]
            _dumpObj=cPickle.loads(_row[3])
            _outObj[_row[0]]=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
        return _outObj

    def getEntitysFromStyle(self,styleId):
        """
            return all the entity that match the styleId
        """
        _outObj={}
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_style_id=%s ORDER BY pycad_id"""%str(styleId)
        _dbEntRow=self.makeSelect(_sqlCheck)
        for _row in _dbEntRow: 
            _style=_row[4]
            _dumpObj=cPickle.loads(_row[3])
            _outObj[_row[0]]=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
        return _outObj
        
def test():
    logging.debug("Create a point")
    basePoint=PyCadPoint(10,10)
    pts={}
    pts['POINT']=basePoint
    logging.debug( "create a point ent")
    sty=PyCadStyle(1)
    p1=PyCadEnt('POINT',pts,sty)
    logging.debug( "Create db kernel")
    kr=PyCadDbKernel()
    logging.debug("save the entity")
    kr.saveEntity(p1)
    logging.debug("End")

def test1():
    logging.debug("Create a point")
    basePoint=PyCadPoint(10,10)
    pts={}
    pts['POINT']=basePoint
    logging.debug( "create a point ent")
    sty=PyCadStyle(1)
    p1=PyCadEnt('POINT',pts,sty)
    p1.dump()
    print "*"*10



#test1()
