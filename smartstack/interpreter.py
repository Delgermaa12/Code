"""
SmartStack Interpreter
AST + Runtime State → үр дүн

Runtime State = (Stack, Dictionary, Storage, Output)
"""

from typing import List, Any, Dict, Optional
from dataclasses import dataclass, field
from .ast_nodes import (
    Node, ProgramNode, DefinitionNode,
    NumberNode, StringNode, BooleanNode,
    OperatorNode, StackOpNode, BuiltinNode,
    WordNode, BlockNode, ListNode
)


# ─── Runtime Errors ──────────────────────────────────────────
class SmartStackError(Exception):
    """SmartStack runtime алдааны суурь класс"""
    pass

class StackUnderflowError(SmartStackError):
    pass

class TypeError_(SmartStackError):
    pass

class DivisionByZeroError(SmartStackError):
    pass

class UnknownWordError(SmartStackError):
    pass

class MissingStorageKeyError(SmartStackError):
    pass

class InvalidIfOperandError(SmartStackError):
    pass


# ─── Levenshtein Distance ────────────────────────────────────
def levenshtein(s: str, t: str) -> int:
    """
    Levenshtein зайг тооцоолно — Diagnostic давхаргад ашиглана.
    Dynamic Programming алгоритм.
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i          # устгах
    for j in range(n + 1):
        dp[0][j] = j          # оруулах

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # устгах
                    dp[i][j - 1],      # оруулах
                    dp[i - 1][j - 1]   # солих
                )
    return dp[m][n]


def suggest(unknown: str, dictionary: Dict) -> Optional[str]:
    """
    Threshold <= 2 бол хамгийн ойр үгийг буцаана.
    """
    best_word, best_dist = None, float('inf')
    for word in dictionary:
        d = levenshtein(unknown, word)
        if d < best_dist:
            best_dist = d
            best_word = word
    return best_word if best_dist <= 2 else None

@dataclass
class State:
    stack:      List[Any]       = field(default_factory=list)
    dictionary: Dict[str, List] = field(default_factory=dict)
    storage:    Dict[str, Any]  = field(default_factory=dict)
    output:     List[str]       = field(default_factory=list)

    def push(self, value: Any):
        self.stack.append(value)

    def pop(self, context: str = "") -> Any:
        if not self.stack:
            raise StackUnderflowError(
                f"Stack Underflow: '{context}' команд гүйцэтгэхэд стек хоосон байна"
            )
        return self.stack.pop()

    def peek(self) -> Any:
        if not self.stack:
            raise StackUnderflowError("Стек хоосон байна")
        return self.stack[-1]

    def require_n(self, n: int, context: str):
        if len(self.stack) < n:
            raise StackUnderflowError(
                f"Stack Underflow: '{context}' командд {n} утга шаардлагатай, "
                f"стекд {len(self.stack)} байна"
            )


# ─── Built-in help text ──────────────────────────────────────
HELP_TEXT = """
╔══════════════════════════════════════════════════════════╗
║            SmartStack — Командын тайлбар                ║
╠══════════════════╦═══════════════╦════════════════════════╣
║ Команд           ║ Stack Effect  ║ Тайлбар                ║
╠══════════════════╬═══════════════╬════════════════════════╣
║ +  -  *  /       ║ (a b -- res)  ║ Арифметик үйлдлүүд     ║
║ >  <  =          ║ (a b -- bool) ║ Харьцуулалт            ║
║ dup              ║ (a -- a a)    ║ Орой утгыг хуулах      ║
║ swap             ║ (a b -- b a)  ║ Дээд 2 утгыг солих     ║
║ drop             ║ (a -- )       ║ Орой устгах             ║
║ over             ║ (a b -- a b a)║ 2-р утгыг хуулах       ║
║ .                ║ (a -- )       ║ Орой хэвлэх             ║
║ store            ║ (val key -- ) ║ Хадгалах                ║
║ load             ║ (key -- val)  ║ Ачаалах                 ║
║ if               ║(b t f -- )    ║ Нөхцөлт гүйцэтгэл      ║
║ help             ║ ( -- )        ║ Энэ тусламж             ║
║ : name ... ;     ║               ║ Word тодорхойлох        ║
╚══════════════════╩═══════════════╩════════════════════════╝
"""


# ─── Interpreter ─────────────────────────────────────────────
class Interpreter:
    def __init__(self):
        self.state = State()
        # Built-in word dictionary-г эхлүүлнэ
        self._init_builtins()

    def _init_builtins(self):
        """Built-in word-уудыг dictionary-д бүртгэнэ"""
        pass  # Built-in-ууд evalBuiltin-д шууд зохицуулагдана

    def run(self, source: str) -> State:
        """Source code-ийг гүйцэтгэж State буцаана"""
        from .parser import parse
        ast = parse(source)
        self.eval_program(ast)
        return self.state

    # ─── Program ─────────────────────────────────────────────
    def eval_program(self, program: ProgramNode):
        for node in program.body:
            self.eval_node(node)

    # ─── Node dispatch ───────────────────────────────────────
    def eval_node(self, node: Node):
        if isinstance(node, NumberNode):
            self.state.push(node.value)

        elif isinstance(node, StringNode):
            self.state.push(node.value)

        elif isinstance(node, BooleanNode):
            self.state.push(node.value)

        elif isinstance(node, OperatorNode):
            self.eval_operator(node.symbol, node)

        elif isinstance(node, StackOpNode):
            self.eval_stack_op(node.name, node)

        elif isinstance(node, BuiltinNode):
            self.eval_builtin(node.name, node)

        elif isinstance(node, DefinitionNode):
            # Word-ийг dictionary-д бүртгэнэ, гүйцэтгэхгүй
            self.state.dictionary[node.name] = node.body

        elif isinstance(node, WordNode):
            self.eval_word(node)

        elif isinstance(node, BlockNode):
            # Блокийг quotation байдлаар стек дээр тавина
            self.state.push(node)

        elif isinstance(node, ListNode):
            # List literal үүсгэнэ
            lst = [self._materialize_literal(e) for e in node.elements]
            self.state.push(lst)

        else:
            raise SmartStackError(f"Тодорхойгүй AST node: {type(node).__name__}")

    def _materialize_literal(self, node: Node) -> Any:
        if isinstance(node, NumberNode):  return node.value
        if isinstance(node, StringNode):  return node.value
        if isinstance(node, BooleanNode): return node.value
        raise SmartStackError(f"List дотор literal бус node байна: {type(node).__name__}")

    # ─── Operators ───────────────────────────────────────────
    def eval_operator(self, op: str, node: Node):
        self.state.require_n(2, op)
        b = self.state.pop(op)
        a = self.state.pop(op)

        # Төрөл шалгах
        if op in ('+', '-', '*', '/') and not (
            isinstance(a, (int, float)) and isinstance(b, (int, float))
            and not isinstance(a, bool) and not isinstance(b, bool)
        ):
            raise TypeError_(
                f"Type Error: '{op}' арифметик тоон утга шаардана, "
                f"харин {type(a).__name__} ба {type(b).__name__} ирлээ"
            )

        if op == '+':   self.state.push(a + b)
        elif op == '-': self.state.push(a - b)
        elif op == '*': self.state.push(a * b)
        elif op == '/':
            if b == 0:
                raise DivisionByZeroError("Division by Zero: тэгд хуваах боломжгүй")
            # Бүхэл хуваарь үр дүн бүхэл хэлбэрт байна
            result = a / b
            self.state.push(int(result) if result == int(result) else result)
        elif op == '>': self.state.push(a > b)
        elif op == '<': self.state.push(a < b)
        elif op == '=': self.state.push(a == b)
        else:
            raise SmartStackError(f"Тодорхойгүй оператор: '{op}'")

    # ─── Stack Operations ────────────────────────────────────
    def eval_stack_op(self, name: str, node: Node):
        if name == 'dup':
            a = self.state.pop('dup')
            self.state.push(a)
            self.state.push(a)

        elif name == 'swap':
            self.state.require_n(2, 'swap')
            b = self.state.pop('swap')
            a = self.state.pop('swap')
            self.state.push(b)
            self.state.push(a)

        elif name == 'drop':
            self.state.pop('drop')

        elif name == 'over':
            self.state.require_n(2, 'over')
            b = self.state.pop('over')
            a = self.state.pop('over')
            self.state.push(a)
            self.state.push(b)
            self.state.push(a)

        else:
            raise SmartStackError(f"Тодорхойгүй stack op: '{name}'")

    # ─── Built-ins ───────────────────────────────────────────
    def eval_builtin(self, name: str, node: Node):
        if name == '.':
            val = self.state.pop('.')
            out = self._format_value(val)
            self.state.output.append(out)
            print(out)

        elif name == 'store':
            self.state.require_n(2, 'store')
            key = self.state.pop('store')
            val = self.state.pop('store')
            if not isinstance(key, str):
                raise TypeError_(
                    f"Type Error: 'store' key нь string байх ёстой, {type(key).__name__} ирлээ"
                )
            self.state.storage[key] = val

        elif name == 'load':
            key = self.state.pop('load')
            if not isinstance(key, str):
                raise TypeError_(
                    f"Type Error: 'load' key нь string байх ёстой, {type(key).__name__} ирлээ"
                )
            if key not in self.state.storage:
                raise MissingStorageKeyError(
                    f"Missing Storage Key: '{key}' storage-д байхгүй"
                )
            self.state.push(self.state.storage[key])

        elif name == 'if':
            self.state.require_n(3, 'if')
            else_block = self.state.pop('if')
            then_block = self.state.pop('if')
            condition  = self.state.pop('if')

            if not isinstance(condition, bool):
                raise InvalidIfOperandError(
                    f"Invalid If Operand: нөхцөл boolean байх ёстой, {type(condition).__name__} ирлээ"
                )
            if not isinstance(then_block, BlockNode) or not isinstance(else_block, BlockNode):
                raise InvalidIfOperandError(
                    "Invalid If Operand: then/else блокууд { } хэлбэрт байх ёстой"
                )

            chosen = then_block if condition else else_block
            for sub in chosen.body:
                self.eval_node(sub)

        elif name == 'map':
            self.state.require_n(2, 'map')
            block = self.state.pop('map')
            lst   = self.state.pop('map')
            if not isinstance(lst, list):
                raise TypeError_("Type Error: 'map' list шаардана")
            if not isinstance(block, BlockNode):
                raise TypeError_("Type Error: 'map' block { } шаардана")

            result = []
            for item in lst:
                self.state.push(item)
                for sub in block.body:
                    self.eval_node(sub)
                result.append(self.state.pop('map'))
            self.state.push(result)

        elif name == 'filter':
            self.state.require_n(2, 'filter')
            block = self.state.pop('filter')
            lst   = self.state.pop('filter')
            if not isinstance(lst, list):
                raise TypeError_("Type Error: 'filter' list шаардана")
            if not isinstance(block, BlockNode):
                raise TypeError_("Type Error: 'filter' block { } шаардана")

            result = []
            for item in lst:
                self.state.push(item)
                for sub in block.body:
                    self.eval_node(sub)
                keep = self.state.pop('filter')
                if keep:
                    result.append(item)
            self.state.push(result)

        elif name == 'help':
            print(HELP_TEXT)

        elif name == 'print':
            # Alias for '.'
            self.eval_builtin('.', node)

        else:
            raise SmartStackError(f"Тодорхойгүй builtin: '{name}'")

    # ─── User-defined Word ───────────────────────────────────
    def eval_word(self, node: WordNode):
        name = node.name
        if name in self.state.dictionary:
            for sub in self.state.dictionary[name]:
                self.eval_node(sub)
        else:
            # Diagnostic: Did you mean?
            # Built-in болон хэрэглэгчийн word-уудыг хамтад нь харьцуулна
            all_words = dict.fromkeys(
                list(self.state.dictionary.keys()) +
                ['dup', 'swap', 'drop', 'over', 'if', 'store', 'load',
                 'map', 'filter', 'help', '+', '-', '*', '/', '>', '<', '=']
            )
            hint = suggest(name, all_words)
            msg = f"Unknown Word: '{name}' тодорхойлогдоогүй байна"
            if hint:
                msg += f"\nDid you mean: '{hint}' ?"
            raise UnknownWordError(msg)

    # ─── Formatting ──────────────────────────────────────────
    def _format_value(self, val: Any) -> str:
        if isinstance(val, bool):
            return 'true' if val else 'false'
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        if isinstance(val, list):
            return '[ ' + ' '.join(self._format_value(v) for v in val) + ' ]'
        if isinstance(val, str):
            return f'"{val}"'
        return str(val)


# ─── Convenience ─────────────────────────────────────────────
def run(source: str) -> State:
    """Source code-ийг шууд гүйцэтгэх"""
    interp = Interpreter()
    return interp.run(source)
