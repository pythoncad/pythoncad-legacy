import os
import sys
import sqlite3 as sql
import cPickle
import logging

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

class PyCadObject(object):
    """
        this class provide basic information usefoul for the
        db like id for exsample
    """
    def __init__(self,objId):
        self.__entityId=objId
    def getId(self):
        """
            get the entity id
        """
        return self.__entityId

class PyCadEnt(PyCadObject):
    """
        basic PythonCad entity structure
    """
    def __init__(self,entType,constructionPoints,style=None):
        PyCadObject.__init__(self,None)
        if not entType in PY_CAD_ENT:
            raise TypeError,'entType not supported' 
        self.__entType=entType
        if not (PyCadStyle is None or isinstance(style,PyCadStyle) ):          
            raise TypeError,'style not supported' 
        self.__style=style        
        if not isinstance(constructionPoints,dict):
            raise TypeError,'type error in dictionary'
        self.__PointDic=constructionPoints

    def getConstructionPoint(self):
        """
            return the base entity array
        """      
        return self.__PointDic

    def getEntityType(self):
        """
            Get the entity type 
        """
        return self.__entType
    eType=property(getEntityType,None,None,"Get the etity type read only attributes")
    def getStyle(self):
        """
            get the object style
        """
        return self.__style
    def setStyle(self,style):
        """
            set/update the entity style
        """
        if not isinstance(style,PyCadStyle):
            raise TypeError,'Type error in style'
        self.__style=style        
    style=property(getStyle,setStyle,None,"Get/Set the entity style")

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

class PyCadStyle(PyCadObject):
    """
        this class rappresent the style in pythoncad
        objID iss the object that rappresent the id in the db
    """
    def __init__(self,objId):
        self.__logger=logging.getLogger('PyCadStyle')
        PyCadObject.__init__(self,objId)     

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

class PyCadBaseDb(object):
    """
        this class provide base db operation
    """
    def __init__(self):
        self.__logger=logging.getLogger('PyCadBaseDb')
        self.__dbConnection=None
    def createConnection(self,dbPath=None):
        """
            create the connection with the database
        """
        if dbPath is None:
            dbPath='pythoncad.pdr' 
        if not os.path.exists(dbPath):
            self.__logger.error('Unable lo get the db %s'%str(dbPath))
            sys.exit()
        self.__dbConnection = sql.connect(dbPath)

    def setConnection(self,dbConnection):
        """
            set the connection with the database
        """
        if not self.__dbConnection is None:
            # Todo fire a warning
            self.__dbConnection.close()
        self.__dbConnection=dbConnection

    def makeSelect(self,statment):
        """
            perform a select operation
        """
        try:
            _cursor = self.__dbConnection.cursor()
            _rows = _cursor.execute(statment)
        except sql.Error, _e:
            self.__logger.error("Sql Phrase: %s"%str(statment))       
            self.__logger.error("Sql Error: %s"%str( _e.args[0] ))
            return None
        except :
            for s in sys.exc_info():
                self.__logger.error("Generic Error: %s"%str(s))
            return None
        return _rows

    def makeUpdateInsert(self,statment):
        """
            make an update Inster operation
        """
        try:
            _cursor = self.__dbConnection.cursor()
            _rows = _cursor.execute(statment)
            self.__dbConnection.commit()
        except sql.Error, _e:
            self.__logger.error("Sql Phrase: %s"%str(statment))       
            self.__logger.error("Sql Error: %s"%str( _e.args[0] ))
        except :
            for s in sys.exc_info():
                self.__logger.error("Generic Error: %s"%str(s))
    def close(self):
        """
            close the database connection
        """
        self.__dbConnection.close()

class PyCadUndoDb(PyCadBaseDb):
    """
        this Class Provide all the basic operation to be made on the
        undo 
    """
    def __init__(self,dbConnection):
        PyCadBaseDb.__init__(self)
        self.setConnection(dbConnection)
        self.__logger=logging.getLogger('PyCadUndoDb')
        self.__logger.debug('__init__')
        def checkTables():
            _sqlCheck="""select * from sqlite_master where name like 'pycadundo'"""
            if self.makeSelect(_sqlCheck) is None:
                self.__logger.info("create undo table")
                _sqlCreation="""CREATE TABLE "pycadundo" (
                                "pycad_id" INTEGER PRIMARY KEY,
                                "pycad_undo_state" TEXT
                                )
                                """
                self.makeUpdateInsert(_sqlCreation)

    def getLastUndoIndex(self):
        """
            get the last undo index
        """
        _sqlCheck="select max(pycad_id) from pycadundo"
        _rows=self.makeSelect(_sqlCheck) 
        if _rows is None:
            # no entity in the table
            _sqlInser="""INSERT INTO pycadundo (pycad_undo_state) VALUES ("active")"""
            self.makeUpdateInsert(_sqlInser)
            _rows=self.makeSelect(_sqlCheck) 
        if _rows== None:
            raise TypeError, "No row fatched in undo search "
        _row=_rows.fetchone()
        return _row[0] # get the max index of the table 

    def setActiveUndo(self,undoId):
        """
            set the active undo 
        """
        self.resetUndoTable()
        _sqlSetLastUndo="""update pycadundo set pycad_undo_state='active' where pycad_id='%s'"""%str(undoId)
        self.makeUpdateInsert(_sqlSetLastUndo)

    def resetUndoTable(self):
        """
            reset all the table value to no-value
        """
        _sqlReset="""update pycadundo set pycad_undo_state='no-value'"""
        self.makeUpdateInsert(_sqlReset)

    def getNextUndo(self):
        """
            get the next undo index pycadundo 
        """
        self.resetUndoTable()
        _lastUndo=self.getLastUndoIndex()
        _sqlInser="""INSERT INTO pycadundo (pycad_undo_state) VALUES ('active')"""    
        self.makeUpdateInsert(_sqlInser)
        return self.getLastUndoIndex()

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
