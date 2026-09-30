"""
    Font-size slider that lives inside the menu-bar dropdown.
"""

import AppKit
import objc
import rumps


class FontSliderTarget(AppKit.NSObject):
    def initWithCallback_default_(self, callback, default_value):
        self = objc.super(FontSliderTarget, self).init()
        if self is None:
            return None
        self.callback = callback
        self.default_value = default_value
        self.snap_threshold = 1.2
        return self

    def sliderChanged_(self, sender):
        value = sender.doubleValue()

        if abs(value - self.default_value) <= self.snap_threshold:
            value = self.default_value
            sender.setDoubleValue_(value)

        if self.callback:
            self.callback(value)


def _static_label(frame, text, font_size, color=None, alignment=None):
    label = AppKit.NSTextField.alloc().initWithFrame_(frame)
    label.setStringValue_(text)
    label.setFont_(AppKit.NSFont.systemFontOfSize_(font_size))
    label.setTextColor_(color if color is not None
                        else AppKit.NSColor.secondaryLabelColor())
    if alignment is not None:
        label.setAlignment_(alignment)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setEditable_(False)
    label.setSelectable_(False)
    return label


def build_font_size_menu_item(current_font_size=16.0, on_change=None):
    min_val, max_val = 10.0, 40.0
    default_value = max(min_val, min(max_val, float(current_font_size)))

    font_item = rumps.MenuItem("Font Size")
    ns_item = font_item._menuitem

    width, height = 280, 65
    track_x, track_w = 24, 232

    view = AppKit.NSView.alloc().initWithFrame_(AppKit.NSMakeRect(0, 0, width, height))

    # min label 
    view.addSubview_(_static_label(
        AppKit.NSMakeRect(6, 30, 30, 14), "10", 10))

    # max label 
    view.addSubview_(_static_label(
        AppKit.NSMakeRect(width - 36, 30, 30, 14), "40", 10,
        alignment=AppKit.NSRightTextAlignment))

    # slider 
    slider = AppKit.NSSlider.alloc().initWithFrame_(
        AppKit.NSMakeRect(track_x, 26, track_w, 20))
    slider.setMinValue_(min_val)
    slider.setMaxValue_(max_val)
    slider.setDoubleValue_(default_value)
    slider.setControlSize_(AppKit.NSControlSizeSmall)

    slider.setContinuous_(False)
    view.addSubview_(slider)

    knob_width = 10.0
    travel_width = track_w - knob_width

    proportion = (default_value - min_val) / (max_val - min_val)
    knob_center_x = track_x + (knob_width / 2) + (proportion * travel_width)

    x_adjustment = 4.0
    knob_center_x += x_adjustment

    tick = AppKit.NSBox.alloc().initWithFrame_(
        AppKit.NSMakeRect(knob_center_x - 0.5, 22, 1, 6))
    tick.setBoxType_(AppKit.NSBoxCustom)
    tick.setBorderWidth_(0)
    tick.setFillColor_(AppKit.NSColor.tertiaryLabelColor())
    view.addSubview_(tick)

    label_w = 60
    label_x = knob_center_x - (label_w / 2)
    label_x = max(4, min(width - label_w - 4, label_x))

    view.addSubview_(_static_label(
        AppKit.NSMakeRect(label_x, 6, label_w, 14),
        f"Default · {int(default_value)}pt", 9,
        color=AppKit.NSColor.tertiaryLabelColor(),
        alignment=AppKit.NSCenterTextAlignment))

    target = FontSliderTarget.alloc().initWithCallback_default_(on_change, default_value)
    slider.setTarget_(target)
    slider.setAction_("sliderChanged:")

    font_item._font_slider_target = target  #keep target alive 

    ns_item.setView_(view)
    return font_item