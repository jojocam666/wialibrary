

import requests
from urllib.parse import urlencode
import json
from wialib.main import *
from wialib.networks import Network
from wialib.keys import Address

_logger = logging.getLogger(__name__)


class ClientError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        _logger.info(msg)

    def __str__(self):
        return self.msg


class BaseClient(object):

    def __init__(self, network, provider, base_url, denominator, api_key='', provider_coin_id='',
                 network_overrides=None, timeout=TIMEOUT_REQUESTS, latest_block=None):
        try:
            self.network = network
            if not isinstance(network, Network):
                self.network = Network(network)
            self.provider = provider
            self.base_url = base_url
            self.resp = None
            self.units = denominator
            self.api_key = api_key
            self.provider_coin_id = provider_coin_id
            self.network_overrides = {}
            self.timeout = timeout
            self.latest_block = latest_block
            if network_overrides is not None:
                self.network_overrides = network_overrides
        except Exception:
            raise ClientError("This Network is not supported by %s Client" % provider)

    def request(self, url_path, variables=None, method='get', secure=True, post_data=''):
        url_vars = ''
        url = self.base_url + url_path
        if not url or not self.base_url:
            raise ClientError("No (complete) url provided: %s" % url)
        headers = {
            'User-Agent': 'WiaLib/%s' % WIALIB_VERSION,
            'Accept': 'application/json',
            # 'Content-Type': 'application/json',
            "Referrer": "https://www.github.com/1200wd/wialib",
        }
        # ToDo: Check use 'headers = None' for some providers?
        if method == 'get':
            if variables is None:
                variables = {}
            if variables:
                url_vars = '?' + urlencode(variables)
            url += url_vars
            log_url = url if '@' not in url else url.split('@')[1]
            _logger.info("Url get request %s" % log_url)
            self.resp = requests.get(url, timeout=self.timeout, verify=secure, headers=headers)
        elif method == 'post':
            log_url = url if '@' not in url else url.split('@')[1]
            _logger.info("Url post request %s" % log_url)
            self.resp = requests.post(url, json=dict(variables), data=post_data, timeout=self.timeout, verify=secure,
                                      headers=headers)

        resp_text = self.resp.text
        if len(resp_text) > 1000:
            resp_text = self.resp.text[:970] + '... truncated, length %d' % len(resp_text)
        _logger.debug("Response [%d] %s" % (self.resp.status_code, resp_text))
        log_url = url if '@' not in url else url.split('@')[1]
        if self.resp.status_code == 429:
            raise ClientError("Maximum number of requests reached for %s with url %s, response [%d] %s" %
                              (self.provider, log_url, self.resp.status_code, resp_text))
        elif not(self.resp.status_code == 200 or self.resp.status_code == 201):
            raise ClientError("Error connecting to %s on url %s, response [%d] %s" %
                              (self.provider, log_url, self.resp.status_code, resp_text))
        try:
            if not self.resp.apparent_encoding and not self.resp.encoding:
                return self.resp.content
            return json.loads(self.resp.text)
        except ValueError or json.decoder.JSONDecodeError:
            return self.resp.text

    def _address_convert(self, address):
        if not isinstance(address, Address):
            return Address.import_address(address, network_overrides=self.network_overrides, network=self.network.name)

    def _addresslist_convert(self, addresslist):
        addresslistconv = []
        for address in addresslist:
            addresslistconv.append(self._address_convert(address))
        return addresslistconv
