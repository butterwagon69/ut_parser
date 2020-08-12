import construct
from functools import partial

word = construct.Int16ul
dword = construct.Int32ul
byte = construct.Int8ul
qword = construct.Int64ul
float = construct.Float32l
single = construct.Float32l
integer = construct.Int32ul


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
            bits = construct.byte2int(construct.stream_read(stream, 1, path))
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
            construct.stream_write(stream, construct.int2byte(byte), 1, path)
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
        index_b = construct.byte2int(construct.stream_read(stream, 1, path))
        morethan1 = index_b & 0x80
        morethan2 = index_b & 0x40
        if not morethan1:
            return index_b
        elif morethan1 and not morethan2:
            index_c = construct.byte2int(construct.stream_read(stream, 1, path))
            return ((index_b & 0x7F) << 8) | index_c
        else:
            res = (index_b & 0x3F) << 24
            for i in range(3):
                num = construct.byte2int(construct.stream_read(stream, 1, path))
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
            construct.stream_write(stream, construct.int2byte(to_write), 1, path)
        elif to_write <= 0x7FFF:
            construct.stream_write(
                stream, construct.int2byte(to_write >> 8 | 0x80), 1, path
            )
            construct.stream_write(stream, construct.int2byte(to_write & 0xFF), 1, path)
        else:
            construct.stream_write(
                stream, construct.int2byte(to_write >> 24 | 0xC0), 1, path
            )
            for i in range(3):
                construct.stream_write(
                    stream, construct.int2byte(to_write >> (2 - i) * 8 & 0xFF), 1, path
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

ascii_z = construct.StringEncoded(
    construct.NullTerminated(
        construct.GreedyBytes, term=construct.encodingunit("ascii")
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


class If(construct.IfThenElse):
    r"""
    If-then conditional construct.

    This implementation will build if the condition cannot be evaluated
    provided that subcon is passed.

    Parsing evaluates condition, if True then subcon is parsed, otherwise just returns None. Building also evaluates condition, if True then subcon gets build from, otherwise does nothing. Size is either same as subcon or 0, depending how condfunc evaluates.

    :param condfunc: bool or context lambda (or a truthy value)
    :param subcon: Construct instance, used if condition indicates True

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        If <--> IfThenElse(condfunc, subcon, Pass)

        >>> d = If(this.x > 0, Byte)
        >>> d.build(255, x=1)
        b'\xff'
        >>> d.build(255, x=0)
        b''
    """

    def __init__(self, condfunc, thensubcon):
        super(If, self).__init__(condfunc, thensubcon, construct.Pass)

    def _build(self, obj, stream, context, path):
        if obj is None:
            return None
        condfunc = self.condfunc
        try:
            if callable(condfunc):
                condfunc = condfunc(context)
            sc = self.thensubcon if condfunc else self.elsesubcon
            return sc._build(obj, stream, context, path)
        except KeyError:
            return self.thensubcon._build(obj, stream, context, path)


class Computed(construct.Construct):
    r"""
    Field computing a value from the context dictionary or some outer source like os.urandom or random module. Underlying byte stream is unaffected. The source can be non-deterministic.

    Parsing and Building return the value returned by the context lambda (although a constant value can also be used). Size is defined as 0 because parsing and building does not consume or produce bytes into the stream.

    :param func: context lambda or constant value

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::
        >>> d = Struct(
        ...     "width" / Byte,
        ...     "height" / Byte,
        ...     "total" / Computed(this.width * this.height),
        ... )
        >>> d.build(dict(width=4,height=5))
        b'\x04\x05'
        >>> d.parse(b"12")
        Container(width=49, height=50, total=2450)

        >>> d = Computed(7)
        >>> d.parse(b"")
        7
        >>> d = Computed(lambda ctx: 7)
        >>> d.parse(b"")
        7

        >>> import os
        >>> d = Computed(lambda ctx: os.urandom(10))
        >>> d.parse(b"")
        b'\x98\xc2\xec\x10\x07\xf5\x8e\x98\xc2\xec'
    """

    def __init__(self, func):
        super(Computed, self).__init__()
        self.func = func
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        try:
            res = self.func(context) if callable(self.func) else self.func
            return res
        except KeyError:
            return None

    def _build(self, obj, stream, context, path):
        return construct.Pass._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        return "%r" % (self.func,)
