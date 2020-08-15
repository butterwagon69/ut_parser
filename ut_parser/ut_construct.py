from construct import (
    Flag,
    Enum,
    this,
    Struct,
    Sequence,
    Pointer,
    Construct,
    stream_read,
    stream_write,
    IntegerError,
    If,
    IfThenElse,
    Bytes,
    Const,
    BytesInteger,
    Computed,
    HexDump,
    Index,
    Enum,
    Probe,
    StringEncoded,
    Prefixed,
    GreedyBytes,
    NullTerminated,
    encodingunit,
    FlagsEnum,
    Switch,
    Int32sl,
    RawCopy,
)
import construct
from construct.lib import byte2int, integertypes, int2byte

from .module_types import idx, word, dword, qword, uuid, string, ascii_z, Computed, If
from .enums import object_flags, package_flags
from .ut_objects import ut_object_map


def get_object_path(path, limit, index):
    name_table = path._root.names
    import_table = path._root.import_objs
    export_table = path._root.export_headers
    result = ""
    s = ""
    while limit != 0:
        if index == 0:
            break
        elif index < 0:
            if abs(index) <= len(import_table):
                i = import_table[abs(index) - 1]
                s = name_table[i.object_index].name + "."
                index = 1 if index == i.package_index else i.package_index
            else:
                s, result, limit = "", "", 1
        elif index > 0:
            if index <= len(export_table):
                e = export_table[index - 1]
                s = name_table[e.object_index].name + "."
                index = 1 if index == e.group_index else e.group_index
            else:
                s, result, limit = "", "", 1
        result = s + result
        limit -= 1
    return result.rstrip(".")


export_header = Struct(
    "exported_index" / Index,
    "cls_index" / idx,
    "sup_index" / idx,
    "group_index" / dword,
    "object_index" / idx,
    "flags" / object_flags,
    "serial_size" / idx,
    "serial_offset" / If(this.serial_size, idx),
)


export_object = Struct(
    *export_header.subcons,
    "cls_name" / Computed(lambda x: get_object_path(x, 1, x.cls_index)),
    "obj_name" / Computed(lambda x: x._root.names[x.object_index].name),
    "group_name" / Computed(lambda x: get_object_path(x, -1, x.group_index)),
    "sup_name" / Computed(lambda x: get_object_path(x, -1, x.sup_index)),
    "object"
    / If(
        this.serial_size,
        Pointer(
            this.serial_offset,
            Switch(
                lambda x: str(x.cls_name).lower(),
                ut_object_map,
                default=HexDump(Bytes(this.serial_size)),
            ),
        ),
    ),
)


header = Struct(
    "lw" / Const(0x9E2A83C1, dword),
    "version" / word,
    "licensee_mode" / word,
    "flags" / package_flags,
    "name_count" / dword,
    "name_offset" / dword,
    "export_count" / dword,
    "export_offset" / dword,
    "import_count" / dword,
    "import_offset" / dword,
    "uuid" / uuid,
    "generation_info_count" / dword,
)

name = Struct(
    "name" / IfThenElse(this._root.header.version >= 64, string, ascii_z),
    "pointer" / dword,
)


import_object = Struct(
    "class_package_index" / idx,
    "class_index" / idx,
    "package_index" / Int32sl,
    "object_index" / idx,
    "object_name" / Computed(lambda x: x._root.names[x.object_index]),
    "class_package_name" / Computed(lambda x: x._root.names[x.class_package_index]),
    "class_name" / Computed(lambda x: x._root.names[x.class_index]),
    # TODO: use "get_object_path"
    # "package_name" / Computed(lambda x: x._.names[x.package_index])
)

package = Struct(
    "header" / header,
    "names" / (Pointer(this.header.name_offset, name[this.header.name_count])),
    "import_objs"
    / (Pointer(this.header.import_offset, import_object[this.header.import_count])),
    "export_headers"
    / Pointer(this.header.export_offset, export_header[this.header.export_count],),
    "export_objects"
    / (Pointer(this.header.export_offset, export_object[this.header.export_count])),
)
