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
Grimoire Programming Language

A magical programming language designed for game development with familiar-based
programming paradigms, effect systems, and dimensional programming concepts.
"""

__version__ = "0.1.0"
__author__ = "Grimoire Language Team"

from .lexer import GrimoireLexer, TokenType, Token, tokenize_grimoire
from .parser import GrimoireParser, parse_grimoire
from .interpreter import GrimoireInterpreter
from .keyword_variants import KeywordVariants, MagicSchool, ThematicCodeGenerator
from importlib import import_module

# Re-export messaging utilities
messaging = import_module('grimoire.messaging')

__all__ = [
    'GrimoireLexer', 'TokenType', 'Token', 'tokenize_grimoire',
    'GrimoireParser', 'parse_grimoire',
    'GrimoireInterpreter',
    'KeywordVariants', 'MagicSchool', 'ThematicCodeGenerator',
    'messaging',
]