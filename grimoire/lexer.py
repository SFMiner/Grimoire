#!/usr/bin/env python3
"""
Grimoire Programming Language Lexical Analyzer (Tokenizer)

This module implements a lexical analyzer for the Grimoire programming language,
converting source code into tokens for parsing.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any
import re


class TokenType(Enum):
    # Literals
    SCROLL = auto()         # String literals $SCROLL(...)
    SIGIL = auto()          # Integer literals SIGIL(...)
    RUNE = auto()           # Character literals
    AETHER = auto()         # Float literals
    IDENTIFIER = auto()     # Variable/function names
    
    # Keywords
    CONJURE = auto()        # Object creation
    SUMMON = auto()         # Import/include
    BIND = auto()           # Variable assignment
    RITUAL = auto()         # Function definition
    ARTIFACT = auto()       # Class definition
    FAMILIAR = auto()       # Familiar definition
    ARCHON = auto()         # Archon definition (strategic AI)
    SPIRIT = auto()         # Spirit definition (tactical AI)
    ESSENCE = auto()        # Class attribute
    INVOKE = auto()         # Constructor/function call
    SCRY = auto()           # Print/output
    TRANSMUTE = auto()      # Type casting
    BANISH = auto()         # Delete
    UPON = auto()           # Function call operator
    PORTAL = auto()         # Cross-plane access
    PLANE = auto()          # Plane definition
    SHIFT = auto()          # Plane transition
    EFFECT = auto()         # Effect definition
    COMMAND = auto()        # Familiar command
    INQUIRE = auto()        # Familiar query
    DISMISS = auto()        # Familiar dismissal
    
    # Control Flow
    SHOULD = auto()         # if statement
    BE_IT = auto()          # elif
    OTHERWISE = auto()      # else
    ELSEWISE = auto()       # else (variant)
    LEST = auto()           # legacy else (kept for compatibility)
    WHILE_CHARGED = auto()  # while loop
    FOR_EACH = auto()       # for loop start
    ARCANA = auto()         # for loop variable
    IN = auto()             # for loop 'in'
    BREAK_SPELL = auto()    # break
    CONTINUE_RITUAL = auto() # continue
    RETURN = auto()         # return
    
    # Operators
    DIMINISH_BY = auto()    # -=
    STRENGTHEN_BY = auto()  # +=
    IS_NOW = auto()         # =
    ADDED_TO = auto()       # +
    SUBTRACTED_FROM = auto() # -
    MULTIPLIED_BY = auto()  # *
    DIVIDED_BY = auto()     # /
    MODULO = auto()         # %
    POWER = auto()          # **
    
    # Comparison
    IS_GREATER_THAN = auto()     # >
    IS_LESSER_THAN = auto()      # <
    IS_NOT_LESSER_THAN = auto()  # >=
    IS_NOT_GREATER_THAN = auto() # <=
    IS_EQUAL_TO = auto()         # ==
    IS_NOT_EQUAL_TO = auto()     # !=
    
    # Logical
    AND = auto()            # and
    OR = auto()             # or
    NOT = auto()            # not
    
    # Punctuation
    LEFT_PAREN = auto()     # (
    RIGHT_PAREN = auto()    # )
    LEFT_BRACE = auto()     # {
    RIGHT_BRACE = auto()    # }
    LEFT_BRACKET = auto()   # [
    RIGHT_BRACKET = auto()  # ]
    COMMA = auto()          # ,
    DOT = auto()            # .
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    WHITESPACE = auto()
    COMMENT = auto()


@dataclass
class Token:
    """Represents a single token in the Grimoire language."""
    type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int


class GrimoireLexer:
    """Lexical analyzer for the Grimoire programming language."""
    
    # Keywords mapping
    KEYWORDS = {
        'conjure': TokenType.CONJURE,
        'bind': TokenType.BIND,
        'ritual': TokenType.RITUAL,
        'artifact': TokenType.ARTIFACT,
        'familiar': TokenType.FAMILIAR,
        'archon': TokenType.ARCHON,
        'spirit': TokenType.SPIRIT,
        'essence': TokenType.ESSENCE,

        'scry': TokenType.SCRY,
        'transmute': TokenType.TRANSMUTE,
        'banish': TokenType.BANISH,
        'upon': TokenType.UPON,
        'portal': TokenType.PORTAL,
        'plane': TokenType.PLANE,
        'shift': TokenType.SHIFT,
        'effect': TokenType.EFFECT,
        'command': TokenType.COMMAND,
        'inquire': TokenType.INQUIRE,
        'dismiss': TokenType.DISMISS,
        'arcana': TokenType.ARCANA,
        'in': TokenType.IN,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'return': TokenType.RETURN,
        'should': TokenType.SHOULD,
        'be_it': TokenType.BE_IT,
        'otherwise': TokenType.OTHERWISE,
        'elsewise': TokenType.ELSEWISE,
        'lest': TokenType.LEST,
    }
    
    # Multi-word keywords and operators
    MULTI_WORD_TOKENS = {
        'while charged': TokenType.WHILE_CHARGED,
        'for each': TokenType.FOR_EACH,
        'break spell': TokenType.BREAK_SPELL,
        'continue ritual': TokenType.CONTINUE_RITUAL,
        'diminish by': TokenType.DIMINISH_BY,
        'strengthen by': TokenType.STRENGTHEN_BY,
        'is now': TokenType.IS_NOW,
        'added to': TokenType.ADDED_TO,
        'subtracted from': TokenType.SUBTRACTED_FROM,
        'multiplied by': TokenType.MULTIPLIED_BY,
        'divided by': TokenType.DIVIDED_BY,
        'is greater than': TokenType.IS_GREATER_THAN,
        'is lesser than': TokenType.IS_LESSER_THAN,
        'is not lesser than': TokenType.IS_NOT_LESSER_THAN,
        'is not greater than': TokenType.IS_NOT_GREATER_THAN,
        'is equal to': TokenType.IS_EQUAL_TO,
        'is not equal to': TokenType.IS_NOT_EQUAL_TO,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        
        # Initialize with keyword variants if available
        self._init_keywords()
    
    def _init_keywords(self):
        """Initialize keyword mappings with support for thematic variants."""
        try:
            from .keyword_variants import KEYWORD_VARIANTS
            
            # Get all keyword mappings from the variants system
            variant_keywords = KEYWORD_VARIANTS.get_all_keywords()
            variant_multiwords = KEYWORD_VARIANTS.get_all_multiwords()
            
            # Update our keyword dictionaries to include all variants
            self.KEYWORDS.update(variant_keywords)
            self.MULTI_WORD_TOKENS.update(variant_multiwords)
            
        except ImportError:
            # If keyword variants aren't available, use defaults (already defined as class attributes)
            pass
    
    def scan_tokens(self) -> List[Token]:
        """Scan the source code and return a list of tokens."""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return self.tokens
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of the source."""
        return self.current >= len(self.source)
    
    def scan_token(self) -> None:
        """Scan a single token."""
        c = self.advance()
        
        # Single character tokens
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '+':
            self.add_token(TokenType.ADDED_TO)
        elif c == '-':
            self.add_token(TokenType.SUBTRACTED_FROM)
        elif c == '*':
            if self.match('*'):
                self.add_token(TokenType.POWER)
            else:
                self.add_token(TokenType.MULTIPLIED_BY)
        elif c == '/':
            self.add_token(TokenType.DIVIDED_BY)
        elif c == '%':
            self.add_token(TokenType.MODULO)
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.IS_EQUAL_TO)
            else:
                self.add_token(TokenType.IS_NOW)
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.IS_NOT_EQUAL_TO)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.IS_NOT_LESSER_THAN)
            else:
                self.add_token(TokenType.IS_GREATER_THAN)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.IS_NOT_GREATER_THAN)
            else:
                self.add_token(TokenType.IS_LESSER_THAN)
        elif c == '\n':
            self.add_token(TokenType.NEWLINE)
            self.line += 1
            self.column = 1
        elif c in ' \t\r':
            # Ignore whitespace
            pass
        elif c == '#':
            # Comment - ignore until end of line
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        elif c == '$':
            # Handle $SCROLL() literals
            if self.match_word('SCROLL'):
                # Advance past 'SCROLL'
                for _ in range(6):  # len('SCROLL')
                    self.advance()
                self.scroll_literal()
        elif c.isalpha() or c == '_':
            # Handle identifiers and keywords
            self.identifier()
        elif c.isdigit():
            # Handle numbers
            self.number()
        else:
            # Unknown character
            raise SyntaxError(f"Unexpected character '{c}' at line {self.line}, column {self.column}")
    
    def advance(self) -> str:
        """Consume and return the current character."""
        if self.is_at_end():
            return '\0'
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]
    
    def match(self, expected: str) -> bool:
        """Check if current character matches expected and consume if it does."""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        self.column += 1
        return True
    
    def match_word(self, word: str) -> bool:
        """Check if the following characters match a word."""
        if self.current + len(word) > len(self.source):
            return False
        
        return self.source[self.current:self.current + len(word)] == word
    
    def peek(self) -> str:
        """Return current character without consuming it."""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        """Return next character without consuming it."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def add_token(self, token_type: TokenType, literal: Any = None) -> None:
        """Add a token to the token list."""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line, self.column - len(text)))
    
    def scroll_literal(self) -> None:
        """Handle $SCROLL() string literals."""
        if not self.match('('):
            raise SyntaxError(f"Expected '(' after $SCROLL at line {self.line}")
        
        value = ""
        while self.peek() != ')' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            if self.peek() == '\\':
                self.advance()  # consume backslash
                escaped = self.advance()
                if escaped == 'n':
                    value += '\n'
                elif escaped == 't':
                    value += '\t'
                elif escaped == 'r':
                    value += '\r'
                elif escaped == '\\':
                    value += '\\'
                elif escaped == '"':
                    value += '"'
                elif escaped == "'":
                    value += "'"
                else:
                    value += escaped
            else:
                value += self.advance()
        
        if self.is_at_end():
            raise SyntaxError(f"Unterminated string at line {self.line}")
        
        # Consume closing )
        self.advance()
        self.add_token(TokenType.SCROLL, value)
    
    def number(self) -> None:
        """Handle numeric literals."""
        while self.peek().isdigit():
            self.advance()
        
        # Look for decimal point
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume the .
            while self.peek().isdigit():
                self.advance()
            
            value = float(self.source[self.start:self.current])
            self.add_token(TokenType.AETHER, value)
        else:
            # Check if it's a SIGIL() literal
            text = self.source[self.start:self.current]
            value = int(text)
            self.add_token(TokenType.SIGIL, value)
    
    def identifier(self) -> None:
        """Handle identifiers and keywords."""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        
        # Check for multi-word tokens by looking ahead
        original_current = self.current
        original_column = self.column
        
        # Skip whitespace and check for multi-word patterns
        while self.peek() in ' \t':
            self.advance()
        
        # Try to match multi-word tokens
        for phrase, token_type in self.MULTI_WORD_TOKENS.items():
            if phrase.startswith(text):
                remaining = phrase[len(text):].strip()
                if remaining and self.match_phrase(remaining):
                    self.add_token(token_type)
                    return
        
        # Restore position if no multi-word match
        self.current = original_current
        self.column = original_column
        
        # Check single-word keywords
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def match_phrase(self, phrase: str) -> bool:
        """Try to match a phrase starting from current position."""
        saved_current = self.current
        saved_column = self.column
        
        words = phrase.split()
        for word in words:
            # Skip whitespace
            while self.peek() in ' \t':
                self.advance()
            
            # Try to match the word
            if not self.match_word(word):
                # Restore position
                self.current = saved_current
                self.column = saved_column
                return False
            
            # Advance past the word
            for _ in range(len(word)):
                self.advance()
        
        return True


def tokenize_grimoire(source: str) -> List[Token]:
    """Convenience function to tokenize Grimoire source code."""
    lexer = GrimoireLexer(source)
    return lexer.scan_tokens()


if __name__ == "__main__":
    # Example usage
    sample_code = '''
    # Conjure a Wizard and cast a fireball
    ritual main():
        bind wizard_name = $SCROLL(Merlin)
        merlin = conjure Wizard upon wizard_name, 10
        
        if enchanted merlin.mana is greater than 20:
            merlin.cast_fireball upon $SCROLL(Dragon)
            diminish merlin.mana by 20
        else cursed:
            scry $SCROLL(Not enough mana!)
    
    main
    '''
    
    try:
        tokens = tokenize_grimoire(sample_code)
        
        print("Tokens:")
        print("-" * 50)
        for token in tokens:
            if token.type != TokenType.NEWLINE:  # Skip newlines for cleaner output
                print(f"{token.type.name:<20} | {token.lexeme:<15} | {token.literal}")
    
    except SyntaxError as e:
        print(f"Lexical Error: {e}")