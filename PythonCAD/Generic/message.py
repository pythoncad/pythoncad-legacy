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
# A base class for objects that send messages
#

import types
import traceback

class Messenger(object):
    __messages = {
        'connected' : True,
        'disconnected' : True
        }
    
    def __init__(self):
        self.__connections = None
        self.__mdict = None
        self.__ignore = None
        self.__muted = False

    def finish(self):
        if self.__connections is not None:
            print "remaining connections for obj: " + `self`
            for _message in self.__connections:
                print "message: %s" % _message
                for _method in self.__connections[_message]:
                    _obj = _method.im_self
                    print "connected to obj: " + `_obj`

    def connect(self, message, method):
        if not self.sendsMessage(message):
            raise ValueError, "Unknown message : %s" % str(message)
        if not isinstance(method, types.MethodType):
            raise TypeError, "Invalid class method type: " + `type(method)`
        if method.im_self is None:
            raise ValueError, "Unbound method use invalid: %s" % str(method)
        if self.__connections is None:
            self.__connections = {}
        _methods = self.__connections.setdefault(message, [])
        _seen = False
        for _m in _methods:
            if _m is method:
                _seen = True
                break
        if not _seen:
            _methods.append(method)
            self.sendMessage('connected', method)

    def disconnect(self, obj, message=None):
        if self.__connections is not None:
            if message is None:
                _messages = self.__connections.keys()
                for _message in _messages:
                    _methods = self.__connections[_message]
                    for _method in _methods[:]:
                        _obj = _method.im_self
                        if _obj is obj:
                            _methods.remove(_method)
                            self.sendMessage('disconnected', obj)
                    if len(_methods) == 0:
                        del self.__connections[_message]
            else:
                if message in self.__connections:
                    _methods = self.__connections[message]
                    for _method in _methods[:]:
                        _obj = _method.im_self
                        if _obj is obj:
                            _methods.remove(_method)
                            self.sendMessage('disconnected', obj)
                            break
                    if len(_methods) == 0:
                        del self.__connections[message]
            if len(self.__connections) == 0:
                self.__connections = None

    def sendsMessage(self, m):
        return m in Messenger.__messages

    def sendMessage(self, message, *args):
        if not isinstance(message, str):
            raise TypeError, "Invalid message type: " + `type(message)`
        if not self.__muted and self.__connections is not None:
            if self.__mdict is None or message not in self.__mdict:
                if message in self.__connections:
                    _methods = self.__connections[message][:] # make a copy
                    for _method in _methods:
                        _obj = _method.im_self
                        if (isinstance(_obj, Messenger) and
                            _obj.ignores(message)):
                            continue
                        #
                        # "handle" the exception - notice the quotes ...
                        #
                        try:
                            _method(self, *args)
                        except:
                            traceback.print_exc()

    def muteMessage(self, message):
        if not isinstance(message, str):
            raise TypeError, "Invalid message type: " + `type(message)`
        if self.__mdict is None:
            self.__mdict = {}
        if message in self.__mdict:
            raise ValueError, "Message '%s' already blocked." % message
        self.__mdict[message] = True

    def unmuteMessage(self, message):
        if not isinstance(message, str):
            raise TypeError, "Invalid message type: " + `type(message)`
        if self.__mdict is not None:
            if message in self.__mdict:
                del self.__mdict[message]
            if len(self.__mdict) == 0:
                self.__mdict = None
        
    def mute(self):
        self.__muted = True

    def unmute(self):
        self.__muted = False

    def isMuted(self):
        return self.__muted is True

    def ignore(self, message):
        if not isinstance(message, str):
            raise TypeError, "Invalid message type: " + `type(message)`
        if self.__ignore is None:
            self.__ignore = {}
        if message in self.__ignore:
            raise RuntimeError, "Message '%s' already ignored." % message
        self.__ignore[message] = True

    def receive(self, message):
        if not isinstance(message, str):
            raise TypeError, "Invalid message type: " + `type(message)`
        if self.__ignore is not None:
            if message in self.__ignore:
                del self.__ignore[message]
            if len(self.__ignore) == 0:
                self.__ignore = None

    def ignores(self, message):
        return self.__ignore is not None and message in self.__ignore
        
    def receives(self, message):
        return self.__ignore is None or message not in self.__ignore
