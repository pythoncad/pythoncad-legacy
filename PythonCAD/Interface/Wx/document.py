
from Generic.Kernel.pycadkernel import PyCadDbKernel


class Document(object):

    def __init__(self, parent):
        self.__cadwindow = parent
        self.__cadkernel = None


    def __GetKernel():
        return self.__cadkernel

    Kernel = property(__GetKernel, None, None, "Gets the kernel")


    def Open(self, filename):
        # todo: check filename

        # open a new kernel
        self.__cadkernel = PyCadDbKernel(filename)

