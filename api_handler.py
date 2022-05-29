import os
import json

from PyQt6.QtCore import QThread
import tweepy


class APIHandler(QThread):
    def __init__(self, bearer_token: str, query_type: str, user_id: str, max_results: list):
        super().__init__()
        self.bearer_token = bearer_token
        self.query_type = query_type
        self.user_id = user_id
        self.data = dict()
        self.max_results = max_results
        if self.query_type == "get_users_tweets":
            self.get_users_tweets()

    def get_users_tweets(self) -> list:
        # NOTE - This is just a proof of concept.
        client = tweepy.Client(self.bearer_token, wait_on_rate_limit=True)
        for tweet in tweepy.Paginator(client.get_users_tweets, self.user_id, max_results=self.max_results):
            for text in tweet.data:
                print(text)

   
