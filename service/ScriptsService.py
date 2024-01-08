from datetime import datetime

from csctracker_py_core.repository.remote_repository import RemoteRepository

from service.Utils import Utils

utils = Utils()


class ScriptsService:
    def __init__(self, remote_repository: RemoteRepository):
        self.remote_repository = remote_repository

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
        if 'data_fim' not in params_:
            params_['data_fim'] = datetime.now().strftime("%Y-%m-%d") + " 23:59:59"

        for key in params_:
            script = script.replace(":" + key, "'" + params_[key] + "'")

        return self.remote_repository.execute_select(script, headers)
