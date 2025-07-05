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
Grimoire Programming Language Parser (Syntax Analyzer)

This module implements a recursive descent parser for the Grimoire programming language,
converting tokens into an Abstract Syntax Tree (AST).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any, Union
from enum import Enum

# Import the lexer components
from .lexer import Token, TokenType, GrimoireLexer


# =============================================================================
# AST Node Definitions
# =============================================================================

class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass


class Expression(ASTNode):
    """Base class for all expression nodes."""
    pass


class Statement(ASTNode):
    """Base class for all statement nodes."""
    pass


@dataclass
class LiteralExpression(Expression):
    """Represents literal values (strings, numbers, etc.)."""
    value: Any
    token_type: TokenType


@dataclass
class IdentifierExpression(Expression):
    """Represents variable/function identifiers."""
    name: str


@dataclass
class BinaryExpression(Expression):
    """Represents binary operations (a + b, a > b, etc.)."""
    left: Expression
    operator: Token
    right: Expression


@dataclass
class UnaryExpression(Expression):
    """Represents unary operations (not x, -x, etc.)."""
    operator: Token
    operand: Expression


@dataclass
class CallExpression(Expression):
    """Represents function calls using 'upon' syntax."""
    callee: Expression
    arguments: List[Expression]
    upon_token: Token  # The 'upon' token for error reporting


@dataclass
class PropertyAccessExpression(Expression):
    """Represents property access (object.property)."""
    object: Expression
    property: str


@dataclass
class ConjureExpression(Expression):
    """Represents object creation with 'conjure'."""
    artifact_type: str
    arguments: List[Expression]


@dataclass
class PortalExpression(Expression):
    """Represents cross-plane access."""
    plane: str
    target: Expression


@dataclass
class PropertyAssignmentExpression(Expression):
    """Represents property assignment (object.property = value)."""
    target: Expression  # Should be a PropertyAccessExpression
    value: Expression


# =============================================================================
# Statement Nodes
# =============================================================================

@dataclass
class ExpressionStatement(Statement):
    """Wraps an expression as a statement."""
    expression: Expression


@dataclass
class BindStatement(Statement):
    """Represents variable binding (bind x = value)."""
    name: str
    initializer: Optional[Expression]


@dataclass
class ScryStatement(Statement):
    """Represents output statements (scry "message")."""
    expression: Expression


@dataclass
class IfStatement(Statement):
    """Represents if-else conditionals."""
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement]


@dataclass
class WhileStatement(Statement):
    """Represents while loops."""
    condition: Expression
    body: Statement


@dataclass
class ForStatement(Statement):
    """Represents for-each loops."""
    variable: str
    iterable: Expression
    body: Statement


@dataclass
class BlockStatement(Statement):
    """Represents a block of statements."""
    statements: List[Statement]


@dataclass
class ReturnStatement(Statement):
    """Represents return statements."""
    value: Optional[Expression]


@dataclass
class BreakStatement(Statement):
    """Represents break statements."""
    pass


@dataclass
class ContinueStatement(Statement):
    """Represents continue statements."""
    pass


@dataclass
class RitualStatement(Statement):
    """Represents function definitions."""
    name: str
    parameters: List[str]
    body: BlockStatement
    return_type: Optional[str] = None


@dataclass
class ArtifactStatement(Statement):
    """Represents class definitions."""
    name: str
    superclass: Optional[str]
    methods: List[RitualStatement]
    essences: List[BindStatement]


@dataclass
class FamiliarStatement(Statement):
    """Represents familiar definitions."""
    name: str
    superclass: Optional[str]
    methods: List[RitualStatement]
    essences: List[BindStatement]


@dataclass
class ArchonStatement(Statement):
    """Represents archon definitions."""
    name: str
    domain: str
    superclass: Optional[str]
    methods: List[RitualStatement]
    essences: List[BindStatement]


@dataclass
class SpiritStatement(Statement):
    """Represents spirit definitions."""
    name: str
    spirit_type: str
    superclass: Optional[str]
    methods: List[RitualStatement]
    essences: List[BindStatement]


@dataclass
class PlaneStatement(Statement):
    """Represents plane definitions."""
    name: str
    body: BlockStatement


@dataclass
class ShiftStatement(Statement):
    """Represents plane shifts (shift to PlaneName)."""
    target_plane: str


@dataclass
class EffectStatement(Statement):
    """Represents effect definitions."""
    name: str


@dataclass
class CommandStatement(Statement):
    """Represents familiar commands."""
    familiar: Expression
    command: str
    arguments: List[Expression]


@dataclass
class Program(ASTNode):
    """Represents the entire program."""
    statements: List[Statement]


# =============================================================================
# Parser Error Classes
# =============================================================================

class ParseError(Exception):
    """Exception raised when parsing fails."""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")


# =============================================================================
# Parser Implementation
# =============================================================================

class GrimoireParser:
    """Recursive descent parser for the Grimoire programming language."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Program:
        """Parse tokens into an AST."""
        statements = []
        
        while not self.is_at_end():
            # Skip newlines at the top level
            if self.check(TokenType.NEWLINE):
                self.advance()
                continue
            
            try:
                stmt = self.declaration()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                # For now, just re-raise. In a production parser, 
                # we might want to implement error recovery.
                raise e
        
        return Program(statements)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        """Return current token without consuming it."""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Return previous token."""
        return self.tokens[self.current - 1]
    
    def advance(self) -> Token:
        """Consume and return current token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self.check(token_type):
            return self.advance()
        
        current_token = self.peek()
        raise ParseError(current_token, message)
    
    def synchronize(self) -> None:
        """Recover from parse error by finding next statement boundary."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.NEWLINE:
                return
            
            if self.peek().type in [
                TokenType.RITUAL, TokenType.ARTIFACT, TokenType.FAMILIAR,
                TokenType.ARCHON, TokenType.SPIRIT, TokenType.BIND, 
                TokenType.SHOULD, TokenType.WHILE_CHARGED,
                TokenType.FOR_EACH, TokenType.RETURN, TokenType.SCRY
            ]:
                return
            
            self.advance()
    
    # =========================================================================
    # Grammar Rules (Top-Down)
    # =========================================================================
    
    def declaration(self) -> Optional[Statement]:
        """Parse declarations (functions, classes, variables, etc.)."""
        try:
            if self.match(TokenType.RITUAL):
                return self.ritual_declaration()
            if self.match(TokenType.ARTIFACT):
                return self.artifact_declaration()
            if self.match(TokenType.FAMILIAR):
                return self.familiar_declaration()
            if self.match(TokenType.ARCHON):
                return self.archon_declaration()
            if self.match(TokenType.SPIRIT):
                return self.spirit_declaration()
            if self.match(TokenType.PLANE):
                return self.plane_declaration()
            if self.match(TokenType.EFFECT):
                return self.effect_declaration()
            
            return self.statement()
        except ParseError as e:
            self.synchronize()
            raise e
    
    def ritual_declaration(self) -> RitualStatement:
        """Parse ritual (function) declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected ritual name").lexeme
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after ritual name")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").lexeme)
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").lexeme)
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        # Optional return type annotation
        return_type = None
        if self.match(TokenType.SUBTRACTED_FROM):  # Using -> for return type
            if self.match(TokenType.IS_GREATER_THAN):  # -> becomes - >
                return_type = self.consume(TokenType.IDENTIFIER, "Expected return type").lexeme
        
        self.consume(TokenType.COLON, "Expected ':' before ritual body")
        
        # Skip newlines before body
        while self.match(TokenType.NEWLINE):
            pass
        
        body = self.block_statement()
        
        return RitualStatement(name, parameters, body, return_type)
    
    def artifact_declaration(self) -> ArtifactStatement:
        """Parse artifact (class) declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected artifact name").lexeme
        
        superclass = None
        # Check if there's inheritance (artifact Name extends SuperClass:)
        # For now, we'll just handle artifact Name: syntax
        
        self.consume(TokenType.COLON, "Expected ':' before artifact body")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        methods = []
        essences = []
        
        # Parse artifact body
        while not self.check(TokenType.EOF) and not self.check_next_declaration():
            if self.match(TokenType.NEWLINE):
                continue
            
            if self.check(TokenType.RITUAL):
                # Don't advance here - let declaration() handle it
                stmt = self.declaration()
                if isinstance(stmt, RitualStatement):
                    methods.append(stmt)
            elif self.check(TokenType.ESSENCE):
                self.advance()
                essences.append(self.essence_declaration())
            else:
                break
        
        return ArtifactStatement(name, superclass, methods, essences)
    
    def familiar_declaration(self) -> FamiliarStatement:
        """Parse familiar declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected familiar name").lexeme
        
        superclass = None
        # For now, we'll just handle familiar Name: syntax
        
        self.consume(TokenType.COLON, "Expected ':' before familiar body")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        methods = []
        essences = []
        
        # Parse familiar body (similar to artifact)
        while not self.check(TokenType.EOF) and not self.check_next_declaration():
            if self.match(TokenType.NEWLINE):
                continue
            
            if self.check(TokenType.RITUAL):
                # Don't advance here - let declaration() handle it
                stmt = self.declaration()
                if isinstance(stmt, RitualStatement):
                    methods.append(stmt)
            elif self.check(TokenType.ESSENCE):
                self.advance()
                essences.append(self.essence_declaration())
            else:
                break
        
        return FamiliarStatement(name, superclass, methods, essences)
    
    def archon_declaration(self) -> ArchonStatement:
        """Parse archon declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected archon name").lexeme
        
        # Parse domain specification (archon Name domain DomainType:)
        domain = "general"
        if self.check(TokenType.IDENTIFIER):
            domain_keyword = self.advance().lexeme
            if domain_keyword == "domain":
                domain = self.consume(TokenType.IDENTIFIER, "Expected domain type").lexeme
        
        superclass = None
        # For now, we'll just handle archon Name domain Domain: syntax
        
        self.consume(TokenType.COLON, "Expected ':' before archon body")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        methods = []
        essences = []
        
        # Parse archon body (similar to artifact)
        while not self.check(TokenType.EOF) and not self.check_next_declaration():
            if self.match(TokenType.NEWLINE):
                continue
            
            if self.check(TokenType.RITUAL):
                # Don't advance here - let declaration() handle it
                stmt = self.declaration()
                if isinstance(stmt, RitualStatement):
                    methods.append(stmt)
            elif self.check(TokenType.ESSENCE):
                self.advance()
                essences.append(self.essence_declaration())
            else:
                break
        
        return ArchonStatement(name, domain, superclass, methods, essences)
    
    def spirit_declaration(self) -> SpiritStatement:
        """Parse spirit declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected spirit name").lexeme
        
        # Parse spirit type specification (spirit Name type SpiritType:)
        spirit_type = "general"
        if self.check(TokenType.IDENTIFIER):
            type_keyword = self.advance().lexeme
            if type_keyword == "type":
                spirit_type = self.consume(TokenType.IDENTIFIER, "Expected spirit type").lexeme
        
        superclass = None
        # For now, we'll just handle spirit Name type Type: syntax
        
        self.consume(TokenType.COLON, "Expected ':' before spirit body")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        methods = []
        essences = []
        
        # Parse spirit body (similar to artifact)
        while not self.check(TokenType.EOF) and not self.check_next_declaration():
            if self.match(TokenType.NEWLINE):
                continue
            
            if self.check(TokenType.RITUAL):
                # Don't advance here - let declaration() handle it
                stmt = self.declaration()
                if isinstance(stmt, RitualStatement):
                    methods.append(stmt)
            elif self.check(TokenType.ESSENCE):
                self.advance()
                essences.append(self.essence_declaration())
            else:
                break
        
        return SpiritStatement(name, spirit_type, superclass, methods, essences)
    
    def plane_declaration(self) -> PlaneStatement:
        """Parse plane declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected plane name").lexeme
        self.consume(TokenType.COLON, "Expected ':' after plane name")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        body = self.block_statement()
        return PlaneStatement(name, body)
    
    def effect_declaration(self) -> EffectStatement:
        """Parse effect declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected effect name").lexeme
        return EffectStatement(name)
    
    def essence_declaration(self) -> BindStatement:
        """Parse essence (class attribute) declarations."""
        name = self.consume(TokenType.IDENTIFIER, "Expected essence name").lexeme
        
        initializer = None
        if self.match(TokenType.IS_NOW):
            initializer = self.expression()
        
        return BindStatement(name, initializer)
    
    def check_next_declaration(self) -> bool:
        """Check if we're at the start of a new declaration."""
        return self.check(TokenType.RITUAL) or self.check(TokenType.ARTIFACT) or \
               self.check(TokenType.FAMILIAR) or self.check(TokenType.ARCHON) or \
               self.check(TokenType.SPIRIT) or self.check(TokenType.PLANE) or \
               self.check(TokenType.EFFECT)
    
    def statement(self) -> Statement:
        """Parse statements."""
        if self.match(TokenType.BIND):
            return self.bind_statement()
        if self.match(TokenType.SCRY):
            return self.scry_statement()
        if self.match(TokenType.SHIFT):
            return self.shift_statement()
        if self.match(TokenType.IF, TokenType.SHOULD):
            return self.if_statement()
        if self.match(TokenType.WHILE_CHARGED):
            return self.while_statement()
        if self.match(TokenType.FOR_EACH):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.BREAK_SPELL):
            return BreakStatement()
        if self.match(TokenType.CONTINUE_RITUAL):
            return ContinueStatement()
        if self.match(TokenType.COMMAND):
            return self.command_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block_statement()
        
        return self.expression_statement()
    
    def bind_statement(self) -> Statement:
        """Parse variable binding statements or property assignments."""
        # Check if this is a property assignment (bind self.property = value)
        if (self.check(TokenType.IDENTIFIER) and 
            self.current + 1 < len(self.tokens) and 
            self.tokens[self.current + 1].type == TokenType.DOT):
            
            # Parse as property assignment
            target = self.expression()  # This will parse self.property
            self.consume(TokenType.IS_NOW, "Expected 'is now' after property")
            value = self.expression()
            
            # Create a property assignment expression statement
            assignment = PropertyAssignmentExpression(target, value)
            return ExpressionStatement(assignment)
        else:
            # Parse as regular variable binding
            name = self.consume(TokenType.IDENTIFIER, "Expected variable name").lexeme
            
            initializer = None
            if self.match(TokenType.IS_NOW):
                initializer = self.expression()
            
            return BindStatement(name, initializer)
    
    def scry_statement(self) -> ScryStatement:
        """Parse scry (print) statements."""
        expr = self.expression()
        return ScryStatement(expr)
    
    def shift_statement(self) -> ShiftStatement:
        """Parse shift statements (shift to PlaneName)."""
        # Expect: shift to <plane_name>
        if not self.check(TokenType.IDENTIFIER) or self.peek().lexeme != "to":
            raise ParseError(self.peek(), "Expected 'to' after 'shift'")
        
        self.advance()  # consume 'to'
        target_plane = self.consume(TokenType.IDENTIFIER, "Expected plane name after 'shift to'").lexeme
        return ShiftStatement(target_plane)
    
    def if_statement(self) -> IfStatement:
        """Parse if statements."""
        condition = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after if condition")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        # Parse then-branch - could be single statement or block
        then_branch = self.parse_if_branch()
        
        # Skip newlines and look for else clause
        while self.match(TokenType.NEWLINE):
            pass
        
        else_branch = None
        # Handle 'be_it' (elif) recursively
        if self.match(TokenType.BE_IT):
            self.consume(TokenType.COLON, "Expected ':' after be_it (elif)")
            while self.match(TokenType.NEWLINE):
                pass
            elif_branch_statement = self.statement()
            else_branch = elif_branch_statement  # chain as else branch containing nested if
        elif self.match(TokenType.OTHERWISE, TokenType.ELSEWISE, TokenType.LEST, TokenType.ELSE):
            self.consume(TokenType.COLON, "Expected ':' after else")
            while self.match(TokenType.NEWLINE):
                pass
            else_branch = self.statement()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def parse_if_branch(self) -> Statement:
        """Parse a branch of an if statement (could be single statement or block)."""
        statements = []
        
        # Collect all statements at the same indentation level
        while (not self.is_at_end() and 
               not self.check(TokenType.ELSE) and not self.check(TokenType.LEST) and
               not self.check_next_declaration()):
            
            if self.match(TokenType.NEWLINE):
                continue
                
            # Check if we're still in the indented block
            # Simple heuristic: if we see these tokens, we've left the block
            if (self.check(TokenType.RITUAL) or self.check(TokenType.ARTIFACT) or 
                self.check(TokenType.FAMILIAR) or self.check(TokenType.ARCHON) or
                self.check(TokenType.SPIRIT) or self.check(TokenType.PLANE) or
                self.check(TokenType.EFFECT)):
                break
            
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
                
            # If we parsed a non-expression statement, we might be done with this block
            if not isinstance(stmt, ExpressionStatement):
                # Check if the next line is at the same or lesser indentation
                # For now, we'll use a simple approach: stop if we see certain tokens
                if (self.check(TokenType.ELSE) or self.check(TokenType.LEST) or 
                    self.check(TokenType.IDENTIFIER) or
                    self.check_next_declaration()):
                    break
        
        if len(statements) == 1:
            return statements[0]
        elif len(statements) > 1:
            return BlockStatement(statements)
        else:
            # Empty block - shouldn't happen but handle gracefully
            return BlockStatement([])
    
    def while_statement(self) -> WhileStatement:
        """Parse while statements."""
        condition = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after while condition")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        body = self.statement()
        return WhileStatement(condition, body)
    
    def for_statement(self) -> ForStatement:
        """Parse for-each statements."""
        self.consume(TokenType.ARCANA, "Expected 'arcana' in for loop")
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").lexeme
        self.consume(TokenType.IN, "Expected 'in' in for loop")
        iterable = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after for clause")
        
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass
        
        body = self.statement()
        return ForStatement(variable, iterable, body)
    
    def return_statement(self) -> ReturnStatement:
        """Parse return statements."""
        value = None
        if not self.check(TokenType.NEWLINE) and not self.is_at_end():
            value = self.expression()
        
        return ReturnStatement(value)
    
    def command_statement(self) -> CommandStatement:
        """Parse familiar command statements."""
        familiar = self.expression()
        self.consume(TokenType.IDENTIFIER, "Expected command name")
        command = self.previous().lexeme
        
        arguments = []
        if self.match(TokenType.UPON):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        return CommandStatement(familiar, command, arguments)
    
    def block_statement(self) -> BlockStatement:
        """Parse block statements."""
        statements = []
        
        # Check if this is a braced block or an indented block
        expects_brace = self.previous().type == TokenType.LEFT_BRACE
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.match(TokenType.NEWLINE):
                continue
            
            # For indented blocks, stop when we reach a non-indented line
            if not expects_brace:
                # Simple heuristic: stop if we see a top-level declaration or EOF
                if (self.check(TokenType.RITUAL) or self.check(TokenType.ARTIFACT) or 
                    self.check(TokenType.FAMILIAR) or self.check(TokenType.ARCHON) or
                    self.check(TokenType.SPIRIT) or self.check(TokenType.PLANE) or
                    self.check(TokenType.EFFECT)):
                    break
                # Also stop if we encounter an identifier that might be a top-level call
                if (self.check(TokenType.IDENTIFIER) and 
                    self.tokens[self.current + 1].type == TokenType.UPON):
                    break
            
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        
        if expects_brace:
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        
        return BlockStatement(statements)
    
    def expression_statement(self) -> ExpressionStatement:
        """Parse expression statements."""
        expr = self.expression()
        return ExpressionStatement(expr)
    
    # =========================================================================
    # Expression Parsing (Operator Precedence)
    # =========================================================================
    
    def expression(self) -> Expression:
        """Parse expressions."""
        return self.logical_or()
    
    def logical_or(self) -> Expression:
        """Parse logical OR expressions."""
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def logical_and(self) -> Expression:
        """Parse logical AND expressions."""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expression:
        """Parse equality expressions."""
        expr = self.comparison()
        
        while self.match(TokenType.IS_EQUAL_TO, TokenType.IS_NOT_EQUAL_TO):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expression:
        """Parse comparison expressions."""
        expr = self.term()
        
        while self.match(TokenType.IS_GREATER_THAN, TokenType.IS_NOT_GREATER_THAN,
                         TokenType.IS_LESSER_THAN, TokenType.IS_NOT_LESSER_THAN):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def term(self) -> Expression:
        """Parse addition and subtraction."""
        expr = self.factor()
        
        while self.match(TokenType.ADDED_TO, TokenType.SUBTRACTED_FROM):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expression:
        """Parse multiplication, division, and modulo."""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLIED_BY, TokenType.DIVIDED_BY, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expression:
        """Parse unary expressions."""
        if self.match(TokenType.NOT, TokenType.SUBTRACTED_FROM):
            operator = self.previous()
            expr = self.unary()
            return UnaryExpression(operator, expr)
        
        return self.power()
    
    def power(self) -> Expression:
        """Parse power expressions."""
        expr = self.call()
        
        if self.match(TokenType.POWER):
            operator = self.previous()
            right = self.unary()  # Right associative
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def call(self) -> Expression:
        """Parse function calls and property access."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.UPON):
                upon_token = self.previous()
                arguments = []
                
                # Only parse arguments if we're not at end of line/file/statement
                if (not self.check(TokenType.NEWLINE) and 
                    not self.check(TokenType.EOF) and
                    not self.check(TokenType.RIGHT_BRACE) and
                    not self.check(TokenType.RIGHT_PAREN)):
                    # Check if we have an actual expression to parse
                    if (self.check(TokenType.IDENTIFIER) or 
                        self.check(TokenType.SCROLL) or 
                        self.check(TokenType.SIGIL) or 
                        self.check(TokenType.AETHER) or
                        self.check(TokenType.LEFT_PAREN) or
                        self.check(TokenType.CONJURE) or
                        self.check(TokenType.SUMMON) or
                        self.check(TokenType.EVOKE)):
                        arguments.append(self.expression())
                        while self.match(TokenType.COMMA):
                            arguments.append(self.expression())
                
                expr = CallExpression(expr, arguments, upon_token)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'").lexeme
                expr = PropertyAccessExpression(expr, name)
            else:
                break
        
        return expr
    
    def primary(self) -> Expression:
        """Parse primary expressions."""
        if self.match(TokenType.SCROLL):
            return LiteralExpression(self.previous().literal, TokenType.SCROLL)
        
        if self.match(TokenType.SIGIL):
            return LiteralExpression(self.previous().literal, TokenType.SIGIL)
        
        if self.match(TokenType.AETHER):
            return LiteralExpression(self.previous().literal, TokenType.AETHER)
        
        if self.match(TokenType.IDENTIFIER):
            return IdentifierExpression(self.previous().lexeme)
        
        if self.match(TokenType.CONJURE):
            artifact_type = self.consume(TokenType.IDENTIFIER, "Expected artifact type after 'conjure'").lexeme
            
            arguments = []
            if self.match(TokenType.UPON):
                # Only parse arguments if there's actually an expression to parse
                if (not self.check(TokenType.NEWLINE) and 
                    not self.check(TokenType.EOF) and
                    not self.check(TokenType.RIGHT_BRACE) and
                    not self.check(TokenType.RIGHT_PAREN)):
                    # Check if we have an actual expression to parse
                    if (self.check(TokenType.IDENTIFIER) or 
                        self.check(TokenType.SCROLL) or 
                        self.check(TokenType.SIGIL) or 
                        self.check(TokenType.AETHER) or
                        self.check(TokenType.LEFT_PAREN) or
                        self.check(TokenType.CONJURE) or
                        self.check(TokenType.SUMMON) or
                        self.check(TokenType.EVOKE)):
                        arguments.append(self.expression())
                        while self.match(TokenType.COMMA):
                            arguments.append(self.expression())
            
            return ConjureExpression(artifact_type, arguments)

        if self.match(TokenType.SUMMON):
            # Handle summon as a function call
            summon_token = self.previous()
            return IdentifierExpression(summon_token.lexeme)

        if self.match(TokenType.EVOKE):
            # Handle evoke for formal property access
            # Parse: evoke object.property -> PropertyAccessExpression
            # Parse the object identifier directly
            obj_name = self.consume(TokenType.IDENTIFIER, "Expected object name after 'evoke'").lexeme
            obj = IdentifierExpression(obj_name)

            # Handle property access with dot notation
            if self.match(TokenType.DOT):
                prop = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'").lexeme
                return PropertyAccessExpression(obj, prop)

            # If no dot, just return the object
            return obj

        if self.match(TokenType.PORTAL):
            plane = self.consume(TokenType.IDENTIFIER, "Expected plane name after 'portal'").lexeme
            self.consume(TokenType.DOT, "Expected '.' after plane name")
            target = self.expression()
            return PortalExpression(plane, target)
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        # If we get here, we have an unexpected token
        raise ParseError(self.peek(), f"Unexpected token '{self.peek().lexeme}'")


# =============================================================================
# Convenience Functions
# =============================================================================

def parse_grimoire(source: str) -> Program:
    """Convenience function to parse Grimoire source code."""
    lexer = GrimoireLexer(source)
    tokens = lexer.scan_tokens()
    parser = GrimoireParser(tokens)
    return parser.parse()


def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    """Convert AST to string representation for debugging."""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        result = f"{prefix}Program:\n"
        for stmt in node.statements:
            result += ast_to_string(stmt, indent + 1)
        return result
    
    elif isinstance(node, RitualStatement):
        result = f"{prefix}Ritual '{node.name}' ({', '.join(node.parameters)}):\n"
        result += ast_to_string(node.body, indent + 1)
        return result
    
    elif isinstance(node, BlockStatement):
        result = f"{prefix}Block:\n"
        for stmt in node.statements:
            result += ast_to_string(stmt, indent + 1)
        return result
    
    elif isinstance(node, BindStatement):
        result = f"{prefix}Bind '{node.name}'"
        if node.initializer:
            result += " = "
            result += ast_to_string(node.initializer, 0).strip()
        return result + "\n"
    
    elif isinstance(node, BinaryExpression):
        return f"({ast_to_string(node.left, 0).strip()} {node.operator.lexeme} {ast_to_string(node.right, 0).strip()})"
    
    elif isinstance(node, LiteralExpression):
        return str(node.value)
    
    elif isinstance(node, IdentifierExpression):
        return node.name
    
    # Add more cases as needed for debugging
    else:
        return f"{prefix}{type(node).__name__}\n"


if __name__ == "__main__":
    # Example usage
    sample_code = '''
    ritual main():
        bind wizard_name = $SCROLL(Merlin)
        merlin = conjure Wizard upon wizard_name, 10
        
        if enchanted merlin.mana is greater than 20:
            merlin.cast_fireball upon $SCROLL(Dragon)
            scry $SCROLL(Fireball cast!)
        else cursed:
            scry $SCROLL(Not enough mana!)
    
    artifact Wizard:
        essence name
        essence power
        essence mana = 100
        
        ritual cast_fireball(target):
            if enchanted self.mana is not lesser than 20:
                diminish self.mana by 20
                scry $SCROLL(Casting fireball!)
    '''
    
    try:
        ast = parse_grimoire(sample_code)
        print("Parse successful!")
        print("\nAST Structure:")
        print(ast_to_string(ast))
    
    except ParseError as e:
        print(f"Parse Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")