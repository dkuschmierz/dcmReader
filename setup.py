import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dcmReader",
    version="0.4.1",
    author="Dominic Kuschmierz",
    author_email="dominic@kuschmierz.org",
    description="Parser for the DCM (Data Conservation format) format used by e.g. Vector, ETAS,...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dkuschmierz/dcmReader",
    project_urls={
        "Bug Tracker": "https://github.com/dkuschmierz/dcmReader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
