"""Preferences keeps the system name, and the window can switch light and dark."""

import os

import pytest

pytest.importorskip("PySide6")
import PySide6.QtCore  # noqa: F401

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QPushButton, QWidget

from workorder.state import AppState
from workorder.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_system_name_is_shown_in_full_with_an_action_checkbox(qapp):
    state = AppState()
    state.add_system("Transmission and transfer case")
    window = MainWindow(state)
    window.show_named("Preferences")
    names = [label.text() for label in window.findChildren(QLabel, "systemName")]
    assert names == ["Transmission and transfer case"]
    actions = [box.text() for box in window.findChildren(QCheckBox)]
    assert actions == ["Diagnose", "Repair", "Replace"]
    repair = next(box for box in window.findChildren(QCheckBox) if box.text() == "Repair")
    repair.setChecked(False)
    qapp.processEvents()
    assert state.systems["Transmission and transfer case"].repair_on is False
    window.deleteLater()
    qapp.processEvents()


def _appearance(window, label):
    return next(button for button in window.findChildren(QPushButton, "appearance") if button.text() == label)


def test_light_and_dark_are_in_preferences(qapp):
    window = MainWindow()
    sidebar = window.findChild(QWidget, "sidebar")
    assert sidebar.findChildren(QPushButton, "appearance") == []
    window.show_named("Preferences")
    _appearance(window, "Dark").click()
    qapp.processEvents()
    dark = qapp.palette().color(QPalette.ColorRole.Window)
    assert dark.lightness() < 80
    assert _appearance(window, "Dark").isChecked()
    _appearance(window, "Light").click()
    qapp.processEvents()
    light = qapp.palette().color(QPalette.ColorRole.Window)
    assert light.lightness() > 200
    assert _appearance(window, "Light").isChecked()
    window.show()
    qapp.processEvents()
    expected = QColor("#5B2C6F")
    for banner in window.findChildren(QLabel, "banner"):
        color = banner.grab().toImage().pixelColor(8, 8)
        assert abs(color.red() - expected.red()) < 12
        assert abs(color.blue() - expected.blue()) < 12
    window.deleteLater()
    qapp.processEvents()
