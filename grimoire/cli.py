#!/usr/bin/env python3
"""
Grimoire Programming Language Command Line Interface

This module provides a command-line interface for running Grimoire programs.
"""

import argparse
import sys
from pathlib import Path

from .interpreter import interpret_grimoire


def main():
    """Main entry point for the Grimoire CLI."""
    parser = argparse.ArgumentParser(
        description="Grimoire Programming Language Interpreter",
        prog="grimoire"
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Grimoire source file to execute"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive REPL"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="Grimoire 0.1.0"
    )
    
    args = parser.parse_args()
    
    if args.interactive or not args.file:
        run_repl()
    else:
        run_file(args.file)


def run_file(filepath: str) -> None:
    """Execute a Grimoire source file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if not path.suffix == ".grim":
        print(f"Warning: Grimoire files should have .grim extension", file=sys.stderr)
    
    try:
        source = path.read_text(encoding="utf-8")
        success = interpret_grimoire(source)
        if not success:
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Could not read file '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: File '{filepath}' is not valid UTF-8", file=sys.stderr)
        sys.exit(1)


def run_repl() -> None:
    """Run the interactive Read-Eval-Print Loop."""
    print("Grimoire Programming Language v0.1.0")
    print("Type 'exit' or 'quit' to leave the REPL")
    print("=" * 40)
    
    while True:
        try:
            # Get input
            line = input("grimoire> ")
            
            # Check for exit commands
            if line.strip().lower() in ("exit", "quit", "q"):
                print("Farewell, mage!")
                break
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Execute the line
            interpret_grimoire(line)
            
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()