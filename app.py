import datetime
import decimal
import json
import threading

from flask import Flask, request
from flask_cors import CORS, cross_origin
from prometheus_flask_exporter import PrometheusMetrics

from repository.HeartbeatRepository import HeartbeatRepository
from service.BarDatasetService import BarDataSetService
from service.DatasetService import DatasetService
from service.LoadBalancerRegister import LoadBalancerRegister
from service.SeriesService import SeriesService

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint', default_labels={'application': 'CscTrackerDataSource'})

heartbeats_service = HeartbeatRepository()
series_repository = SeriesService(heartbeats_service)
dataset_service = DatasetService(heartbeats_service)
bar_dataset_service = BarDataSetService(heartbeats_service)
balancer = LoadBalancerRegister()


def schedule_job():
    balancer.register_service('datasource')


t1 = threading.Thread(target=schedule_job, args=())
t1.start()


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')


@app.route('/dataset', methods=['GET'])
@cross_origin()
def dataset():
    return json.dumps(dataset_service.get_dataset()), 200, {'Content-Type': 'application/json'}


@app.route('/series', methods=['GET'])
@cross_origin()
def serie():
    return json.dumps(series_repository.get_series()), 200, {'Content-Type': 'application/json'}


@app.route('/bar-dataset', methods=['GET'])
@cross_origin()
def bar_dataset():
    return json.dumps(bar_dataset_service.get_dataset()), 200, {'Content-Type': 'application/json'}


@app.route('/bar-dataset/<table>', methods=['GET'])
@cross_origin()
def bar_generic_dataset(table):
    return json.dumps(bar_dataset_service.get_generic_dataset(table, request.args, request.headers), cls=Encoder,
                      ensure_ascii=False), 200, {
        'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
