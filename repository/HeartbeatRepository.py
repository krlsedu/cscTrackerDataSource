import psycopg2
from flask import request

from model.Heartbeat import Heartbeat
from repository.GenericRepository import GenericRepository
from service.Interceptor import Interceptor

generic_repository = GenericRepository()


class HeartbeatRepository(Interceptor):
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
        dashboard_token_ = request.args.get('dashboardToken')
        if dashboard_token_ == 'undefined':
            dashboard_token_ = None
        heartbeat = Heartbeat()
        if keys is None:
            select_heartbeats = "SELECT " + heartbeat.get_cols_select() + " FROM heartbeat where date_time between '" \
                                + ini_ + "' and '" + end_ + "' and user_id = " + str(user_)
        else:
            select_heartbeats = "SELECT " + str(keys).replace("[", "").replace("]", "").replace("'", "") + \
                                " FROM heartbeat where date_time between '" \
                                + ini_ + "' and '" + end_ + "'"

        if dashboard_token_ is not None:
            dash_info = generic_repository.get_object("external_dash", ["hash"], {"hash": dashboard_token_})
            if dash_info is not None:
                select_heartbeats += " and client_name = '" + str(dash_info['client_name']) + "'"
            else:
                select_heartbeats += " and user_id = " + str(user_)
        else:
            select_heartbeats += " and user_id = " + str(user_)

        cursor, cursor_heartbeats = self.execute_query(select_heartbeats)

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

    def execute_query(self, select_heartbeats):
        cursor = self.conn.cursor()
        cursor.execute(select_heartbeats)
        cursor_heartbeats = cursor.fetchall()
        return cursor, cursor_heartbeats

    def ajust_heartbeats(self, heartbeats):
        colision_hb = []

        heartbeats.sort(key=lambda x: x['date_time'])

        hb_ant = None

        for heartbeat in heartbeats:
            if hb_ant is None:
                hb_ant = heartbeat
                continue
            for hb in colision_hb:
                if self.get_colisions(hb, heartbeat):
                    if colision_hb.__contains__(hb_ant):
                        colision_hb.append(hb_ant)

                    colision_hb.append(heartbeat)

        return heartbeats

    def get_colision_time(self, hb_ant, hb_post):
        if hb_ant['date_time_end'] >= hb_post['date_time']:
            if hb_ant['date_time_end'] >= hb_post['date_time_end']:
                return hb_post['time_spent_millis']
            return (hb_ant['date_time_end'].timestamp() - hb_post['date_time'].timestamp()) * 1000
        return 0

    def get_colisions(self, heartbeat_ant, heartbeat_post):
        if heartbeat_ant['date_time_end'] >= heartbeat_post['date_time']:
            return True
        return False

    def get_grouped(self, filters):
        cursor = self.conn.cursor()

        metric_1 = filters['metric']
        filters_value_ = filters['value']
        ini_ = filters['dateIni']
        end_ = filters['dateEnd']
        user_ = filters['userId']
        dashboard_token_ = request.args.get('dashboardToken')
        if dashboard_token_ == 'undefined':
            dashboard_token_ = None
        filters_metric_ = "SELECT " + metric_1 + ", sum(" + filters_value_ + ") " \
                                                                             "FROM heartbeat where date_time " \
                                                                             "between '" + ini_ + "' and '" + end_ + \
                          "' "
        if dashboard_token_ is not None:
            dash_info = generic_repository.get_object("external_dash", ["hash"], {"hash": dashboard_token_})
            if dash_info is not None:
                filters_metric_ += " and client_name = '" + str(dash_info['client_name']) + "'"
            else:
                filters_metric_ += " and user_id = " + str(user_)
        else:
            filters_metric_ += " and user_id = " + str(user_)
        filters_metric_ += " group by " + metric_1
        cursor.execute(
            filters_metric_)
        heartbeats = cursor.fetchall()
        cursor.close()
        return heartbeats
