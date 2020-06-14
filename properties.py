from construct import (
    Struct,
    Computed,
    If,
    this,
    BitStruct,
    Flag,
    BitsInteger,
    Probe,
    Switch,
    IfThenElse,
    Bytes,
    PascalString,
    Byte,
)
from module_types import (
    byte,
    idx,
    word,
    dword,
    prop_idx,
    If,
    Computed,
    float,
    sized_ascii_z,
)
from enums import property_types

property_info = Struct(
    "info"
    / BitStruct("is_array" / Flag, "size" / BitsInteger(3), "type" / property_types,),
    "struct_index"
    / IfThenElse(this.info.type == property_types.struct, idx, Computed(0)),
    "struct_name" / Computed(lambda x: x._root.names[x.struct_index].name),
    "size"
    / Switch(
        this.info.size,
        {
            0: Computed(1),
            1: Computed(2),
            2: Computed(4),
            3: Computed(12),
            4: Computed(16),
            5: byte,
            6: word,
            7: dword,
        },
    ),
    "index"
    / IfThenElse(
        this.info.is_array & (this.info.type != property_types.bool),
        prop_idx,
        Computed(-1),
    ),
)
_raw_type = Struct("value" / Bytes(this._.property_info.size))
_string_type = Struct("value" / PascalString(idx, "utf8"))  # only for version < 120
value_switch = Switch(
    this._.property_info.info.type,
    {
        property_types.none: Struct("value" / Computed(0)),
        property_types.byte: Computed("Byte"),
        property_types.int: Struct("value" / dword),
        property_types.bool: Struct(
            "raw" / Byte, "value" / Computed(lambda x: bool(x.raw))
        ),
        property_types.float: Struct("value" / float),
        property_types.object: Struct(
            "index" / idx, "value" / Computed(this._root.export_headers[this.idx - 1])
        ),
        property_types.name: Struct(
            "index" / idx, "value" / Computed(this._root.names[this.index].name)
        ),
        property_types.string: _string_type,
        property_types.cls: Struct(
            "index" / idx,
            "value" / Computed(lambda x: get_object_path(x, -1, x.index)),
        ),
        property_types.array: Computed("Array"),
        property_types.struct: Computed("Struct"),
        property_types.vector: Computed("Vector"),
        property_types.rotator: Computed("Rotator"),
        property_types.str: _string_type,
        property_types.map: _raw_type,
        property_types.fixed_array: _raw_type,
        property_types.buffer: _raw_type,
        property_types.word: Struct("value" / word),
    },
)

ut_property = Struct(
    "name_index" / idx,
    "prop_name" / Computed(lambda x: x._root.names[x.name_index].name),
    "more" / Computed(this.name_index != 0),
    "value"
    / If(
        this.more,
        Struct(
            "property_info" / property_info,
            "data"
            / IfThenElse(
                lambda x: x.property_info.info.type == property_types.bool,
                Computed(this.property_info.info.is_array),
                Bytes(this.property_info.size),
            ),
        ),
    ),
)
