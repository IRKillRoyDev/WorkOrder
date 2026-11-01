"""A work order in its own window. Two tabs: the work order, and its defects."""

from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from workorder.state import WorkOrder
from workorder.ui.defect_list_page import DefectListPage
from workorder.ui.widgets import marking_banner
from workorder.ui.work_order_page import WorkOrderPage


class WorkOrderWindow(QMainWindow):
    def __init__(self, order: WorkOrder, install_menu) -> None:
        super().__init__()
        self.order = order
        self.setWindowTitle(order.label())
        self.resize(980, 760)

        shell = QWidget()
        shell.setObjectName("shell")
        root = QVBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(marking_banner())

        self.tabs = QTabWidget()
        self.tabs.addTab(WorkOrderPage(order), "Main Work Order")
        self.tabs.addTab(DefectListPage(order), "Defects")
        root.addWidget(self.tabs, 1)
        root.addWidget(marking_banner())
        self.setCentralWidget(shell)

        install_menu(self, order)
        order.app.subscribe(self._retitle)

    def _retitle(self) -> None:
        self.setWindowTitle(self.order.label())
