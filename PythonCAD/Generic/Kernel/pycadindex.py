# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="gertwin"
__date__="$Mar 11, 2010 9:44:52 PM$"

from pysqlite2 import dbapi2 as sql


class PyCadIndex(object):
    """
    Sqlite specific index.
    """

    def __init__(self, connection):
        # connection to the database
        self.__connetion = connection
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

        if cur.fetchone() is not None:
            index_exists = True

        if not index_exists:
            try:
                # create index
                cur.execute('CREATE VIRTUAL TABLE sp_index USING rtree (id, min_x, max_x, min_y, max_y)')
                self.__connetion.commit()
            except sql.Error, e:
                print "Sqlite error:", e.args[0]

        cur.close()


    def RemoveAll(self):
        """
        Remove all entities from the index
        """
        cur = self.__connetion.cursor()

        try:
            cur.execute('DELETE FROM sp_index')
        except sql.Error, e:
            print "Sqlite error:", e.args[0]

        self.__connetion.commit()
        cur.close()


    def Remove(self, id):
        """
        Remove a single entity from the index
        """
        cur = self.__connetion.cursor()
        t = (id,)

        try:
            cur.execute('DELETE FROM sp_index WHERE id=?', t)
        except sql.Error, e:
            print "Sqlite error:", e.args[0]

        self.__connetion.commit()
        cur.close()

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

    def Insert(self, id, mbr):
        """
        Insert an entity in the index based on its bounding rectangle
        """
        cur = self.__connetion.cursor()

        try:
            # check bounding rectangle
            mbr = self.__CheckMBR(mbr)
            # parameter template
            t = (id, mbr[0], mbr[2], mbr[1], mbr[3],)
            cur.execute('INSERT INTO sp_index VALUES (?,?,?,?,?)', t)
        except sql.Error, e:
            print "Sqlite error:", e.args[0]

        self.__connetion.commit()
        cur.close()


    def GetInside(self, boundary):
        """
        Get all the entities that are inside the boundary
        This is simple first approach, refinement is needed
        TODO: make this better
        """
        # result is a list of entity ids
        result = []
        cur = self.__connetion.cursor()

        try:
            t = (boundary[0], boundary[1], boundary[2], boundary[3],)
            # select candidates from the index
            cur.execute('SELECT id FROM sp_index WHERE minX<=? AND maxX>=? AND minY<=? AND maxY>=?', t)
            # add the candidates to the list
            for row in cur:
                result.append(row.id)
        except sql.Error, e:
            print "Sqlite error:", e.args[0]

        cur.close()
        # return result
        return result


    def GetExtents(self):
        """
        Get the extents from all index entities
        """
        cur = self.__connetion.cursor()

        try:
            # select candidates from the index
            cur.execute('SELECT min(min_x), min(min_y), max(max_x), max(max_y) FROM sp_index')
            # add the candidates to the list
            row = cur.fetchone()
            # is there any result
            if row is not None:
                return row

        except sql.Error, e:
            print "Sqlite error:", e.args[0]

        cur.close()
        return (0.0, 0.0, 0.0, 0.0)

