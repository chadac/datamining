#!/usr/bin/env python3

from lib.http import HTTP
from bs4 import BeautifulSoup
import re, json
import os
import logging, sys
import traceback


DOWNLOAD_DIR = './data'


http = HTTP()
image_http = HTTP(wait_time=0.2)
listing_url_fmt = 'https://{}.craigslist.org/search/{}?s={}'
img_url_fmt = 'https://images.craigslist.org/{}_{}_{}x{}.{}'


def fetch_cities():
    r = http.get('https://geo.craigslist.org/iso/us')
    html = r.text
    urls = re.findall(r'"https://([a-zA-Z0-9]+)\.craigslist\.org"', html)
    return list(set(urls))


def fetch_listings(city, category, s=0):
    url = listing_url_fmt.format(city, category, s)
    r = http.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.findAll('p', {'class': 'result-info'})
    listings = []
    for i, result in enumerate(results):
        title = result.find('a', {'class': 'result-title'})
        listing = {
            'title': title.getText().strip(),
            'url': title['href'],
            'id': title['data-id']
        }
        price = result.find('span', {'class': 'result-price'})
        listing['short'] = True
        if price:
            listing['price'] = price.getText().strip()
        submitted = result.find('time', {'class': 'result-date'})
        if submitted:
            listing['date'] = submitted['datetime']
        hood = result.find('span', {'class': 'result-hood'})
        if hood:
            listing['hood'] = hood.getText().strip().strip('()')

        listings += [listing]
    return listings


def get_detailed_listing(data):
    r = http.get(data['url'])
    soup = BeautifulSoup(r.text, 'html.parser')
    attrs = {}
    for attrgroup in soup.findAll('p', {'class': 'attrgroup'}):
        for span in attrgroup.findAll('span'):
            if not ':' in span.text:
                continue
            attr = span.find(text=True).strip().strip(':')
            value = span.find('b').text.strip()
            if attr != value:
                attrs[attr] = value
    body = '\n'.join([txt.strip() for txt in soup.find('section', {'id': 'postingbody'}).findAll(text=True, recursive=False)])
    gallery = soup.find('div', {'id': 'thumbs'})
    for ele in soup.find('div', {'class': 'postinginfos'}).findAll('p'):
        if 'posted:' in ele.text:
            data['date'] = ele.find('time').attrs['datetime']
        elif 'updated:' in ele.text:
            data['updated'] = ele.find('time').attrs['datetime']
    if not 'updated' in data:
        data['updated'] = data['date']
    images = []
    if gallery:
        for img in gallery.findAll('img'):
            m = re.match('https://images\.craigslist\.org/(\w+)_(\w+)_[0-9]+x\w+\.(.+)$', img['src'])
            if m:
                images += [{
                    'prefix': m.group(1),
                    'id': m.group(2),
                    'ext': m.group(3)
                }]

    data['body'] = body
    data['images'] = images
    data['attrs'] = attrs
    data['short'] = False


def download_images(images, image_dir):
    if not image_dir:
        ## will not be downloading
        return

    for img in images:
        path = image_dir / f"{img['id']}.{img['ext']}"
        if not path.exists():
            url = img_url_fmt.format(img['prefix'], img['id'], 1200, 900, img['ext'])
            r = image_http.get(url)
            img['path'] = str(path)
            with open(path, 'wb') as f:
                f.write(r.content)
    return images
