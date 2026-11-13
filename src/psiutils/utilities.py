"""Common methods for psiutils."""

import ctypes
import platform
import re
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

GEOMETRY_RE = re.compile(r"^(\d+)x(\d+)([+-]\d+)([+-]\d+)$")


_resize_job = {}  # needed in widows_resize


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


def window_resize(
    root: tk.Tk, file: str, config: dict | None = None, *args
) -> None:
    if not config:
        config = {}

    key = Path(file).stem
    if key in _resize_job:
        root.after_cancel(_resize_job[key])

    _resize_job[key] = root.after(
        300, lambda: _save_geometry(root, key, config)
    )


def _get_saved_geometry(
    config: TomlConfig, file: Path, default: str = ""
) -> str:
    """Return the saved geometry for a window, unadjusted."""
    default = default or DEFAULT_GEOMETRY
    try:
        saved = config.geometry[Path(file).stem]
    except KeyError:
        return default
    return saved if GEOMETRY_RE.match(saved) else default


def _save_geometry(root: tk.Tk, key: str, config) -> None:
    match = GEOMETRY_RE.match(root.geometry())
    if not match:
        return
    width, height, x, y = match.groups()
    window_geometry = f"{width}x{height}{x}{y}"

    new_geometry = config.geometry
    new_geometry[key] = window_geometry
    config.update("geometry", new_geometry)
    config.save()


def restore_geometry(
    root: tk.Tk, config: TomlConfig, file: Path, default: str = ""
) -> None:
    """Apply saved geometry, correcting any offset the WM introduces."""
    wanted = _get_saved_geometry(config, file, default)
    root.geometry(wanted)
    root.after(100, lambda: _settle(root, wanted))


def _settle(root: tk.Tk, wanted: str) -> None:
    want = GEOMETRY_RE.match(wanted)
    got = GEOMETRY_RE.match(root.geometry())
    if not (want and got):
        return
    dx = int(got.group(3)) - int(want.group(3))
    dy = int(got.group(4)) - int(want.group(4))
    if dx or dy:
        root.geometry(f"+{int(want.group(3)) - dx}+{int(want.group(4)) - dy}")
