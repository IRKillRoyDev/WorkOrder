"""Each system is one row. The name takes the wide column. Each action can be turned off."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from workorder.state import ACTIONS, AppState
from workorder.ui.widgets import Page, discard, section


class PreferencesPage(Page):
    def __init__(self, state: AppState, on_theme) -> None:
        super().__init__()
        self._state = state
        self._writing = False
        self._syncing = False
        self._on_theme = on_theme

        appearance, appearance_layout = section("Appearance")
        row = QHBoxLayout()
        self._appearance = QButtonGroup(self)
        self._appearance.setExclusive(True)
        self._light = self._theme_button("Light", Qt.ColorScheme.Light)
        self._dark = self._theme_button("Dark", Qt.ColorScheme.Dark)
        row.addWidget(self._light)
        row.addWidget(self._dark)
        row.addStretch(1)
        appearance_layout.addLayout(row)
        self.column.addWidget(appearance)

        lead, lead_layout = section("Lead time")
        lead_row = QHBoxLayout()
        lead_row.addWidget(QLabel("Average days when a part is not on hand"))
        self.lead_time = QLineEdit()
        self.lead_time.setValidator(QDoubleValidator(0.0, 9999.0, 2))
        self.lead_time.setPlaceholderText("Not set")
        self.lead_time.setMaximumWidth(120)
        self.lead_time.editingFinished.connect(self._save_lead_time)
        lead_row.addWidget(self.lead_time)
        lead_row.addStretch(1)
        lead_layout.addLayout(lead_row)
        self.column.addWidget(lead)

        systems, systems_layout = section("Systems")
        note = QLabel(
            "The system name uses the wide column, so the whole name stays visible. "
            "Check Diagnose, Repair, or Replace to use that action on a work order. "
            "Leave the days blank until you have an average."
        )
        note.setWordWrap(True)
        note.setObjectName("hint")
        systems_layout.addWidget(note)
        self.rows = QVBoxLayout()
        self.rows.setSpacing(8)
        systems_layout.addLayout(self.rows)

        add_row = QHBoxLayout()
        self.system_name = QLineEdit()
        self.system_name.setPlaceholderText("System name")
        add = QPushButton("Add system")
        add.clicked.connect(self._add_system)
        self.system_name.returnPressed.connect(self._add_system)
        add_row.addWidget(self.system_name, 1)
        add_row.addWidget(add)
        systems_layout.addLayout(add_row)
        self.message = QLabel("")
        self.message.setObjectName("hint")
        self.message.setWordWrap(True)
        systems_layout.addWidget(self.message)
        self.column.addWidget(systems)
        self.column.addStretch(1)

        state.subscribe(self.refresh)
        self.refresh()

    def _theme_button(self, label: str, scheme: Qt.ColorScheme) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("appearance")
        button.setCheckable(True)
        button.clicked.connect(lambda _checked, chosen=scheme: self._pick_theme(chosen))
        self._appearance.addButton(button)
        return button

    def _pick_theme(self, scheme: Qt.ColorScheme) -> None:
        if self._syncing:
            return
        self._on_theme(scheme)

    def set_scheme(self, scheme: Qt.ColorScheme) -> None:
        self._syncing = True
        self._light.setChecked(scheme == Qt.ColorScheme.Light)
        self._dark.setChecked(scheme == Qt.ColorScheme.Dark)
        self._syncing = False

    def _add_system(self) -> None:
        self._writing = True
        added = self._state.add_system(self.system_name.text())
        self._writing = False
        if added:
            self.system_name.clear()
            self.message.setText("")
        else:
            self.message.setText("Enter a new system name. Other is reserved for the defect list.")
        self.refresh()

    def _remove_system(self, name: str) -> None:
        self._writing = True
        removed = self._state.remove_system(name)
        self._writing = False
        if not removed:
            self.message.setText(f"{name} is on a work order, so it stays.")
        else:
            self.message.setText("")
        self.refresh()

    def _save_lead_time(self) -> None:
        self._writing = True
        self._state.set_lead_time(_parse_days(self.lead_time.text()))
        self._writing = False

    def _save_days(self, system: str, action: str, text: str) -> None:
        if self._writing:
            return
        self._writing = True
        self._state.set_average(system, action, _parse_days(text))
        self._writing = False

    def _save_on(self, system: str, action: str, on: bool) -> None:
        if self._writing:
            return
        self._writing = True
        self._state.set_action_on(system, action, on)
        self._writing = False

    def refresh(self) -> None:
        if self._writing:
            return
        self._writing = True
        while self.rows.count():
            item = self.rows.takeAt(0)
            widget = item.widget()
            if widget is not None:
                discard(widget)
        for name, averages in self._state.systems.items():
            self.rows.addWidget(self._row(name, averages))
        shown = "" if self._state.lead_time_days is None else f"{self._state.lead_time_days:g}"
        if self.lead_time.text() != shown and not self.lead_time.hasFocus():
            self.lead_time.setText(shown)
        self._writing = False

    def _row(self, name: str, averages) -> QWidget:
        row = QWidget()
        row.setObjectName("systemRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        title = QLabel(name)
        title.setObjectName("systemName")
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title, 1)

        actions = QVBoxLayout()
        actions.setSpacing(6)
        values = (averages.diagnose, averages.repair, averages.replace)
        flags = (averages.diagnose_on, averages.repair_on, averages.replace_on)
        for action, value, on in zip(ACTIONS, values, flags):
            line = QHBoxLayout()
            line.setSpacing(8)
            box = QCheckBox(action)
            box.setChecked(on)
            box.toggled.connect(lambda checked, n=name, a=action: self._save_on(n, a, checked))
            days = QLineEdit("" if value is None else f"{value:g}")
            days.setValidator(QDoubleValidator(0.0, 9999.0, 2))
            days.setPlaceholderText("Days")
            days.setFixedWidth(72)
            days.editingFinished.connect(
                lambda n=name, a=action, field=days: self._save_days(n, a, field.text())
            )
            line.addWidget(box)
            line.addWidget(days)
            actions.addLayout(line)
        side = QVBoxLayout()
        side.setSpacing(8)
        side.addLayout(actions)
        remove = QPushButton("Remove")
        remove.clicked.connect(lambda _checked=False, n=name: self._remove_system(n))
        side.addWidget(remove, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(side, 0)
        return row


def _parse_days(text: str) -> float | None:
    cleaned = text.strip()
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    if value < 0:
        return None
    return value
