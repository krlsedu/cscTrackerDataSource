import logging
from datetime import datetime, timezone

import pandas
from csctracker_py_core.repository.http_repository import HttpRepository
from csctracker_py_core.repository.remote_repository import RemoteRepository

from repository.FiltersRepository import FiltersRepository


class BarDataSetService:
    def __init__(self,
                 heartbeat_repository,
                 filters_repository: FiltersRepository,
                 remote_repository: RemoteRepository,
                 http_repository: HttpRepository):
        self.logger = logging.getLogger()
        self.filters_repository = filters_repository
        self.remote_repository = remote_repository
        self.heartbeat_repository = heartbeat_repository
        self.http_repository = http_repository

    def get_generic_dataset(self, table, args=None, headers=None):
        args_ = {}
        metric_ = None
        date_field_ = None
        mask_ = None
        value_ = None
        for key, value in args.items():
            if key == "metric":
                metric_ = value
            elif key == "date_field":
                date_field_ = value
            elif key == "mask":
                mask_ = value
            elif key == "value":
                value_ = value
            else:
                if key != "with_uncategorized":
                    args_[key] = value
        if metric_ is None:
            metric_ = "value"
        if date_field_ is None:
            date_field_ = "date"
        if value_ is None:
            value_ = "value"
        if mask_ is None:
            mask_ = "{:%m/%Y}"
        elif mask_ == "month":
            mask_ = "{:%m/%Y}"
        elif mask_ == "day":
            mask_ = "{:%d/%m/%Y}"
        elif mask_ == "hour":
            mask_ = "{:%d/%m/%Y %H}"
        elif mask_ == "minute":
            mask_ = "{:%d/%m/%Y %H:%M}"
        elif mask_ == "second":
            mask_ = "{:%d/%m/%Y %H:%M:%S}"

        objects = self.remote_repository.get_objects(table, data=args_, headers=headers)

        date_group = self.group_data(objects, group=date_field_, mask=mask_)

        group = {}
        metrics = []
        categories = []
        for date in date_group:
            if date not in categories:
                categories.append(date)
            metric_group = self.group_data(date_group[date], group=metric_)
            for metric in metric_group:
                if metric not in metrics:
                    metrics.append(metric)
            group[date] = metric_group
        dataset = {'categories': categories, 'series': []}
        series = {}
        categories.sort()
        for category in categories:
            for metric in metrics:
                try:
                    heartbeats = group[category][metric]
                    if metric in series:
                        series[metric].append(self.get_sum(heartbeats, group=value_))
                    else:
                        series[metric] = []
                        series[metric].append(self.get_sum(heartbeats, group=value_))
                except Exception as e:
                    try:
                        series[metric].append(0)
                    except Exception as e:
                        series[metric] = []
                        series[metric].append(0)
        for serie in series:
            serie_ = {'name': serie, 'data': series[serie]}
            dataset['series'].append(serie_)
        return dataset

    def get_dataset(self):
        filters = self.filters_repository.get_filters()

        keys = [filters['metric'], filters['value'], 'date_time']

        heartbeats = self.heartbeat_repository.read_heartbeats(filters, keys)

        args = self.http_repository.get_args()
        if 'with_uncategorized' in args:
            with_uncategorized = args['with_uncategorized'] == 'True'
        else:
            with_uncategorized = False

        date_group = self.group_data(heartbeats, group='date_time', mask='{:%d/%m/%Y}',
                                     with_uncategorized=with_uncategorized)

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
            metric_group = self.group_data(date_group[date], group=filters['metric'], mask=None,
                                           with_uncategorized=with_uncategorized)
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
            self.logger.exception(e)
        return sum

    def group_data(self, heartbeats, group=None, mask=None, with_uncategorized=False):
        date_group = {}
        try:
            for heartbeat in heartbeats:
                metric_ = heartbeat[group]
                if metric_ is None and with_uncategorized:
                    metric_ = 'Uncategorized'
                if mask is not None:
                    try:
                        metric_ = mask.format(
                            datetime.strptime(metric_, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc))
                    except Exception as e:
                        metric_ = mask.format(datetime.strptime(metric_, '%Y-%m-%d').replace(tzinfo=timezone.utc))
                if metric_ is not None:
                    if metric_ in date_group:
                        date_group[metric_].append(heartbeat)
                    else:
                        date_group[metric_] = []
                        date_group[metric_].append(heartbeat)
        except Exception as e:
            self.logger.exception(e)
        return date_group
