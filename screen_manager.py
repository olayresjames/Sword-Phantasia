"""Central lifecycle registry for seamless fullscreen surfaces."""

import tkinter as tk
import weakref


class ScreenManager:
    def __init__(self):
        self._stack = []

    def register(self, window):
        self._stack = [reference for reference in self._stack if reference() and reference().winfo_exists()]
        if not any(reference() is window for reference in self._stack):
            self._stack.append(weakref.ref(window))
            window.bind("<Destroy>", lambda event, target=window: self._released(target, event), add="+")
        try:
            window.lift()
            window.focus_force()
        except tk.TclError:
            pass
        return window

    def _released(self, window, event):
        if event.widget is not window:
            return
        self._stack = [reference for reference in self._stack if reference() not in (None, window)]
        if self._stack:
            previous = self._stack[-1]()
            if previous and previous.winfo_exists():
                try:
                    previous.lift()
                    previous.focus_force()
                except tk.TclError:
                    pass


screen_manager = ScreenManager()
