# app.py
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
import signal
import os

from utils.downloader import wget_available, CA_BUNDLE


WGET_BIN = "wget2"                                       # switch to "wget" if you prefer
PROGRESS_REGEX = re.compile(r"\[Files:\s+(\d+).*Todo:\s+(\d+)")  # parses wget2 stats


class MirrorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Offline Site Mirror")
        self.geometry("740x480")
        self.minsize(740, 480)

        # ── URL & path inputs ───────────────────────────────────────
        tk.Label(self, text="Website URL:").grid(row=0, column=0,
                                                 sticky="e", padx=6, pady=8)
        self.url_var = tk.StringVar()
        tk.Entry(self, textvariable=self.url_var, width=84).grid(row=0, column=1,
                                                                 padx=6, sticky="w")

        tk.Label(self, text="Save to folder:").grid(row=1, column=0, sticky="e",
                                                   padx=6)
        self.path_var = tk.StringVar()
        tk.Entry(self, textvariable=self.path_var, width=64).grid(row=1, column=1,
                                                                  sticky="w",
                                                                  padx=(6, 0))
        tk.Button(self, text="Browse…", command=self._choose_folder).grid(row=1,
                                                                          column=1,
                                                                          sticky="e",
                                                                          padx=6)

        # ── Buttons & progress bar ──────────────────────────────────
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=1, sticky="e", padx=6, pady=(6, 10))

        self.extract_btn = tk.Button(btn_frame, text="Extract",
                                     width=12, command=self._start_extract)
        self.extract_btn.pack(side="left", padx=(0, 6))

        self.cancel_btn = tk.Button(btn_frame, text="Cancel",
                                    width=12, state="disabled",
                                    command=self._cancel_download)
        self.cancel_btn.pack(side="left")

        self.progress_var = tk.StringVar(value="Progress: –")
        tk.Label(self, textvariable=self.progress_var).grid(row=2, column=0,
                                                            sticky="w",
                                                            padx=6, pady=(6, 10))

        self.pb = ttk.Progressbar(self, orient="horizontal",
                                  mode="determinate", length=620)
        self.pb.grid(row=3, column=0, columnspan=2, padx=6, sticky="we")
        self.pb["maximum"] = 1
        self.pb["value"] = 0

        # ── Scrolling log widget ────────────────────────────────────
        self.log = scrolledtext.ScrolledText(self, height=16, wrap=tk.NONE,
                                             state="disabled")
        self.log.grid(row=4, column=0, columnspan=2, padx=6, pady=(4, 6),
                      sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)

        if not wget_available(WGET_BIN):
            messagebox.showwarning("wget2 missing",
                                   f"'{WGET_BIN}' is not in PATH. Install it first!")

        # queue for thread→GUI messages
        self._queue: queue.Queue = queue.Queue()
        self.after(100, self._process_queue)

        # handle for running wget2 process
        self._proc: subprocess.Popen | None = None

        # intercept window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ────────────────────────────────────────────────────────────────
    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Select output directory")
        if folder:
            self.path_var.set(folder)

    def _start_extract(self):
        url = self.url_var.get().strip()
        out_dir = Path(self.path_var.get().strip()).expanduser()

        if not url or not out_dir:
            messagebox.showerror("Missing data",
                                 "Please provide both the URL and output folder.")
            return

        self.extract_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_var.set("Progress: starting…")
        self.pb["value"] = 0
        self.pb["maximum"] = 1
        self._clear_log()
        self._log(f"=== Mirroring {url} → {out_dir} ===\n")

        out_dir.mkdir(parents=True, exist_ok=True)
        threading.Thread(target=self._run_wget,
                         args=(url, out_dir),
                         daemon=True).start()

    # ── background thread ──────────────────────────────────────────
    def _run_wget(self, url: str, out_dir: Path):
        cmd = [
            WGET_BIN, "--verbose", "--mirror", "--convert-links",
            "--adjust-extension", "--page-requisites", "--no-parent",
            "-e", "robots=off", "--wait=1",
            url
        ]
        if CA_BUNDLE:
            cmd.insert(1, f"--ca-certificate={CA_BUNDLE}")

        # launch inside target dir
        self._proc = subprocess.Popen(
            cmd,
            cwd=out_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # makes kill easier on Windows
        )

        for line in self._proc.stdout:
            self._queue.put(line)
            m = PROGRESS_REGEX.search(line)
            if m:
                done, todo = map(int, m.groups())
                total = done + todo
                self._queue.put(("progress", done, total))

        self._proc.wait()
        self._queue.put(("done", self._proc.returncode, out_dir))
        self._proc = None  # clear handle

    # ── cancel button ──────────────────────────────────────────────
    def _cancel_download(self):
        if self._proc and self._proc.poll() is None:
            self._terminate_proc()
            self._log("\n=== Download cancelled by user ===\n")
        self._finish_ui()

    # ── queue handler in Tk thread ─────────────────────────────────
    def _process_queue(self):
        try:
            while True:
                item = self._queue.get_nowait()
                if isinstance(item, str):
                    self._log(item)
                elif item[0] == "progress":
                    _, done, total = item
                    self.pb["maximum"] = max(self.pb["maximum"], total)
                    self.pb["value"] = done
                    percent = (done / self.pb["maximum"]) * 100 if self.pb["maximum"] else 0
                    self.progress_var.set(f"Progress: {done}/{self.pb['maximum']} "
                                          f"files ({percent:.1f} %)")
                elif item[0] == "done":
                    _, rc, out_dir = item
                    self._finish_ui()
                    if rc == 0:
                        self._log("\n=== Mirror finished successfully ===\n")
                        messagebox.showinfo("Done",
                                            f"Mirror saved to:\n{out_dir}")
                    else:
                        self._log(f"\n=== wget2 exited with code {rc} ===\n")
                        messagebox.showerror("Error",
                                             f"wget2 exited with code {rc}")
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    # ── helper to reset buttons & progress ─────────────────────────
    def _finish_ui(self):
        self.extract_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.pb["value"] = min(self.pb["value"], self.pb["maximum"])
        self.progress_var.set("Progress: complete")

    # ── terminate child process safely ─────────────────────────────
    def _terminate_proc(self):
        if not self._proc or self._proc.poll() is not None:
            return
        try:
            if os.name == "nt":
                # Windows: send CTRL_BREAK to the process group
                os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)
            else:
                self._proc.terminate()
        except Exception:
            pass
        # give it a moment, then force-kill if needed
        try:
            self._proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._proc.kill()

    # ── window close handler ───────────────────────────────────────
    def _on_close(self):
        if self._proc and self._proc.poll() is None:
            if not messagebox.askyesno("Quit",
                                       "A download is still in progress.\n"
                                       "Close anyway and stop it?"):
                return
            self._terminate_proc()
        self.destroy()

    # ── log helpers ────────────────────────────────────────────────
    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


if __name__ == "__main__":
    MirrorGUI().mainloop()
