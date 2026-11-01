"""Defect list PDF. The mechanic section exists only in this file."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPageSize, QPainter, QPdfWriter, QPen

_CUI = QColor("#5B2C6F")
_CUI_TEXT = QColor("#FFFFFF")

from workorder.state import WorkOrder, split_columns

MECHANIC_LINE_COUNT = 16
_MARGIN = 40
_LINE = 18


def write_defect_list_pdf(path: str, state: WorkOrder) -> None:
    writer = QPdfWriter(path)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    writer.setResolution(72)
    writer.setTitle("Defect list")
    painter = QPainter(writer)
    if not painter.isActive():
        raise RuntimeError(f"Could not write {path}")
    try:
        _paint(painter, writer.width(), writer.height(), state)
    finally:
        painter.end()


def _paint(painter: QPainter, width: int, height: int, state: WorkOrder) -> None:
    y = _MARGIN
    painter.setPen(QPen(Qt.GlobalColor.black))
    title_font = QFont()
    title_font.setPointSize(14)
    title_font.setBold(True)
    body_font = QFont()
    body_font.setPointSize(11)
    small_font = QFont()
    small_font.setPointSize(9)
    small_font.setBold(True)

    painter.setFont(small_font)
    _cui_bar(painter, 0, width, 22)

    painter.setFont(title_font)
    painter.drawText(_MARGIN, y + 16, "Equipment")
    y += 24
    painter.drawRect(_MARGIN, y, width - 2 * _MARGIN, 64)
    y += 80

    y = _section_title(painter, title_font, y, "Quality Control")
    painter.setFont(body_font)
    lines = state.qc_lines()
    if not lines:
        painter.drawText(_MARGIN, y + 14, "No defects on this work order.")
        y += 28
    else:
        left, right = split_columns(lines)
        for row in range(max(len(left), len(right))):
            _qc_line(painter, 0, row, y, left, width)
            _qc_line(painter, 1, row, y, right, width)
            y += _LINE

    y += 12
    y = _section_title(painter, title_font, y, "Mechanic")
    painter.setFont(body_font)
    rows = (MECHANIC_LINE_COUNT + 1) // 2
    for row in range(rows):
        _blank_line(painter, 0, y, width)
        _blank_line(painter, 1, y, width)
        y += _LINE

    painter.setFont(small_font)
    _cui_bar(painter, height - 22, width, 22)


def _cui_bar(painter: QPainter, y: int, width: int, height: int) -> None:
    painter.fillRect(0, y, width, height, _CUI)
    painter.setPen(QPen(_CUI_TEXT))
    painter.drawText(QRectF(0, y, width, height), Qt.AlignmentFlag.AlignCenter, "CUI")
    painter.setPen(QPen(Qt.GlobalColor.black))


def _section_title(painter: QPainter, font: QFont, y: int, title: str) -> int:
    painter.setFont(font)
    painter.drawText(_MARGIN, y + 16, title)
    return y + 26


def _qc_line(painter: QPainter, column: int, row: int, y: int, items: list, width: int) -> None:
    if row >= len(items):
        return
    _kind, label = items[row]
    x = _column_x(column, width)
    box = 10
    top = y + 2
    painter.drawRect(x, top, box, box)
    painter.drawText(x + box + 6, y + 12, label)


def _blank_line(painter: QPainter, column: int, y: int, width: int) -> None:
    x = _column_x(column, width)
    span = _column_width(width) - 8
    painter.drawLine(x, y + 14, x + span, y + 14)


def _column_x(column: int, width: int) -> int:
    gap = 24
    usable = width - 2 * _MARGIN - gap
    if column == 0:
        return _MARGIN
    return _MARGIN + usable // 2 + gap


def _column_width(width: int) -> int:
    return (width - 2 * _MARGIN - 24) // 2
