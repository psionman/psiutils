import pytest
import tkinter as tk
from datetime import datetime

from psiutils.date_picker import DatePicker


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()  # hide window
    yield root
    root.destroy()


def test_default_date_is_today(tk_root):
    picker = DatePicker(tk_root)

    today = picker.date
    now = datetime.now()

    assert today.year == now.year
    assert today.month == now.month
    assert today.day == now.day


def test_initial_date(tk_root):
    date = datetime(2024, 12, 25)
    picker = DatePicker(tk_root, initial_date=date)

    assert picker.date == date.replace(
        hour=0, minute=0, second=0, microsecond=0)


def test_date_setter_updates_stringvar(tk_root):
    picker = DatePicker(tk_root)

    d = datetime(2023, 1, 2)
    picker.date = d

    assert picker._date_input.get() == "02/01/2023"


def test_date_getter_parses_correctly(tk_root):
    picker = DatePicker(tk_root)
    picker._date_input.set("31/08/2025")

    d = picker.date
    assert d.year == 2025
    assert d.month == 8
    assert d.day == 31


def test_date_increment_forward(tk_root):
    picker = DatePicker(tk_root)
    picker.date = datetime(2024, 2, 28)

    picker._date_increment(picker._date_input, 1)

    assert picker.date == datetime(2024, 2, 29)  # leap year


def test_date_increment_backward(tk_root):
    picker = DatePicker(tk_root)
    picker.date = datetime(2024, 1, 1)

    picker._date_increment(picker._date_input, -1)

    assert picker.date == datetime(2023, 12, 31)


def test_month_rollover(tk_root):
    picker = DatePicker(tk_root)
    picker.date = datetime(2023, 12, 31)

    picker._date_increment(picker._date_input, 1)

    assert picker.date == datetime(2024, 1, 1)


def test_invalid_date_string_raises(tk_root):
    picker = DatePicker(tk_root)
    picker._date_input.set("not/a/date")

    with pytest.raises(ValueError):
        _ = picker.date
