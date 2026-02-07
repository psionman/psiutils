import pytest
import tkinter as tk
from datetime import datetime

from psiutils.date_picker import TimePicker, Time, DAY_START, MIDNIGHT


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()  # hide window
    yield root
    root.destroy()


def test_time_defaults():
    t = Time()
    assert t.hour == 0
    assert t.minute == 0
    assert t.second == 0


def test_time_on_applies_to_date():
    date = datetime(2024, 1, 15)
    t = Time(13, 45, 30)

    result = t.on(date)

    assert result == datetime(2024, 1, 15, 13, 45, 30)


def test_day_start_constant():
    assert DAY_START == Time(0, 0, 0)


def test_midnight_constant():
    assert MIDNIGHT == Time(23, 59, 59)


def test_timepicker_defaults(tk_root):
    picker = TimePicker(tk_root)

    assert picker.hour == 0
    assert picker.minute == 0
    assert picker.second == 0


def test_timepicker_initial_time(tk_root):
    picker = TimePicker(tk_root, time=Time(9, 30, 15), use_seconds=True)

    assert picker.hour == 9
    assert picker.minute == 30
    assert picker.second == 15

def test_timepicker_time_property(tk_root):
    picker = TimePicker(tk_root)
    picker.time = Time(10, 20, 0)

    t = picker.time
    assert isinstance(t, Time)
    assert t == Time(10, 20, 0)


def test_timepicker_time_setter(tk_root):
    picker = TimePicker(tk_root)

    picker.time = Time(22, 58, 12)

    assert picker.hour == 22
    assert picker.minute == 58
    assert picker.second == 12


def test_time_increment_wraps_forward(tk_root):
    picker = TimePicker(tk_root)
    picker._hour_input.set("23")

    picker.increment_buttons['hours'].invoke()

    assert picker.hour == 0


def test_time_decrement_wraps_backward(tk_root):
    picker = TimePicker(tk_root)
    picker._minute_input.set("00")

    picker.decrement_buttons['minutes'].invoke()

    assert picker.minute == 59


def test_seconds_disabled_defaults_to_zero(tk_root):
    picker = TimePicker(tk_root, use_seconds=False)

    assert picker.second == 0


def test_labels_enabled(tk_root):
    picker = TimePicker(tk_root, use_labels=True)

    labels = [
        w for w in picker.winfo_children()[0].winfo_children()
        if w.winfo_class() == "TLabel"
    ]

    texts = [lbl.cget("text") for lbl in labels]
    assert "Hour" in texts
    assert "Mins" in texts


def test_timepicker_on_applies_to_date(tk_root):
    picker = TimePicker(tk_root)
    picker.time = Time(14, 15, 16)

    date = datetime(2024, 2, 10)
    result = picker.on(date)

    assert result == datetime(2024, 2, 10, 14, 15, 16)
