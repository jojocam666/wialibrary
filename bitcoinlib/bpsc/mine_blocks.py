
#the bpsc is in charge of the mining of new blocks to the blockchain; mining a block means  #01.take entire current tx informations for the block from the mempool and verify that the block is valid
#this work is done by the whole connected nodes,who receive bipm_tx in their mempool and verify them with their Client; next,#02.check the full block information from the block relayer(the last node to do a transaction for this block)
#and verify the block; after this #03.the bpsc check the full block(only when is confirmation_ratio as succesfully been achieved) and add it to the chain in three different modes:ligth,for the 
#majority of the nodes; complete(full blockchain files and wallets states) and basic(completely all informations); when added, the new block and blockchain are both broadcasted on the network
#and every node must update his chain(automatically done by the Client when connexion turned on)
#























import hashlib
import json
from wialib import blocks

class Smart_Blockchain:
       
    def __init__(self):
        
        self.current_transactions = []
        
        self.chain = []
        
        self.nodes = set()

        self.build_genesis()
        
    def build_genesis(self):       # Create the genesis block
        
        genesis_block = Block(,prev_block=1
        
        self.new_block(previous_hash='1')

    def new_block(self, previous_hash):
        """
        Create a new Block in the Smart Blockchain
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = Block(
            'index': len(self.chain) + 1,
            'timestamp': time() or str(datetime.datetime.now()),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        )

        # Reset the current list of transactions
        
        self.current_transactions = []

        self.chain.append(block)
        
        return block
        
    @staticmethod
    
     def confirm_validity(block, previous_block):
           
           if last_block.index + 1 != block.index:

            return False

        elif last_block.hash != block.previous_hash:

            return False

        elif block.timestamp <= last_block.timestamp:

            return False

        return True
        
        
    def get_data(self, sender, receiver, amount):

        self.current_data.append({

            'sender': sender,

            'receiver': receiver,

            'amount': amount

        })

        return True
        
        
 blockchain = Smart_BlockChain()

        
        self.chain = []        
 
def is_valid_block(self, block,block_confirms):
        
        if block_confirms > min_confirmations:
        return True     
        
def _add_new_block(block_dict):
 
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_block(block, block_confirms):
            return False
        block.hash = proof
        self.chain.append(block)
        return True
 
        self.chain.append(block_dict)
        return chain

    


 

    
    
    
    
    
    
