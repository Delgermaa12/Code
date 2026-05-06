# smartstack/desugar.py
import re

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


def desugar_human(source: str) -> str:
    import re

    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # set score to 85
        m = re.match(r"set\s+(\w+)\s+to\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'{value} "{name}" store')
            continue

        # if score is greater than 60
        m = re.match(r"if\s+(\w+)\s+is\s+greater\s+than\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value} >')
            result.append("{")
            continue

        # otherwise
        if line == "otherwise":
            result.append("}")
            result.append("{")
            continue

        # end
        if line == "end":
            result.append("}")
            result.append("if")
            continue

        # show something
        m = re.match(r"show\s+(.+)", line)
        if m:
            value = m.group(1)

            if value.startswith('"'):
                result.append(f"{value} .")
            else:
                result.append(f'"{value}" load .')
            continue

        raise Exception(f"Unknown human syntax: {line}")

    return "\n".join(result)

def desugar_mongolian(source: str) -> str:
    import re

    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # оноо гэдэг нь 85
        m = re.match(r"(\w+)\s+гэдэг\s+нь\s+(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'{value} "{name}" store')
            continue

        # хэрэв оноо 60-аас их бол
        m = re.match(r"хэрэв\s+(\w+)\s+(.+)-аас\s+их\s+бол", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value} >')
            result.append("{")
            continue

        # эсвэл
        if line == "эсвэл":
            result.append("}")
            result.append("{")
            continue

        # төгсөв
        if line == "төгсөв":
            result.append("}")
            result.append("if")
            continue

        # "ТЭНЦСЭН" харуул
        # оноо харуул
        m = re.match(r"(.+)\s+харуул", line)
        if m:
            value = m.group(1)

            if value.startswith('"'):
                result.append(f"{value} .")
            else:
                result.append(f'"{value}" load .')
            continue

        raise Exception(f"Unknown mongolian syntax: {line}")

    return "\n".join(result)

def desugar_code_like(source: str) -> str:
    lines = source.splitlines()
    result = []

    for line in lines:
        line = line.strip().rstrip(";")

        if not line or line.startswith("//"):
            continue

        # let score = 85
        m = re.match(r"let\s+(\w+)\s*=\s*(.+)", line)
        if m:
            name, value = m.groups()
            result.append(f'{value} "{name}" store')
            continue

        # print(score)
        m = re.match(r"print\((.+)\)", line)
        if m:
            value = m.group(1)
            if value.startswith('"'):
                result.append(f"{value} .")
            else:
                result.append(f'"{value}" load .')
            continue

        # if (score > 60) {
        m = re.match(r"if\s*\(\s*(\w+)\s*>\s*(.+)\s*\)\s*\{", line)
        if m:
            name, value = m.groups()
            result.append(f'"{name}" load {value} >')
            result.append("{")
            continue

        if line == "} else {":
            result.append("}{")
            continue

        if line == "}":
            result.append("} if")
            continue

    return "\n".join(result)