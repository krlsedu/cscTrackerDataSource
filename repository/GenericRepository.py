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

    def get_objects(self, table, keys=[], data={}, object_=None):
        self.check_sql_injection(table, keys, data)
        col_names, cursor, cursor_ = self.col_names(data, keys, object_, table)
        objects = []
        for row in cursor_:
            obj = {}
            i = 0
            for col_name in col_names:
                obj[col_name[0]] = row[i]
                i += 1
            objects.append(obj)
        cursor.close()
        return objects

    def get_object(self, table, keys=[], data={}, object_=None):
        col_names, cursor, cursor_ = self.col_names(data, keys, object_, table)
        obj = {}
        for row in cursor_:
            i = 0
            for col_name in col_names:
                obj[col_name[0]] = row[i]
                i += 1
            cursor.close()
            return obj

    def col_names(self, data, keys, object_, table):
        if object_ is None:
            ks = "*"
        else:
            ks = object_.__dict__.keys()
            cols = []
            for k in ks:
                cols.append(k)
            ks = str(cols).replace("[", "").replace("]", "").replace("'", "")
        if keys.__len__() > 0:
            select_ = f"select {ks} from {table} where "
            select_ = self.wheres(data, keys, select_)
        else:
            select_ = f"select {ks} from {table}"
        cursor, cursor_ = self.execute_select(select_)
        col_names = cursor.description
        return col_names, cursor, cursor_

    def wheres(self, data, key=[], select_=""):
        for i in range(key.__len__()):
            key_i_ = key[i]
            i_ = data[key_i_]
            tp_ = type(i_)
            if tp_ == str:
                select_ += f"{key_i_}='{i_}'"
            else:
                select_ += f"{key_i_}={i_}"
            if i < key.__len__() - 1:
                select_ += " and "
        return select_

    def execute_select(self, select_):
        cursor = self.conn.cursor()
        cursor.execute(select_)
        cursor_ = cursor.fetchall()
        return cursor, cursor_

    def check_sql_injection(self, table, keys, data):
        select_ = f"select * from {table} limit 1"
        cursor, cursor_ = self.execute_select(select_)
        col_names = cursor.description
        cols_valid = {}
        for row__ in cursor_:
            for col_name in col_names:
                cols_valid[col_name[0]] = col_name[1]
            cursor.close()
            break
        for key in keys:
            if key in data:
                kv_ = data[key]
                if key not in cols_valid.keys():
                    Exception(f"key {key} not found in table {table}")
                tp_ = cols_valid[key]
                if tp_ == 25 or tp_ == 1114:
                    data[key] = kv_.replace("'", "''")
                elif tp_ == 16:
                    data[key] = bool(kv_)
                else:
                    data[key] = float(kv_)
            else:
                Exception(f"key {key} not found in data")
        return data
