import json

import psycopg2
from flask import Flask, request
import requests
from datetime import datetime
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint')


@app.route('/dataset', methods=['GET'])
def dataset():
    metric = request.args.get('metric')
    value = request.args.get('value')
    period = request.args.get('period')
    if value is None:
        value = "timeSpentMillis"
    print("request.args", metric, value, period, request.args)
    response = requests.get('http://backend:8080/heartbeats-filters', params=request.args,
                            headers=request.headers)
    filters = response.json()

    conn = psycopg2.connect(
        host="postgres",
        database="postgres",
        user="postgres",
        password="postgres")

    cursor = conn.cursor()

    metric_1 = filters['metric']
    filters_value_ = filters['value']
    ini_ = filters['dateIni']
    end_ = filters['dateEnd']
    user_ = filters['userId']
    filters_metric_ = "SELECT " + metric_1 + ", sum(" + filters_value_ + ") " \
                                                                         "FROM heartbeat where date_time " \
                                                                         "between '" + ini_ + "' and '" + end_ + \
                      "' and user_id = " + str(user_) + \
                      " group by " + metric_1
    cursor.execute(
        filters_metric_)
    heartbeats = cursor.fetchall()
    datasets = []
    for row in heartbeats:
        print(row)
        row_ = row[0]
        if row_ is not None:
            dataset = {'label': row_, 'value': int(row[1])}
            datasets.append(dataset)
    conn.close()
    return json.dumps(datasets), 200, {'Content-Type': 'application/json'}


@app.route('/series', methods=['GET'])
def serie():
    metric = request.args.get('metric')
    response = requests.get('http://backend:8080/heartbeats', headers=request.headers, params=request.args)
    heartbeats = response.json()
    print(response.status_code)
    map_series = {}

    if response.status_code == 200:
        try:
            for heartbeat in heartbeats:
                metric_ = heartbeat[metric]
                if metric_ is not None:
                    if metric_ in map_series:
                        map_series[metric_].append(heartbeat)
                    else:
                        map_series[metric_] = []
                        map_series[metric_].append(heartbeat)
        except Exception as e:
            print(e)
    else:
        return response.text, response.status_code
    series = []
    for key in map_series:
        heartbeats = map_series[key]
        list = sorted(heartbeats, key=lambda x: datetime.fromisoformat(x['dateTime']).timestamp(), reverse=False)
        start_time = None
        end_time = None
        for heartbeat in list:
            start_time_atu = int(datetime.fromisoformat(heartbeat['dateTime']).timestamp() * 1000)
            end_time_atu = int(datetime.fromisoformat(heartbeat['dateTimeEnd']).timestamp() * 1000)
            if start_time is None:
                start_time = start_time_atu
            if end_time is None:
                end_time = end_time_atu

            diff = start_time_atu - end_time
            if diff > 100:
                arr = [int(start_time), int(end_time)]
                serie = {}
                serie['x'] = key
                serie['y'] = arr
                series.append(serie)
                start_time = start_time_atu
            end_time = end_time_atu
        arr = [int(start_time), int(end_time)]
        serie = {}
        serie['x'] = key
        serie['y'] = arr
        series.append(serie)
    return json.dumps(series), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
