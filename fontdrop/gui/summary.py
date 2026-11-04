"""Samenvattingsscherm: geïnstalleerd, overgeslagen, mislukt."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


def _rule() -> QFrame:
    rule = QFrame()
    rule.setObjectName("rule")
    rule.setFrameShape(QFrame.NoFrame)
    return rule


def _row(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("border: none; font-size: 14px; padding: 4px 0;")
    return label


class SummaryWidget(QWidget):
    doneRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(16)

        kicker = QLabel("FONTDROP")
        kicker.setObjectName("kicker")
        self._headline = QLabel("Klaar")
        self._headline.setObjectName("headline")
        root.addWidget(kicker)
        root.addWidget(self._headline)
        root.addWidget(_rule())

        self._totals = QLabel("")
        self._totals.setStyleSheet("border: none; font-size: 15px; font-weight: 600;")
        root.addWidget(self._totals)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 8, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._list_container)
        root.addWidget(scroll, stretch=1)

        root.addWidget(_rule())
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._done_btn = QPushButton("NOG EEN KEER")
        self._done_btn.clicked.connect(self.doneRequested.emit)
        buttons.addWidget(self._done_btn)
        root.addLayout(buttons)

    def set_results(self, installed: list, skipped: list, failed: list) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._totals.setText(
            f"{len(installed)} GEÏNSTALLEERD   ·   {len(skipped)} OVERGESLAGEN   ·   {len(failed)} MISLUKT"
        )

        for face in installed:
            self._list_layout.insertWidget(
                self._list_layout.count() - 1,
                _row(f"Geïnstalleerd — {face.family} {face.style} ({face.fmt})"),
            )
        for face in skipped:
            self._list_layout.insertWidget(
                self._list_layout.count() - 1,
                _row(f"Overgeslagen (al aanwezig) — {face.family} {face.style} ({face.fmt})"),
            )
        for face, reason in failed:
            self._list_layout.insertWidget(
                self._list_layout.count() - 1,
                _row(f"Mislukt — {face.family} {face.style} ({face.fmt}): {reason}"),
            )
