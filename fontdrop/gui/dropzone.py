"""Dropzone: een zachte, onregelmatige vorm (blob) met een dunne inktrand."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .style import HEADLINE_FONT_STACK, INK, INK_MUTED, SAGE, SAGE_TINT

ACCEPTED_SUFFIX = ".zip"


class DropZone(QFrame):
    """Accepteert gesleepte zips en mappen; emit paths bij drop of klik."""

    filesDropped = Signal(list)
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(300, 300)
        self._active = False

        self._label = QLabel("Drop zips of mappen")
        self._label.setAlignment(Qt.AlignCenter)
        self._sub = QLabel("of klik om te bladeren")

        layout = QVBoxLayout(self)
        layout.setAlignment(self._label.alignment())
        layout.setSpacing(6)
        layout.addStretch(1)
        layout.addWidget(self._label)
        layout.addWidget(self._sub)
        layout.addStretch(1)

        self._sub.setAlignment(self._label.alignment())
        self._apply_style()

    def _apply_style(self) -> None:
        border = SAGE if self._active else INK
        bg = SAGE_TINT if self._active else "transparent"
        self.setStyleSheet(
            f"""
            DropZone {{
                background-color: {bg};
                border: 1.5px solid {border};
                border-top-left-radius: 60px;
                border-top-right-radius: 90px;
                border-bottom-right-radius: 70px;
                border-bottom-left-radius: 100px;
            }}
            """
        )
        self._label.setStyleSheet(
            f"color: {INK}; font-family: {HEADLINE_FONT_STACK}; font-style: italic; "
            "font-size: 20px; font-weight: 600; border: none; background: transparent;"
        )
        self._sub.setStyleSheet(
            f"color: {INK_MUTED}; font-size: 12px; border: none; background: transparent;"
        )

    def _set_active(self, active: bool) -> None:
        if active != self._active:
            self._active = active
            self._apply_style()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._set_active(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._set_active(False)
        event.accept()

    def dropEvent(self, event):
        self._set_active(False)
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        paths = [p for p in paths if p.exists()]
        if paths:
            self.filesDropped.emit(paths)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
