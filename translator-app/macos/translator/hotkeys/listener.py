import threading

from Quartz import (
    CGEventTapCreate, kCGSessionEventTap, kCGHeadInsertEventTap,
    kCGEventTapOptionDefault, CGEventMaskBit, kCGEventKeyDown,
    CGEventGetFlags, kCGEventFlagMaskControl, CGEventTapEnable,
    CFMachPortCreateRunLoopSource, CFRunLoopGetCurrent,
    CFRunLoopAddSource, kCFRunLoopCommonModes, CFRunLoopRun,
    CGEventGetIntegerValueField, kCGKeyboardEventKeycode,
    kCGEventTapDisabledByTimeout, kCGEventTapDisabledByUserInput,
)

KEY_SPACE = 49   # ⌃Space → translate
KEY_D = 2        # ⌃D     → define


class HotkeyHub:
    def __init__(self):
        self._events = {}
        self._tap = None

    def register(self, keycode: int) -> threading.Event:
        event = threading.Event()
        self._events[keycode] = event
        return event

    def start(self):
        threading.Thread(target=self._run, daemon=True, name="hotkey-listener").start()

    def _run(self):
        def callback(proxy, event_type, event, refcon):
            if event_type in (kCGEventTapDisabledByTimeout, kCGEventTapDisabledByUserInput):
                print("Event tap was disabled — re-enabling.")
                if self._tap is not None:
                    CGEventTapEnable(self._tap, True)
                return event
            try:
                if (event_type == kCGEventKeyDown
                        and CGEventGetFlags(event) & kCGEventFlagMaskControl):
                    keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                    flag = self._events.get(keycode)
                    if flag is not None:
                        flag.set()      # the ONLY work done on this thread
                        return None     # swallow the keystroke
            except Exception as exc:
                print(f"Hotkey callback error: {exc}")
            return event

        self._tap = CGEventTapCreate(
            kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionDefault,
            CGEventMaskBit(kCGEventKeyDown), callback, None,
        )
        if self._tap is None:
            print("Failed to create event tap — check Accessibility permissions.")
            return
        source = CFMachPortCreateRunLoopSource(None, self._tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
        CGEventTapEnable(self._tap, True)
        CFRunLoopRun()  # blocks this thread forever