"""Start de FontDrop GUI: python -m fontdrop.app"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .gui.style import QSS
from .gui.window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
