"""Theme-consistent modal dialogs used across Sword Phantasia."""

import tkinter as tk


BG = "#080b13"
SURFACE = "#111724"
BORDER = "#343e56"
TEXT = "#f3f5ff"
MUTED = "#aab4c9"


def _center(window, parent, width, height):
    parent.update_idletasks()
    x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
    y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def confirm(parent, title, message, confirm_text="CONFIRM", accent="#4ca8ff", danger=False):
    result = {"accepted": False}
    window = tk.Toplevel(parent)
    window.title(title)
    window.configure(bg=BG)
    window.resizable(False, False)
    window.transient(parent.winfo_toplevel())
    window.grab_set()
    width = 540
    lines = max(1, len(message) // 58 + message.count("\n") + 1)
    height = min(410, 225 + lines * 13)
    _center(window, parent.winfo_toplevel(), width, height)

    header = tk.Frame(window, bg=SURFACE, height=76, highlightbackground=BORDER, highlightthickness=1)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Frame(header, bg="#ff5967" if danger else accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
    tk.Label(header, text=title.upper(), font=("Georgia", 18, "bold"), fg=TEXT, bg=SURFACE).pack(side=tk.LEFT, padx=20)

    tk.Label(window, text=message, wraplength=470, justify=tk.LEFT, font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(fill=tk.BOTH, expand=True, padx=32, pady=25)
    actions = tk.Frame(window, bg=BG)
    actions.pack(fill=tk.X, padx=28, pady=(0, 24))

    def choose(value):
        result["accepted"] = value
        window.destroy()

    tk.Button(actions, text="CANCEL", command=lambda: choose(False), bg="#202a3d", fg=TEXT, activebackground="#34425e", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"), padx=22, pady=11).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
    primary = "#8f2d3c" if danger else accent
    hover = "#c43d4e" if danger else "#6ab7ff"
    tk.Button(actions, text=confirm_text, command=lambda: choose(True), bg=primary, fg="#ffffff", activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"), padx=22, pady=11).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
    window.bind("<Escape>", lambda _event: choose(False))
    window.bind("<Return>", lambda _event: choose(True))
    parent.wait_window(window)
    return result["accepted"]


def alert(parent, title, message, accent="#4ca8ff", button_text="CONTINUE"):
    window = tk.Toplevel(parent)
    window.title(title)
    window.configure(bg=BG)
    window.resizable(False, False)
    window.transient(parent.winfo_toplevel())
    window.grab_set()
    width, height = 560, 340
    _center(window, parent.winfo_toplevel(), width, height)
    header = tk.Frame(window, bg=SURFACE, height=76, highlightbackground=BORDER, highlightthickness=1)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Frame(header, bg=accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
    tk.Label(header, text=title.upper(), font=("Georgia", 18, "bold"), fg=TEXT, bg=SURFACE).pack(side=tk.LEFT, padx=20)
    tk.Label(window, text=message, wraplength=490, justify=tk.LEFT, font=("Segoe UI", 10), fg=MUTED, bg=BG).pack(fill=tk.BOTH, expand=True, padx=32, pady=24)
    tk.Button(window, text=button_text, command=window.destroy, bg=accent, fg="#ffffff", activebackground="#6ab7ff", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"), pady=11).pack(fill=tk.X, padx=32, pady=(0, 24))
    window.bind("<Escape>", lambda _event: window.destroy())
    window.bind("<Return>", lambda _event: window.destroy())
    parent.wait_window(window)
