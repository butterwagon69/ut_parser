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
    / BitStruct(
        "is_array" / Flag, "size" / BitsInteger(3), "type" / property_types,
    ),
    "name_index"
    / IfThenElse(this.info.type == property_types.struct, idx, Computed(0)),
    "name" / Computed(lambda x: x._root.names[x.name_index].name),
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


type_switch = Switch(
    this.property_info.type,
    {
        property_types.bool: Struct(
            "value" / Computed(lambda x: x._.info.is_array),
        ),
        property_types.byte: Struct(
            "value" / Bytes(this._.property_info.size)
        ),
    }
)

ut_property = Struct(
    "name_index" / idx,
    "name" / Computed(lambda x: x._root.names[x.name_index].name),
    "more" / Computed(this.name_index != 0),
    "data"
    / If(
        this.more,
        Struct(
            "property_info" / property_info,
            "data" / IfThenElse(
                lambda x: x.property_info.info.type == property_types.bool,
                Computed(this.property_info.info.is_array),
                Bytes(this.property_info.size)
            )
        ),
    ),
)
