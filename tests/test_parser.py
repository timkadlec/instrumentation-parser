import pytest
from parser import clean_line, normalize_abbr, split_instrumentation_line

def test_clean_line():
    assert clean_line("a\u200b b\u200c\u200d\u2060\ufeffc") == "a b c"

def test_normalize_abbr():
    assert normalize_abbr("Fl.") == "fl"
    assert normalize_abbr("  Ob - ") == "ob"

def test_split_instrumentation_line_simple():
    assert split_instrumentation_line("2,2,2") == ["2", "2", "2"]

def test_split_instrumentation_line_with_parentheses():
    line = "2(pic+eh),2,2"
    assert split_instrumentation_line(line) == ["2(pic+eh)", "2", "2"]
