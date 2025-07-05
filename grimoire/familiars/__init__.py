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

"""Familiar class registry and helper utilities.

This sub-package groups specialised `GrimoireFamiliar` subclasses while providing a
simple registry mechanism that lets the interpreter map the *familiar_type* string
passed to the `summon` built-in to the appropriate Python class.
"""
from __future__ import annotations

from typing import Dict, Type

# The base class is imported lazily to avoid circular imports at module load time
# (the interpreter defines GrimoireFamiliar inside its module scope).
import importlib

def _get_base_familiar_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")

# Registry -------------------------------------------------------------------
FAMILIAR_CLASS_REGISTRY: Dict[str, Type] = {}

# Mapping helper to attempt auto-import based on naming convention
_DEF_MODULE_TEMPLATE = "grimoire.familiars.{name}_familiar"


def register_familiar_class(name: str):
    """Decorator to register a new familiar subclass under a type *name*."""

    def decorator(cls):  # type: ignore
        FAMILIAR_CLASS_REGISTRY[name] = cls
        return cls

    return decorator


def get_familiar_class(name: str):
    """Return the registered subclass for *name* or the base class.

    If the class isn't registered yet we will try to *lazily* import a module
    following the convention ``grimoire.familiars.{name_lower}_familiar`` which
    should register itself as a side-effect of evaluation.
    """
    cls = FAMILIAR_CLASS_REGISTRY.get(name)
    if cls is not None:
        return cls

    # Attempt lazy import
    module_name = _DEF_MODULE_TEMPLATE.format(name=name.lower())
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        pass  # Silently ignore – caller will get base class

    return FAMILIAR_CLASS_REGISTRY.get(name, _get_base_familiar_cls())


# Public re-export
__all__ = [
    "register_familiar_class",
    "get_familiar_class",
    "FAMILIAR_CLASS_REGISTRY",
]