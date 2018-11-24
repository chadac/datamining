#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re, json
import os
import logging
import traceback

logger = logging.getLogger('bringatrailer')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/bringatrailer.log')
fh.setLevel(logging.INFO)

NAME = 'Bring a Trailer'
UPDATE_INTERVAL = 60*60*24

admin_url = 'https://bringatrailer.com/wp-admin/admin-ajax.php'
img_path = 'media/bringatrailer/images/'

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
    return list(set(d)), r['max_pages']


def mine_listing(url):
    slug = re.match(r'https://bringatrailer\.com/listing/([^/]+)/?', url).group(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    info = soup.findAll('td', {'class': 'listing-stats-value'})
    img_urls = [link.get('href') for link in soup.findAll('a', {'class': 'listing-gallery-image-container'})]
    images = []

    if not os.path.exists(img_path + '{}'.format(slug)):
        os.makedirs(img_path + '{}'.format(slug))

    for i, img_url in enumerate(img_urls):
        ext = re.search(r'\.([^.^/]+)$', img_url).group(1)
        path = img_path + '{}/{:03d}.{}'.format(slug, i, ext)
        r1 = requests.get(img_url)
        with open(path, 'wb') as f:
            f.write(r1.content)
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
    print(result)


def mine(client):
    db = client.bringatrailer
    page = 0
    max_pages = 10000
    total = 0
    while page <= max_pages:
        urls, max_pages = mine_listings(page)
        logger.info('Loaded {} entries from page {}.'.format(len(urls), page))
        listings = []
        for url in urls:
            logger.debug('url: {}'.format(url))
            if db.listings.find({'url': url}).count() > 0:
                continue
            count += 1
            try:
                listings += [mine_listing(url)]
            except Exception as e:
                msg = traceback.format_exc()
                logger.error('Failed to load {}:\n{}'.format(url, msg))
                listings += [{'url': url, 'failed': True, 'msg': msg}]

        if len(listings) <= 0:
            break
        else:
            db.listings.insert_many(listings)

        page += 1
        total += len(listings)

    logger.info('{} listings inserted.'.format(total))
