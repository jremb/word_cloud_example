from typing import Union
import re
from collections import Counter

import spacy
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal


class Tokenize(QThread):
    """
    Class to pipe data through a list of preprocessors.
    """

    signal_error = pyqtSignal(str)
    signal_finished = pyqtSignal()
    signal_data = pyqtSignal(list)

    def __init__(self, data: str, opts: list):
        super().__init__()
        self.data = data
        self.opts = opts

    def run(self):
        """
        Creates a spacy doc from string of data. Creates bag of words with
        punctuation removed. Optionally removes urls removed and stop words.
        """
        try:
            # Remove urls:
            if "remove_urls" in self.opts:
                self.data = re.sub(r"(https:\S*[^'\. ])", "", self.data)
            # Create spacy doc:
            doc = self.create_spacy_doc()
            # Create bow, removing punctuation and stop words if specified:
            if "remove_stop_words" in self.opts:
                bow = [
                    token.text
                    for token in doc
                    if not token.is_punct and not token.is_stop
                ]
            else:
                # Create bow, removing punctuation:
                bow = [token.text for token in doc if not token.is_punct]
            # Send bow to main thread:
            self.signal_data.emit(bow)
            # Finish:
            self.signal_finished.emit()
        except Exception as e:
            self.signal_error.emit(
                f"Error: Missing 'en_core_web_lg' library.\nInstall with 'python -m spacy download en_core_web_lg'"
            )
            self.signal_finished.emit()

    def create_spacy_doc(self) -> spacy.tokens.Doc:
        """
        Creates a spacy doc from string of data.

        For this example, I used en_core_web_lg. You can also use
        en_core_web_md or en_core_web_sm. These would be installed
        in your environment with a command like:
            python -m spacy download en_core_web_sm
        then you can load it with:
            nlp = spacy.load("en_core_web_sm")
        """
        nlp = spacy.load("en_core_web_lg")
        return nlp(self.data)
