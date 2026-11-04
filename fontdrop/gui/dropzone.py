"""Grote dropzone: dikke zwarte rand, bold tekst, inversie bij hover/drag."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .style import BLACK, HEADLINE_FONT_STACK, WHITE

ACCEPTED_SUFFIX = ".zip"


class DropZone(QFrame):
    """Accepteert gesleepte zips en mappen; emit paths bij drop of klik."""

    filesDropped = Signal(list)
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(280)
        self._active = False

        self._label = QLabel("SLEEP FONTS HIER")
        self._label.setAlignment(Qt.AlignCenter)
        self._sub = QLabel("zips en mappen, allemaal tegelijk")

        layout = QVBoxLayout(self)
        layout.setAlignment(self._label.alignment())
        layout.addStretch(1)
        layout.addWidget(self._label)
        layout.addWidget(self._sub)
        layout.addStretch(1)

        self._sub.setAlignment(self._label.alignment())
        self._apply_style()

    def _apply_style(self) -> None:
        bg, fg = (BLACK, WHITE) if self._active else (WHITE, BLACK)
        self.setStyleSheet(
            f"DropZone {{ background-color: {bg}; border: 4px solid {BLACK}; }}"
        )
        self._label.setStyleSheet(
            f"color: {fg}; font-family: {HEADLINE_FONT_STACK}; font-size: 32px; font-weight: 700; border: none; background: transparent;"
        )
        self._sub.setStyleSheet(
            f"color: {fg}; font-size: 13px; letter-spacing: 1px; border: none; background: transparent;"
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
