import ut_construct


with open("Samples/00_Intro.dx", "rb") as f:
    big_map_bytes = f.read()
big_map_construct = ut_construct.package.parse(big_map_bytes)
