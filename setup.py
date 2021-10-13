"""
===============================================================================
@filename:  setup.py
@author:    Alvaro Carril
@project:   cb-higered-brain
@purpose:   Higher Education Chatbot - Brain API Setup File
===============================================================================
"""
import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cb-highered-brain",
    version="1.0.0",
    install_requires=[],
    author="Alvaro Carril",
    author_email="acarril@princeton.edu",
    description="Higher Education Chatbot - Brain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acarril/cb-highered-brain",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)