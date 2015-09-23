import asyncio
import os
import aiohttp
import requests
import oauth2
import yaml

api_keys = yaml.load(open(os.getenv('YELP_YAML', '')))
CONSUMER_KEY = api_keys['CONSUMER_KEY']
CONSUMER_SECRET = api_keys['CONSUMER_SECRET']
TOKEN = api_keys['TOKEN']
TOKEN_SECRET = api_keys['TOKEN_SECRET']

PROTOCOL = 'https'
HOST = 'api.yelp.com'

SEARCH_PATH = '/v2/search'
SEARCH_LIMIT = 10
BUSINESS_PATH = '/v2/business'


def sign_request(path, path_parameters=None):
    url = PROTOCOL + '://' + HOST + path
    parameters = {
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': oauth2.generate_timestamp(),
        'oauth_token': TOKEN,
        'oauth_consumer_key': CONSUMER_KEY
    }
    if path_parameters is not None and type(path_parameters) == dict:
        parameters.update(path_parameters)
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    req = oauth2.Request(method="GET", url=url, parameters=parameters)
    req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = req.to_url()
    return signed_url


def search(term, location):
    parameters = {
        'term': term,
        'location': location,
        'limit': SEARCH_LIMIT
    }
    url = sign_request(SEARCH_PATH, parameters)
    results = requests.get(url)
    return results.json()


@asyncio.coroutine
def get_business(business_id):
    path = BUSINESS_PATH + '/' + business_id
    url = sign_request(path)
    response = yield from aiohttp.request('GET', url)
    result = yield from response.read_and_close(decode=True)
    business = result
    return business


@asyncio.coroutine
def get_all_businesses(search_results):
    businesses = []
    coroutines = []
    for business in search_results['businesses']:
        coroutines.append(get_business(business['id']))
    for result in asyncio.as_completed(coroutines):
        b = yield from result
        businesses.append(b)
    return businesses


if __name__ == '__main__':
    term = "Mc Donald's"
    location = 'San Francisco, CA'
    results = search(term, location)
    loop = asyncio.get_event_loop()
    businesses = loop.run_until_complete(get_all_businesses(results))
    print('businesses: %d' % len(businesses))
    for item in businesses:
        if 'error' not in item:
            print('name, id,rating = %s, %s, %f' % (item['name'], item['id'], item['rating']))
        else:
            print('error: %s' % (item['error']['description']))
    pass