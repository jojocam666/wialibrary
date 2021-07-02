# -*- coding: utf-8 -*-
#    VALUE class - representing cryptocurrency values


from wialib.networks import *
from wialib.config.config import NETWORK_DENOMINATORS


def value_to_lio(value, network=None):
    """
    Convert Value object or value string to smallest denominator amount as integer

    :param value: Value object, value string as accepted by Value class or numeric value amount
    :type value: str, int, float, Value
    :param network: Specify network to validate value string
    :type network: str, Network

    :return int:
    """
    if isinstance(value, str):
        value = Value(value)
    if isinstance(value, Value):
        if network and value.network != network:
            raise ValueError("Value uses different network (%s) then supplied network: %s" % (value.network.name, network))
        value = value.value_sat
    return value


class Value:
    """
    Class to represent and convert cryptocurrency values
    """

    @classmethod
    def from_lio(cls, value, denominator=None, network=DEFAULT_NETWORK):
        """
        Initialize Value class with smallest denominator as input. Such as represented in script and transactions cryptocurrency values.

        :param value: Amount of lio's / smallest denominator for this network
        :type value: int
        :param denominator: Denominator as integer or string. Such as 0.001 or m for milli, 1000 or k for kilo, etc. See NETWORK_DENOMINATORS for list of available denominator symbols.
        :type denominator: int, float, str
        :param network: Specify network if not supplied already in the value string
        :type network: str, Network

        :return Value:
        """
        if not isinstance(network, Network):
            network = Network(network)
        if denominator is None:
            denominator = network.denominator
        else:
            if isinstance(denominator, str):
                dens = [den for den, symb in NETWORK_DENOMINATORS.items() if symb == denominator]
                if dens:
                    denominator = dens[0]
            value = value * (network.denominator / denominator)
        return cls(value or 0, denominator, network)

    def __init__(self, value, denominator=None, network=DEFAULT_NETWORK):
        """
        Create a new Value class. Specify value as integer, float or string. If a string is provided
        the amount, denominator and currency will be extracted if provided

        Examples: Initialize value class
        >>> Value(10)
        Value(value=10.00000000000000, denominator=1.00000000, network='wia')

        >>> Value('15 mWIA')
        Value(value=0.01500000000000, denominator=0.00100000, network='wia')

        >>> Value('10 lio')
        Value(value=0.00000010000000, denominator=0.00000001, network='wia')

        >>> Value(500, 0.001)
        Value(value=0.50000000000000, denominator=0.00100000, network='bitcoin')
        
        >>> Value(500, 'm')
        Value(value=0.50000000000000, denominator=0.00100000, network='wia')

        >>> Value(500, 0.001)
        Value(value=0.50000000000000, denominator=0.00100000, network='bitcoin')

        All frequently used arithmetic, comparision and logical operators can be used on the Value object. So you can compare Value object, add them together, divide or multiply them, etc.

        Values need to use the same network / currency if you work with multiple Value objects. I.e. Value('1 BTC') + Value('1 WIA') raises an error.

        # Examples: Value operators
        >>> Value('500 lio') == Value('5000 sat')  # 1 lio equals 10 Satoshi's
        True

        >>> Value('1 wia') > Value('2 wia')
        False

        
        >>> Value('0.002 BTC') + 0.02
        Value(value=0.02200000000000, denominator=1.00000000, network='bitcoin')

        The Value class can be represented in several formats.

        # Examples: Format Value class
        >>> int(Value("10.1 BTC"))
        10

        >>> float(Value("10.1 BTC"))
        10.1

        >>> round(Value("10.123 BTC"), 2).str()
        '10.12000000 BTC'

        >>> hex(Value("10.1 BTC"))
        '0x3c336080'

        :param value: Value as integer, float or string. Numeric values must be supllied in smallest denominator such as Satoshi's. String values must be in the format: <value> [<denominator>][<currency_symbol>]
        :type value: int, float, str
        :param denominator: Denominator as integer or string. Such as 0.001 or m for milli, 1000 or k for kilo, etc. See NETWORK_DENOMINATORS for list of available denominator symbols.
        :type denominator: int, float, str
        :param network: Specify network if not supplied already in the value string
        :type network: str, Network

        """
        self.network = network
        if not isinstance(network, Network):
            self.network = Network(network)
        if isinstance(denominator, str):
            dens = [den for den, symb in NETWORK_DENOMINATORS.items() if symb == denominator]
            if dens:
                denominator = dens[0]
        den_arg = denominator

        if isinstance(value, str):
            value_items = value.split()
            value = value_items[0]
            cur_code = self.network.currency_code
            den_input = 1
            if len(value_items) > 1:
                cur_code = value_items[1]
            network_names = [n for n in NETWORK_DEFINITIONS if
                             NETWORK_DEFINITIONS[n]['currency_code'].upper() == cur_code.upper()]
            if network_names:
                self.network = Network(network_names[0])
                self.currency = cur_code
            else:
                for den, symb in NETWORK_DENOMINATORS.items():
                    if len(symb) and cur_code[:len(symb)] == symb:
                        cur_code = cur_code[len(symb):]
                        network_names = [n for n in NETWORK_DEFINITIONS if
                                         NETWORK_DEFINITIONS[n]['currency_code'].upper() == cur_code.upper()]
                        if network_names:
                            self.network = Network(network_names[0])
                            self.currency = cur_code
                        elif len(cur_code):
                            raise ValueError("Currency symbol not recognised")
                        den_input = den
                        break
            self.value = float(value) * den_input
            self.denominator = den_input if den_arg is None else den_arg
        else:
            self.denominator = den_arg or 1.0
            self.value = float(value) * self.denominator

    def __str__(self):
        return self.str()

    def __repr__(self):
        return "Value(value=%.14f, denominator=%.8f, network='%s')" % \
               (self.value, self.denominator, self.network.name)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        if self.value > self.network.denominator:
            return round(self.value, -int(math.log10(self.network.denominator)))
        else:
            return self.value

    def __lt__(self, other):
        if self.network != other.network:
            raise ValueError("Cannot compare values from different networks")
        return self.value < other.value

    def __le__(self, other):
        if self.network != other.network:
            raise ValueError("Cannot compare values from different networks")
        return self.value <= other.value

    def __eq__(self, other):
        if isinstance(other, Value):
            if self.network != other.network:
                raise ValueError("Cannot compare values from different networks")
            return self.value == other.value
        else:
            other = Value(other)
            return self.value == other.value and self.network == other.network

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        if self.network != other.network:
            raise ValueError("Cannot compare values from different networks")
        return self.value >= other.value

    def __gt__(self, other):
        if self.network != other.network:
            raise ValueError("Cannot compare values from different networks")
        return self.value > other.value

    def __add__(self, other):
        if isinstance(other, Value):
            if self.network != other.network:
                raise ValueError("Cannot calculate with values from different networks")
            other = other.value
        return Value((self.value + other) / self.denominator, self.denominator, self.network)

    def __iadd__(self, other):
        if isinstance(other, Value):
            if self.network != other.network:
                raise ValueError("Cannot calculate with values from different networks")
            other = other.value
        return Value((self.value + other) / self.denominator, self.denominator, self.network)

    def __isub__(self, other):
        if isinstance(other, Value):
            if self.network != other.network:
                raise ValueError("Cannot calculate with values from different networks")
            other = other.value
        return Value((self.value - other) / self.denominator, self.denominator, self.network)

    def __sub__(self, other):
        if isinstance(other, Value):
            if self.network != other.network:
                raise ValueError("Cannot calculate with values from different networks")
            other = other.value
        return Value((self.value - other) / self.denominator, self.denominator, self.network)

    def __mul__(self, other):
        return Value((self.value * other) / self.denominator, self.denominator, self.network)

    def __truediv__(self, other):
        return Value((self.value / other) / self.denominator, self.denominator, self.network)

    def __floordiv__(self, other):
        return Value(((self.value / self.denominator) // other), self.denominator, self.network)

    def __round__(self, n=0):
        val = round(self.value / self.denominator, n) * self.denominator
        return Value(val, self.denominator, self.network)

    def __index__(self):
        return self.value_sat

    def str(self, denominator=None, decimals=None, currency_repr='code'):
        """
        Get string representation of Value with requested denominator and number of decimals.

        >>> Value(1200000, 'lio').str('m')  # milli Wia
        '12.00000 mWIA'

        >>> Value(12000.3, 'lio').str(1)  # Use denominator = 1 for Wia
        '0.00012000 WIA'

        >>> Value(12000, 'lio').str('auto')
        '120.00 µWIA'

        >>> Value(0.005).str('m')
        '5.00000 mWIA'

        >>> Value(12000, 'lio').str('auto', decimals=0)
        '120 µWIA'


        >>> Value('2100000000').str('auto')
        '2.10000000 GWIA'

        >>> Value('1.5 WIA').str(currency_repr='symbol')
        '1.50000000 W'

        >>> Value('1.5 WIA').str(currency_repr='name')
        '1.50000000 wias'

        :param denominator: Denominator as integer or string. Such as 0.001 or m for milli, 1000 or k for kilo, etc. See NETWORK_DENOMINATORS for list of available denominator symbols. If not provided the default self.denominator value is used. Use value 'auto' to automatically determine best denominator for human readability.
        :type denominator: int, float, str
        :param decimals: Number of decimals to use
        :type decimals: float
        :param currency_repr: Representation of currency. I.e. code: WIA, name: wias, symbol: W
        :type currency_repr: str

        :return str:
        """
        if denominator is None:
            denominator = self.denominator
        elif denominator == 'auto':
            # First try denominator=1 and smallest denominator (lio)
            if 0.001 <= self.value < 1000:
                denominator = 1
            elif 1 <= self.value / self.network.denominator < 1000:
                denominator = self.network.denominator
            else:  # Try other frequently used denominators
                for den, symb in NETWORK_DENOMINATORS.items():
                    if symb in ['n', 'fin', 'da', 'c', 'd', 'h']:
                        continue
                    if 1 <= self.value / den < 1000:
                        denominator = den
        elif isinstance(denominator, str):
            dens = [den for den, symb in NETWORK_DENOMINATORS.items() if symb == denominator[:len(symb)] and len(symb)]
            if len(dens) > 1:
                dens = [den for den, symb in NETWORK_DENOMINATORS.items() if symb == denominator]
            if dens:
                denominator = dens[0]
        if denominator in NETWORK_DENOMINATORS:
            den_symb = NETWORK_DENOMINATORS[denominator]
        else:
            raise ValueError("Denominator not found in NETWORK_DENOMINATORS definition")

        if decimals is None:
            decimals = -int(math.log10(self.network.denominator / denominator))
            if decimals > 8:
                decimals = 8
        if decimals < 0:
            decimals = 0
        balance = round(self.value / denominator, decimals)
        cur_code = self.network.currency_code
        if currency_repr == 'symbol':
            cur_code = self.network.currency_symbol
        if currency_repr == 'name':
            cur_code = self.network.currency_name_plural
        if 'lio' in den_symb and self.network.name == 'wia':
            cur_code = ''
        return ("%%.%df %%s%%s" % decimals) % (balance, den_symb, cur_code)

    def str_unit(self, decimals=None, currency_repr='code'):
        """
        String representation of this Value. Wrapper for the :func:`str` method, but always uses 1 as denominator, meaning main denominator such as BTC, LTC.

        >>> Value('12000 lio').str_unit()
        '0.00012000 WIA'

        :param decimals: Number of decimals to use
        :type decimals: float
        :param currency_repr: Representation of currency. I.e. code: WIA, name: Wia, symbol: W
        :type currency_repr: str
        :return str:
        """
        return self.str(1, decimals, currency_repr)

    def str_auto(self, decimals=None, currency_repr='code'):
        """
        String representation of this Value. Wrapper for the :func:`str` method, but automatically determines the denominator depending on the value.

        >>> Value('0.0000012 WIA').str_auto()
        '120 lio'

        >>> Value('0.0005 WIA').str_auto()
        '500.00 µWIA'

        :param decimals: Number of decimals to use
        :type decimals: float
        :param currency_repr: Representation of currency. I.e. code: WIA, name: Wia, symbol: W
        :type currency_repr: str
        :return str:
        """

        return self.str('auto', decimals, currency_repr)

    @property
    def value_lio(self):
        """
        Value in smallest denominator, i.e. Lio for the Wia network

        :return int:
        """
        return round(self.value / self.network.denominator)

    def to_bytes(self, length=8, byteorder='little'):
        """
        Representation of value_sat (value in smallest denominator: lio's) as bytes string. Used for script or transaction serialization.

        >>> Value('1 lio').to_bytes()
        b'\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00'

        :param length: Length of bytes string to return, default is 8 bytes
        :type length: int
        :param byteorder: Order of bytes: little or big endian. Default is 'little'
        :type byteorder: str

        :return bytes:
        """
        return self.value_lio.to_bytes(length, byteorder)

    def to_hex(self, length=16, byteorder='little'):
        """
        Representation of value_sat (value in smallest denominator: lio's) as hexadecimal string.

        >>> Value('15 lio').to_hex()
        '0f00000000000000'

        :param length: Length of hexadecimal string to return, default is 16 characters
        :type length: int
        :param byteorder: Order of bytes: little or big endian. Default is 'little'
        :type byteorder: str
        :return:
        """
        return self.value_lio.to_bytes(length // 2, byteorder).hex()
