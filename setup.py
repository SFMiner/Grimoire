#!/usr/bin/env python3
# Grimoire Programming Language
# Copyright (C) 2025 Sean Miner
#
# This file is part of Grimoire.
#
# Grimoire is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Grimoire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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