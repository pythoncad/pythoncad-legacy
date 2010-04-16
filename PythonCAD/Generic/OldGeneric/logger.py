#
# Copyright (c) 2004, 2005 Art Haas
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
# base class for entity history storage and undo/redo mechanisms
#

from PythonCAD.Generic import message

class Logger(message.Messenger):
    def __init__(self):
        super(Logger, self).__init__()
        self.__undo = None
        self.__redo = None
        self.__inredo = False
        self.__undone = False

    def detatch(self):
        pass
    
    def saveUndoData(self, *data):
        if self.__undo is None:
            self.__undo = []
        # print "saveUndoData: " + str(data)
        self.__undo.append(data)
        if self.__undone and not self.__inredo:
            self.__redo = None
            self.__undone = False

    def printUndoData(self):
        print "Undo stack ..."
        if self.__undo is None:
            print "None"
        else:
            for _d in self.__undo:
                print _d
                
    def getUndoData(self):
        _data = None
        if self.__undo is not None:
            _data = self.__undo.pop()
            if len(self.__undo) == 0:
                self.__undo = None
        return _data

    def undo(self):
        if self.__undo is not None:
            _data = self.__undo.pop()
            if len(self.__undo) == 0:
                self.__undo = None
            self.execute(True, *_data)
            self.__undone = True

    def saveRedoData(self, *data):
        if self.__redo is None:
            self.__redo = []
        # print "saveRedoData: "  + str(data)
        self.__redo.append(data)

    def getRedoData(self):
        _data = None
        if self.__redo is not None:
            _data = self.__redo.pop()
            if len(self.__redo) == 0:
                self.__redo = None
        return _data

    def printRedoData(self):
        print "Redo stack ..."
        if self.__redo is None:
            print "None"
        else:
            for _d in self.__redo:
                print _d

    def redo(self):
        if self.__redo is not None:
            _data = self.__redo.pop()
            if len(self.__redo) == 0:
                self.__redo = None
            self.__inredo = True
            try:
                self.execute(False, *_data)
            finally:
                self.__inredo = False

    def execute(self, undo, *args):
        pass

    def clear(self):
        self.__undo = None
        self.__redo = None

    def transferData(self, log):
        if not isinstance(log, Logger):
            raise TypeError, "Invalid Logger: " + `log`
        _undo = []
        _redo = []
        _data = log.getUndoData()
        while _data is not None:
            _undo.append(_data)
            _data = log.getUndoData()
        if len(_undo):
            if self.__undo is None:
                self.__undo = []
            _undo.reverse()
            for _data in _undo:
                self.__undo.append(_data)
        _data = log.getRedoData()
        while _data is not None:
            _redo.append(_data)
            _data = log.getRedoData()
        if len(_redo):
            if self.__redo is None:
                self.__redo = []
            _redo.reverse()
            for _data in _redo:
                self.__redo.append(_data)
        
