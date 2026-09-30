import AppKit
import objc


class WindowCloseDelegate(AppKit.NSObject):
    def initWithWindows_(self, windows):
        self = objc.super(WindowCloseDelegate, self).init()
        if self is None:
            return None
        self._windows = windows
        return self

    def windowWillClose_(self, notification):
        self.performSelector_withObject_afterDelay_(
            "removeWindow:", notification.object(), 0.0
        )

    def removeWindow_(self, win):
        if win in self._windows:
            self._windows.remove(win)