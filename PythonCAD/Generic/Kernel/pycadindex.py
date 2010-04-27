# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="gertwin"
__date__="$Mar 11, 2010 9:44:52 PM$"

from pysqlite2 import dbapi2 as sql
from Generic.Kernel.pycadtransaction import Transaction
from Generic.Kernel.exception import *

print "Pysql2 --" , sql.__file__

class PyCadIndex(object):
    """
    Sqlite specific index.
    """

    def __init__(self, connection):
        # connection to the database
        self.__connetion = connection
        # cursor
        self._cursor = None
        # name of index table
        self.__index_tablename = "sp_index"
        # check if the index exists
        self.__CheckIndex()


    def __CheckIndex(self):
        """
        Create an index if this does not exists
        """
        index_exists = False

        cur = self.__connetion.cursor()

        try:
            t = ('sp_index', )
            cur.execute('SELECT name FROM sqlite_master WHERE tbl_name=?', t)
        except sql.Error, e:
            print "Sqlite error:", e.args[0]
            return

        if cur.fetchone() is None:
            try:
                # create index
                cur.execute('CREATE VIRTUAL TABLE sp_index USING rtree (id, min_x, max_x, min_y, max_y)')
                self.__connetion.commit()
            except sql.Error, e:
                msg= "Unable to create the virtual table Error : Sqlite error:", e.args[0]
                raise StructuralError, msg
        cur.close()


    def GetTransaction(self):
        """
        returns a new constructed spatial index object
        """
        try:
            transaction = Transaction(self.__connetion)
            return transaction
        except:
            self.__logger.debug('Unable to create transaction object')
        return None


    def RemoveAll(self, transaction):
        """
        Remove all entities from the index
        """
        try:
            transaction.Cursor.execute('DELETE FROM sp_index')
        except sql.Error, e:
            msg ="Unable to RemoveAll the index Sqlite error:", e.args[0]
            raise StructuralError, msg
        return


    def Remove(self, transaction, id):
        """
        Remove a single entity from the index
        """
        t = (id,)

        try:
            transaction.Cursor.execute('DELETE FROM sp_index WHERE id=?', t)
        except sql.Error, e:
            msg ="Unable to remove the index Sqlite error:", e.args[0]
            raise StructuralError, msg
        return


    def __CheckMBR(self, mbr):
        """
        Check the MBR: min_x < max_x and min_y < max_y
        TODO: what if min_x == max_x or min_y == max_y
        """
        # check min_x < max_x
        if mbr[0] > mbr[2]:
            temp = mbr[0]
            mbr[0] = mbr[2]
            mbr[2] = temp
        # check min_y < max_y
        if mbr[1] > mbr[3]:
            temp = mbr[1]
            mbr[1] = mbr[3]
            mbr[3] = temp
        return mbr

    def Insert(self, transaction, id, mbr):
        """
        Insert an entity in the index based on its bounding rectangle
        """
        try:
            # check bounding rectangle
            mbr = self.__CheckMBR(mbr)
            # parameter template
            t = (id, mbr[0], mbr[2], mbr[1], mbr[3],)
            transaction.Cursor.execute('INSERT INTO sp_index VALUES (?,?,?,?,?)', t)
        except sql.Error, e:
            msg="Unable to insert the index Sqlite error:", e.args[0]
            raise StructuralError, msg
        return

    def GetInside(self, transaction, boundary):
        """
        Get all the entities that are inside the boundary
        This is simple first approach, refinement is needed
        TODO: make this better
        """
        # result is a list of entity ids
        result = []

        try:
            t = (boundary[0], boundary[1], boundary[2], boundary[3],)
            # select candidates from the index
            transaction.Cursor.execute('SELECT id FROM sp_index WHERE minX<=? AND maxX>=? AND minY<=? AND maxY>=?', t)
            # add the candidates to the list
            for row in transaction.Cursor:
                result.append(row.id)
        except sql.Error, e:
            msg="Sqlite error:", e.args[0]
            raise StructuralError, msg
        return result

    def GetExtents(self, transaction):
        """
            Get the extents from all index entities
        """
        try:
            # select candidates from the index
            transaction.Cursor.execute('SELECT min(min_x), min(min_y), max(max_x), max(max_y) FROM sp_index')
            # add the candidates to the list
            row = transaction.Cursor.fetchone()
            # is there any result
            if row is not None:
                return row
        except sql.Error, e:
            msg="GetExtents Sqlite error:", e.args[0]
            raise StructuralError(msg)

