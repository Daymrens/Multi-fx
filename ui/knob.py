from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient, QConicalGradient
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import math

from .theme import *


class Knob(QWidget):
    value_changed = pyqtSignal(float)

    def __init__(self, label='', min_val=0, max_val=100, default=50, unit='', parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._value = default
        self._default = default
        self._label_text = label
        self._unit = unit
        self._dragging = False
        self._start_y = 0
        self._start_val = default
        self._fine = False
        self.setFixedSize(56, 72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self._value_label = QLabel(self._format_value(default))
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setStyleSheet(f'font-size: 11px; font-weight: 600; color: {ACCENT}; font-family: {FONT_MONO};')
        layout.addWidget(self._value_label)
        layout.addStretch()

    def _format_value(self, v):
        if abs(v) < 10:
            return f'{v:.1f}{self._unit}'
        return f'{int(v)}{self._unit}'

    def _to_angle(self):
        ratio = (self._value - self._min) / max(self._max - self._min, 1)
        return -135 + ratio * 270

    def _from_ratio(self, ratio):
        return self._min + ratio * (self._max - self._min)

    def set_value(self, v):
        old = self._value
        self._value = max(self._min, min(self._max, v))
        if self._value != old:
            self._value_label.setText(self._format_value(self._value))
            self.update()

    def value(self):
        return self._value

    def reset(self):
        self.set_value(self._default)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_y = event.position().y()
            self._start_val = self._value
            self._fine = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        elif event.button() == Qt.MouseButton.RightButton:
            self.reset()

    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = self._start_y - event.position().y()
            sensitivity = 0.005 if self._fine else 0.002
            delta = dy * (self._max - self._min) * sensitivity
            self.set_value(self._start_val + delta)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self.value_changed.emit(self._value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = 28, 38
        radius = 22
        angle = self._to_angle()

        pen_bg = QPen(QColor(KNOB_TRACK), 3)
        painter.setPen(pen_bg)
        painter.drawArc(QRectF(cx - radius + 2, cy - radius + 2, (radius - 2) * 2, (radius - 2) * 2),
                        135 * 16, 270 * 16)

        pen_active = QPen(QColor(KNOB_ACTIVE), 3)
        pen_active.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_active)
        painter.drawArc(QRectF(cx - radius + 2, cy - radius + 2, (radius - 2) * 2, (radius - 2) * 2),
                        135 * 16, int((angle + 135) * 16))

        painter.setPen(Qt.PenStyle.NoPen)
        grad = QRadialGradient(cx, cy, radius - 6)
        grad.setColorAt(0, QColor(KNOB_ACTIVE if self._dragging else KNOB_BG))
        grad.setColorAt(1, QColor(KNOB_BG))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(cx, cy), radius - 6, radius - 6)

        painter.setPen(QPen(QColor(FG), 2))
        end_x = cx + (radius - 10) * math.cos(math.radians(angle))
        end_y = cy + (radius - 10) * math.sin(math.radians(angle))
        painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))

        painter.setPen(QPen(QColor(FG_DIM), 1))
        font = QFont(FONT_FAMILY, 7)
        painter.setFont(font)
        painter.drawText(QRectF(0, cy + radius + 4, 56, 14), Qt.AlignmentFlag.AlignCenter, self._label_text)
