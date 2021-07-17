I- BLOCKCHAIN/
Wia is a new disruptive form of blockchain which is manipulated by the nodes of the network but is authenticated by a "distributed node" technology, which is in fact a mini-software which ensures several trust missions not yet truly resolved by the blockchain community at present , such as block validation and transaction authentication, thus requiring no mining activity on the network, which makes our blockchain an autonomous network, which in the future would prove to be very efficient in terms of electrical energy saving and faster and more reliable.

The Wia blockchain, commonly referred to here under the name of "smartblockchain" is usually a chain of blocks, where the addition of a transaction follows:
1-A wallet A carries out a transaction towards a wallet B.
2-A set of transactions is grouped together within the same block.
3-The block is checked by the different "mining_log" (distributed node) of the nodes of the network, which check its validity by a cryptographic technique.
4-The validated block is added to the blockchain and all users have access to the transactions it contains.
5-Wallet B receives the transaction issued by wallet A.

Detail of the creation of a transaction:
- class Tx (sender, recipient, amount, inputs, outputs, fees_mode, fees, timestamp, signature, lock_packet)
 *The fees_mode allows you to know if the charges applied will be at the value of the transaction or at its size in bytes and its number of outputs.
 
 *The lock packet is an "encrypted set of encrypted transactions" used to determine the validity of a transaction.
The signature, or more precisely the witness signature is the digital signature of a transaction completed with a flag which allows to know the ordinal position of an unlocking packet on the block in order to find there the real signature of the transaction, using a different process.

 *A lock package is a list containing 1°) an original script as follows:
- the real witness signature
-the data of the transaction
-the data hash
*the said script being encrypted with the owner's symetric key previously used for this transaction;
to this package is added 2°):
- the true signature,
-crypted transactions and
- the cipher of the symetric key used to encrypt the transactions
There are three types of tx: normal, bpsc_serial and coinbase

  *There are several types of locks on the wia blockchain, such as hybrid closing scripts (the classic one), kneaded padlock scripts and multi-signature scripts
  *A transaction can take several forms: change of owner,in case of equal input-output value; input distributed to several outputs; several outputs for a single output.
