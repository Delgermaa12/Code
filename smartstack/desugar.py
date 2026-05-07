import re
from smartstack.interpreter import suggest
HUMAN_KEYWORDS = {
    "set": [],
    "ask": [],
    "show": [],
    "calculate": [],
    "if": [],
    "otherwise": [],
    "end": [],
}

MN_KEYWORDS = {
    "гэдэг": [],
    "асуу": [],
    "харуул": [],
    "бод": [],
    "хэрэв": [],
    "эсвэл": [],
    "төгсөв": [],
}

CODE_KEYWORDS = {
    "let": [],
    "print": [],
    "input": [],
    "if": [],
    "else": [],
}

def syntax_error_with_suggestion(style: str, line: str, keywords: dict):
    first = line.strip().split()[0] if line.strip() else ""
    hint = suggest(first, keywords)

    msg = f"Unknown {style} syntax: {line}"
    if hint:
        msg += f"\nDid you mean: '{hint}' ?"

    raise Exception(msg)
def detect_style(filename: str) -> str:
    if filename.endswith(".human"):
        return "human"
    if filename.endswith(".mnss"):
        return "mn"
    if filename.endswith(".ssc"):
        return "code"
    return "stack"


def desugar(source: str, style: str) -> str:
    if style == "human":
        return desugar_human(source)
    if style == "mn":
        return desugar_mongolian(source)
    if style == "code":
        return desugar_code_like(source)
    return source


def value_token(x: str) -> str:
    x = x.strip()
    if x.startswith('"') and x.endswith('"'):
        return x
    if re.fullmatch(r"-?\d+(\.\d+)?", x):
        return x
    return f'"{x}" load'

def expr_to_stack(expr: str, lang="human") -> str:
    words = expr.strip().split()
    result = []

    ops = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "divide": "/",
        "нэмэх": "+",
        "хасах": "-",
        "үржих": "*",
        "хуваах": "/",
        "+": "+",
        "-": "-",
        "*": "*",
        "/": "/",
    }

    i = 0
    result.append(value_token(words[i]))
    i += 1

    while i < len(words):
        op_word = words[i]
        op = ops.get(op_word)

        if op is None:
            raise Exception(f"Unknown operator: {op_word}")

        i += 1

        if i >= len(words):
            raise Exception("Expression incomplete")

        result.append(value_token(words[i]))
        result.append(op)
        i += 1

    return " ".join(result)


def desugar_human(source: str) -> str:
    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        m = re.match(r"set\s+(\w+)\s+to\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'{value_token(value)} "{name}" store')
            continue

        m = re.match(r"ask\s+(\w+)", line)
        if m:
            name = m.group(1)
            result.append(f'"{name}" input')
            continue

        m = re.match(r"calculate\s+(\w+)\s+as\s+(.+)", line)
        if m:
            name, expr = m.groups()
            result.append(f'{expr_to_stack(expr)} "{name}" store')
            continue

        m = re.match(r"show\s+(.+)", line)
        if m:
            value = m.group(1)
            result.append(f"{value_token(value)} .")
            continue

        m = re.match(r"if\s+(\w+)\s+is\s+greater\s+than\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} >')
            result.append("{")
            continue

        m = re.match(r"if\s+(\w+)\s+is\s+equal\s+to\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} =')
            result.append("{")
            continue

        if line == "otherwise":
            result.append("}")
            result.append("{")
            continue

        if line == "end":
            result.append("}")
            result.append("if")
            continue

        syntax_error_with_suggestion("human", line, HUMAN_KEYWORDS)

    return "\n".join(result)


def desugar_mongolian(source: str) -> str:
    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        m = re.match(r"(\w+)\s+гэдэг\s+нь\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'{value_token(value)} "{name}" store')
            continue

        m = re.match(r"(\w+)\s+асуу", line)
        if m:
            name = m.group(1)
            result.append(f'"{name}" input')
            continue

        m = re.match(r"(\w+)\s+бод\s+(.+)", line)
        if m:
            name, expr = m.groups()
            result.append(f'{expr_to_stack(expr, "mn")} "{name}" store')
            continue

        m = re.match(r"(.+)\s+харуул", line)
        if m:
            value = m.group(1)
            result.append(f"{value_token(value)} .")
            continue

        m = re.match(r"хэрэв\s+(\w+)\s+(.+)-аас\s+их\s+бол", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} >')
            result.append("{")
            continue

        m = re.match(r"хэрэв\s+(\w+)\s+(.+)-тай\s+тэнцүү\s+бол", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} =')
            result.append("{")
            continue

        if line == "эсвэл":
            result.append("}")
            result.append("{")
            continue

        if line == "төгсөв":
            result.append("}")
            result.append("if")
            continue

        syntax_error_with_suggestion("mongolian", line, MN_KEYWORDS)

    return "\n".join(result)


def code_expr_to_stack(expr: str) -> str:
    expr = expr.strip()

    for op in ["+", "-", "*", "/"]:
        if op in expr:
            parts = [p.strip() for p in expr.split(op)]
            stack = value_token(parts[0])
            for p in parts[1:]:
                stack += " " + value_token(p) + " " + op
            return stack

    return value_token(expr)


def desugar_code_like(source: str) -> str:
    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip().rstrip(";")

        if not line or line.startswith("//"):
            continue

        m = re.match(r"let\s+(\w+)\s*=\s*(.+)", line)
        if m:
            name, expr = m.groups()
            result.append(f'{code_expr_to_stack(expr)} "{name}" store')
            continue

        m = re.match(r"input\((\w+)\)", line)
        if m:
            name = m.group(1)
            result.append(f'"{name}" input')
            continue

        m = re.match(r"print\((.+)\)", line)
        if m:
            value = m.group(1)
            result.append(f"{value_token(value)} .")
            continue

        m = re.match(r"if\s*\(\s*(\w+)\s*>\s*(.+)\s*\)\s*\{", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} >')
            result.append("{")
            continue

        m = re.match(r"if\s*\(\s*(\w+)\s*==\s*(.+)\s*\)\s*\{", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value_token(value)} =')
            result.append("{")
            continue

        if line == "} else {":
            result.append("}")
            result.append("{")
            continue

        if line == "}":
            result.append("}")
            result.append("if")
            continue

        syntax_error_with_suggestion("code-like", line, CODE_KEYWORDS)

    return "\n".join(result)