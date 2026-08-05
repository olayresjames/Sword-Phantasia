"""Optional game-controller focus navigation with silent keyboard fallback."""

import tkinter as tk


class ControllerNavigator:
    def __init__(self, window):
        self.window = window
        self.joystick = None
        self._last_hat = (0, 0)
        self._last_buttons = set()
        try:
            import pygame
            self.pygame = pygame
            pygame.joystick.init()
            if pygame.joystick.get_count():
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
        except (ImportError, RuntimeError, OSError):
            self.pygame = None
        if self.joystick:
            self._poll()

    def _poll(self):
        if not self.window.winfo_exists() or not self.joystick:
            return
        try:
            self.pygame.event.pump()
            hat = self.joystick.get_hat(0) if self.joystick.get_numhats() else (0, 0)
            buttons = {index for index in range(self.joystick.get_numbuttons()) if self.joystick.get_button(index)}
            if hat != self._last_hat and hat != (0, 0):
                self._move_focus(reverse=hat[0] < 0 or hat[1] > 0)
            if 0 in buttons and 0 not in self._last_buttons:
                widget = self.window.focus_get()
                if widget and hasattr(widget, "invoke"):
                    widget.invoke()
            if 1 in buttons and 1 not in self._last_buttons:
                self.window.event_generate("<Escape>")
            self._last_hat, self._last_buttons = hat, buttons
        except (RuntimeError, self.pygame.error, tk.TclError):
            return
        self.window.after(90, self._poll)

    def _move_focus(self, reverse=False):
        widget = self.window.focus_get() or self.window
        target = widget.tk_focusPrev() if reverse else widget.tk_focusNext()
        if target:
            target.focus_set()


def enable_controller_navigation(window):
    if getattr(window, "_controller_navigator", None) is None:
        window._controller_navigator = ControllerNavigator(window)
    return window._controller_navigator
