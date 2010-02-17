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
# This  module provide access to the basic operation on pythoncad database
#

import os
import sys
import sqlite3 as sql
import logging

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
