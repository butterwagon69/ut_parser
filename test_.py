import ut_construct
import utils
import io
import secrets
import construct
import ut_packages
import sys


# struct = construct.Struct("byte_range" / ut_construct.Idx())

# for i in range(100):
#     byte_range = secrets.token_bytes(16)
#     print(f"byte_range: {list(byte_range)}")
#     stream = io.BytesIO(byte_range)
#     struct_res = struct.parse(byte_range)
#     utils_res = utils.read_idx(stream)
#     print(f"struct_res: {struct_res['byte_range']}, utils_res: {utils_res}")
#     assert utils_res == struct_res["byte_range"]
#     new_byte_range = struct.build(dict(byte_range=struct_res["byte_range"]))
#     print(f"new_byte_range: {list(new_byte_range)}")
#     assert byte_range[:len(new_byte_range)] == new_byte_range

if __name__ == "__main__":
    with open(sys.argv[1], "rb") as f:
        res1 = ut_construct.package.parse_stream(f)
else:
    with open("NewTest.utx", "rb") as f:
        res1 = ut_construct.package.parse_stream(f)
