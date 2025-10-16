import threading
import tkinter as tk
from tkinter import ttk, messagebox

from main import AutoPRBot


class TextLogger:
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget

    def __call__(self, message: str) -> None:
        self.text_widget.after(0, self._append, message)

    def _append(self, message: str) -> None:
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.see(tk.END)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto PR Bot")
        self.geometry("640x520")
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

        ttk.Label(frm, text="GitHub Token").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.token_var, show="*").grid(row=0, column=1, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Username / Owner").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.username_var).grid(row=1, column=1, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Repository Name").grid(row=2, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.repo_var).grid(row=2, column=1, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Base Branch").grid(row=3, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.base_branch_var).grid(row=3, column=1, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Head Branch").grid(row=4, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.head_branch_var).grid(row=4, column=1, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Uptime (seconds)").grid(row=5, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self.uptime_var).grid(row=5, column=1, sticky=tk.EW, **pad)

        frm.columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=6, column=0, columnspan=2, sticky=tk.EW, **pad)
        ttk.Button(btns, text="Run Once", command=self.on_run_once).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Start Loop", command=self.on_start_loop).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Stop Loop", command=self.on_stop_loop).pack(side=tk.LEFT, padx=4)

        # Log Area
        ttk.Label(frm, text="Logs").grid(row=7, column=0, columnspan=2, sticky=tk.W, **pad)
        self.log_text = tk.Text(frm, height=16)
        self.log_text.grid(row=8, column=0, columnspan=2, sticky=tk.NSEW, **pad)
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
        return AutoPRBot(
            token=token,
            repo=repo_full,
            base_branch=self.base_branch_var.get().strip() or "main",
            head_branch=self.head_branch_var.get().strip() or "dev",
            logger=logger,
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


