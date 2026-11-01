"""Shared pieces of the WorkOrder window."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def section(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("section")
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 16)
    layout.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


def two_columns(parent_layout: QVBoxLayout) -> tuple[QVBoxLayout, QVBoxLayout]:
    row = QHBoxLayout()
    row.setSpacing(24)
    left = QVBoxLayout()
    right = QVBoxLayout()
    left.setSpacing(6)
    right.setSpacing(6)
    row.addLayout(left, 1)
    divider = QFrame()
    divider.setObjectName("columnDivider")
    divider.setFrameShape(QFrame.Shape.VLine)
    row.addWidget(divider)
    row.addLayout(right, 1)
    parent_layout.addLayout(row)
    return left, right


def discard(widget: QWidget) -> None:
    """Remove a rebuilt row now. deleteLater alone stays visible until a full event loop."""
    widget.hide()
    widget.setParent(None)
    widget.deleteLater()


def marking_banner() -> QLabel:
    banner = QLabel("CUI")
    banner.setObjectName("banner")
    banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return banner


class Page(QWidget):
    """One full-width screen inside the main window."""

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.viewport().setObjectName("pageViewport")
        body = QWidget()
        body.setObjectName("pageBody")
        self.column = QVBoxLayout(body)
        self.column.setContentsMargins(24, 20, 24, 20)
        self.column.setSpacing(16)
        scroll.setWidget(body)
        outer.addWidget(scroll)
