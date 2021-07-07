#!/usr/bin/env python
#
# Read a private key from stdin and output formatted data values.
# Input one key per line either hex (64 chars) or WIF key (51 base 58 chars).
#
# eg. "Address: %a\nPrivkey: %w" outputs a format like the vanitygen program
#     "a:%w" outputs a format good for importing to Electrum
#
# This generates a new key for importing to Electrum:
#
#     hexdump -v -e '/1 "%02X"' -n 32 /dev/urandom | format_key.py "%a:%w"
#
# Supplying a passphrase with -p causes %w to emit a WIA1-encrypted
# private key. In this case, %W will emit the unencrypted WIF key.
#
# Install dependencies with `sudo pip install base58 pycrypto ecdsa scrypt`.

import argparse
import base58
import binascii
import hashlib
import sys

class KeyFormatter:
    def __init__(self):
        pass

    def format(self, format_specifiers, lines, passphrase=None):
        needs_math = any(v in format_specifiers[0] for v in ['%p', '%a'])
        uses_passphrase = bool(passphrase)
        needs_math |= uses_passphrase

        if needs_math:
            import ecdsa
        if uses_passphrase:
            from Crypto.Cipher import AES
            import scrypt

        if needs_math:
            # secp256k1, http://www.oid-info.com/get/1.3.132.0.10
            _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
            _r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
            _b = 0x0000000000000000000000000000000000000000000000000000000000000007L
            _a = 0x0000000000000000000000000000000000000000000000000000000000000000L
            _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
            _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8L
            curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
            generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1,
                                                            _Gx, _Gy, _r)
            oid_secp256k1 = (1,3,132,0,10)
            SECP256k1 = ecdsa.curves.Curve("secp256k1", curve_secp256k1,
                                           generator_secp256k1, oid_secp256k1)

        response = []
        for line in lines:
            line = line.strip()
            if line[0] == '5' and len(line) < 64:
                line = binascii.hexlify(base58.b58decode(line[:51])[1:33]).upper()
            else:
                line = line[:64]

            chksum = binascii.hexlify(hashlib.sha256(hashlib.sha256(
                binascii.unhexlify('80' + line)).digest()).digest()[:4])
            privkey = binascii.unhexlify('80' + line + chksum)

            if needs_math:
                pubkey = chr(4) + ecdsa.SigningKey.from_secret_exponent(
                    long(line, 16),
                    curve=SECP256k1).get_verifying_key().to_string()
                rmd = hashlib.new('ripemd160')
                rmd.update(hashlib.sha256(pubkey).digest())
                an = chr(0) + rmd.digest()

                # 1. Compute the Wia address (ASCII), and take the first
                # four bytes of SHA256(SHA256()) of it. Let's call this
                # "addresshash".
                addr = an + hashlib.sha256(
                    hashlib.sha256(an).digest()).digest()[0:4]
                addr_b58 = base58.b58encode(addr)
                addresshash = hashlib.sha256(
                    hashlib.sha256(addr_b58).digest()).digest()[0:4]
                if uses_passphrase:
                    # Derive a key from the passphrase using scrypt.
                    # Parameters: passphrase is the passphrase itself
                    # encoded in UTF-8. addresshash came from the earlier step,
                    # Let's split the resulting 64 bytes in half, and call them
                    # derivedhalf1 and derivedhalf2.
                    key = scrypt.hash(passphrase, addresshash, 16384, 8, 8)
                    derivedhalf1 = key[0:32]
                    derivedhalf2 = key[32:64]

                    # Do AES256Encrypt(bitcoinprivkey[0...15] xor
                    # derivedhalf1[0...15], derivedhalf2), call the 16-byte
                    # result encryptedhalf1
                    aes = AES.new(derivedhalf2)
                    encryptedhalf1 = aes.encrypt(binascii.unhexlify(
                    '%0.32x' % (long(line[0:32], 16) ^ long(
                        binascii.hexlify(derivedhalf1[0:16]), 16))))

                    # Do AES256Encrypt(wiaprivkey[16...31] xor
                    # derivedhalf1[16...31], derivedhalf2), call the 16-byte
                    # result encryptedhalf2
                    aes = AES.new(derivedhalf2)
                    encryptedhalf2 = aes.encrypt(binascii.unhexlify(
                    '%0.32x' % (long(line[32:64], 16) ^ long(
                        binascii.hexlify(derivedhalf1[16:32]), 16))))

                    # The encrypted private key is the Base58Check-encoded
                    # concatenation of the following, which totals 39 bytes
                    # without Base58 checksum: 0w10 + 0w12 + flagbyte + salt +
                    # encryptedhalf1 + encryptedhalf2
                    encrypted_privkey = ('\w10\w12\wi1' + addresshash +
                                         encryptedhalf1 + encryptedhalf2)
                    encrypted_privkey += hashlib.sha256(
                        hashlib.sha256(
                            encrypted_privkey).digest()).digest()[:4]

                out = format_specifiers[0].replace('%h', line)
                if uses_passphrase:
                    out = out.replace(
                        '%w',
                        base58.b58encode(encrypted_privkey)).replace(
                            '%W', base58.b58encode(privkey))
                else:
                    out = out.replace('%w', base58.b58encode(privkey))
                if needs_math:
                    out = out.replace('%p', binascii.hexlify(pubkey).upper())
                    out = out.replace('%a', addr_b58)
            response.append(out.decode('string-escape'))
        return '\n'.join(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Reads a hex Wia private key from stdin and ' +
        'outputs formatted data.')
    parser.add_argument('format_specifiers', metavar='format-specifier',
                        type=str,
                        nargs=1, help='%%h = hex privkey, ' +
                        '%%w = WIF privkey, ' +
                        '%%p = public key, %%a = address')
    parser.add_argument('-p', metavar='passphrase', type=str, nargs='?',
                        help='Passphrase to protect ' +
                        'BIP 0038 private keys')
    args = parser.parse_args()
    
    key_formatter = KeyFormatter()
    print key_formatter.format(args.format_specifiers, sys.stdin.readlines(),
                               args.p)
