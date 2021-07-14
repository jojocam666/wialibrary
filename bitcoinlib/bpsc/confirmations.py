#if a transaction as been relayed-confirmed a sufficient number of times on the network between the nodes, it's confirmed
#when a clien treceive the bipm_tx of  the transaction,he send it too to a random node and his verifying app would verify if the transaction is valid,and if, return a bool;if the bool is True,the transaction_confirmation_n +=1 
#if the tx_confirms_n >= 5% of the total nodes on the blockchain,the tx is valid and can be added to the current_block 
