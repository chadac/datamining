#!/usr/bin/env python3

import os, pkgutil, importlib
from pymongo import MongoClient
from threading import Thread
import time


modules = ['miners.' + name
           for _, name, _ in pkgutil.iter_modules(['miners'])]


def run_miner(module):
    client = MongoClient('db', username='root', password='root')
    while True:
        module.mine()
        time.sleep(module.UPDATE_INTERVAL)


threads = []
for module_name in modules:
    module = importlib.import_module(module_name)
    thread = Thread(name=module.NAME, target=run_miner, args=(module,))
    thread.start()
    threads += [thread]
    print("Started [{}]".format(module.NAME))

for thread in threads:
    thread.join()
