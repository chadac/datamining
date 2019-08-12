#!/usr/bin/env python3

import os
import json
import miner
from pymongo import MongoClient
from pathlib import Path
from lib.log import logger
import traceback


CL_CATEGORY = os.environ.get('CL_CATEGORY', 'cto')
DATA_DIRECTORY = os.environ.get('DATA_DIRECTORY', './data')
MONGO_URL = os.environ.get('MONGO_URL', 'localhost')


def mine(db):
    cities = miner.fetch_cities()
    image_dir = Path(DATA_DIRECTORY)
    if not image_dir.exists():
        os.makedirs(image_dir)

    logger.info(f"Found {len(cities)} cities.")
    for city in cities:
        logger.info(f"Processing '{city}'.")
        s = 0
        while True:
            try:
                listings = miner.fetch_listings(city, CL_CATEGORY, s)
                if not listings:
                    break
            except Exception as e:
                logger.error("Could not retrieve listings for {city} on page {s}:\n"\
                             + traceback.format_exc())
                continue

            logger.info(f"Processing offset={s} with {len(listings)} listings.")
            for listing in listings:
                try:
                    ## for now, skip duplicates and focus on getting an original listing
                    ## duplicates are expensive
                    latest_listing = db.listings.find({'id': listing['id']}).sort([('updated', -1)]).limit(1)
                    if latest_listing.count() <= 0: #or listing['updated'] > latest_listing.next()['updated']:
                        miner.get_detailed_listing(listing)
                        miner.download_images(listing['images'], image_dir)
                        db.listings.insert_one(listing)
                except Exception as e:
                    logger.error("Could not retrieve details on listing {listing['id']}:\n"
                                 + traceback.format_exc())
            s += len(listings)


def main():
    client = MongoClient(MONGO_URL, username='root', password='root')
    ## TODO: Change this to something more configurable
    db = client.craigslist

    mine(db)


logger.info("Started up!")
if __name__ == '__main__':
    main()
