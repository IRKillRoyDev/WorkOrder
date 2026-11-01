"""The single WorkOrder window."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from workorder.reports.defect_list_pdf import write_defect_list_pdf
from workorder.state import AppState, WorkOrder
from workorder.ui.library_page import LibraryPage
from workorder.ui.preferences_page import PreferencesPage
from workorder.ui.status_page import StatusPage
from workorder.ui.theme import apply_theme
from workorder.ui.widgets import marking_banner
from workorder.ui.work_order_window import WorkOrderWindow


class MainWindow(QMainWindow):
    def __init__(self, state: AppState | None = None) -> None:
        super().__init__()
        self.setWindowTitle("WorkOrder")
        self.resize(1180, 760)
        self.state = state or AppState()
        self._scheme = apply_theme(None)
        self._sheets: dict[int, WorkOrderWindow] = {}

        self.preferences = PreferencesPage(self.state, self._choose_theme)
        self.library = LibraryPage(self.state)
        self.status_page = StatusPage(self.state, self.open_work_order)

        shell = QWidget()
        shell.setObjectName("shell")
        root = QVBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(marking_banner())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(196)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 16, 12, 16)
        side.setSpacing(4)
        title = QLabel("WorkOrder")
        title.setObjectName("sectionTitle")
        side.addWidget(title)
        stage = QLabel("Layout stage")
        stage.setObjectName("hint")
        stage.setWordWrap(True)
        side.addWidget(stage)
        side.addSpacing(12)

        self.stack = QStackedWidget()
        self._pages = [
            ("Status", self.status_page),
            ("Library", self.library),
            ("Preferences", self.preferences),
        ]
        group = QButtonGroup(self)
        group.setExclusive(True)
        for index, (name, page) in enumerate(self._pages):
            button = QPushButton(name)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.clicked.connect(lambda _checked, i=index: self.stack.setCurrentIndex(i))
            group.addButton(button)
            side.addWidget(button)
            self.stack.addWidget(page)
            if index == 0:
                button.setChecked(True)
        side.addStretch(1)
        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)
        root.addLayout(body, 1)
        root.addWidget(marking_banner())
        self.setCentralWidget(shell)

        self._install_file_menu(self)
        self.preferences.set_scheme(self._scheme)
        QGuiApplication.styleHints().colorSchemeChanged.connect(self._sync_appearance)

    def show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        buttons = self.findChildren(QPushButton, "nav")
        if 0 <= index < len(buttons):
            buttons[index].setChecked(True)

    def show_named(self, name: str) -> None:
        for index, (title, _page) in enumerate(self._pages):
            if title == name:
                self.show_page(index)
                return

    def _choose_theme(self, scheme: Qt.ColorScheme) -> None:
        self._scheme = apply_theme(scheme)
        self.preferences.set_scheme(self._scheme)

    def _sync_appearance(self, scheme: Qt.ColorScheme) -> None:
        if scheme not in (Qt.ColorScheme.Light, Qt.ColorScheme.Dark):
            return
        self.preferences.set_scheme(scheme)

    def open_work_order(self, order: WorkOrder) -> WorkOrderWindow:
        sheet = self._sheets.get(order.number)
        if sheet is not None:
            sheet.show()
            sheet.raise_()
            sheet.activateWindow()
            return sheet
        sheet = WorkOrderWindow(order, self._install_file_menu)
        sheet.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._sheets[order.number] = sheet
        sheet.destroyed.connect(lambda *_args, number=order.number: self._sheets.pop(number, None))
        sheet.show()
        return sheet

    def _install_file_menu(self, window: QMainWindow, order: WorkOrder | None = None) -> None:
        file_menu = window.menuBar().addMenu("File")
        new_action = QAction("New", window)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_work_order)
        open_action = QAction("Open...", window)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._not_ready_open)
        save_action = QAction("Save", window)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._not_ready_save)
        save_as_action = QAction("Save As...", window)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._not_ready_save_as)
        close_action = QAction("Close", window)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(window.close)

        import_menu = file_menu.addMenu("Import")
        import_menu.addAction("Troubleshooting Manual...").triggered.connect(
            lambda: self._import_manual("Troubleshooting manual")
        )
        import_menu.addAction("Parts Manual...").triggered.connect(
            lambda: self._import_manual("Parts manual")
        )
        import_menu.addSeparator()
        for source in ("DSI", "SMU", "RIP"):
            import_menu.addAction(f"{source}...").triggered.connect(
                lambda _checked=False, name=source: self._import_inventory(name)
            )

        export_menu = file_menu.addMenu("Export")
        export_menu.addAction("Defect List PDF...").triggered.connect(
            lambda _checked=False, chosen=order: self._export_defect_list(chosen)
        )

        file_menu.insertAction(import_menu.menuAction(), new_action)
        file_menu.insertAction(import_menu.menuAction(), open_action)
        file_menu.insertAction(import_menu.menuAction(), save_action)
        file_menu.insertAction(import_menu.menuAction(), save_as_action)
        file_menu.insertSeparator(import_menu.menuAction())
        file_menu.addSeparator()
        file_menu.addAction(close_action)

    def _new_work_order(self) -> None:
        self.open_work_order(self.state.new_work_order())

    def _not_ready_open(self) -> None:
        self._not_ready("Open", "Opening a saved work order waits until the database is connected.")

    def _not_ready_save(self) -> None:
        self._not_ready("Save", "Saving waits until the database is connected.")

    def _not_ready_save_as(self) -> None:
        self._not_ready("Save As", "Save As waits until the database is connected.")

    def _not_ready(self, title: str, text: str) -> None:
        QMessageBox.information(self, title, text)

    def _import_manual(self, kind: str) -> None:
        platform = self._ask_platform(kind)
        if not platform:
            return
        path, _selected = QFileDialog.getOpenFileName(self, kind, "", "PDF (*.pdf)")
        if not path:
            return
        self.state.record_publication(platform, kind, Path(path).name)
        self.show_named("Library")
        self.library.show_platform(platform)

    def _import_inventory(self, source: str) -> None:
        path, _selected = QFileDialog.getOpenFileName(
            self,
            f"Import {source}",
            "",
            "Spreadsheets (*.csv *.CSV);;All files (*)",
        )
        if not path:
            return
        self.state.record_inventory(source, Path(path).name)
        self.show_named("Library")
        self.library.show_overview()

    def _ask_platform(self, kind: str) -> str | None:
        dialog = QDialog(self)
        dialog.setWindowTitle(kind)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Platform"))
        box = QComboBox()
        box.setEditable(True)
        box.addItems(self.state.platforms())
        box.setCurrentText("")
        if box.lineEdit() is not None:
            box.lineEdit().setPlaceholderText("Platform")
        layout.addWidget(box)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        name = box.currentText().strip()
        return name or None

    def _export_defect_list(self, order: WorkOrder | None = None) -> None:
        if order is None:
            if len(self.state.work_orders) == 1:
                order = self.state.work_orders[0]
            else:
                self._not_ready("Export", "Open a work order, then export its defect list.")
                return
        path, _selected = QFileDialog.getSaveFileName(
            self,
            "Export defect list",
            "defect-list.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        write_defect_list_pdf(path, order)
