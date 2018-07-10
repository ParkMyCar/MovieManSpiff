"""
Session object used to maintain an open session with PTP

Almost entirely based off of session by kannibalox from their PTPAPI project on GitHub

Author: Parker Timmerman
"""

import logging
import requests

from ptp_config import config
from time import time, sleep

LOGGER = logging.getLogger(__name__)

class TokenSession(requests.Session):
    """ Allow rate-limiting requests to a site """

    def __init__(self, capacity, fill_rate):
        """ tokens is the total number of tokens in the bucket
            fill_rate is the rate in tokens/second that the bucket will be refilled.
            A request can be made when there are enough tokens in the bucket for the request """

        requests.Session.__init__(self)
        self.capacity = float(capacity)
        self._tokens = float(capacity)                  # current tokens in bucket, start at capacity (full)
        self.consumed_tokens = 0
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def consume(self, tokens):
        """ Consume tokens from the bucket. Returns True if there were enough tokens, otherwise False. """

        self.update_tokens()
        if tokens < self._tokens:
            self._tokens -= tokens
            self.consumed_tokens += tokens
            LOGGER.debug("Consuming {0} token(s), total tokens consumed so far: {1}".format(tokens, self.consumed_tokens))
        else:
            return False
        return True

    def request(self, *args, **kwargs):
        while not self.consume(1):
            LOGGER.debug("Waiting for token bucket to refull...")
            sleep(1)
        return requests.Session.request(self, *args, **kwargs)

    def update_tokens(self):
        if self._tokens < self.capacity:
            now = time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens

    tokens = (update_tokens)

    def base_get(self, url_path, *args, **kwargs):
        return self.get(config.get('Main', 'baseURL') + url_path, *args, **kwargs)

    def base_post(self, url_path, *args, **kwargs):
        return self.post(config.get('Main', 'baseURL') + url_path, *args, **kwargs)

LOGGER.debug("Initializing token session")
session = TokenSession(3, 0.5)
session.headers.update({"User-Agent": "Wget/1.13.4"})
