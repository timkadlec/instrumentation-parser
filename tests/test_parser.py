import pytest
from parser_utils import clean_line, normalize_abbr, split_instrumentation_line


def test_clean_line_removes_invisible_and_extra_spaces():
    raw = "  2 Fl\u200b,  2 Ob  "
    cleaned = clean_line(raw)
    assert cleaned == "2 Fl, 2 Ob"


def test_normalize_abbr_strips_noise():
    assert normalize_abbr("Fl.") == "fl"
    assert normalize_abbr("Alt-Fl") == "altfl"
    assert normalize_abbr("Cl. in A") == "clinA".lower()


def test_split_instrumentation_line_handles_nested():
    line = "2(fl+pic),2(ob),2(cl),2(fg)"
    parts = split_instrumentation_line(line)
    assert parts == ["2(fl+pic)", "2(ob)", "2(cl)", "2(fg)"]


def test_split_instrumentation_line_handles_plain_commas():
    line = "2fl, 2ob, 2cl"
    parts = split_instrumentation_line(line)
    assert parts == ["2fl", "2ob", "2cl"]
