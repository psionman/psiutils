import pytest
import tkinter as tk

from psiutils.buttons import Button, ButtonFrame, enable_buttons


@pytest.fixture
def app():
    return tk.Tk()


def test_enable_button_frame(app):
    button_frame = ButtonFrame(app, tk.VERTICAL)
    button_1 = Button(text='d', command=None, dimmable=True)
    button_2 = Button(text='s', command=None)
    button_frame.buttons = [button_1, button_2]

    button_frame.enable(False)
    assert str(button_1['state']) == tk.DISABLED
    assert str(button_2['state']) == tk.NORMAL
    button_frame.enable(True)
    assert str(button_1['state']) == tk.NORMAL
    assert str(button_2['state']) == tk.NORMAL

    button_1.disable()
    assert str(button_1['state']) == tk.DISABLED
    button_1.disable()
    assert str(button_2['state']) == tk.NORMAL


def test_enable_buttons():
    button = Button(text='d', command=None, dimmable=True)
    enable_buttons([button], False)
    assert str(button['state']) == tk.DISABLED
    enable_buttons([button], True)
    assert str(button['state']) == tk.NORMAL
