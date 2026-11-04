"""Hoofdvenster: start (dropzone) -> overzicht -> samenvatting."""
from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .dropzone import DropZone
from .overview import OverviewWidget
from .summary import SummaryWidget
from .workers import InstallWorker, ScanWorker


def _rule() -> QFrame:
    rule = QFrame()
    rule.setObjectName("rule")
    rule.setFrameShape(QFrame.NoFrame)
    return rule


class _StartPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)

        kicker = QLabel("FontDrop")
        kicker.setObjectName("kicker")
        headline = QLabel("Installeer al je fonts in één keer.")
        headline.setObjectName("headline")
        headline.setWordWrap(True)
        root.addWidget(kicker)
        root.addWidget(headline)
        root.addWidget(_rule())

        self.dropzone = DropZone()
        dropzone_row = QHBoxLayout()
        dropzone_row.addStretch(1)
        dropzone_row.addWidget(self.dropzone)
        dropzone_row.addStretch(1)
        root.addStretch(1)
        root.addLayout(dropzone_row)
        root.addStretch(1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.pick_zips_btn = QPushButton("Kies zip(s)")
        self.pick_folder_btn = QPushButton("Kies map")
        buttons.addWidget(self.pick_zips_btn)
        buttons.addWidget(self.pick_folder_btn)
        buttons.addStretch(1)
        root.addLayout(buttons)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FontDrop")
        self.resize(760, 680)

        self._stack = QStackedWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)

        self._start_page = _StartPage()
        self._overview_page = OverviewWidget()
        self._summary_page = SummaryWidget()
        self._stack.addWidget(self._start_page)
        self._stack.addWidget(self._overview_page)
        self._stack.addWidget(self._summary_page)

        self._start_page.dropzone.filesDropped.connect(self._start_scan)
        self._start_page.pick_zips_btn.clicked.connect(self._pick_zips)
        self._start_page.pick_folder_btn.clicked.connect(self._pick_folder)
        self._overview_page.installRequested.connect(self._start_install)
        self._overview_page.backRequested.connect(self._reset)
        self._summary_page.doneRequested.connect(self._reset)

        self._scan_worker: ScanWorker | None = None
        self._install_worker: InstallWorker | None = None
        self._current_tempdir: str | None = None

    # -- invoer kiezen -----------------------------------------------------
    def _pick_zips(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Kies font-zips", "", "Zip-bestanden (*.zip)")
        if paths:
            self._start_scan([Path(p) for p in paths])

    def _pick_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Kies een map met fonts")
        if path:
            self._start_scan([Path(path)])

    # -- scannen -------------------------------------------------------------
    def _start_scan(self, paths: list[Path]) -> None:
        self._cleanup_tempdir()
        self._start_page.setEnabled(False)
        self._scan_worker = ScanWorker(paths, prefer="otf")
        self._scan_worker.finished_ok.connect(self._on_scan_done)
        self._scan_worker.failed.connect(self._on_scan_failed)
        self._scan_worker.start()

    def _on_scan_done(self, families, failures, tempdir) -> None:
        self._start_page.setEnabled(True)
        self._current_tempdir = tempdir
        if not families:
            QMessageBox.information(self, "FontDrop", "Geen bruikbare fonts gevonden.")
            self._cleanup_tempdir()
            return
        self._overview_page.set_families(families, failures)
        self._stack.setCurrentWidget(self._overview_page)

    def _on_scan_failed(self, message: str) -> None:
        self._start_page.setEnabled(True)
        QMessageBox.warning(self, "FontDrop", f"Scannen mislukt:\n{message}")

    # -- installeren ---------------------------------------------------------
    def _start_install(self, faces: list) -> None:
        self._overview_page.setEnabled(False)
        self._install_worker = InstallWorker(faces)
        self._install_worker.finished_ok.connect(self._on_install_done)
        self._install_worker.start()

    def _on_install_done(self, outcomes) -> None:
        self._overview_page.setEnabled(True)
        installed = [f for f, status, _ in outcomes if status == "installed"]
        failed = [(f, reason) for f, status, reason in outcomes if status == "failed"]
        skipped = self._overview_page.unchecked_already_installed_faces()
        self._summary_page.set_results(installed, skipped, failed)
        self._stack.setCurrentWidget(self._summary_page)
        self._cleanup_tempdir()

    # -- opruimen --------------------------------------------------------------
    def _reset(self) -> None:
        self._cleanup_tempdir()
        self._stack.setCurrentWidget(self._start_page)

    def _cleanup_tempdir(self) -> None:
        if self._current_tempdir:
            shutil.rmtree(self._current_tempdir, ignore_errors=True)
            self._current_tempdir = None

    def closeEvent(self, event) -> None:
        self._cleanup_tempdir()
        super().closeEvent(event)
