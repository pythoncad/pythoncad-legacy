
from Generic.Kernel.pycadkernel import PyCadDbKernel
from Interface.Wx.quadtree import Quadtree


class Document(object):
	"""
	The Document is the interface to the cad kernel.
	The spatial index (quad tree's) are in the Document.
	For on screen display see the ViewPort class.
	"""
    def __init__(self, parent, viewport):
		# quadtree indices (per layer there is a quadtree
		self.__spatial_indices = {}
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
		# TODO: create quadtree indices
		
        # draw all items
        self.__viewport.ZoomAll()
        
		
	def CreateLayerList(self):
		pass
		

	def GetDrawingExtents(self):
		pass
		
		
		
		
