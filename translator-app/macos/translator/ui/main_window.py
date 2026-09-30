import AppKit
import objc

from translator.core.dictionary import format_entry

W, H = 480, 700
MARGIN = 20
INNER_W = W - 2 * MARGIN


def _label(frame, text, font, color=None):
    lbl = AppKit.NSTextField.alloc().initWithFrame_(frame)
    lbl.setStringValue_(text)
    lbl.setFont_(font)
    if color is not None:
        lbl.setTextColor_(color)
    lbl.setBezeled_(False)
    lbl.setDrawsBackground_(False)
    lbl.setEditable_(False)
    lbl.setSelectable_(False)
    return lbl


def _section_header(frame, title):
    font = AppKit.NSFont.systemFontOfSize_weight_(11, AppKit.NSFontWeightSemibold)
    return _label(frame, title.upper(), font, AppKit.NSColor.secondaryLabelColor())


def _text_view(frame, editable, rtl):
    tv = AppKit.NSTextView.alloc().initWithFrame_(frame)
    tv.setRichText_(False)
    tv.setEditable_(editable)
    tv.setSelectable_(True)
    tv.setDrawsBackground_(False)
    tv.setTextColor_(AppKit.NSColor.labelColor())
    tv.setFont_(AppKit.NSFont.systemFontOfSize_(13))
    tv.setVerticallyResizable_(True)
    tv.setHorizontallyResizable_(False)
    tv.setAutoresizingMask_(AppKit.NSViewWidthSizable)
    tv.setMinSize_(AppKit.NSSize(0.0, frame.size.height))
    tv.setMaxSize_(AppKit.NSSize(1e7, 1e7))
    tv.textContainer().setWidthTracksTextView_(True)
    tv.textContainer().setContainerSize_(AppKit.NSSize(1e7, 1e7))
    tv.setTextContainerInset_((8, 8))
    if rtl:
        tv.setAlignment_(AppKit.NSRightTextAlignment)
        tv.setBaseWritingDirection_(AppKit.NSWritingDirectionRightToLeft)
    else:
        tv.setAlignment_(AppKit.NSLeftTextAlignment)
        tv.setBaseWritingDirection_(AppKit.NSWritingDirectionLeftToRight)
    return tv


def _scrolled_text_view(frame, editable, rtl):
    scroll = AppKit.NSScrollView.alloc().initWithFrame_(frame)
    scroll.setHasVerticalScroller_(True)
    scroll.setAutohidesScrollers_(True)
    scroll.setBorderType_(AppKit.NSBezelBorder)
    scroll.setDrawsBackground_(False)
    scroll.setAutoresizingMask_(AppKit.NSViewWidthSizable)
    width = scroll.contentView().bounds().size.width
    tv = _text_view(AppKit.NSMakeRect(0, 0, width, frame.size.height), editable, rtl)
    scroll.setDocumentView_(tv)
    return scroll, tv


class MainWindowController(AppKit.NSObject):
    def initWithApp_(self, app):
        self = objc.super(MainWindowController, self).init()
        if self is None:
            return None
        self._app = app
        self._build_window()
        return self

    def _build_window(self):
        style = (AppKit.NSWindowStyleMaskTitled
                 | AppKit.NSWindowStyleMaskClosable
                 | AppKit.NSWindowStyleMaskMiniaturizable)
        self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(0, 0, W, H), style, AppKit.NSBackingStoreBuffered, False)
        self.window.setTitle_("Translator")
        self.window.setReleasedWhenClosed_(False)   # close = hide, don't destroy
        self.window.center()
        
        view = self.window.contentView()

        #header
        title_font = AppKit.NSFont.systemFontOfSize_weight_(20, AppKit.NSFontWeightBold)
        view.addSubview_(_label(AppKit.NSMakeRect(MARGIN, 642, 220, 28), "Translator", title_font))
        settings_btn = AppKit.NSButton.buttonWithTitle_target_action_(
            "⚙︎ Settings", self, "settingsClicked:")
        settings_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        settings_btn.setFrame_(AppKit.NSMakeRect(W - MARGIN - 120, 641, 120, 26))
        view.addSubview_(settings_btn)

        #translate section
        view.addSubview_(_section_header(AppKit.NSMakeRect(MARGIN, 606, 200, 14), "Translate"))
        input_scroll, self.input_view = _scrolled_text_view(
            AppKit.NSMakeRect(MARGIN, 446, INNER_W, 150), editable=True, rtl=False)
        view.addSubview_(input_scroll)

        translate_btn = AppKit.NSButton.buttonWithTitle_target_action_(
            "Translate", self, "translateClicked:")
        translate_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        translate_btn.setKeyEquivalent_("\r")
        translate_btn.setFrame_(AppKit.NSMakeRect(W - MARGIN - 120, 412, 120, 26))
        view.addSubview_(translate_btn)

        result_scroll, self.result_view = _scrolled_text_view(
            AppKit.NSMakeRect(MARGIN, 248, INNER_W, 150), editable=False, rtl=True)
        view.addSubview_(result_scroll)

        #dictionary section
        view.addSubview_(_section_header(AppKit.NSMakeRect(MARGIN, 228, 200, 14), "Dictionary"))
        self.word_field = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(MARGIN, 194, INNER_W - 130, 24))
        self.word_field.setPlaceholderString_("Type an English word…")
        self.word_field.setBezelStyle_(AppKit.NSTextFieldRoundedBezel)
        self.word_field.setTarget_(self)
        self.word_field.setAction_("lookupClicked:")
        view.addSubview_(self.word_field)

        lookup_btn = AppKit.NSButton.buttonWithTitle_target_action_(
            "Look Up", self, "lookupClicked:")
        lookup_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        lookup_btn.setFrame_(AppKit.NSMakeRect(W - MARGIN - 120, 193, 120, 26))
        view.addSubview_(lookup_btn)

        dict_scroll, self.dict_view = _scrolled_text_view(
            AppKit.NSMakeRect(MARGIN, 72, INNER_W, 110), editable=False, rtl=False)
        view.addSubview_(dict_scroll)

        #status footer 
        self.status_label = _label(AppKit.NSMakeRect(MARGIN, 44, INNER_W, 18), "",
                                   AppKit.NSFont.systemFontOfSize_(11))
        view.addSubview_(self.status_label)
        view.addSubview_(_label(
            AppKit.NSMakeRect(MARGIN, 24, INNER_W, 14),
            "⌃Space translate selection · ⌃D define word",
            AppKit.NSFont.systemFontOfSize_(10),
            AppKit.NSColor.tertiaryLabelColor()))

        self.refresh_status()

    # actions
    def settingsClicked_(self, sender):
        self._app.show_settings()

    def translateClicked_(self, sender):
        text = self.input_view.string().strip()
        if not text:
            return
        self.result_view.setString_("…")
        self._app.translate_async(text, self._show_translation)

    def _show_translation(self, result):
        self.result_view.setString_(result.translated if result else "Translation failed.")

    def lookupClicked_(self, sender):
        word = self.word_field.stringValue().strip()
        if not word:
            return
        self.dict_view.setString_("…")
        self._app.define_async(word, self._show_entry)

    def _show_entry(self, entry):
        if entry:
            self.dict_view.setString_(format_entry(entry))
        else:
            self.dict_view.setString_("No definition found.")

    # status
    def refresh_status(self):
        text = AppKit.NSMutableAttributedString.alloc().init()
        font = AppKit.NSFont.systemFontOfSize_(11)
        for name, ok in self._app.provider_status():
            color = (AppKit.NSColor.systemGreenColor() if ok
                     else AppKit.NSColor.secondaryLabelColor())
            seg = AppKit.NSAttributedString.alloc().initWithString_attributes_(
                f"  {'●' if ok else '○'} {name}",
                {AppKit.NSFontAttributeName: font,
                 AppKit.NSForegroundColorAttributeName: color})
            text.appendAttributedString_(seg)
        self.status_label.setAttributedStringValue_(text)

    def show(self):
        self.window.makeKeyAndOrderFront_(None)
        AppKit.NSApp.activateIgnoringOtherApps_(True)