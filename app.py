from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)


@app.route('/dataset', methods=['GET'])
def dataset():
    metric = request.args.get('metric')
    value = request.args.get('value')
    period = request.args.get('period')
    if value is None:
        value = "timeSpentMillis"
    print("request.args", metric, value, period, request.args)
    response = requests.get('http://backend:8080/heartbeats?metric=' + metric + '&period=' + period,
                            headers=request.headers)
    print("ResponseCode: {}".format(response.status_code))
    heartbeats = response.json()
    data_set = {}
    if response.status_code == 200:
        print("In", 200)
        try:
            for heartbeat in heartbeats:
                print("For")
                metric_ = heartbeat[metric]
                value_ = heartbeat[value]
                print("metric_", metric_, "value_", value_)
                if metric_ is not None:
                    if metric_ in data_set:
                        data_set[metric_] += value_
                    else:
                        data_set[metric_] = value_
                return data_set
        except Exception as e:
            print("Error: ", e)
            return response.text, response.status_code
    else:
        print(response.status_code, "else")
        return response.text, response.status_code
    return data_set


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
    return str(series), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
