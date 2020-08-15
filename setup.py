import setuptools

setuptools.setup(
    name="ut_parser",
    version="0.0.1",
    author="Butterwagon69",
    author_email="butterwagon69@gmail.com",
    description="A small library for parsing ut packages",
    long_description="""
    A library for parsing Unreal Tournament packages.
    Currently only tested for Deus Ex.""",
    long_description_content_type="text",
    url="https://github.com/butterwagon69/ut_parser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT Licens",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
