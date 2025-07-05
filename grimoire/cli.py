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
Grimoire Programming Language Command Line Interface

This module provides a command-line interface for running Grimoire programs.
"""

import argparse
import sys
from pathlib import Path

from .interpreter import interpret_grimoire

GRIMOIRE_VERSION = "1.0.0"

HELP_TEXT = {
    'main': """
🔮 Grimoire Programming Language - A Magical Language for Game Development

USAGE:
    grimoire [OPTIONS] [FILE]
    grimoire --interactive
    grimoire --help

ARGUMENTS:
    FILE                    Grimoire source file to execute (.grim extension)

OPTIONS:
    -i, --interactive       Start interactive REPL mode
    -v, --version          Show version information
    -h, --help             Show this help message
    --debug                Enable debug mode with verbose output

EXAMPLES:
    grimoire my_game.grim              # Run a Grimoire file
    grimoire --interactive             # Start interactive mode
    grimoire --help                    # Show this help

GETTING STARTED:
    Type 'grimoire --interactive' to start the interactive shell
    In the REPL, type 'help()' for language documentation
    
For more information, visit: https://github.com/grimoire-lang/grimoire
""",
    
    'repl': """
🎭 Grimoire Interactive REPL Commands:

BASIC COMMANDS:
    help()                  Show language help
    help('topic')          Show help for specific topic
    exit, quit, q          Exit the REPL
    clear                  Clear the screen
    version                Show Grimoire version

DEBUGGING:
    debug on/off           Toggle debug mode
    show_tokens            Show lexer tokens for next input
    show_ast              Show parser AST for next input

AGENT SYSTEM:
    agents()              List all active agents
    familiars()           List all active familiars
    spirits()             List all active spirits
    archons()             List all active archons
    wrangler()            Show familiar wrangler status

EXAMPLES:
    scry $SCROLL(Hello, World!)       # Print hello world
    bind x = 42                       # Declare variable
    ritual greet(): scry $SCROLL(Hi!) # Define function
    help('rituals')                   # Get help on functions
""",

    'version': f"""
🔮 Grimoire Programming Language v{GRIMOIRE_VERSION}

A magical programming language designed for game development with:
✨ Hierarchical autonomous agents (Archons → Spirits → Familiars)
🤝 Immutable pact system with true name security
📊 Familiar Wrangler for agent monitoring
🎯 Goal-oriented AI with emergent behaviors
🌍 Multidimensional plane system
🎨 Thematic keyword variants for different magic schools

Built with love for game developers who believe in magic.
"""
}


def main():
    """Main entry point for the Grimoire CLI."""
    parser = argparse.ArgumentParser(
        description="🔮 Grimoire Programming Language - A magical language for game development",
        prog="grimoire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  grimoire my_game.grim           Run a Grimoire file
  grimoire --interactive          Start interactive mode
  grimoire --help                 Show this help
  
For language help, use 'grimoire --interactive' then 'help()'
"""
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Grimoire source file to execute (.grim extension)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive REPL mode"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle version
    if args.version:
        print(HELP_TEXT['version'])
        return
    
    # Handle REPL or file execution
    if args.interactive or not args.file:
        run_repl()
    else:
        run_file(args.file, debug=args.debug)


def run_file(filepath: str, debug: bool = False) -> None:
    """Execute a Grimoire source file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"💥 Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if not path.suffix == ".grim":
        print(f"⚠️  Warning: Grimoire files should have .grim extension", file=sys.stderr)
    
    if debug:
        print(f"🔍 Debug: Running file '{filepath}'")
    
    try:
        source = path.read_text(encoding="utf-8")
        success = interpret_grimoire(source)
        if not success:
            sys.exit(1)
    except FileNotFoundError:
        print(f"💥 Error: Could not read file '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"💥 Error: File '{filepath}' is not valid UTF-8", file=sys.stderr)
        sys.exit(1)


def run_repl() -> None:
    """Run the interactive Read-Eval-Print Loop."""
    print(f"🔮 Grimoire REPL - Interactive Magical Programming")
    print(f"Version {GRIMOIRE_VERSION} - Type 'help()' for assistance")
    print("=" * 50)
    
    debug_mode = False
    show_tokens = False
    show_ast = False
    
    while True:
        try:
            # Get input
            prompt = "🧙 grimoire> " if not debug_mode else "🐛 debug> "
            line = input(prompt)
            
            # Handle special commands
            stripped_input = line.strip().lower()
            
            # Exit commands
            if stripped_input in ("exit", "quit", "q"):
                print("✨ Farewell, wizard! May your code be ever magical.")
                break
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Help commands
            if stripped_input in ['help', 'help()']:
                print_repl_help()
                continue
            elif stripped_input.startswith('help(') and stripped_input.endswith(')'):
                topic = line[5:-1].strip().strip('"\'')
                print_topic_help(topic)
                continue
            
            # Utility commands
            elif stripped_input == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif stripped_input == 'version':
                print(HELP_TEXT['version'])
                continue
            
            # Debug commands
            elif stripped_input == 'debug on':
                debug_mode = True
                print("🐛 Debug mode enabled")
                continue
            elif stripped_input == 'debug off':
                debug_mode = False
                print("✨ Debug mode disabled")
                continue
            elif stripped_input == 'show_tokens':
                show_tokens = True
                print("🔍 Will show tokens for next input")
                continue
            elif stripped_input == 'show_ast':
                show_ast = True
                print("🌳 Will show AST for next input")
                continue
            
            # Agent system commands
            elif stripped_input == 'agents()':
                show_agent_status()
                continue
            elif stripped_input == 'familiars()':
                show_familiar_status()
                continue
            elif stripped_input == 'wrangler()':
                show_wrangler_status()
                continue
            
            # Debug output
            if show_tokens:
                print("🔍 TOKENS:")
                try:
                    from .lexer import GrimoireLexer
                    lexer = GrimoireLexer(line)
                    tokens = lexer.scan_tokens()
                    for token in tokens:
                        if token.type.name != 'EOF':
                            print(f"  {token.type.name}: {token.lexeme}")
                except Exception as e:
                    print(f"  Lexer error: {e}")
                show_tokens = False
                print()
            
            if show_ast:
                print("🌳 AST:")
                try:
                    from .lexer import GrimoireLexer
                    from .parser import GrimoireParser
                    lexer = GrimoireLexer(line)
                    tokens = lexer.scan_tokens()
                    parser = GrimoireParser(tokens)
                    ast = parser.parse()
                    print(f"  {ast}")
                except Exception as e:
                    print(f"  Parser error: {e}")
                show_ast = False
                print()
            
            # Execute the line
            if debug_mode:
                print("⚡ Executing...")
            
            interpret_grimoire(line)
            
        except KeyboardInterrupt:
            print("\n💡 Use 'exit' to quit the REPL.")
        except EOFError:
            print("\n✨ Farewell, wizard!")
            break


def print_repl_help():
    """Print REPL help information."""
    print(HELP_TEXT['repl'])


def print_topic_help(topic):
    """Print help for a specific topic."""
    # Import the help system when needed
    try:
        from .help_system import get_help_for_topic
        help_text = get_help_for_topic(topic)
        if help_text and help_text.strip():
            print(help_text)
        else:
            print(f"❓ No help available for '{topic}'")
            print("💡 Try: help('keywords'), help('functions'), help('agents'), help('pacts')")
    except ImportError:
        print(f"❓ Help system not available for '{topic}'")
        print("💡 Basic help available with help()")


def show_agent_status():
    """Show status of all agents in the system."""
    print("🤖 Agent System Status:")
    print("  (This would show active agents - requires interpreter context)")
    

def show_familiar_status():
    """Show familiar-specific status."""
    print("🐾 Familiar Status:")
    print("  (This would show familiar details - requires interpreter context)")


def show_wrangler_status():
    """Show familiar wrangler status."""
    print("📊 Familiar Wrangler Status:")
    print("  (This would show wrangler details - requires interpreter context)")


if __name__ == "__main__":
    main()