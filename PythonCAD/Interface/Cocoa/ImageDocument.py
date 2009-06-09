#
# Copyright (c) 2002-2004 Art Haas
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
# Cocoa wrapper for Image class - handles display of
# drawing in a window, saving & loading of files
#
# P.L.V. nov 23 05
# import adjustment
from __future__ import division

import math
import sys
import types

import PythonCAD.Generic.image
import PythonCAD.Generic.imageio
import PythonCAD.Generic.tools
import PythonCAD.Generic.globals
import PythonCAD.Generic.layer
import PythonCAD.Generic.message

import PythonCAD.Interface.Cocoa.Globals
import PythonCAD.Interface.Cocoa.CADView
from PythonCAD.Interface.Cocoa import ImageWindowController

from PyObjCTools import NibClassBuilder
from Foundation import NSLog, NSObject, NSString, NSNotificationCenter, NSNotificationQueue, NSNotification, NSPostWhenIdle, NSPostASAP, NSNotificationNoCoalescing
from AppKit import NSOutlineViewDataSource, NSWindowController, NSChangeDone

#
# Define True & False if this is Python < 2.2.1
#
try:
    True, False
except NameError:
    True, False = 1, 0

NibClassBuilder.extractClasses("ImageDocument")

class CocoaMessenger(PythonCAD.Generic.message.Messenger):
    """ Class converts PythonCAD messages into NSNotificationCenter
    messages
    
    """
    def added_object_event(self, obj, *args):
        """ Notification of new point, line, etc. added to drawing.
        object is Image object, userinfo dict stores new object
        under key "item"
        """
        _nq = NSNotificationQueue.defaultQueue()
        if len(args) != 2:
            raise ValueError, "Invalid number of new items in added_object_event"
        _info = {"layer" : args[0], "item": args[1]}
        _obj = Globals.wrap(obj)
        _note = NSNotification.notificationWithName_object_userInfo_("added_object", _obj, _info)
        _nq.enqueueNotification_postingStyle_coalesceMask_forModes_(_note, NSPostASAP, NSNotificationNoCoalescing, None)

    def deleted_object_event(self, obj, *args):
        """ Notification of point, line, etc. removed from a layer.
        object is Image object, userinfo dict stores object
        under key "item", layer it was removed from under "layer"
        """
        _nq = NSNotificationQueue.defaultQueue()
        if len(args) != 2:
            raise ValueError, "Invalid number of items in deleted_object_event"
        _info = {"layer" : args[0], "item": args[1]}
        _obj = Globals.wrap(obj)
        _note = NSNotification.notificationWithName_object_userInfo_("deleted_object", _obj, _info)
        _nq.enqueueNotification_postingStyle_coalesceMask_forModes_(_note, NSPostASAP, NSNotificationNoCoalescing, None)

    def added_child_event(self, obj, *args):
        """ Notification of new layer added to drawing.
        object is Image object, userinfo dict stores new layer
        under key "layer", parent layer under key "parent"
        """
        _nq = NSNotificationQueue.defaultQueue()
        if len(args) != 2:
            raise ValueError, "Invalid number of new items in added_layer_event"
        _info = {"layer" : args[0], "parent" : args[0].getParent()}
        _obj = Globals.wrap(obj)
        _note = NSNotification.notificationWithName_object_userInfo_(Globals.LayerAddedNotification, _obj, _info)
        _nq.enqueueNotification_postingStyle_coalesceMask_forModes_(_note, NSPostASAP, NSNotificationNoCoalescing, None)
  
    def removed_child_event(self, obj, *args):
        """ Notification of deletion of a layer.  object is Image object,
        userinfo dict stores layer under key "layer", parent layer under
        key "parent"
        """
        _nq = NSNotificationQueue.defaultQueue()
        if len(args) != 2:
            raise ValueError, "Invalid number of items in deleted_layer_event"
        _info = {"layer" : args[0], "parent" : args[0].getParent()}
        _obj = Globals.wrap(obj)
        _note = NSNotification.notificationWithName_object_userInfo_(Globals.LayerDeletedNotification, _obj, _info)
        _nq.enqueueNotification_postingStyle_coalesceMask_forModes_(_note, NSPostASAP, NSNotificationNoCoalescing, None)


# class defined in ImageDocument.nib
class ImageDocument(NibClassBuilder.AutoBaseClass):
    """Cocoa wrapper around an Image.
    
The ImageDocument is an NSDocument which has as a member variable
an instance of the Image class.  It is the data source for the 
Outline view of the window.  It has the following additional methods:

getDA(): Get CADView holding the drawing area
getOutlineView: Get NSOutlineView holding layer information
getEntry(): Get NSTextField used for command entry
getSplitView(): Get NSSplitView containing the CADView & Layer Outline View
{get/set}Option(): Get/set option in generic Image object
{get/set}Image(): Get generic Image object
{get/set}Prompt(): Get/Set the prompt.
{get/set}Tool(): Get/Set the tool used for working in the GTKImage.
{get/set}UnitsPerPixel(): Get/Set this display parameter.
{get/set}Point(): Get/Set the current coordinates of the tool.
reset(): Sets the image to an initial drawing state

    """
#
# Setup variables
#
    __image = None
#
# Beginning of Cocoa methods
#
    def init(self):
        """ NSDocument override for cocoa initializer of ImageDocument. 

init()
        """
        
        self = super(ImageDocument, self).init()
        if (self):
            #
            # Set up messaging
            #
            self.setMessenger(CocoaMessenger()) 
            #
            # Initialize image object
            #
            self.setImage(PythonCAD.Generic.image.Image())             
            #
            # tool setup & location
            #
            self.__tool = None
            self.__oldtool = PythonCAD.Generic.tools.Tool()
            self.__point_x = 0.0
            self.__point_y = 0.0
            
            #
            # viewable region 
            #
            self.__disp_width = None
            self.__disp_height = None
            self.__xmin = None
            self.__ymin = None
            self.__xmax = None
            self.__ymax = None
                                
        return self
        
    def windowNibName(self):
        """ NSDocument override to load ImageDocument nib

windowNibName()
        """
        return "ImageDocument"
        
    def makeWindowControllers(self):
        """ NSDocument override to manage custom NSWindowController
        
makeWindowControllers()
        """
        _nib = self.windowNibName()
        _wc = ImageWindowController.alloc().initWithWindowNibName_owner_(_nib,self)
        self.addWindowController_(_wc)
        
        
    def windowControllerDidLoadNib_(self, windowController):
        """ NSDocument override to do post-window appearance initialization
        
windowControllerDidLoadNib(windowController)
        """
        #
        # layer view setup
        #
        self.promptField.setStringValue_("Enter Command:")
        self.locationField.setStringValue_(self.getPoint())
        self.getOutlineView().reloadData()
        _da = self.getDA()
        _img = self.getImage()    
        if len(_img.getTopLayer().getChildren()) > 0:
            _da.fitImage()
        _da.postLoadSetup()
        
    
    
    def close(self):
        """ NSDocument override called when window is closing

close()
        """
        PythonCAD.Generic.image.Image.close(self.getImage())
        super(ImageDocument, self).close()
                
        
    def setFileName_(self, name):
        """ NSDocument override to keep filename set correctly in Image

setFileName(name)
        """
        self.getImage().setFilename(name)
        super(ImageDocument, self).setFileName_(name)
        
    def prepareSavePanel_(self, savePanel):
        """ NSDocument override to specify required extensions, etc

prepareSavePanel(savePanel)
        """
        savePanel.setRequiredFileType_("xml.gz")
        return True
        
            
    def writeToFile_ofType_(self, path, tp):
        """ NSDocument override to write file to disk
        
writeToFile_ofType_(path, filetype)
        """
        try:
            PythonCAD.Generic.imageio.save_image(self.getImage(),path)
        except (IOError, OSError), e:
            sys.stderr.write("Error writing file: %s\n" % str(e))
            return False
        except StandardError, e:
            sys.stderr.write("Error: %s\n" % str(e))
            return False
        return True

    def readFromFile_ofType_(self, path, tp):
        """ NSDocument override to read file from disk
        
readFromFile_ofType_(path, filetype)
        """
        _image = PythonCAD.Generic.image.Image()
        try:
            _imagefile = PythonCAD.Generic.fileio.CompFile(path, "r")
            try:
                PythonCAD.Generic.imageio.load_image(_image, _imagefile)
            finally:
                _imagefile.close()
        except (IOError, OSError), e:
            sys.stderr.write("Can't open '%s': %s\n" % (_fname, e))
            return False
        except StandardError, e:
            sys.stderr.write("Error: %s\n" % str(e))
            return False
        self.setImage(_image)
        return True

#
# End of Cocoa methods
#            
    
#
# Beginning of PythonCad specific methods
#    
    def addChildLayer(self, layer):
        """Add a new Layer as a Child of the entered layer.
#
#addChildLayer(l)
#
#This method covers the image::addChildLayer() method.
#        """
        new_layer = PythonCAD.Generic.layer.Layer("NewChildLayer")
        try:
            self.getImage().addChildLayer(new_layer, layer)
        except: #should do this better
            return
        self.updateChangeCount_(NSChangeDone)
#        _nc = NSNotificationCenter.defaultCenter()
#        _nc.postNotificationName_object_(Globals.LayerAddedNotification, self)

    def delLayer(self, layer):
        """Remove a Layer from the drawing.

delLayer(l)

This method covers the image::delLayer() method.
        """
        try:
            self.getImage().delLayer(layer)
        except: #should do this better
            return
        self.updateChangeCount_(NSChangeDone)
#        _nc = NSNotificationCenter.defaultCenter()
#        _nc.postNotificationName_object_(Globals.LayerDeletedNotification, self)
         
        
    def getDA(self):
        """ Return the CADView for the Image

getDA()
        """
        return self.CADView

    da = property(getDA, None, None, "DrawingArea for a ImageDocument.")
    
    def getOutlineView(self):
        """ Return the NSOutlineView holding layers for the Image
        
getOutlineView()
        """
        return self.layerOutlineView

    outline_view = property(getOutlineView, None, None, "OutlineView for a ImageDocument.")
    
    def getEntry(self):
        """ Returns the NSTextField for command entry
        
getEntry()
        """
        return self.entryField

    entry = property(getEntry, None, None, "Entry box for a ImageDocument.")
    
    def getSplitView(self):
        """ Returns the NSSplitView containing the OutlineView & DA

getSplitView()
        """
        return self.splitView
        
    def getOption(self, key):
        """Cover method to return the value of an option set in the drawing.

getOption(key)

Return the value of the option associated with the string "key".
If there is no option found for that key, return None.
        """
        return self.getImage().getOption(key)


    def setOption(self, key, value):
        """Cover method to set values of an option in the drawing

setOption(key, value)

The "key" must be a string, and "value" can be anything.
Using the same key twice will result on the second value
overwriting the first.
        """
        self.getImage().setOption(key, value)
        

    def getImage(self):
        """ Returns Generic PythonCad Image object associated with this document
        
getImage()
        """
        return self.__image
    
    image = property(getImage, None, None, "Generic Image object of ImageDocument")
    
    def setImage(self, image):
        """ Sets Generic PythondCad Image object associated with this document
        
setImage(image)
        """
        _curImg = self.getImage()
        if isinstance(_curImg, PythonCAD.Generic.image.Image): 
            PythonCAD.Generic.image.Image.close(_curImg)
        self.__image = image
        _m = self.getMessenger()
        image.connect("added_object", _m.added_object_event)
        image.connect("deleted_object", _m.deleted_object_event)
        image.connect("added_child", _m.added_child_event)
        image.connect("removed_child", _m.removed_child_event)
        
        
    def getMessenger(self):
        """  Returns PythonCad to NSNotificationCenter translation object for
        this document

getMessenger()
        """
        return self.__messenger
        
    def setMessenger(self, m):
        """ Sets PythongCad to NSNotificationCenter translation object for this document
        
setMessenger()
        """
        if not isinstance(m, CocoaMessenger):
            raise TypeError, "Invalid messenger object!"
        self.__messenger = m
        
    def getPrompt(self):
        """Return the current prompt string.

getPrompt()        
        """
        return self.promptField.stringValue()
    
    def setPrompt(self, prompt):
        """Set the current prompt string.

setPrompt(prompt)
        """
        if not isinstance(prompt, types.StringTypes):
            raise TypeError, "Invalid prompt: " + `prompt`
        self.promptField.setStringValue_(prompt)

    prompt = property(getPrompt, setPrompt, None, "Prompt string.")
        
    
    def setTool(self, tool):
        """Replace the tool in the image with a new Tool.

setTool(tool)

The argument "tool" should be an instance of a Tool object.
        """
        if not isinstance(tool, PythonCAD.Generic.tools.Tool):
            raise TypeError, "Invalid tool: " + str(tool)
        self.__tool = tool
        _nc = NSNotificationCenter.defaultCenter()
        _nc.postNotificationName_object_userInfo_(Globals.ToolChangedNotification, self, {"tool" : tool})

    def getTool(self):
        """Return the current Tool used in the drawing.

getTool()        
        """
        return self.__tool
    
    tool = property(getTool, None, None, "Tool for adding/modifying entities.")


    def getPoint(self):
        """Get the current point where the tool is located.

getPoint()

This function returns a tuple with two floats

(x,y)

x: x-coordinate
y: y-coordinate
        """
        return (self.__point_x, self.__point_y)

    def setPoint(self, x, y):
        """Store the point where the tool currently is located at.

setPoint(x,y)

The x and y arguments should be floats.
        """
        _x = x
        _y = y
        try:
            if not isinstance(_x, float):
                _x = float(x)
            if not isinstance(_y, float):
                _y = float(y)
            _str = "%.4f, %.4f" % (_x, _y)
            self.locationField.setStringValue_(_str)
            self.__point_x = _x
            self.__point_y = _y
        except: # need better error handling
            pass
            
    point = property(getPoint, setPoint, None, "Current tool location.")
    
    def reset(self):
        """Set the image to an initial drawing state.

reset()        
        """
        self.__tool = None
        self.setPrompt("Enter command:")
        self.getEntry().setStringValue_("")
        _da = self.getDA()
        _da.setTempObject()
        _da.setNeedsDisplay_(True)


    def changeColor_(self, sender):
        """ Records new colors chosen from color picker.
        
changeColor_(colorPicker)
        """
        _nscolor = sender.color().colorUsingColorSpaceName_("NSCalibratedRGBColorSpace")
        (_r, _g, _b, _a) = _nscolor.getRed_green_blue_alpha_()
        _ir = int(_r*255)
        _ig = int(_g*255)
        _ib = int(_b*255)
        _color = PythonCAD.Generic.color.get_color(_ir, _ig, _ib)
        self.setOption('LINE_COLOR', _color)



