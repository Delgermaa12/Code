"""
SmartStack — Stack-based scripting language
"""
from .lexer       import Lexer, Token, TokenType, LexerError
from .ast_nodes   import *
from .parser      import Parser, parse, ParseError
from .interpreter import Interpreter, run, SmartStackError

__all__ = ['Lexer', 'Parser', 'Interpreter', 'parse', 'run', 'SmartStackError']
__version__ = '1.0.0'
