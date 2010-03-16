
from Generic.Kernel.pycadkernel import PyCadDbKernel
#from Generic.Kernel.pycadsettings import PyCadSettings
#from Interface.Wx.quadtree import Quadtree


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


    def __GetKernel(self):
        return self.__cadkernel

    Kernel = property(__GetKernel, None, None, "Gets the kernel")


    def Open(self, filename):
        # todo: check filename

        # open a new kernel
        print "before open"
        self.__cadkernel = PyCadDbKernel(filename)
        print "after open"
        # create a spatial index
        self.__RebuildIndex()
        # create the displaylayers
        #self.__CreateDisplayLayers()
        # draw all items
        self.__viewport.ZoomAll()


    def __RebuildIndex(self):
        """
        Rebuilds the spatial index for all entities in the database
        """
        # index object
        index = self.__cadkernel.getSpIndex()
        
        if index is not None:
            print "index constructed"
            # remove current content
            index.RemoveAll()
            # get all entities from the database
            entities = self.__cadkernel.getEntityFromType('SEGMENT')
            # traverse each layer in the list
            for entity in entities:
                # add entity to index
                index.Insert(entity.getId(), entity.getBBox())
                # add entity to display
                self.__AddEntityToDisplay(entity)

            print "index rebuild"
        else:
            print "error rebuilding index"


    def __AddEntityToDisplay(self, entity):
        """
        Add an entity do the viewport displaylist
        """
        # for now create a single layer
        dummy_layer = 'standard'
        # TODO: real layer creation
        display_layer = self.__viewport.GetDisplayLayer(dummy_layer)
        
        if display_layer is not None:
            # add entity to display layer
            display_layer.AddEntity(entity)


    def GetDrawingExtents(self):
        """
        Gets the min_x, min_y, max_x, max_y for all entities
        """
        # index object
        index = self.__cadkernel.getSpIndex()
        
        if index is not None:
            # get the extents from the index
            return index.GetExtents()
        # error        
        return None



