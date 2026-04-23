"""
SmartStack Lexer
Токенжуулагч: source code → token жагсаалт
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any


class TokenType(Enum):
    NUMBER      = auto()
    STRING      = auto()
    BOOLEAN     = auto()
    IDENT       = auto()
    OPERATOR    = auto()
    STACK_OP    = auto()
    BUILTIN     = auto()
    COLON       = auto()
    SEMICOLON   = auto()
    LBRACE      = auto()
    RBRACE      = auto()
    LBRACKET    = auto()
    RBRACKET    = auto()
    DOT         = auto()
    EOF         = auto()


OPERATORS  = {'+', '-', '*', '/', '>', '<', '='}
STACK_OPS  = {'dup', 'swap', 'drop', 'over'}
BUILTINS   = {'if', 'store', 'load', 'map', 'filter', 'help', 'print'}
BOOLEANS   = {'true', 'false'}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int = 0
    col: int = 0

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


class LexerError(Exception):
    def __init__(self, msg, line=0, col=0):
        super().__init__(f"LexerError (мөр {line}, баганa {col}): {msg}")


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def error(self, msg):
        raise LexerError(msg, self.line, self.col)

    def peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in (' ', '\t', '\n', '\r'):
                self.advance()
            elif ch == '#':  # SmartStack comment
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.advance()
            else:
                break

    def read_number(self) -> Token:
        line, col = self.line, self.col
        buf = ''
        while self.pos < len(self.source) and (self.peek().isdigit() or self.peek() == '.'):
            buf += self.advance()
        value = float(buf) if '.' in buf else int(buf)
        return Token(TokenType.NUMBER, value, line, col)

    def read_string(self) -> Token:
        line, col = self.line, self.col
        self.advance()  # skip opening "
        buf = ''
        while self.pos < len(self.source):
            ch = self.advance()
            if ch == '"':
                return Token(TokenType.STRING, buf, line, col)
            if ch == '\\':
                esc = self.advance()
                buf += {'n': '\n', 't': '\t', '\\': '\\', '"': '"'}.get(esc, esc)
            else:
                buf += ch
        self.error("Тэмдэгт мөр хаагдаагүй байна")

    def read_word(self) -> Token:
        line, col = self.line, self.col
        buf = ''
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() in '_-?!'):
            buf += self.advance()

        if buf in BOOLEANS:
            return Token(TokenType.BOOLEAN, buf == 'true', line, col)
        elif buf in OPERATORS:
            return Token(TokenType.OPERATOR, buf, line, col)
        elif buf in STACK_OPS:
            return Token(TokenType.STACK_OP, buf, line, col)
        elif buf in BUILTINS:
            return Token(TokenType.BUILTIN, buf, line, col)
        else:
            return Token(TokenType.IDENT, buf, line, col)

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                tokens.append(Token(TokenType.EOF, None, self.line, self.col))
                break

            ch = self.peek()
            line, col = self.line, self.col

            if ch.isdigit() or (ch == '-' and self.peek(1) and self.peek(1).isdigit()):
                # negative number
                if ch == '-':
                    self.advance()
                    tok = self.read_number()
                    tok.value = -tok.value
                    tok.line, tok.col = line, col
                    tokens.append(tok)
                else:
                    tokens.append(self.read_number())

            elif ch == '"':
                tokens.append(self.read_string())

            elif ch == ':':
                self.advance()
                tokens.append(Token(TokenType.COLON, ':', line, col))

            elif ch == ';':
                self.advance()
                tokens.append(Token(TokenType.SEMICOLON, ';', line, col))

            elif ch == '{':
                self.advance()
                tokens.append(Token(TokenType.LBRACE, '{', line, col))

            elif ch == '}':
                self.advance()
                tokens.append(Token(TokenType.RBRACE, '}', line, col))

            elif ch == '[':
                self.advance()
                tokens.append(Token(TokenType.LBRACKET, '[', line, col))

            elif ch == ']':
                self.advance()
                tokens.append(Token(TokenType.RBRACKET, ']', line, col))

            elif ch == '.':
                self.advance()
                tokens.append(Token(TokenType.DOT, '.', line, col))

            elif ch in OPERATORS:
                self.advance()
                tokens.append(Token(TokenType.OPERATOR, ch, line, col))

            elif ch.isalpha() or ch == '_':
                tokens.append(self.read_word())

            else:
                self.error(f"Тодорхойгүй тэмдэгт: '{ch}'")

        return tokens
