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
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)

from sidebar import SideMenu
import preprocessors
import api_handler


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
        self.data_preview_tracker = list()
        self.bow = Counter()
        self.token_opts = list()
        self.query_opts = list()
        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        # Filepath input:
        self.filepath_input = QLineEdit(self)
        self.filepath_input.setPlaceholderText("Path to file")
        self.btn_load_file = QPushButton("Load file")
        self.btn_load_file.clicked.connect(self.load_file)
        self.btn_clear_loaded_data = QPushButton("Clear loaded data")
        self.btn_clear_loaded_data.clicked.connect(self.clear_loaded_data)
        # Info view:
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        # Generate word cloud:
        self.btn_word_cloud = QPushButton("Generate word cloud")
        self.btn_word_cloud.clicked.connect(self.generate_word_cloud)
        # Sidebar:
        self.sb = SideMenu()
        self.sb.cb_remove_urls.stateChanged.connect(self.remove_urls)
        self.sb.cb_remove_stop_words.stateChanged.connect(self.remove_stop_words)
        self.sb.btn_run_preprocessing.clicked.connect(self.start_worker)
        self.sb.btn_run_query.clicked.connect(self.run_query)
        # Word cloud:
        self.figure = Figure()

    def _init_layout(self):
        self.sub_vbox = QVBoxLayout()
        self.sub_vbox.addWidget(self.filepath_input)
        self.sub_hbox = QHBoxLayout()
        self.sub_hbox.addWidget(self.btn_load_file)
        self.sub_hbox.addWidget(self.btn_clear_loaded_data)
        self.sub_vbox.addLayout(self.sub_hbox)
        self.sub_vbox.addWidget(self.info_view)
        self.sub_vbox.addWidget(self.btn_word_cloud)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.sb)
        self.hbox.addLayout(self.sub_vbox)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

    def load_file(self):
        """
        Attempts to load the file assuming it is JSON. If successfull, it attempts to find the tweet text field and concatenates each text into a single str while case-folding, removing newline chars, and expanding contractions. A sample of the data is extracted for the info view. If the file is not JSON, it hands off to self.load_newline_delimited_file.
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
                f"Error: file is not JSON\nWill try to load as text file and assume\ntweets are delimited by newlines ..."
            )
            self.load_newline_delimited_file()

    def load_newline_delimited_file(self):
        """
        Attempts to load the file assuming it is a plain text file and that each line of data is a tweet text. If successfull, it stores each line (tweet's text) in a list, creates a single string representation of the data, and creates a sample of the data for the info view.
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

    def clear_loaded_data(self):
        self.loaded_data = ""
        self.data_preview_tracker = []
        self.bow = []
        self.info_view.setText("")
        self.signal_update_status_bar.emit("Data cleared")

    def update_info_view(self):
        """
        Updates the info view
        """
        data = self.data_preview_tracker[-1]
        self.info_view.setText(
            f"Loaded {self.filepath_input.text()}\n\nSample of data:\n{data}"
        )

    def start_worker(self):
        """
        Starts a worker thread to run the preprocessing functions on the entire data set.
        """
        self.worker_token = preprocessors.Tokenize(self.loaded_data, self.token_opts)
        self.worker_token.signal_data.connect(self.attach_processed_data)
        self.worker_token.signal_finished.connect(self.worker_token.deleteLater)
        self.worker_token.start()

    def attach_processed_data(self, bow):
        """
        Attaches bow from worker to self.bow.
        """
        self.bow = Counter(bow)
        self.signal_update_status_bar.emit(f"Vocabulary: {len(self.bow):,}")
        # Can't use escape char in f-string:
        msg = [str(tup) for tup in self.bow.most_common(20)]
        self.info_view.setText(f"10 most common words:\n{msg}")

    def remove_urls(self):
        """
        Adds or removes remove_urls option.
        """
        if self.sb.cb_remove_urls.isChecked():
            self.token_opts.append("remove_urls")
        else:
            self.token_opts.remove("remove_urls")

    def remove_stop_words(self):
        """
        Adds or removes remove_stop_words option.
        """
        if self.sb.cb_remove_stop_words.isChecked():
            self.token_opts.append("remove_stop_words")
        else:
            self.token_opts.remove("remove_stop_words")

    def generate_word_cloud(self):
        if self.bow:
            self.word_cloud = WordCloud(
                background_color="white",
                max_words=100,
                width=800,
                height=600,
                random_state=1,
            ).generate_from_frequencies(self.bow)
            plt.axis("off")
            plt.imshow(self.word_cloud)
            self.figure = Figure(plt.show())

    def run_query(self):
        """
        Runs the query.
        """
        query_type = self.sb.combo_query_type.currentText()
        user_id = self.sb.input_user_id.text()
        max_results = self.sb.combo_max_results.currentText()
        bearer_token = self.sb.input_bearer_token.text()
        self.worker_query = api_handler.APIHandler(bearer_token, query_type, user_id, max_results)
        self.worker_query.signal_finished.connect(self.worker_token.deleteLater)
        self.worker_query.start()

    def error_popup(self, msg: str):
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
