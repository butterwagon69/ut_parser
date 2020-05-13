import construct

word = construct.Int16ul
dword = construct.Int32ul
byte = construct.Int8ul
qword = construct.Int64ul
float = construct.Float32l


uuid = construct.Sequence(dword, word, word, word, construct.BytesInteger(6))


class Idx(construct.Construct):
    """
    Format for "Index" objects in Unreal Tournament 1999 packages.
    Index objects are variable length signed integers with the following structure:

    +------------------------------------+-------------------------+--------------+
    | Byte 0                             | Bytes 1-3               | Byte 4       |
    +----------+----------+--------------+----------+--------------+--------------+
    | Sign Bit | More Bit | Data Bits[6] | More Bit | Data Bits[7] | Data Bits[8] |
    +----------+----------+--------------+----------+--------------+--------------+

    If the "More" bit is 0 in any byte, that's the end of the Index. Otherwise,
    keep going. There cannot be more than 5 bytes in an Index so Byte 4 doesn't
    have a "More" bit.
    """

    lengths = {0: 6, 1: 7, 2: 7, 3: 7, 4: 8}
    negative_bit = 0x80

    @staticmethod
    def _get_data_mask(length):
        return (0xFF ^ (0xFF << length)) & 0xFF

    @staticmethod
    def _get_more_bit(length):
        return 1 << length

    def _parse(self, stream, context, path):
        result = 0
        sign = 1
        i = 0
        depth = 0
        while True:
            length = self.lengths[i]
            bits = construct.byte2int(construct.stream_read(stream, 1))
            mask = self._get_data_mask(length)
            data = bits & mask
            more = self._get_more_bit(length) & bits
            if (i == 0) and (self.negative_bit & bits):
                sign = -1
            result |= data << depth
            if not more:
                break
            i += 1
            depth += length
        return sign * result

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, construct.integertypes):
            raise construct.IntegerError("Value is not an integer")
        to_write = obj
        for i in range(5):
            byte = 0
            length = self.lengths[i]
            if i == 0:
                negative = obj < 0
                byte |= self.negative_bit * negative
                if negative:
                    to_write *= -1
            mask = self._get_data_mask(length)
            byte |= to_write & mask
            to_write >>= length
            more_bit = (to_write > 0) and self._get_more_bit(length)
            byte |= more_bit
            byte &= 0xFF
            construct.stream_write(stream, construct.int2byte(byte), 1)
            if not more_bit:
                break
        return obj


idx = Idx()


class PropIdx(construct.Construct):
    """Special index class for properties.
    Similar to the normal index but different.

    +---------+---------+
    | !1 byte | !2 byte |
    """

    def _parse(self, stream, context, path):
        index_b = construct.byte2int(construct.stream_read(stream, 1))
        morethan1 = index_b & 0x80
        morethan2 = index_b & 0x40
        if not morethan1:
            return index_b
        elif morethan1 and not morethan2:
            index_c = construct.byte2int(construct.stream_read(stream, 1))
            return ((index_b & 0x7F) << 8) | index_c
        else:
            res = (index_b & 0x3F) << 24
            for i in range(3):
                num = construct.byte2int(construct.stream_read(stream, 1))
                res |= num << (8 * (2 - i))
            return res

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, construct.integertypes):
            raise construct.IntegerError("Value is not an integer")
        if obj < 0:
            raise ValueError("Negative Numbers not supported")
        if obj > 0x3FFFFFFF:
            raise ValueError("Value too large to encode")
        to_write = obj
        if to_write <= 0x7F:
            construct.stream_write(stream, construct.int2byte(to_write), 1)
        elif to_write <= 0x7FFF:
            construct.stream_write(
                stream, construct.int2byte(to_write >> 8 | 0x80), 1
            )
            construct.stream_write(
                stream, construct.int2byte(to_write & 0xFF), 1
            )
        else:
            construct.stream_write(
                stream, construct.int2byte(to_write >> 24 | 0xC0), 1
            )
            for i in range(3):
                construct.stream_write(
                    stream,
                    construct.int2byte(to_write >> (2 - i) * 8 & 0xFF),
                    1,
                )
        return obj

prop_idx = PropIdx()

string = construct.StringEncoded(
    construct.Prefixed(
        byte,
        construct.NullTerminated(
            construct.GreedyBytes, term=construct.encodingunit("ascii")
        ),
    ),
    "ascii",
)
string._emitseq = lambda ksy, bitwise: [
    dict(id="lengthfield", type=byte._compileprimitivetype(ksy, bitwise)),
    dict(id="data", size="lengthfield", type="str", encoding="ascii"),
]
sized_ascii_z = construct.StringEncoded(
    construct.Prefixed(
        idx,
        construct.NullTerminated(
            construct.GreedyBytes, term=construct.encodingunit("ascii")
        ),
    ),
    "ascii",
)


def longstring_emitseq(ksy, bitwise):
    return [
        dict(id="lengthfield", type=idx._compileprimitivetype(ksy, bitwise)),
        dict(id="data", size="lengthfield", type="str", encoding="ascii"),
    ]


sized_ascii_z._emitseq = longstring_emitseq
sized_ascii = construct.StringEncoded(
    construct.Prefixed(idx, construct.GreedyBytes), "ascii"
)
sized_ascii._emitseq = longstring_emitseq
