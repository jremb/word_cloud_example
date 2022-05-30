import sys
import json
from collections import Counter

import contractions
import matplotlib.pyplot as plt

# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# TODO: Check matplotlib documentation about direct import of plt:
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStatusBar,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QTabWidget,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)

from sidebar_wc import WordcloudSideMenu
from sidebar_api import APISideMenu
import preprocessors
import api_handler
import db_handler
import pg_sql as sql


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tweeasy")
        self.setGeometry(300, 300, 833, 434)
        self.init_ui()

    def init_ui(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.main_gui = MainGui()
        self.main_gui.signal_update_status_bar.connect(self.update_status)
        self.setCentralWidget(self.main_gui)

    def update_status(self, status):
        self.status_bar.showMessage(status)


class MainGui(QWidget):
    signal_update_status_bar = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 831, 402)
        self.loaded_data: str = ""
        self.wc_type = "text of tweets"
        self.data_preview_tracker = list()
        self.bow = Counter()
        self.token_opts = list()
        self.query_opts = list()
        self._init_widgets()
        self._init_layout()

    def _init_widgets(self) -> None:
        # Tab widget:
        self.tab_widget = QTabWidget(self)
        self.twitter_tab = QWidget()
        self.wordcloud_tab = QWidget()
        self.tab_widget.addTab(self.twitter_tab, "Query Twitter")
        self.tab_widget.addTab(self.wordcloud_tab, "Word Cloud")

        # Twitter tab
        # API info view:
        self.info_view_api = QTextEdit()
        self.info_view_api.setReadOnly(True)
        # API Sidebar:
        self.sb_api = APISideMenu()
        self.sb_api.btn_run_query.clicked.connect(self.start_worker_api)

        # Word cloud tab
        # Filepath input:
        self.filepath_input = QLineEdit()
        self.filepath_input.setPlaceholderText("Path to file")
        # Database groupbox:
        self.gb_db = QGroupBox("Database Credentials")
        self.gb_db.hide()
        # Database credentials:
        self.inp_db_name = QLineEdit()
        self.inp_db_name.setPlaceholderText("Database name")
        self.inp_db_user = QLineEdit()
        self.inp_db_user.setPlaceholderText("User")
        self.inp_db_pass = QLineEdit()
        self.inp_db_pass.setPlaceholderText("Password")
        self.inp_db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_db_host = QLineEdit()
        self.inp_db_host.setPlaceholderText("Host")
        self.inp_db_port = QLineEdit()
        self.inp_db_port.setPlaceholderText("Port")
        self.btn_test_db_conn = QPushButton("Test Connection")
        self.btn_test_db_conn.clicked.connect(self.test_db_conn)
        # Load / Clear buttons:
        self.btn_load_file = QPushButton("Load file")
        self.btn_load_file.clicked.connect(self.load_file)
        self.btn_clear_loaded_data = QPushButton("Clear loaded data")
        self.btn_clear_loaded_data.clicked.connect(self.clear_loaded_data)
        # WC info view:
        self.info_view_wc = QTextEdit()
        self.info_view_wc.setReadOnly(True)
        # Generate word cloud button:
        self.btn_word_cloud = QPushButton("Generate word cloud")
        self.btn_word_cloud.clicked.connect(self.generate_word_cloud)
        # Word Cloud Sidebar:
        self.sb_wc = WordcloudSideMenu()
        self.sb_wc.signal_toggle_load.connect(self.toggle_data_loading)
        self.sb_wc.signal_wc_type.connect(self.set_wc_type)
        self.sb_wc.cb_remove_urls.stateChanged.connect(self.remove_urls)
        self.sb_wc.cb_remove_stop_words.stateChanged.connect(self.remove_stop_words)
        self.sb_wc.btn_run_preprocessing.clicked.connect(self.start_worker_token)
        self.figure = Figure()

    def _init_layout(self) -> None:
        # Word cloud tab, right side:
        wc_sub_vbox = QVBoxLayout()
        # Load from file:
        wc_sub_vbox.addWidget(self.filepath_input)
        # Load from db:
        db_grid_box = QGridLayout()
        db_grid_box.addWidget(self.inp_db_name, 0, 0)
        db_grid_box.addWidget(self.inp_db_user, 0, 1)
        db_grid_box.addWidget(self.inp_db_pass, 1, 0)
        db_grid_box.addWidget(self.inp_db_host, 1, 1)
        db_grid_box.addWidget(self.inp_db_port, 2, 0)
        db_grid_box.addWidget(self.btn_test_db_conn, 2, 1)
        self.gb_db.setLayout(db_grid_box)
        wc_sub_vbox.addWidget(self.gb_db)
        # Load from file:
        wc_sub_hbox = QHBoxLayout()
        wc_sub_hbox.addWidget(self.btn_load_file)
        wc_sub_hbox.addWidget(self.btn_clear_loaded_data)
        wc_sub_vbox.addLayout(wc_sub_hbox)
        wc_sub_vbox.addWidget(self.info_view_wc)
        wc_sub_vbox.addWidget(self.btn_word_cloud)
        # Add word cloud sidebar, left side:
        wc_hbox = QHBoxLayout()
        wc_hbox.addWidget(self.sb_wc)
        # Add word cloud widgets, right side:
        wc_hbox.addLayout(wc_sub_vbox)
        # Add layout to word cloud tab:
        self.wordcloud_tab.setLayout(wc_hbox)
        # API Query tab, right side:
        api_sub_vbox = QVBoxLayout()
        api_sub_vbox.addWidget(self.info_view_api)
        # Add API sidebar, left side:
        api_hbox = QHBoxLayout()
        api_hbox.addWidget(self.sb_api)
        # Add API widgets, right side:
        api_hbox.addLayout(api_sub_vbox)
        # Add layout to API tab:
        self.twitter_tab.setLayout(api_hbox)
        # Add tab_widget to main layout:
        main_vbox = QVBoxLayout()
        main_vbox.addWidget(self.tab_widget)
        # Attach main layout to main widget:
        self.setLayout(main_vbox)

    def _format_credentials(self) -> dict:
        """
        Formats the credentials to a dict.
        Returns
            dict: The credentials.
        """
        return {
            "dbname": self.inp_db_name.text(),
            "user": self.inp_db_user.text(),
            "password": self.inp_db_pass.text(),
            "host": self.inp_db_host.text(),
            "port": self.inp_db_port.text(),
        }

    def toggle_data_loading(self, state) -> None:
        if state:
            self.filepath_input.show()
            self.btn_load_file.show()
            self.gb_db.hide()
        else:
            self.filepath_input.hide()
            self.btn_load_file.hide()
            self.gb_db.show()

    def set_wc_type(self, wc_type) -> None:
        self.wc_type = wc_type

    def load_file(self) -> None:
        """
        Attempts to load the file assuming it is JSON. If successfull, it attempts
        to find the tweet text field and concatenates each text into a single str
        while case-folding, removing newline chars, and expanding contractions.
        A sample of the data is extracted for the info view. If the file is not JSON,
        it hands off to self.load_newline_delimited_file.
        """
        try:
            with open(self.filepath_input.text(), "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
            self.loaded_data = ". ".join(
                [
                    contractions.fix(field["text"].lower())
                    for field in self.json_data["data"]
                    if "\n" not in field["text"]
                ]
            )
            self.data_preview_tracker.append(self.loaded_data[:500])
            self.update_info_view()
            self.signal_update_status_bar.emit(
                f"{len(self.loaded_data):,} tweets loaded"
            )
        except TypeError as e:
            self.error_popup(f"Error: {e}")
        except FileNotFoundError as e:
            self.error_popup(f"Error: {e}")
        except json.decoder.JSONDecodeError as e:
            self.error_popup(
                f"Error: file is not JSON\nWill try to load as text file and assume\n\
                    tweets are delimited by newlines ..."
            )
            self.load_newline_delimited_file()

    def load_newline_delimited_file(self) -> None:
        """
        Attempts to load the file assuming it is a plain text file and that each
        line of data is a tweet text. If successfull, it stores each line (tweet's
        text) in a list, creates a single string representation of the data, and
        creates a sample of the data for the info view.
        """
        try:
            with open(self.filepath_input.text(), "r", encoding="utf-8") as f:
                tweets = f.readlines()
            # TODO: Haven't tested following line yet:
            self.loaded_data = " ".join(
                [
                    contractions.fix(word.lower())
                    for word in [line.strip("\n") for line in tweets]
                ]
            ).strip()
            self.data_preview_tracker.append(self.loaded_data[:10])
            self.update_info_view()
            self.signal_update_status_bar.emit(
                f"{len(self.loaded_data):,} tweets loaded"
            )
        except Exception as e:
            self.error_popup(f"Error: {e}")

    def test_db_conn(self) -> None:
        """
        Attempts to connect to the database using the provided credentials.
        If successful, it will display a success message in the info view.
        """
        try:
            params = self._format_credentials()
            query = sql.list_tables()
            self.db_worker = db_handler.DbHandler("test", params, query, [])
            self.db_worker.signal_data.connect(self.db_response_handler)
            self.db_worker.signal_error.connect(self.error_popup)
            self.db_worker.signal_finished.connect(self.db_worker.deleteLater)
            self.db_worker.start()
        except Exception as e:
            self.error_popup(f"Error: {e}")

    def db_response_handler(self, _sender, response) -> None:
        """
        Handles the response from the database worker. If successful, it will
        display a success message in the info view.
        """
        if _sender == "test":
            self.info_view_wc.append(
                f"Successfully connected to database.\nFound {len(response)} tables:"
            )
            # parse table names from response:
            for table in response:
                self.info_view_wc.append("  " + table[0])

    def clear_loaded_data(self) -> None:
        self.loaded_data = ""
        self.data_preview_tracker = []
        self.bow = []
        self.info_view_wc.setText("")
        self.signal_update_status_bar.emit("Data cleared")

    def update_info_view(self) -> None:
        """
        Updates the info view
        """
        data = self.data_preview_tracker[-1]
        self.info_view_wc.setText(
            f"Loaded {self.filepath_input.text()}\n\nSample of data:\n{data}"
        )

    def start_worker_token(self) -> None:
        """
        Starts a worker thread to run the preprocessing functions on the entire data set.
        """
        self.worker_token = preprocessors.Tokenize(self.loaded_data, self.token_opts)
        self.worker_token.signal_data.connect(self.attach_processed_data)
        self.worker_token.signal_finished.connect(self.worker_token.deleteLater)
        self.worker_token.signal_error.connect(self.error_popup)
        self.worker_token.start()

    def attach_processed_data(self, bow) -> None:
        """
        Attaches bow from worker to self.bow.
        """
        self.bow = Counter(bow)
        self.signal_update_status_bar.emit(f"Vocabulary: {len(self.bow):,}")
        # Can't use escape char in f-string:
        msg = [str(tup) for tup in self.bow.most_common(20)]
        self.info_view_wc.setText(f"10 most common words:\n{msg}")

    def remove_urls(self) -> None:
        """
        Adds or removes remove_urls option.
        """
        if self.sb_wc.cb_remove_urls.isChecked():
            self.token_opts.append("remove_urls")
        else:
            self.token_opts.remove("remove_urls")

    def remove_stop_words(self) -> None:
        """
        Adds or removes remove_stop_words option.
        """
        if self.sb_wc.cb_remove_stop_words.isChecked():
            self.token_opts.append("remove_stop_words")
        else:
            self.token_opts.remove("remove_stop_words")

    def generate_word_cloud(self) -> None:
        data = None
        if self.bow and self.wc_type == "text of tweets":
            data = self.bow
        elif self.wc_type == "QTs per user":
            data = self.get_users_qt_count()
        if data:
            self.word_cloud = WordCloud(
                background_color="white",
                max_words=100,
                width=800,
                height=600,
                random_state=1,
            ).generate_from_frequencies(data)
            plt.axis("off")
            plt.imshow(self.word_cloud)
            self.figure = Figure(plt.show())

    def get_users_qt_count(self) -> dict:
        if self.json_data:
            users_qts_dict = dict()
            try:  # Might not have the fields/expansions:
                for idx, obj in enumerate(self.json_data["data"]):
                    users_qts_dict.setdefault(obj["author_id"], 0)
                    users_qts_dict[obj["author_id"]] += int(self.json_data["data"][idx]["public_metrics"]["quote_count"])
                for idx, obj in enumerate(self.json_data["includes"]["tweets"]):
                    users_qts_dict.setdefault(obj["author_id"], 0)
                    users_qts_dict[obj["author_id"]] += int(self.json_data["includes"]["tweets"][idx]["public_metrics"]["quote_count"])
            except KeyError as e:
                self.error_popup(f"Error: {e}")
            finally:
                return users_qts_dict

    def start_worker_api(self) -> None:
        """
        Runs the query.
        """
        query_type = self.sb_api.combo_query_type.currentText()
        user_id = self.sb_api.input_user_id.text()
        max_results = self.sb_api.combo_max_results.currentText()
        bearer_token = self.sb_api.input_bearer_token.text()
        self.worker_query = api_handler.APIHandler(
            bearer_token, query_type, user_id, max_results
        )
        self.worker_query.signal_data.connect(self.handle_api_data)
        self.worker_query.signal_finished.connect(self.worker_query.deleteLater)
        self.worker_query.start()

    def handle_api_data(self, data) -> None:
        """
        Handles the data from the API worker.
        """
        # TODO: Parse response data and format it for easier display. 
        # Add option to write data to database or save to file. Add
        # ability to create word cloud directly from data.
        self.info_view_api.append(f"{data}")

    def error_popup(self, msg: str) -> None:
        pop = QMessageBox()
        pop.setIcon(QMessageBox.Icon.Critical)
        pop.setWindowTitle("Error")
        pop.setText(msg)
        pop.setStandardButtons(QMessageBox.StandardButton.Ok)
        pop.setDefaultButton(QMessageBox.StandardButton.Ok)
        pop.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
