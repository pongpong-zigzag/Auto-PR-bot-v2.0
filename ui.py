import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

from main import AutoPRBot


class TextLogger:
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget

    def __call__(self, message: str) -> None:
        self.text_widget.after(0, self._append, message)

    def _append(self, message: str) -> None:
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.see(tk.END)


class CoAuthorManager:
    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame
        self.co_authors: List[Dict[str, str]] = []
        self.co_author_frames: List[ttk.Frame] = []
        self._build_co_author_section()

    def _build_co_author_section(self):
        # Co-authors section
        co_authors_frame = ttk.LabelFrame(self.parent_frame, text="Co-Authors", padding=10)
        co_authors_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, padx=8, pady=6)
        
        # Add co-author button
        add_btn = ttk.Button(co_authors_frame, text="+ Add Co-Author", command=self._add_co_author)
        add_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Co-authors list frame
        self.co_authors_list_frame = ttk.Frame(co_authors_frame)
        self.co_authors_list_frame.pack(fill=tk.X)

    def _add_co_author(self):
        co_author_frame = ttk.Frame(self.co_authors_list_frame)
        co_author_frame.pack(fill=tk.X, pady=2)
        
        # Name entry
        name_var = tk.StringVar()
        name_entry = ttk.Entry(co_author_frame, textvariable=name_var, width=20)
        name_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Email entry
        email_var = tk.StringVar()
        email_entry = ttk.Entry(co_author_frame, textvariable=email_var, width=25)
        email_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(co_author_frame, text="Remove", 
                               command=lambda: self._remove_co_author(co_author_frame))
        remove_btn.pack(side=tk.LEFT)
        
        # Store references
        co_author_data = {
            'frame': co_author_frame,
            'name_var': name_var,
            'email_var': email_var
        }
        self.co_author_frames.append(co_author_data)
        
        # Add labels for first entry
        if len(self.co_author_frames) == 1:
            labels_frame = ttk.Frame(self.co_authors_list_frame)
            labels_frame.pack(fill=tk.X, pady=(0, 5))
            ttk.Label(labels_frame, text="Name", font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(labels_frame, text="Email", font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT, padx=(0, 5))

    def _remove_co_author(self, frame_to_remove: ttk.Frame):
        # Find and remove the co-author data
        for i, co_author_data in enumerate(self.co_author_frames):
            if co_author_data['frame'] == frame_to_remove:
                self.co_author_frames.pop(i)
                break
        
        # Destroy the frame
        frame_to_remove.destroy()
        
        # Remove labels if no co-authors left
        if not self.co_author_frames:
            for child in self.co_authors_list_frame.winfo_children():
                if isinstance(child, ttk.Frame) and len(child.winfo_children()) == 2:
                    child.destroy()

    def get_co_authors(self) -> List[Dict[str, str]]:
        co_authors = []
        for co_author_data in self.co_author_frames:
            name = co_author_data['name_var'].get().strip()
            email = co_author_data['email_var'].get().strip()
            if name and email:
                co_authors.append({"name": name, "email": email})
        return co_authors


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto PR Bot")
        self.geometry("700x600")
        self._bg_thread = None
        self._stop_event = threading.Event()

        # Inputs
        self.token_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.repo_var = tk.StringVar()
        self.uptime_var = tk.IntVar(value=60)
        self.base_branch_var = tk.StringVar(value="main")
        self.head_branch_var = tk.StringVar(value="dev")

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True)

        # Basic configuration section
        config_frame = ttk.LabelFrame(frm, text="Configuration", padding=10)
        config_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="GitHub Token").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.token_var, show="*").grid(row=0, column=1, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="Username / Owner").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.username_var).grid(row=1, column=1, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="Repository Name").grid(row=2, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.repo_var).grid(row=2, column=1, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="Base Branch").grid(row=3, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.base_branch_var).grid(row=3, column=1, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="Head Branch").grid(row=4, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.head_branch_var).grid(row=4, column=1, sticky=tk.EW, **pad)

        ttk.Label(config_frame, text="Uptime (seconds)").grid(row=5, column=0, sticky=tk.W, **pad)
        ttk.Entry(config_frame, textvariable=self.uptime_var).grid(row=5, column=1, sticky=tk.EW, **pad)

        config_frame.columnconfigure(1, weight=1)

        # Initialize co-author manager
        self.co_author_manager = CoAuthorManager(frm)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, columnspan=2, sticky=tk.EW, **pad)
        ttk.Button(btns, text="Run Once", command=self.on_run_once).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Start Loop", command=self.on_start_loop).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Stop Loop", command=self.on_stop_loop).pack(side=tk.LEFT, padx=4)

        # Log Area
        log_frame = ttk.LabelFrame(frm, text="Logs", padding=5)
        log_frame.grid(row=8, column=0, columnspan=2, sticky=tk.NSEW, **pad)
        self.log_text = tk.Text(log_frame, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        frm.rowconfigure(8, weight=1)

    def _build_repo_fullname(self) -> str:
        owner = self.username_var.get().strip()
        repo = self.repo_var.get().strip()
        return f"{owner}/{repo}"

    def _make_bot(self) -> AutoPRBot:
        token = self.token_var.get().strip()
        if not token:
            raise ValueError("Token is required")
        repo_full = self._build_repo_fullname()
        if "/" not in repo_full:
            raise ValueError("Provide valid owner and repository")
        logger = TextLogger(self.log_text)
        
        # Get co-authors from the manager
        co_authors = self.co_author_manager.get_co_authors()
        
        return AutoPRBot(
            token=token,
            repo=repo_full,
            base_branch=self.base_branch_var.get().strip() or "main",
            head_branch=self.head_branch_var.get().strip() or "dev",
            logger=logger,
            co_authors=co_authors,
        )

    def on_run_once(self):
        try:
            bot = self._make_bot()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        threading.Thread(target=self._run_once_thread, args=(bot,), daemon=True).start()

    def _run_once_thread(self, bot: AutoPRBot):
        try:
            bot.run_once()
        except Exception as e:
            bot.log(f"Error: {e}")

    def on_start_loop(self):
        if self._bg_thread and self._bg_thread.is_alive():
            messagebox.showinfo("Running", "Loop is already running")
            return
        try:
            bot = self._make_bot()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        interval = max(1, int(self.uptime_var.get() or 60))
        self._stop_event.clear()
        self._bg_thread = threading.Thread(target=self._loop_worker, args=(bot, interval), daemon=True)
        self._bg_thread.start()

    def _loop_worker(self, bot: AutoPRBot, interval: int):
        while not self._stop_event.is_set():
            try:
                bot.run_once()
            except Exception as e:
                bot.log(f"Error: {e}")
            self._stop_event.wait(interval)

    def on_stop_loop(self):
        if self._bg_thread and self._bg_thread.is_alive():
            self._stop_event.set()
            self.log_text.insert(tk.END, "Stop requested.\n")
            self.log_text.see(tk.END)


if __name__ == "__main__":
    app = App()
    app.mainloop()


