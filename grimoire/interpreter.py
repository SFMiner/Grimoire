#!/usr/bin/env python3
"""
Grimoire Programming Language Interpreter

This module implements a tree-walking interpreter for the Grimoire programming language.
"""

import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .lexer import TokenType
from .parser import (
    Program, Statement, Expression, ASTNode,
    LiteralExpression, IdentifierExpression, BinaryExpression, UnaryExpression,
    CallExpression, PropertyAccessExpression, ConjureExpression, PortalExpression,
    PropertyAssignmentExpression, ExpressionStatement, BindStatement, ScryStatement,
    IfStatement, WhileStatement, ForStatement, BlockStatement, ReturnStatement,
    BreakStatement, ContinueStatement,
    RitualStatement, ArtifactStatement, FamiliarStatement, PlaneStatement,
    EffectStatement, CommandStatement
)


# =============================================================================
# Runtime Values and Environment
# =============================================================================

@dataclass
class GrimoireFunction:
    """Represents a runtime function (ritual)."""
    name: str
    parameters: List[str]
    body: BlockStatement
    closure: 'Environment'
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> Any:
        """Execute the function with given arguments."""
        if len(arguments) != len(self.parameters):
            raise RuntimeError(f"Expected {len(self.parameters)} arguments but got {len(arguments)}")
        
        # Create new environment for function execution
        function_env = Environment(self.closure)
        
        # Bind parameters to arguments
        for param, arg in zip(self.parameters, arguments):
            function_env.define(param, arg)
        
        # Execute function body
        try:
            interpreter.execute_block(self.body.statements, function_env)
        except ReturnValue as return_val:
            return return_val.value
        
        return None


@dataclass
class GrimoireClass:
    """Represents a runtime class (artifact)."""
    name: str
    superclass: Optional['GrimoireClass']
    methods: Dict[str, GrimoireFunction]
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> 'GrimoireInstance':
        """Create a new instance of this class."""
        instance = GrimoireInstance(self)
        
        # Look for constructor (invoke method)
        if "invoke" in self.methods:
            self.methods["invoke"].call(interpreter, [instance] + arguments)
        
        return instance


class GrimoireInstance:
    """Represents a runtime instance of a class."""
    
    def __init__(self, grimoire_class: GrimoireClass):
        self.grimoire_class = grimoire_class
        self.fields = {}
    
    def get(self, name: str) -> Any:
        """Get a property value."""
        if name in self.fields:
            return self.fields[name]
        
        # Look for method
        method = self.grimoire_class.methods.get(name)
        if method:
            return BoundMethod(self, method)
        
        raise RuntimeError(f"Undefined property '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """Set a property value."""
        self.fields[name] = value


# =============================================================================
# Familiar System
# =============================================================================

class FamiliarCapability(ABC):
    """Base class for familiar capabilities."""
    
    @abstractmethod
    def execute(self, command: str, arguments: List[Any]) -> Any:
        """Execute a command with given arguments."""
        pass
    
    @abstractmethod
    def inquire(self, query: str) -> Any:
        """Handle an inquiry about the familiar's state."""
        pass


class MemoryImpCapability(FamiliarCapability):
    """Memory management familiar capability."""
    
    def __init__(self):
        self.allocated_memory = 0
        self.max_memory = 1024 * 1024  # 1MB default
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "allocate":
            if len(arguments) != 1:
                raise RuntimeError("allocate expects 1 argument (bytes)")
            bytes_to_allocate = arguments[0]
            if self.allocated_memory + bytes_to_allocate > self.max_memory:
                raise RuntimeError("Not enough memory available")
            self.allocated_memory += bytes_to_allocate
            return f"Allocated {bytes_to_allocate} bytes"
        elif command == "deallocate":
            if len(arguments) != 1:
                raise RuntimeError("deallocate expects 1 argument (bytes)")
            bytes_to_free = arguments[0]
            self.allocated_memory = max(0, self.allocated_memory - bytes_to_free)
            return f"Deallocated {bytes_to_free} bytes"
        else:
            raise RuntimeError(f"Unknown memory command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "free_space":
            return self.max_memory - self.allocated_memory
        elif query == "used_space":
            return self.allocated_memory
        elif query == "total_space":
            return self.max_memory
        else:
            raise RuntimeError(f"Unknown memory query: {query}")


class FileSpriteCapability(FamiliarCapability):
    """File system operations familiar capability."""
    
    def __init__(self):
        self.open_files = {}
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "read":
            if len(arguments) != 1:
                raise RuntimeError("read expects 1 argument (filename)")
            filename = arguments[0]
            try:
                with open(filename, 'r') as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to read file: {e}")
        elif command == "write":
            if len(arguments) != 2:
                raise RuntimeError("write expects 2 arguments (filename, content)")
            filename, content = arguments
            try:
                with open(filename, 'w') as f:
                    f.write(str(content))
                return f"Wrote to {filename}"
            except Exception as e:
                raise RuntimeError(f"Failed to write file: {e}")
        elif command == "append":
            if len(arguments) != 2:
                raise RuntimeError("append expects 2 arguments (filename, content)")
            filename, content = arguments
            try:
                with open(filename, 'a') as f:
                    f.write(str(content))
                return f"Appended to {filename}"
            except Exception as e:
                raise RuntimeError(f"Failed to append to file: {e}")
        else:
            raise RuntimeError(f"Unknown file command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "open_files":
            return list(self.open_files.keys())
        else:
            raise RuntimeError(f"Unknown file query: {query}")


class LogScribeCapability(FamiliarCapability):
    """Logging and tracing familiar capability."""
    
    def __init__(self):
        self.log_entries = []
        self.log_level = "INFO"
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "log":
            if len(arguments) < 1:
                raise RuntimeError("log expects at least 1 argument (message)")
            message = arguments[0]
            level = arguments[1] if len(arguments) > 1 else "INFO"
            self.log_entries.append(f"[{level}] {message}")
            return f"Logged: {message}"
        elif command == "clear":
            self.log_entries.clear()
            return "Log cleared"
        elif command == "set_level":
            if len(arguments) != 1:
                raise RuntimeError("set_level expects 1 argument (level)")
            self.log_level = arguments[0]
            return f"Log level set to {self.log_level}"
        else:
            raise RuntimeError(f"Unknown log command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "entries":
            return self.log_entries.copy()
        elif query == "level":
            return self.log_level
        elif query == "count":
            return len(self.log_entries)
        else:
            raise RuntimeError(f"Unknown log query: {query}")


class GrimoireFamiliar:
    """Represents a runtime familiar - a semi-autonomous agent."""
    
    def __init__(self, name: str, familiar_type: str, capabilities: Dict[str, FamiliarCapability]):
        self.name = name
        self.familiar_type = familiar_type
        self.capabilities = capabilities
        self.charge = None  # The entity this familiar manages
        self.state = "active"  # active, inactive, dismissed
        self.properties = {}
    
    def command(self, command: str, arguments: List[Any]) -> Any:
        """Execute a command on this familiar."""
        if self.state != "active":
            raise RuntimeError(f"Familiar {self.name} is not active")
        
        # Handle built-in commands
        if command == "activate":
            self.state = "active"
            return f"Familiar {self.name} activated"
        elif command == "deactivate":
            self.state = "inactive"
            return f"Familiar {self.name} deactivated"
        elif command == "set_charge":
            if len(arguments) != 1:
                raise RuntimeError("set_charge expects 1 argument (entity)")
            self.charge = arguments[0]
            return f"Familiar {self.name} now manages {self.charge}"
        
        # Look for capability that can handle this command
        for capability in self.capabilities.values():
            try:
                return capability.execute(command, arguments)
            except RuntimeError:
                continue
        
        raise RuntimeError(f"Unknown command '{command}' for familiar {self.name}")
    
    def inquire(self, query: str) -> Any:
        """Handle an inquiry about the familiar's state."""
        if self.state != "active":
            raise RuntimeError(f"Familiar {self.name} is not active")
        
        # Handle built-in queries
        if query == "state":
            return self.state
        elif query == "type":
            return self.familiar_type
        elif query == "charge":
            return self.charge
        elif query == "capabilities":
            return list(self.capabilities.keys())
        
        # Look for capability that can handle this query
        for capability in self.capabilities.values():
            try:
                return capability.inquire(query)
            except RuntimeError:
                continue
        
        raise RuntimeError(f"Unknown query '{query}' for familiar {self.name}")
    
    def dismiss(self) -> str:
        """Dismiss this familiar."""
        self.state = "dismissed"
        return f"Familiar {self.name} dismissed"


# Built-in familiar types
FAMILIAR_TYPES = {
    "MemoryImp": lambda: {"memory": MemoryImpCapability()},
    "FileSprite": lambda: {"file": FileSpriteCapability()},
    "LogScribe": lambda: {"log": LogScribeCapability()},
    "TimeKeeper": lambda: {},  # TODO: Implement time-based capabilities
    "ErrorBanshee": lambda: {},  # TODO: Implement error handling capabilities
}


@dataclass
class BoundMethod:
    """Represents a method bound to an instance."""
    instance: GrimoireInstance
    method: GrimoireFunction
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> Any:
        """Execute the bound method."""
        return self.method.call(interpreter, [self.instance] + arguments)


class Environment:
    """Manages variable scoping and symbol tables."""
    
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any) -> None:
        """Define a new variable."""
        self.values[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable's value."""
        if name in self.values:
            return self.values[name]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def assign(self, name: str, value: Any) -> None:
        """Assign to an existing variable."""
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'")


# =============================================================================
# Control Flow Exceptions
# =============================================================================

class ReturnValue(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value
        super().__init__()


class BreakException(Exception):
    """Exception used to implement break statements."""
    pass


class ContinueException(Exception):
    """Exception used to implement continue statements."""
    pass


# =============================================================================
# Interpreter Implementation
# =============================================================================

class GrimoireInterpreter:
    """Tree-walking interpreter for the Grimoire programming language."""
    
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.familiars = {}  # Active familiars
        
        # Define built-in functions
        self._define_builtins()
    
    def _define_builtins(self) -> None:
        """Define built-in functions and constants."""
        # Built-in scry function for output
        def scry_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("scry expects exactly 1 argument")
            print(self._grimoire_to_string(arguments[0]))
            return None
        
        # Built-in summon function for creating familiars
        def summon_builtin(interpreter, arguments):
            if len(arguments) < 1:
                raise RuntimeError("summon expects at least 1 argument (familiar type)")
            familiar_type = arguments[0]
            familiar_name = arguments[1] if len(arguments) > 1 else f"{familiar_type.lower()}_familiar"
            
            if familiar_type not in FAMILIAR_TYPES:
                raise RuntimeError(f"Unknown familiar type: {familiar_type}")
            
            capabilities = FAMILIAR_TYPES[familiar_type]()
            familiar = GrimoireFamiliar(familiar_name, familiar_type, capabilities)
            self.familiars[familiar_name] = familiar
            return familiar
        
        self.globals.define("scry", scry_builtin)
        self.globals.define("summon", summon_builtin)
    
    def _grimoire_to_string(self, value: Any) -> str:
        """Convert a Grimoire value to its string representation."""
        if value is None:
            return "void"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float, str)):
            return str(value)
        elif isinstance(value, GrimoireInstance):
            return f"<{value.grimoire_class.name} instance>"
        elif isinstance(value, GrimoireClass):
            return f"<artifact {value.name}>"
        elif isinstance(value, GrimoireFunction):
            return f"<ritual {value.name}>"
        elif isinstance(value, GrimoireFamiliar):
            return f"<familiar {value.name} ({value.familiar_type})>"
        else:
            return str(value)
    
    def interpret(self, program: Program) -> bool:
        """Interpret a Grimoire program."""
        try:
            for statement in program.statements:
                self.execute(statement)
        except RuntimeError as e:
            print(f"Runtime Error: {e}", file=sys.stderr)
            return False
        return True
    
    def execute(self, statement: Statement) -> None:
        """Execute a statement."""
        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
        
        elif isinstance(statement, BindStatement):
            value = None
            if statement.initializer:
                value = self.evaluate(statement.initializer)
            self.environment.define(statement.name, value)
        
        elif isinstance(statement, ScryStatement):
            value = self.evaluate(statement.expression)
            print(self._grimoire_to_string(value))
        
        elif isinstance(statement, IfStatement):
            condition = self.evaluate(statement.condition)
            if self._is_truthy(condition):
                self.execute(statement.then_branch)
            elif statement.else_branch:
                self.execute(statement.else_branch)
        
        elif isinstance(statement, WhileStatement):
            try:
                while self._is_truthy(self.evaluate(statement.condition)):
                    try:
                        self.execute(statement.body)
                    except ContinueException:
                        continue
            except BreakException:
                pass
        
        elif isinstance(statement, ForStatement):
            # For now, implement basic iteration (would need iterable support)
            raise RuntimeError("For loops not yet implemented")
        
        elif isinstance(statement, BlockStatement):
            self.execute_block(statement.statements, Environment(self.environment))
        
        elif isinstance(statement, ReturnStatement):
            value = None
            if statement.value:
                value = self.evaluate(statement.value)
            raise ReturnValue(value)
        
        elif isinstance(statement, BreakStatement):
            raise BreakException()
        
        elif isinstance(statement, ContinueStatement):
            raise ContinueException()
        
        elif isinstance(statement, RitualStatement):
            function = GrimoireFunction(
                statement.name,
                statement.parameters,
                statement.body,
                self.environment
            )
            self.environment.define(statement.name, function)
        
        elif isinstance(statement, ArtifactStatement):
            superclass = None
            if statement.superclass:
                superclass = self.environment.get(statement.superclass)
                if not isinstance(superclass, GrimoireClass):
                    raise RuntimeError("Superclass must be an artifact")
            
            methods = {}
            for method in statement.methods:
                methods[method.name] = GrimoireFunction(
                    method.name,
                    method.parameters,
                    method.body,
                    self.environment
                )
            
            artifact = GrimoireClass(statement.name, superclass, methods)
            self.environment.define(statement.name, artifact)
        
        elif isinstance(statement, FamiliarStatement):
            # Handle familiar definitions - create a familiar type
            methods = {}
            for method in statement.methods:
                methods[method.name] = GrimoireFunction(
                    method.name,
                    method.parameters,
                    method.body,
                    self.environment
                )
            
            # For now, treat custom familiar definitions as creating a new familiar type
            # This is a simplified approach - in a full implementation, you'd want
            # to create a proper familiar class system
            familiar_class = GrimoireClass(statement.name, None, methods)
            self.environment.define(statement.name, familiar_class)
        
        elif isinstance(statement, CommandStatement):
            # Handle familiar commands
            familiar_expr = self.evaluate(statement.familiar)
            
            if isinstance(familiar_expr, GrimoireFamiliar):
                arguments = [self.evaluate(arg) for arg in statement.arguments]
                result = familiar_expr.command(statement.command, arguments)
                # Command results are usually printed or stored somewhere
                if result is not None:
                    print(self._grimoire_to_string(result))
            else:
                raise RuntimeError(f"Can only command familiars, not {type(familiar_expr)}")
        
        else:
            raise RuntimeError(f"Unknown statement type: {type(statement)}")
    
    def execute_block(self, statements: List[Statement], environment: Environment) -> None:
        """Execute a block of statements in a given environment."""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def evaluate(self, expression: Expression) -> Any:
        """Evaluate an expression and return its value."""
        if isinstance(expression, LiteralExpression):
            return expression.value
        
        elif isinstance(expression, IdentifierExpression):
            return self.environment.get(expression.name)
        
        elif isinstance(expression, BinaryExpression):
            left = self.evaluate(expression.left)
            right = self.evaluate(expression.right)
            
            token_type = expression.operator.type
            
            # Arithmetic operators
            if token_type == TokenType.ADDED_TO:
                return left + right
            elif token_type == TokenType.SUBTRACTED_FROM:
                return left - right
            elif token_type == TokenType.MULTIPLIED_BY:
                return left * right
            elif token_type == TokenType.DIVIDED_BY:
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
            elif token_type == TokenType.MODULO:
                return left % right
            elif token_type == TokenType.POWER:
                return left ** right
            
            # Comparison operators
            elif token_type == TokenType.IS_GREATER_THAN:
                return left > right
            elif token_type == TokenType.IS_LESSER_THAN:
                return left < right
            elif token_type == TokenType.IS_NOT_LESSER_THAN:
                return left >= right
            elif token_type == TokenType.IS_NOT_GREATER_THAN:
                return left <= right
            elif token_type == TokenType.IS_EQUAL_TO:
                return self._is_equal(left, right)
            elif token_type == TokenType.IS_NOT_EQUAL_TO:
                return not self._is_equal(left, right)
            
            # Logical operators
            elif token_type == TokenType.AND:
                return self._is_truthy(left) and self._is_truthy(right)
            elif token_type == TokenType.OR:
                return self._is_truthy(left) or self._is_truthy(right)
            
            else:
                raise RuntimeError(f"Unknown binary operator: {expression.operator.lexeme}")
        
        elif isinstance(expression, UnaryExpression):
            operand = self.evaluate(expression.operand)
            
            if expression.operator.type == TokenType.NOT:
                return not self._is_truthy(operand)
            elif expression.operator.type == TokenType.SUBTRACTED_FROM:
                return -operand
            else:
                raise RuntimeError(f"Unknown unary operator: {expression.operator.lexeme}")
        
        elif isinstance(expression, CallExpression):
            callee = self.evaluate(expression.callee)
            
            arguments = []
            for arg in expression.arguments:
                arguments.append(self.evaluate(arg))
            
            if isinstance(callee, GrimoireFunction):
                return callee.call(self, arguments)
            elif isinstance(callee, GrimoireClass):
                return callee.call(self, arguments)
            elif isinstance(callee, BoundMethod):
                return callee.call(self, arguments)
            elif callable(callee):  # Built-in function
                return callee(self, arguments)
            else:
                raise RuntimeError("Can only call functions and classes")
        
        elif isinstance(expression, PropertyAccessExpression):
            obj = self.evaluate(expression.object)
            
            if isinstance(obj, GrimoireInstance):
                return obj.get(expression.property)
            elif isinstance(obj, GrimoireFamiliar):
                # Handle familiar property access for inquiries
                return obj.inquire(expression.property)
            else:
                raise RuntimeError("Only instances and familiars have properties")
        
        elif isinstance(expression, ConjureExpression):
            artifact_class = self.environment.get(expression.artifact_type)
            
            if not isinstance(artifact_class, GrimoireClass):
                raise RuntimeError(f"'{expression.artifact_type}' is not an artifact")
            
            arguments = []
            for arg in expression.arguments:
                arguments.append(self.evaluate(arg))
            
            return artifact_class.call(self, arguments)
        
        elif isinstance(expression, PortalExpression):
            # For now, portal expressions are not implemented
            raise RuntimeError("Portal expressions not yet implemented")
        
        elif isinstance(expression, PropertyAssignmentExpression):
            # Handle property assignment (self.property = value)
            if isinstance(expression.target, PropertyAccessExpression):
                obj = self.evaluate(expression.target.object)
                value = self.evaluate(expression.value)
                
                if isinstance(obj, GrimoireInstance):
                    obj.set(expression.target.property, value)
                    return value
                else:
                    raise RuntimeError("Only instances have properties")
            else:
                raise RuntimeError("Invalid assignment target")
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expression)}")
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy in Grimoire."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True
    
    def _is_equal(self, left: Any, right: Any) -> bool:
        """Check if two values are equal in Grimoire."""
        return left == right


# =============================================================================
# Convenience Functions
# =============================================================================

def interpret_grimoire(source: str) -> bool:
    """Convenience function to interpret Grimoire source code."""
    from .lexer import GrimoireLexer
    from .parser import GrimoireParser
    
    try:
        # Tokenize
        lexer = GrimoireLexer(source)
        tokens = lexer.scan_tokens()
        
        # Parse
        parser = GrimoireParser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = GrimoireInterpreter()
        return interpreter.interpret(ast)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Example usage
    sample_code = '''
    ritual greet(name):
        scry $SCROLL(Hello, ) added to name
    
    artifact Wizard:
        essence name
        essence mana = 100
        
        ritual invoke(wizard_name):
            bind self.name = wizard_name
            scry $SCROLL(A wizard named ) added to wizard_name added to $SCROLL( appears!)
        
        ritual cast_spell():
            should self.mana is greater than 10:
                diminish self.mana by 10
                scry $SCROLL(Spell cast! Remaining mana: ) added to self.mana
            lest:
                scry $SCROLL(Not enough mana!)
    
    greet upon $SCROLL(World)
    
    bind merlin = conjure Wizard upon $SCROLL(Merlin)
    merlin.cast_spell upon
    merlin.cast_spell upon
    '''
    
    interpret_grimoire(sample_code)