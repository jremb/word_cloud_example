from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import (
    QWidget,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QGroupBox,
    QRadioButton,
)


class WordcloudSideMenu(QWidget):
    # Custom signals:
    signal_toggle_load = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        # self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Options")
        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        # Data Source Options:
        self.load_from_file = QRadioButton("Load from file")
        self.load_from_file.setChecked(True)
        self.load_from_file.toggled.connect(self.toggle_load_source)
        # With only two options, we don't need to connect a signal/slot for
        # the below radio button. The above signal/slot can handle the logic for
        # both options:
        self.load_from_db = QRadioButton("Load from database")
        # Word Cloud GB:
        self.gb_word_cloud = QGroupBox("Tokenizer Options")
        # Remove links option:
        self.cb_remove_urls = QCheckBox("Remove urls")
        # Remove stop words option:
        self.cb_remove_stop_words = QCheckBox("Remove stop words")
        # Run preprocessing:
        self.btn_run_preprocessing = QPushButton("Tokenize")

    def _init_layout(self):
        # General layout:
        self.layout = QVBoxLayout()
        # Main layout:
        main_vbox = QVBoxLayout()
        # Data Source Options:
        main_vbox.addWidget(self.load_from_file)
        main_vbox.addWidget(self.load_from_db)
        # Word Cloud GB:
        vbox_gb_preprocessing = QVBoxLayout()
        vbox_gb_preprocessing.addWidget(self.cb_remove_urls)
        vbox_gb_preprocessing.addWidget(self.cb_remove_stop_words)
        vbox_gb_preprocessing.addWidget(self.btn_run_preprocessing)
        vbox_gb_preprocessing.addStretch()
        self.gb_word_cloud.setLayout(vbox_gb_preprocessing)
        # Add word cloud gb to main layout:
        main_vbox.addWidget(self.gb_word_cloud)
        # Add main layout to self:
        self.setLayout(main_vbox)
        self.layout.addStretch()

    def toggle_load_source(self, state):
        if self.sender().text() == "Load from file" and state:
            self.signal_toggle_load.emit(True)
        else:
            self.signal_toggle_load.emit(False)
