from flask import request

from repository.FiltersRepository import FiltersRepository
from service.Interceptor import Interceptor

filters_repository = FiltersRepository()


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
