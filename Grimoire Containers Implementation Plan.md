# Grimoire Arrays, Dictionaries, and Containers Implementation Plan

## Overview

This implementation plan adds comprehensive container support to the Grimoire programming language, following the existing magical syntax patterns and Python-based architecture. The containers will integrate with the current lexer, parser, and interpreter infrastructure.

## Current Language Foundation

Based on project analysis:
- **Primary Language**: Python implementation
- **Existing Data Types**: `$SCROLL()` (strings), `SIGIL()` (integers), `RUNE` (characters), `AETHER` (floats)
- **Architecture**: Lexer → Parser → AST → Tree-walking interpreter
- **Style**: Magical/mystical syntax with practical game development focus

## Phase 1: Core Container Types

### 1.1 Lexer Extensions (`grimoire/lexer.py`)

Add new token types for containers:

```python
class TokenType(Enum):
	# ... existing tokens
	
	# Container types
	TOME = auto()           # $TOME(...) - Arrays/Lists
	GRIMOIRE = auto()       # $GRIMOIRE(...) - Dictionaries/Maps
	CODEX = auto()          # $CODEX(...) - Sets
	CHRONICLE = auto()      # $CHRONICLE(...) - Ordered collections
	VAULT = auto()          # $VAULT(...) - Tuples/immutable sequences
	
	# Container operations
	INSCRIBE = auto()       # Add/append to container
	EXTRACT = auto()        # Remove from container
	SEEK = auto()           # Search/find in container
	MANIFEST = auto()       # Create/initialize container
	ENUMERATE = auto()      # List/iterate container contents
	
	# Collection literals
	LEFT_BRACKET = auto()   # [ for array literals
	RIGHT_BRACKET = auto()  # ] for array literals
	LEFT_BRACE = auto()     # { for dict/set literals
	RIGHT_BRACE = auto()    # } for dict/set literals
	COLON = auto()          # : for key-value pairs
	ARROW = auto()          # => alternative syntax for key-value
```

### 1.2 Container Literal Parsing

```python
def tome_literal(self) -> None:
	"""Handle $TOME([item1, item2, ...]) array literals"""
	if not self.match('('):
		raise SyntaxError(f"Expected '(' after $TOME at line {self.line}")
	
	# Parse array contents
	items = []
	if not self.check(')'):
		items = self.parse_array_elements()
	
	self.consume(')', "Expected ')' after array elements")
	self.add_token(TokenType.TOME, items)

def grimoire_literal(self) -> None:
	"""Handle $GRIMOIRE({key: value, ...}) dictionary literals"""
	if not self.match('('):
		raise SyntaxError(f"Expected '(' after $GRIMOIRE at line {self.line}")
	
	# Parse dictionary contents
	pairs = {}
	if not self.check(')'):
		pairs = self.parse_dict_elements()
	
	self.consume(')', "Expected ')' after dictionary elements")
	self.add_token(TokenType.GRIMOIRE, pairs)
```

### 1.3 Parser AST Nodes (`grimoire/parser.py`)

```python
@dataclass
class ContainerLiteral(Expression):
	"""Base class for container literals"""
	container_type: str
	elements: Any

@dataclass
class TomeLiteral(ContainerLiteral):
	"""Array/list literal: $TOME([1, 2, 3])"""
	elements: List[Expression]
	
	def __init__(self, elements: List[Expression]):
		super().__init__("tome", elements)
		self.elements = elements

@dataclass
class GrimoireLiteral(ContainerLiteral):
	"""Dictionary literal: $GRIMOIRE({key: value})"""
	pairs: List[Tuple[Expression, Expression]]
	
	def __init__(self, pairs: List[Tuple[Expression, Expression]]):
		super().__init__("grimoire", pairs)
		self.pairs = pairs

@dataclass
class CodexLiteral(ContainerLiteral):
	"""Set literal: $CODEX({1, 2, 3})"""
	elements: List[Expression]
	
	def __init__(self, elements: List[Expression]):
		super().__init__("codex", elements)
		self.elements = elements

@dataclass
class ContainerAccess(Expression):
	"""Container element access: tome[index] or grimoire[key]"""
	container: Expression
	index: Expression

@dataclass
class ContainerSlice(Expression):
	"""Container slicing: tome[start:end]"""
	container: Expression
	start: Optional[Expression]
	end: Optional[Expression]
	step: Optional[Expression]
```

## Phase 2: Container Implementation (`grimoire/containers/`)

### 2.1 Base Container Classes

```python
# grimoire/containers/base.py
from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional

class GrimoireContainer(ABC):
	"""Base class for all Grimoire containers"""
	
	def __init__(self):
		self._elements = None
		self._metadata = {}
	
	@abstractmethod
	def inscribe(self, *args) -> None:
		"""Add element(s) to container"""
		pass
	
	@abstractmethod
	def extract(self, key) -> Any:
		"""Remove and return element"""
		pass
	
	@abstractmethod
	def seek(self, value) -> Any:
		"""Find element in container"""
		pass
	
	@abstractmethod
	def manifest(self, initial_data=None) -> None:
		"""Initialize container with data"""
		pass
	
	@abstractmethod
	def enumerate_contents(self) -> Iterator:
		"""Iterate over container contents"""
		pass
	
	def __len__(self) -> int:
		return len(self._elements) if self._elements else 0
	
	def __bool__(self) -> bool:
		return len(self) > 0
```

### 2.2 Tome (Array/List) Implementation

```python
# grimoire/containers/tome.py
from .base import GrimoireContainer
from typing import Any, List, Optional, Union

class Tome(GrimoireContainer):
	"""Array/List container - ordered, mutable sequence"""
	
	def __init__(self, initial_data: Optional[List] = None):
		super().__init__()
		self._elements: List[Any] = initial_data.copy() if initial_data else []
	
	def inscribe(self, *items) -> None:
		"""Add items to end of tome"""
		self._elements.extend(items)
	
	def inscribe_at(self, index: int, item: Any) -> None:
		"""Insert item at specific index"""
		if index < 0 or index > len(self._elements):
			raise IndexError(f"Tome index {index} out of bounds")
		self._elements.insert(index, item)
	
	def extract(self, index: int) -> Any:
		"""Remove and return item at index"""
		if index < 0 or index >= len(self._elements):
			raise IndexError(f"Tome index {index} out of bounds")
		return self._elements.pop(index)
	
	def extract_last(self) -> Any:
		"""Remove and return last item"""
		if not self._elements:
			raise IndexError("Cannot extract from empty tome")
		return self._elements.pop()
	
	def seek(self, value: Any) -> Optional[int]:
		"""Find first index of value, None if not found"""
		try:
			return self._elements.index(value)
		except ValueError:
			return None
	
	def seek_all(self, value: Any) -> List[int]:
		"""Find all indices of value"""
		return [i for i, x in enumerate(self._elements) if x == value]
	
	def manifest(self, initial_data: Optional[List] = None) -> None:
		"""Initialize with data"""
		self._elements = initial_data.copy() if initial_data else []
	
	def enumerate_contents(self):
		"""Iterate over elements"""
		return iter(self._elements)
	
	def __getitem__(self, key: Union[int, slice]) -> Any:
		return self._elements[key]
	
	def __setitem__(self, key: Union[int, slice], value: Any) -> None:
		self._elements[key] = value
	
	def __str__(self) -> str:
		return f"$TOME({self._elements})"
	
	def __repr__(self) -> str:
		return f"Tome({self._elements})"
	
	# Tome-specific methods
	def reverse_order(self) -> None:
		"""Reverse the tome in place"""
		self._elements.reverse()
	
	def sort_contents(self, key=None, reverse=False) -> None:
		"""Sort the tome in place"""
		self._elements.sort(key=key, reverse=reverse)
	
	def slice_tome(self, start: int = None, end: int = None, step: int = None) -> 'Tome':
		"""Return a new tome with sliced contents"""
		sliced_data = self._elements[start:end:step]
		return Tome(sliced_data)
```

### 2.3 Grimoire (Dictionary/Map) Implementation

```python
# grimoire/containers/grimoire.py
from .base import GrimoireContainer
from typing import Any, Dict, Iterator, Optional, Tuple, Union

class Grimoire(GrimoireContainer):
	"""Dictionary/Map container - key-value associations"""
	
	def __init__(self, initial_data: Optional[Dict] = None):
		super().__init__()
		self._elements: Dict[Any, Any] = initial_data.copy() if initial_data else {}
	
	def inscribe(self, key: Any, value: Any) -> None:
		"""Add or update key-value pair"""
		self._elements[key] = value
	
	def inscribe_many(self, pairs: Dict[Any, Any]) -> None:
		"""Add multiple key-value pairs"""
		self._elements.update(pairs)
	
	def extract(self, key: Any) -> Any:
		"""Remove and return value for key"""
		if key not in self._elements:
			raise KeyError(f"Key '{key}' not found in grimoire")
		return self._elements.pop(key)
	
	def extract_or_default(self, key: Any, default: Any = None) -> Any:
		"""Remove and return value, or default if key not found"""
		return self._elements.pop(key, default)
	
	def seek(self, key: Any) -> Any:
		"""Get value for key (doesn't remove)"""
		return self._elements.get(key)
	
	def seek_or_default(self, key: Any, default: Any = None) -> Any:
		"""Get value for key or return default"""
		return self._elements.get(key, default)
	
	def seek_by_value(self, value: Any) -> Optional[Any]:
		"""Find first key with given value"""
		for k, v in self._elements.items():
			if v == value:
				return k
		return None
	
	def manifest(self, initial_data: Optional[Dict] = None) -> None:
		"""Initialize with data"""
		self._elements = initial_data.copy() if initial_data else {}
	
	def enumerate_contents(self) -> Iterator[Tuple[Any, Any]]:
		"""Iterate over key-value pairs"""
		return iter(self._elements.items())
	
	def enumerate_keys(self) -> Iterator[Any]:
		"""Iterate over keys"""
		return iter(self._elements.keys())
	
	def enumerate_values(self) -> Iterator[Any]:
		"""Iterate over values"""
		return iter(self._elements.values())
	
	def contains_key(self, key: Any) -> bool:
		"""Check if key exists"""
		return key in self._elements
	
	def contains_value(self, value: Any) -> bool:
		"""Check if value exists"""
		return value in self._elements.values()
	
	def __getitem__(self, key: Any) -> Any:
		return self._elements[key]
	
	def __setitem__(self, key: Any, value: Any) -> None:
		self._elements[key] = value
	
	def __contains__(self, key: Any) -> bool:
		return key in self._elements
	
	def __str__(self) -> str:
		pairs = [f"{k}: {v}" for k, v in self._elements.items()]
		return f"$GRIMOIRE({{{', '.join(pairs)}}})"
	
	def __repr__(self) -> str:
		return f"Grimoire({self._elements})"
```

### 2.4 Codex (Set) Implementation

```python
# grimoire/containers/codex.py
from .base import GrimoireContainer
from typing import Any, Set, Optional, Iterator

class Codex(GrimoireContainer):
	"""Set container - unique, unordered elements"""
	
	def __init__(self, initial_data: Optional[Set] = None):
		super().__init__()
		self._elements: Set[Any] = set(initial_data) if initial_data else set()
	
	def inscribe(self, *items) -> None:
		"""Add items to codex (duplicates ignored)"""
		for item in items:
			self._elements.add(item)
	
	def extract(self, item: Any) -> Any:
		"""Remove specific item from codex"""
		if item not in self._elements:
			raise KeyError(f"Item '{item}' not found in codex")
		self._elements.remove(item)
		return item
	
	def extract_any(self) -> Any:
		"""Remove and return arbitrary item"""
		if not self._elements:
			raise KeyError("Cannot extract from empty codex")
		return self._elements.pop()
	
	def seek(self, item: Any) -> bool:
		"""Check if item exists in codex"""
		return item in self._elements
	
	def manifest(self, initial_data: Optional[Set] = None) -> None:
		"""Initialize with data"""
		self._elements = set(initial_data) if initial_data else set()
	
	def enumerate_contents(self) -> Iterator[Any]:
		"""Iterate over elements"""
		return iter(self._elements)
	
	def __contains__(self, item: Any) -> bool:
		return item in self._elements
	
	def __str__(self) -> str:
		return f"$CODEX({{{', '.join(map(str, self._elements))}}})"
	
	def __repr__(self) -> str:
		return f"Codex({self._elements})"
	
	# Set operations
	def unite_with(self, other: 'Codex') -> 'Codex':
		"""Union operation"""
		return Codex(self._elements | other._elements)
	
	def intersect_with(self, other: 'Codex') -> 'Codex':
		"""Intersection operation"""
		return Codex(self._elements & other._elements)
	
	def exclude(self, other: 'Codex') -> 'Codex':
		"""Difference operation"""
		return Codex(self._elements - other._elements)
```

## Phase 3: Interpreter Integration (`grimoire/interpreter.py`)

### 3.1 Container Evaluation Methods

```python
def visit_tome_literal(self, expr: TomeLiteral) -> Tome:
	"""Evaluate tome literal"""
	elements = [self.evaluate(element) for element in expr.elements]
	return Tome(elements)

def visit_grimoire_literal(self, expr: GrimoireLiteral) -> Grimoire:
	"""Evaluate grimoire literal"""
	pairs = {}
	for key_expr, value_expr in expr.pairs:
		key = self.evaluate(key_expr)
		value = self.evaluate(value_expr)
		pairs[key] = value
	return Grimoire(pairs)

def visit_codex_literal(self, expr: CodexLiteral) -> Codex:
	"""Evaluate codex literal"""
	elements = [self.evaluate(element) for element in expr.elements]
	return Codex(set(elements))

def visit_container_access(self, expr: ContainerAccess) -> Any:
	"""Evaluate container[index] access"""
	container = self.evaluate(expr.container)
	index = self.evaluate(expr.index)
	
	if isinstance(container, (Tome, Grimoire)):
		return container[index]
	elif isinstance(container, Codex):
		raise RuntimeError("Cannot index into codex (use 'seek' instead)")
	else:
		raise RuntimeError(f"Cannot index into {type(container)}")

def visit_container_slice(self, expr: ContainerSlice) -> Any:
	"""Evaluate container[start:end] slicing"""
	container = self.evaluate(expr.container)
	
	if not isinstance(container, Tome):
		raise RuntimeError("Slicing only supported on tomes")
	
	start = self.evaluate(expr.start) if expr.start else None
	end = self.evaluate(expr.end) if expr.end else None
	step = self.evaluate(expr.step) if expr.step else None
	
	return container.slice_tome(start, end, step)
```

### 3.2 Built-in Container Functions

```python
# Add to interpreter's built-in functions
def setup_container_builtins(self):
	"""Setup built-in container functions"""
	
	# Tome functions
	self.define_builtin("manifest_tome", self._builtin_manifest_tome)
	self.define_builtin("inscribe_tome", self._builtin_inscribe_tome)
	self.define_builtin("extract_tome", self._builtin_extract_tome)
	self.define_builtin("seek_tome", self._builtin_seek_tome)
	self.define_builtin("sort_tome", self._builtin_sort_tome)
	self.define_builtin("reverse_tome", self._builtin_reverse_tome)
	
	# Grimoire functions
	self.define_builtin("manifest_grimoire", self._builtin_manifest_grimoire)
	self.define_builtin("inscribe_grimoire", self._builtin_inscribe_grimoire)
	self.define_builtin("extract_grimoire", self._builtin_extract_grimoire)
	self.define_builtin("seek_grimoire", self._builtin_seek_grimoire)
	self.define_builtin("enumerate_keys", self._builtin_enumerate_keys)
	self.define_builtin("enumerate_values", self._builtin_enumerate_values)
	
	# Codex functions
	self.define_builtin("manifest_codex", self._builtin_manifest_codex)
	self.define_builtin("inscribe_codex", self._builtin_inscribe_codex)
	self.define_builtin("extract_codex", self._builtin_extract_codex)
	self.define_builtin("seek_codex", self._builtin_seek_codex)
	self.define_builtin("unite_codices", self._builtin_unite_codices)
	self.define_builtin("intersect_codices", self._builtin_intersect_codices)

def _builtin_manifest_tome(self, *args) -> Tome:
	"""manifest_tome() or manifest_tome([1,2,3])"""
	if len(args) == 0:
		return Tome()
	elif len(args) == 1:
		if isinstance(args[0], list):
			return Tome(args[0])
		else:
			return Tome([args[0]])
	else:
		return Tome(list(args))

def _builtin_inscribe_tome(self, tome: Tome, *items) -> None:
	"""inscribe_tome(my_tome, item1, item2, ...)"""
	if not isinstance(tome, Tome):
		raise RuntimeError("First argument must be a tome")
	tome.inscribe(*items)

def _builtin_extract_tome(self, tome: Tome, index: int) -> Any:
	"""extract_tome(my_tome, index)"""
	if not isinstance(tome, Tome):
		raise RuntimeError("First argument must be a tome")
	return tome.extract(index)
```

## Phase 4: Enhanced Syntax Support

### 4.1 Alternative Container Syntax

Support both magical and bracket syntax:

```python
# Magical syntax (primary)
bind my_tome = $TOME([1, 2, 3])
bind my_grimoire = $GRIMOIRE({$SCROLL("name"): $SCROLL("Alice"), $SCROLL("age"): SIGIL(25)})

# Bracket syntax (alternative)
bind my_tome = [1, 2, 3]
bind my_grimoire = {$SCROLL("name"): $SCROLL("Alice"), $SCROLL("age"): SIGIL(25)}
```

### 4.2 Container Comprehensions

```python
# Tome comprehensions
bind squares = $TOME([x multiplied by x for each x in range(10)])
bind evens = $TOME([x for each x in my_tome if enchanted x modulo 2 is equal to 0])

# Grimoire comprehensions  
bind word_lengths = $GRIMOIRE({word: length(word) for each word in word_list})
```

### 4.3 Iterator Integration

```python
# For loop with containers
for each item in my_tome:
	scry item

for each key, value in my_grimoire:
	scry $SCROLL("Key: ") added to key added to $SCROLL(", Value: ") added to value

# Tome slicing
bind subset = my_tome[SIGIL(1):SIGIL(5)]
bind every_other = my_tome[::SIGIL(2)]
```

## Phase 5: Advanced Container Features

### 5.1 Container Validation and Type Checking

```python
# grimoire/containers/typed_containers.py
class TypedTome(Tome):
	"""Tome that enforces element type"""
	
	def __init__(self, element_type: type, initial_data: Optional[List] = None):
		self._element_type = element_type
		if initial_data:
			for item in initial_data:
				if not isinstance(item, element_type):
					raise TypeError(f"All elements must be {element_type.__name__}")
		super().__init__(initial_data)
	
	def inscribe(self, *items) -> None:
		for item in items:
			if not isinstance(item, self._element_type):
				raise TypeError(f"Item must be {self._element_type.__name__}")
		super().inscribe(*items)
```

### 5.2 Lazy and Infinite Containers

```python
# grimoire/containers/lazy.py
class LazyTome(GrimoireContainer):
	"""Tome with lazy evaluation"""
	
	def __init__(self, generator_func):
		super().__init__()
		self._generator = generator_func
		self._cached = []
		self._exhausted = False
	
	def __getitem__(self, index: int):
		while len(self._cached) <= index and not self._exhausted:
			try:
				self._cached.append(next(self._generator))
			except StopIteration:
				self._exhausted = True
				break
		
		if index >= len(self._cached):
			raise IndexError("Index out of range")
		return self._cached[index]
```

### 5.3 Container Serialization

```python
# grimoire/containers/serialization.py
def serialize_container(container: GrimoireContainer) -> str:
	"""Serialize container to Grimoire code string"""
	if isinstance(container, Tome):
		elements = [repr(item) for item in container._elements]
		return f"$TOME([{', '.join(elements)}])"
	elif isinstance(container, Grimoire):
		pairs = [f"{repr(k)}: {repr(v)}" for k, v in container._elements.items()]
		return f"$GRIMOIRE({{{', '.join(pairs)}}})"
	elif isinstance(container, Codex):
		elements = [repr(item) for item in container._elements]
		return f"$CODEX({{{', '.join(elements)}}})"
	else:
		raise ValueError(f"Unknown container type: {type(container)}")

def deserialize_container(grimoire_code: str) -> GrimoireContainer:
	"""Deserialize Grimoire code string to container"""
	# Use the lexer and parser to convert string back to container
	from grimoire.lexer import GrimoireLexer
	from grimoire.parser import GrimoireParser
	from grimoire.interpreter import GrimoireInterpreter
	
	lexer = GrimoireLexer(grimoire_code)
	tokens = lexer.scan_tokens()
	parser = GrimoireParser(tokens)
	ast = parser.parse()
	interpreter = GrimoireInterpreter()
	return interpreter.evaluate(ast)
```

## Summary

This implementation plan provides:

1. **Complete container system** with magical syntax (`$TOME`, `$GRIMOIRE`, `$CODEX`)
2. **Lexer and parser integration** for both magical and traditional syntax
3. **Full interpreter support** with built-in functions
4. **Advanced features** like type checking, lazy evaluation, and serialization
5. **Consistent with existing codebase** using the same patterns and architecture

The containers integrate seamlessly with Grimoire's existing familiar system, AI components, and tag system, providing a solid foundation for complex game development scenarios.
