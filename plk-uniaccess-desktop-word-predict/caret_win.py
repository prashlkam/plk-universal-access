# Windows caret fetching using GetGUIThreadInfo via ctypes.
import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('hwndActive', wintypes.HWND),
        ('hwndFocus', wintypes.HWND),
        ('hwndCapture', wintypes.HWND),
        ('hwndMenuOwner', wintypes.HWND),
        ('hwndMoveSize', wintypes.HWND),
        ('hwndCaret', wintypes.HWND),
        ('rcCaret', wintypes.RECT),
    ]

def get_caret_position():
    try:
        hwnd = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(hwnd, None)
        info = GUITHREADINFO()
        info.cbSize = ctypes.sizeof(GUITHREADINFO)
        res = user32.GetGUIThreadInfo(thread_id, ctypes.byref(info))
        if not res:
            return None
        # rcCaret is in client coordinates for hwndCaret; convert to screen
        rect = info.rcCaret
        pt = wintypes.POINT(rect.left, rect.bottom)
        if info.hwndCaret:
            user32.ClientToScreen(info.hwndCaret, ctypes.byref(pt))
        else:
            user32.ClientToScreen(hwnd, ctypes.byref(pt))
        return (pt.x, pt.y)
    except Exception as e:
        # fallback
        return None
