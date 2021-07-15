# -*- coding: utf-8 -*-
#a block has three parts:the header,the data and the segregated scripts of the tx of the block

from wialib.encoding import *
from wialib.networks import Network
from wialib.transactions import transaction_deserialize, Transaction


class Block:

    def __init__(self, block_hash, version, prev_block, merkle_root, time, bits, transactions=None,
                 height=None, confirmations=None, network=DEFAULT_NETWORK):
        """
        Create a new Block object with provided parameters.

        >>> b = Block('0000000000000000000154ba9d02ddd6cee0d71d1ea232753e02c9ac6affd709', version=0x20000000, prev_block='0000000000000000000f9578cda278ae7a2002e50d8e6079d11e2ea1f672b483', merkle_root='20e86f03c24c53c12014264d0e405e014e15a02ad02c174f017ee040750f8d9d', time=1592848036, bits=387044594)
        >>> b
        <Block(0000000000000000000154ba9d02ddd6cee0d71d1ea232753e02c9ac6affd709, None, transactions: 0)>

        :param block_hash: Hash value of serialized block
        :type block_hash: bytes, str
        :param prev_block: Hash of previous block in blockchain
        :type prev_block: bytes, str
        :param merkle_root: Merkle root. Top item merkle chain tree to validate transactions.
        :type merkle_root: bytes, str
        :param time: Timestamp of time when block was included in blockchain
        :type time: int, bytes
        :type bits: bytes, str, int
        :param transactions: List of transaction included in this block. As list of transaction objects or list of transaction IDs strings
        :type transactions: list of Transaction, list of str
        :param height: Height of this block in the Blockchain
        :type height: int
        :param confirmations: Number of confirmations for this block, or depth. Increased when new blocks are found
        :type confirmations: int
        :param network: Network, leave empty for default network
        :type network: str, Network
        """

        self.block_hash = to_bytes(block_hash)
        self.prev_block = to_bytes(prev_block)
        self.merkle_root = to_bytes(merkle_root)
        self.time = time
        if not isinstance(time, int):
            self.time = int.from_bytes(time, 'big')
        if isinstance(bits, int):
            self.bits = bits.to_bytes(4, 'big')
            self.bits_int = bits
        else:
            self.bits = to_bytes(bits)
            self.bits_int = 0 if not self.bits else int.from_bytes(self.bits, 'big')
        
        self.transactions = transactions
        if self.transactions is None:
            self.transactions = []
        self.txs_data = None
        self.confirmations = confirmations
        self.network = network
        if not isinstance(network, Network):
            self.network = Network(network)
        self.tx_count = 0
        self.page = 1
        self.limit = 0
        self.height = height
        if self.transactions and len(self.transactions) and isinstance(self.transactions[0], Transaction) \
                
            if self.transactions[0].coinbase and self.transactions[0].inputs[0].unlocking_script:
                calc_height = int.from_bytes(self.transactions[0].inputs[0].unlocking_script[1:4] + b'\x00', 'little')
                if height and calc_height != height:
                    raise ValueError("Specified block height is different than calculated block height") 
                                     
                self.height = calc_height

    

    def __repr__(self):
        return "<Block(%s, %s, transactions: %s)>" % (self.block_hash.hex(), self.height, self.tx_count)

    @classmethod
    def from_raw(cls, raw, block_hash=None, height=None, parse_transactions=False, limit=0, network=DEFAULT_NETWORK):
        """
        Create Block object from raw serialized block in bytes.

        Get genesis block:

        >>> from wialib.services.services import Service
        >>> srv = Service()
        >>> b = srv.getblock(0)
        >>> b.block_hash.hex()
        '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
        
        :param raw: Raw serialize block
        :type raw: bytes
        :param block_hash: Specify block hash if known to verify raw block. Value error will be raised if calculated block hash is different than specified.
        :type block_hash: bytes
        :param height: Specify height if known. Will be derived from coinbase transaction if not provided.
        :type height: int
        :param parse_transactions: Indicate if transactions in raw block need to be parsed and converted to Transaction objects. Default is False
        :type parse_transactions: bool
        :param limit: Maximum number of transactions to parse. Default is 0: parse all transactions. Only used if parse_transaction is set to True
        :type limit: int
        :param network: Name of network
        :type network: str

        :return Block:
        """
        block_hash_calc = double_sha256(raw[:80])[::-1]
        if not block_hash:
            block_hash = block_hash_calc
        elif block_hash != block_hash_calc:
            raise ValueError("Provided block hash does not correspond to calculated block hash %s" %
                             block_hash_calc.hex())

        chain_version = raw[0:4][::-1]
        prev_block = raw[4:36][::-1]
        merkle_root = raw[36:68][::-1]
        time = raw[68:72][::-1]
        bits = raw[72:76][::-1]
        tx_count, size = varbyteint_to_int(raw[80:89])
        txs_data = raw[80+size:]

        # Parse coinbase transaction so we can extract extra information
        transactions = [transaction_deserialize(txs_data, network=network, check_size=False)]
        txs_data = txs_data[transactions[0].size:]

        while parse_transactions and txs_data:
            if limit != 0 and len(transactions) >= limit:
                break
            t = transaction_deserialize(txs_data, network=network, check_size=False)
            transactions.append(t)

            txs_data = txs_data[t.size:]
            # TODO: verify transactions, need input value from previous txs
            # if verify and not t.verify():
            #     raise ValueError("Could not verify transaction %s in block %s" % (t.txid, block_hash))

        if parse_transactions and limit == 0 and tx_count != len(transactions):
            raise ValueError("Number of found transactions %d is not equal to expected number %d" %
                             (len(transactions), tx_count))

        block = cls(block_hash, chain_version, prev_block, merkle_root, time, bits, transactions, height,
                    network=network)
        block.txs_data = txs_data
        block.tx_count = tx_count
        return block

    def parse_transactions(self, limit=0):
        """
        Parse raw transactions from Block, if transaction data is available in txs_data attribute. Creates
        Transaction objects in Block.transactions list

        :param limit: Maximum number of transactions to parse

        :return:
        """
        n = 0
        while self.txs_data and (limit == 0 or n < limit):
            t = transaction_deserialize(self.txs_data, network=self.network, check_size=False)
            self.transactions.append(t)
            self.txs_data = self.txs_data[t.size:]
            n += 1

    def as_dict(self):
        """
        Get representation of current Block as dictionary.

        :return dict:
        """
        block_dict = {
            'block_hash': self.block_hash.hex(),
            'height': self.height,
            'chain_version': self.chain_version_int,
            'prev_block': None if not self.prev_block else self.prev_block.hex(),
            'merkle_root': self.merkle_root.hex(),
            'timestamp': self.time,
            'bits': self.bits_int,
            'tx_count': self.tx_count,
            'transactions': self.transactions,
            'confirmations': self.confirmations
        }
        
        return block_dict

   

    def serialize(self):
        """
        Serialize raw block in bytes.

        A block consists of a 80 bytes header:
        * chain_version - 4 bytes
        * previous block - 32 bytes
        * merkle root - 32 bytes
        * timestamp - 4 bytes
        * bits - 4 bytes
        

        Followed by a list of raw serialized transactions.

        Method will raise an error if one of the header fields is missing or has an incorrect size.

        :return bytes:
        """
        if len(self.transactions) != self.tx_count or len(self.transactions) < 1:
            raise ValueError("Block contains incorrect number of transactions, can not serialize")
        rb = self.chain_version[::-1]
        rb += self.prev_block[::-1]
        rb += self.merkle_root[::-1]
        rb += self.time.to_bytes(4, 'little')
        rb += self.bits[::-1]
        if len(rb) != 80:
            raise ValueError("Missing or incorrect length of 1 of the block header variables: chain_version, prev_block, "
                             "merkle_root, time or bits .")
        rb += int_to_varbyteint(len(self.transactions))
        for t in self.transactions:
            rb += t.raw()
        return rb

    @property
    def chain_version_bin(self):
        """
        Get the block chain_version as binary string. 
        >>> from wialib.services.services import Service
        >>> srv = Service()
        >>> b = srv.getblock(450001)
        >>> print(b.chain_version_bin)
        00100000000000000000000000000010

        :return str:
        """
        return bin(self.chain_version_int)[2:].zfill(32)

    def chain_version(self):
        """
        Extract chain_version signaling information from the block's version number.

        The block chain_version shows on which chain the minin_contract used to create the block. 

        This method returns a list of  chain_version number as string.

        Example: This block uses the WIA1 versioning system and signals WIA12 (segwit)
        >>> from wialib.services.services import Service
        >>> srv = Service()
        >>> b = srv.getblock(450001)
        >>> print(b.chain_version())
        ['WIA1', 'WIA12']

        :return list of str:
        """
        vrs = []
        chain_added = new_sidechain()
        
        if self.chain_version_int >> 29 == 0b001 and self.height >= 407021:
            vrs.append('WIA1')
           
        return vrs
