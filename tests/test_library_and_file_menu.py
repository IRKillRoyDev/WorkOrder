"""Library groups publications by platform. File holds the usual commands."""

import os
from datetime import date

import pytest

pytest.importorskip("PySide6")
import PySide6.QtCore  # noqa: F401

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QLabel, QPushButton

from workorder.state import AppState
from workorder.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_publications_open_from_the_platform(qapp):
    state = AppState()
    state.record_publication("Abrams", "Troubleshooting manual", "engine-tm.pdf", date(2026, 10, 2))
    state.record_publication("Abrams", "Parts manual", "engine-parts.pdf", date(2026, 10, 31))
    state.record_publication("Bradley", "Troubleshooting manual", "hull-tm.pdf", date(2026, 9, 1))
    state.record_inventory("DSI", "dsi.csv", date(2026, 10, 15))
    window = MainWindow(state)
    window.show_named("Library")
    qapp.processEvents()
    buttons = [button.text() for button in window.library.findChildren(QPushButton, "platformButton")]
    assert any(text.startswith("Abrams") and "Latest 31 Oct 2026" in text for text in buttons)
    assert any(text.startswith("Bradley") for text in buttons)
    window.library.show_platform("Abrams")
    qapp.processEvents()
    names = [label.text() for label in window.library.findChildren(QLabel, "publicationName")]
    dates = [label.text() for label in window.library.findChildren(QLabel, "publicationDate")]
    assert "engine-parts.pdf" in names
    assert "31 Oct 2026" in dates
    assert "hull-tm.pdf" not in names
    assert "dsi.csv" in names
    assert window.library.platform_title.text() == "Abrams"
    window.deleteLater()
    qapp.processEvents()


def test_file_menu_has_the_usual_commands(qapp):
    window = MainWindow()
    menu = window.menuBar().actions()[0].menu()
    titles = [action.text().replace("&", "") for action in menu.actions() if not action.isSeparator()]
    assert titles == ["New", "Open...", "Save", "Save As...", "Import", "Export", "Close"]
    import_menu = next(action.menu() for action in menu.actions() if action.text() == "Import")
    names = [action.text() for action in import_menu.actions() if not action.isSeparator()]
    assert names == [
        "Troubleshooting Manual...",
        "Parts Manual...",
        "DSI...",
        "SMU...",
        "RIP...",
    ]
    export_menu = next(action.menu() for action in menu.actions() if action.text() == "Export")
    assert [action.text() for action in export_menu.actions()] == ["Defect List PDF..."]
    window.deleteLater()
    qapp.processEvents()


def test_new_opens_a_work_order_window(qapp):
    window = MainWindow()
    nav = [button.text() for button in window.findChildren(QPushButton, "nav")]
    assert nav == ["Status", "Library", "Preferences"]
    window._new_work_order()
    qapp.processEvents()
    order = window.state.work_orders[0]
    assert order.status == "Open"
    sheet = window._sheets[order.number]
    assert [sheet.tabs.tabText(index) for index in range(sheet.tabs.count())] == [
        "Main Work Order",
        "Defects",
    ]
    combo = window.status_page.findChildren(QComboBox, "lifecycle")[0]
    combo.setCurrentText("Archive")
    qapp.processEvents()
    assert order.status == "Archive"
    titles = [label.text() for label in window.status_page.findChildren(QLabel, "sectionTitle")]
    assert titles == ["Open", "Maint", "Close", "Archive"]
    frames = {
        frame.findChildren(QLabel, "sectionTitle")[0].text(): frame
        for frame in window.status_page.findChildren(QFrame, "section")
    }
    assert [button.text() for button in frames["Archive"].findChildren(QPushButton, "platformButton")] == [
        order.label()
    ]
    assert frames["Open"].findChildren(QPushButton, "platformButton") == []
    assert frames["Maint"].findChildren(QPushButton, "platformButton") == []
    assert frames["Close"].findChildren(QPushButton, "platformButton") == []
    sheet.deleteLater()
    window.deleteLater()
    qapp.processEvents()


def test_new_work_order_starts_open_and_keeps_the_library():
    state = AppState()
    state.record_publication("Abrams", "Parts manual", "parts.pdf", date(2026, 10, 31))
    order = state.new_work_order()
    order.add_other_defect("leaking hose")
    assert order.status == "Open"
    assert state.work_orders == [order]
    assert state.platforms() == ["Abrams"]
