import requests
from flask import request

from repository.FiltersRepository import FiltersRepository
from repository.GenericRepository import GenericRepository
from service.Interceptor import Interceptor

generic_repository = GenericRepository()
filter_repository = FiltersRepository()


class PersistService(Interceptor):
    def __init__(self):
        pass

    def persist(self, data):
        response = requests.get('http://service:5000/service?service=transaction')
        url_ = response.json()['url'] + 'save'
        if not self.is_insert(data):
            filters = filter_repository.get_filters_generic()
            obj = generic_repository.get_by_id(data['id'], filters)
            if obj is not None:
                for key in data:
                    obj[key] = data[key]
                data = obj
        response = requests.post(url_, headers=request.headers, json=data)
        return response.json(), response.status_code

    def is_insert(self, data):
        return data['id'] is None or data['id'] == 'null'
