from PyQt6.QtCore import Qt, QMimeData, QPoint, pyqtSignal
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QFrame, QSizePolicy
import math

from .theme import *

EFFECT_COLORS = {
    'Gate': '#64748B',
    'FilterEQ': '#3B82F6',
    'Compressor': '#F59E0B',
    'Distortion': '#EF4444',
    'Modulation': '#8B5CF6',
    'Delay': '#06B6D4',
    'Reverb': '#EC4899',
    'Limiter': '#F97316',
}


class ChainView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._slots = []
        self._on_select = None
        self._on_reorder = None
        self._on_toggle_bypass = None
        self._on_remove = None
        self._selected = -1

        self.setAcceptDrops(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self._layout = layout

        self.setStyleSheet(f"""
            ChainView {{
                background-color: {BG_DARK};
                border: 1px solid {BORDER};
                border-radius: 8px;
                min-height: 52px;
            }}
        """)

        self._add_empty_label()

    def _add_empty_label(self):
        if len(self._slots) == 0:
            lbl = QLabel('+ Click to add effects (or use presets)')
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f'color: {FG_DIM}; font-size: 11px; padding: 12px;')
            self._layout.addWidget(lbl)

    def _remove_empty_label(self):
        for i in range(self._layout.count()):
            w = self._layout.itemAt(i).widget()
            if isinstance(w, QLabel) and w.text().startswith('+'):
                self._layout.removeWidget(w)
                w.deleteLater()

    def set_effects(self, names, bypasses):
        self._remove_empty_label()
        for i in reversed(range(self._layout.count())):
            w = self._layout.itemAt(i).widget()
            if w:
                self._layout.removeWidget(w)
                w.deleteLater()
        self._slots = []

        for name, bypassed in zip(names, bypasses):
            self._add_slot(name, bypassed)

        if len(self._slots) == 0:
            self._add_empty_label()

    def _add_slot(self, name, bypassed=False):
        idx = len(self._slots)
        slot = _EffectSlot(name, idx, bypassed)
        slot.selected = (idx == self._selected)
        slot.clicked.connect(lambda i=idx: self._on_slot_click(i))
        slot.bypass_toggled.connect(lambda i=idx: self._on_bypass_toggle(i))
        slot.remove_requested.connect(lambda i=idx: self._on_remove_request(i))
        self._layout.addWidget(slot)
        self._slots.append(slot)

    def _on_slot_click(self, idx):
        self._selected = idx
        for i, s in enumerate(self._slots):
            s.selected = (i == idx)
        if self._on_select:
            self._on_select(idx)

    def _on_bypass_toggle(self, idx):
        if self._on_toggle_bypass:
            self._on_toggle_bypass(idx)

    def _on_remove_request(self, idx):
        if self._on_remove:
            self._on_remove(idx)

    def select(self, idx):
        self._selected = idx
        for i, s in enumerate(self._slots):
            s.selected = (i == idx)

    def get_selected(self):
        return self._selected


class _EffectSlot(QFrame):
    clicked = pyqtSignal(int)
    bypass_toggled = pyqtSignal(int)
    remove_requested = pyqtSignal(int)

    def __init__(self, name, index, bypassed=False):
        super().__init__()
        self._name = name
        self._index = index
        self._bypassed = bypassed
        self._selected = False
        self._drag_start = None

        self.setFixedWidth(90)
        self._build_ui()
        self._update_style()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        color = EFFECT_COLORS.get(self._name, '#64748B')
        indicator = QFrame()
        indicator.setFixedHeight(3)
        indicator.setStyleSheet(f'background: {color}; border-radius: 1.5px;')
        layout.addWidget(indicator)

        name_lbl = QLabel(self._name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f'font-size: 10px; font-weight: 600; color: {FG};')
        layout.addWidget(name_lbl)

        self._bypass_btn = QPushButton('B')
        self._bypass_btn.setFixedSize(20, 16)
        self._bypass_btn.setStyleSheet(f'font-size: 8px; font-weight: bold; padding: 0; color: {FG_MUTED}; background: {BG_CARD}; border: 1px solid {BORDER_SUBTLE}; border-radius: 3px;')
        self._bypass_btn.clicked.connect(lambda: self.bypass_toggled.emit(self._index))
        layout.addWidget(self._bypass_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _update_style(self):
        if self._bypassed:
            bg = BG_CARD
            border = BORDER_SUBTLE
            opacity = 0.5
        elif self._selected:
            bg = ACTIVE_BG
            border = ACCENT
            opacity = 1.0
        else:
            bg = BG_CARD
            border = BORDER
            opacity = 1.0

        self.setStyleSheet(f"""
            _EffectSlot {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
        """)
        self.setWindowOpacity(opacity)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, v):
        self._selected = v
        self._update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
            self.clicked.emit(self._index)

    def mouseMoveEvent(self, event):
        if self._drag_start and (event.position().toPoint() - self._drag_start).manhattanLength() > 10:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f'effect:{self._index}')
            drag.setMimeData(mime)
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.position().toPoint())
            drag.exec(Qt.DropAction.MoveAction)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.bypass_toggled.emit(self._index)



