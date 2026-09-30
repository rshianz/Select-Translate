import AppKit

from translator.ui.delegates import WindowCloseDelegate

WINDOW_MODULE_VERSION = 6 

OPEN_WINDOWS = []
_DELEGATES = []


_NONACTIVATING = getattr(
    AppKit, "NSWindowStyleMaskNonactivatingPanel",
    getattr(AppKit, "NSNonactivatingPanelMask", 1 << 7))


def _screen_under_mouse():
    pos = AppKit.NSEvent.mouseLocation()
    for screen in AppKit.NSScreen.screens():
        f = screen.frame()
        if (f.origin.x <= pos.x < f.origin.x + f.size.width
                and f.origin.y <= pos.y < f.origin.y + f.size.height):
            return screen
    return AppKit.NSScreen.mainScreen()


def set_font_size_for_all(size: float) -> None:
    """Live-update every open window (called by the slider)."""
    for win in OPEN_WINDOWS:
        if not (win.contentView() and win.contentView().subviews()):
            continue
        vibrancy = win.contentView().subviews()[0]
        if vibrancy.subviews() and isinstance(vibrancy.subviews()[0], AppKit.NSScrollView):
            text_view = vibrancy.subviews()[0].documentView()
            if isinstance(text_view, AppKit.NSTextView):
                text_view.setFont_(AppKit.NSFont.systemFontOfSize_(size))


def show(message: str, title: str, rtl: bool = True, font_size: float = 16.0) -> None:
    try:
        frontmost = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        frontmost_name = frontmost.localizedName() if frontmost else "?"
    except Exception:
        frontmost_name = "?"
    print(f"[floating v{WINDOW_MODULE_VERSION}] app_active="
          f"{AppKit.NSApp.isActive()}  frontmost={frontmost_name}")
    # ----------------------------------------------------------------------

    screen = _screen_under_mouse()
    screen_width = screen.frame().size.width
    screen_height = screen.frame().size.height

    base_font = AppKit.NSFont.systemFontOfSize_(font_size)
    full_message = f"{title}\n\n{message}"

    text_storage = AppKit.NSTextStorage.alloc().initWithString_(full_message)
    text_storage.setFont_(base_font)
    layout_manager = AppKit.NSLayoutManager.alloc().init()
    text_storage.addLayoutManager_(layout_manager)

    text_container = AppKit.NSTextContainer.alloc().initWithContainerSize_((420, 10000))
    text_container.setLineFragmentPadding_(0)
    layout_manager.addTextContainer_(text_container)
    layout_manager.glyphRangeForTextContainer_(text_container)

    text_height = layout_manager.usedRectForTextContainer_(text_container).size.height

    w = 450
    required_h = text_height + 40 + 30
    max_h = screen_height * 0.75
    final_h = max(min(required_h, max_h), 120)

    cascade = 36 * len(OPEN_WINDOWS)
    x = screen_width - w - 20
    y = max(20, screen_height - final_h - 60 - cascade)

    frame = AppKit.NSMakeRect(x, y, w, final_h)
    style_mask = (AppKit.NSWindowStyleMaskTitled |
                  AppKit.NSWindowStyleMaskClosable |
                  AppKit.NSWindowStyleMaskResizable |
                  AppKit.NSWindowStyleMaskFullSizeContentView |
                  _NONACTIVATING)                   

    win = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
        frame, style_mask, AppKit.NSBackingStoreBuffered, False
    )

    win.setBecomesKeyOnlyIfNeeded_(True)
    win.setHidesOnDeactivate_(False)
    win.setLevel_(AppKit.NSFloatingWindowLevel)
    win.setCollectionBehavior_(
        AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
        | AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary
        | AppKit.NSWindowCollectionBehaviorIgnoresCycle)

    win.setTitlebarAppearsTransparent_(True)
    win.setTitleVisibility_(AppKit.NSWindowTitleHidden)
    win.setMovableByWindowBackground_(True)
    win.setOpaque_(False)
    win.setBackgroundColor_(AppKit.NSColor.clearColor())
    win.setMinSize_(AppKit.NSSize(300, 120))
    win.setReleasedWhenClosed_(False)

    delegate = WindowCloseDelegate.alloc().initWithWindows_(OPEN_WINDOWS)
    win.setDelegate_(delegate)
    _DELEGATES.append(delegate)

    # Vibrancy background
    vibrancy = AppKit.NSVisualEffectView.alloc().initWithFrame_(
        AppKit.NSMakeRect(0, 0, w, final_h))
    vibrancy.setBlendingMode_(AppKit.NSVisualEffectBlendingModeBehindWindow)
    vibrancy.setMaterial_(AppKit.NSVisualEffectMaterialPopover)
    vibrancy.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)

    # Scroll View
    scroll_view = AppKit.NSScrollView.alloc().initWithFrame_(
        AppKit.NSMakeRect(0, 0, w, final_h))
    scroll_view.setHasVerticalScroller_(True)
    scroll_view.setAutohidesScrollers_(True)
    scroll_view.setDrawsBackground_(False)
    scroll_view.setBorderType_(AppKit.NSNoBorder)
    scroll_view.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)

    content_size = scroll_view.contentSize()

    # Text View
    text_view = AppKit.NSTextView.alloc().initWithFrame_(
        AppKit.NSMakeRect(0, 0, content_size.width, content_size.height))

    text_view.setString_(full_message)
    text_view.setEditable_(False)
    text_view.setSelectable_(True)
    text_view.setDrawsBackground_(False)
    text_view.setTextColor_(AppKit.NSColor.labelColor())
    text_view.setFont_(base_font)
    text_view.setAlignment_(
        AppKit.NSRightTextAlignment if rtl else AppKit.NSLeftTextAlignment)
    text_view.setBaseWritingDirection_(
        AppKit.NSWritingDirectionRightToLeft if rtl
        else AppKit.NSWritingDirectionLeftToRight)

    text_view.setMinSize_(AppKit.NSSize(0.0, content_size.height))
    text_view.setMaxSize_(AppKit.NSSize(10000.0, 10000.0))
    text_view.setVerticallyResizable_(True)
    text_view.setHorizontallyResizable_(False)
    text_view.setAutoresizingMask_(AppKit.NSViewWidthSizable)

    text_view.textContainer().setWidthTracksTextView_(True)
    text_view.textContainer().setContainerSize_(AppKit.NSSize(content_size.width, 10000.0))
    text_view.setTextContainerInset_((20, 20))

    scroll_view.setDocumentView_(text_view)
    vibrancy.addSubview_(scroll_view)
    win.contentView().addSubview_(vibrancy)

    # front
    # focus from the app you're reading in.
    win.orderFrontRegardless()
    OPEN_WINDOWS.append(win)