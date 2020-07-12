import os
import importlib
from collections.abc import Iterable, Container

root = "/home/jason/WINE32PREFIXTEST/drive_c/deusex/Maps"
map1path = os.path.join(root, "TestMap.dx")
map2path = os.path.join(root, "TestMap2.dx")
map3path = os.path.join(root, "simple.dx")
map4path = os.path.join(root, "simple2.dx")

map3newpath = map3path + "new"
import construct
import difflib
import ut_construct
import diff_bin
from diff_bin import print_diff
from ut_construct import export_object

importlib.reload(ut_construct)

with open(map1path, "rb") as f:
    map1 = ut_construct.package.parse(f.read())
with open(map2path, "rb") as f:
    map2 = ut_construct.package.parse(f.read())
with open(map3path, "rb") as f:
    map3 = ut_construct.package.parse(f.read())
with open(map4path, "rb") as f:
    map4 = ut_construct.package.parse(f.read())

# with open(map3path + "new", "rb") as f:
#     map3new = ut_construct.package.parse_stream(f)
importlib.reload(diff_bin)
entdict1 = {obj.obj_name: obj for obj in map1.export_objects}
entdict2 = {obj.obj_name: obj for obj in map2.export_objects}
entdict3 = {obj.obj_name: obj for obj in map3.export_objects}
entdict4 = {obj.obj_name: obj for obj in map4.export_objects}

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
def descend(c, ofunc, keyfunc):
    if hasattr(c, "keys"):
        for key in c.keys():
            keyfunc(key)
            descend(c[key], ofunc, keyfunc)
    elif (
        isinstance(c, Container)
        and not isinstance(c, str)
        and not isinstance(c, construct.Enum)
    ):
        for o in c:
            descend(o, ofunc, keyfunc)
    else:
        ofunc(c)


def descend2(tree1, tree2, ofunc, pathfunc, path=[]):
    if hasattr(tree1, "keys") and hasattr(tree2, "keys"):
        shared_keys = set(tree1.keys()) & set(tree2.keys())
        tree1_keys = set(tree1.keys()) - set(tree2.keys())
        tree2_keys = set(tree2.keys()) - set(tree1.keys())
        for key in shared_keys - {"_io"}:
            descend2(tree1[key], tree2[key], ofunc, pathfunc, path + [key])
        if tree1_keys:
            print("Missing from tree1: ", tree1_keys)
        if tree2_keys:
            print("Missing from tree2:", tree2_keys)
    elif (
        (isinstance(tree1, Container) and isinstance(tree2, Container))
        and not (isinstance(tree1, str) or isinstance(tree2, str))
        and not (isinstance(tree1, construct.Enum) or isinstance(tree2, construct.Enum))
    ):
        for t1, t2 in zip(tree1, tree2):
            descend2(t1, t2, ofunc, pathfunc, path)
    else:
        if tree1 != tree2:
            pathfunc(path)
            ofunc(tree1)
            ofunc(tree2)


shared_keys = entdict3.keys() & entdict4.keys()
for key in shared_keys:
    obj1 = entdict3[key]
    obj2 = entdict4[key]
    if obj1.data != obj2.data:
        print(key)
        print("=" * 80)
        print(entdict3[key])
        print(entdict4[key])
