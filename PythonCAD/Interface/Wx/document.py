
from Generic.Kernel.pycadkernel import PyCadDbKernel
from Generic.Kernel.pycadsettings import PyCadSettings
from Interface.Wx.quadtree import Quadtree


class Document(object):
    """
    The Document is the interface to the cad kernel.
    The spatial index (quad tree's) are in the Document.
    For on screen display see the ViewPort class.
    """
    def __init__(self, parent, viewport):
        # list of display layers
        self.__display_layers = {}
        # reference to the cad window
        self.__cadwindow = parent
        # cad kernel is created on file open
        self.__cadkernel = None
        # viewport reference
        self.__viewport = viewport
        # make the document known to the view
        viewport.Document = self


    def __GetKernel():
        return self.__cadkernel

    Kernel = property(__GetKernel, None, None, "Gets the kernel")


    def Open(self, filename):
        # todo: check filename

        # open a new kernel
        self.__cadkernel = PyCadDbKernel(filename)
        # create the displaylayers
        self.__CreateDisplayLayers()
        # draw all items
        self.__viewport.ZoomAll()


    def __CreateDisplayLayers(self):
        """
        Creates an display layer list from the database
        """
        # first get all layers from the database
        layers = self.__cadkernel.getEntityFromType('LAYER')
        # traverse each layer in the list
        for layer in layser:
            layer_ent = layer[0]


    def GetDrawingExtents(self):
        pass




