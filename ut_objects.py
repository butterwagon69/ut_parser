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
    "start_pos" / Tell,
    "flags" / Computed(this._.flags),
    "state_frame" / If(this.flags.HasStack, state_frame),
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
        "start" / Tell,
        "length" / Computed(this.pos_after - this.start),
        "imgbytes" / HexDump(Bytes(this.length)),
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
    Probe(),
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


# 2d Objects
# palette = ut_object
# font = ut_object
# texture = ut_object
cubemap = ut_object
fire = ut_object
ice_texture = ut_object
water_texture = ut_object
wave_texture = ut_object
wet_texture = ut_object
fluid_texture = ut_object
movie_texture = ut_object
# scripted_texture = ut_object
# 3d Objects
# primitive = ut_object
mesh = ut_object
lod_mesh = ut_object
skeletal_mesh = ut_object
vert_mesh = ut_object
static_mesh = ut_object
# animation = ut_object
mesh_animation = ut_object
index_animation = ut_object
index_buffer = ut_object
# brush = ut_object
mover = ut_object
# model = ut_object
# polys = ut_object
# Sounds
# sound = ut_object
# sound_group = ut_object
# procedural_sound = ut_object
# music = ut_object
# code
null = ut_object
# text_buffer = ut_object
# field = ut_object
const = ut_object
enum = ut_object
# property = ut_object
byte_property = ut_object
int_property = ut_object
bool_property = ut_object
float_property = ut_object
# object_property = ut_object
class_property = ut_object
name_property = ut_object
struct_property = ut_object
str_property = ut_object
array_property = ut_object
fixed_array_property = ut_object
map_property = ut_object
string_property = ut_object
delegate_property = ut_object
pointer_property = ut_object
function = ut_object
# Other
package = ut_object
# level_base = ut_object
level = ut_object
# package_check_info = ut_object


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
