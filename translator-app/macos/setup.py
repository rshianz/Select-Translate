from setuptools import setup

APP = ["main.py"]

OPTIONS = {
    "iconfile": "assets/Translator.icns",
    "packages": [
        "rumps",
        "requests",
        "deep_translator",
        "pynput",
        "pyperclip",
    ],
    "plist": {
        "CFBundleName": "Translator",
        "CFBundleDisplayName": "Translator",
        "CFBundleIdentifier": "com.arshianazari.translator",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        # Uncomment for a menu-bar-only app (no Dock icon). Since we now
        # have a main window, the default (Dock icon + menu bar) is better:
        # "LSUIElement": True,
    },
}

setup(
    app=APP,
    name="SelecTranslator",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)