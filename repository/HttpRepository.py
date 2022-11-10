import requests
from flask import request

from service.Interceptor import Interceptor

url_repository = 'http://repository:5000/'


class HttpRepository(Interceptor):
    def __init__(self):
        super().__init__()

    def insert(self, table, data, headers=None):
        if headers is None:
            headers = request.headers
        try:
            response = requests.post(url_repository + table, headers=headers, json=data)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error inserting data: {response.text}')
        except Exception as e:
            raise e

    def update(self, table, keys=[], data={}, headers=None):
        if headers is None:
            headers = request.headers
        params = {}
        for key in keys:
            params[key] = data[key]
        try:
            response = requests.post(url_repository + table, headers=headers, json=data, params=params)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error updating data: {response.text}')
        except Exception as e:
            raise e

    def add_user_id(self, data, headers=None):
        if headers is None:
            headers = request.headers
        user = self.get_user(headers)
        data['user_id'] = user['id']
        return data

    def get_user(self, headers=None):
        if headers is None:
            headers = request.headers
        user_name = headers.get('userName')
        try:
            user = self.get_object('users', ['email'], {'email': user_name}, headers)
            return user
        except Exception as e:
            raise e

    def get_object(self, table, keys=[], data={}, headers=None):
        if headers is None:
            headers = request.headers
        params = {}
        for key in keys:
            params[key] = data[key]
        try:
            response = requests.get(url_repository + 'single/' + table, params=params, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def get_objects(self, table, keys=[], data={}, headers=None):
        if headers is None:
            headers = request.headers
        params = {}
        for key in keys:
            params[key] = data[key]
        try:
            response = requests.get(url_repository + table, params=params, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def execute_select(self, select, headers=None):
        if headers is None:
            headers = request.headers
        command = {
            'command': select
        }
        try:
            response = requests.post(url_repository + "command/select", headers=headers, json=command)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def exist_by_key(self, table, key=[], data={}, headers=None):
        if headers is None:
            headers = request.headers
        try:
            objects = self.get_objects(table, key, data, headers)
            return objects.__len__() > 0
        except Exception as e:
            return False

    def get_filters(self, args=None):
        filters = []
        values = {}
        for key in args:
            filters.append(key)
            values[key] = args[key]
        return filters, values
