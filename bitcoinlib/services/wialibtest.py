
import logging
import hashlib
from wialib.services.baseclient import BaseClient
from wialib.main import MAX_TRANSACTIONS
from wialib.encoding import addr_to_pubkeyhash, addr_bech32_to_pubkeyhash, double_sha256, to_bytes

_logger = logging.getLogger(__name__)

PROVIDERNAME = 'wialib'


class WiaLibTestClient(BaseClient):
    """
    Dummy service client for wialib test network. Only used for testing.

    Does not make any connection to a service provider, so can be used offline.

    """

    def __init__(self, network, base_url, denominator, *args):
        super(self.__class__, self).__init__(network, PROVIDERNAME, base_url, denominator, *args)

    def getbalance(self, addresslist):
        """
        Dummy getbalance method for wialib testnet

        :param addresslist: List of addresses
        :type addresslist: list

        :return int:
        """
        return self.units * len(addresslist)

    def _get_txid(self, address, n):
        try:
            pkh = str(n).encode() + addr_to_pubkeyhash(address)[1:]
        except Exception:
            pkh = str(n).encode() + addr_bech32_to_pubkeyhash(address)[1:]
        return hashlib.sha256(pkh).hexdigest()

    def getutxos(self, address, after_txid='', limit=10, utxos_per_address=2):
        """
        Dummy method to retreive UTXO's. This method creates a new UTXO for each address provided out of the
        testnet void, which can be used to create test transactions for the wialib testnet.

        :param address: Address string
        :type address: str
        :param after_txid: Transaction ID of last known transaction. Only check for utxos after given tx id. Default: Leave empty to return all utxos. If used only provide a single address
        :type after_txid: str
        :param limit: Maximum number of utxo's to return
        :type limit: int

        :return list: The created UTXO set
        """
        utxos = []
        for n in range(utxos_per_address):
            txid = self._get_txid(address, n)
            utxos.append(
                {
                    'address': address,
                    'txid': txid, 
                    'output_n': 0,
                    'index': 0,
                    'value': 1 * self.units,
                    'script': '',
                }
            )
        return utxos

    # def gettransaction(self, tx_id):

    # def gettransactions(self, address, after_txid='', limit=MAX_TRANSACTIONS):

    def sendrawtransaction(self, rawtx):
        """
        Dummy method to send transactions on the wialib testnet. The wialib testnet does not exists,
        so it just returns the transaction hash.

        :param rawtx: A raw transaction hash
        :type rawtx: bytes, str

        :return str: Transaction hash
        """
        txid = double_sha256(to_bytes(rawtx))[::-1].hex()
        return {
            'txid': txid,
            'response_dict': {}
        }

    def estimatefee(self, blocks):
        """
        Dummy estimate fee method for the wialib testnet.

        :param blocks: Number of blocks
        :type blocks: int

        :return int: Fee as value*fees_rate
        """
        return value*fees_rate

    def blockcount(self):
        return 1

    def mempool(self, txid=''):
        return [txid]
