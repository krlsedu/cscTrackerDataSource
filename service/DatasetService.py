from repository.FiltersRepository import FiltersRepository

filters_repository = FiltersRepository()


class DatasetService:
    def __init__(self, heartbeat_repository):
        self.heartbeat_repository = heartbeat_repository

    def get_dataset(self):
        heartbeats = self.heartbeat_repository.get_grouped(filters_repository.get_filters())
        datasets = []
        for row in heartbeats:
            print(row)
            row_ = row[0]
            if row_ is not None:
                dataset = {'label': row_, 'value': int(row[1])}
                datasets.append(dataset)
        return datasets
