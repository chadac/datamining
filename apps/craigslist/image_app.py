#!/usr/bin/env python3

import os
import json
import miner
from pymongo import MongoClient
from pathlib import Path
from lib.log import logger
import traceback
import time


DATA_DIRECTORY = os.environ.get('DATA_DIRECTORY', './data')
MONGO_URL = os.environ.get('MONGO_URL', 'localhost')


def mine(db):
    image_dir = Path(DATA_DIRECTORY)
    images = db.images.find({'path': {'$exists': False}})
    logger.info(f"Processing {images.count()} images.")
    for image in images:
        miner.download_image(image, image_dir)
        db.images.update_one({'_id': image['_id']},
                             {'$set': {'path': image['path']}})


def main():
    client = MongoClient(MONGO_URL, username='root', password='root')
    ## TODO: Change this to something more configurable
    db = client.craigslist

    try:
        mine(db)
    except:
        logger.error("Ran into exception during mining:\n" +\
                      traceback.format_exc())


if __name__ == '__main__':
    main()
