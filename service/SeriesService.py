
from datetime import datetime

import pytz

from repository.FiltersRepository import FiltersRepository
from service.Interceptor import Interceptor
from service.Utils import Utils

filters_repository = FiltersRepository()


class SeriesService(Interceptor):
    def __init__(self, heartbeat_repository):
        self.heartbeat_repository = heartbeat_repository

    def get_series(self):
        filters = filters_repository.get_filters()
        metric = filters['metric']

        keys = [filters['metric'], filters['value'], 'date_time', 'date_time_end']

        heartbeats = self.heartbeat_repository.read_heartbeats(filters, keys)
        map_series = {}

        try:
            for heartbeat in heartbeats:
                metric_ = heartbeat[metric]
                if metric_ is not None:
                    if metric_ in map_series:
                        map_series[metric_].append(heartbeat)
                    else:
                        map_series[metric_] = []
                        map_series[metric_].append(heartbeat)
        except Exception as e:
            print(e)
        series = []
        for key in map_series:
            heartbeats = map_series[key]
            list = sorted(heartbeats, key=lambda x: datetime.strptime(x['date_time'], '%Y-%m-%d %H:%M:%S.%f')
                          .timestamp(), reverse=False)
            start_time = None
            end_time = None
            for heartbeat in list:
                dt_time = datetime.strptime(Utils.get_format_date_time_in_tz(heartbeat['date_time'],
                                                                             '%Y-%m-%d %H:%M:%S.%f',
                                                                             'UTC',
                                                                             'America/Sao_Paulo'),
                                            '%Y-%m-%d %H:%M:%S.%f')
                dt_time = pytz.UTC.localize(dt_time)
                start_time_atu = int(dt_time.timestamp() * 1000)
                dt_time_end = datetime.strptime(Utils.get_format_date_time_in_tz(heartbeat['date_time_end'],
                                                                                 '%Y-%m-%d %H:%M:%S.%f',
                                                                                 'UTC',
                                                                                 'America/Sao_Paulo'),
                                                '%Y-%m-%d %H:%M:%S.%f')
                dt_time_end = pytz.UTC.localize(dt_time_end)
                end_time_atu = int(dt_time_end.timestamp() * 1000)
                if start_time is None:
                    start_time = start_time_atu
                if end_time is None:
                    end_time = end_time_atu

                diff = start_time_atu - end_time
                if diff > 100:
                    arr = [int(start_time), int(end_time)]
                    serie = {}
                    serie['x'] = key
                    serie['y'] = arr
                    series.append(serie)
                    start_time = start_time_atu
                end_time = end_time_atu
            arr = [int(start_time), int(end_time)]
            serie = {}
            serie['x'] = key
            serie['y'] = arr
            series.append(serie)
        return series
