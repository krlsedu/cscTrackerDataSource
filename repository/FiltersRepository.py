from flask import request
import requests

from service.Interceptor import Interceptor


class FiltersRepository(Interceptor):
    def __init__(self):
        pass

    def get_filters(self):
        metric = request.args.get('metric')
        value = request.args.get('value')
        period = request.args.get('period')
        if value is None:
            value = "timeSpentMillis"
        print("request.args", metric, value, period, request.args)
        response = requests.get('http://backend:8080/heartbeats-filters', params=request.args,
                                headers=request.headers)
        filters = response.json()
        return filters
