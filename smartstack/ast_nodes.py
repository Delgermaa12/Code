"""
SmartStack AST Node тодорхойлолтууд
"""
from dataclasses import dataclass, field
from typing import List, Any, Union


# ─── Base ────────────────────────────────────────────────────
@dataclass
class Node:
    """Бүх AST node-уудын суурь класс"""
    line: int = field(default=0, repr=False)
    col: int  = field(default=0, repr=False)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


# ─── Literals ────────────────────────────────────────────────
@dataclass
class NumberNode(Node):
    value: Union[int, float] = 0

    def __repr__(self):
        return f"NumberNode({self.value})"


@dataclass
class StringNode(Node):
    value: str = ""

    def __repr__(self):
        return f'StringNode("{self.value}")'


@dataclass
class BooleanNode(Node):
    value: bool = False

    def __repr__(self):
        return f"BooleanNode({self.value})"


# ─── Operations ──────────────────────────────────────────────
@dataclass
class OperatorNode(Node):
    symbol: str = ""

    def __repr__(self):
        return f"OperatorNode({self.symbol!r})"


@dataclass
class StackOpNode(Node):
    name: str = ""

    def __repr__(self):
        return f"StackOpNode({self.name!r})"


@dataclass
class BuiltinNode(Node):
    name: str = ""

    def __repr__(self):
        return f"BuiltinNode({self.name!r})"


# ─── Word ────────────────────────────────────────────────────
@dataclass
class WordNode(Node):
    name: str = ""

    def __repr__(self):
        return f"WordNode({self.name!r})"


# ─── Compound ────────────────────────────────────────────────
@dataclass
class BlockNode(Node):
    body: List[Node] = field(default_factory=list)

    def __repr__(self):
        return f"BlockNode([{', '.join(repr(n) for n in self.body)}])"


@dataclass
class ListNode(Node):
    elements: List[Node] = field(default_factory=list)

    def __repr__(self):
        return f"ListNode([{', '.join(repr(n) for n in self.elements)}])"


@dataclass
class DefinitionNode(Node):
    name: str = ""
    body: List[Node] = field(default_factory=list)

    def __repr__(self):
        return f"DefinitionNode({self.name!r}, [{', '.join(repr(n) for n in self.body)}])"


# ─── Root ────────────────────────────────────────────────────
@dataclass
class ProgramNode(Node):
    body: List[Node] = field(default_factory=list)

    def __repr__(self):
        return f"ProgramNode([{', '.join(repr(n) for n in self.body)}])"
