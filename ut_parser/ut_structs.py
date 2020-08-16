from .module_types import (
    single,
    integer,
    idx,
    dword,
    word,
    byte,
    sized_ascii_z,
    float,
    qword,
    Computed,
)
from construct import Struct, this, Probe, Int16sl

color = Struct("R" / byte, "G" / byte, "B" / byte, "A" / byte)

vector = Struct("x" / single, "y" / single, "z" / single)

pointregion = Struct("zone" / idx, "ileaf" / integer, "zonenumber" / byte)

rotator = Struct("yaw" / integer, "roll" / integer, "pitch" / integer)

scale = Struct(
    "x" / single, "y" / single, "z" / single, "sheerrate" / single, "sheeraxis" / byte
)

plane = Struct(*vector.subcons, "w" / single)

sphere = Struct(*plane.subcons)

quat = Struct("x" / single, "y" / single, "z" / single, "w" / single)

polygon = Struct(
    "vertex_array_size" / idx,
    "base" / vector,
    "normal" / vector,
    "texture_u" / vector,
    "texture_v" / vector,
    "vertex" / vector[this.vertex_array_size],
    "poly_flags" / dword,
    "actor" / idx,
    "texture" / idx,
    "item_name" / idx,
    "i_link" / idx,
    "i_brush_poly" / idx,
    "pan_u" / Int16sl,
    "pan_v" / Int16sl,
)

url = Struct(
    "protocol" / sized_ascii_z,
    "host" / sized_ascii_z,
    "map" / sized_ascii_z,
    "size" / idx,
    "options" / sized_ascii_z[this.size],
    "portal" / sized_ascii_z,
    "port" / dword,
    "valid" / dword,
)

named_bone = Struct("name_idx" / idx, "flags" / dword, "parent_index" / dword,)

analog_track = Struct(
    "flags" / dword,
    "num_key_quats" / idx,
    "key_quats" / quat[this.num_key_quats],
    "num_key_pos" / idx,
    "key_pos" / vector,
    "num_key_times" / idx,
    "key_times" / single[this.num_key_times],
)

motion_chunk = Struct(
    "root_speed_vector" / vector,
    "track_time" / single,
    "start_bone" / dword,
    "flags" / dword,
    "num_indeces" / idx,
    "bone_indeces" / dword[this.num_indeces],
    "num_anims" / idx,
    "anim_tracks" / analog_track[this.num_anims],
    "root_track" / analog_track,
)

bounding_box = Struct("min" / vector, "max" / vector, "valid" / byte)

bounding_sphere = Struct(
    "center" / vector, "radius" / float  # only valid if version > 61
)

bsp_node = Struct(
    "plane" / plane,
    "zone_mask" / qword,
    "node_flags" / byte,
    "vert_pool_index" / idx,
    "suface_index" / idx,
    "front_index" / idx,
    "back_index" / idx,
    "plane_index" / idx,
    "collision_bound_index" / idx,
    "render_bound_index" / idx,
    "zone_index" / byte[2],
    "num_vertices" / byte,
    "leaf_index" / dword[2],
)

bsp_surface = Struct(
    "texture_index" / idx,
    "poly_flags" / dword,
    "p_base" / idx,
    "v_normal" / idx,
    "v_texture_u" / idx,
    "v_texture_v" / idx,
    "lightmap_index" / idx,
    "brush_poly_index" / idx,
    "pan_u" / word,
    "pan_v" / word,
    "actor" / idx,
)

f_vertex = Struct("p_vertex" / idx, "side_index" / idx)

mesh_vertex = Struct(
    # if game is not Deus Ex, these will be sized differently
    "x" / Int16sl,
    "y" / Int16sl,
    "z" / Int16sl,
    "trash" / Int16sl,
)

triangle = Struct(
    "vertex1" / word,
    "vertex2" / word,
    "vertex3" / word,
    "u1" / byte,
    "v1" / byte,
    "u2" / byte,
    "v2" / byte,
    "u3" / byte,
    "v3" / byte,
    "flags" / dword,
    "texture_index" / dword,
)


anim_seq_notify = Struct("time" / float, "function_index" / idx)


anim_seq = Struct(
    "name_index" / idx,
    "group_index" / idx,
    "startframe" / dword,
    "numframes" / dword,
    "num_notifys" / idx,
    "notifys" / anim_seq_notify[this.num_notifys],
    "rate" / float,
)


connect = Struct("num_vert_tiangles" / dword, "triangle_list_offset" / dword)

struct_texture = Struct("index" / idx)

face = Struct(
    "wedge_index_1" / word,
    "wedge_index_2" / word,
    "wedge_index_3" / word,
    "material_index" / word,
)

material = Struct("flags" / dword, "texture_index" / dword,)

wedge = Struct("vertex_index" / word, "u" / byte, "v" / byte,)

zone = Struct("actor" / idx, "connectivity" / qword, "visibility" / qword,)

lightmap = Struct(
    "data_offset" / dword,
    "pan" / vector,
    "u_clamp" / idx,
    "v_clamp" / idx,
    "u_scale" / float,
    "v_scale" / float,
    "light_actors_index" / dword,
)

leaf = Struct(
    "zone_index" / idx,
    "permeating_index" / idx,
    "volumetric_index" / idx,
    "visible_zones" / qword,
)

struct_map = {
    "color": color,
    "vector": vector,
    "pointregion": pointregion,
    "rotator": rotator,
    "scale": scale,
    "plane": plane,
    "sphere": sphere,
}
