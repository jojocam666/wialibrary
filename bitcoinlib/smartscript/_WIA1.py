# ASYMMETRICAL ENCRYPTION IN RSA TAKING INTO ACCOUNT TWO PUBLIC AND PRIVATE KEYS



from __future__ import unicode_literals
import base64
import os

import six
from Crypto import Random
from Crypto.PublicKey import RSA





class PublicKeyFileExists(Exception): pass


class RSAEncryption(object):
    PRIVATE_KEY_FILE_PATH = None
    PUBLIC_KEY_FILE_PATH = None

    def encrypt_rsa(self, message):
        public_key = self._get_public_key()
        public_key_object = RSA.importKey(public_key)
        random_phrase = 'M'
        encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message), random_phrase)[0]
        # use base64 for save encrypted_message in database without problems with encoding
        return base64.b64encode(encrypted_message)

    def decrypt_rsa(self, encoded_encrypted_message):
        encrypted_message = base64.b64decode(encoded_encrypted_message)
        private_key = self._get_private_key()
        private_key_object = RSA.importKey(private_key)
        decrypted_message = private_key_object.decrypt(encrypted_message)
        return six.text_type(decrypted_message, encoding='utf8')

    def generate_keys(self):
        """Be careful rewrite your keys"""
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        private, public = key.exportKey(), key.publickey().exportKey()

        if os.path.isfile(self.PUBLIC_KEY_FILE_PATH):
            raise PublicKeyFileExists('Файл с публичным ключом существует. Удалите ключ')
        self.create_directories()

        with open(self.PRIVATE_KEY_FILE_PATH, 'w') as private_file:
            private_file.write(private)
        with open(self.PUBLIC_KEY_FILE_PATH, 'w') as public_file:
            public_file.write(public)
        return private, public

    def create_directories(self, for_private_key=True):
        public_key_path = self.PUBLIC_KEY_FILE_PATH.rsplit('/', 1)
        if not os.path.exists(public_key_path):
            os.makedirs(public_key_path)
        if for_private_key:
            private_key_path = self.PRIVATE_KEY_FILE_PATH.rsplit('/', 1)
            if not os.path.exists(private_key_path):
                os.makedirs(private_key_path)

    def _get_public_key(self):
        """run generate_keys() before get keys """
        with open(self.PUBLIC_KEY_FILE_PATH, 'r') as _file:
            return _file.read()

    def _get_private_key(self):
        """run generate_keys() before get keys """
        with open(self.PRIVATE_KEY_FILE_PATH, 'r') as _file:
            return _file.read()

    def _to_format_for_encrypt(value):
        if isinstance(value, int):
            return six.binary_type(value)
        for str_type in six.string_types:
            if isinstance(value, str_type):
                return value.encode('utf8')
        if isinstance(value, six.binary_type):
            return value
            
            
     KEYS_DIRECTORY = settings.SURVEY_DIR_WITH_ENCRYPTED_KEYS

class TestingEncryption(RSAEncryption):
    PRIVATE_KEY_FILE_PATH = KEYS_DIRECTORY + 'private.key'
    PUBLIC_KEY_FILE_PATH = KEYS_DIRECTORY + 'public.key'


# django/flask
from django.core.files import File 

class ProductionEncryption(RSAEncryption):
    PUBLIC_KEY_FILE_PATH = settings.SURVEY_DIR_WITH_ENCRYPTED_KEYS + 'public.key'

    def _get_private_key(self):
        """run generate_keys() before get keys """
        from corportal.utils import global_elements
        private_key = global_elements.request.FILES.get('private_key')
        if private_key:
            private_key_file = File(private_key)
            return private_key_file.read()

message = 'Hello мой friend'
encrypted_mes = ProductionEncryption().encrypt(message)
decrypted_mes = ProductionEncryption().decrypt(message)
......................

   
def new_address():
    
    address = RIPEMD160( SHA256( public_key ) )
    
    return address
    

        
  ............................
  
 # SYMMETRICAL ENCRYPTION AES CBC MODE
 
 
 
  def randomCryptoNumber():
    return RNG.new().read(AES.block_size) #Returns a random number

  
  def append_data(data):
    # if the data size is 16 byte, no addition
    if len(data) % 16 == 0:
        return data

    # We remove a byte to add the 0x80

    dataAppend = 15 - (len(data) % 16)

    data = '%s\x80' % data
    data = '%s%s' % (data, '\x00' * dataAjouter)

    return data  
  
  def remove_data(data):
  if not data:
      return data

  data = data.rstrip('\x00')
  if data[-1] == '\x80':
      return data[:-1]
  else:
      return data
  
 

def generateCryptoKey():
    key_size = 32
    key = str(RNG.new().read(key_size))
    return key  
  
 import Crypto.Cipher.AES as AES

def encrypt_aes(data, key):

  #Encrypts data using AES in CBC mode

  data = append_data(data)
  number = randomCryptoNumber()
  aes = AES.new(key, AES.MODE_CBC, number)
  msg_crypt = aes.encrypt(data)

  return number + msg_crypt

def decrypt_aes(ciphertext, key):

  #Decrypts a ciphertext encrypted with AES in CBC mode

  if len(ciphertext) <= AES.block_size:
      raise Exception("Invalid ciphertext.")
  number = ciphertext[:AES.block_size]
  ciphertext = ciphertext[AES.block_size:]
  aes = AES.new(key, AES.MODE_CBC, number)
  data = aes.decrypt(ciphertext)

  return remove_data(data) #Remove added padding
...................

# SIGNATURE PROCEDURE
# PREPARATION OF THE SIGNED MESSAGE


def signature_data(self,data,key):

    key = self.key
    data = ""
    if data =! None:
    condensat_data =  hash256(data)
    
    if condensat_data =! None:
    
    signature = encrypt_aes(self,condensat_data,key)
    
    return signature
    
 def _get_signed_message
 
    signed_message = []
    
    cipher_key = encrypt_rsa(self,key)
    
    
    signed_message.extend([data, signature, cipher_key])
    
    return signed_message
    
#................................................................. RECEIPT OF MESSAGE....................................................................
def decrypt_signature(self):
    
    return decrypt_rsa(self,signature)


def _get_authentic_signature(self):
    
      if hash256(signed_message[0]) == decrypt_signature
      
      return True
    
    
class Wia1():
    
    def __init__(self, locking, unlocking, script_type, script = None):
   
    """class to define wia's specific script of transaction locking
    """
    self.data = transaction
    lockscript = []
    originscript = []
    script = []
    def hash256(self,data):
            data_string = json.dumps(data, sort_keys=True).encode()
            hash256 = hashlib.sha256(data_string).hexdigest()
  
        return hash256_data
   
    def WIA1_encrypt(self,data,public_key,rand_key,data):
        key_size = 32
        new_random_key = str(RNG.new().read(key_size))
        script.append(hash256(data),new_random_key,data)
        originscript.append(encrypt_rsa(script,public_key)#FIX ME:à la base la kpb est deja definie dans la fonction encrypt_rsa
        
        cif_data = encrypt_aes(data,new_random_key)
        cif_rd_key = encrypt_rsa(new_random_key)
        tx_signature = signature_data(data,new_random_key)
        lockscript.append(tx_signature,cif_rd_key,cif_data)
        
        return lockscript
     
    
    
    def WIA1_decrypt(self,script,private_key):
     
    
        lockscript = self.lockscript
       
            for cif_data,cif_rd_key,tx_signature in lockscript
    
            prime_tx = self.transaction
            verif_hash = self.verif_hash
            verif_rd_key = decrypt_rsa(cif_rd_key,new_random_key)
            verif_data = decrypt_aes(cif_data,verif_rd_key)
      
        if verif_hash == None:
            verif_hash = decrypt_aes(signature,verif_rd_key)
          return verif_hash
        
        if verif_hash = hash256(transaction) and verif_data == prime_tx  :
            unlockscript = [verif_hash,verif_rd_key,verif_data]
            
        if unlockscript = decrypt_rsa(origin_script,private_key):#verifier s'il ny a pas besoin de serialiser les scripts
            return True
    return True

    
        
        
    
.....................

.....................    
 
 
 # data hash to sha(256,384,512)   
   
   
   
 #/import hashlib
  
#def hash384(data)
 # data_string = json.dumps(data, sort_keys=True).encode()
  #hashed_data384 = hashlib.sha1(data_string).hexdigest()
  
  #return hashed_data384



#def hash512(data)
 # data_string = json.dumps(data, sort_keys=True).encode()
  #hashed_data512 = hashlib.sha512(data_string).hexdigest()
  
 # return hashed_data512

   #@staticmethod
    #def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
      #  block_string = json.dumps(block, sort_keys=True).encode()
     #   return hashlib.sha256(block_string).hexdigest()
        
    #def hash(transaction):
        """
        Creates a SHA-256 hash of a transaction
        :param block: transaction
        """
   #     def hash384(data)
  #data_string = json.dumps(data, sort_keys=True).encode()
  #hashed_data384 = hashlib.sha1(data_string).hexdigest()
  
  #return hashed_data384
..................

#



