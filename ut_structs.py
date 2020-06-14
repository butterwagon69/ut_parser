from module_types import single, integer, idx, dword, word, byte, sized_ascii_z
from construct import Struct, this, Computed, Probe

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
    "pan_u_base" / word,
    "pan_v_base" / word,
    "pan_u"
    / Computed(
        lambda x: x.pan_u_base | 0xFFFF0000 if x.pan_u_base > 0x8000 else x.pan_u_base
    ),
    "pan_v"
    / Computed(
        lambda x: x.pan_v_base | 0xFFFF0000 if x.pan_v_base > 0x8000 else x.pan_v_base
    ),
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

struct_map = {
    "color": color,
    "vector": vector,
    "pointregion": pointregion,
    "rotator": rotator,
    "scale": scale,
    "plane": plane,
    "sphere": sphere,
}
