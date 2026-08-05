"""Theme-consistent modal dialogs used across Sword Phantasia."""

import tkinter as tk

from game_settings import apply_fullscreen


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


def show_guide(parent):
    """Open the title-screen player guide as a readable fullscreen reference."""
    window = tk.Toplevel(parent)
    window.title("Sword Phantasia — Guide & Controls")
    window.configure(bg=BG)
    window.transient(parent.winfo_toplevel())
    window.grab_set()
    apply_fullscreen(window)

    header = tk.Frame(window, bg="#0d131e", height=86, highlightbackground=BORDER, highlightthickness=1)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    copy = tk.Frame(header, bg="#0d131e")
    copy.pack(side=tk.LEFT, padx=34, pady=14)
    tk.Label(copy, text="GUIDE & CONTROLS", font=("Georgia", 21, "bold"), fg=TEXT, bg="#0d131e").pack(anchor="w")
    tk.Label(copy, text="A concise field manual for your journey.", font=("Segoe UI", 10), fg=MUTED, bg="#0d131e").pack(anchor="w")
    tk.Button(header, text="×", command=window.destroy, bg="#0d131e", fg=MUTED, activebackground="#54232c", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 21), cursor="hand2", padx=22).pack(side=tk.RIGHT, padx=20)

    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    shell_width = min(1160, max(900, int(screen_width * .88)))
    shell_height = min(660, max(560, int((screen_height - 100) * .90)))
    shell = tk.Frame(window, bg=BG, width=shell_width, height=shell_height)
    shell.place(relx=.5, rely=.54, anchor="center")
    shell.pack_propagate(False)
    navigation = tk.Frame(shell, bg=SURFACE, width=225, highlightbackground=BORDER, highlightthickness=1)
    navigation.pack(side=tk.LEFT, fill=tk.Y)
    navigation.pack_propagate(False)
    tk.Label(navigation, text="FIELD MANUAL", font=("Segoe UI", 9, "bold"), fg="#72809a", bg=SURFACE).pack(anchor="w", padx=20, pady=(22, 12))
    reader_panel = tk.Frame(shell, bg="#0b1019", highlightbackground=BORDER, highlightthickness=1)
    reader_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(14, 0))
    reader = tk.Text(reader_panel, state=tk.DISABLED, wrap=tk.WORD, bg="#0b1019", fg="#d4dbea", font=("Segoe UI", 12), relief=tk.FLAT, bd=0, padx=38, pady=30, spacing1=3, spacing3=10)
    scrollbar = tk.Scrollbar(reader_panel, command=reader.yview, bg=SURFACE, troughcolor="#0b1019", relief=tk.FLAT)
    reader.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    reader.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    reader.tag_configure("title", font=("Georgia", 27, "bold"), foreground="#ffd166", spacing3=18)
    reader.tag_configure("heading", font=("Segoe UI", 14, "bold"), foreground="#67b8ff", spacing1=14, spacing3=6)
    reader.tag_configure("key", font=("Consolas", 12, "bold"), foreground="#67dca5", lmargin1=12, lmargin2=12)
    reader.tag_configure("body", font=("Segoe UI", 12), foreground="#cbd4e5", lmargin1=12, lmargin2=12)
    reader.tag_configure("note", font=("Segoe UI", 11, "italic"), foreground="#c59af2", lmargin1=12, lmargin2=12)

    pages = {
        "QUICK START": [
            ("BEGIN YOUR JOURNEY\n", "title"),
            ("Explore the realm\n", "heading"),
            ("Use the directional controls to travel, or choose Explore to search the current area for battles, treasure, landmarks, materials, and story events.\n", "body"),
            ("Grow stronger\n", "heading"),
            ("Defeat enemies for EXP and gold, improve equipment at the blacksmith, and complete regional quests to unlock each champion.\n", "body"),
            ("Reach the throne\n", "heading"),
            ("Defeat the three region champions, reach level 10, then travel to the Primordial Throne for the final encounter.\n", "body"),
            ("Progress autosaves after encounters. Use Save Game before major battles or purchases.\n", "note"),
        ],
        "ADVENTURE": [
            ("ADVENTURE CONTROLS\n", "title"),
            ("W / ↑", "key"), ("   Move forward\n", "body"),
            ("S / ↓", "key"), ("   Move back\n", "body"),
            ("A / ←", "key"), ("   Move left\n", "body"),
            ("D / →", "key"), ("   Move right\n", "body"),
            ("I", "key"), ("   Inventory\n", "body"),
            ("E", "key"), ("   Equipment\n", "body"),
            ("M", "key"), ("   Region Map\n", "body"),
            ("Q", "key"), ("   Quest Log\n", "body"),
            ("F10", "key"), ("   Audio, settings, and player statistics\n", "body"),
            ("Escape", "key"), ("   Close the current screen or open Options\n", "body"),
        ],
        "COMBAT": [
            ("COMBAT REFERENCE\n", "title"),
            ("Read enemy intent\n", "heading"),
            ("The target panel reveals the enemy's next move. Heavy attacks are best answered with Defend or a class skill.\n", "body"),
            ("A", "key"), ("   Attack with the equipped weapon\n", "body"),
            ("D", "key"), ("   Defend, reduce damage, and recover MP\n", "body"),
            ("I", "key"), ("   Use a healing item\n", "body"),
            ("S", "key"), ("   Open the class skill deck\n", "body"),
            ("R", "key"), ("   Attempt to escape ordinary encounters\n", "body"),
            ("Class skills gain bonus damage when they interrupt a telegraphed heavy attack. Champions and bosses cannot be escaped.\n", "note"),
        ],
        "PROGRESSION": [
            ("PROGRESSION & SURVIVAL\n", "title"),
            ("Equipment\n", "heading"),
            ("Weapons increase damage and armor reduces incoming attacks. At the Ember & Anvil workshop, select any owned equipment and raise its damage or defense through five forge tiers.\n", "body"),
            ("Defeat recovery\n", "heading"),
            ("A defeat is recoverable: retry, return to camp, load the latest save, or return to the title screen.\n", "body"),
            ("Postgame mastery\n", "heading"),
            ("After level 10, ascended enemies appear. Class skills improve at levels 12 and 15 through Mastery II and III.\n", "body"),
        ],
    }
    buttons = {}

    def show_page(name):
        reader.config(state=tk.NORMAL)
        reader.delete("1.0", tk.END)
        for text, tag in pages[name]:
            reader.insert(tk.END, text, tag)
        reader.config(state=tk.DISABLED)
        reader.yview_moveto(0)
        for page, button in buttons.items():
            selected = page == name
            button.config(bg="#30415e" if selected else SURFACE, fg="#ffffff" if selected else MUTED)

    for name in pages:
        button = tk.Button(navigation, text=name, command=lambda page=name: show_page(page), bg=SURFACE, fg=MUTED, activebackground="#30415e", activeforeground="#ffffff", relief=tk.FLAT, bd=0, anchor="w", font=("Segoe UI", 10, "bold"), padx=20, pady=14, cursor="hand2")
        button.pack(fill=tk.X, padx=10, pady=2)
        buttons[name] = button
    tk.Label(navigation, text="ESC  CLOSE GUIDE", font=("Consolas", 9, "bold"), fg="#63718a", bg=SURFACE).pack(side=tk.BOTTOM, anchor="w", padx=20, pady=20)
    show_page("QUICK START")
    window.bind("<Escape>", lambda _event: window.destroy())
    parent.wait_window(window)
