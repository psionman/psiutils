"""Button class for Tkinter applications."""

import json
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from psiutils.constants import PAD, Pad
from psiutils.text import Text
from psiutils.widgets import HAND, clickable_widget, enter_widget

txt = Text()

DEFAULT_ICON = "question-red"
MISSING_DEFINITION = "missing-definition"

COLOURS = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 160, 20),
    "orange": (212, 100, 50),
}


@dataclass(slots=True)
class IconButtonConfig:
    text: str
    icon: str


class IconButton(ttk.Frame):
    def __init__(
        self,
        master: tk.Frame,
        text: str,
        icon: str,
        command: Callable | None = None,
        dimmable: bool = False,
        *,
        sticky: str = "",
        icon_path: str = "",
        icon_colour: str | tuple[int] = "",
        text_colour: str | tuple[int] = "",
        tag: str = "",
        **kwargs,
    ):
        super().__init__(master, borderwidth=1, relief="raised", **kwargs)
        self.command = command
        self._state = tk.NORMAL
        self.text = text
        self.icon = icon
        self.icon_colour = icon_colour
        self.text_colour = text_colour
        self.tag = tag
        self.icon_path = icon_path

        # Icon and text
        photo_image = self._get_photo_image(icon_path, icon)

        self.button_label = ttk.Label(
            self,
            text=text,
            image=photo_image,
            compound=tk.LEFT,
            foreground=self.text_colour,
        )
        self.button_label.image = photo_image  # Prevent garbage collection
        self.button_label.pack(padx=(3, 5), pady=5)
        self.widget = self.button_label

        # Make the whole frame clickable
        self.bind_widgets()

        self.sticky = sticky
        self.dimmable = dimmable

    def _get_photo_image(
        self,
        path: Path,
        icon: str,
    ) -> ImageTk.PhotoImage:
        icon_path = Path(path, f"{icon}.png")
        if not icon_path.exists():
            if icon_path.name != icon_path.stem:
                print(
                    f"Icon not found: Text: {self.text} "
                    f"Icon: '{icon}' "
                    f"Path: {icon_path}"
                )
            icon_path = Path(path, f"{DEFAULT_ICON}.png")
            return None
        image = Image.open(icon_path).resize((16, 16)).convert("RGBA")

        image = self._colour_image(image)

        photo_image = ImageTk.PhotoImage(image)
        return photo_image

    def _colour_image(self, image: Image) -> Image:
        if not self.icon_colour:
            return image

        if isinstance(self.icon_colour, str):
            r, g, b = COLOURS[self.icon_colour]

        if isinstance(self.icon_colour, tuple):
            r, g, b = self.icon_colour

        pixels = image.load()

        for y in range(image.size[1]):
            for x in range(image.size[0]):
                _, _, _, a = pixels[x, y]
                pixels[x, y] = (r, g, b, a)
        return image

    def __repr__(self) -> str:
        return f"IconButton: {self.text} {self.icon}"

    def state(self, *args, **kwargs) -> dict:
        return self._state

    def enable(self, enable: bool = True) -> None:
        state = tk.NORMAL if enable else tk.DISABLED
        self.button_label.configure(state=state)
        self._state = state

    def disable(self, disable: bool = True) -> None:
        state = tk.DISABLED if disable else tk.NORMAL
        self.button_label.configure(state=state)
        self._state = state

    def bind_widgets(self):
        for widget in (self, self.button_label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._enter_button)
            widget.bind("<Leave>", lambda e: self.config(relief="raised"))

    def _enter_button(self, event) -> None:
        if self._state == tk.DISABLED:
            return
        self.config(relief="sunken")
        event.widget.winfo_toplevel().config(cursor=HAND)

    def _on_click(self, *args):
        if self._state == tk.DISABLED:
            return
        if self.command:
            self.command()


class Button(ttk.Button):
    def __init__(
        self,
        *args,
        sticky: str = "",
        dimmable: bool = False,
        **kwargs: dict,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.sticky = sticky
        self.dimmable = dimmable

    def enable(self, enable: bool = True) -> None:
        state = tk.NORMAL if enable else tk.DISABLED
        self["state"] = state

    def disable(self, disable: bool = True) -> None:
        state = tk.DISABLED if disable else tk.NORMAL
        self["state"] = state


class ButtonFrame(ttk.Frame):
    def __init__(
        self,
        master: tk.Frame,
        orientation: str = tk.HORIZONTAL,
        button_config_path: str = "",
        icon_path: str = "",
        **kwargs: dict,
    ) -> None:
        super().__init__(master, **kwargs)
        self._buttons = []
        self._enabled = False
        self.orientation = orientation
        self.tagged_buttons = {}

        if "enabled" in kwargs:
            self._enabled = kwargs["enabled"]
        self.button_config_path = button_config_path
        self.icon_path = icon_path
        self.button_configs = self._read_buttons_config()
        # self.icon_buttons = self._get_icon_buttons()

    def icon_button(
        self,
        id_: str,
        command: object = None,
        dimmable: bool = False,
        text: str = "",
        icon_colour: str | tuple[int] = "",
        text_colour: str | tuple[int] = "",
        tag: str = "",
    ) -> IconButton:
        if id_ not in self.button_configs:
            text = id_.capitalize()
            id_ = MISSING_DEFINITION
        button_defn = self.button_configs.get(id_)
        if not button_defn:
            button_defn = ["", ""]
        button_config = IconButtonConfig(*button_defn)
        if not button_config:
            raise ValueError(f"Button {id_} not found")
        return IconButton(
            self,
            text or button_config.text,
            button_config.icon,
            command=command,
            dimmable=dimmable,
            icon_colour=icon_colour,
            text_colour=text_colour,
            icon_path=self.icon_path,
            tag=tag,
        )

    @property
    def buttons(self) -> list[Button]:
        return self._buttons

    @buttons.setter
    def buttons(self, value: list[Button]) -> None:
        self._buttons = value

        if self.orientation == tk.VERTICAL:
            self._vertical_buttons()
        elif self.orientation == tk.HORIZONTAL:
            self._horizontal_buttons()

        self.tagged_buttons = {}
        for button in self._buttons:
            if button.tag:
                self.tagged_buttons[button.tag] = button

    def get_button(self, tag: str) -> IconButton:
        if tag in self.tagged_buttons:
            return self.tagged_buttons[tag]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        state = tk.NORMAL if value else tk.DISABLED
        for button in self.buttons:
            button.widget["state"] = state

    def enable(self, enable: bool = True) -> None:
        self._enabled = enable
        self._enable_buttons(self.buttons, enable)

    def disable(self) -> None:
        self._enabled = False
        self._enable_buttons(self.buttons, False)

    def _vertical_buttons(self) -> None:
        self.rowconfigure(len(self.buttons) - 1, weight=1)
        for row, button in enumerate(self.buttons):
            pady = PAD
            if row == 0:
                pady = Pad.S
            if row == len(self.buttons) - 1:
                self.rowconfigure(row, weight=1)
                row += 1
                pady = Pad.N

            button.grid(row=row, column=0, sticky=tk.EW, pady=pady)
            clickable_widget(button)

    def _horizontal_buttons(self) -> None:
        self.columnconfigure(len(self.buttons) - 1, weight=1)
        for col, button in enumerate(self.buttons):
            padx = PAD
            if col == 0:
                padx = Pad.W
            if col == len(self.buttons) - 1:
                self.columnconfigure(col, weight=1)
                col += 1
            button.grid(row=0, column=col, sticky=button.sticky, padx=padx)
            clickable_widget(button)

    @staticmethod
    def _enable_buttons(buttons: list[Button], enable: bool = True):
        for button in buttons:
            if button.dimmable:
                button.enable(enable)

    def _read_buttons_config(self) -> dict[str, tuple[str, str]]:
        if not self.button_config_path:
            return {}
        try:
            with open(self.button_config_path, encoding="utf8") as f_json:
                try:
                    return json.load(f_json)
                except json.decoder.JSONDecodeError:
                    print(f"JSON decode error {self.button_config_path}")
                    return {}
        except FileNotFoundError:
            print(f"File not found {self.button_config_path}")
            return {}


def enable_buttons(buttons: list[Button], enable: bool = True):
    state = tk.NORMAL if enable else tk.DISABLED
    for button in buttons:
        if button.dimmable:
            button["state"] = state
            button.bind("<Enter>", enter_widget)
