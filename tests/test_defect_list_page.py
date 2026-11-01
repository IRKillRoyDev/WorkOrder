"""The on-screen defect list has no mechanic section. The PDF does."""

import os

import pytest

pytest.importorskip("PySide6")
import PySide6.QtCore  # noqa: F401  sets the Qt plugin path before the app starts

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QCheckBox, QLabel

from workorder.reports.defect_list_pdf import write_defect_list_pdf
from workorder.state import AppState, OtherDefect, WorkOrder
from workorder.ui.defect_list_page import DefectListPage


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_screen_has_quality_control_and_not_the_mechanic_section(qapp):
    order = AppState().new_work_order()
    order.other_defects = [OtherDefect(f"defect {i}") for i in range(3)]
    page = DefectListPage(order)
    titles = [label.text() for label in page.findChildren(QLabel, "sectionTitle")]
    assert titles == ["Equipment", "Quality Control"]
    assert page.qc_column_counts() == (2, 1)
    assert page.findChildren(QCheckBox) == []
    qapp.processEvents()


def test_pdf_is_written(tmp_path, qapp):
    order = AppState().new_work_order()
    order.add_other_defect("leaking hose")
    path = tmp_path / "defect-list.pdf"
    write_defect_list_pdf(str(path), order)
    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000
