

from wialib.services.baseclient import BaseClient

PROVIDERNAME = 'cryptofees'


class CryptofeesClient(BaseClient):

    def __init__(self, network, base_url, denominator, *args):
        super(self.__class__, self).__init__(network, PROVIDERNAME, base_url, denominator, *args)

    def compose_request(self, category, cmd, method='get'):
        url_path = category
        if cmd:
            url_path += '/' + cmd
        return self.request(url_path, method=method)

    def estimatefee(self, blocks):
        res = self.compose_request('fees', 'recommended')
        if blocks <= 1:
            return res['fastestFee'] * 1024
        elif blocks <= 2:
            return res['halfHourFee'] * 1024
        return res['hourFee'] * 1024
