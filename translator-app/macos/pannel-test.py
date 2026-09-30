"""
TEST

Standalone panel test — no app, no hotkeys, no translation code.

    python3 panel_test.py

Within 6 seconds, switch to any other app (Preview, a browser — any Space,
even full-screen). A small panel must appear over it, WITHOUT macOS
switching Spaces. Ctrl+C in the terminal to quit.
"""
import AppKit

app = AppKit.NSApplication.sharedApplication()
# Deliberately NO activate() anywhere in this test.

NONACTIVATING = getattr(
    AppKit, "NSWindowStyleMaskNonactivatingPanel",
    getattr(AppKit, "NSNonactivatingPanelMask", 1 << 7))

style = (AppKit.NSWindowStyleMaskTitled
         | AppKit.NSWindowStyleMaskClosable
         | NONACTIVATING)

panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
    AppKit.NSMakeRect(300, 300, 360, 120),
    style, AppKit.NSBackingStoreBuffered, False)
panel.setTitle_("Panel test — I must appear over your PDF")
panel.setLevel_(AppKit.NSFloatingWindowLevel)
panel.setHidesOnDeactivate_(False)
panel.setCollectionBehavior_(
    AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
    | AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary)


class Firer(AppKit.NSObject):
    def fire_(self, timer):
        panel.orderFrontRegardless()
        print("→ panel ordered front NOW. Is it over your other app?")


firer = Firer.alloc().init()
AppKit.NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
    6.0, firer, "fire:", None, False)

print("You have 6 seconds — switch to another app or Space…")
app.run()