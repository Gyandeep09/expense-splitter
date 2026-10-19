import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from splitter import Group, SplitError, split_amount, to_money

D = Decimal


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("12", "12.00"),
        ("$12.345", "12.35"),
        ("1,5", "1.50"),
        ("1,000", "1000.00"),
        ("1,234.56", "1234.56"),
        ("₹ 99.9", "99.90"),
    ],
)
def test_to_money(raw, expected):
    assert to_money(raw) == D(expected)


@pytest.mark.parametrize("bad", ["", "abc", "0", "-5", "NaN", "Infinity", "1e999999"])
def test_to_money_rejects(bad):
    with pytest.raises(SplitError):
        to_money(bad)


@pytest.mark.parametrize("amount, count", [("100.00", 3), ("0.01", 4), ("10.00", 7), ("99.99", 2)])
def test_split_amount_adds_up(amount, count):
    shares = split_amount(D(amount), count)
    assert sum(shares) == D(amount)
    assert max(shares) - min(shares) <= D("0.01")


def test_split_amount_offset_moves_extra_cent():
    assert split_amount(D("10.00"), 3, 0) == [D("3.34"), D("3.33"), D("3.33")]
    assert split_amount(D("10.00"), 3, 1) == [D("3.33"), D("3.34"), D("3.33")]


def make_group():
    group = Group()
    for name in ("Ana", "Ben", "Cy"):
        group.add_member(name)
    return group


def test_balances_sum_to_zero_and_settle():
    group = make_group()
    group.add_expense("Pizza", "100.00", "Ana", ["Ana", "Ben", "Cy"])
    group.add_expense("Taxi", "30", "Ben", ["Ben", "Cy"])
    balances = group.balances()
    assert sum(balances.values()) == D("0.00")
    settled = dict(balances)
    for t in group.settlements():
        settled[t.sender] += t.amount
        settled[t.receiver] -= t.amount
    assert all(v == 0 for v in settled.values())


def test_simple_settlement():
    group = make_group()
    group.add_expense("Dinner", "90", "Ana", ["Ana", "Ben", "Cy"])
    transfers = group.settlements()
    assert {(t.sender, t.receiver, t.amount) for t in transfers} == {
        ("Ben", "Ana", D("30.00")),
        ("Cy", "Ana", D("30.00")),
    }


def test_even_group_has_no_transfers():
    group = make_group()
    group.add_expense("A", "30", "Ana", ["Ana", "Ben", "Cy"])
    group.add_expense("B", "30", "Ben", ["Ana", "Ben", "Cy"])
    group.add_expense("C", "30", "Cy", ["Ana", "Ben", "Cy"])
    assert group.settlements() == []


def test_member_rules():
    group = make_group()
    with pytest.raises(SplitError):
        group.add_member("ana")
    with pytest.raises(SplitError):
        group.add_member("   ")
    group.add_expense("Snacks", "5", "Ana", ["Ana"])
    with pytest.raises(SplitError):
        group.remove_member("Ana")
    group.remove_member("Cy")
    assert "Cy" not in group.members


def test_expense_rules():
    group = Group()
    with pytest.raises(SplitError):
        group.add_expense("x", "5", "Ana", ["Ana"])
    group = make_group()
    with pytest.raises(SplitError):
        group.add_expense("", "5", "Ana", ["Ana"])
    with pytest.raises(SplitError):
        group.add_expense("x", "5", "Nobody", ["Ana"])
    with pytest.raises(SplitError):
        group.add_expense("x", "5", "Ana", [])


def test_remove_expense_and_summary():
    group = make_group()
    group.add_expense("Dinner", "90", "Ana", ["Ana", "Ben", "Cy"])
    assert "Ben ➜ Ana: $30.00" in group.summary_text()
    group.remove_expense(0)
    assert group.total() == D("0.00")
    assert "no cap" in group.summary_text()
