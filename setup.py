import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bftool-pkg-sulcud",
    version="1.4.2.2",
    author="Antonio Donis",
    author_email="antoniojosedonishung@gmail.com",
    description="A python module (with script) included to handle different kinds of bruteforce",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shoriwe/bftool",
    packages=["bftool"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
