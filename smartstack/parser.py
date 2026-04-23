"""
SmartStack Parser
Token жагсаалт → AST  (Recursive Descent)
"""

from typing import List
from .lexer import Lexer, Token, TokenType
from .ast_nodes import (
    Node, ProgramNode, DefinitionNode,
    NumberNode, StringNode, BooleanNode,
    OperatorNode, StackOpNode, BuiltinNode,
    WordNode, BlockNode, ListNode
)


class ParseError(Exception):
    def __init__(self, msg, line=0, col=0):
        super().__init__(f"ParseError (мөр {line}, багана {col}): {msg}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek_type(self) -> TokenType:
        return self.current.type

    def advance(self) -> Token:
        tok = self.current
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def expect(self, ttype: TokenType, msg: str = "") -> Token:
        if self.current.type != ttype:
            tok = self.current
            raise ParseError(msg or f"{ttype.name} хүлээгдсэн, {tok.type.name} ирлээ",
                             tok.line, tok.col)
        return self.advance()

    # ─── Entry ───────────────────────────────────────────────
    def parse_program(self) -> ProgramNode:
        body = []
        while self.peek_type() != TokenType.EOF:
            if self.peek_type() == TokenType.COLON:
                body.append(self.parse_definition())
            else:
                node = self.parse_expr()
                if node is not None:
                    body.append(node)
        return ProgramNode(body=body)

    # ─── Definition  :  name  expr*  ; ───────────────────────
    def parse_definition(self) -> DefinitionNode:
        tok = self.expect(TokenType.COLON)
        name_tok = self.expect(TokenType.IDENT, "Word нэр хүлээгдсэн")
        body = []
        while self.peek_type() not in (TokenType.SEMICOLON, TokenType.EOF):
            node = self.parse_expr()
            if node is not None:
                body.append(node)
        self.expect(TokenType.SEMICOLON, "';' хүлээгдсэн (definition хаагдаагүй)")
        return DefinitionNode(name=name_tok.value, body=body,
                              line=tok.line, col=tok.col)

    # ─── Expression ──────────────────────────────────────────
    def parse_expr(self) -> Node:
        tok = self.current
        tt = tok.type

        if tt == TokenType.NUMBER:
            self.advance()
            return NumberNode(value=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.STRING:
            self.advance()
            return StringNode(value=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.BOOLEAN:
            self.advance()
            return BooleanNode(value=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.OPERATOR:
            self.advance()
            return OperatorNode(symbol=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.STACK_OP:
            self.advance()
            return StackOpNode(name=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.BUILTIN:
            self.advance()
            return BuiltinNode(name=tok.value, line=tok.line, col=tok.col)

        elif tt == TokenType.DOT:
            self.advance()
            return BuiltinNode(name='.', line=tok.line, col=tok.col)

        elif tt == TokenType.LBRACE:
            return self.parse_block()

        elif tt == TokenType.LBRACKET:
            return self.parse_list()

        elif tt == TokenType.IDENT:
            self.advance()
            return WordNode(name=tok.value, line=tok.line, col=tok.col)

        else:
            raise ParseError(f"Хүлээгдээгүй token: {tok.type.name} ({tok.value!r})",
                             tok.line, tok.col)

    # ─── Block  {  expr*  } ──────────────────────────────────
    def parse_block(self) -> BlockNode:
        tok = self.expect(TokenType.LBRACE)
        body = []
        while self.peek_type() not in (TokenType.RBRACE, TokenType.EOF):
            node = self.parse_expr()
            if node is not None:
                body.append(node)
        self.expect(TokenType.RBRACE, "'}' хүлээгдсэн (block хаагдаагүй)")
        return BlockNode(body=body, line=tok.line, col=tok.col)

    # ─── List  [  literal*  ] ────────────────────────────────
    def parse_list(self) -> ListNode:
        tok = self.expect(TokenType.LBRACKET)
        elements = []
        while self.peek_type() not in (TokenType.RBRACKET, TokenType.EOF):
            node = self.parse_expr()
            if node is not None:
                elements.append(node)
        self.expect(TokenType.RBRACKET, "']' хүлээгдсэн (list хаагдаагүй)")
        return ListNode(elements=elements, line=tok.line, col=tok.col)


# ─── Convenience function ─────────────────────────────────────
def parse(source: str) -> ProgramNode:
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse_program()
