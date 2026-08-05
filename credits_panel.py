import os
import sys
import tkinter as tk

from game_settings import apply_fullscreen


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class EndCreditsScreen(tk.Toplevel):
    """Animated end credits shown after the final victory."""

    BG = "#05070d"
    TEXT = "#eef2ff"
    MUTED = "#8390aa"
    GOLD = "#ffd166"
    PURPLE = "#bd8cff"

    def __init__(self, parent, player):
        super().__init__(parent)
        self.player = player
        self.result = "quit"
        self._scroll_job = None
        self._finished = False
        self.title("Sword Phantasia — End Credits")
        self.configure(bg=self.BG)
        self.transient(parent)
        self.grab_set()
        apply_fullscreen(self)
        self.protocol("WM_DELETE_WINDOW", lambda: self._choose("quit"))

        self.canvas = tk.Canvas(self, bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.update_idletasks()
        self.width = max(900, self.canvas.winfo_width())
        self.height = max(620, self.canvas.winfo_height())
        self._draw_backdrop()
        self._create_credits()

        self.skip_btn = tk.Button(
            self,
            text="SKIP CREDITS  ›",
            command=self._show_finale,
            bg="#141b29",
            fg="#aab5ca",
            activebackground="#26334b",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            padx=18,
            pady=9,
        )
        self.skip_btn.place(relx=0.975, rely=0.96, anchor="se")
        self.bind("<Escape>", lambda _event: self._show_finale())
        self.bind("<Return>", lambda _event: self._show_finale())
        self.focus_set()
        self._scroll_job = self.after(700, self._scroll_credits)
        self.wait_window(self)

    def _draw_backdrop(self):
        canvas = self.canvas
        canvas.create_polygon(0, 0, self.width, 0, self.width, self.height, int(self.width * .72), self.height, int(self.width * .42), 0, fill="#080d18", outline="", tags="backdrop")
        canvas.create_polygon(0, self.height, 0, int(self.height * .4), int(self.width * .35), self.height, fill="#0b1220", outline="", tags="backdrop")
        stars = ((.08, .12, 2), (.18, .31, 1), (.30, .17, 2), (.72, .13, 1), (.88, .28, 2), (.93, .61, 1), (.12, .72, 1), (.67, .76, 2), (.81, .88, 1))
        for x_ratio, y_ratio, size in stars:
            x, y = int(self.width * x_ratio), int(self.height * y_ratio)
            canvas.create_oval(x, y, x + size, y + size, fill="#65769a", outline="", tags="backdrop")

    def _create_credits(self):
        entries = [
            ("SWORD PHANTASIA", "title", 100),
            ("THE PRIMORDIAL KING HAS FALLEN", "subtitle", 62),
            ("", "body", 75),
            ("DEVELOPER & CREATOR", "heading", 48),
            ("JAMES OLAYRES", "name", 95),
            ("", "body", 70),
            ("GAME DESIGN & DIRECTION", "heading", 46),
            ("James Olayres", "body", 72),
            ("", "body", 55),
            ("WORLD, COMBAT & PROGRESSION", "heading", 46),
            ("Sword Phantasia Development", "body", 72),
            ("", "body", 55),
            ("HEROES OF THE REALM", "heading", 46),
            ("Vanguard  •  Ranger  •  Berserker", "body", 72),
            ("", "body", 55),
            ("SPECIAL THANKS", "heading", 46),
            ("To every adventurer who entered this realm", "body", 72),
            ("", "body", 80),
            (f"{self.player.name.upper()}", "player", 54),
            ("THE HERO WHO ENDED THE PRIMORDIAL NIGHT", "subtitle", 105),
            ("", "body", 85),
            ("THANK YOU FOR PLAYING", "final", 150),
        ]
        styles = {
            "title": (("Georgia", 36, "bold"), self.GOLD),
            "subtitle": (("Arial", 10, "bold"), self.PURPLE),
            "heading": (("Arial", 9, "bold"), self.MUTED),
            "name": (("Georgia", 30, "bold"), self.GOLD),
            "body": (("Arial", 13), self.TEXT),
            "player": (("Georgia", 22, "bold"), "#6fc5ff"),
            "final": (("Georgia", 25, "bold"), self.GOLD),
        }
        y = self.height + 90
        for text, style, spacing in entries:
            font, color = styles[style]
            self.canvas.create_text(self.width // 2, y, text=text, font=font, fill=color, justify=tk.CENTER, tags="credits")
            y += spacing

    def _scroll_credits(self):
        if self._finished or not self.winfo_exists():
            return
        self.canvas.move("credits", 0, -2)
        bounds = self.canvas.bbox("credits")
        if not bounds or bounds[3] < 80:
            self._show_finale()
            return
        self._scroll_job = self.after(28, self._scroll_credits)

    def _show_finale(self):
        if self._finished:
            return
        self._finished = True
        if self._scroll_job:
            try:
                self.after_cancel(self._scroll_job)
            except tk.TclError:
                pass
        self.canvas.delete("credits")
        self.skip_btn.place_forget()
        self.canvas.create_text(self.width // 2, int(self.height * .28), text="SWORD PHANTASIA", font=("Georgia", 38, "bold"), fill=self.GOLD)
        self.canvas.create_text(self.width // 2, int(self.height * .39), text="A GAME BY", font=("Arial", 10, "bold"), fill=self.MUTED)
        self.canvas.create_text(self.width // 2, int(self.height * .47), text="JAMES OLAYRES", font=("Georgia", 29, "bold"), fill=self.TEXT)
        self.canvas.create_text(self.width // 2, int(self.height * .58), text="Thank you for playing.", font=("Arial", 13), fill="#aab5ca")

        actions = tk.Frame(self, bg=self.BG)
        actions.place(relx=.5, rely=.74, anchor="center")
        self._button(actions, "RETURN TO TITLE", lambda: self._choose("title"), "#b1832e", "#d6a943").pack(side=tk.LEFT, padx=7)
        self._button(actions, "QUIT GAME", lambda: self._choose("quit"), "#3a2430", "#663542").pack(side=tk.LEFT, padx=7)

    def _button(self, parent, text, command, color, hover):
        button = tk.Button(parent, text=text, command=command, bg=color, fg="#ffffff", activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 10, "bold"), cursor="hand2", padx=24, pady=12)
        button.bind("<Enter>", lambda event: event.widget.config(bg=hover))
        button.bind("<Leave>", lambda event: event.widget.config(bg=color))
        return button

    def _choose(self, result):
        self.result = result
        self._finished = True
        if self._scroll_job:
            try:
                self.after_cancel(self._scroll_job)
            except tk.TclError:
                pass
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
