#!/usr/bin/env python3

from bs4 import BeautifulSoup
import re, json
import os
import logging, sys
import traceback
# import boto3
import hashlib
from lib.http import HTTP

logger = logging.getLogger('bringatrailer')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('output.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
oh = logging.StreamHandler(sys.stdout)
oh.setLevel(logging.DEBUG)
oh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(oh)

admin_url = 'https://bringatrailer.com/wp-admin/admin-ajax.php'
img_path = './data'


def gen_key(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def mine_listings(page):
    data = {
        'action': 'bat_auctions_results',
        'exclude': '',
        'maxPages': 500,
        'process': 'more',
        'queryPaged': page,
        'search': '',
        'sort': 'timestamp',
        'timeFrame': 'all',
        'watch': 0,
        'yearFrom': '',
        'yearTo': ''
    }
    r = requests.post(admin_url, data=data)
    r = json.loads(r.text)
    d = re.findall(r'"(https://bringatrailer.com/listing/[^/]+/)"',
                   r['auctions_results'])
    return list(set(d)), int(r['max_pages'])


def mine_listing(url):
    slug = re.match(r'https://bringatrailer\.com/listing/([^/]+)/?', url).group(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    info = soup.findAll('td', {'class': 'listing-stats-value'})
    img_urls = [link.get('href') for link in soup.findAll('a', {'class': 'listing-gallery-image-container'})]
    images = []

    if not os.path.exists('{img_path}/{slug}'):
        os.makedirs('{img_path}/{slug}')

    for i, img_url in enumerate(img_urls):
        img_key = gen_key(url + img_url)
        ext = re.search(r'\.([^.^/]+)$', img_url).group(1)
        path = f'{img_path}/{slug}/{i:03d}.{ext}'
        r1 = requests.get(img_url)
        with open(f'./data/{img_key}.{ext}', 'w') as f:
            f.write(r1.content)
        # try:
        #     bucket.Object(path).load()
        # except botocore.exceptions.ClientError:
        #     bucket.Object(path).put(Body=r1.content)
        images += [{
            'url': img_url,
            'path': path
        }]

    result = {
        'slug': slug,
        'url': url,
        'name': soup.find('h1', {'class': 'post-title'}).getText(),
        'price': info[0].getText().strip(),
        'date': info[1].getText().strip(),
        'num_bids': int(info[2].getText().strip()),
        'description': soup.find('div', {'class':'post-excerpt'}).getText().strip(),
        'images': images
    }

    return result


def mine(db):
    page = 0
    max_pages = 10000
    total = 0
    while page <= max_pages:
        urls, max_pages = mine_listings(page)
        logger.info('Loaded {} entries from page {} / {}.'.format(len(urls), page, max_pages))
        listings = []
        for url in urls:
            if db.listings.find({'url': url, 'failed': {'$exists': False}}).count() > 0:
                continue
            try:
                logger.debug('url: {}'.format(url))
                listings += [mine_listing(url)]
            except Exception as e:
                msg = traceback.format_exc()
                logger.error('Failed to load {}:\n{}'.format(url, msg))
                listings += [{'url': url, 'failed': True, 'msg': msg}]

        if len(listings):
            db.listings.insert_many(listings)

        page += 1
        total += len(listings)

    logger.info('{} listings inserted.'.format(total))


if __name__ == '__main__':
    from pymongo import MongoClient
    client = MongoClient('db', username='root', password='root')
    db = client.bringatrailer
    mine(db)
