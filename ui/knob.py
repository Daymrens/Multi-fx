from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import QWidget
import math

from .theme import *


class Knob(QWidget):
    value_changed = pyqtSignal(float)

    def __init__(self, label='', vmin=0, vmax=100, default=50, unit='',
                 show_readout=False, range_dots=False, parent=None):
        super().__init__(parent)
        self._vmin = vmin
        self._vmax = vmax
        self._value = default
        self._default = default
        self._label_text = label
        self._unit = unit
        self._show_readout = show_readout
        self._range_dots = range_dots
        self._dragging = False
        self._hovered = False
        self._start_y = 0
        self._start_val = default
        self._fine = False

        self._knob_r = KNOB_DIAMETER // 2
        h = KNOB_DIAMETER + Spacing.XL + (Spacing.MD + 2 if show_readout else 0) + Spacing.SM
        self.setFixedSize(KNOB_DIAMETER, h)

    def _format_value(self, v):
        if self._unit:
            if abs(v) < 10:
                return f'{v:.1f}{self._unit}'
            return f'{int(v)}{self._unit}'
        if isinstance(v, float):
            if abs(v) < 10:
                return f'{v:.1f}'
            return f'{int(v)}'
        return str(v)

    def _angle_for_value(self):
        ratio = (self._value - self._vmin) / max(self._vmax - self._vmin, 1)
        return -135 + ratio * 270

    def set_value(self, v):
        old = self._value
        self._value = max(self._vmin, min(self._vmax, v))
        if self._value != old:
            self.update()

    def value(self):
        return self._value

    def reset(self):
        self.set_value(self._default)
        self.value_changed.emit(self._value)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_y = event.position().y()
            self._start_val = self._value
            self._fine = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.reset()

    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = self._start_y - event.position().y()
            sensitivity = 0.005 if self._fine else 0.002
            delta = dy * (self._vmax - self._vmin) * sensitivity
            self.set_value(self._start_val + delta)
            self.value_changed.emit(self._value)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.update()
            self.value_changed.emit(self._value)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta != 0:
            step = (self._vmax - self._vmin) * 0.01
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                step *= 0.2
            self.set_value(self._value + (delta / 120) * step)
            self.value_changed.emit(self._value)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        r = self._knob_r
        cx, cy = w / 2, r + Spacing.SM + 4
        angle = self._angle_for_value()

        label_top = Spacing.XS // 2
        painter.setPen(QColor(FG))
        font = QFont(FONT_FAMILY, 11, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, label_top, w, Spacing.SM + 2), Qt.AlignmentFlag.AlignCenter, self._label_text)

        if self._hovered and not self._dragging:
            glow_r = r + 4
            glow = QRadialGradient(cx, cy, glow_r)
            glow.setColorAt(0, QColor(ACCENT))
            glow.setColorAt(1, QColor(ACCENT))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(ACCENT))
            painter.setOpacity(0.12)
            painter.drawEllipse(QPointF(cx, cy), glow_r, glow_r)
            painter.setOpacity(1.0)

        grad = QRadialGradient(cx - Spacing.XS, cy - Spacing.XS, r)
        grad.setColorAt(0, QColor('#4A4A54'))
        grad.setColorAt(0.5, QColor(KNOB_BODY))
        grad.setColorAt(1, QColor(KNOB_SHADOW))
        painter.setPen(QPen(QColor(KNOB_SHADOW), 1))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        arc_rect = QRectF(cx - r + 3, cy - r + 3, (r - 3) * 2, (r - 3) * 2)
        arc_color = KNOB_INDICATOR if self._dragging else QColor(KNOB_INDICATOR).darker(120)
        pen_arc = QPen(QColor(arc_color), 2)
        pen_arc.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_arc)
        painter.drawArc(arc_rect, 135 * 16, int((angle + 135) * 16))

        if self._range_dots:
            start_angle = -135
            end_angle = 135
            dot_r = 2.5
            for a, color in [(start_angle, '#EF5350'), (end_angle, '#26C6DA')]:
                rad = math.radians(a)
                dx = cx + (r + 3) * math.cos(rad)
                dy = cy + (r + 3) * math.sin(rad)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(color))
                painter.drawEllipse(QPointF(dx, dy), dot_r, dot_r)

        indicator_len = r * 0.75
        indicator_color = '#FFFFFF' if self._dragging else KNOB_INDICATOR
        pen = QPen(QColor(indicator_color), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        end_x = cx + indicator_len * math.cos(math.radians(angle))
        end_y = cy + indicator_len * math.sin(math.radians(angle))
        painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))

        painter.setPen(QPen(QColor(KNOB_BODY).lighter(120), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), r, r)

        if self._show_readout:
            ry = cy + r + Spacing.SM - 2
            rh = 16
            readout_border = ACCENT if self._dragging else READOUT_BORDER
            painter.setPen(QPen(QColor(readout_border), 1))
            painter.setBrush(QColor(READOUT_BG))
            painter.drawRoundedRect(QRectF(cx - CELL_W // 4, ry, CELL_W // 2, rh), 3, 3)
            painter.setPen(QColor(ACCENT))
            font_r = QFont(FONT_MONO, 9)
            painter.setFont(font_r)
            painter.drawText(QRectF(cx - CELL_W // 4, ry, CELL_W // 2, rh), Qt.AlignmentFlag.AlignCenter, self._format_value(self._value))
