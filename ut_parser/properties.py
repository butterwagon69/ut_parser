from construct import (
    Struct,
    this,
    BitStruct,
    Flag,
    BitsInteger,
    Switch,
    IfThenElse,
    Bytes,
    PascalString,
    Byte,
)
from .module_types import (
    byte,
    idx,
    word,
    dword,
    prop_idx,
    If,
    Computed,
    float,
)
from .enums import property_types

from .ut_structs import (
    color,
    vector,
    pointregion,
    rotator,
    scale,
    plane,
    sphere,
)

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

_struct_types = {
    "Color": color,
    "Vector": vector,
    "PointRegion": pointregion,
    "Rotator": rotator,
    "Scale": scale,
    "Plane": plane,
    "Sphere": sphere,
}

_raw_type = Bytes(this.property_info.size)

_string_type = PascalString(idx, "utf8")  # only for version < 120

value_switch = Switch(
    this.property_info.info.type,
    {
        property_types.name_: Struct(
            "index" / idx, "value" / Computed(lambda x: x._root.names[x.index].name),
        ),
        property_types.none: Computed(0),
        property_types.byte: Byte,
        property_types.int: dword,
        property_types.bool: Computed(this.property_info.info.is_array),
        property_types.float: float,
        property_types.object: Struct(
            "index" / idx,
            "value" / Computed(lambda x: x._root.export_headers[x.index - 1]),
        ),
        property_types.string: _string_type,
        property_types.cls: Struct(
            "index" / idx,
            "value" / Computed(lambda x: get_object_path(x, -1, x.index)),
        ),
        property_types.array: Computed("Array"),
        property_types.struct: Switch(this.property_info.struct_name, _struct_types),
        property_types.vector: Computed("Vector"),
        property_types.rotator: Computed("Rotator"),
        property_types.str: _string_type,
        property_types.map: _raw_type,
        property_types.fixed_array: _raw_type,
        property_types.buffer: _raw_type,
        property_types.word: word,
    },
)

ut_property = Struct(
    "name_index" / idx,
    "prop_name" / Computed(lambda x: x._root.names[x.name_index].name),
    "more" / Computed(lambda x: x.prop_name != "None"),
    "value"
    / If(this.more, Struct("property_info" / property_info, "data" / value_switch,),),
)
