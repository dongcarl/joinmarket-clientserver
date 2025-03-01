
# Descriptor checksum calculation code taken from
# https://github.com/bitcoin-core/HWI/blob/master/hwilib/descriptor.py

def poly_mod(c: int, val: int) -> int:
    """
    :meta private:
    Function to compute modulo over the polynomial used for descriptor checksums
    From: https://github.com/bitcoin/bitcoin/blob/master/src/script/descriptor.cpp
    """
    c0 = c >> 35
    c = ((c & 0x7ffffffff) << 5) ^ val
    if (c0 & 1):
        c ^= 0xf5dee51989
    if (c0 & 2):
        c ^= 0xa9fdca3312
    if (c0 & 4):
        c ^= 0x1bab10e32d
    if (c0 & 8):
        c ^= 0x3706b1677a
    if (c0 & 16):
        c ^= 0x644d626ffd
    return c


def descriptor_checksum(desc: str) -> str:
    """
    Compute the checksum for a descriptor
    :param desc: The descriptor string to compute a checksum for
    :return: A checksum
    """
    INPUT_CHARSET = "0123456789()[],'/*abcdefgh@:$%{}IJKLMNOPQRSTUVWXYZ&+-.;<=>?!^_|~ijklmnopqrstuvwxyzABCDEFGH`#\"\\ "
    CHECKSUM_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

    c = 1
    cls = 0
    clscount = 0
    for ch in desc:
        pos = INPUT_CHARSET.find(ch)
        if pos == -1:
            return ""
        c = poly_mod(c, pos & 31)
        cls = cls * 3 + (pos >> 5)
        clscount += 1
        if clscount == 3:
            c = poly_mod(c, cls)
            cls = 0
            clscount = 0
    if clscount > 0:
        c = poly_mod(c, cls)
    for j in range(0, 8):
        c = poly_mod(c, 0)
    c ^= 1

    ret = [''] * 8
    for j in range(0, 8):
        ret[j] = CHECKSUM_CHARSET[(c >> (5 * (7 - j))) & 31]
    return ''.join(ret)


def add_checksum(desc: str) -> str:
    """
    Compute and attach the checksum for a descriptor
    :param desc: The descriptor string to add a checksum to
    :return: Descriptor with checksum
    """
    return desc + "#" + descriptor_checksum(desc)


def get_address_descriptor(address: str) -> str:
    return add_checksum("addr({})".format(address))


def get_xpub_descriptor(xpub_key: str, address_type: str) -> str:
    if address_type == "p2pkh":
        function = "pkh"
    elif address_type == "p2sh-p2wpkh" or address_type == "p2wpkh":
        function = "wpkh"
    else:
        raise Exception("Unsupported address type {}".format(address_type))
    descriptor = "{}({}/*)".format(function, xpub_key)
    if address_type == "p2sh-p2wpkh":
        descriptor = "sh({})".format(descriptor)
    return add_checksum(descriptor)

