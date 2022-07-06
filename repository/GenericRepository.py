import psycopg2

from service.Interceptor import Interceptor


class GenericRepository(Interceptor):
    def __init__(self):
        self.conn = psycopg2.connect(
            host="postgres",
            database="postgres",
            user="postgres",
            password="postgres")

    def execute_query(self, select_):
        cursor = self.conn.cursor()
        cursor.execute(select_)
        cursor_ = cursor.fetchall()
        return cursor, cursor_

    def read_by_id(self, id_, filters):
        keys = filters['keys']
        table_ = filters['table']
        user_ = filters['userId']
        select_ = "SELECT " + str(keys).replace("[", "").replace("]", "").replace("'", "") + " FROM " + table_ + \
                  " where id = " + id_ + " and user_id = " + str(user_)

        cursor, cursor_ = self.execute_query(select_)
        for row in cursor_:
            obj = {}
            i = 0
            for key in keys:
                obj[key] = row[i]
                i += 1
            cursor.close()
            return obj
        cursor.close()
        return {}

    def read(self, filters):
        ini_ = filters['dateIni']
        end_ = filters['dateEnd']
        user_ = filters['userId']
        table_ = filters['table']
        keys = filters['keys']
        select_ = "SELECT " + str(keys).replace("[", "").replace("]", "").replace("'", "") + " FROM " + table_ + \
                  " where date_time between '" + ini_ + "' and '" + end_ + "' and user_id = " + str(user_)

        cursor, cursor_ = self.execute_query(select_)
        objs = []
        for row in cursor_:
            obj = {}
            i = 0
            for key in keys:
                obj[key] = row[i]
                i += 1
            objs.append(obj)
        cursor.close()
        return objs
