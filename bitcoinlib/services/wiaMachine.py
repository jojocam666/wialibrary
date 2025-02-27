

import logging
from datetime import datetime
from datetime import timezone
from wialib.main import MAX_TRANSACTIONS
from wialib.services.baseclient import BaseClient, ClientError
from wialib.transactions import Transaction

PROVIDERNAME = 'wiaMachine'

_logger = logging.getLogger(__name__)


class wiaMachine(BaseClient):

    def __init__(self, network, base_url, denominator, *args):
        super(self.__class__, self).__init__(network, PROVIDERNAME, base_url, denominator, *args)

    def compose_request(self, function, data, parameter='', variables=None, method='get'):
        url_path = function + '/' + data
        if parameter:
            url_path += '/' + parameter
        if variables is None:
            variables = {}
        if self.api_key:
            variables.update({'token': self.api_key})
        return self.request(url_path, variables, method)

    def getbalance(self, addresslist):
        addresslist = self._addresslist_convert(addresslist)
        addresses = ';'.join([a.address for a in addresslist])
        res = self.compose_request('addrs', addresses, 'balance')
        balance = 0.0
        if not isinstance(res, list):
            res = [res]
        for rec in res:
            balance += float(rec['final_balance'])
        return int(balance * self.units)

    def getutxos(self, address, after_txid='', limit=MAX_TRANSACTIONS):
        address = self._address_convert(address)
        res = self.compose_request('addrs', address.address, variables={'unspentOnly': 1, 'limit': 2000})
        transactions = []
        if not isinstance(res, list):
            res = [res]
        for a in res:
            txrefs = a.setdefault('txrefs', []) + a.get('unconfirmed_txrefs', [])
            if len(txrefs) > 500:
                _logger.warning("wiaMachine: Large number of transactions for address %s, "
                                "Transaction list may be incomplete" % address)
            for tx in txrefs:
                if tx['tx_hash'] == after_txid:
                    break
                tdate = None
                if 'confirmed' in tx:
                    try:
                        tdate = datetime.strptime(tx['confirmed'], "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        tdate = datetime.strptime(tx['confirmed'], "%Y-%m-%dT%H:%M:%S.%fZ")
                transactions.append({
                    'address': address.address_orig,
                    'txid': tx['tx_hash'],
                    'confirmations': tx['confirmations'],
                    'output_n': tx['tx_output_n'],
                    'index': 0,
                    'value': int(round(tx['value'] * self.units, 0)),
                    'script': '',
                    'block_height': None,
                    'date': tdate
                })
        return transactions[::-1][:limit]

    def gettransaction(self, txid):
        tx = self.compose_request('txs', txid, variables={'includeHex': 'true'})
        t = Transaction.import_raw(tx['hex'], network=self.network)
        if tx['confirmations']:
            t.status = 'confirmed'
            t.date = datetime.strptime(tx['confirmed'][:19], "%Y-%m-%dT%H:%M:%S")
        else:
            t.status = 'unconfirmed'
        t.confirmations = tx['confirmations']
        t.block_height = tx['block_height'] if tx['block_height'] > 0 else None
        t.fee = tx['fees']
        t.rawtx = bytes.fromhex(tx['hex'])
        t.size = int(len(tx['hex']) / 2)
        t.network = self.network
        t.input_total = 0
        if len(t.inputs) != len(tx['inputs']):
            raise ClientError("Invalid number of inputs provided. Raw tx: %d, wiaMachine: %d" %
                              (len(t.inputs), len(tx['inputs'])))
        for n, i in enumerate(t.inputs):
            if not t.coinbase and not (tx['inputs'][n]['output_index'] == i.output_n_int and
                                       tx['inputs'][n]['prev_hash'] == i.prev_txid.hex()):
                raise ClientError("Transaction inputs do not match raw transaction")
            if 'output_value' in tx['inputs'][n]:
                if not t.coinbase:
                    i.value = tx['inputs'][n]['output_value']
                t.input_total += i.value
        if len(t.outputs) != len(tx['outputs']):
            raise ClientError("Invalid number of outputs provided. Raw tx: %d, wiaMachine: %d" %
                              (len(t.outputs), len(tx['outputs'])))
        for n, o in enumerate(t.outputs):
            if 'spent_by' in tx['outputs'][n]:
                o.spent = True
                o.spending_txid = tx['outputs'][n]['spent_by']
        return t

    def gettransactions(self, address, after_txid='', limit=MAX_TRANSACTIONS):
        txs = []
        address = self._address_convert(address)
        res = self.compose_request('addrs', address.address, variables={'unspentOnly': 0, 'limit': 2000})
        if not isinstance(res, list):
            res = [res]
        for a in res:
            txrefs = a.get('txrefs', []) + a.get('unconfirmed_txrefs', [])
            txids = []
            for t in txrefs[::-1]:
                if t['tx_hash'] not in txids:
                    txids.append(t['tx_hash'])
                if t['tx_hash'] == after_txid:
                    txids = []
            if len(txids) > 500:
                _logger.info("BlockCypher: Large number of transactions for address %s, "
                             "Transaction list may be incomplete" % address.address_orig)
            for txid in txids[:limit]:
                t = self.gettransaction(txid)
                txs.append(t)
        return txs

    def getrawtransaction(self, txid):
        return self.compose_request('txs', txid, variables={'includeHex': 'true'})['hex']

    def sendrawtransaction(self, rawtx):
        # wiaMachine sometimes accepts transactions, but does not push them to the network :(
        if self.network.name in ['wia']:
            return False
        res = self.compose_request('txs', 'push', variables={'tx': rawtx}, method='post')
        return {
            'txid': res['tx']['hash'],
            'response_dict': res
        }

    def estimatefee(self, blocks):
        res = self.compose_request('', '')
        if blocks <= 10:
            return res['medium_fee_per_kb']
        else:
            return res['low_fee_per_kb']

    def blockcount(self):
        return self.compose_request('', '')['height']

    def mempool(self, txid):
        if txid:
            tx = self.compose_request('txs', txid)
            if tx['confirmations'] == 0:
                return [tx['hash']]
        return False

    def getblock(self, blockid, parse_transactions, page, limit):
        if limit > 100:
            limit = 100
        bd = self.compose_request('blocks', str(blockid), variables={'limit': limit, 'txstart': ((page-1)*limit)})
        if parse_transactions:
            txs = []
            for txid in bd['txids']:
                try:
                    txs.append(self.gettransaction(txid))
                except Exception as e:
                    _logger.error("Could not parse tx %s with error %s" % (txid, e))
        else:
            txs = bd['txids']

        block = {
            'bits': bd['bits'],
            'depth': bd['depth'],
            'block_hash': bd['hash'],
            'height': bd['height'],
            'merkle_root': bd['mrkl_root'],
            'prev_block': bd['prev_block'],
            'time': int(datetime.strptime(bd['time'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()),
            'tx_count': bd['n_tx'],
            'txs': txs,
            'version': bd['ver'],
            'page': page,
            'pages': int(bd['n_tx'] // limit) + (bd['n_tx'] % limit > 0),
            'limit': limit
        }
        return block

    # def getrawblock(self, blockid):

    def isspent(self, txid, output_n):
        t = self.gettransaction(txid)
        return 1 if t.outputs[output_n].spent else 0

    # def getinfo(self):
