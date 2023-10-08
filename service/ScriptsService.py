import os
from datetime import datetime

import requests as requests

from service.Interceptor import Interceptor
from service.Utils import Utils

utils = Utils()
url_repository = os.environ['URL_REPOSITORY'] + '/'


class ScriptsService(Interceptor):
    def __init__(self):
        super().__init__()

    def get_script(self, script_name):
        script = utils.read_file("static/" + script_name + ".sql")
        return script

    def execute_script(self, script_name, headers=None, params=None):
        script = self.get_script(script_name)

        params_ = {}
        for param in params:
            params_[param] = params[param]

        if 'data_ini' not in params_:
            params_['data_ini'] = '2020-01-01'
        if 'data_end' not in params_:
            params_['data_fim'] = datetime.now().strftime("%Y-%m-%d")

        for key in params_:
            script = script.replace(":" + key, "'" + params_[key] + "'")

        body = {'command': script}
        response = requests.post(f"{url_repository}command/select", headers=headers, json=body)
        return response.json()
