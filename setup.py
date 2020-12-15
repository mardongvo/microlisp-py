# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="microlisp",
    version="0.1",
    author="Mardong",
    author_email="mardong_@inbox.ru",
    description="Micro evaluator for S-expression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mardongvo/microlisp-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
