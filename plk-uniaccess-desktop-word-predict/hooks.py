# Global keyboard hook using pynput. Captures keys and maintains a simple text buffer per active window.
from pynput import keyboard
import threading, time

class KeyHook:
    def __init__(self, callback):
        self.callback = callback  # callback(text_buffer, key_event)
        self.buffer = ''
        self.lock = threading.Lock()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.last_time = time.time()

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def on_press(self, key):
        try:
            k = key.char
        except AttributeError:
            k = None
        with self.lock:
            if k and k.isprintable():
                self.buffer += k
            else:
                # handle special keys: space, backspace, enter, tab
                if key == keyboard.Key.space:
                    self.buffer += ' '
                elif key == keyboard.Key.backspace:
                    self.buffer = self.buffer[:-1]
                elif key in (keyboard.Key.enter, keyboard.Key.tab):
                    self.buffer += ' '
            # call callback in a separate thread to avoid blocking
            threading.Thread(target=self.callback, args=(self.buffer, key), daemon=True).start()

    def on_release(self, key):
        pass
