import psycopg2

from model.Heartbeat import Heartbeat


class HeartbeatRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="postgres",
            database="postgres",
            user="postgres",
            password="postgres")

    def read_heartbeats(self, filters, keys=None):
        ini_ = filters['dateIni']
        end_ = filters['dateEnd']
        user_ = filters['userId']
        heartbeat = Heartbeat()
        if keys is None:
            select_heartbeats = "SELECT " + heartbeat.get_cols_select() + " FROM heartbeat where date_time between '" \
                                + ini_ + "' and '" + end_ + "' and user_id = " + str(user_)
        else:
            select_heartbeats = "SELECT " + str(keys).replace("[", "").replace("]", "").replace("'", "") + \
                                " FROM heartbeat where date_time between '" \
                                + ini_ + "' and '" + end_ + "' and user_id = " + str(user_)

        cursor = self.conn.cursor()
        cursor.execute(select_heartbeats)
        cursor_heartbeats = cursor.fetchall()

        heartbeats = []
        for row in cursor_heartbeats:
            hb = {}
            if keys is None:
                for key in heartbeat.__dict__:
                    hb[key] = row[heartbeat.__dict__[key]]
            else:
                i = 0
                for key in keys:
                    hb[key] = row[i]
                    i += 1
            heartbeats.append(hb)
        cursor.close()
        return heartbeats

    def get_grouped(self, filters):
        cursor = self.conn.cursor()

        metric_1 = filters['metric']
        filters_value_ = filters['value']
        ini_ = filters['dateIni']
        end_ = filters['dateEnd']
        user_ = filters['userId']
        filters_metric_ = "SELECT " + metric_1 + ", sum(" + filters_value_ + ") " \
                                                                             "FROM heartbeat where date_time " \
                                                                             "between '" + ini_ + "' and '" + end_ + \
                          "' and user_id = " + str(user_) + \
                          " group by " + metric_1
        cursor.execute(
            filters_metric_)
        heartbeats = cursor.fetchall()
        cursor.close()
        return heartbeats
