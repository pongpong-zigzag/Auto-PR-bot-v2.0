from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTE = {
    # Base colors - harmonious dark theme with blue gradient
    "bg": "#1e293b",  # Dark blue base
    "surface": "#1e3a5f",  # Dark blue surface
    "surface_hover": "#1e40af",  # Darker blue hover
    "card": "#1e3a5f",  # Blue card background
    "card_hover": "#2563eb",  # Blue card hover
    "border": "#3b82f6",  # Blue border
    "border_light": "#60a5fa",  # Light blue border
    
    # Text colors - white and light shades for contrast
    "text": "#ffffff",
    "text_secondary": "#e0e7ff",  # Light blue-tinted white
    "text_tertiary": "#c7d2fe",  # Light blue-tinted
    "muted": "#93c5fd",  # Light blue muted
    
    # Accent colors - vibrant blue
    "accent": "#3b82f6",  # Blue
    "accent_hover": "#2563eb",
    "accent_light": "#60a5fa",
    "accent_dark": "#1d4ed8",
    
    # Blue accents for variation (keeping for compatibility)
    "purple": "#3b82f6",  # Blue (renamed from purple)
    "purple_hover": "#2563eb",
    "purple_light": "#60a5fa",
    
    # Status colors - green and yellow from palette
    "success": "#22c55e",  # Green
    "success_light": "#4ade80",
    "warning": "#fbbf24",  # Yellow
    "warning_light": "#fcd34d",
    "danger": "#ef4444",
    "danger_light": "#f87171",
    "info": "#3b82f6",  # Blue for info
    
    # Gradients and effects - blue gradient
    "gradient_start": "#60a5fa",  # Light Blue
    "gradient_end": "#3b82f6",    # Medium Blue
    "bg_gradient_start": "#3b82f6",  # Blue for background gradient
    "bg_gradient_end": "#2563eb",    # Darker blue for background gradient
    "shadow": "#00000060",
}


def apply_style(root: tk.Tk) -> None:
    """Configure ttk styles for a modern dark interface with enhanced UX."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=PALETTE["bg_gradient_start"])  # Use gradient start color as fallback

    # Base frame styles - use midpoint of gradient for better blend
    gradient_mid = "#1e40af"  # Midpoint of blue gradient
    style.configure("Root.TFrame", background=gradient_mid)
    style.configure("TFrame", background=PALETTE["surface"])
    style.configure("Card.TFrame", background=PALETTE["card"], relief="flat")
    
    # Gradient header frame - blue accent
    style.configure(
        "CardAccent.TFrame",
        background=PALETTE["gradient_start"],
        relief="flat",
        borderwidth=0,
    )
    
    # Card label frame with modern borders
    style.configure(
        "Card.TLabelframe",
        background=PALETTE["card"],
        foreground=PALETTE["text_secondary"],
        borderwidth=1,
        bordercolor=PALETTE["border"],
        relief="flat",
        padding=(12, 12),
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=PALETTE["card"],
        foreground=PALETTE["purple_light"],
        font=("Segoe UI", 10, "bold"),
    )
    
    # Label styles with improved hierarchy
    style.configure(
        "Card.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9),
    )
    
    style.configure(
        "Muted.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["text_tertiary"],
        font=("Segoe UI", 8),
    )
    
    # Hero heading styles (for header section) - blue gradient effect
    style.configure(
        "HeroHeading.TLabel",
        background=PALETTE["gradient_start"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 14, "bold"),
    )
    
    style.configure(
        "HeroSubheading.TLabel",
        background=PALETTE["gradient_start"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9),
    )
    
    style.configure(
        "HeroMetric.TLabel",
        background=PALETTE["gradient_start"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 13, "bold"),
    )
    
    # Section header
    style.configure(
        "SectionHeader.TLabel",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 10, "bold"),
    )

    # Button styles with improved hover states
    style.configure(
        "TButton",
        background=PALETTE["surface"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9),
        padding=(12, 8),
        borderwidth=0,
        relief="flat",
        focuscolor="none",
    )
    style.map(
        "TButton",
        background=[
            ("active", PALETTE["surface_hover"]),
            ("disabled", PALETTE["surface"]),
        ],
        foreground=[("disabled", PALETTE["muted"])],
    )

    # Primary accent button - blue
    style.configure(
        "Accent.TButton",
        background=PALETTE["gradient_start"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9, "bold"),
        padding=(14, 8),
        borderwidth=0,
        relief="flat",
        focuscolor="none",
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", PALETTE["purple_hover"]),
            ("pressed", PALETTE["accent_dark"]),
            ("disabled", PALETTE["surface"]),
        ],
        foreground=[("disabled", PALETTE["muted"])],
    )
    
    # Secondary button
    style.configure(
        "Secondary.TButton",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9),
        padding=(12, 8),
        borderwidth=1,
        relief="flat",
        focuscolor="none",
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("active", PALETTE["card_hover"]),
            ("disabled", PALETTE["surface"]),
        ],
        bordercolor=[("", PALETTE["border"])],
        foreground=[("disabled", PALETTE["muted"])],
    )

    # Danger button
    style.configure(
        "Danger.TButton",
        background=PALETTE["danger"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9, "bold"),
        padding=(12, 8),
        borderwidth=0,
        relief="flat",
        focuscolor="none",
    )
    style.map(
        "Danger.TButton",
        background=[
            ("active", PALETTE["danger_light"]),
            ("pressed", "#dc2626"),
            ("disabled", PALETTE["surface"]),
        ],
        foreground=[("disabled", PALETTE["muted"])],
    )

    # Input field styles with focus states
    entry_style = {
        "background": PALETTE["surface"],
        "foreground": PALETTE["text"],
        "fieldbackground": PALETTE["surface"],
        "bordercolor": PALETTE["border"],
        "lightcolor": PALETTE["border"],
        "darkcolor": PALETTE["border"],
        "insertcolor": PALETTE["accent"],
        "selectbackground": PALETTE["purple"],
        "selectforeground": PALETTE["text"],
        "padding": 8,
    }
    
    style.configure("TEntry", **entry_style)
    style.configure("TCombobox", **entry_style)
    style.configure("TSpinbox", **entry_style)
    
    style.map(
        "TEntry",
        bordercolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["border"]),
        ],
        lightcolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["border"]),
        ],
        darkcolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["border"]),
        ],
    )
    
    style.map(
        "TCombobox",
        bordercolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["border"]),
        ],
        arrowcolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["text_secondary"]),
        ],
    )
    
    style.map(
        "TSpinbox",
        bordercolor=[
            ("focus", PALETTE["accent"]),
            ("!focus", PALETTE["border"]),
        ],
    )

    # Checkbox styles
    style.configure(
        "TCheckbutton",
        background=PALETTE["card"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 9),
        focuscolor="none",
    )
    style.map(
        "TCheckbutton",
        background=[("active", PALETTE["card"]), ("selected", PALETTE["card"])],
        indicatorcolor=[
            ("selected", PALETTE["accent"]),
            ("!selected", PALETTE["border"]),
        ],
        indicatorrelief=[("selected", "flat"), ("!selected", "flat")],
    )

    # Status badge labels - using green and yellow
    style.configure(
        "StatusInfo.TLabel",
        background=PALETTE["purple"],
        foreground=PALETTE["text"],
        padding=(8, 4),
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )
    
    style.configure(
        "StatusSuccess.TLabel",
        background=PALETTE["success"],
        foreground=PALETTE["bg"],
        padding=(8, 4),
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )
    
    style.configure(
        "StatusWarning.TLabel",
        background=PALETTE["warning"],
        foreground=PALETTE["bg"],
        padding=(8, 4),
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )
    
    style.configure(
        "StatusDanger.TLabel",
        background=PALETTE["danger"],
        foreground=PALETTE["text"],
        padding=(8, 4),
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )

    # Paned window styles
    style.configure(
        "TPanedwindow",
        background=PALETTE["bg"],
        borderwidth=0,
        sashwidth=8,
    )
    style.map(
        "TPanedwindow",
        background=[("background", PALETTE["bg"])],
    )
    
    # Scrollbar styles
    style.configure(
        "Vertical.TScrollbar",
        background=PALETTE["surface"],
        troughcolor=PALETTE["card"],
        bordercolor=PALETTE["card"],
        arrowcolor=PALETTE["text_secondary"],
        width=12,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", PALETTE["purple"])],
        arrowcolor=[("active", PALETTE["purple"])],
    )
    
    style.configure(
        "Horizontal.TScrollbar",
        background=PALETTE["surface"],
        troughcolor=PALETTE["card"],
        bordercolor=PALETTE["card"],
        arrowcolor=PALETTE["text_secondary"],
        width=12,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[("active", PALETTE["purple"])],
        arrowcolor=[("active", PALETTE["purple"])],
    )

    # Sizegrip
    style.configure(
        "TSizegrip",
        background=PALETTE["bg"],
    )

