#!/usr/bin/env python3

import os
import json
import miner
from pymongo import MongoClient
from pathlib import Path
from lib.log import logger
import traceback
import time


CL_CATEGORY = os.environ.get('CL_CATEGORY', 'cto')
MONGO_URL = os.environ.get('MONGO_URL', 'localhost')


def mine(db):
    cities = miner.fetch_cities()

    logger.info(f"Found {len(cities)} cities.")
    for city in sorted(cities):
        logger.info(f"[{city}] Loading new listings.")
        s = 0
        page = 1
        listings = []
        t1 = time.time()
        while True:
            try:
                new_listings = miner.fetch_listings(city, CL_CATEGORY, s)
                listings += new_listings
                if not new_listings:
                    break
                s += len(new_listings)
                page += 1
            except Exception as e:
                logger.error(f"[{city}] Could not retrieve listings on page {page}:\n"\
                             + traceback.format_exc())
                continue
        t2 = time.time()

        logger.info(f"[{city}] Processed {page-1} pages and {len(listings)} listings in {t2-t1:.2f}s.")
        ## filter out those that have already been visited
        listings = [listing for listing in listings if
                    db.listings.count_documents({'id': listing['id']}, limit=1) <= 0]

        t3 = time.time()
        logger.info(f"[{city}] Found {len(listings)} new listings in {t3-t2:.2f}s.")
        for listing in listings:
            try:
                miner.get_detailed_listing(listing)
                if len(listing['images']) > 0:
                    db.images.insert_many(listing['images'])
                db.listings.insert_one(listing)
            except Exception as e:
                logger.error(f"Could not retrieve details from {listing['url']}:\n"
                             + traceback.format_exc())
        t4 = time.time()
        logger.info(f"[{city}] Downloaded detailed listings in {t4-t3:.2f}s")


def main():
    client = MongoClient(MONGO_URL, username='root', password='root')
    ## TODO: Change this to something more configurable
    db = client.craigslist

    try:
        mine(db)
    except:
        logger.error("Ran into exception during mining:\n" +\
                     traceback.format_exc())


logger.info("Started up!")
if __name__ == '__main__':
    main()
