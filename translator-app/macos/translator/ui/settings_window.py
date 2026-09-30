"""Settings window: API keys, custom prompt, behaviour toggle."""

import AppKit
import objc

from translator import config

W, H = 540, 620
M = 20
IW = W - 2 * M


def _label(frame, text, font, color):
    lbl = AppKit.NSTextField.alloc().initWithFrame_(frame)
    lbl.setStringValue_(text)
    lbl.setFont_(font)
    lbl.setTextColor_(color)
    lbl.setBezeled_(False)
    lbl.setDrawsBackground_(False)
    lbl.setEditable_(False)
    lbl.setSelectable_(False)
    return lbl


class SettingsWindowController(AppKit.NSObject):

    def initWithApp_settings_(self, app, settings):
        self = objc.super(SettingsWindowController, self).init()
        if self is None:
            return None
        self._app = app
        self._settings = settings
        self._build_window()
        return self

    def _build_window(self):
        style = AppKit.NSWindowStyleMaskTitled | AppKit.NSWindowStyleMaskClosable
        self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(0, 0, W, H), style, AppKit.NSBackingStoreBuffered, False)
        self.window.setTitle_("Settings")
        self.window.setReleasedWhenClosed_(False)
        
        self.window.center()

        view = self.window.contentView()
        bold = AppKit.NSFont.systemFontOfSize_weight_(13, AppKit.NSFontWeightSemibold)
        small = AppKit.NSFont.systemFontOfSize_(10)
        mono = (AppKit.NSFont.fontWithName_size_("Menlo", 12)
                or AppKit.NSFont.systemFontOfSize_(12))

        # gemini 
        view.addSubview_(_label(AppKit.NSMakeRect(M, 566, 200, 16),
                                "Gemini API Key", bold, AppKit.NSColor.labelColor()))
        gemini_link = AppKit.NSButton.buttonWithTitle_target_action_(
            "Get Key ↗", self, "openGeminiKey:")
        gemini_link.setBezelStyle_(AppKit.NSBezelStyleRounded)
        gemini_link.setFrame_(AppKit.NSMakeRect(W - M - 130, 562, 130, 24))
        view.addSubview_(gemini_link)
        self.gemini_field = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(M, 530, IW, 24))
        self.gemini_field.setPlaceholderString_("AIza…")
        view.addSubview_(self.gemini_field)

        # groq 
        view.addSubview_(_label(AppKit.NSMakeRect(M, 490, 200, 16),
                                "Groq API Key", bold, AppKit.NSColor.labelColor()))
        groq_link = AppKit.NSButton.buttonWithTitle_target_action_(
            "Get Key ↗", self, "openGroqKey:")
        groq_link.setBezelStyle_(AppKit.NSBezelStyleRounded)
        groq_link.setFrame_(AppKit.NSMakeRect(W - M - 130, 486, 130, 24))
        view.addSubview_(groq_link)
        self.groq_field = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(M, 454, IW, 24))
        self.groq_field.setPlaceholderString_("gsk_…")
        view.addSubview_(self.groq_field)

        # prompt
        view.addSubview_(_label(AppKit.NSMakeRect(M, 410, 300, 16),
                                "Translation Prompt", bold, AppKit.NSColor.labelColor()))
        view.addSubview_(_label(
            AppKit.NSMakeRect(M, 394, IW, 13),
            "Sent to AI providers as the system prompt. Leave empty to use the default.",
            small, AppKit.NSColor.secondaryLabelColor()))

        prompt_scroll = AppKit.NSScrollView.alloc().initWithFrame_(
            AppKit.NSMakeRect(M, 260, IW, 128))
        prompt_scroll.setHasVerticalScroller_(True)
        prompt_scroll.setAutohidesScrollers_(True)
        prompt_scroll.setBorderType_(AppKit.NSBezelBorder)
        prompt_scroll.setDrawsBackground_(False)
        self.prompt_view = AppKit.NSTextView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, IW, 128))
        self.prompt_view.setRichText_(False)
        self.prompt_view.setFont_(mono)
        self.prompt_view.setVerticallyResizable_(True)
        self.prompt_view.setHorizontallyResizable_(False)
        self.prompt_view.setAutoresizingMask_(AppKit.NSViewWidthSizable)
        self.prompt_view.setMinSize_(AppKit.NSSize(0.0, 128))
        self.prompt_view.setMaxSize_(AppKit.NSSize(1e7, 1e7))
        self.prompt_view.textContainer().setWidthTracksTextView_(True)
        self.prompt_view.textContainer().setContainerSize_(AppKit.NSSize(1e7, 1e7))
        self.prompt_view.setTextContainerInset_((6, 6))
        prompt_scroll.setDocumentView_(self.prompt_view)
        view.addSubview_(prompt_scroll)

        reset_btn = AppKit.NSButton.buttonWithTitle_target_action_(
            "Reset to Default", self, "resetPromptClicked:")
        reset_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        reset_btn.setFrame_(AppKit.NSMakeRect(M, 228, 150, 24))
        view.addSubview_(reset_btn)

        # behaviour
        self.auto_check = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(M, 190, IW, 22))
        self.auto_check.setButtonType_(AppKit.NSSwitchButton)
        self.auto_check.setTitle_("Also show dictionary definitions for single English words (⌃Space)")
        self.auto_check.setFont_(AppKit.NSFont.systemFontOfSize_(12))
        view.addSubview_(self.auto_check)

        # save
        self.status = _label(AppKit.NSMakeRect(M, 146, 300, 20), "",
                             AppKit.NSFont.systemFontOfSize_(12),
                             AppKit.NSColor.systemGreenColor())
        view.addSubview_(self.status)
        save_btn = AppKit.NSButton.buttonWithTitle_target_action_("Save", self, "saveClicked:")
        save_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        save_btn.setKeyEquivalent_("\r")
        save_btn.setFrame_(AppKit.NSMakeRect(W - M - 120, 140, 120, 28))
        view.addSubview_(save_btn)

        # footer 
        view.addSubview_(_label(
            AppKit.NSMakeRect(M, 18, IW, 40),
            "Everything is stored locally in\n~/Library/Application Support/Translator/settings.json",
            small, AppKit.NSColor.tertiaryLabelColor()))

    # actions
    def saveClicked_(self, sender):
        self._settings.set("gemini_api_key", self.gemini_field.stringValue().strip())
        self._settings.set("groq_api_key", self.groq_field.stringValue().strip())
        self._settings.set("custom_prompt", self.prompt_view.string().strip())
        self._settings.set("auto_dictionary", bool(self.auto_check.state()))
        self._app.on_settings_changed()
        self.status.setStringValue_("✓ Saved")
        self.performSelector_withObject_afterDelay_("clearStatus:", None, 1.5)

    def clearStatus_(self, _):
        self.status.setStringValue_("")

    def resetPromptClicked_(self, sender):
        self.prompt_view.setString_(config.DEFAULT_PROMPT)

    def openGeminiKey_(self, sender):
        self._open_url("https://aistudio.google.com/apikey")

    def openGroqKey_(self, sender):
        self._open_url("https://console.groq.com/keys")

    @staticmethod
    def _open_url(url):
        AppKit.NSWorkspace.sharedWorkspace().openURL_(AppKit.NSURL.URLWithString_(url))

    # show
    def show(self):
        # reload current values every time, in case they changed elsewhere.
        self.gemini_field.setStringValue_(self._settings.get("gemini_api_key"))
        self.groq_field.setStringValue_(self._settings.get("groq_api_key"))
        self.prompt_view.setString_(self._settings.get("custom_prompt"))
        self.auto_check.setState_(
            AppKit.NSControlStateValueOn if self._settings.get("auto_dictionary")
            else AppKit.NSControlStateValueOff)
        self.status.setStringValue_("")
        self.window.makeKeyAndOrderFront_(None)
        AppKit.NSApp.activateIgnoringOtherApps_(True)