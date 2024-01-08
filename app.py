import datetime
import decimal
import json

from csctracker_py_core.repository.http_repository import cross_origin
from csctracker_py_core.starter import Starter

from repository.FiltersRepository import FiltersRepository
from repository.HeartbeatRepository import HeartbeatRepository
from service.BarDatasetService import BarDataSetService
from service.DatasetService import DatasetService
from service.ScriptsService import ScriptsService
from service.SeriesService import SeriesService

starter = Starter()
app = starter.get_app()
http_repository = starter.get_http_repository()
remote_repository = starter.get_remote_repository()

heartbeats_service = HeartbeatRepository(http_repository, remote_repository)
filters_repository = FiltersRepository(http_repository)
series_repository = SeriesService(heartbeats_service, filters_repository)
dataset_service = DatasetService(heartbeats_service, filters_repository, remote_repository, http_repository)
bar_dataset_service = BarDataSetService(heartbeats_service, filters_repository, remote_repository, http_repository)
scripts_service = ScriptsService(remote_repository)


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


@app.route('/dataset/<table>', methods=['GET'])
@cross_origin()
def generic_dataset(table):
    return (
        json.dumps(dataset_service.get_generic_dataset(table,
                                                       http_repository.get_args(),
                                                       http_repository.get_headers()),
                   cls=Encoder,
                   ensure_ascii=False),
        200,
        {'Content-Type': 'application/json'}
    )


@app.route('/script/<script_name>', methods=['GET'])
@cross_origin()
def scripts(script_name):
    json_data = scripts_service.execute_script(script_name, http_repository.get_headers(), http_repository.get_args())
    return json.dumps(json_data), 200, {'Content-Type': 'application/json'}


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
    return (
        json.dumps(bar_dataset_service.get_generic_dataset(table,
                                                           http_repository.get_args(),
                                                           http_repository.get_headers()),
                   cls=Encoder,
                   ensure_ascii=False),
        200,
        {'Content-Type': 'application/json'}
    )


starter.start()
