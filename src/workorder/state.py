"""In-memory work order for the GUI stage.

Manuals, inventories, and the encrypted database are not connected yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

ACTIONS = ("Diagnose", "Repair", "Replace")
INVENTORY_SOURCES = ("DSI", "SMU", "RIP")
LIFECYCLE = ("Open", "Maint", "Close", "Archive")


@dataclass
class MajorDefect:
    system: str
    title: str
    action: str
    included: bool = True


@dataclass
class OtherDefect:
    text: str
    included: bool = True


@dataclass
class SystemAverages:
    diagnose: float | None = None
    repair: float | None = None
    replace: float | None = None
    diagnose_on: bool = True
    repair_on: bool = True
    replace_on: bool = True

    def for_action(self, action: str) -> float | None:
        return {
            "Diagnose": self.diagnose,
            "Repair": self.repair,
            "Replace": self.replace,
        }[action]

    def action_on(self, action: str) -> bool:
        return {
            "Diagnose": self.diagnose_on,
            "Repair": self.repair_on,
            "Replace": self.replace_on,
        }[action]


@dataclass
class Publication:
    platform: str
    kind: str
    filename: str
    imported_on: date


@dataclass
class InventoryImport:
    source: str
    filename: str
    imported_on: date


@dataclass
class EstimateLine:
    label: str
    days: float | None
    missing: bool


@dataclass
class Estimate:
    lines: list[EstimateLine]
    total_days: float | None
    missing: list[str]
    turned_off: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.missing and bool(self.lines)


@dataclass
class WorkOrder:
    """One work order document. Preferences and the library stay on the app."""

    opened_on: date
    number: int
    status: str = "Open"
    major_defects: list[MajorDefect] = field(default_factory=list)
    other_defects: list[OtherDefect] = field(default_factory=list)
    app: AppState | None = field(default=None, repr=False)

    def label(self) -> str:
        text = self.opened_on.strftime("%-d %b %Y")
        same = [item for item in self.app.work_orders if item.opened_on == self.opened_on]
        if len(same) < 2:
            return text
        return f"{text} · {same.index(self) + 1}"

    def set_status(self, status: str) -> None:
        if status not in LIFECYCLE or status == self.status:
            return
        self.status = status
        self.app.notify()

    def add_other_defect(self, text: str) -> bool:
        cleaned = text.strip()
        if not cleaned:
            return False
        self.other_defects.append(OtherDefect(cleaned))
        self.app.notify()
        return True

    def remove_other_defect(self, index: int) -> None:
        del self.other_defects[index]
        self.app.notify()

    def set_major_included(self, index: int, included: bool) -> None:
        self.major_defects[index].included = included
        self.app.notify()

    def set_other_included(self, index: int, included: bool) -> None:
        self.other_defects[index].included = included
        self.app.notify()

    def qc_lines(self) -> list[tuple[str, str]]:
        """Defects turned on from this work order. kind is 'major' or 'other'."""
        lines: list[tuple[str, str]] = []
        for defect in self.major_defects:
            if defect.included:
                lines.append(("major", f"{defect.system} - {defect.title}"))
        for defect in self.other_defects:
            if defect.included:
                lines.append(("other", f"Other - {defect.text}"))
        return lines

    def estimate(self) -> Estimate:
        lines: list[EstimateLine] = []
        missing: list[str] = []
        turned_off: list[str] = []
        total = 0.0
        counted = 0
        for defect in self.major_defects:
            if not defect.included:
                continue
            label = f"{defect.system} {defect.action}"
            if not self._action_counts(defect):
                turned_off.append(label)
                continue
            counted += 1
            days = self.app.systems.get(defect.system, SystemAverages()).for_action(defect.action)
            if days is None:
                missing.append(label)
                lines.append(EstimateLine(label, None, True))
            else:
                total += days
                lines.append(EstimateLine(label, days, False))
        if counted == 0:
            return Estimate([], None, [], turned_off)
        if missing:
            return Estimate(lines, None, missing, turned_off)
        return Estimate(lines, total, [], turned_off)

    def _action_counts(self, defect: MajorDefect) -> bool:
        averages = self.app.systems.get(defect.system)
        if averages is None:
            return True
        return averages.action_on(defect.action)


@dataclass
class AppState:
    systems: dict[str, SystemAverages] = field(default_factory=dict)
    work_orders: list[WorkOrder] = field(default_factory=list)
    lead_time_days: float | None = None
    publications: list[Publication] = field(default_factory=list)
    inventory_imports: dict[str, InventoryImport] = field(default_factory=dict)
    _listeners: list = field(default_factory=list, repr=False)
    _next_number: int = 1

    def subscribe(self, listener) -> None:
        self._listeners.append(listener)

    def notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def add_system(self, name: str) -> bool:
        cleaned = name.strip()
        if not cleaned or cleaned in self.systems or cleaned.casefold() == "other":
            return False
        self.systems[cleaned] = SystemAverages()
        self.notify()
        return True

    def new_work_order(self) -> WorkOrder:
        order = WorkOrder(opened_on=date.today(), number=self._next_number, app=self)
        self._next_number += 1
        self.work_orders.append(order)
        self.notify()
        return order

    def remove_system(self, name: str) -> bool:
        used = any(
            defect.system == name
            for order in self.work_orders
            for defect in order.major_defects
        )
        if used:
            return False
        if name not in self.systems:
            return False
        del self.systems[name]
        self.notify()
        return True

    def set_average(self, system: str, action: str, days: float | None) -> None:
        averages = self.systems[system]
        if action == "Diagnose":
            averages.diagnose = days
        elif action == "Repair":
            averages.repair = days
        elif action == "Replace":
            averages.replace = days
        else:
            raise ValueError(action)
        self.notify()

    def set_action_on(self, system: str, action: str, on: bool) -> None:
        averages = self.systems[system]
        if action == "Diagnose":
            averages.diagnose_on = on
        elif action == "Repair":
            averages.repair_on = on
        elif action == "Replace":
            averages.replace_on = on
        else:
            raise ValueError(action)
        self.notify()

    def set_lead_time(self, days: float | None) -> None:
        self.lead_time_days = days
        self.notify()

    def record_publication(
        self,
        platform: str,
        kind: str,
        filename: str,
        imported_on: date | None = None,
    ) -> bool:
        cleaned = platform.strip()
        name = filename.strip()
        if not cleaned or not name:
            return False
        self.publications.append(
            Publication(cleaned, kind, name, imported_on or date.today())
        )
        self.notify()
        return True

    def record_inventory(
        self,
        source: str,
        filename: str,
        imported_on: date | None = None,
    ) -> bool:
        name = filename.strip()
        if source not in INVENTORY_SOURCES or not name:
            return False
        self.inventory_imports[source] = InventoryImport(
            source, name, imported_on or date.today()
        )
        self.notify()
        return True

    def platforms(self) -> list[str]:
        return sorted({item.platform for item in self.publications}, key=str.casefold)

    def publications_for(self, platform: str) -> list[Publication]:
        rows = [item for item in self.publications if item.platform == platform]
        rows.sort(key=lambda item: (item.imported_on, item.kind, item.filename), reverse=True)
        return rows

def split_columns(items: list) -> tuple[list, list]:
    """Fill the left column, then the right, so both sides of a section are used."""
    if not items:
        return [], []
    midpoint = (len(items) + 1) // 2
    return items[:midpoint], items[midpoint:]
