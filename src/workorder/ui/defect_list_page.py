"""On-screen defect list. It shows the defects turned on from the work order."""

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton

from workorder.reports.defect_list_pdf import write_defect_list_pdf
from workorder.state import WorkOrder, split_columns
from workorder.ui.widgets import Page, discard, section, two_columns


class DefectListPage(Page):
    def __init__(self, order: WorkOrder) -> None:
        super().__init__()
        self._order = order

        equipment, equipment_layout = section("Equipment")
        equipment.setMinimumHeight(88)
        equipment_layout.addStretch(1)
        self.column.addWidget(equipment)

        qc, qc_layout = section("Quality Control")
        self.qc_left, self.qc_right = two_columns(qc_layout)
        self._qc_empty = QLabel("No defects turned on from the work order.")
        self._qc_empty.setObjectName("hint")
        self._qc_empty.setWordWrap(True)
        qc_layout.addWidget(self._qc_empty)
        self.column.addWidget(qc)

        actions = QHBoxLayout()
        generate = QPushButton("Generate PDF")
        generate.clicked.connect(self._generate)
        actions.addWidget(generate)
        actions.addStretch(1)
        self.column.addLayout(actions)
        self.status = QLabel("This list is the defects checked on the Work order page.")
        self.status.setObjectName("hint")
        self.status.setWordWrap(True)
        self.column.addWidget(self.status)
        self.column.addStretch(1)

        order.app.subscribe(self.refresh)
        self.refresh()

    def _generate(self) -> None:
        path, _selected = QFileDialog.getSaveFileName(
            self,
            "Generate defect list",
            "defect-list.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        write_defect_list_pdf(path, self._order)
        self.status.setText(f"Saved {path}")

    def refresh(self) -> None:
        self._fill_qc()

    def _fill_qc(self) -> None:
        while self.qc_left.count():
            item = self.qc_left.takeAt(0)
            if item.widget() is not None:
                discard(item.widget())
        while self.qc_right.count():
            item = self.qc_right.takeAt(0)
            if item.widget() is not None:
                discard(item.widget())
        lines = self._order.qc_lines()
        self._qc_empty.setVisible(not lines)
        left, right = split_columns(lines)
        for _kind, label in left:
            self.qc_left.addWidget(self._line(label))
        for _kind, label in right:
            self.qc_right.addWidget(self._line(label))

    def _line(self, label: str) -> QLabel:
        line = QLabel(label)
        line.setWordWrap(True)
        return line

    def qc_column_counts(self) -> tuple[int, int]:
        return self.qc_left.count(), self.qc_right.count()
