#!/usr/bin/env python3

from lib.http import HTTP
from bs4 import BeautifulSoup
import re, json
import os
import logging, sys
import traceback

http = HTTP()
cto_url_fmt = 'https://{}.craigslist.org/search/cto?s={}'
img_url_fmt = 'https://images.craigslist.org/{}_{}_{}x{}.{}'


def mine_cities():
    r = http.get('https://geo.craigslist.org/iso/us')
    html = r.text
    urls = re.findall(r'"https://([a-zA-Z0-9]+)\.craigslist\.org"', html)
    return list(set(urls))


def mine_listings(city, s=0):
    url = cto_url_fmt.format(city, s)
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


def mine_listing(data):
    r = http.get(data['url'])
    print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    attrs = {}
    for attrgroup in soup.findAll('p', {'class': 'attrgroup'}):
        for span in attrgroup.findAll('span'):
            attr = span.find(text=True).strip().strip(':')
            value = span.find('b').text.strip()
            if attr != value:
                attrs[attr] = value
    body = '\n'.join([txt.strip() for txt in soup.find('section', {'id': 'postingbody'}).findAll(text=True, recursive=False)])
    gallery = soup.find('div', {'id': 'thumbs'})
    images = []
    for img in gallery.findAll('img'):
        print(img)
        m = re.match('https://images\.craigslist\.org/(\w+)_(\w+)_[0-9]+x\w+\.(.+)$', img['src'])
        if m:
            images += [{
                'prefix': m.group(1),
                'id': m.group(2),
                'ext': m.group(3)
            }]
    data['body'] = body
    data['images'] = images
    data['attrss'] = attrs
    return data


if __name__ == '__main__':
    listings = mine_listings('tulsa')
    print(mine_listing(listings[1]))
