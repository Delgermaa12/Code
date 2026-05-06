# main.py
import sys

from smartstack import run, parse
from smartstack.desugar import detect_style, desugar

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py run file.human")
        print("  python main.py run file.mnss")
        print("  python main.py run file.ssc")
        print("  python main.py run file.ss")
        return

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()

    style = detect_style(filename)
    stack_code = desugar(source, style)

    if command == "run":
        run(stack_code)

    elif command == "check":
        ast = parse(stack_code)
        print("Syntax OK")
        print(ast)

    elif command == "show-core":
        print(stack_code)

    else:
        print("Unknown command")

if __name__ == "__main__":
    main()