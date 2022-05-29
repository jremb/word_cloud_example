from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import (
    QWidget,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLabel,
)


class SideMenu(QWidget):
    def __init__(self):
        super().__init__()
        # self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Options")
        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        self.label_word_cloud_section = QLabel("Word Cloud Options")
        # Remove links option:
        self.cb_remove_urls = QCheckBox("Remove urls")
        # Remove stop words option:
        self.cb_remove_stop_words = QCheckBox("Remove stop words")
        # Run preprocessing:
        self.btn_run_preprocessing = QPushButton("Apply preprocessing")
        # Query:
        self.label_api_section = QLabel("API Query")
        self.input_bearer_token = QLineEdit()
        self.input_bearer_token.setPlaceholderText("Your bearer token")
        self.combo_query_type = QComboBox()
        self.combo_query_type.addItems(["get_users_tweets"])
        self.combo_query_type.currentTextChanged.connect(self.adjust_query_opts)
        # User id:
        self.input_user_id = QLineEdit(self)
        self.input_user_id.setPlaceholderText("User ID")
        # Max results:
        self.combo_max_results = QComboBox()
        self.combo_max_results.addItems(
            ["10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "32000"]
        )
        # Run query:
        self.btn_run_query = QPushButton("Run query")
        # self.input_user_id.hide()

    def _init_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_word_cloud_section)
        self.layout.addWidget(self.cb_remove_urls)
        self.layout.addWidget(self.cb_remove_stop_words)
        self.layout.addWidget(self.btn_run_preprocessing)
        # API section:
        self.layout.addWidget(self.label_api_section)
        self.layout.addWidget(self.input_bearer_token)
        self.layout.addWidget(self.combo_query_type)
        self.layout.addWidget(self.input_user_id)
        self.layout.addWidget(self.combo_max_results)
        self.layout.addWidget(self.btn_run_query)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def adjust_query_opts(self):
        pass
        # if self.combo_query_type.currentText() == "get_users_tweets":
        #     self.input_user_id.show()
        # else:
        #     self.input_user_id.hide()
