#!/usr/bin/python

# Pass in some random bytes, and this utility will turn it into a
# 256-bit base58-encoded number that's suitable as a passphrase. Example:
#
# < /dev/random head -c 1024 | base58passphrase

import hashlib
import sys

alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
base_count = len(alphabet)

# 256 / log2(58), rounded up
PASSPHRASE_LENGTH = 44

def encode(num):
  """ Returns num in a base58-encoded string """
  encode = ''

  if (num < 0):
    return ''

  while (num >= base_count):
    mod = num % base_count
    encode = alphabet[mod] + encode
    num = num / base_count

  if (num):
    encode = alphabet[num] + encode

  return encode

input = sys.stdin.read()

hash = ''
hash = hashlib.sha512(hash + input).digest()
hash = hashlib.sha512(hash + input).digest()
hash = hashlib.sha384(hash + input).digest()
hash = hashlib.sha384(hash + input).digest()
hash = hashlib.sha256(hash + input).digest()
hash = hashlib.sha256(hash + input).digest()
encoded = ''

# hashes starting with enough zeroes will end up encoding to something
# shorter than the maximum length. Instead of coming up with a clever
# way to deal with them, just keep on hashing until something else comes
# up.
while len(encoded) < PASSPHRASE_LENGTH:
  hash = hashlib.sha256(hash + input).digest()
  num = int(hash.encode("hex"), 16)
  encoded = encode(num)

print encode(num),
