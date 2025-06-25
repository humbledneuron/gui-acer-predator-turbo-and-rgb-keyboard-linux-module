#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="acer-predator-gui",
    version="1.0.0",
    author="Acer RGB Community",
    description="Modern GUI for Acer RGB Keyboard Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JafarAkhondali/acer-predator-turbo-and-rgb-keyboard-linux-module",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "acer-predator-gui=gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.qss", "*.png", "*.svg", "*.ico"],
    },
)