"""Work order screen. Major defects wait for a troubleshooting manual."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from workorder.state import ACTIONS, WorkOrder
from workorder.ui.widgets import Page, discard, section


class WorkOrderPage(Page):
    def __init__(self, order: WorkOrder) -> None:
        super().__init__()
        self._order = order
        self._app = order.app
        self._writing = False

        equipment, equipment_layout = section("Equipment")
        note = QLabel("Equipment details are not on this screen yet.")
        note.setObjectName("hint")
        equipment_layout.addWidget(note)
        self.column.addWidget(equipment)

        major, major_layout = section("Major defects")
        hint = QLabel(
            "Choose a system, then a defect from the troubleshooting manual. "
            "No manual is loaded in this stage, so the defect list is empty."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hint")
        major_layout.addWidget(hint)

        row = QHBoxLayout()
        self.system_combo = QComboBox()
        self.defect_combo = QComboBox()
        self.defect_combo.setEnabled(False)
        self.action_combo = QComboBox()
        self.action_combo.addItems(ACTIONS)
        self.system_combo.currentIndexChanged.connect(lambda _index: self._fill_actions())
        self.add_major = QPushButton("Add")
        self.add_major.setEnabled(False)
        row.addWidget(self.system_combo, 1)
        row.addWidget(self.defect_combo, 2)
        row.addWidget(self.action_combo)
        row.addWidget(self.add_major)
        major_layout.addLayout(row)
        self.major_rows = QVBoxLayout()
        major_layout.addLayout(self.major_rows)
        self.column.addWidget(major)

        other, other_layout = section("Other defects")
        other_row = QHBoxLayout()
        self.other_text = QLineEdit()
        self.other_text.setPlaceholderText("Defect that is not in the troubleshooting manual")
        self.add_other = QPushButton("Add")
        self.add_other.clicked.connect(self._add_other)
        self.other_text.returnPressed.connect(self._add_other)
        other_row.addWidget(self.other_text, 1)
        other_row.addWidget(self.add_other)
        other_layout.addLayout(other_row)
        other_hint = QLabel(
            "Checked defects are the defect list. Uncheck one to leave it off the list and out of the time."
        )
        other_hint.setWordWrap(True)
        other_hint.setObjectName("hint")
        other_layout.addWidget(other_hint)
        self.other_rows = QVBoxLayout()
        other_layout.addLayout(self.other_rows)
        self.column.addWidget(other)

        estimate, estimate_layout = section("Time to repair")
        self.estimate_label = QLabel()
        self.estimate_label.setWordWrap(True)
        estimate_layout.addWidget(self.estimate_label)
        self.column.addWidget(estimate)
        self.column.addStretch(1)

        self._app.subscribe(self.refresh)
        self.refresh()

    def _add_other(self) -> None:
        self._writing = True
        added = self._order.add_other_defect(self.other_text.text())
        self._writing = False
        if added:
            self.other_text.clear()
            self.refresh()

    def _remove_other(self, index: int) -> None:
        self._writing = True
        self._order.remove_other_defect(index)
        self._writing = False
        self.refresh()

    def _include_major(self, index: int, included: bool) -> None:
        if self._writing:
            return
        self._writing = True
        self._order.set_major_included(index, included)
        self._writing = False

    def _include_other(self, index: int, included: bool) -> None:
        if self._writing:
            return
        self._writing = True
        self._order.set_other_included(index, included)
        self._writing = False

    def refresh(self) -> None:
        if self._writing:
            return
        self._writing = True
        self._rebuild()
        self._writing = False

    def _rebuild(self) -> None:
        current_system = self.system_combo.currentText()
        self.system_combo.blockSignals(True)
        self.system_combo.clear()
        names = list(self._app.systems)
        if names:
            self.system_combo.addItems(names)
            if current_system in names:
                self.system_combo.setCurrentText(current_system)
        else:
            self.system_combo.addItem("Add a system in Preferences")
        self.system_combo.blockSignals(False)

        self.defect_combo.clear()
        self.defect_combo.addItem("No troubleshooting manual loaded")
        self._fill_actions()
        self._fill_major_rows()
        self._fill_other_rows()

        estimate = self._order.estimate()
        if not estimate.lines:
            text = "Add a major defect to see a time to repair."
        elif estimate.missing:
            names = ", ".join(estimate.missing)
            text = f"Enter an average in Preferences for: {names}."
        else:
            parts = [f"{line.label}: {line.days:g} days" for line in estimate.lines]
            text = "\n".join(parts) + f"\n\nTotal: {estimate.total_days:g} days"
        if estimate.turned_off:
            text += "\n\nTurned off in Preferences: " + ", ".join(estimate.turned_off) + "."
        if self._app.lead_time_days is not None:
            text += (
                f"\n\nLead time ({self._app.lead_time_days:g} days) is added once "
                "when a required part is not on hand. Parts are not loaded in this stage."
            )
        self.estimate_label.setText(text)

    def _fill_actions(self) -> None:
        current = self.action_combo.currentText()
        system = self.system_combo.currentText()
        averages = self._app.systems.get(system)
        self.action_combo.blockSignals(True)
        self.action_combo.clear()
        if averages is None:
            self.action_combo.addItem("Add a system in Preferences")
        else:
            enabled = [action for action in ACTIONS if averages.action_on(action)]
            if enabled:
                self.action_combo.addItems(enabled)
                if current in enabled:
                    self.action_combo.setCurrentText(current)
            else:
                self.action_combo.addItem("Turn an action on in Preferences")
        self.action_combo.blockSignals(False)

    def _fill_major_rows(self) -> None:
        self._clear_rows(self.major_rows)
        for index, defect in enumerate(self._order.major_defects):
            self.major_rows.addWidget(
                self._defect_row(
                    f"{defect.system} - {defect.title}",
                    defect.included,
                    lambda on, i=index: self._include_major(i, on),
                )
            )

    def _fill_other_rows(self) -> None:
        self._clear_rows(self.other_rows)
        for index, defect in enumerate(self._order.other_defects):
            self.other_rows.addWidget(
                self._defect_row(
                    f"Other - {defect.text}",
                    defect.included,
                    lambda on, i=index: self._include_other(i, on),
                    lambda _checked=False, i=index: self._remove_other(i),
                )
            )

    def _clear_rows(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                discard(widget)

    def _defect_row(self, label: str, included: bool, on_toggle, on_remove=None) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        box = QCheckBox(label)
        box.blockSignals(True)
        box.setChecked(included)
        box.blockSignals(False)
        box.toggled.connect(on_toggle)
        layout.addWidget(box, 1)
        if on_remove is not None:
            remove = QPushButton("Remove")
            remove.clicked.connect(on_remove)
            layout.addWidget(remove)
        return row
