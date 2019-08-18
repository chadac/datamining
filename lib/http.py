#!/usr/bin/env python

import time
import threading
import requests

class HTTP:
    """Thread-safe HTTP calls with delays inbetween. This is more of a
    courtesy to services that we mine from, since a massive number of
    requests in a moment are usually seen as not good practice.

    It is meant to serve as a general-purpose tool for data mining
    that includes common features needed with such requests.

    :param wait_time: The time (in seconds) to wait between HTTP requests
    :type wait_time: int, float
    :param retries: The number of attempts to make if a connection fails
    :type retries: int
    """
    def __init__(self, wait_time=2, retries=5):
        self._next_request = time.time()
        self._lock = threading.Lock()
        self.wait_time = wait_time
        self.retries = retries


    def _start_request(self):
        self._lock.acquire()
        ct = time.time()
        if ct < self._next_request:
            time.sleep(self._next_request - ct)

    def _end_request(self):
        self.next_request = time.time() + self.wait_time
        self._lock.release()

    def get(self, url, *args, **kwargs):
        self._lock.acquire()
        r = None
        err = None
        for _ in range(self.retries):
            t = time.time()
            if t < self._next_request:
                time.sleep(self._next_request - t)
            try:
                r = requests.get(url, *args, **kwargs)
            except Exception as e:
                err = e

            self._next_request = time.time() + self.wait_time
            if r:
                break
        self._lock.release()
        if r:
            return r
        else:
            raise Exception(f"Could not retrieve URL: {err}")

    # def post(self, url, *args, **kwargs):
    #     self._start_request()
    #     err = None
    #     try:
    #         r = requests.post(url, *args, **kwargs)
    #     except Exception as e:
    #         err = e
    #     if err:
    #         raise err
    #     self._end_request()
    #     return r
