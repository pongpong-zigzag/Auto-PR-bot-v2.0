from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTE = {
    "bg": "#0f172a",
    "surface": "#1e293b",
    "card": "#16223a",
    "muted": "#94a3b8",
    "text": "#f8fafc",
    "accent": "#38bdf8",
    "accent_dark": "#0ea5e9",
    "success": "#22c55e",
    "warning": "#fbbf24",
    "danger": "#ef4444",
}


def apply_style(root: tk.Tk) -> None:
    """Configure ttk styles for a modern dark interface."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=PALETTE["bg"])

    # Base styles
    style.configure("Root.TFrame", background=PALETTE["bg"])
    style.configure("TFrame", background=PALETTE["surface"])
    style.configure("Card.TFrame", background=PALETTE["card"], relief="flat")
    style.configure(
        "CardAccent.TFrame",
        background=PALETTE["accent"],
        relief="flat",
        borderwidth=0,
    )
    style.configure("Card.TLabel", background=PALETTE["card"], foreground=PALETTE["text"])
    style.configure(
        "Card.TLabelframe",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        borderwidth=1,
        bordercolor=PALETTE["surface"],
        relief="flat",
        padding=5,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=PALETTE["card"],
        foreground=PALETTE["accent"],
        font=("Segoe UI Semibold", 9),
    )

    style.configure(
        "Header.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 12, "bold"),
    )
    style.configure(
        "Subheader.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Muted.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["muted"],
        font=("Segoe UI", 8),
    )
    style.configure(
        "HeroHeading.TLabel",
        background=PALETTE["accent"],
        foreground=PALETTE["bg"],
        font=("Segoe UI Semibold", 12),
    )
    style.configure(
        "HeroSubheading.TLabel",
        background=PALETTE["accent"],
        foreground=PALETTE["bg"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "HeroMetric.TLabel",
        background=PALETTE["accent"],
        foreground=PALETTE["bg"],
        font=("Segoe UI", 12, "bold"),
    )
    style.configure(
        "Metric.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9, "bold"),
        padding=(12, 6),
    )
    style.configure(
        "MetricValue.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["muted"],
        font=("Segoe UI", 8),
    )

    # Buttons
    style.configure(
        "TButton",
        background=PALETTE["surface"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 8),
        padding=(8, 4),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "TButton",
        background=[("active", PALETTE["card"]), ("disabled", "#1f2937")],
        foreground=[("disabled", PALETTE["muted"])],
    )

    style.configure(
        "Accent.TButton",
        background=PALETTE["accent"],
        foreground=PALETTE["bg"],
        font=("Segoe UI Semibold", 8),
        padding=(8, 4),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Accent.TButton",
        background=[("active", PALETTE["accent_dark"]), ("disabled", "#1f2937")],
        foreground=[("disabled", PALETTE["muted"])],
    )

    style.configure(
        "Danger.TButton",
        background=PALETTE["danger"],
        foreground=PALETTE["text"],
        font=("Segoe UI Semibold", 8),
        padding=(8, 4),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#dc2626"), ("disabled", "#1f2937")],
        foreground=[("disabled", PALETTE["muted"])],
    )

    # Inputs
    entry_style = {
        "background": PALETTE["surface"],
        "foreground": PALETTE["text"],
        "fieldbackground": PALETTE["surface"],
        "bordercolor": PALETTE["accent"],
        "lightcolor": PALETTE["accent"],
        "darkcolor": PALETTE["surface"],
        "insertcolor": PALETTE["accent"],
        "selectbackground": PALETTE["accent"],
        "selectforeground": PALETTE["bg"],
    }
    style.configure("TEntry", **entry_style, padding=4)
    style.configure("TCombobox", **entry_style, padding=4)
    style.configure("TSpinbox", **entry_style, padding=4)
    style.map(
        "TEntry",
        bordercolor=[("focus", PALETTE["accent"]), ("!focus", PALETTE["surface"])],
    )
    style.configure(
        "TCheckbutton",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 8),
    )
    style.map(
        "TCheckbutton",
        background=[("active", PALETTE["card"]), ("selected", PALETTE["card"])],
        indicatorcolor=[("selected", PALETTE["accent"])],
    )

    # Status labels
    style.configure(
        "StatusInfo.TLabel",
        background=PALETTE["accent_dark"],
        foreground=PALETTE["bg"],
        padding=(6, 2),
        font=("Segoe UI", 8, "bold"),
    )

    # Misc elements
    style.configure(
        "TPanedwindow",
        background=PALETTE["bg"],
        borderwidth=0,
        sashwidth=16,
    )
    style.map(
        "TPanedwindow",
        background=[("background", PALETTE["bg"])],
    )
    # Note: Sash styling may not work on all platforms
    try:
        style.configure(
            "Sash",
            sashthickness=10,
            background=PALETTE["muted"],
        )
        style.map(
            "Sash",
            background=[("active", PALETTE["accent"])],
        )
    except tk.TclError:
        pass
    style.configure(
        "Vertical.TScrollbar",
        background=PALETTE["surface"],
        troughcolor=PALETTE["card"],
        bordercolor=PALETTE["card"],
        arrowcolor=PALETTE["text"],
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", PALETTE["accent"])],
    )
    style.configure(
        "TSizegrip",
        background=PALETTE["bg"],
    )
    style.configure(
        "StatusSuccess.TLabel",
        background=PALETTE["success"],
        foreground=PALETTE["bg"],
        padding=(6, 2),
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "StatusWarning.TLabel",
        background=PALETTE["warning"],
        foreground=PALETTE["bg"],
        padding=(6, 2),
        font=("Segoe UI", 8, "bold"),
    )
    style.configure(
        "StatusDanger.TLabel",
        background=PALETTE["danger"],
        foreground=PALETTE["bg"],
        padding=(6, 2),
        font=("Segoe UI", 8, "bold"),
    )


