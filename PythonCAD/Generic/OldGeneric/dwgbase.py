#
# Copyright (c) 2003 Art Haas
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
# a class for reading (and hopefully eventually writing) DWG files
#

from __future__ import generators

import types
import sys

class Dwg:
    """The class for revision-neutral handling of DWG files.

The Dwg class is designed to provide a version-neutral interface
for reading DWG files. A Dwg instance has the following methods:

getHandle(): Get the opened file handle associated with the instance.
{get/set}Version(): Get/Set the version of the underlying DWG file.
{get/set}Offset(): Get/Set the offsets to sections with the DWG file.
getOffsetKeys(): Retrieve the section names for which offsets are stored.
setReader(): Set the function used for reading a particular DWG section.
{get/set}Header(): Get/Set a header variable used in the DWG file.
getHeaderKeys(): Get all the header variables in the DWG file.
{get/set}Class(): Get/Set a class used in the DWG file.
getClassKeys(): Get all the classes used in the DWG file.
{get/set}Object(): Get/Set an entity stored in the DWG file.
{get/set}ImageData(): Get/Set any bitmap image data in the DWG file.

Older versions of the DWG format lack image data and header variables,
and the presence of image data is optional. Also, the header data
variables keys can be different from one release to another.
    """
    def __init__(self, filename):
        """Initialize a Dwg instance.

dwg = Dwg(filename)

The one required argument is the path to a DWG file.
        """
        _mode = 'r'
        if sys.platform == 'win32':
            _mode = 'rb'
        self.__fp = file(filename, _mode)
        self.__version = None
        self.__offsets = {} # file offsets
        self.__entities = [] # entity offset data
        self.__dxfnames = {} # class/dxfname map
        self.__readers = {}
        self.__headers = {}
        self.__classes = {}
        self.__objects = []
        self.__wmfdata = None # not before R13
        self.__bmpdata = None # not before R13
        self.__index = 0
        self.__len = 0
        self.setVersion()

    def __del__(self):
        self.__fp.close()

    def getHandle(self):
        """Return the opened file handle associated with the DWG file.

getHandle()
        """
        return self.__fp

    def setVersion(self):
        """Store the version of the DWG file.

setVersion()
        """
        _fp = self.__fp
        _fp.seek(0, 0)
        _buf = _fp.read(6)
        if _buf == 'AC1009':
            _ver = 'R12'
        elif _buf == 'AC1010': # autocad 10?
            _ver = 'R12+'
        elif _buf == 'AC1012':
            import dwg1314
            dwg1314.initialize_dwg(self)
            _ver = 'R13'
        elif _buf == 'AC1014':
            import dwg1314
            dwg1314.initialize_dwg(self)
            _ver = 'R14'
        elif _buf == 'AC1015':
            import dwg15
            dwg15.initialize_dwg(self)
            _ver = 'R15'
        else:
            _ver = None # unknown file - maybe raise an error?
            self.__fp.close()
        self.__version = _ver

    def getVersion(self):
        """Return the version of the DWG file in use.

getVersion()
        """
        if self.__version is None:
            self.setVersion()
        return self.__version

    def setOffset(self, key, value):
        """Store the offset to a section within the DWG file.

setOffset(key, value)

This method requires two arguments:

key: A text string giving the section name.
value: A tuple of two objects.

Valid keys are one of the following:
HEADERS, CLASSES, OBJECTS, IMAGES, UNKNOWN, R14DATA, R15REC5

The tuple is of the following format:

(offset, size)

offset: Offset in the file
size: The size of the section; This argument can be 'None'
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid offset key: " + str(key)
        if not isinstance(value, tuple):
            raise TypeError, "Invalid offset tuple: " + str(value)
        if not len(value) == 2:
            raise ValueError, "Invalid offset tuple: " + str(value)
        if key in self.__offsets:
            raise ValueError, "Key already set: " + key
        if (key == 'HEADERS' or
            key == 'CLASSES' or
            key == 'OBJECTS' or
            key == 'IMAGES' or
            key == 'UNKNOWN' or
            key == 'R14DATA' or
            key == 'R14REC5'):
            self.__offsets[key] = value
        else:
            raise ValueError, "Unexpected offset key: " + key

    def getOffsetKeys(self):
        """Return the strings giving the sections for which offset data is stored.

getOffsetKeys()

This method returns the keys used in the setOffset() calls. The ordering
of the keys is random. The offset data can be retrieved by calling the
getOffset() method.
        """
        return self.__offsets.keys()

    def getOffset(self, key):
        """Return the section data associated with a particular section key.

getOffset(key)

Argument 'key' should be a string returned from getOffsetKeys().
        """
        return self.__offsets[key]

    def setReader(self, key, value):
        """Store a function which reads a section of the DWG file.

setReader(key, value)

This function has two required arguments:

key: A text string giving the reader type
value: The function used to read the section of the DWG file.

Valid keys are:
HEADERS, CLASSES, OBJECTS, IMAGES
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid offset key: " + str(key)
        if not isinstance(value, types.FunctionType):
            raise TypeError, "Invalid reader for '%s': %s" % (key, str(value))
        if (key == 'HEADERS' or
            key == 'CLASSES' or
            key == 'OBJECTS' or
            key == 'OFFSETS' or
            key == 'OBJECT' or
            key == 'IMAGES'):
            self.__readers[key] = value
        else:
            raise ValueError, "Unexpected reader key: " + key

    def getReader(self, key):
        """Return the function for reading a DWG file section.

getReader(key)        
        """
        return self.__readers[key]
    
    def setHeader(self, key, value):
        """Store a header variable found in the DWG file.

setHeader(key, value)

This method has two arguments:

key: The header variable
value: Its value.

The 'key' must be a string, and the value can be any type of Python
object (string, int, double, tuple, etc...)
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid header key: " + str(key)
        self.__headers[key] = value

    def getHeaderKeys(self):
        """Return the various header variables found in the DWG file.

getHeaderKeys()

This method returns a list of strings, with each being one of the
header variables found in the DWG file. The data associated with
each header can be retrieved with the getHeader() method.
        """
        if not len(self.__headers):
            if 'HEADERS' in self.__readers:
                _reader = self.__readers['HEADERS']
                _reader(self)
        return self.__headers.keys()

    def getHeader(self, key):
        """Return the associated value for a particular header variable.

getHeader(key)

Argument 'key' should be one of the strings returned from getHeaderKeys()
        """
        return self.__headers[key]

    def setDxfName(self, key, dxfname):
        """Store the mapping between the type number and DXF name.

setDxfName(key, dxfname)

Argument 'key' is an integer, and argument 'dxfname' is a string.
This data is found in the class data section in R13, R14, and R15
DWG files.
        """
        if not isinstance(key, int):
            raise TypeError, "Invalid dxfname key: " + str(key)
        if not isinstance(dxfname, str):
            raise TypeError, "Invalid dxfname: " + str(key)
        self.__dxfnames[key] = dxfname

    def getDxfName(self, key):
        """Return the dxfname for a given class key.

getDxfName(key)

Argument 'key' should be an integer. This method returns a
string if there is a class for the key value. Otherwise this
method returns None.

        """
        if not isinstance(key, int):
            raise TypeError, "Invalid dxfname key: " + str(key)
        return self.__dxfnames.get(key)

    def setClass(self, key, value):
        """Store a class variable found in the DWG file.

setClass(key, value)

This method has two required arguments:

key: An integer value
value: A tuple

The contents of the tuple are as follows:
(appname, cplusplusname, dxfname, zombie, id)

The tuple data comes from the R13/R14/R15 spec.
        """
        if not isinstance(key, int):
            raise TypeError, "Non-integer class key: " + str(key)
        if not isinstance(value, tuple):
            raise TypeError, "Non-tuple class value: " + str(value)
        self.__classes[key] = value

    def getClassKeys(self):
        """Return the various classes found in the DWG file.

getClassKeys()

This method returns a list of class values. The data associated
for each class can be obtained with getClass().
        """
        if not len(self.__classes):
            if 'CLASSES' in self.__readers:
                _reader = self.__readers['CLASSES']
                _reader(self)
        return self.__classes.keys()

    def getClass(self, key):
        """Return the class data for a given class.

getClass()

This method returns a tuple holding the class data.
        """
        return self.__classes.get(key)

    def addEntityOffset(self, handle, offset):
        """Store handle/offset data for an entity in the DWG file.

addEntityOffset(handle, offset)
        """
        self.__entities.append((handle, offset))

    def getEntityOffset(self):
        """Return the list of handle/offset data for the DWG file entities.

getEntityOffset()
        """
        for _entdata in self.__entities:
            _id, _offset = _entdata
            yield _offset

    def setObject(self, obj):
        """Store an entity found within the DWG file.

setObject(obj)

Argument 'obj' must be an dwgEntity instance.
        """
        if not isinstance(obj, dwgEntity):
            raise TypeError, "Invalid DWG object: " + str(obj)
        self.__objects.append(obj)

    def getObject(self):
        """Return a single object from the DWG file.

getObject()

This method can be called to extract the dwgEntity objects from
the DWG file one object at a time. The first call gets the
first entity, and each subsequent call retrieves the following
entity.
        """
        if not len(self.__classes):
            if 'CLASSES' in self.__readers:
                _reader = self.__readers['CLASSES']
                _reader(self)
        if not len(self.__entities):
            if 'OFFSETS' in self.__readers:
                _reader = self.__readers['OFFSETS']
                _reader(self)
        if 'OBJECT' not in self.__readers:
            raise StopIteration
        _reader = self.__readers['OBJECT']
        for entdata in self.__entities:
            _id, _offset = entdata
            yield _reader(self, _offset)

    def rewind(self):
        if not len(self.__classes):
            if 'CLASSES' in self.__readers:
                _reader = self.__readers['CLASSES']
                _reader(self)
        if not len(self.__entities):
            if 'OFFSETS' in self.__readers:
                _reader = self.__readers['OFFSETS']
                _reader(self)
        self.__index = 0
        self.__len = len(self.__entities)

    def next_object(self):
        if self.__index == self.__len:
            return
        _id, _offset = self.__entities[self.__index]
        _reader = self.__readers['OBJECT']
        self.__index = self.__index + 1
        return _reader(self, _offset)

    def getEntities(self):
        if not len(self.__classes):
            if 'CLASSES' in self.__readers:
                _reader = self.__readers['CLASSES']
                _reader(self)
        if not len(self.__entities):
            if 'OFFSETS' in self.__readers:
                _reader = self.__readers['OFFSETS']
                _reader(self)
        return self.__entities

    def getObjects(self):
        """Return all the stored objects found in the DWG file.

getObjects()

This method returns a list of dwgEntity objects.
        """
        if not len(self.__classes):
            if 'CLASSES' in self.__readers:
                _reader = self.__readers['CLASSES']
                _reader(self)
        if not len(self.__entities):
            if 'OFFSETS' in self.__readers:
                _reader = self.__readers['OFFSETS']
                _reader(self)
        if not len(self.__objects):
            if 'OBJECTS' in self.__readers:
                _reader = self.__readers['OBJECTS']
                _reader(self)
        return self.__objects[:]

    def setImageData(self, imagetype, data):
        """Store the bitmap image data found in the DWG file.

setImageData(imagetype, data)

This method has two required arguments:

imagetype: A string - either 'BMP' or 'WMF'
data: The image data

The format in which the data is stored is not checked. The R13/R14/R15
readers use array.array instances for this. The image data is not
found in R12 and earlier files.
        """
        if not isinstance(imagetype, str):
            raise TypeError, "Invalid image type: " + str(imagetype)
        if imagetype == 'BMP':
            self.__bmpdata = data
        elif imagetype == 'WMF':
            self.__wmfdata = data
        else:
            raise ValueError, "Unexpected image type: " + imagetype

    def getImageData(self, imagetype):
        """Return the image data found in the DWG file.

getImageData(imagetype)

This method requires a single argument:

imagetype: A string - either 'BMP' or 'WMF'.

There is no image data in R12 and earlier files, and image data
is optional in R13 and later files. If there is no image data
this method returns None.
        """
        if not isinstance(imagetype, str):
            raise TypeError, "Invalid image type: " + str(imagetype)
        if imagetype == 'BMP':
            return self.__bmpdata
        elif imagetype == 'WMF':
            return self.__wmfdata
        else:
            raise ValueError, "Unexpected image type: " + imagetype

class dwgEntity:
    """A generic class for storing information about DWG objects.

The dwgEntity class provides a revision neutral means of storing
data found within the DWG file for all the drawing entities. Some entities
are visible entities like lines, circles, and arcs, and others are
non-graphical entities like tables. The dwgEntity class has the
following methods:

{get/set}Type(): Get/Set the entity type.
{get/set}Handle(): Get/Set the entity handle (identifier).
{get/set}EntityData(): Get/Set some information about a DWG entity.
getEntityKeys(): Return the keys used for storing entity data.

Each different type of DWG entity will have different keys stored,
and the number of keys varies based on the entity and the ability to
decode the information found in the DWG file itself.

DWG entities in R13, R14, and R15 files have a large number of
shared data attributes. The followin method are available for
examining this information. Many of the following methods will only
be useful when reading the entities from the DWG file itself.

{get/set}Version(): Get/Set a DWG version in the entity
{get/set}Mode(): Get/Set the entity mode.
{get/set}NumReactors(): Get/Set the number of reactors.
{get/set}NoLinks(): Get/Set the entity linkage flag.
{get/set}IsLayerByLinetype(): ????
{get/set}Color(): Get/Set the entity color.
{get/set}LinetypeScale(): Get/Set the linetype scale factor.
{get/set}LinetypeFlags(): Get/Set the linetype flags.
{get/set}PlotstyleFlags(): Get/Set the plotstyle flags.
{get/set}Invisibility(): Get/Set the entity invisiblity flags.
{get/set}Lineweight(): Get/Set the entity lineweight factor.
{get/set}Subentity(): Get/Set the subentity flgas.
addReactor(): Add a handle of a reactor object.
getReactors(): Get all the reactors associated with an object.
{get/set}Xdicobj(): ????
{get/set}Layer(): Get/Set the layer where the object is placed.
{get/set}Linetype(): Get/Set the entity linetype
getPrevious(): Get the previous entity in a entity chain.
getNext(): Get the subsequent entity in an entity chain.
{get/set}Plotstyle(): Get/Set the plotstyle flags.

Some of the methods are particular to R13 and R14 files, and some
are particular to R15 files.
    """
    def __init__(self):
        """Initialize a dwgEntity instance.

ent = dwgEntity()

This method requires no arguments.
        """
        self.__cdata = {} # "common" stuff for all entities
        self.__edata = {} # entity specfic data

    def getEntityKeys(self):
        """Return the keys used to store entity specific data.

getEntityKeys()

THis method returns an unsorted list of strings. The value associated
with each key can be obtained by calling the getEntityData() method.
        """
        return self.__edata.keys()

    def setEntityData(self, key, value):
        """Store entity specfic data in the dwgEntity.

setEntityData(key, value)

This method requires two arguments:

key: A string used to describe the stored data.
value: Any Python type.

        """
        if not isinstance(key, str):
            raise TypeError, "Invalid entity data key: " + str(key)
        self.__edata[key] = value

    def getEntityData(self, key):
        """Retrieve the entity data value for a given key.

getEntityData(key):

Argument 'key' should be one of the keys returned from getEntityKeys().
        """
        return self.__edata[key]

    def setType(self, objtype):
        """Store the type of object in the dwgEntity instance.

setType(objtype)

Argument 'objtype' is an integer value corresponding to the entity
type. The OpenDWG specs give this information in more detail.
        """
        if not isinstance(objtype, int):
            raise TypeError, "Invalid object type: " + str(objtype)
        self.__cdata['TYPE'] = objtype

    def getType(self):
        """Return the type of object the dwgEntity represents.

getType()

This method returns an integer. See the OpenDWG specs for information
to match this value to the entity type.
        """
        return self.__cdata.get('TYPE')

    def setHandle(self, handle):
        """Set the handle (id) that the dwgEntity holds.

setHandle(handle)

Argument 'handle' is a tuple containing integer values.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['HANDLE'] = handle

    def getHandle(self):
        """Return the handle (id) of the dwgEntity.

getHandle()

This method returns a tuple containing integers.
        """
        return self.__cdata['HANDLE']

    def setVersion(self, version):
        """Set a version string in the dwgEntity.

setVersion(version)

Argument 'version' must be a string.
        """
        if not isinstance(version, str):
            raise TypeError, "Invalid version string: " + str(version)
        self.__cdata['VERSION'] =  version

    def getVersion(self):
        """Retrieve the version string in the dwgEntity.

getVersion()

This method returns a string, or None if the setVersion() method
has not been invoked on the instance.
        """
        return self.__cdata.get('VERSION')

    def setMode(self, mode):
        """Set the mode of the entity.

setMode(mode)

Argument 'mode' must be an integer.
        """
        if not isinstance(mode, int):
            raise TypeError, "Invalid mode: " + str(mode)
        self.__cdata['MODE'] = mode

    def getMode(self):
        """Return the mode of the entity.

getMode()

This method returns an integer value.
        """
        return self.__cdata.get('MODE')

    def setNumReactors(self, nr):
        """Set the number of reactors of an entity.

setNumReactors(nr)

Argument 'nr' must be an integer.
        """
        if not isinstance(nr, int):
            raise TypeError, "Invalind reactor count:" + str(nr)
        self.__cdata['NUMREACTORS'] = nr

    def getNumReactors(self):
        """Get the number of reactors of an entity.

getNumReactors()

This method returns an integer value.
        """
        return self.__cdata.get('NUMREACTORS', 0)

    def setNoLinks(self, flag):
        """Set the 'nolinks' flag of an entity.

setNoLinks(self, flag)

Argument 'flag' can be either True, False, or an integer. If
it is an integer, 0 is False, and all other values are True.
        """
        if isinstance(flag, int):
            if flag == 0:
                _nlflag = False
            else:
                _nlflag = True
        elif flag is False:
            _nlflag = False
        elif flag is True:
            _nlflag = True
        else:
            raise TypeError, "Invalid type for flag: " + str(flag)
        self.__cdata['NOLINKS'] = _nlflag

    def getNoLinks(self):
        """Return the 'nolinks' flag of an entity.

getNoLinks()
        """
        return self.__cdata.get('NOLINKS')

    def setIsLayerByLinetype(self, flag):
        """Set a flag value.

setIsLayerByLinetype(flag)

Argument 'flag' can be either True, False, or an integer. If
it is an integer, 0 is False, and all other values are True.
        """
        if isinstance(flag, int):
            if flag == 0:
                _iflag = False
            else:
                _iflag = True
        elif flag is False:
            _iflag = False
        elif flag is True:
            _iflag = True
        else:
            raise TypeError, "Invalid type for flag: " + str(flag)
        self.__cdata['ILBT'] = _iflag

    def getIsLayerByLinetype(self):
        """Return the flag value.

getIsLayerByLinetype()
        """
        return self.__cdata.get('ILBT')

    def setColor(self, color):
        """Store the entity color in the dwgEntity object.

setColor(color)

Argument 'color' is an integer.
        """
        if not isinstance(color, int):
            raise TypeError, "Invalid color: " + str(color)
        self.__cdata['COLOR'] = color

    def getColor(self):
        """Return the color of the entity.

getColor()

This method returns an integer giving the entity color.
        """
        return self.__cdata.get('COLOR')

    def setLinetypeScale(self, scale):
        """Store the linetype scale factor of the DWG object.

setLinetypeScale(scale)

Argument 'scale' must be a float value.
        """
        if not isinstance(scale, float):
            raise TypeError, "Invalid linetype scale: " + str(scale)
        self.__cdata['LTSCALE'] = scale

    def getLinetypeScale(self):
        """Return the linetype scale factor for the dwgEntity.

getLinetypeScale()

This method returns a float value.
        """
        return self.__cdata.get('LTSCALE')

    def setLinetypeFlags(self, flags):
        """Set the linetype flags.

setLinetypeFlags(flags)

Argument 'flags' must be an integer.
        """
        if not isinstance(flags, int):
            raise TypeError, "Invalid linetype flags: " + str(flags)
        self.__cdata['LTFLAGS'] = flags

    def getLinetypeFlags(self):
        """Return the linetype flags.

getLinetypesFlags()
        """
        return self.__cdata.get('LTFLAGS')

    def setPlotstyleFlags(self, flags):
        """Set the plotstyle flags.

setPlotstyleFlags(flags)

Argument 'flags' must be an integer.
        """
        if not isinstance(flags, int):
            raise TypeError, "Invalid plotstyle flags: " + str(flags)
        self.__cdata['PSFLAGS'] = flags

    def getPlotstyleFlags(self):
        """Get the plotstyle flags.

getPlotstyleFlags()
        """
        return self.__cdata.get('PSFLAGS')

    def setInvisiblity(self, flag):
        """Set the invisiblity flag.

setInvisiblity(flag)

Argument 'flag' can be either True, False, or an integer. If
it is an integer, 0 is False, and all other values are True.
        """
        if isinstance(flag, int):
            if flag == 0:
                _iflag = False
            else:
                _iflag = True
        elif flag is False:
            _iflag = False
        elif flag is True:
            _iflag = True
        else:
            raise TypeError, "Invalid type for flag: " + str(flag)
        self.__cdata['INVIS'] = _iflag

    def getInvisibility(self):
        """Get the invisibility flag.

getInvisibility()
        """
        return self.__cdata.get('INVIS')

    def setLineweight(self, weight):
        """Set the line weight.

setLineweight(weight)

Argument 'weight' must be an integer.
        """
        if not isinstance(weight, int):
            raise TypeError, "Invalid lineweight: " + str(weight)
        self.__cdata['LINEWEIGHT'] = weight

    def getLineweight(self):
        """Get the line weight.

getLineweight()
        """
        return self.__cdata.get('LINEWEIGHT')

    def setSubentity(self, handle): # code 3 handles
        """Set the subentity handle (id).

setSubentity(handle)

Argument 'handle' must be a tuple
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['SUBENTITY'] = handle

    def getSubentity(self):
        """Get the subentity handle.

getSubentity
        """
        return self.__cdata.get('SUBENTITY')

    def addReactor(self, handle): # code 4 handles
        """Add a reactor to an dwgEntity.

addReactor(handle)

Argument 'handle' must be a tuple.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        if 'REACTORS' not in self.__cdata:
            self.__cdata['REACTORS'] = []
        self.__cdata['REACTORS'].append(handle)

    def getReactors(self):
        """Get all the reactors for a dwgEntity.

getReactors()

This method returns a list of tuples.
        """
        _rlist = []
        if 'REACTORS' in self.__cdata:
            _rlist.extend(self.__cdata['REACTORS'][:])
        return _rlist

    def setXdicobj(self, handle): # code 3 handle
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['XDICOBJ'] = handle

    def getXdicobj(self):
        return self.__cdata.get('XDICOBJ')

    def setLayer(self, handle): # code 5 handle
        """Store the layer where the entity is held.

setLayer(handle)

Argument 'handle' is a tuple containing integers.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['LAYER'] = handle

    def getLayer(self):
        """Return the layer handle to which this entity belongs.

getLayer()

This method returns a tuple.
        """
        return self.__cdata.get('LAYER')

    def setLinetype(self, handle): # code 5 handle
        """Set the linetype handle for a dwgEntity.

setLinetype(handle)

Argument 'handle' must be a tuple.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['LINETYPE'] = handle

    def getLinetype(self):
        """Get the linetype for a dwgEntity.

getLinetype()
        """
        return self.__cdata.get('LINETYPE')

    def setPrevious(self, handle): # code 4 handle
        """Set the previous entity handle for a dwgEntity.

setPrevious(handle)

Argument 'handle' must be a tuple.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['PREV'] = handle

    def getPrevious(self):
        """Get the previous entity handle for a dwgEntity.

getPrevious()
        """
        return self.__cdata.get('PREV')

    def setNext(self, handle): # code 4 handle
        """Set the next entity handle for a dwgEntity.

setNext(handle)

Argument 'handle' must be a tuple.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['NEXT'] = handle

    def getNext(self):
        """Get the next entity handle for a dwgEntity.

getNext()
        """
        return self.__cdata.get('NEXT')

    def setPlotstyle(self, handle): # code 5 handle
        """Set the plotstyle handle for an dwgEntity.

setPlotstyle(handle)

Argument 'handle' must be a tuple.
        """
        if not isinstance(handle, tuple):
            raise TypeError, "Invalid handle: " + str(handle)
        self.__cdata['PLOTSTYLE'] = handle

    def getPlotstyle(self):
        """Get the plotstyle handle for a dwgEntity.

getPlotstyle()
        """
        return self.__cdata.get('PLOTSTYLE')
