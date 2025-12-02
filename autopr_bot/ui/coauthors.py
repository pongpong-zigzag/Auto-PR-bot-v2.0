from __future__ import annotations

from dataclasses import dataclass
from typing import List
import tkinter as tk
from tkinter import ttk


@dataclass
class CoAuthorRow:
    frame: ttk.Frame
    name_var: tk.StringVar
    email_var: tk.StringVar


class CoAuthorManager:
    """Manage dynamic co-author inputs."""

    def __init__(self, master: ttk.Widget):
        self.master = master
        self.frame = ttk.Frame(master, style="Card.TFrame")
        self.frame.columnconfigure(0, weight=1)
        self.rows: List[CoAuthorRow] = []

        controls = ttk.Frame(self.frame, style="Card.TFrame")
        controls.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            controls,
            text="Add collaborators who should appear in commit metadata.",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)

        ttk.Button(
            controls,
            text="+ Add Co-Author",
            style="Accent.TButton",
            command=self.add_row,
        ).pack(side=tk.RIGHT, padx=(4, 0))

        self.list_frame = ttk.Frame(self.frame, style="Card.TFrame")
        self.list_frame.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.columnconfigure(1, weight=2)

        header = ttk.Frame(self.list_frame, style="Card.TFrame")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=2)
        ttk.Label(header, text="Name", style="Card.TLabel", font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Email", style="Card.TLabel", font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w")

    # ------------------------------------------------------------------ #
    def add_row(self) -> None:
        row_index = len(self.rows) + 1  # +1 because row 0 is the header
        row_frame = ttk.Frame(self.list_frame, style="Card.TFrame")
        row_frame.grid(row=row_index, column=0, columnspan=3, sticky="ew", pady=2)
        row_frame.columnconfigure(0, weight=1)
        row_frame.columnconfigure(1, weight=2)

        name_var = tk.StringVar()
        email_var = tk.StringVar()

        name_entry = ttk.Entry(row_frame, textvariable=name_var)
        name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        email_entry = ttk.Entry(row_frame, textvariable=email_var)
        email_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        
        ttk.Button(
            row_frame,
            text="Remove",
            command=lambda: self._remove_row(row_frame),
        ).grid(row=0, column=2, sticky="e")

        self.rows.append(CoAuthorRow(row_frame, name_var, email_var))

    def _remove_row(self, frame: ttk.Frame) -> None:
        frame.destroy()
        self.rows = [row for row in self.rows if row.frame != frame]
        # Re-grid remaining rows to maintain proper order
        for idx, row in enumerate(self.rows, start=1):
            row.frame.grid(row=idx, column=0, columnspan=3, sticky="ew", pady=2)

    def clear(self) -> None:
        for row in list(self.rows):
            row.frame.destroy()
        self.rows.clear()

    def get_co_authors(self) -> List[dict]:
        authors: List[dict] = []
        for row in self.rows:
            name = row.name_var.get().strip()
            email = row.email_var.get().strip()
            if name and email:
                authors.append({"name": name, "email": email})
        return authors

    def has_rows(self) -> bool:
        return bool(self.rows)

    # Convenience for toggling visibility
    def show(self) -> None:
        self.frame.grid()

    def hide(self) -> None:
        self.frame.grid_remove()


