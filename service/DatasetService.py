from flask import request

from repository.FiltersRepository import FiltersRepository
from repository.HttpRepository import HttpRepository
from service.Interceptor import Interceptor

filters_repository = FiltersRepository()
http_repository = HttpRepository()


class DatasetService(Interceptor):
    def __init__(self, heartbeat_repository):
        self.heartbeat_repository = heartbeat_repository

    def get_dataset(self):
        heartbeats = self.heartbeat_repository.get_grouped(filters_repository.get_filters())
        datasets = []

        args = request.args
        if 'with_uncategorized' in args:
            with_uncategorized = args['with_uncategorized'] == 'True'
        else:
            with_uncategorized = False
        for row in heartbeats:
            row_ = row['label']
            if row_ is None and with_uncategorized:
                row_ = 'Uncategorized'
            if row_ is not None:
                dataset = {'label': row_, 'value': int(row['value'])}
                datasets.append(dataset)
        return datasets

    def get_generic_dataset(self, table, args=None, headers=None):
        args_ = {}
        metric_ = None
        value_ = 'value'
        for key, value in args.items():
            if key == "metric":
                metric_ = value
            elif key == "value":
                value_ = value
            elif key != "with_uncategorized":
                args_[key] = value

        keys_, values_ = http_repository.get_filters(args_)
        rows = http_repository.get_objects(table, keys_, values_, headers)
        return self.group_data(rows, metric_, with_uncategorized=args['with_uncategorized'], value=value_)

    def group_data(self, rows, metric, with_uncategorized=False, value='value'):
        date_group = {}
        try:
            for row in rows:
                metric_ = row[metric]
                if metric_ is None and with_uncategorized:
                    metric_ = 'Uncategorized'
                if metric_ is not None:
                    if metric_ in date_group:
                        date_group[metric_] += row[value]
                    else:
                        date_group[metric_] = row[value]
        except Exception as e:
            print(e)

        values = []
        for key, value in date_group.items():
            values.append({'label': key, 'value': value})
        return values
