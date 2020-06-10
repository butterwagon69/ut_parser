import os
import importlib

root = "/home/jason/WINE32PREFIXTEST/drive_c/deusex/Maps"
map1path = os.path.join(root, "TestMap.dx")
map2path = os.path.join(root, "TestMap2.dx")
map3path = os.path.join(root, "simple.dx")
map4path = os.path.join(root, "simple2.dx")

map3newpath = map3path + "new"
import difflib
import ut_construct
import diff_bin
from diff_bin import print_diff
from ut_construct import export_object

importlib.reload(ut_construct)

with open(map1path, "rb") as f:
    map1 = ut_construct.package.parse_stream(f)
with open(map2path, "rb") as f:
    map2 = ut_construct.package.parse_stream(f)
with open(map3path, "rb") as f:
    map3 = ut_construct.package.parse_stream(f)
with open(map4path, "rb") as f:
    map4 = ut_construct.package.parse_stream(f)

# with open(map3path + "new", "rb") as f:
#     map3new = ut_construct.package.parse_stream(f)
importlib.reload(diff_bin)
entdict1 = {obj.obj_name: obj for obj in map1.export_objects}
entdict2 = {obj.obj_name: obj for obj in map2.export_objects}
entdict3 = {obj.obj_name: obj for obj in map3.export_objects}
# entdict3new = {obj.obj_name: obj for obj in map3new.export_objects}

#
# with open(map3path, "rb") as f:
#     map3datacache = f.read()
#     map3data = bytearray(map3datacache)
#     map3 = ut_construct.package.parse(map3datacache)
# for obj in map3.export_objects:
#     if obj.cls_name == "Polys":
#         start = obj.serial_offset
#         end = start + obj.serial_size
#         sl = slice(start, end)
#         assert map3datacache[sl] == export_object.build(obj)[sl]
#         for poly in obj.object.polygons:
#             for vector in ("texture_u", "texture_v"):
#                 poly_vector = getattr(poly, vector)
#                 for component in "xyz":
#                     currentscale = getattr(poly_vector, component)
#                     setattr(poly_vector, component, 100 * currentscale)
#         new_bin_raw = export_object.build(obj)
#         assert len(new_bin_raw) == end
#         new_bin = new_bin_raw[sl]
#         old_bin = map3datacache[sl]
#         assert len(new_bin) == len(old_bin)
#         print_diff(old_bin, new_bin)
#         print(len(old_bin))
#         print(len(new_bin))
#         map3data[sl] = new_bin
# with open(map3newpath, "wb") as f:
#     f.write(map3data)

# with open(map3path, "rb") as f1, open(map3newpath, "rb") as f2:
#     print_diff(f1.read(), f2.read())
# print("Hello!")

for object1, object2 in zip(map3.export_objects, map4.export_objects):
    if (object1 != object2) and (object1.obj_name == object2.obj_name):
        print(object1)
        print(object2)
