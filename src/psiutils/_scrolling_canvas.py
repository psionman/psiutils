
import tkinter as tk
from tkinter import ttk


class ScrollingCanvas(tk.Frame):
    """
    A reusable scrolling container.

    This widget embeds a Frame (`self.content`) inside a Canvas,
    with a vertical scrollbar that activates when the content
    exceeds the visible height.

    IMPORTANT:
    - The canvas controls scrolling
    - Widgets must be added to `self.content`, not the canvas
    """

    def __init__(
            self,
            master,
            *,
            relief,
            borderwidth,
            **kwargs):
        super().__init__(master, relief=relief, borderwidth=borderwidth)

        self.grid_propagate(False)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            borderwidth=0,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = tk.Frame(self.canvas)

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )

        # Geometry management
        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_content_configure(self, event=None):
        """
        Update the scrollable region to include all content.

        Using after_idle ensures Tk has finished laying out widgets
        before bbox("all") is computed — without this, the scrollbar
        may behave incorrectly.
        """
        self.after_idle(
            lambda: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def _on_canvas_configure(self, event):
        """
        Keep the content frame the same width as the canvas.

        CRITICAL:
        - Width is synced
        - Height is NEVER synced (this would break scrolling)
        """
        self.canvas.itemconfigure(self.window_id, width=event.width)
