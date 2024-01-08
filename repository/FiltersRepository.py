import logging

from csctracker_py_core.repository.http_repository import HttpRepository


class FiltersRepository:
    def __init__(self, http_repository: HttpRepository):
        self.logger = logging.getLogger()
        self.http_repository = http_repository
        pass

    def get_filters(self):
        metric = self.http_repository.get_args().get('metric')
        value = self.http_repository.get_args().get('value')
        period = self.http_repository.get_args().args.get('period')
        if value is None:
            value = "timeSpentMillis"
        self.logger.info("request.args", metric, value, period, self.http_repository.get_args())
        if self.http_repository.get_args().get('userName') is None:
            heeaders = {"userName": "krlsedu@gmail.com"}
            response = self.http_repository.get('http://backend:8080/heartbeats-filters',
                                                params=self.http_repository.get_args(),
                                                headers=heeaders)
        else:
            response = self.http_repository.get('http://backend:8080/heartbeats-filters',
                                                params=self.http_repository.get_args(),
                                                headers=self.http_repository.get_headers())
        filters = response.json()
        return filters

    def get_filters_generic(self):
        response = self.http_repository.get('http://service:5000/filters',
                                            params=self.http_repository.get_args(),
                                            headers=self.http_repository.get_headers())
        filters = response.json()
        return filters
