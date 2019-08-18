#!/usr/bin/env python3

import os

import pymongo
from pymongo import MongoClient
import time
import traceback

from lib.log import logger

import miner


MONGO_URL = os.environ.get('MONGO_URL', 'localhost:27017')
MONGO_USER = os.environ.get('MONGO_USER', 'root')
MONGO_PASS = os.environ.get('MONGO_PASS', 'root')


def run(db):
    first_run = True
    for listings in miner.mine_all_listings():
        for listing in listings:
            if db.listings.count_documents({'id': listing['id']}, limit=1) > 0:
                continue
            db.listings.insert_one(listing)
            if 'images' in listing:
                media_items = [{
                    'listing_id': listing['id'],
                    'url': image['src'],
                    'path': None,
                    'mined': None
                } for image in listing['images']['sources']]
                db.media.insert_many(media_items)
            t3 = time.time()

        ## create index for faster access
        if first_run and 'id_index' not in db.listings.index_information():
            db.listings.create_index([('id', pymongo.HASHED)], name='id_index')
            first_run = False



def main():
    client = MongoClient(MONGO_URL, username=MONGO_USER, password=MONGO_PASS)
    db = client.autotrader

    try:
        run(db)
    except:
        logger.error(f"Could not complete mining: {traceback.format_exc()}")


if __name__ == '__main__':
    main()
