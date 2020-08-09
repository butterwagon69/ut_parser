from construct import (
    Struct,
    If,
    this,
    Probe,
    HexDump,
    Bytes,
    RepeatUntil,
    Tell,
    Pointer,
)
from module_types import (
    byte,
    idx,
    word,
    dword,
    qword,
    float,
    sized_ascii_z,
    uuid,
    If,
    Computed,
)
import enums
from properties import ut_property
from ut_structs import (
    polygon,
    color,
    named_bone,
    motion_chunk,
    analog_track,
    url,
    bounding_box,
    bounding_sphere,
    bsp_node,
    bsp_surface,
    vector,
    f_vertex,
    zone,
    lightmap,
    leaf,
)

state_frame = Struct(
    "node" / idx,
    "statenode" / idx,
    "probemask" / qword,
    "latentaction" / dword,
    "NodeOffset" / If(this.node != 0, idx),
)

ut_object = Struct(
    "state_frame" / If(this._.flags.HasStack, state_frame),
    "property"
    / If(this._.cls_index, RepeatUntil(lambda x, lst, ctx: not x.more, ut_property)),
)

# code
field = Struct(*ut_object.subcons, "super_field" / idx, "next" / idx)

property = Struct(
    *field.subcons,
    "array_dimension" / word,
    "element_size" / word,
    "property_flags" / enums.property_flags,
    "category_index" / idx,
    "category" / Computed(lambda x: x._root.names[x.category_index].name),
    "rep_offset" / If(this.property_flags.net, word),
    "comment" / If(this.property_flags.editor_data, sized_ascii_z),
)
object_property = Struct(*property.subcons, "object" / idx,)

palette = Struct(
    *ut_object.subcons, "color_count" / idx, "colors" / color[this.color_count],
)
sound = Struct(
    *ut_object.subcons,
    "format_index" / idx,
    "next_object_exists" / dword,
    "sound_data_size" / idx,
    "sound_data" / HexDump(Bytes(this.sound_data_size)),
)
procedural_sound = Struct(
    *ut_object.subcons,
    "todo" / float,
    "base_sound" / idx,
    "pitch_modification" / float,
    "volume_modification" / float,
    "pitch_variance" / float,
    "volume_variance" / float,
)
sound_group = Struct(
    *ut_object.subcons,
    "sounds_array_size" / idx,
    "sounds" / HexDump(Bytes(this.sounds_array_size)),
)
music = Struct(
    "num_chunks" / word,
    "next_chunk" / dword,
    "data_size" / idx,
    "data" / HexDump(Bytes(this.data_size)),
)
text_buffer = Struct(
    *ut_object.subcons,
    "pos" / dword,
    "top" / dword,
    "data_size" / idx,
    "data" / HexDump(Bytes(this.data_size)),
)
font = Struct(*ut_object.subcons,)
texture = Struct(
    *ut_object.subcons,
    "mip_map_count" / byte,
    "img_data"
    / Struct(
        "pos_after" / dword,
        "block_size" / idx,
        "imgbytes" / HexDump(Bytes(this.block_size)),
        "width" / dword,
        "height" / dword,
        "widthbits" / byte,
        "heightbits" / byte,
    )[this.mip_map_count]
    # Different mipmap formats
    # Different games
    # Compression
)
scripted_texture = Struct(*ut_object.subcons,)
primitive = Struct(
    *ut_object.subcons,
    "primitive_bounding_box" / bounding_box,
    "primitive_bounding_sphere" / bounding_sphere,
)
polys = Struct(
    *ut_object.subcons,
    "num_polys" / dword,
    "poly_count" / dword,
    "polygons" / polygon[this.poly_count],
)
brush = Struct(*ut_object.subcons,)  # done
level_base = Struct(
    *ut_object.subcons, "size" / dword, "actors" / idx[this.size], "url" / url
)
animation = Struct(
    *ut_object.subcons,
    "num_ref_bones" / idx,
    "ref_bones" / named_bone[this.num_ref_bones],
    "num_moves" / idx,
    "motion_chunks" / motion_chunk[this.num_moves],
    "num_anims" / idx,
    "anim_seqs" / analog_track[this.num_anims],
)
package_check_info = Struct(
    *ut_object.subcons,
    "package_md5" / sized_ascii_z,
    "num_md5s" / idx,
    "md5s" / sized_ascii_z,
    "unk1" / dword,
    "unk2" / dword,
)


struct = Struct(
    *field.subcons,
    "script_text_index" / idx,
    "children_index" / idx,
    "friendly_name_index" / idx,
    "friendly_name" / Computed(lambda x: x._root.names[x.friendly_name_index].name),
    "line" / dword,
    "text_pos" / dword,
    "script_size" / dword,
)

state = Struct(
    *struct.subcons,
    "probe_mask" / qword,
    "ignore_mask" / qword,
    "label_table_offset" / word,
    "state_flags" / dword,
)

class_ = Struct(
    *state.subcons,
    "class_flags" / dword,
    "class_uuid" / uuid,
    "dependencies_array_size" / idx,
    "dependencies"
    / Struct("class" / idx, "deep" / dword, "crc" / dword)[
        this.dependencies_array_size
    ],
    "package_import_count" / idx,
    "package_imports" / idx[this.package_import_count],
    "class_within" / idx,
    "config_name" / idx,
    "properties" / RepeatUntil(lambda x, lst, ctx: not x.more, ut_property),
)

model = Struct(
    *primitive.subcons,
    "num_vectors" / idx,
    "vectors" / vector[this.num_vectors],
    "num_points" / idx,
    "points" / vector[this.num_points],
    "num_nodes" / idx,
    "nodes" / bsp_node[this.num_nodes],
    "num_surfaces" / idx,
    "surfaces" / bsp_surface[this.num_surfaces],
    "num_vertices" / idx,
    "vertices" / f_vertex[this.num_vertices],
    "num_shared_sides" / dword,
    "num_zones" / dword,
    "zones" / zone[this.num_zones],
    "num_polys" / idx,
    "num_lightmaps" / idx,
    "lightmaps" / lightmap[this.num_lightmaps],
    "num_lightbits" / idx,
    "lightbits" / byte[this.num_lightbits],
    "num_bounds" / idx,
    "bounds" / bounding_box[this.num_bounds],
    "num_leafhulls" / idx,
    "leafhulls" / dword[this.num_leafhulls],
    "num_leaves" / idx,
    "leaves" / leaf[this.num_leaves],
    "num_lights" / idx,
    "lights" / idx[this.num_lights],
    "root_outside" / dword,
    "linked" / dword,
)

default_object = Struct(
    *ut_object.subcons,
    "raw" / Pointer(
        this._.serial_offset, 
        HexDump(Bytes(this._.serial_size))
    )
)

# 2d Objects
# palette = ut_object
# font = ut_object
# texture = ut_object
cubemap = default_object
fire = default_object
ice_texture = default_object
water_texture = default_object
wave_texture = default_object
wet_texture = default_object
fluid_texture = default_object
movie_texture = default_object
# scripted_texture = default_object
# 3d Objects
# primitive = default_object
mesh = default_object
lod_mesh = default_object
skeletal_mesh = default_object
vert_mesh = default_object
static_mesh = default_object
# animation = default_object
mesh_animation = default_object
index_animation = default_object
index_buffer = default_object
# brush = default_object
mover = default_object
# model = default_object
# polys = default_object
# Sounds
# sound = default_object
# sound_group = default_object
# procedural_sound = default_object
# music = default_object
# code
null = default_object
# text_buffer = default_object
# field = default_object
const = default_object
enum = default_object
# property = default_object
byte_property = default_object
int_property = default_object
bool_property = default_object
float_property = default_object
# object_property = default_object
class_property = default_object
name_property = default_object
struct_property = default_object
str_property = default_object
array_property = default_object
fixed_array_property = default_object
map_property = default_object
string_property = default_object
delegate_property = default_object
pointer_property = default_object
function = default_object
# Other
package = default_object
# level_base = default_object
level = default_object
# package_check_info = default_object


ut_object_map = {
    "none": ut_object,
    "palette": palette,
    "font": font,
    "texture": texture,
    "cubemap": cubemap,
    "fire": fire,
    "icetexture": ice_texture,
    "watertexture": water_texture,
    "wavetexture": wave_texture,
    "wettexture": wet_texture,
    "fluidtexture": fluid_texture,
    "movietexture": movie_texture,
    "scriptedtexture": scripted_texture,
    # 3d Objects
    "primitive": primitive,
    "mesh": mesh,
    "lodmesh": lod_mesh,
    "skeletalmesh": skeletal_mesh,
    "vertmesh": vert_mesh,
    "staticmesh": static_mesh,
    "animation": animation,
    "meshanimation": mesh_animation,
    "indexanimation": index_animation,
    "indexbuffer": index_buffer,
    "brush": brush,
    "mover": mover,
    "model": model,
    "polys": polys,
    # Sounds
    "sound": sound,
    "soundgroup": sound_group,
    "proceduralsound": procedural_sound,
    "music": music,
    # code
    "null": null,
    "textbuffer": text_buffer,
    "field": field,
    "const": const,
    "enum": enum,
    "property": property,
    "byteproperty": byte_property,
    "intproperty": int_property,
    "boolproperty": bool_property,
    "floatproperty": float_property,
    # "objectproperty": object_property,
    "objectproperty": object_property,
    "classproperty": class_property,
    "nameproperty": name_property,
    "structproperty": struct_property,
    "strproperty": str_property,
    "arrayproperty": array_property,
    "fixedarrayproperty": fixed_array_property,
    "mapproperty": map_property,
    "stringproperty": string_property,
    "delegateproperty": delegate_property,
    "pointerproperty": pointer_property,
    "struct": struct,
    "function": function,
    "state": state,
    "class": class_,
    "": class_,
    # Other
    "package": package,
    "levelbase": level_base,
    "level": level,
    "packagecheckinfo": package_check_info,
}
