import time

import pyperclip
from Quartz import (
    CGEventCreateKeyboardEvent, CGEventPost, CGEventSetFlags,
    kCGHIDEventTap, kCGEventFlagMaskCommand,
)

_KEYCODE_C = 8


def _post_cmd_c():
    key_down = CGEventCreateKeyboardEvent(None, _KEYCODE_C, True)
    key_up = CGEventCreateKeyboardEvent(None, _KEYCODE_C, False)
    CGEventSetFlags(key_down, kCGEventFlagMaskCommand)
    CGEventSetFlags(key_up, kCGEventFlagMaskCommand)
    CGEventPost(kCGHIDEventTap, key_down)
    CGEventPost(kCGHIDEventTap, key_up)


def get_selected_text(settle_delay: float = 0.3) -> str:
    pyperclip.copy("")
    time.sleep(0.05)
    _post_cmd_c()
    time.sleep(settle_delay)
    return pyperclip.paste()