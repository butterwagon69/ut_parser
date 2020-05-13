from construct import Enum, FlagsEnum, BitsInteger
from module_types import dword, byte, word

object_flags = FlagsEnum(
    dword,
    Transactional=1 << 0,
    Unreachable=1 << 1,
    Public=1 << 2,
    TagImp=1 << 3,
    TagExp=1 << 4,
    SourceModified=1 << 5,
    TagGarbage=1 << 6,
    Private=1 << 7,
    RF_Unk_00000100=1 << 8,
    NeedLoad=1 << 9,
    HighlightedName=1 << 10,
    InSingularFunc=1 << 11,
    Suppress=1 << 12,
    InEndState=1 << 13,
    Transient=1 << 14,
    PreLoading=1 << 15,
    LoadForClient=1 << 16,
    LoadForServer=1 << 17,
    LoadForEdit=1 << 18,
    Standalone=1 << 19,
    NotForClient=1 << 20,
    NotForServer=1 << 21,
    NotForEdit=1 << 22,
    Destroyed=1 << 23,
    NeedPostLoad=1 << 24,
    HasStack=1 << 25,
    Native=1 << 26,
    Marked=1 << 27,
    ErrorShutDown=1 << 28,
    DebugPostLoad=1 << 29,
    DebugSerialSize=1 << 30,
    DebugDestroy=1 << 31,
)

package_flags = FlagsEnum(
    dword,
    allow_download=1,
    client_optional=2,
    server_side_only=4,
    broken_links=8,
    unsecure=0x10,
    encrypted=0x20,
    need=0x8000,
)


property_types = Enum(
    BitsInteger(4),
    none=0,
    byte=1,
    int=2,
    bool=3,
    float=4,
    object=5,
    name=6,
    string=7,
    cls=8,
    array=9,
    struct=10,
    vector=11,
    rotator=12,
    str=13,
    map=14,
    fixed_array=15,
    extended_value=16,
    word=17,
)

property_flags = FlagsEnum(
    dword,
    edit=0x00000001,  # Property is user-settable in the editor.
    const=0x00000002,  # Actor's property always matches class's default actor property.
    input=0x00000004,  # Variable is writable by the input system.
    export_object=0x00000008,  # Object can be exported with actor.
    optional_parm=0x00000010,  # Optional parameter (if Param is set).
    net=0x00000020,  # Property is relevant to network replication.
    const_ref=0x00000040,  # Reference to a constant object.
    parm=0x00000080,  # Function/When call parameter.
    out_parm=0x00000100,  # Value is copied out after function call.
    skip_parm=0x00000200,  # Property is a short-circuitable evaluation function parm.
    return_parm=0x00000400,  # Return value.
    coerce_parm=0x00000800,  # Coerce args into this function parameter.
    native=0x00001000,  # Property is native: C++ code is responsible for serializing it.
    transient=0x00002000,  # Property is transient: shouldn't be saved, zero-filled at load time.
    config=0x00004000,  # Property should be loaded/saved as permanent profile.
    localized=0x00008000,  # Property should be loaded as localizable text.
    travel=0x00010000,  # Property travels across levels/servers.
    edit_const=0x00020000,  # Property is uneditable in the editor.
    global_config=0x00040000,  # Load config from base class, not subclass.
    on_demand=0x00100000,  # Object or dynamic array loaded on demand only.
    new=0x00200000,  # Automatically create inner object.
    need_ctor_link=0x00400000,  # Fields need construction/destruction.
    editor_data=0x02000000,  # property has extra data to use in editor
    edit_inline_use=0x14000000,
    edit_inline=0x04000000,
    deprecated=0x20000000,
)
