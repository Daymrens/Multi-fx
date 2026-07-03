from PyQt6.QtCore import Qt, QMimeData, QPoint, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QFrame, QSizePolicy, QScrollArea

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
        self._on_ensure_visible = None
        self._selected = -1

        self.setAcceptDrops(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:horizontal { background: transparent; height: 4px; border: none; }
            QScrollBar::handle:horizontal { background: #27273B; border-radius: 2px; min-width: 20px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """)
        outer.addWidget(self.scroll_area)

        self.strip = QWidget()
        self.strip_layout = QHBoxLayout(self.strip)
        self.strip_layout.setContentsMargins(8, 6, 8, 6)
        self.strip_layout.setSpacing(0)
        self.scroll_area.setWidget(self.strip)

        self.setStyleSheet(f"""
            ChainView {{
                background-color: {BG_DARK};
                border: 1px solid {BORDER};
                border-radius: 8px;
                min-height: 58px;
            }}
        """)

        self._add_empty_label()

    def _add_empty_label(self):
        if len(self._slots) == 0:
            lbl = QLabel('+ Click to add effects (or use presets)')
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f'color: {FG_DIM}; font-size: 11px; padding: 12px;')
            self.strip_layout.addWidget(lbl)

    def _remove_empty_label(self):
        for i in range(self.strip_layout.count()):
            w = self.strip_layout.itemAt(i).widget()
            if isinstance(w, QLabel) and w.text().startswith('+'):
                self.strip_layout.removeWidget(w)
                w.deleteLater()

    def set_effects(self, names, bypasses):
        self._remove_empty_label()
        for i in reversed(range(self.strip_layout.count())):
            w = self.strip_layout.itemAt(i).widget()
            if w:
                self.strip_layout.removeWidget(w)
                w.deleteLater()
        self._slots = []

        for name, bypassed in zip(names, bypasses):
            self._add_slot(name, bypassed)

        if len(self._slots) == 0:
            self._add_empty_label()

    def _add_slot(self, name, bypassed=False):
        if len(self._slots) > 0:
            arrow = QLabel('→')
            arrow.setStyleSheet(f'color: {ARROW_FADED}; font-size: 11px; background: transparent;')
            arrow.setFixedWidth(14)
            arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.strip_layout.addWidget(arrow)

        idx = len(self._slots)
        slot = _EffectSlot(name, idx, bypassed)
        slot.selected = (idx == self._selected)
        slot.clicked.connect(lambda i=idx: self._on_slot_click(i))
        slot.bypass_toggled.connect(lambda i=idx: self._on_bypass_toggle(i))
        slot.remove_requested.connect(lambda i=idx: self._on_remove_request(i))
        self.strip_layout.addWidget(slot)
        self._slots.append(slot)

    def _on_slot_click(self, idx):
        self._selected = idx
        for i, s in enumerate(self._slots):
            s.selected = (i == idx)
        if self._on_select:
            self._on_select(idx)
        if self._on_ensure_visible:
            self._on_ensure_visible(idx)

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
        self._hovered = False
        self._drag_start = None

        self.setFixedSize(110, 46)
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

        self._name_lbl = QLabel(self._name)
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setStyleSheet(f'font-size: 10px; font-weight: 600; color: {FG}; background: transparent;')
        layout.addWidget(self._name_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def _update_style(self):
        if self._bypassed:
            bg = BG_CARD
            border = BORDER_SUBTLE
        elif self._selected:
            bg = ACTIVE_BG
            border = ACCENT
        else:
            bg = BG_CARD
            border = BORDER

        self.setStyleSheet(f"""
            _EffectSlot {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
        """)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, v):
        self._selected = v
        self._update_style()
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        if self._selected:
            cx, cy = w / 2, h / 2
            glow = QRadialGradient(cx, cy, w * 0.5)
            glow.setColorAt(0, QColor(ACCENT))
            glow.setColorAt(1, QColor(ACCENT))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(ACCENT))
            painter.setOpacity(0.08)
            painter.drawRoundedRect(1, 1, w - 2, h - 2, 5, 5)
            painter.setOpacity(1.0)

        led_cy = h - 8
        led_cx = w / 2
        led_r = 4

        if self._bypassed:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor('#555555'))
            painter.drawEllipse(QPointF(led_cx, led_cy), led_r, led_r)
        else:
            glow_r = led_r * 2.5
            glow2 = QRadialGradient(led_cx, led_cy, glow_r)
            glow2.setColorAt(0, QColor(ACCENT))
            glow2.setColorAt(1, QColor(ACCENT))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(ACCENT))
            painter.setOpacity(0.15)
            painter.drawEllipse(QPointF(led_cx, led_cy), glow_r, glow_r)
            painter.setOpacity(1.0)
            painter.setBrush(QColor(ACCENT))
            painter.drawEllipse(QPointF(led_cx, led_cy), led_r, led_r)

        if self._bypassed:
            text_rect = self._name_lbl.geometry()
            painter.setPen(QPen(QColor(FG_DIM), 1))
            y = text_rect.center().y()
            painter.drawLine(int(text_rect.left() + 6), y, int(text_rect.right() - 6), y)

        if self._hovered:
            remove_r = 6
            remove_x = w - 9
            remove_y = 9
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.drawEllipse(QPointF(remove_x, remove_y), remove_r, remove_r)
            painter.setPen(QPen(QColor(FG_MUTED), 1.5))
            painter.drawLine(QPointF(remove_x - 2.5, remove_y - 2.5), QPointF(remove_x + 2.5, remove_y + 2.5))
            painter.drawLine(QPointF(remove_x + 2.5, remove_y - 2.5), QPointF(remove_x - 2.5, remove_y + 2.5))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            remove_x = self.width() - 9
            remove_y = 9
            if self._hovered and (pos.x() - remove_x) ** 2 + (pos.y() - remove_y) ** 2 <= 49:
                self.remove_requested.emit(self._index)
                return
            led_cx = self.width() / 2
            led_cy = self.height() - 8
            if (pos.x() - led_cx) ** 2 + (pos.y() - led_cy) ** 2 <= 64:
                self.bypass_toggled.emit(self._index)
                return
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
