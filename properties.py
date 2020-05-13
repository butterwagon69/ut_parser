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
from module_types import byte, idx, word, dword, prop_idx
from enums import property_types


ut_property = Struct(
    "name_index" / idx,
    Probe(),
    "name" / Computed(lambda x: x._root.names[x.name_index].name),
    "more" / Computed(this.name_index != 0),
    "data" / If(
        this.more,
        Struct(
            "info" / BitStruct(
                "is_array" / Flag,
                "size" / BitsInteger(3),
                "type" / property_types,
            ),
            "name_index" / IfThenElse(
                this.info.type == property_types.struct,
                idx,
                Computed(0)
            ),
            "name"
            / Computed(
                lambda x: x._root.names[
                    x.name_index
                ].name
            ),
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
            "index" / IfThenElse(
                this.info.is_array & (this.info.type != property_types.bool),
                prop_idx,
                Computed(-1)
            ),
            "data" / Bytes(this.size),
        )

    ),
    Probe(),
    # "data" / IfThenElse(
    #     this.info.type == property_types.bool,
    #     Computed(this.info.is_array),
    #     IfThenElse(
    #         (this.info.type == property_types.byte
    #         | this.info.type == property_types.int
    #         | this.info.type == property_types.float
    #         | this.info.type == property_types.object
    #         | this.info.type == property_types.cls
    #         | this.info.type == property_types.string
    #         | this.info.type == property_types.str
    #         | this.info.type == property_types.array
    #         | this.info.type == property_types.struct
    #         | this.info.type == property_types.vector
    #         | this.info.type == property_types.rotator
    #         | this.info.type == property_types.map
    #         | this.info.type == property_types.fixed_array),
    #         byte[this.info.size],
    #         byte[this.info.size]
    #     )
    # )
)
