import os
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
SEARCH_LIMIT = 3
BUSINESS_PATH = '/v2/business'
PHONE_SEARCH_PATH = '/v2/phone_search'


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


def get_business(business_id):
    path = BUSINESS_PATH + '/' + business_id
    url = sign_request(path)
    results = requests.get(url)
    return results.json()


def phone_search(phone, cc=None, category=None):
    parameters = {'phone': phone}
    if cc is not None:
        parameters['cc'] = cc
    if category is not None:
        parameters['category'] = category
    url = sign_request(PHONE_SEARCH_PATH, parameters)
    results = requests.get(url)
    return results.json()


if __name__ == '__main__':
    term = 'fedex office'
    location = 'San Francisco, CA'
    results = search(term, location)
    business_id = 'fedex-office-print-and-ship-center-colma'
    results = get_business(business_id)
    phone = '3154431870'
    results = phone_search(phone)
    pass