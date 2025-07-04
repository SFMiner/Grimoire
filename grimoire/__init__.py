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

__all__ = [
    'GrimoireLexer', 'TokenType', 'Token', 'tokenize_grimoire',
    'GrimoireParser', 'parse_grimoire',
    'GrimoireInterpreter'
]