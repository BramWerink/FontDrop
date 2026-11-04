"""Start de FontDrop GUI: python -m fontdrop.app"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from .gui.style import QSS
from .gui.window import MainWindow


def _fonts_dir() -> Path:
    """Map met meegeleverde lettertypen, zowel bij `python -m fontdrop.app`
    als in een PyInstaller-build (waar bestanden in `_internal` terechtkomen)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "gui" / "fonts"


def _load_bundled_fonts() -> None:
    fonts_dir = _fonts_dir()
    if not fonts_dir.is_dir():
        return
    for font_file in fonts_dir.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))


def main() -> int:
    app = QApplication(sys.argv)
    _load_bundled_fonts()
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
