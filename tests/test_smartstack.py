import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartstack.interpreter import (
    Interpreter, run,
    StackUnderflowError, TypeError_, DivisionByZeroError,
    UnknownWordError, MissingStorageKeyError, InvalidIfOperandError,
    levenshtein, suggest
)
from smartstack.lexer import LexerError
from smartstack.parser import ParseError
from smartstack.desugar import desugar

passed = 0
failed = 0


def section(title: str):
    print(f"\n{'─' * 60}")
    print(title)
    print(f"{'─' * 60}")


def test_ok(name, source, expected_output, expected_stack=None):
    global passed, failed
    try:
        interp = Interpreter()
        state = interp.run(source)
        actual_output = state.output

        ok_output = actual_output == expected_output
        ok_stack = expected_stack is None or state.stack == expected_stack

        if ok_output and ok_stack:
            print(f"PASS  {name}")
            passed += 1
        else:
            print(f"FAIL  {name}")
            print("SOURCE:")
            print(source)
            print("Expected output:", expected_output)
            print("Actual output  :", actual_output)
            print("Expected stack :", expected_stack)
            print("Actual stack   :", state.stack)
            failed += 1

    except Exception as e:
        print(f"FAIL  {name} -> {type(e).__name__}: {e}")
        failed += 1


def test_error(name, source, error_class):
    global passed, failed
    try:
        run(source)
        print(f"FAIL  {name} -> expected {error_class.__name__}, but no error")
        failed += 1
    except error_class:
        print(f"PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"FAIL  {name} -> wrong error {type(e).__name__}: {e}")
        failed += 1


def test_desugar(name, source, style, expected_core_contains):
    global passed, failed
    try:
        core = desugar(source, style)
        ok = all(part in core for part in expected_core_contains)

        if ok:
            print(f"PASS  {name}")
            passed += 1
        else:
            print(f"FAIL  {name}")
            print("Core:")
            print(core)
            print("Expected contains:", expected_core_contains)
            failed += 1

    except Exception as e:
        print(f"FAIL  {name} -> {type(e).__name__}: {e}")
        failed += 1


section("1. Arithmetic")

test_ok("T01 add", "3 4 + .", ["7"])
test_ok("T02 subtract", "10 2 - .", ["8"])
test_ok("T03 multiply", "6 7 * .", ["42"])
test_ok("T04 divide", "20 5 / .", ["4"])
test_ok("T05 float", "3.5 1.5 + .", ["5"])
test_ok("T06 greater true", "5 3 > .", ["true"])
test_ok("T07 greater false", "2 9 > .", ["false"])
test_ok("T08 equal true", "4 4 = .", ["true"])
test_ok("T09 equal false", "3 5 = .", ["false"])
test_ok("T10 postfix expression", "3 4 + 5 * .", ["35"])
test_ok("T11 postfix precedence manually", "3 4 5 * + .", ["23"])


section("2. Stack operations")

test_ok("T12 dup", "10 dup * .", ["100"])
test_ok("T13 swap", "1 2 swap . .", ["1", "2"])
test_ok("T14 drop", "5 drop 9 .", ["9"])
test_ok("T15 over", "3 4 over . . .", ["3", "4", "3"])
test_ok("T16 dup add", "4 dup + .", ["8"])
test_ok("T17 mixed stack ops", "1 2 3 drop swap . .", ["1", "2"])


section("3. Word definitions")

test_ok("T18 square", ": square dup * ; 5 square .", ["25"])
test_ok("T19 cube", ": cube dup dup * * ; 3 cube .", ["27"])
test_ok("T20 double", ": double 2 * ; 7 double .", ["14"])
test_ok("T21 nested words", ": square dup * ; : quad square square ; 2 quad .", ["16"])
test_ok("T22 inc", ": inc 1 + ; 9 inc .", ["10"])


section("4. Storage")

test_ok("T23 store/load", '100 "x" store "x" load .', ["100"])
test_ok("T24 store/load arithmetic", '100 "x" store "x" load 20 + .', ["120"])
test_ok("T25 multiple storage", '5 "a" store 3 "b" store "a" load "b" load + .', ["8"])
test_ok("T26 overwrite storage", '10 "x" store 99 "x" store "x" load .', ["99"])


section("5. Conditional")

test_ok("T27 if true", '1500 1000 > { "Yes" } { "No" } if .', ['"Yes"'])
test_ok("T28 if false", '5 10 > { "big" } { "small" } if .', ['"small"'])
test_ok("T29 bool true", 'true { "T" } { "F" } if .', ['"T"'])
test_ok("T30 bool false", 'false { "T" } { "F" } if .', ['"F"'])
test_ok("T31 if calculation", '5 3 > { 1 } { 0 } if .', ["1"])


section("6. List map/filter")

test_ok("T32 map", "[ 10 20 30 ] { 2 * } map .", ["[ 20 40 60 ]"])
test_ok("T33 filter", "[ 10 20 30 40 ] { 20 > } filter .", ["[ 30 40 ]"])
test_ok("T34 filter second", "[ 10 30 50 ] { 20 > } filter .", ["[ 30 50 ]"])


section("7. Integration")

test_ok(
    "T35 square + storage + if",
    """
: square dup * ;
9 square
"ans" store
"ans" load 10 >
{ "large" }
{ "small" }
if .
""",
    ['"large"']
)

test_ok(
    "T36 salary formula core",
    """
160 "worked_hours" store
8000 "hourly_rate" store
50000 "penalty" store

"worked_hours" load
"hourly_rate" load
*
"gross_salary" store

"gross_salary" load
0.115
*
"social_insurance" store

"gross_salary" load
"social_insurance" load
-
"salary_after_social" store

"salary_after_social" load
0.10
*
"income_tax" store

"salary_after_social" load
"income_tax" load
-
"penalty" load
-
"net_salary" store

"net_salary" load .
""",
    ["969200"]
)


section("8. Desugar tests")

test_desugar(
    "T37 human calculate",
    """
set penalty to 50000
calculate gross_salary as worked_hours times hourly_rate
show gross_salary
""",
    "human",
    ['50000 "penalty" store', '"worked_hours" load "hourly_rate" load * "gross_salary" store']
)

test_desugar(
    "T38 mn calculate",
    """
торгууль гэдэг нь 50000
нийт_цалин бод ажилласан_цаг үржих цагийн_хөлс
нийт_цалин харуул
""",
    "mn",
    ['50000 "торгууль" store', '"ажилласан_цаг" load "цагийн_хөлс" load * "нийт_цалин" store']
)

test_desugar(
    "T39 code-like calculate",
    """
let gross_salary = worked_hours * hourly_rate;
print(gross_salary);
""",
    "code",
    ['"worked_hours" load "hourly_rate" load * "gross_salary" store', '"gross_salary" load .']
)


section("9. Runtime errors")

test_error("N01 plus empty stack", "+", StackUnderflowError)
test_error("N02 multiply one value", "5 *", StackUnderflowError)
test_error("N03 dup empty", "dup", StackUnderflowError)
test_error("N04 swap one value", "5 swap", StackUnderflowError)
test_error("N05 drop empty", "drop", StackUnderflowError)
test_error("N06 print empty", ".", StackUnderflowError)
test_error("N07 over one value", "5 over", StackUnderflowError)

test_error("N08 string + number", '"abc" 5 +', TypeError_)
test_error("N09 bool * number", "true 5 *", TypeError_)
test_error("N10 store key not string", "10 20 store", TypeError_)
test_error("N11 load key not string", "42 load", TypeError_)

test_error("N12 divide by zero", "10 0 /", DivisionByZeroError)
test_error("N13 unknown word", "foobar .", UnknownWordError)
test_error("N14 missing storage key", '"nokey" load', MissingStorageKeyError)
test_error("N15 invalid if condition", "5 { 1 } { 0 } if", InvalidIfOperandError)
test_error("N16 invalid if block", "true 1 2 if", InvalidIfOperandError)

test_error("N17 unclosed string", '"hello', LexerError)
test_error("N18 unclosed block", "{ 1 2 +", ParseError)
test_error("N19 unclosed list", "[ 1 2 3", ParseError)
test_error("N20 definition without name", ": dup * ;", ParseError)


section("10. Suggestion helper")

def test_value(name, actual, expected):
    global passed, failed
    if actual == expected:
        print(f"PASS  {name}")
        passed += 1
    else:
        print(f"FAIL  {name}: expected {expected}, got {actual}")
        failed += 1


test_value("T40 levenshtein txx/tax", levenshtein("txx", "tax"), 1)
test_value("T41 levenshtein swp/swap", levenshtein("swp", "swap"), 1)
test_value("T42 levenshtein same", levenshtein("abc", "abc"), 0)

dictionary = {"tax": [], "swap": [], "dup": [], "drop": [], "over": []}
test_value("T43 suggest txx", suggest("txx", dictionary), "tax")
test_value("T44 suggest swp", suggest("swp", dictionary), "swap")
test_value("T45 suggest unknown", suggest("abcxyz", dictionary), None)


total = passed + failed

print(f"\n{'═' * 60}")
print(f"TOTAL: {total} tests | PASSED: {passed} | FAILED: {failed}")
print(f"{'═' * 60}")

if failed == 0:
    print("All tests passed.")
else:
    print(f"{failed} tests failed.")