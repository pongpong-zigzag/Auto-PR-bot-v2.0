from __future__ import annotations

from datetime import datetime
import tkinter as tk


class TextLogger:
    """Thread-safe logger that streams messages into a text widget."""

    def __init__(self, text_widget: tk.Text, max_lines: int = 500) -> None:
        self.text_widget = text_widget
        self.max_lines = max_lines

    def __call__(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.text_widget.after(0, self._append, formatted)

    def _append(self, message: str) -> None:
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.see(tk.END)
        self._trim_lines()

    def _trim_lines(self) -> None:
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        if lines > self.max_lines:
            self.text_widget.delete("1.0", f"{lines - self.max_lines}.0")


