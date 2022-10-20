import pandas

from repository.FiltersRepository import FiltersRepository
from service.Interceptor import Interceptor

filters_repository = FiltersRepository()



class BarDataSetService(Interceptor):
    def __init__(self, heartbeat_repository):
        self.heartbeat_repository = heartbeat_repository

    def get_dataset(self):
        filters = filters_repository.get_filters()

        keys = [filters['metric'], filters['value'], 'date_time']

        heartbeats = self.heartbeat_repository.read_heartbeats(filters, keys)

        date_group = self.group_data(heartbeats, group='date_time', mask='{:%d/%m/%Y}')

        group = {}
        metrics = []
        categories = []
        ini_ = filters['dateIni']
        end_ = filters['dateEnd']
        date_range = pandas.date_range(ini_, end_, inclusive="both")
        for date in date_range:
            date_ = date.strftime('%d/%m/%Y')
            if date_ not in categories:
                categories.append(date_)
        for date in date_group:
            metric_group = self.group_data(date_group[date], group=filters['metric'])
            for metric in metric_group:
                if metric not in metrics:
                    metrics.append(metric)
            group[date] = metric_group
        dataset = {'categories': categories, 'series': []}
        series = {}
        for category in categories:
            for metric in metrics:
                try:
                    heartbeats = group[category][metric]
                    if metric in series:
                        series[metric].append(self.get_sum(heartbeats, group=filters['value']))
                    else:
                        series[metric] = []
                        series[metric].append(self.get_sum(heartbeats, group=filters['value']))
                except Exception as e:
                    try:
                        series[metric].append(0)
                    except Exception as e:
                        series[metric] = []
                        series[metric].append(0)
        for serie in series:
            serie_ = {}
            serie_['name'] = serie
            serie_['data'] = series[serie]
            dataset['series'].append(serie_)
        return dataset

    def get_sum(self, heartbeats, group=None):
        sum = 0
        try:
            for heartbeat in heartbeats:
                metric_ = heartbeat[group]
                if metric_ is not None:
                    sum += metric_
        except Exception as e:
            print(e)
        return sum

    def group_data(self, heartbeats, group=None, mask=None):
        date_group = {}
        try:
            for heartbeat in heartbeats:
                metric_ = heartbeat[group]
                if mask is not None:
                    metric_ = mask.format(metric_)
                if metric_ is not None:
                    if metric_ in date_group:
                        date_group[metric_].append(heartbeat)
                    else:
                        date_group[metric_] = []
                        date_group[metric_].append(heartbeat)
        except Exception as e:
            print(e)
        return date_group
