"""Menu class for Tkinter applications."""

import contextlib
import tkinter as tk
from tkinter import TclError


class Separator:
    """A separator item for use in a Menu."""

    dimmable = False
    menu = None


class MenuItem:
    def __init__(
        self,
        text: str,
        command: object,
        dimmable: bool = False,
        tag: str = None,
        **kwargs: dict,
    ) -> None:

        self.text: str = text
        self.command: object = command
        self.dimmable = dimmable
        self.underline = None
        self.menu = None
        self.tag = tag

        if "disabled" in kwargs and kwargs["disabled"]:
            self.state = tk.DISABLED
            self.disable()
        if "underline" in kwargs:
            self.underline = kwargs["underline"]

    def __repr__(self) -> str:
        return f"MenuItem: {self.text}"

    def enable(self, enable: bool = True) -> None:
        enable_menu_items(self.menu, [self], enable)

    def disable(self) -> None:
        enable_menu_items(self.menu, [self], False)


class Menu(tk.Menu):
    def __init__(self, root: tk.Tk, menu_items: list = None) -> None:
        if menu_items is None:
            menu_items = []
        super().__init__(root)
        self.menu_items = menu_items
        for menu_item in menu_items:
            menu_item.menu = self
            if isinstance(menu_item, Separator):
                self.add_separator()
            else:
                self.add_command(
                    label=menu_item.text,
                    command=menu_item.command,
                    underline=menu_item.underline,
                )
        self.tagged_menu_items = {}
        for menu_item in self.menu_items:
            if menu_item.tag:
                self.tagged_menu_items[menu_item.tag] = menu_item

    def get_menu_item(self, tag: str) -> MenuItem:
        if tag in self.tagged_menu_items:
            return self.tagged_menu_items[tag]

    def enable(self, enable: bool = True) -> None:
        enable_menu_items(self, self.menu_items, enable)

    def disable(self) -> None:
        self.enable(False)


def enable_menu_items(menu: Menu, menu_items: list, enable: bool) -> None:
    state = tk.NORMAL if enable else tk.DISABLED
    for menu_item in menu_items:
        with contextlib.suppress(TclError):
            if menu_item.dimmable:
                menu.entryconfig(menu_item.text, state=state)
