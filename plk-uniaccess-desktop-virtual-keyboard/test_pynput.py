from pynput.keyboard import Controller
import time

keyboard = Controller()
time.sleep(2) # Give yourself 2 seconds to switch to another window
keyboard.type('hello')
print("Typed 'hello'")