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
)
from module_types import byte, idx, word, dword, prop_idx, If, Computed
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
type_name_map = Switch(
    this._.property_info.info.type,
    {
        property_types.none: Computed(""),
        property_types.byte: Computed("Byte"),
        property_types.int: Computed("Int"),
        property_types.bool: Computed("Bool"),
        property_types.float: Computed("Float"),
        property_types.object: Computed("Object"),
        property_types.name: Computed("Name"),
        property_types.string: Computed("String"),
        property_types.cls: Computed("Class"),
        property_types.array: Computed("Array"),
        property_types.struct: Computed("Struct"),
        property_types.vector: Computed("Vector"),
        property_types.rotator: Computed("Rotator"),
        property_types.str: Computed("Str"),
        property_types.map: Computed("Map"),
        property_types.fixed_array: Computed("FixedArray"),
        property_types.word: Computed("Word"),
    },
)

bytestruct = Struct("value_type_name" / type_name_map)

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
