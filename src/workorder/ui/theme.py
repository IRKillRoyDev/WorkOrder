"""Light and dark palettes. The window does not keep one set of light colors."""

import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPalette, QPen, QPixmap

_LIGHT = {
    "window": "#f2f2f7",
    "window_text": "#1c1c1e",
    "sidebar": "#e5e5ea",
    "base": "#ffffff",
    "text": "#1c1c1e",
    "card": "#ffffff",
    "border": "#c7c7cc",
    "button": "#ffffff",
    "button_text": "#1c1c1e",
    "highlight": "#007aff",
    "highlighted_text": "#ffffff",
}

_DARK = {
    "window": "#1c1c1e",
    "window_text": "#f2f2f7",
    "sidebar": "#2c2c2e",
    "base": "#1c1c1e",
    "text": "#f2f2f7",
    "card": "#2c2c2e",
    "border": "#48484a",
    "button": "#3a3a3c",
    "button_text": "#f2f2f7",
    "highlight": "#0a84ff",
    "highlighted_text": "#ffffff",
}

# CUI banners stay purple with white text in both appearances.
# The marking is not window chrome, so it does not invert with the theme.
CUI_PURPLE = "#5B2C6F"
CUI_TEXT = "#FFFFFF"


def apply_theme(scheme: Qt.ColorScheme | None = None) -> Qt.ColorScheme:
    """None follows the Mac appearance. Light or Dark overrides it."""
    app = QGuiApplication.instance()
    hints = QGuiApplication.styleHints()
    if scheme is None:
        hints.unsetColorScheme()
        resolved = hints.colorScheme()
        if resolved not in (Qt.ColorScheme.Light, Qt.ColorScheme.Dark):
            resolved = Qt.ColorScheme.Light
    else:
        resolved = scheme
        if app is None or app.platformName() != "offscreen":
            hints.setColorScheme(scheme)
    colors = _DARK if resolved == Qt.ColorScheme.Dark else _LIGHT
    if app is not None:
        app.setPalette(_palette(colors))
        app.setStyleSheet(_stylesheet(colors))
    return resolved


def _palette(colors: dict[str, str]) -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["window"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["window_text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["base"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["sidebar"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["button"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["button_text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["highlight"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["highlighted_text"]))
    palette.setColor(QPalette.ColorRole.Mid, QColor(colors["border"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors["border"]))
    return palette


def _checked_icon(fill: str) -> str:
    path = Path(tempfile.gettempdir()) / f"workorder-checked-{fill[1:]}.png"
    if not path.exists():
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(fill))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 17, 17, 3, 3)
        pen = QPen(QColor("#ffffff"))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(4, 9, 7, 13)
        painter.drawLine(7, 13, 14, 5)
        painter.end()
        pixmap.save(str(path))
    return path.as_posix()


def _stylesheet(colors: dict[str, str]) -> str:
    checked = _checked_icon(colors["highlight"])
    return f"""
QMainWindow, QWidget#shell, QWidget#pageBody, QWidget#pageViewport {{
    background: {colors["window"]};
    color: {colors["window_text"]};
}}
QScrollArea#pageScroll {{
    background: {colors["window"]};
    border: none;
}}
QWidget#sidebar {{
    background: {colors["sidebar"]};
    color: {colors["window_text"]};
}}
QPushButton#nav, QPushButton#appearance {{
    text-align: left;
    padding: 8px 12px;
    border: 1px solid transparent;
    border-radius: 6px;
    background: transparent;
    color: {colors["window_text"]};
}}
QPushButton#appearance {{
    text-align: center;
    padding: 6px 10px;
    border: 1px solid {colors["border"]};
    background: {colors["button"]};
}}
QPushButton#nav:checked, QPushButton#appearance:checked {{
    background: {colors["highlight"]};
    color: {colors["highlighted_text"]};
    font-weight: 600;
}}
QPushButton {{
    background: {colors["button"]};
    color: {colors["button_text"]};
    border: 1px solid {colors["border"]};
    border-radius: 6px;
    padding: 6px 12px;
}}
QPushButton#platformButton {{
    text-align: left;
    background: {colors["base"]};
    color: {colors["text"]};
    padding: 10px 12px;
}}
QPushButton#backButton {{
    padding: 6px 12px;
}}
QTabWidget::pane {{
    border: none;
    background: {colors["window"]};
}}
QTabBar::tab {{
    background: {colors["sidebar"]};
    color: {colors["window_text"]};
    padding: 8px 16px;
    margin-right: 4px;
    border: 1px solid {colors["border"]};
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background: {colors["card"]};
    font-weight: 600;
}}
QLabel#banner {{
    background: {CUI_PURPLE};
    color: {CUI_TEXT};
    padding: 6px;
    font-weight: 700;
    letter-spacing: 0.12em;
}}
QFrame#section, QWidget#systemRow {{
    background: {colors["card"]};
    color: {colors["text"]};
    border: 1px solid {colors["border"]};
    border-radius: 8px;
}}
QFrame#section QLabel, QWidget#systemRow QLabel {{
    background: transparent;
    color: {colors["text"]};
}}
QLabel#sectionTitle, QLabel#systemName, QLabel#platformTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {colors["text"]};
}}
QLabel#platformTitle {{ font-size: 20px; }}
QLabel#hint {{ color: {colors["text"]}; }}
QFrame#columnDivider {{ color: {colors["border"]}; }}
QLineEdit, QComboBox {{
    background: {colors["base"]};
    color: {colors["text"]};
    border: 1px solid {colors["border"]};
    border-radius: 4px;
    padding: 4px 6px;
    min-height: 22px;
    selection-background-color: {colors["highlight"]};
    selection-color: {colors["highlighted_text"]};
}}
QCheckBox {{
    color: {colors["window_text"]};
    background: transparent;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {colors["border"]};
    border-radius: 3px;
    background: {colors["base"]};
}}
QCheckBox::indicator:checked {{
    image: url({checked});
    border: none;
}}
"""
