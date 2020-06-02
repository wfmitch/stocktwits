import logging as log
import sys
import os
import requests 
import urllib
import json

RC = 0

# Example list of exchanges to limit a watchlist to
EXCHANGES = ['NYSE', 'NASDAQ', 'NYSEMkt', 'NYSEArca']

# StockTwits details
ST_BASE_URL = 'https://api.stocktwits.com/api/2/'
ST_BASE_PARAMS = dict(access_token=os.getenv('ST_ACCESS_TOKEN'))

def get_json(self,url, params=None):
    """ Uses tries to GET a few times before giving up if a timeout.  returns JSON
    """
    resp = None
    for i in range(4):
        try:
            resp = requests.get(url, params=params, timeout=5)
        except requests.Timeout:
            trimmed_params = {k: v for k, v in params.iteritems() if k not in ST_BASE_PARAMS.keys()}
            log.error('GET Timeout to {} w/ {}'.format(url[len(ST_BASE_URL):], trimmed_params))
        if resp is not None:
            break
    if resp is None:
        log.error('GET loop Timeout')
        return None
    else:
        return json.loads(resp.content)

def post_json(self,url, params=None, deadline=30):
    """ Tries to post a couple times in a loop before giving up if a timeout.
    """
    resp = None
    for i in range(4):
        try:
            resp = requests.post(url, params=params, timeout=5)
        except requests.Timeout:
            trimmed_params = {k: v for k, v in params.iteritems() if k not in ST_BASE_PARAMS.keys()}
            log.error('POST Timeout to {} w/ {}'.format(url[len(ST_BASE_URL):], trimmed_params))
        if resp is not None:
            break
    # TODO wrap in appropriate try/except
    return json.loads(resp.content)





# ---------------------------------------------------------------------
# Basic StockTwits interface
# ---------------------------------------------------------------------
def get_watched_stocks(wl_id):
    """ Get list of symbols being watched by specified StockTwits watchlist
    """
    wl = R.get_json(ST_BASE_URL + 'watchlists/show/{}.json'.format(wl_id), params=ST_BASE_PARAMS)
    wl = wl['watchlist']['symbols']
    return [s['symbol'] for s in wl]


def get_stock_stream(symbol, params={}):
    """ gets stream of messages for given symbol
    """
    all_params = ST_BASE_PARAMS.copy()
    for k, v in params.iteritems():
        all_params[k] = v
    return R.get_json(ST_BASE_URL + 'streams/symbol/{}.json'.format(symbol), params=all_params)


def get_message_stream(wl_id, params={}):
    """ Gets up to 30 messages from Watchlist (wl_id) according to additional params
    """
    all_params = ST_BASE_PARAMS.copy()
    for k, v in params.iteritems():
        all_params[k] = v
    return R.get_json(ST_BASE_URL + 'streams/watchlist/{}.json'.format(wl_id), params=all_params)


def add_to_watchlist(symbols, wl_id):
    """ Adds list of symbols to our StockTwits watchlist.  Returns list of new symbols added
    """
    deadline = 30 * len(symbols)
    symbols = ','.join(symbols)  # must be a csv list
    params = ST_BASE_PARAMS.copy()
    params['symbols'] = symbols
    resp = R.post_json(ST_BASE_URL + 'watchlists/{}/symbols/create.json'.format(wl_id), params=params, deadline=deadline)
    if resp['response']['status'] == 200:
        return [s['symbol'] for s in resp['symbols']]
    else:
        return []


def delete_from_watchlist(symbol, wl_id):
    """ removes a single "symbols" (str) from watchlist.  Returns True on success, False on failure
    """
    params = ST_BASE_PARAMS.copy()
    params['symbols'] = symbol
    resp = R.post_json(ST_BASE_URL + 'watchlists/{}/symbols/destroy.json'.format(wl_id), params=params)
    if resp['response']['status'] == 200:
        return True
    else:
        return False


def get_trending_stocks():
    """ returns list of trending stock symbols, ensuring each symbol is part of a NYSE or NASDAQ
    """
    trending = R.get_json(ST_BASE_URL + 'trending/symbols.json', params=ST_BASE_PARAMS)['symbols']
    symbols = [s['symbol'] for s in trending if s['exchange'] in EXCHANGES]
    return symbols


def clean_watchlist(wl_id):
    """ Deletes stocks to follow if they aren't part of NASDAQ or NYSE
    """
    wl = R.get_json(ST_BASE_URL + 'watchlists/show/{}.json'.format(wl_id),
                params=ST_BASE_PARAMS)['watchlist']['symbols']
    qty_deleted = 0
    for sym in wl:
        if sym['exchange'] not in EXCHANGES:
            log.info("Removing {}".format(sym))
            if delete_from_watchlist(sym['symbol'], wl_id=wl_id):
                qty_deleted += 1
            else:
                log.error("Error deleting symbol from watchlist: {}".format(sym))
    return qty_deleted

def main(): 


    sys.exit(RC)

if __name__=='__main__':
    main()  