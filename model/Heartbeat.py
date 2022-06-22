class Heartbeat:
    def __init__(self):
        self.entity = 0
        self.process = 1
        self.application_name = 2
        self.entity_type = 3
        self.timestamp = 4
        self.project = 5
        self.write = 6
        self.language = 7
        self.category = 8
        self.ide_name = 9
        self.ide_version = 10
        self.host_name = 11
        self.os_name = 12
        self.time_spent_millis = 13
        self.time_spent_millis_no_conflict = 14
        self.date_time = 15
        self.date_time_end = 16
        self.domain = 17

    def get_cols_select(self):
        return "entity, process, application_name, entity_type, \"timestamp\", project, \"write\", " \
                "\"language\", \"category\", ide_name, ide_version, host_name, os_name, time_spent_millis, " \
                "time_spent_millis_no_conflict, date_time, date_time_end, \"domain\" "
