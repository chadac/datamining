#!/usr/bin/env python

import time
import threading
import requests

class HTTP:
    def __init__(self, wait_time=2):
        self._next_request = time.time()
        self._lock = threading.Lock()
        self.wait_time = wait_time


    def _start_request(self):
        self._lock.acquire()
        ct = time.time()
        if ct < self._next_request:
            time.sleep(self._next_request - ct)

    def _end_request(self):
        self.next_request = time.time() + self.wait_time
        self._lock.release()

    def get(self, url, *args, **kwargs):
        self._start_request()
        err = None
        try:
            r = requests.get(url, *args, **kwargs)
        except Exception as e:
            err = e
        self._end_request()
        if err:
            raise err
        return r

    def post(self, url, *args, **kwargs):
        self._start_request()
        err = None
        try:
            r = requests.post(url, *args, **kwargs)
        except Exception as e:
            err = e
        if err:
            raise err
        self._end_request()
        return r
