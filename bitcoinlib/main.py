# -*- coding: utf-8 -*-
#
#    
#    MAIN - Load configs, initialize logging and database
#   
# Do not remove any of the imports below, used by other files
import os
import sys
import functools
import logging
from logging.handlers import RotatingFileHandler
from wialib.config.config import *


# Initialize logging
logger = logging.getLogger('wialib')
logger.setLevel(LOGLEVEL)

if ENABLE_WIALIB_LOGGING:
    handler = RotatingFileHandler(str(WIL_LOG_FILE), maxBytes=100 * 1024 * 1024, backupCount=2)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(LOGLEVEL)
    logger.addHandler(handler)

    _logger = logging.getLogger(__name__)
    logger.info('WELCOME TO WIALIB - CRYPTOCURRENCY LIBRARY')
    logger.info('Version: %s' % WIALIB_VERSION)
    logger.info('Logger name: %s' % logging.__name__)
    logger.info('Read config from: %s' % WIL_CONFIG_FILE)
    logger.info('Directory databases: %s' % WIL_DATABASE_DIR)
    logger.info('Default database: %s' % DEFAULT_DATABASE)
    logger.info('Logging to: %s' % WIL_LOG_FILE)
    logger.info('Directory for data files: %s' % WIL_DATA_DIR)


def script_type_default(witness_type=None, multisig=False, locking_script=False):
    """
    Determine default script type for provided witness type and key type combination used in this library.

    >>> script_type_default('segwit', locking_script=True)
    'p2wpkh'

    :param witness_type: Witness type used: standard, p2sh-segwit or segwit
    :type witness_type: str
    :param multisig: Multi-signature key or not, default is False
    :type multisig: bool
    :param locking_script: Limit search to locking_script. Specify False for locking scripts and True for unlocking scripts
    :type locking_script: bool

    :return str: Default script type
    """

    if not witness_type:
        return None
    if witness_type == 'legacy' and not multisig:
        return 'p2pkh' if locking_script else 'sig_pubkey'
    elif witness_type == 'legacy' and multisig:
        return 'p2sh' if locking_script else 'p2sh_multisig'
    elif witness_type == 'segwit' and not multisig:
        return 'p2wpkh' if locking_script else 'sig_pubkey'
    elif witness_type == 'segwit' and multisig:
        return 'p2wsh' if locking_script else 'p2sh_multisig'
    elif witness_type == 'p2sh-segwit' and not multisig:
        return 'p2sh' if locking_script else 'p2sh_p2wpkh'
    elif witness_type == 'p2sh-segwit' and multisig:
        return 'p2sh' if locking_script else 'p2sh_p2wsh'
    else:
        raise ValueError("Wallet and key type combination not supported: %s / %s" % (witness_type, multisig))


def get_encoding_from_witness(witness_type=None):
    """
    Derive address encoding (base58 or bech32) from transaction witness type.

    Returns 'base58' for legacy and p2sh-segwit witness type and 'bech32' for segwit

    :param witness_type: Witness type: legacy, p2sh-segwit or segwit
    :type witness_type: str

    :return str:
    """

    if witness_type == 'segwit':
        return 'bech32'
    elif witness_type in [None, 'legacy', 'p2sh-segwit']:
        return 'base58'
    else:
        raise ValueError("Unknown witness type %s" % witness_type)


def deprecated(func):
    """
    This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        logging.warning("Call to deprecated function {}.".format(func.__name__))
        return func(*args, **kwargs)
    return new_func
