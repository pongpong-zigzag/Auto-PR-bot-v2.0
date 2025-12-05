from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

from autopr_bot import AutoPRBot
from autopr_bot.content import generate_pr_content, generate_readme_content

from .coauthors import CoAuthorManager
from .logger import TextLogger
from .styles import PALETTE, apply_style


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Auto PR Bot Studio")
        self.geometry("1120x720")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        apply_style(self)
        
        # Show loading screen first, then initialize UI after 3 seconds
        self._show_loading_screen()
        self.after(3000, self._initialize_after_loading)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        # Create container frame - will blend with gradient background
        container = ttk.Frame(self, style="Root.TFrame", padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container, style="CardAccent.TFrame", padding=(20, 16))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)
        header.columnconfigure(2, weight=0)

        title_frame = ttk.Frame(header, style="CardAccent.TFrame")
        title_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Label(title_frame, text="Auto PR Bot Studio", style="HeroHeading.TLabel").pack(anchor="w")
        ttk.Label(
            title_frame,
            text="Automate README refreshes, PR creation, and merges — all inside a live dashboard.",
            style="HeroSubheading.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        controls_frame = ttk.Frame(header, style="CardAccent.TFrame")
        controls_frame.grid(row=0, column=2, sticky="e", padx=(0, 0))
        
        self.status_label = ttk.Label(controls_frame, textvariable=self.status_var, style="StatusInfo.TLabel")
        self.status_label.pack(anchor="e", pady=(0, 6))
        
        ttk.Button(controls_frame, text="Preview Sample Content", command=self.on_preview_content).pack(anchor="e")

        metrics_frame = ttk.Frame(header, style="CardAccent.TFrame")
        metrics_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        metrics = [
            ("Base Branch", self.base_branch_var),
            ("Head Branch", self.head_branch_var),
            ("Loop Interval (s)", self.uptime_var),
        ]
        for idx, (label, var) in enumerate(metrics):
            col = ttk.Frame(metrics_frame, style="CardAccent.TFrame")
            col.grid(row=0, column=idx, sticky="ew", padx=(0, 12 if idx < len(metrics) - 1 else 0))
            metrics_frame.columnconfigure(idx, weight=1)
            ttk.Label(col, text=label, style="HeroSubheading.TLabel").pack(anchor="w")
            ttk.Label(col, textvariable=var, style="HeroMetric.TLabel").pack(anchor="w", pady=(1, 0))

        paned = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew")

        forms_panel = ttk.Frame(paned, style="Root.TFrame")
        forms_panel.columnconfigure(0, weight=1)
        forms_panel.rowconfigure(0, weight=1)
        paned.add(forms_panel, weight=3)

        # Create scrollable frame for cards
        canvas = tk.Canvas(forms_panel, bg=PALETTE["bg"], highlightthickness=0)
        scrollbar_forms = ttk.Scrollbar(forms_panel, orient=tk.VERTICAL, command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = ttk.Frame(canvas, style="Root.TFrame")
        
        def update_scroll_region(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_forms.set)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Also bind to child widgets
        def bind_to_children(parent):
            for child in parent.winfo_children():
                try:
                    child.bind("<MouseWheel>", on_mousewheel)
                    bind_to_children(child)
                except:
                    pass
        
        bind_to_children(scrollable_frame)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_forms.grid(row=0, column=1, sticky="ns")
        
        cards_container = ttk.Frame(scrollable_frame, style="Root.TFrame")
        cards_container.pack(fill=tk.BOTH, expand=True)
        cards_container.columnconfigure(0, weight=1)
        
        # Store canvas reference for later updates
        self._cards_canvas = canvas
        self._scrollable_frame = scrollable_frame

        self._build_config_card(cards_container, row=0)
        self._build_automation_card(cards_container, row=1)
        self._build_author_card(cards_container, row=2)
        self._build_collaboration_card(cards_container, row=3)

        log_panel = ttk.Frame(paned, style="Root.TFrame")
        log_panel.columnconfigure(0, weight=1)
        log_panel.rowconfigure(0, weight=1)
        paned.add(log_panel, weight=2)

        log_card = ttk.LabelFrame(log_panel, text="Activity Stream", style="Card.TLabelframe")
        log_card.grid(row=0, column=0, sticky="nsew")
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)

        ttk.Label(
            log_card,
            text="Live output from GitHub operations, loop events, and previews.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        log_container = ttk.Frame(log_card, style="Card.TFrame")
        log_container.grid(row=1, column=0, sticky="nsew")
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_container,
            height=20,
            bg=PALETTE["card"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["accent"],
            relief=tk.FLAT,
            font=("Consolas", 9),
            wrap=tk.WORD,
            padx=12,
            pady=8,
            selectbackground=PALETTE["purple"],
            selectforeground=PALETTE["text"],
            borderwidth=0,
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text["yscrollcommand"] = scrollbar.set

        log_footer = ttk.Frame(log_card, style="Card.TFrame")
        log_footer.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        log_footer.columnconfigure(0, weight=1)
        ttk.Label(log_footer, text="Logs auto-scroll during runs.", style="Muted.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))
        ttk.Button(log_footer, text="Clear Logs", command=lambda: self.log_text.delete("1.0", tk.END)).grid(
            row=0, column=1, sticky="e"
        )

        sizegrip = ttk.Sizegrip(container, style="TSizegrip")
        sizegrip.grid(row=2, column=0, sticky="se", pady=(12, 0))

        self.logger = TextLogger(self.log_text)

    def _build_config_card(self, parent: ttk.Frame, row: int) -> None:
        card = ttk.LabelFrame(parent, text="Repository Settings", style="Card.TLabelframe")
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        card.columnconfigure(1, weight=1)

        fields = [
            ("GitHub Token", self.token_var, {"show": "*"}, "Personal Access Token with 'repo' scope"),
            ("Username / Owner", self.username_var, {}, "GitHub username or organization name"),
            ("Repository", self.repo_var, {}, "Repository name (without owner)"),
            ("Base Branch", self.base_branch_var, {}, "Target branch (usually 'main' or 'master')"),
            ("Head Branch", self.head_branch_var, {}, "Source branch for PRs (usually 'dev')"),
        ]

        for idx, (label, var, extra, tooltip_text) in enumerate(fields):
            label_widget = ttk.Label(card, text=label, style="Card.TLabel")
            label_widget.grid(row=idx, column=0, sticky="w", pady=(8 if idx == 0 else 4, 4), padx=(0, 12))
            
            entry = ttk.Entry(card, textvariable=var, **extra)
            entry.grid(row=idx, column=1, sticky="ew", pady=(8 if idx == 0 else 4, 4))
            
            # Add tooltip
            self._create_tooltip(entry, tooltip_text)

    def _build_automation_card(self, parent: ttk.Frame, row: int) -> None:
        card = ttk.LabelFrame(parent, text="Automation", style="Card.TLabelframe")
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        card.columnconfigure(0, weight=1)

        interval_row = ttk.Frame(card, style="Card.TFrame")
        interval_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(interval_row, text="Loop Interval (seconds)", style="Card.TLabel").pack(side=tk.LEFT)
        ttk.Spinbox(
            interval_row,
            textvariable=self.uptime_var,
            from_=10,
            to=3600,
            increment=10,
            width=12,
        ).pack(side=tk.RIGHT)
        self._create_tooltip(interval_row, "Interval between automation cycles in seconds")

        self.loop_label = ttk.Label(card, textvariable=self.loop_var, style="Muted.TLabel")
        self.loop_label.grid(row=1, column=0, sticky="w", pady=(0, 10))

        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.grid(row=2, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        buttons.columnconfigure(2, weight=1)

        self.run_button = ttk.Button(buttons, text="Run Once", style="Accent.TButton", command=self.on_run_once)
        self.run_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.loop_button = ttk.Button(buttons, text="Start Loop", style="Secondary.TButton", command=self.on_start_loop)
        self.loop_button.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self.stop_button = ttk.Button(
            buttons,
            text="Stop Loop",
            style="Danger.TButton",
            command=self.on_stop_loop,
            state=tk.DISABLED,
        )
        self.stop_button.grid(row=0, column=2, sticky="ew")

    def _build_author_card(self, parent: ttk.Frame, row: int) -> None:
        card = ttk.LabelFrame(parent, text="Commit Author Settings", style="Card.TLabelframe")
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        card.columnconfigure(1, weight=1)

        # Info section
        info_frame = ttk.Frame(card, style="Card.TFrame")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        
        ttk.Label(
            info_frame,
            text="✨ Automatic Features:",
            style="Card.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        
        auto_features = [
            "📅 Commit dates are randomly assigned between 2022 and current date (always in the past)",
            "👤 Author is automatically set to repository owner",
        ]
        for idx, feature in enumerate(auto_features, start=1):
            ttk.Label(
                info_frame,
                text=feature,
                style="Muted.TLabel",
            ).grid(row=idx, column=0, sticky="w", padx=(12, 0), pady=(2, 0))

        ttk.Separator(card, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 12))

        # Author override fields
        author_frame = ttk.Frame(card, style="Card.TFrame")
        author_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        author_frame.columnconfigure(1, weight=1)

        ttk.Label(
            card,
            text="Override Author (optional):",
            style="Card.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

        fields = [
            ("Author Name", self.commit_author_name_var, "Override default author name"),
            ("Author Email", self.commit_author_email_var, "Override default author email"),
        ]

        for idx, (label, var, tooltip_text) in enumerate(fields):
            ttk.Label(author_frame, text=label, style="Card.TLabel").grid(
                row=idx, column=0, sticky="w", pady=4, padx=(0, 12)
            )
            entry = ttk.Entry(author_frame, textvariable=var)
            entry.grid(row=idx, column=1, sticky="ew", pady=4)
            self._create_tooltip(entry, tooltip_text)

    def _build_collaboration_card(self, parent: ttk.Frame, row: int) -> None:
        card = ttk.LabelFrame(parent, text="Collaboration", style="Card.TLabelframe")
        card.grid(row=row, column=0, sticky="new")
        card.columnconfigure(0, weight=1)

        ttk.Checkbutton(
            card,
            text="Include co-authors in README commits",
            variable=self.use_co_authors_var,
            command=self._toggle_co_authors,
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            card,
            text="When enabled, commits will include the selected collaborators.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        self.co_author_manager = CoAuthorManager(card)
        self.co_author_manager.frame.grid(row=2, column=0, sticky="new")
        if not self.co_author_manager.has_rows():
            self.co_author_manager.add_row()
        self._toggle_co_authors()

    # ------------------------------------------------------------------ #
    def _make_bot(self) -> AutoPRBot:
        token = self.token_var.get().strip()
        if not token:
            raise ValueError("Token is required.")

        owner = self.username_var.get().strip()
        repo = self.repo_var.get().strip()
        if not owner or not repo:
            raise ValueError("Provide both the repository owner and name.")

        repo_full = f"{owner}/{repo}"
        co_authors = self.co_author_manager.get_co_authors() if self.use_co_authors_var.get() else []
        
        # Author configuration (dates are always random)
        commit_author_name = self.commit_author_name_var.get().strip() or None
        commit_author_email = self.commit_author_email_var.get().strip() or None

        return AutoPRBot(
            token=token,
            repo=repo_full,
            base_branch=self.base_branch_var.get().strip() or "main",
            head_branch=self.head_branch_var.get().strip() or "dev",
            logger=self.logger,
            co_authors=co_authors,
            commit_author_name=commit_author_name,
            commit_author_email=commit_author_email,
        )

    def on_run_once(self) -> None:
        try:
            bot = self._make_bot()
        except Exception as exc:
            messagebox.showerror("Configuration Error", str(exc))
            return

        self.run_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._run_once_thread, args=(bot,), daemon=True)
        thread.start()

    def _run_once_thread(self, bot: AutoPRBot) -> None:
        self._set_status("Running single sync…", "info")
        try:
            bot.run_once()
            self._set_status("Run completed successfully.", "success")
        except Exception as exc:
            bot.log(f"Error: {exc}")
            self._set_status("Run failed. Check logs for details.", "danger")
        finally:
            self.after(0, lambda: self.run_button.config(state=tk.NORMAL))

    def on_start_loop(self) -> None:
        if self._bg_thread and self._bg_thread.is_alive():
            messagebox.showinfo("Loop Running", "The loop is already running.")
            return

        try:
            bot = self._make_bot()
        except Exception as exc:
            messagebox.showerror("Configuration Error", str(exc))
            return

        interval = max(10, int(self.uptime_var.get() or 60))
        self._stop_event.clear()
        self.loop_var.set(f"Loop running every {interval}s.")
        self._set_status("Loop running…", "success")

        self.loop_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.DISABLED)

        self._bg_thread = threading.Thread(target=self._loop_worker, args=(bot, interval), daemon=True)
        self._bg_thread.start()

    def _loop_worker(self, bot: AutoPRBot, interval: int) -> None:
        while not self._stop_event.is_set():
            try:
                bot.run_once()
                timestamp = datetime.now().strftime("%H:%M:%S")
                self._set_loop_message(f"Last run completed at {timestamp}.")
            except Exception as exc:
                bot.log(f"Error: {exc}")
                self._set_status("Loop encountered errors. See logs.", "danger")
            if self._stop_event.wait(interval):
                break
        self._set_loop_message("Loop stopped.")
        self._set_status("Loop stopped.", "warning")
        self.after(0, self._reset_controls_after_loop)

    def on_stop_loop(self) -> None:
        if self._bg_thread and self._bg_thread.is_alive():
            self._stop_event.set()
            self._set_status("Stopping loop…", "warning")
            self.stop_button.config(state=tk.DISABLED)

    def _reset_controls_after_loop(self) -> None:
        self.loop_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def _toggle_co_authors(self) -> None:
        if self.use_co_authors_var.get():
            self.co_author_manager.frame.grid()
            if not self.co_author_manager.has_rows():
                self.co_author_manager.add_row()
        else:
            self.co_author_manager.frame.grid_remove()
        # Update scroll region when toggling
        if hasattr(self, '_cards_canvas'):
            self.after(10, lambda: self._cards_canvas.configure(scrollregion=self._cards_canvas.bbox("all")))


    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Create a tooltip that appears on hover."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=text,
                background=PALETTE["surface"],
                foreground=PALETTE["text"],
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 8),
                padx=8,
                pady=4,
            )
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def on_preview_content(self) -> None:
        pr = generate_pr_content()
        readme = generate_readme_content()
        self.logger("\n--- SAMPLE PR CONTENT ---")
        self.logger(f"Title: {pr['title']}")
        self.logger(pr["body"])
        self.logger("--- SAMPLE README CONTENT ---")
        self.logger(readme)

    def _set_status(self, message: str, level: str = "info") -> None:
        style_map = {
            "info": "StatusInfo.TLabel",
            "success": "StatusSuccess.TLabel",
            "warning": "StatusWarning.TLabel",
            "danger": "StatusDanger.TLabel",
        }
        style = style_map.get(level, "StatusInfo.TLabel")

        def update() -> None:
            self.status_var.set(message)
            self.status_label.configure(style=style)

        self.after(0, update)

    def _set_loop_message(self, message: str) -> None:
        self.after(0, lambda: self.loop_var.set(message))

    def _on_close(self) -> None:
        self._stop_event.set()
        self.destroy()

    def run(self) -> None:
        self.mainloop()

    # ------------------------------------------------------------------ #
    # Window helpers
    # ------------------------------------------------------------------ #
    def _show_loading_screen(self) -> None:
        """Display a loading screen for 3 seconds."""
        # Create loading screen overlay
        self._loading_frame = tk.Frame(self, bg=PALETTE["bg_gradient_start"])
        self._loading_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create gradient background for loading screen
        loading_canvas = tk.Canvas(
            self._loading_frame,
            highlightthickness=0,
            borderwidth=0,
            bg=PALETTE["bg_gradient_start"]
        )
        loading_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Draw gradient on loading screen
        def draw_loading_gradient():
            width = self.winfo_width()
            height = self.winfo_height()
            if width > 1 and height > 1:
                loading_canvas.delete("gradient")
                start_color = PALETTE["bg_gradient_start"]
                end_color = PALETTE["bg_gradient_end"]
                r1, g1, b1 = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
                r2, g2, b2 = int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16)
                
                for y in range(height):
                    ratio = y / height
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    loading_canvas.create_line(0, y, width, y, fill=color, width=1, tags="gradient")
        
        self.update_idletasks()
        draw_loading_gradient()
        self.bind("<Configure>", lambda e: draw_loading_gradient())
        
        # Loading content - use canvas for text overlay (text only, transparent background)
        content_frame = tk.Canvas(
            self._loading_frame,
            highlightthickness=0,
            borderwidth=0,
            bg=PALETTE["bg_gradient_start"]  # Will blend with gradient
        )
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
        
        # Store canvas reference for updates
        self._loading_canvas = content_frame
        
        # App icon/logo (text only)
        content_frame.create_text(
            200, 40,
            text="PR",
            font=("Segoe UI", 48, "bold"),
            fill=PALETTE["text"],
            anchor="center"
        )
        
        # Loading text (text only)
        content_frame.create_text(
            200, 110,
            text="Auto PR Bot Studio",
            font=("Segoe UI", 20, "bold"),
            fill=PALETTE["text"],
            anchor="center"
        )
        
        # Loading spinner text (text only, no background box)
        self._loading_text_id = content_frame.create_text(
            200, 140,
            text="Loading...",
            font=("Segoe UI", 12),
            fill=PALETTE["text_secondary"],
            anchor="center"
        )
        
        # Progress bar container - positioned below loading text
        progress_container = tk.Canvas(
            self._loading_frame,
            width=280,
            height=10,
            highlightthickness=0,
            borderwidth=0,
            bg=PALETTE["bg_gradient_start"]
        )
        progress_container.place(relx=0.5, rely=0.55, anchor="center")
        
        self._progress_canvas = progress_container
        self._progress_start_time = datetime.now()
        self._animate_progress()
        
        # Animate loading dots
        self._loading_dots = 0
        self._animate_loading()
    
    def _animate_loading(self) -> None:
        """Animate loading dots."""
        try:
            if hasattr(self, '_loading_canvas') and hasattr(self, '_loading_frame') and self._loading_frame.winfo_exists():
                dots = "." * (self._loading_dots % 4)
                self._loading_canvas.itemconfig(self._loading_text_id, text=f"Loading{dots}")
                self._loading_dots += 1
                self.after(500, self._animate_loading)
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, stop animation
            pass
    
    def _animate_progress(self) -> None:
        """Animate progress bar with rounded corners and gradient."""
        try:
            # Check if widgets still exist
            if not (hasattr(self, '_progress_canvas') and hasattr(self, '_loading_frame')):
                return
            
            # Check if the frame widget is still valid
            if not self._loading_frame.winfo_exists():
                return
            
            # Clear previous progress
            self._progress_canvas.delete("progress")
            
            width = 280
            height = 10
            radius = 5  # Roundness for smooth corners
            
            # Calculate progress based on time (0-100% over 3 seconds)
            elapsed = (datetime.now() - self._progress_start_time).total_seconds()
            progress = min(100, (elapsed / 3.0) * 100)
            
            # Draw background track with rounded corners using ovals
            # Background track - main rectangle
            self._progress_canvas.create_rectangle(
                radius, 0, width - radius, height,
                fill=PALETTE["surface"],
                outline="",
                tags="progress"
            )
            # Rounded corners for background
            self._progress_canvas.create_oval(0, 0, radius * 2, radius * 2, fill=PALETTE["surface"], outline="", tags="progress")
            self._progress_canvas.create_oval(width - radius * 2, 0, width, radius * 2, fill=PALETTE["surface"], outline="", tags="progress")
            self._progress_canvas.create_oval(0, height - radius * 2, radius * 2, height, fill=PALETTE["surface"], outline="", tags="progress")
            self._progress_canvas.create_oval(width - radius * 2, height - radius * 2, width, height, fill=PALETTE["surface"], outline="", tags="progress")
            
            # Draw progress bar with rounded corners and gradient
            bar_width = int((progress / 100.0) * width)
            if bar_width > 0:
                # Create gradient effect
                gradient_start = PALETTE["gradient_start"]
                gradient_end = PALETTE["gradient_end"]
                r1, g1, b1 = int(gradient_start[1:3], 16), int(gradient_start[3:5], 16), int(gradient_start[5:7], 16)
                r2, g2, b2 = int(gradient_end[1:3], 16), int(gradient_end[3:5], 16), int(gradient_end[5:7], 16)
                
                # Draw left rounded corner first
                if bar_width >= radius:
                    # Left rounded corners
                    self._progress_canvas.create_oval(
                        0, 0, radius * 2, radius * 2,
                        fill=gradient_start, outline="", tags="progress"
                    )
                    self._progress_canvas.create_oval(
                        0, height - radius * 2, radius * 2, height,
                        fill=gradient_start, outline="", tags="progress"
                    )
                    # Fill vertical section between corners
                    self._progress_canvas.create_rectangle(
                        0, radius, radius, height - radius,
                        fill=gradient_start, outline="", tags="progress"
                    )
                
                # Draw main progress bar body with gradient
                if bar_width > radius:
                    # Draw gradient segments for smooth transition
                    segments = 60
                    main_width = bar_width - radius
                    segment_width = main_width / segments if segments > 0 else main_width
                    
                    for i in range(int(segments)):
                        x_start = radius + int(i * segment_width)
                        x_end = radius + int((i + 1) * segment_width)
                        if x_end > bar_width:
                            x_end = bar_width
                        if x_end > x_start:
                            ratio = i / segments if segments > 0 else 0
                            r = int(r1 + (r2 - r1) * ratio)
                            g = int(g1 + (g2 - g1) * ratio)
                            b = int(b1 + (b2 - b1) * ratio)
                            color = f"#{r:02x}{g:02x}{b:02x}"
                            
                            self._progress_canvas.create_rectangle(
                                x_start, 0, x_end, height,
                                fill=color, outline="", tags="progress"
                            )
                
                # Draw right rounded corner if bar reaches the end
                if bar_width >= width - radius:
                    # Right rounded corners
                    self._progress_canvas.create_oval(
                        width - radius * 2, 0, width, radius * 2,
                        fill=gradient_end, outline="", tags="progress"
                    )
                    self._progress_canvas.create_oval(
                        width - radius * 2, height - radius * 2, width, height,
                        fill=gradient_end, outline="", tags="progress"
                    )
                    # Fill vertical section between corners
                    self._progress_canvas.create_rectangle(
                        width - radius, radius, width, height - radius,
                        fill=gradient_end, outline="", tags="progress"
                    )
            
            if progress < 100:
                try:
                    # Check if widget still exists before scheduling next animation
                    if hasattr(self, '_loading_frame') and self._loading_frame.winfo_exists():
                        self.after(30, self._animate_progress)
                except (tk.TclError, AttributeError):
                    # Widget destroyed, stop animation
                    pass
        except (tk.TclError, AttributeError):
            # Widget has been destroyed during drawing, stop animation
            return
    
    def _initialize_after_loading(self) -> None:
        """Initialize the main UI after loading screen."""
        # Stop animations and remove loading screen
        if hasattr(self, '_loading_frame'):
            # Cancel any pending animations by destroying the frame
            try:
                self._loading_frame.destroy()
            except (tk.TclError, AttributeError):
                pass
            # Clear references to stop animations
            if hasattr(self, '_loading_canvas'):
                delattr(self, '_loading_canvas')
            if hasattr(self, '_progress_canvas'):
                delattr(self, '_progress_canvas')
            if hasattr(self, '_loading_frame'):
                delattr(self, '_loading_frame')
        
        # Initialize main UI components
        self._create_gradient_background()
        self._set_base_fonts()
        self._icon_image = self._build_icon()
        self.iconphoto(True, self._icon_image)

        # Async helpers
        self._bg_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Tk variables
        self.token_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.repo_var = tk.StringVar()
        self.base_branch_var = tk.StringVar(value="main")
        self.head_branch_var = tk.StringVar(value="dev")
        self.uptime_var = tk.IntVar(value=60)
        self.use_co_authors_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Idle • Waiting for configuration")
        self.loop_var = tk.StringVar(value="Loop stopped.")
        
        # Author configuration (dates are always random)
        self.commit_author_name_var = tk.StringVar()
        self.commit_author_email_var = tk.StringVar()

        self._build_ui()
    
    def _create_gradient_background(self) -> None:
        """Create a gradient background using a canvas behind all widgets."""
        # Create a canvas for the gradient background
        self._bg_canvas = tk.Canvas(
            self,
            highlightthickness=0,
            borderwidth=0,
        )
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Canvas is created first, so it will naturally be behind other widgets
        
        # Bind to window resize to update gradient
        def update_gradient(event=None):
            width = self.winfo_width()
            height = self.winfo_height()
            if width > 1 and height > 1:
                self._bg_canvas.delete("gradient")
                # Create gradient from blue to darker blue
                start_color = PALETTE["bg_gradient_start"]  # Blue
                end_color = PALETTE["bg_gradient_end"]      # Darker Blue
                
                # Parse hex colors
                r1, g1, b1 = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
                r2, g2, b2 = int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16)
                
                # Create vertical gradient
                for y in range(height):
                    ratio = y / height
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self._bg_canvas.create_line(0, y, width, y, fill=color, width=1, tags="gradient")
        
        self.bind("<Configure>", update_gradient)
        self.update_idletasks()
        update_gradient()
    
    def _set_base_fonts(self) -> None:
        base_fonts = [
            "TkDefaultFont",
            "TkMenuFont",
            "TkTextFont",
            "TkFixedFont",
            "TkHeadingFont",
            "TkTooltipFont",
            "TkIconFont",
            "TkCaptionFont",
            "TkSmallCaptionFont",
        ]
        for font_name in base_fonts:
            try:
                tkfont.nametofont(font_name).configure(size=8)
            except tk.TclError:
                continue

    def _build_icon(self) -> tk.PhotoImage:
        """Load icon from PNG file or create programmatic fallback."""
        # Try to load icon from assets/PR.png
        icon_paths = [
            # Path when running from project root
            Path(__file__).parent.parent.parent / "assets" / "PR.png",
            # Path when running as executable (PyInstaller bundle)
            Path(sys.executable).parent / "assets" / "PR.png",
            # Path relative to current directory
            Path("assets") / "PR.png",
            # Absolute path fallback
            Path(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "PR.png")).resolve(),
        ]
        
        for icon_path in icon_paths:
            try:
                if icon_path.exists() and icon_path.is_file():
                    icon = tk.PhotoImage(file=str(icon_path))
                    return icon
            except (tk.TclError, Exception):
                continue
        
        # Fallback: Create programmatic icon if PNG file not found
        size = 64
        icon = tk.PhotoImage(width=size, height=size)
        
        # Gradient background using blue gradient
        accent = PALETTE["gradient_start"]  # Light Blue
        gradient_end = PALETTE["gradient_end"]  # Medium Blue
        r1, g1, b1 = int(accent[1:3], 16), int(accent[3:5], 16), int(accent[5:7], 16)
        r2, g2, b2 = int(gradient_end[1:3], 16), int(gradient_end[3:5], 16), int(gradient_end[5:7], 16)
        
        for y in range(size):
            ratio = y / size
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            icon.put(color, to=(0, y, size, y + 1))
        
        # Draw stylized "PR" letters in white
        letter_color = PALETTE["text"]
        # Letter P
        for y in range(14, 50):
            icon.put(letter_color, to=(14, y, 18, y + 1))
        for x in range(14, 30):
            icon.put(letter_color, to=(x, 14, x + 1, 18))
            icon.put(letter_color, to=(x, 28, x + 1, 32))
        for y in range(14, 32):
            icon.put(letter_color, to=(26, y, 30, y + 1))
        
        # Letter R
        for y in range(14, 50):
            icon.put(letter_color, to=(34, y, 38, y + 1))
        for x in range(34, 50):
            icon.put(letter_color, to=(x, 14, x + 1, 18))
            icon.put(letter_color, to=(x, 28, x + 1, 32))
        for y in range(14, 32):
            icon.put(letter_color, to=(46, y, 50, y + 1))
        # R diagonal
        for i in range(12):
            icon.put(letter_color, to=(38 + i, 32 + i, 42 + i, 36 + i))
        
        return icon


def launch() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    launch()


