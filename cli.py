#!/usr/bin/env python3
"""
SmartStack CLI
Хэрэглээ:
  python cli.py run example.ss
  python cli.py repl
  python cli.py test
"""

import sys
import os
try:
    import readline  # REPL history support (Linux/Mac)
except ImportError:
    pass  # Windows-д байхгүй, зүгээр

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartstack.interpreter import Interpreter, run as ss_run, SmartStackError
from smartstack.lexer import LexerError
from smartstack.parser import ParseError

BANNER = """
╔══════════════════════════════════════════════╗
║   SmartStack v1.0  — Stack-based language   ║
║   'help' гэж бичнэ үү        Ctrl+C: гарах  ║
╚══════════════════════════════════════════════╝
"""

def cmd_run(filepath: str):
    """Файл гүйцэтгэнэ"""
    if not os.path.exists(filepath):
        print(f"Алдаа: '{filepath}' файл олдсонгүй")
        sys.exit(1)
    with open(filepath, encoding='utf-8') as f:
        source = f.read()
    try:
        interp = Interpreter()
        interp.run(source)
    except (SmartStackError, LexerError, ParseError) as e:
        print(f"\n⚠️  {e}")
        sys.exit(1)


def cmd_repl():
    """Интерактив REPL горим"""
    print(BANNER)
    interp = Interpreter()
    buf = []

    while True:
        try:
            prompt = "ss> " if not buf else "... "
            line = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nТантай уулзтал!")
            break

        if line.lower() in ('exit', 'quit'):
            print("Тантай уулзтал!")
            break

        buf.append(line)
        source = ' '.join(buf)

        # Нээлттэй { эсвэл [ байвал үргэлжлүүлэн авна
        if source.count('{') > source.count('}') or \
           source.count('[') > source.count(']') or \
           source.count(':') > source.count(';'):
            continue

        if source.strip():
            try:
                before_stack = list(interp.state.stack)
                interp.run(source)
                after_stack = interp.state.stack
                if after_stack != before_stack:
                    print(f"  стек: {after_stack}")
            except (SmartStackError, LexerError, ParseError) as e:
                print(f"  ⚠️  {e}")

        buf = []


def cmd_test():
    """Тест ажиллуулна"""
    test_path = os.path.join(os.path.dirname(__file__), 'tests', 'test_smartstack.py')
    os.system(f"{sys.executable} {test_path}")


def usage():
    print("Хэрэглээ:")
    print("  python cli.py run <file.ss>   — Файл гүйцэтгэх")
    print("  python cli.py repl            — Интерактив горим")
    print("  python cli.py test            — Тест ажиллуулах")
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        cmd_repl()
    elif sys.argv[1] == 'run':
        if len(sys.argv) < 3:
            usage()
        cmd_run(sys.argv[2])
    elif sys.argv[1] == 'repl':
        cmd_repl()
    elif sys.argv[1] == 'test':
        cmd_test()
    else:
        usage()
