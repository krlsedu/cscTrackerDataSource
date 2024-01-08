import logging

from csctracker_py_core.repository.http_repository import HttpRepository
from csctracker_py_core.repository.remote_repository import RemoteRepository

from repository.FiltersRepository import FiltersRepository


class DatasetService:
    def __init__(self, heartbeat_repository,
                 filters_repository: FiltersRepository,
                 remote_repository: RemoteRepository,
                 http_repository: HttpRepository):
        self.logger = logging.getLogger()
        self.filters_repository = filters_repository
        self.remote_repository = remote_repository
        self.http_repository = http_repository
        self.heartbeat_repository = heartbeat_repository

    def get_dataset(self):
        heartbeats = self.heartbeat_repository.get_grouped(self.filters_repository.get_filters())
        datasets = []

        args = self.http_repository.get_args()
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
        rows = self.remote_repository.get_objects(table, data=args_, headers=headers)
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
            self.logger.exception(e)

        values = []
        for key, value in date_group.items():
            values.append({'label': key, 'value': value})

        values = sorted(values, key=lambda x: x['value'], reverse=True)
        return values
