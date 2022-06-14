# Version number is tracked in docs/conf.py.
import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras = {}
# Packages required for installing docs.


setuptools.setup(
    name="lineage",
    version="0.0",
    author="UCLA",
    author_email="jysun@cs.ucla.edu",
    description="A library to provide lineage for ml systems",
    include_package_data=False,
    license="MIT",
    url="https://github.com/fabriceyhc/dpml",
    packages=setuptools.find_namespace_packages(
        exclude=[
            "build*",
            "docs*",
            "dist*",
            "examples*",
            "outputs*",
            "tests*",
            "wandb*",
        ]
    ),
    extras_require=extras,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=open("requirements.txt").readlines(),
)
