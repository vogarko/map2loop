import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="map2model",
    version="0.0.17",
    author="Mark Jessell",
    author_email="mark.jessell@gmail.com",
    description="A package to extract information from geological maps to feed 3D modelling packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/map2model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
