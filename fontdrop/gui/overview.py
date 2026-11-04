"""Overzichtsscherm: per family een kop, per stijl een rij met voorbeeld in het font zelf."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..dedupe import Family
from .style import HEADLINE_FONT_STACK, INK_MUTED, SAGE


def _rule() -> QFrame:
    rule = QFrame()
    rule.setObjectName("rule")
    rule.setFrameShape(QFrame.NoFrame)
    return rule


class _StyleRow(QWidget):
    def __init__(self, choice, parent=None):
        super().__init__(parent)
        self.choice = choice

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(not choice.already_installed)
        layout.addWidget(self.checkbox)

        preview_font = self._load_preview_font(choice)
        label = QLabel(f"{choice.chosen.family} {choice.style}")
        label.setFont(preview_font)
        label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(label, stretch=1)

        if choice.already_installed:
            status, color = "installed", INK_MUTED
        else:
            status, color = "new", SAGE
        meta = QLabel(f"{choice.chosen.fmt.lower()} · {status}")
        meta.setStyleSheet(f"border: none; background: transparent; font-size: 11px; color: {color};")
        meta.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(meta)

    def _load_preview_font(self, choice) -> QFont:
        try:
            font_id = QFontDatabase.addApplicationFont(str(choice.chosen.path))
            families = QFontDatabase.applicationFontFamilies(font_id) if font_id != -1 else []
            if families:
                font = QFont(families[0])
                font.setPointSize(18)
                return font
        except Exception:
            pass
        font = QFont()
        font.setPointSize(18)
        return font

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()


class OverviewWidget(QWidget):
    installRequested = Signal(list)  # list[FontFace]
    backRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[_StyleRow] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(16)

        kicker = QLabel("FontDrop")
        kicker.setObjectName("kicker")
        headline = QLabel("Wat is er gevonden")
        headline.setObjectName("headline")
        root.addWidget(kicker)
        root.addWidget(headline)
        root.addWidget(_rule())

        self._failures_label = QLabel("")
        self._failures_label.setWordWrap(True)
        self._failures_label.setStyleSheet("color: #555555; font-size: 12px; border: none;")
        self._failures_label.hide()
        root.addWidget(self._failures_label)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._list_container)
        root.addWidget(scroll, stretch=1)

        root.addWidget(_rule())

        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet("border: none; font-size: 13px;")
        root.addWidget(self._summary_label)

        buttons = QHBoxLayout()
        self._back_btn = QPushButton("Opnieuw")
        self._back_btn.clicked.connect(self.backRequested.emit)
        self._install_btn = QPushButton("Installeer")
        self._install_btn.setObjectName("primary")
        self._install_btn.clicked.connect(self._emit_install)
        buttons.addWidget(self._back_btn)
        buttons.addStretch(1)
        buttons.addWidget(self._install_btn)
        root.addLayout(buttons)

    def set_families(self, families: list[Family], failures: list[tuple[str, str]]) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._rows = []

        if failures:
            lines = "\n".join(f"{src}: {reason}" for src, reason in failures)
            self._failures_label.setText(f"Niet te lezen:\n{lines}")
            self._failures_label.show()
        else:
            self._failures_label.hide()

        for family in families:
            heading = QLabel(family.name)
            heading.setStyleSheet(
                f"font-family: {HEADLINE_FONT_STACK}; font-size: 20px; font-weight: 600; "
                "border: none; margin-top: 12px;"
            )
            self._list_layout.insertWidget(self._list_layout.count() - 1, heading)
            for choice in family.styles:
                row = _StyleRow(choice)
                self._rows.append(row)
                self._list_layout.insertWidget(self._list_layout.count() - 1, row)
            self._list_layout.insertWidget(self._list_layout.count() - 1, _rule())

        self._update_summary()
        for row in self._rows:
            row.checkbox.stateChanged.connect(self._update_summary)

    def _update_summary(self) -> None:
        selected = sum(1 for r in self._rows if r.is_checked())
        already = sum(1 for r in self._rows if r.choice.already_installed)
        self._summary_label.setText(
            f"{selected} geselecteerd om te installeren  ·  {already} al aanwezig  ·  {len(self._rows)} totaal"
        )
        self._install_btn.setEnabled(selected > 0)

    def _emit_install(self) -> None:
        faces = [row.choice.chosen for row in self._rows if row.is_checked()]
        self.installRequested.emit(faces)

    def unchecked_already_installed_faces(self) -> list:
        """Fonts die al aanwezig waren en niet (opnieuw) zijn aangevinkt — voor de samenvatting."""
        return [row.choice.chosen for row in self._rows if not row.is_checked() and row.choice.already_installed]
