"""Common methods for psiutils."""

import ctypes
import platform
import sys
import tkinter as tk
from pathlib import Path
from typing import Any

from psiconfig import TomlConfig

from psiutils._logger import psi_logger as logger
from psiutils.constants import DEFAULT_GEOMETRY
from psiutils.text import Text

psi_logger = logger
txt = Text()


def display_icon(
    root: tk.Tk, icon_file_path: str, ignore_error: bool = True
) -> None:
    if platform.system() == "Windows":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("_")
    try:
        icon = tk.PhotoImage(master=root, file=icon_file_path)
        root.wm_iconphoto(True, icon)
    except tk.TclError as err:
        if ignore_error and txt.NO_SUCH_FILE in str(err):
            return
        print(f"Cannot find icon file: {icon_file_path}")


def resource_path(base: Path, relative_path: Path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(base).parent
    return Path(base_path, relative_path)


def confirm_delete(parent: Any) -> str:
    question = txt.DELETE_THESE_ITEMS
    return tk.messagebox.askquestion(
        "Delete items", question, icon="warning", parent=parent
    )


def create_directories(path: str | Path) -> bool:
    """Create directories recursively."""
    print('*** psiutils  "create_directories" called: DEPRECATED ***')
    print("Use Path(path).mkdir(parents=True, exist_ok=True) instead!!!")
    create_parts = []
    create_path = Path(path)
    for part in create_path.parts:
        create_parts.append(part)
        new_path = Path(*create_parts)
        if not Path(new_path).is_dir():
            try:
                Path(new_path).mkdir()
            except PermissionError:
                print(f"Invalid file path: {new_path}")
                return False
    return True


def enable_frame(parent: tk.Frame, enable: bool = True) -> None:
    state = tk.NORMAL if enable else tk.DISABLED
    for child in parent.winfo_children():
        w_type = child.winfo_class()
        if w_type in ("Frame", "Labelframe", "TFrame", "TLabelframe"):
            enable_frame(child, enable)
        else:
            child.configure(state=state)


def geometry(config: TomlConfig, file: Path, default: str = "") -> str:
    if not default:
        default = DEFAULT_GEOMETRY
    try:
        return config.geometry[Path(file).stem]
    except KeyError:
        return default


def window_resize(
    root: tk.Tk, file: str, config: dict | None = None, *args
) -> None:
    if not config:
        config = {}
    match = root.geometry().split("+")
    window_geometry = (
        f"{root.winfo_width()}x{root.winfo_height()}+"
        f"{root.winfo_x()}+{match[2]}"
    )
    new_geometry = config.geometry
    new_geometry[Path(file).stem] = window_geometry
    config.update("geometry", new_geometry)
    config.save()
