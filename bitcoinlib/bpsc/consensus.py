#Consensus class for defining blocks' validity conditions before adding them to the chain
#The Wia consensus is based on the principle that a block is valid if it has been relayed 
#a significant number of times by the nodes of the network; no node is responsible for mining the block, if not all the active nodes

from wialib import p2pnet
from wialib import blocks
from wialib import transactions
