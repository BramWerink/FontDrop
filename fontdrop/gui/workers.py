"""Achtergrondthreads voor scannen en installeren, zodat de UI niet blokkeert."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ..dedupe import Family, build_families
from ..installer import install_faces, read_registered_fonts, registry_name
from ..scanner import FontFace, ScanResult, scan


class ScanWorker(QThread):
    finished_ok = Signal(list, list, str)  # families, failures, tempdir
    failed = Signal(str)

    def __init__(self, inputs: list[Path], prefer: str, parent=None):
        super().__init__(parent)
        self._inputs = inputs
        self._prefer = prefer

    def run(self) -> None:
        tmp = tempfile.mkdtemp(prefix="fontdrop-")
        try:
            result: ScanResult = scan(self._inputs, Path(tmp))
            families: list[Family] = build_families(result.faces, prefer=self._prefer)
            registered = read_registered_fonts()
            for family in families:
                for choice in family.styles:
                    choice.already_installed = registry_name(choice.chosen) in registered
            self.finished_ok.emit(families, result.failures, tmp)
        except Exception as exc:  # onverwachte fout tijdens scannen
            shutil.rmtree(tmp, ignore_errors=True)
            self.failed.emit(str(exc))


class InstallWorker(QThread):
    finished_ok = Signal(list)  # list[(FontFace, status, reason)]

    def __init__(self, faces: list[FontFace], parent=None):
        super().__init__(parent)
        self._faces = faces

    def run(self) -> None:
        outcomes = install_faces(self._faces)
        self.finished_ok.emit(outcomes)
