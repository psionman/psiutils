
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import dateutil  # type: ignore
from dateutil.parser import parse  # type: ignore
from PIL import Image, ImageTk
from dataclasses import dataclass

CHECK_BOX_SIZE = (20, 20)


@dataclass
class ColumnDefn():
    name: str
    heading: str
    width: int


class Treeview(ttk.Treeview):
    def __init__(self, master, column_defs: dict = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        if not column_defs:
            column_defs = {}
        self.column_defs = column_defs

        self._configure_columns()

    def _configure_columns(self) -> None:
        column_ids = [col_defn.name for col_defn in self.column_defs]
        self["columns"] = column_ids[1:]

        # Configure each column
        for index, col_defn in enumerate(self.column_defs):
            if index == 0:
                self.column(
                    "#0",
                    width=col_defn.width,
                    minwidth=col_defn.width,
                    stretch=False,
                    anchor="center")
                self._heading('#0', col_defn.heading)
            else:
                self.column(
                    col_defn.name,
                    width=col_defn.width,
                    anchor="w",
                    stretch=True)
                self._heading(col_defn.name, col_defn.heading)

    @property
    def columns(self) -> dict[int, str]:
        return {
            col_defn.name: column-1
            for column, col_defn in enumerate(self.column_defs)
    }

    def _heading(self, col_id: str, heading: str) -> Treeview.heading:
        return self.heading(
            col_id,
            text=heading,
            command=lambda c=col_id: self._sort_columns(c, False)
        )

    def populate(self, values: dict[tuples]) -> None:
        self.delete(*self.get_children())
        for item in values:
            item = self.insert('', 'end', values=item)


    def select_item(self, column: int | str, value: str) -> None:
        if isinstance(column, str):
            column = self.columns[column]

        for iid in self.get_children():
            values = self.item(iid, "values")
            if values[column] == value:
                self.selection_set(iid)
                break

    def _sort_columns(self, col: int, reverse: bool) -> None:
        """Sort the Treeview by column."""
        children = [
                (self.set(child, col), child) for child in self.get_children('')
            ]
        date_children = self._get_date_children(children)
        if date_children:
            children = date_children
        try:
            children.sort(key=lambda t: float(t[0]), reverse=reverse)
        except TypeError:
            children.sort(key=lambda t: t[0], reverse=reverse)
        except ValueError:
            children.sort(reverse=reverse)

        for index, (val, child) in enumerate(children):
            self.move(child, '', index)

        self.heading(col, command=lambda: self._sort_columns(col, not reverse))

    def _get_date_children(self, children) -> list:
        try:
            date_children = []
            for child in children:
                if len(child[0]) < 8:
                    is_date = False
                    break
                date = parse(child[0])
                date_children.append((date, child[1]))
            return date_children
        except dateutil.parser._parser.ParserError:
            return []



def sort_treeview(tree: Treeview, col: int, reverse: bool) -> None:
    """Sort the Treeview by column."""
    print('*** psiutils  "sort_treeview" called: DEPRECATED ***')
    print('Use psiutils.Treeviw class instead!!!')

    children = [
            (tree.set(child, col), child) for child in tree.get_children('')
        ]
    is_date = True
    try:
        date_children = []
        for child in children:
            if len(child[0]) < 8:
                is_date = False
                break
            date = parse(child[0])
            date_children.append((date, child[1]))
    except dateutil.parser._parser.ParserError:
        is_date = False
    if is_date:
        children = date_children
    try:
        children.sort(key=lambda t: float(t[0]), reverse=reverse)
    except TypeError:
        children.sort(key=lambda t: t[0], reverse=reverse)
    except ValueError:
        children.sort(reverse=reverse)

    for index, (val, child) in enumerate(children):
        tree.move(child, '', index)

    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


class CheckTreeView(Treeview):
    def __init__(
            self,
            master,
            column_defs,
            **kwargs):
        """

        :param column_defs: a tuple defining column (key, text, width)
        Other parameters are passed to the `TreeView`.
        """
        super().__init__(master, column_defs, **kwargs)
        self["show"] = "tree headings"
        (
            self.unchecked_image,
            self.checked_image
        ) = self._get_checkbox_images()

        if "selectmode" not in kwargs:
            kwargs["selectmode"] = "none"
        if "show" not in kwargs:
            kwargs["show"] = "tree"

    def _get_checkbox_images(
            self) -> tuple[ImageTk.PhotoImage, ImageTk.PhotoImage]:

        icon_path = f'{Path(__file__).parent}/icons/'
        unchecked_img = Image.open(f"{icon_path}checkbox_unchecked.png")
        unchecked_img = unchecked_img.resize(CHECK_BOX_SIZE, Image.LANCZOS)
        unchecked = ImageTk.PhotoImage(unchecked_img)

        checked_img = tk.PhotoImage(file=f"{icon_path}checkbox_checked.png")
        checked_img = Image.open(f"{icon_path}checkbox_checked.png")
        checked_img = checked_img.resize(CHECK_BOX_SIZE, Image.LANCZOS)
        checked = ImageTk.PhotoImage(checked_img)
        return (unchecked, checked)

    def populate(self, values: list[tuple], checked: bool = False) -> None:
        self.delete(*self.get_children())
        item_checked = (self.checked_image
                        if checked else self.unchecked_image)
        for item in values:
            iid = self.insert(
                parent='',
                index='end',
                image=item_checked,
                values=item
            )
            if checked:
                self.item(iid, tags=("checked",))
            else:
                self.item(iid, tags=("unchecked"))

    def item_click(self, event) -> int:
        iid = self.identify_row(event.y)
        if not iid:
            return

        current_img = self.item(iid, "image")[0]
        if current_img == str(self.unchecked_image):
            self.item(iid, image=self.checked_image, tags=("checked",))
        else:
            self.item(iid, image=self.unchecked_image, tags=("unchecked"))

        return "break"

    def checked_items(self) -> list[tuple]:
        """
        Returns a list of the values (text columns) for all currently
        checked rows.

        Each returned tuple contains the values from the data columns only
        (excludes the checkbox image in the tree column).

        Example return value:
            [("docs", "report.pdf", "Read this file"),
            ("code", "main.py", "Fix bug")]
        """
        checked_items = []

        for iid in self.get_children(''):
            tags = self.item(iid, "tags")
            if "checked" in tags:
                values = self.item(iid, "values")
                checked_items.append(values)
        return checked_items
