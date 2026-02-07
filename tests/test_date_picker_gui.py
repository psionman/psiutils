# tests/conftest.py
import pytest
import tkinter as tk
from datetime import datetime

from psiutils.date_picker import DatePicker, PICKER_DATE_PATTERN


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()  # no window popup
    yield root
    root.destroy()


def test_picker_builds_widgets(tk_root):
    picker = DatePicker(tk_root)

    # ttk.Frame returned by _picker is packed into self
    children = picker.winfo_children()
    assert len(children) == 1

    main_frame = children[0]
    assert main_frame.winfo_class() == "TFrame"


def test_dateentry_updates_stringvar(tk_root):
    picker = DatePicker(tk_root)

    # simulate user typing via StringVar
    picker._date_input.set("10/11/2024")

    assert picker.date == datetime(2024, 11, 10)


def test_increment_button_changes_date(tk_root):
    picker = DatePicker(tk_root)
    picker.date = datetime(2024, 1, 1)

    picker.increment_button.invoke()

    assert picker.date == datetime(2024, 1, 2)


def test_decrement_button_changes_date(tk_root):
    picker = DatePicker(tk_root)
    picker.date = datetime(2024, 1, 2)

    picker.decrement_button.invoke()

    assert picker.date == datetime(2024, 1, 1)


def test_buttons_use_increment_style(tk_root):
    picker = DatePicker(tk_root)
    frame = picker.winfo_children()[0]

    inc_button = frame.grid_slaves(row=0, column=1)[0]
    dec_button = frame.grid_slaves(row=1, column=1)[0]

    assert inc_button.cget("style") == "Increment.TButton"
    assert dec_button.cget("style") == "Increment.TButton"


def test_dateentry_configuration(tk_root):
    picker = DatePicker(tk_root)

    assert picker.date_picker.cget("date_pattern") == PICKER_DATE_PATTERN



def test_initial_date_populates_ui(tk_root):
    d = datetime(2023, 7, 14)
    picker = DatePicker(tk_root, initial_date=d)

    assert picker._date_input.get() == "14/07/2023"
