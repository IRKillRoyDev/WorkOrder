"""Where each work order sits in the maintenance lifecycle."""

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from workorder.state import LIFECYCLE, AppState, WorkOrder
from workorder.ui.widgets import Page, discard, section


class StatusPage(Page):
    def __init__(self, state: AppState, on_open) -> None:
        super().__init__()
        self._state = state
        self._on_open = on_open
        self._columns: dict[str, QVBoxLayout] = {}

        row = QHBoxLayout()
        row.setSpacing(12)
        for name in LIFECYCLE:
            frame, layout = section(name)
            frame.setMinimumHeight(360)
            orders = QVBoxLayout()
            orders.setSpacing(8)
            layout.addLayout(orders)
            layout.addStretch(1)
            row.addWidget(frame, 1)
            self._columns[name] = orders
        self.column.addLayout(row)
        self.column.addStretch(1)

        state.subscribe(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        for name, layout in self._columns.items():
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    discard(widget)
            for order in self._state.work_orders:
                if order.status == name:
                    layout.addWidget(self._card(order))

    def _card(self, order: WorkOrder) -> QWidget:
        card = QWidget()
        card.setObjectName("systemRow")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        open_button = QPushButton(order.label())
        open_button.setObjectName("platformButton")
        open_button.clicked.connect(lambda _checked=False, chosen=order: self._on_open(chosen))
        status = QComboBox()
        status.setObjectName("lifecycle")
        status.addItems(LIFECYCLE)
        status.setCurrentText(order.status)
        status.currentTextChanged.connect(lambda chosen, target=order: target.set_status(chosen))
        layout.addWidget(open_button)
        layout.addWidget(status)
        return card
