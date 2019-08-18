#!/usr/bin/env python3

import traceback

from lib.http import HTTP
from lib.log import logger


default_zipcode = 64030
num_records = 100 ## seems to be the max allowed
listing_url = 'https://www.autotrader.com/rest/searchresults/base?zip={zipcode}&searchRadius=0&sortBy=yearASC'


http = HTTP()


def retrieve(url, first_record=0, num_records=25):
    try:
        r = http.get(f'{url}&firstRecord={first_record}&numRecords={num_records}', headers={
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        })
        return r.json()
    except:
        print(r.content)
        logger.error(f"Could not retrieve results from {url}:\n {traceback.format_exc()}")
        return None


def mine_listings_from_url(url, r):
    first_record = 25
    ## TODO: Clean up control flow here.
    while True:
        if r is not None and 'listings' in r:
            # logger.debug(f"Retrieved {len(r['listings'])} listings")
            yield r['listings']

            r = retrieve(url, first_record, num_records=100)
            if first_record > r['totalResultCount']:
                break
            first_record += 100
        else:
            break


def _mine_listings(url, next_f=None):
    r =  retrieve(url)
    logger.info(f"total results: {r['totalResultCount']}")
    if not r:
        yield []
    elif next_f is not None and r['totalResultCount'] > 1100:
        yield from next_f(url, r)
    else:
        yield from mine_listings_from_url(url, r)


def mine_all_listings():
    logger.info("Mining all listings.")
    url = listing_url.format(zipcode=default_zipcode, num_records=num_records)
    yield from _mine_listings(url, mine_listings_by_make)


def mine_listings_by_make(url, r):
    makes = [x['value'] for x in r['filters']['makeCodeList']['options']]
    logger.info(f"Found {len(makes)} makes.")
    for make in makes:
        logger.info(f"Mining listings for make {make}.")
        yield from _mine_listings(f'{url}&makeCodeList={make}',
                                  mine_listings_by_model(make))


def mine_listings_by_model(make):
    def _f(url, r):
        models = [x['value'] for x in r['filterGroups']['modelCodeList'][make]['options']]
        logger.info(f"Found {len(models)} models for make {make}")
        for model in models:
            logger.info(f"Mining listings for make {make} and model {model}.")
            yield from _mine_listings(f'{url}&modelCodeList={model}',
                                      mine_listings_by_extcolor)
    return _f


def mine_listings_by_extcolor(url, r):
    colors = [x['value'] for x in r['filters']['extColorsSimple']['options']]
    for ext_color in colors:
        logger.info(f"Mining listings for exterior color {ext_color}.")
        yield from _mine_listings(f'{url}&extColorsSimple={ext_color}',
                                  mine_listings_by_intcolor)

def mine_listings_by_intcolor(url, r):
    colors = [x['value'] for x in r['filters']['interiorColorsSimple']['options']]
    for int_color in colors:
        logger.info(f"Mining listings for interior color {int_color}.")
        yield from _mine_listings(f'{url}&interiorColorsSimple={int_color}',
                                  mine_listings_by_year)

def mine_listings_by_year(url, r):
    years = [x['value'] for x in r['filters']['yearRange']['options']
             if x['label'] != 'Any']
    for year in years:
        logger.info(f"Mining listings for year {year} ")
        yield from _mine_listings(f'{url}&startYear={year}&endYear={year}')
