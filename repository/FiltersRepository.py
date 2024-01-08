import logging

from csctracker_py_core.repository.http_repository import HttpRepository


class FiltersRepository:
    def __init__(self, http_repository: HttpRepository):
        self.logger = logging.getLogger()
        self.http_repository = http_repository
        pass

    def get_filters(self):
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
