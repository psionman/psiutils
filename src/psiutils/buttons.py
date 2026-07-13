"""Button class for Tkinter applications."""

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from psiutils.constants import PAD, Pad
from psiutils.text import Text
from psiutils.widgets import HAND, clickable_widget, enter_widget

txt = Text()

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
    colour: str | None = None


class IconButton(ttk.Frame):
    def __init__(
        self,
        master,
        text,
        icon,
        command=None,
        dimmable: bool = False,
        sticky: str = "",
        icon_path: str = "",
        colour: str | tuple[int] = "",
        **kwargs,
    ):
        super().__init__(master, borderwidth=1, relief="raised", **kwargs)
        self.command = command
        self._state = tk.NORMAL
        self.text = text
        self.icon = icon
        self.colour = colour

        # Icon and text
        if not icon_path:
            icon_path = f"{Path(__file__).parent}/icons/"
        photo_image = self._get_photo_image(icon_path, icon)

        self.button_label = ttk.Label(
            self, text=text, image=photo_image, compound=tk.LEFT
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
        image = (
            Image.open(f"{path}{icon}.png").resize((16, 16)).convert("RGBA")
        )

        image = self._colour_image(image)

        photo_image = ImageTk.PhotoImage(image)
        return photo_image

    def _colour_image(self, image: Image) -> Image:
        if not self.colour:
            return image

        if isinstance(self.colour, str):
            r, g, b = COLOURS[self.colour]

        if isinstance(self.colour, tuple):
            r, g, b = self.colour

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
        **kwargs: dict,
    ) -> None:
        super().__init__(master, **kwargs)
        self._buttons = []
        self._enabled = False
        self.orientation = orientation

        if "enabled" in kwargs:
            self._enabled = kwargs["enabled"]

        self.icon_buttons = {
            name: IconButton(
                self, config.text, config.icon, colour=config.colour
            )
            for name, config in icon_buttons.items()
        }

    def icon_button(
        self,
        id_: str,
        command: object = None,
        dimmable: bool = False,
        text: str = "",
    ) -> IconButton:
        button = self.icon_buttons[id_]
        button.dimmable = dimmable
        button.command = command
        if text:
            button.text = text
        return button

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
            # if not button.sticky:
            #     button.sticky = tk.W
            button.grid(row=0, column=col, sticky=button.sticky, padx=padx)
            clickable_widget(button)

    @staticmethod
    def _enable_buttons(buttons: list[Button], enable: bool = True):
        state = tk.NORMAL if enable else tk.DISABLED
        for button in buttons:
            if button.dimmable:
                if isinstance(button, Button):
                    button["state"] = state
                    button.bind("<Enter>", enter_widget)
                elif isinstance(button, IconButton):
                    if enable:
                        button.enable()
                    else:
                        button.disable()


def enable_buttons(buttons: list[Button], enable: bool = True):
    state = tk.NORMAL if enable else tk.DISABLED
    for button in buttons:
        if button.dimmable:
            button["state"] = state
            button.bind("<Enter>", enter_widget)


icon_buttons = {
    "backup": IconButtonConfig(txt.BACKUP, "backup"),
    "build": IconButtonConfig(txt.BUILD, "build"),
    "check": IconButtonConfig(txt.CHECK, "check"),
    "clear": IconButtonConfig(txt.CLEAR, "clear"),
    "close": IconButtonConfig(txt.CLOSE, "cancel"),
    "close-red": IconButtonConfig(txt.CLOSE, "cancel", "red"),
    "code": IconButtonConfig(txt.CODE, "code"),
    "code-blue": IconButtonConfig(txt.CODE, "code", "blue"),
    "compare": IconButtonConfig(txt.COMPARE, "compare"),
    "compare-orange": IconButtonConfig(txt.COMPARE, "compare", "orange"),
    "config": IconButtonConfig(txt.CONFIG, "gear"),
    "console": IconButtonConfig(txt.KONSOLE, "console"),
    "convert": IconButtonConfig(txt.CONVERT, "convert"),
    "copy_docs": IconButtonConfig(txt.COPY, "copy_docs"),
    "copy_clipboard": IconButtonConfig(txt.COPY, "copy_clipboard"),
    "delete": IconButtonConfig(txt.DELETE, "delete"),
    "download": IconButtonConfig(txt.DOWNLOAD, "download"),
    "diff": IconButtonConfig(txt.DIFF, "diff"),
    "done": IconButtonConfig(txt.DONE, "done"),
    "edit": IconButtonConfig(txt.EDIT, "edit"),
    "exit": IconButtonConfig(txt.EXIT, "cancel"),
    "exit-red": IconButtonConfig(txt.EXIT, "cancel", "red"),
    "exit-orange": IconButtonConfig(txt.EXIT, "cancel", "orange"),
    "help": IconButtonConfig(txt.HELP, "help"),
    "new": IconButtonConfig(txt.NEW, "new"),
    "next": IconButtonConfig(txt.NEXT, "next"),
    "open": IconButtonConfig(txt.OPEN, "open"),
    "paste": IconButtonConfig(txt.PASTE, "paste"),
    "pause": IconButtonConfig(txt.PAUSE, "pause"),
    "preferences": IconButtonConfig(txt.PREFERENCES, "preferences"),
    "previous": IconButtonConfig(txt.PREVIOUS, "previous"),
    "process": IconButtonConfig(txt.PROCESS, "process"),
    "redo": IconButtonConfig(txt.REDO, "redo"),
    "refresh": IconButtonConfig(txt.REFRESH, "refresh"),
    "rename": IconButtonConfig(txt.RENAME, "rename"),
    "report": IconButtonConfig(txt.REPORT, "report"),
    "reset": IconButtonConfig(txt.RESET, "reset"),
    "restore": IconButtonConfig(txt.RESTORE, "restore"),
    "restore_database": IconButtonConfig(txt.RESTORE, "restore_database"),
    "restore_page": IconButtonConfig(txt.RESTORE, "restore_page"),
    "revert": IconButtonConfig(txt.REVERT, "revert"),
    "run": IconButtonConfig(txt.RUN, "start"),
    "save": IconButtonConfig(txt.SAVE, "save"),
    "script": IconButtonConfig(txt.SCRIPT, "script"),
    "search": IconButtonConfig(txt.SEARCH, "search"),
    "send": IconButtonConfig(txt.SEND, "send"),
    "start": IconButtonConfig(txt.START, "start"),
    "update": IconButtonConfig(txt.UPDATE, "update"),
    "upgrade": IconButtonConfig(txt.UPGRADE, "upgrade"),
    "upload": IconButtonConfig(txt.UPLOAD, "upload"),
    "use": IconButtonConfig(txt.USE, "done"),
    "windows": IconButtonConfig(txt.WINDOWS, "windows"),
    "windsurf": IconButtonConfig(txt.WINDSURF, "windsurf"),
}


def list_icon_buttons() -> None:
    """List of icon_button."""
    name_length, text_length, icon_length = 15, 10, 15

    print(
        f"{'name':<{name_length}} {'text':<{text_length}} {'icon':<{icon_length}}"
    )

    print(
        f"{'-' * name_length:<{name_length}} "
        f"{'-' * text_length:<{text_length}} "
        f"{'-' * icon_length:<{icon_length}}"
    )

    for name, button in icon_buttons.items():
        print(
            f"{name:<{name_length}} "
            f"{button[0]:<{text_length}} "
            f"{button[1]:<{icon_length}}"
        )
