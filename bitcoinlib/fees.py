from wialib import network
import transaction

def calculate_fee(self):
        """
        Get fee for this transaction in smallest denominator (i.e. lio) based on its size and the
        transaction.fee_per_kb value

        :return int: Estimated transaction fee
        """

        if not self.fee_per_kb:
            raise TransactionError("Cannot calculate transaction fees: transaction.fee_per_kb is not set")
        fee = int(self.estimate_size() / 1024.0 * self.fee_per_kb)
        # FIXME: fee is in kb, network.fee_min in lio/kb
        if fee < self.network.fee_min:
            fee = self.network.fee_min
        elif fee > self.network.fee_max:
            fee = self.network.fee_max
        return fee
      
      
def calculate_fee2(self):
        """
        Get fee for this transaction in smallest denominator based on its total value and the transaction.fee_per_coin value
        
        :return int: Estimated transaction fee
        """
    
        if not self.fee_per_coin:
            raise TransactionError("Cannot calculate transaction fees: transaction.fee_per_coin is not set")
          fee = int(self.outputs.value * self.fee_per_coin)
          if fee < self.network.fee_min:
            fee = self.network.fee_min
        elif fee > self.network.fee_max:
            fee = self.network.fee_max
        return fee
      
      
 def fees_mode(self, outputs, value )
        """
        Get the fees_calculating mode from the transaction value and size
        
        :return bool: fees_mode
        """
        if len(self.outputs) < 5:
            fees_mode = calculate_fee2
            return fees_mode
        else 
            fees_mode = calculate_fee
