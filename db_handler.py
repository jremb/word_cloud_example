import psycopg
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal


class DbHandler(QThread):
    signal_data = pyqtSignal(str, list)
    signal_error = pyqtSignal(str)
    signal_finished = pyqtSignal()

    def __init__(self, q_type: str, params: dict, query: str, query_params: list):
        super().__init__()
        self.params = params
        self.query = query
        self.db_query_params = query_params
        self.type = q_type

    def run(self):
        try:
            with psycopg.connect(**self.params) as conn:
                with conn.cursor() as cur:
                    if self.db_query_params:
                        cur.execute(self.query, self.db_query_params)
                    else:
                        cur.execute(self.query)
                    self.data = cur.fetchall()
            self.signal_data.emit(self.type, self.data)
            self.signal_finished.emit()
        except Exception as e:
            self.signal_error.emit(str(e))
