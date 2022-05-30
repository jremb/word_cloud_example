import os
import json

from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
import tweepy


class APIHandler(QThread):
    signal_data = pyqtSignal(list)
    signal_finished = pyqtSignal()

    def __init__(
        self, bearer_token: str, query_type: str, user_id: str, max_results: list
    ):
        super().__init__()
        self.bearer_token = bearer_token
        self.query_type = query_type
        self.user_id = user_id
        self.data = list()
        self.max_results = max_results
        if self.query_type == "get_users_tweets":
            self.get_users_tweets()

    def get_users_tweets(self) -> list:
        # NOTE - This is just a proof of concept.
        client = tweepy.Client(self.bearer_token, wait_on_rate_limit=True)
        for tweets in tweepy.Paginator(
            client.get_users_tweets, self.user_id, max_results=int(self.max_results)
        ):
            # tweets will be tweepy.client.Response object
            self.data.append(tweets)
            if len(self.data) >= 100:
                self.signal_data.emit(self.data)
                self.data = list()

    def run(self):
        if self.query_type == "get_users_tweets":
            self.get_users_tweets()
        if self.data:
            self.signal_data.emit(self.data)
        self.signal_finished.emit()
