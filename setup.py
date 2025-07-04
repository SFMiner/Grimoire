#!/usr/bin/env python3
"""
Setup script for the Grimoire Programming Language
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="grimoire-lang",
    version="0.1.0",
    description="A magical programming language designed for game development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Grimoire Language Team",
    author_email="grimoire@example.com",
    url="https://github.com/grimoire-lang/grimoire",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "grimoire=grimoire.cli:main",
        ],
    },
    keywords="programming-language, game-development, magic, compiler, interpreter",
    project_urls={
        "Bug Reports": "https://github.com/grimoire-lang/grimoire/issues",
        "Source": "https://github.com/grimoire-lang/grimoire",
    },
)