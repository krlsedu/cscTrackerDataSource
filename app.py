import json

from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from repository.HeartbeatRepository import HeartbeatRepository
from service.BarDatasetService import BarDataSetService
from service.DatasetService import DatasetService
from service.PersistService import PersistService
from service.SeriesService import SeriesService

app = Flask(__name__)

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint')

heartbeats_service = HeartbeatRepository()
series_repository = SeriesService(heartbeats_service)
dataset_service = DatasetService(heartbeats_service)
bar_dataset_service = BarDataSetService(heartbeats_service)
persist_service = PersistService


@app.route('/dataset', methods=['GET'])
def dataset():
    return json.dumps(dataset_service.get_dataset()), 200, {'Content-Type': 'application/json'}


@app.route('/series', methods=['GET'])
def serie():
    return json.dumps(series_repository.get_series()), 200, {'Content-Type': 'application/json'}


@app.route('/bar-dataset', methods=['GET'])
def bar_dataset():
    return json.dumps(bar_dataset_service.get_dataset()), 200, {'Content-Type': 'application/json'}

@app.route('/save', methods=['POST'])
def post_metrics():
    json = request.get_json()
    return persist_service.persist(json)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
