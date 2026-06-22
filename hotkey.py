import sys
import threading
from typing import Callable

from config import cfg

# On macOS, use pynput to avoid root permission requirements of keyboard module.
USE_PYNPUT = (sys.platform == "darwin")

if USE_PYNPUT:
    try:
        from pynput import keyboard as pk
    except ImportError:
        pk = None
else:
    pk = None

try:
    import keyboard
except ImportError:
    keyboard = None


class GlobalHotkeyMonitor:
    """
    Registers a system-wide hotkey (default: ctrl+alt+space).
    Fires on_press when held, on_release when released.
    Runs in a daemon thread so it doesn't block the Qt event loop.
    """

    def __init__(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        hotkey: str | None = None,
    ):
        self._hotkey_str = hotkey or cfg.hotkey
        self._on_press = on_press
        self._on_release = on_release
        self._held = False

        if USE_PYNPUT and pk:
            parts = [p.strip().lower() for p in self._hotkey_str.split("+")]
            self._modifiers = set(parts[:-1])
            self._trigger_key = parts[-1]
            self._current_pressed = set()
            self._listener = None
        else:
            self._listener = None

    def _get_key_names(self, key) -> list[str]:
        names = []
        if hasattr(key, 'name') and key.name is not None:
            name = key.name.lower()
            names.append(name)
            if "ctrl" in name:
                names.append("ctrl")
            if "alt" in name or "option" in name:
                names.append("alt")
            if "shift" in name:
                names.append("shift")
            if "cmd" in name or "win" in name:
                names.append("win")
        elif hasattr(key, 'char') and key.char is not None:
            names.append(key.char.lower())
        return names

    def _on_key_press(self, key):
        names = self._get_key_names(key)
        for name in names:
            self._current_pressed.add(name)
        if self._trigger_key in names:
            if all(m in self._current_pressed for m in self._modifiers):
                if not self._held:
                    self._held = True
                    self._on_press()

    def _on_key_release(self, key):
        names = self._get_key_names(key)
        for name in names:
            self._current_pressed.discard(name)
        if self._held:
            still_held = (self._trigger_key in self._current_pressed and 
                          all(m in self._current_pressed for m in self._modifiers))
            if not still_held:
                self._held = False
                self._on_release()

    def start(self):
        if USE_PYNPUT and pk:
            self._listener = pk.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
            self._listener.start()
        elif keyboard:
            keyboard.on_press_key(self._hotkey_str.split("+")[-1], self._handle_press)
            keyboard.on_release_key(self._hotkey_str.split("+")[-1], self._handle_release)

    def _modifiers_held(self) -> bool:
        if not keyboard:
            return False
        parts = [p.strip() for p in self._hotkey_str.lower().split("+")]
        mods = parts[:-1]
        mod_map = {
            "ctrl": keyboard.is_pressed("ctrl"),
            "alt": keyboard.is_pressed("alt"),
            "shift": keyboard.is_pressed("shift"),
            "win": keyboard.is_pressed("windows"),
        }
        return all(mod_map.get(m, False) for m in mods)

    def _handle_press(self, event):
        if not self._held and self._modifiers_held():
            self._held = True
            self._on_press()

    def _handle_release(self, event):
        if self._held:
            self._held = False
            self._on_release()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        elif keyboard:
            keyboard.unhook_all()


class StopHotkey:
    """A global key that cancels the current generation (default: Esc).

    Only fires while Clicky is actively talking/thinking — the callback itself
    should no-op when Clicky is idle, so this can be left always-on without
    stealing Esc from other apps' UX.
    """

    def __init__(self, on_stop: Callable[[], None], key: str = "esc"):
        self._on_stop = on_stop
        self._key = key.lower()
        self._listener = None

    def _on_key_press(self, key):
        name = ""
        if hasattr(key, 'name') and key.name is not None:
            name = key.name.lower()
        elif hasattr(key, 'char') and key.char is not None:
            name = key.char.lower()
        if name == self._key:
            self._on_stop()

    def start(self):
        if USE_PYNPUT and pk:
            self._listener = pk.Listener(on_press=self._on_key_press)
            self._listener.start()
        elif keyboard:
            keyboard.add_hotkey(self._key, self._on_stop, suppress=False)

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
