
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
        self._layers_display = {}
        # reference to the cad window
        self._cadwindow = parent
        # cad kernel is created on file open
        self._cadkernel = None
        # viewport reference
        self._viewport = viewport
        # make the document known to the view
        viewport.Document = self


    def __GetKernel(self):
        return self._cadkernel

    Kernel = property(__GetKernel, None, None, "Gets the kernel")


    def Open(self, filename):
        # todo: check filename

        # open a new kernel
        print "before open"
        self._cadkernel = PyCadDbKernel(filename)
        print "after open"
        # create a spatial index
        self.RebuildIndex()
        # regenerate drawing
        self.Regen()
        # draw all items
        self._viewport.ZoomAll()


    def RebuildIndex(self):
        """
        Rebuilds the spatial index for all entities in the database
        """
        # index object
        index = self._cadkernel.getSpIndex()
        
        if index is not None:
            print "index constructed"
            # remove current content
            index.RemoveAll()
            # get all entities from the database
            entities = self._cadkernel.getEntityFromType('SEGMENT')
            # traverse each layer in the list
            for entity in entities:
                # add entity to index
                index.Insert(entity.Id, entity.getBBox())

            print "index rebuild"
        else:
            print "error rebuilding index"


    def Regen(self):
        """
        Rebuild display lists and redraw the viewport
        """
        # get all entities from the database
        entities = self._cadkernel.getEntityFromType('SEGMENT')
        # traverse each layer in the list
        for entity in entities:
            # add entity to view port
            self._viewport.AddEntity(entity)
        
 
    def GetDrawingExtents(self):
        """
        Gets the min_x, min_y, max_x, max_y for all entities
        """
        # index object
        index = self._cadkernel.getSpIndex()
        
        if index is not None:
            # get the extents from the index
            return index.GetExtents()
        # error        
        return None



