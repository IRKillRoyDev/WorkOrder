"""Publications by platform, plus the inventory import dates."""

from datetime import date

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from workorder.state import INVENTORY_SOURCES, AppState
from workorder.ui.widgets import Page, discard, section


class LibraryPage(Page):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self._state = state
        self._platform: str | None = None

        self._stack = QStackedWidget()
        self.column.addWidget(self._stack)

        overview = QWidget()
        overview_layout = QVBoxLayout(overview)
        overview_layout.setContentsMargins(0, 0, 0, 0)
        overview_layout.setSpacing(16)

        inventories, inventory_layout = section("Inventories")
        self.inventory_rows = QVBoxLayout()
        inventory_layout.addLayout(self.inventory_rows)
        overview_layout.addWidget(inventories)

        platforms, platform_layout = section("Platforms")
        note = QLabel(
            "Each platform opens to the maintenance and technical publications uploaded for it."
        )
        note.setWordWrap(True)
        note.setObjectName("hint")
        platform_layout.addWidget(note)
        self.platform_rows = QVBoxLayout()
        self.platform_rows.setSpacing(8)
        platform_layout.addLayout(self.platform_rows)
        self.platform_empty = QLabel("No publications yet.")
        self.platform_empty.setObjectName("hint")
        platform_layout.addWidget(self.platform_empty)
        overview_layout.addWidget(platforms)
        overview_layout.addStretch(1)
        self._stack.addWidget(overview)

        detail = QWidget()
        detail_layout = QVBoxLayout(detail)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(16)
        back_row = QHBoxLayout()
        back = QPushButton("All platforms")
        back.setObjectName("backButton")
        back.clicked.connect(self.show_overview)
        back_row.addWidget(back)
        back_row.addStretch(1)
        detail_layout.addLayout(back_row)
        publications, publication_layout = section("Publications")
        self.platform_title = QLabel("")
        self.platform_title.setObjectName("platformTitle")
        self.platform_title.setWordWrap(True)
        publication_layout.insertWidget(0, self.platform_title)
        self.publication_rows = QVBoxLayout()
        self.publication_rows.setSpacing(8)
        publication_layout.addLayout(self.publication_rows)
        detail_layout.addWidget(publications)
        detail_layout.addStretch(1)
        self._stack.addWidget(detail)

        state.subscribe(self.refresh)
        self.refresh()

    def show_overview(self) -> None:
        self._platform = None
        self._stack.setCurrentIndex(0)
        self.refresh()

    def show_platform(self, name: str) -> None:
        self._platform = name
        self._stack.setCurrentIndex(1)
        self.refresh()

    def refresh(self) -> None:
        self._fill_inventories()
        self._fill_platforms()
        self._fill_publications()

    def _fill_inventories(self) -> None:
        _clear(self.inventory_rows)
        for source in INVENTORY_SOURCES:
            record = self._state.inventory_imports.get(source)
            if record is None:
                text = "Not imported"
                when = ""
            else:
                text = record.filename
                when = _format_date(record.imported_on)
            self.inventory_rows.addWidget(_dated_row(source, text, when))

    def _fill_platforms(self) -> None:
        _clear(self.platform_rows)
        names = self._state.platforms()
        self.platform_empty.setVisible(not names)
        for name in names:
            rows = self._state.publications_for(name)
            count = len(rows)
            noun = "publication" if count == 1 else "publications"
            latest = _format_date(rows[0].imported_on)
            button = QPushButton(f"{name}     {count} {noun}     Latest {latest}")
            button.setObjectName("platformButton")
            button.clicked.connect(lambda _checked=False, chosen=name: self.show_platform(chosen))
            self.platform_rows.addWidget(button)

    def _fill_publications(self) -> None:
        _clear(self.publication_rows)
        if not self._platform:
            self.platform_title.setText("")
            return
        self.platform_title.setText(self._platform)
        for item in self._state.publications_for(self._platform):
            self.publication_rows.addWidget(
                _dated_row(item.kind, item.filename, _format_date(item.imported_on))
            )


def _dated_row(title: str, detail: str, when: str) -> QWidget:
    row = QWidget()
    row.setObjectName("systemRow")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(12, 8, 12, 8)
    name = QLabel(title)
    name.setObjectName("publicationKind")
    name.setMinimumWidth(200)
    detail_label = QLabel(detail)
    detail_label.setObjectName("publicationName")
    when_label = QLabel(when)
    when_label.setObjectName("publicationDate")
    layout.addWidget(name)
    layout.addWidget(detail_label, 1)
    layout.addWidget(when_label)
    return row


def _format_date(value: date) -> str:
    return value.strftime("%-d %b %Y")


def _clear(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            discard(widget)
