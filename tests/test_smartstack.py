import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartstack.interpreter import (
    Interpreter, run,
    StackUnderflowError, TypeError_, DivisionByZeroError,
    UnknownWordError, MissingStorageKeyError, InvalidIfOperandError
)
from smartstack.lexer import LexerError
from smartstack.parser import ParseError
passed = 0
failed = 0

def test(name: str, source: str, expected_output: list, expected_stack: list = None):
    global passed, failed
    try:
        interp = Interpreter()
        state  = interp.run(source)
        actual = state.output

        ok_out   = actual == [str(e) if not isinstance(e, str) else e for e in expected_output]
        ok_stack = (expected_stack is None) or (state.stack == expected_stack)

        if ok_out and ok_stack:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f" FAIL  {name}")
            print(f"         Оролт   : {source.strip()}")
            print(f"         Хүлээсэн: output={expected_output}, stack={expected_stack}")
            print(f"         Авсан   : output={actual}, stack={state.stack}")
            failed += 1
    except Exception as e:
        print(f"  FAIL  {name}  → Exception: {e}")
        failed += 1


def test_error(name: str, source: str, error_class):
    global passed, failed
    try:
        run(source)
        print(f"  FAIL  {name}  → Алдаа гараагүй (гарах ёстой байсан)")
        failed += 1
    except error_class as e:
        print(f"  PASS  {name}  → {error_class.__name__}: {e}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}  → Буруу алдааны төрөл: {type(e).__name__}: {e}")
        failed += 1


def section(title: str):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")


section("1. Арифметик үйлдлүүд (Arithmetic)")

test("T01 — Нийлбэр",          "3 4 + .",            ['"7"' if False else "7"])
def run_and_output(source):
    interp = Interpreter()
    state  = interp.run(source)
    return state.output

def test2(name, source, expected_outputs, expected_stack=None):
    global passed, failed
    try:
        interp = Interpreter()
        state  = interp.run(source)
        actual = state.output
        ok_out   = actual == expected_outputs
        ok_stack = (expected_stack is None) or (state.stack == expected_stack)
        if ok_out and ok_stack:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}")
            print(f"         Оролт   : {repr(source.strip())}")
            print(f"         Хүлээсэн output: {expected_outputs}")
            print(f"         Авсан output   : {actual}")
            if expected_stack is not None:
                print(f"         Хүлээсэн stack : {expected_stack}")
                print(f"         Авсан stack    : {state.stack}")
            failed += 1
    except Exception as e:
        print(f"  FAIL  {name}  → Exception: {type(e).__name__}: {e}")
        failed += 1

section("1. Арифметик үйлдлүүд (Arithmetic)")
test2("T01 — Нийлбэр 3+4=7",          "3 4 + .",       ["7"])
test2("T02 — Зөрүү 10-2=8",           "10 2 - .",      ["8"])
test2("T03 — Үржвэр 6×7=42",          "6 7 * .",       ["42"])
test2("T04 — Хуваарь 20÷5=4",         "20 5 / .",      ["4"])
test2("T05 — Бодит тоо 3.5+1.5=5",    "3.5 1.5 + .",   ["5"])
test2("T06 — Харьцуулалт 5>3 = true", "5 3 > .",       ["true"])
test2("T07 — Харьцуулалт 2>9 = false","2 9 > .",       ["false"])
test2("T08 — Тэгш байдал 4=4 = true", "4 4 = .",       ["true"])
test2("T09 — Тэгш байдал 3=5 = false","3 5 = .",       ["false"])
test2("T10 — Олон үйлдэл 3 4+5×=35", "3 4 + 5 * .",   ["35"])
test2("T11 — Постфикс (3+4×5=23)",    "3 4 5 * + .",   ["23"])

section("2. Стекийн үйлдлүүд (Stack Operations)")
test2("T12 — dup: 10²=100",           "10 dup * .",    ["100"])
test2("T13 — swap: 1 2 swap → 2 1",   "1 2 swap . .",  ["1", "2"])
test2("T14 — drop: 5 drop 9",         "5 drop 9 .",    ["9"])
test2("T15 — over: 3 4 over",         "3 4 over . . .",["3", "4", "3"])
test2("T16 — dup dup + (4+4=8)",      "4 dup + .",     ["8"])
test2("T17 — Олон стек үйлдэл",       "1 2 3 drop swap . .", ["1", "2"])
section("3. Word тодорхойлолт (Word Definition)")
test2("T18 — square: 5²=25",
      ": square dup * ; 5 square .", ["25"])
test2("T19 — cube: 3³=27",
      ": cube dup dup * * ; 3 cube .", ["27"])
test2("T20 — double: 7×2=14",
      ": double 2 * ; 7 double .", ["14"])
test2("T21 — Word дарааллаар дуудах",
      ": square dup * ; : quad square square ; 2 quad .", ["16"])
test2("T22 — Word болон арифметик хослуулах",
      ": inc 1 + ; 9 inc .", ["10"])

section("4. Named Storage (store / load)")
test2("T23 — store/load: x=100",
      '100 "x" store "x" load .', ["100"])
test2("T24 — store/load + арифметик",
      '100 "x" store "x" load 20 + .', ["120"])
test2("T25 — Олон storage утга",
      '5 "a" store 3 "b" store "a" load "b" load + .', ["8"])
test2("T26 — Storage дарж бичих",
      '10 "x" store 99 "x" store "x" load .', ["99"])

section("5. Нөхцөлт гүйцэтгэл (Conditional if)")
test2("T27 — if true branch",
      '1500 1000 > { "Yes" } { "No" } if .', ['"Yes"'])
test2("T28 — if false branch",
      '5 10 > { "big" } { "small" } if .', ['"small"'])
test2("T29 — if with boolean literal",
      'true { "T" } { "F" } if .', ['"T"'])
test2("T30 — if false literal",
      'false { "T" } { "F" } if .', ['"F"'])
test2("T31 — if with calculation",
      '5 3 > { 1 } { 0 } if .', ["1"])

section("6. List болон map/filter (Phase 2)")
test2("T32 — map: [10 20 30] × 2",
      "[ 10 20 30 ] { 2 * } map .", ["[ 20 40 60 ]"])
test2("T33 — filter: >20 байх утгууд",
      "[ 10 20 30 40 ] { 20 > } filter .", ["[ 30 40 ]"])

interp_tmp = Interpreter()
interp_tmp.run("[ 10 30 50 ] { 20 > } filter .")
if interp_tmp.state.output == ["[ 30 50 ]"]:
    print("  PASS  T33b — filter: [10 30 50] filter >20 = [30 50]")
    passed += 1
else:
    print(f"  FAIL  T33b — filter output: {interp_tmp.state.output}")
    failed += 1

section("7. Нэгдсэн жишээ программ (Integration)")
test2("T34 — Нэгдсэн: square + storage + if",
      """: square dup * ;
9 square
"ans" store
"ans" load 10 >
{ "large" }
{ "small" }
if .""",
      ['"large"'])

test2("T35 — Олон word + storage",
      """: double 2 * ;
: triple 3 * ;
5 double "d" store
5 triple "t" store
"d" load "t" load + .""",
      ["25"]) 

section("8. Stack Underflow алдаанууд")
test_error("N01 — + хоосон стек дээр",       "+",           StackUnderflowError)
test_error("N02 — * нэг утгатай стек дээр",  "5 *",         StackUnderflowError)
test_error("N03 — dup хоосон стек",          "dup",         StackUnderflowError)
test_error("N04 — swap нэг утга",             "5 swap",      StackUnderflowError)
test_error("N05 — drop хоосон стек",         "drop",        StackUnderflowError)
test_error("N06 — . хоосон стек",            ".",           StackUnderflowError)
test_error("N07 — over нэг утга",             "5 over",      StackUnderflowError)

section("9. Type Error алдаанууд")
test_error("N08 — string + number",    '"abc" 5 +',     TypeError_)
test_error("N09 — bool * number",      'true 5 *',      TypeError_)
test_error("N10 — store key not str",  '10 20 store',   TypeError_)
test_error("N11 — load key not str",   '42 load',       TypeError_)

section("10. Division by Zero")
test_error("N12 — 10 / 0",            "10 0 /",        DivisionByZeroError)
test_error("N13 — 0 / 0",             "0 0 /",         DivisionByZeroError)

section("11. Unknown Word алдаанууд")
test_error("N14 — тодорхойгүй word",   "foobar .",      UnknownWordError)
test_error("N15 — typo 'txx' (tax?)",  "5 txx .",       UnknownWordError)

section("12. Missing Storage Key")
test_error('N16 — load байхгүй key',   '"nokey" load',  MissingStorageKeyError)

section("13. Invalid if operand")
test_error("N17 — if-д boolean биш",   '5 { 1 } { 0 } if', InvalidIfOperandError)
test_error("N18 — if-д block биш",
           'true 1 2 if',               InvalidIfOperandError)

section("14. Lexer / Parse алдаанууд")
test_error("N19 — хаагдаагүй string",  '"hello',        LexerError)
test_error("N20 — хаагдаагүй block",   '{ 1 2 +',       ParseError)
test_error("N21 — хаагдаагүй list",    '[ 1 2 3',       ParseError)
test_error("N22 — definition нэргүй",  ': dup * ;',     ParseError)

section("15. Levenshtein Diagnostic")

from smartstack.interpreter import levenshtein, suggest

def test_lev(s, t, expected):
    global passed, failed
    result = levenshtein(s, t)
    if result == expected:
        print(f"   PASS  levenshtein({s!r}, {t!r}) = {result}")
        passed += 1
    else:
        print(f"   FAIL  levenshtein({s!r}, {t!r}) = {result}, хүлээсэн {expected}")
        failed += 1

test_lev("txx", "tax",  1)
test_lev("swp", "swap", 1)
test_lev("txx", "dup",  3)
test_lev("",    "abc",  3)
test_lev("abc", "",     3)
test_lev("abc", "abc",  0)

dict_sample = {"tax": [], "swap": [], "dup": [], "drop": [], "over": []}
s1 = suggest("txx",    dict_sample)
s2 = suggest("swp",    dict_sample)
s3 = suggest("abcxyz", dict_sample)

def test_suggest(input_word, expected, result):
    global passed, failed
    if result == expected:
        print(f"   PASS  suggest({input_word!r}) = {result!r}")
        passed += 1
    else:
        print(f"   FAIL  suggest({input_word!r}) = {result!r}, хүлээсэн {expected!r}")
        failed += 1

test_suggest("txx",    "tax",  s1)
test_suggest("swp",    "swap", s2)
test_suggest("abcxyz", None,   s3)


total = passed + failed
print(f"\n{'═'*55}")
print(f"  НИЙТ: {total} тест  |   {passed} амжилттай  |   {failed} амжилтгүй")
print(f"{'═'*55}")
if failed == 0:
    print("   Бүх тест амжилттай өнгөрлөө!")
else:
    print(f"    {failed} тест амжилтгүй боллоо.")
