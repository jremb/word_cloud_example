from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QGroupBox,
    QLabel,
)


class APISideMenu(QWidget):
    def __init__(self):
        super().__init__()
        # self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Options")
        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        # Query Opts GB:
        self.gb_query_opts = QGroupBox("Query Options")
        # Credentials:
        self.input_bearer_token = QLineEdit()
        self.input_bearer_token.setPlaceholderText("Your bearer token")
        self.input_bearer_token.setEchoMode(QLineEdit.EchoMode.Password)
        # Query type:
        self.combo_query_type = QComboBox()
        self.combo_query_type.addItems(["get_users_tweets"])
        self.combo_query_type.currentTextChanged.connect(self.adjust_query_opts)
        # User id:
        self.input_user_id = QLineEdit(self)
        self.input_user_id.setPlaceholderText("User ID")
        # Max results:
        self.label_max_results = QLabel("Max results:")
        self.combo_max_results = QComboBox()
        self.combo_max_results.addItems(
            [
                "10",
                "20",
                "30",
                "40",
                "50",
                "100",
                "200",
                "300",
                "400",
                "500",
                "1000",
                "2000",
                "32000",
            ]
        )
        # Run query:
        self.btn_run_query = QPushButton("Run query")
        # self.input_user_id.hide()

    def _init_layout(self):
        # General layout:
        self.layout = QVBoxLayout()
        # Word Cloud GB:
        self.vbox_gb_query_opts = QVBoxLayout()
        # Credentials:
        self.vbox_gb_query_opts.addWidget(self.input_bearer_token)
        # Query type:
        self.vbox_gb_query_opts.addWidget(self.combo_query_type)
        # User id:
        self.vbox_gb_query_opts.addWidget(self.input_user_id)
        # Max results:
        self.vbox_gb_query_opts.addWidget(self.label_max_results)
        self.vbox_gb_query_opts.addWidget(self.combo_max_results)
        # Run query:
        self.vbox_gb_query_opts.addWidget(self.btn_run_query)
        # Add to GB:
        self.gb_query_opts.setLayout(self.vbox_gb_query_opts)
        self.layout.addWidget(self.gb_query_opts)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def adjust_query_opts(self):
        pass
        # if self.combo_query_type.currentText() == "get_users_tweets":
        #     self.input_user_id.show()
        # else:
        #     self.input_user_id.hide()
