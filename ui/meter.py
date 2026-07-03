from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import numpy as np

from .theme import *


class Meter(QWidget):
    def __init__(self, label='', parent=None):
        super().__init__(parent)
        self._label = label
        self._peak = 0.0
        self._hold = 0.0
        self._fall = 0.0
        self.setFixedSize(20, 140)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._decay)
        self._timer.start(30)

    def set_peak(self, peak):
        self._peak = peak
        if peak > self._hold:
            self._hold = peak
            self._fall = 0

    def _decay(self):
        self._hold *= 0.97
        if self._hold < 0.001:
            self._hold = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 2
        bar_w = w - margin * 2
        bar_h = h - margin * 2 - 14

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(METER_BG))
        painter.drawRoundedRect(margin, margin, bar_w, bar_h, 3, 3)

        if self._peak > 0:
            db = max(-60, 20 * np.log10(max(self._peak, 1e-10)))
            ratio = (db + 60) / 60
            ratio = max(0, min(1, ratio))

            fill_h = int(ratio * bar_h)

            grad = QLinearGradient(0, margin + bar_h, 0, margin)
            grad.setColorAt(0, QColor(METER_LOW))
            grad.setColorAt(0.6, QColor(METER_MID))
            grad.setColorAt(0.85, QColor(METER_HIGH))
            painter.setBrush(grad)

            painter.drawRoundedRect(margin, margin + bar_h - fill_h, bar_w, fill_h, 2, 2)

            hold_y = margin + bar_h - (20 * np.log10(max(self._hold, 1e-10)) + 60) / 60 * bar_h
            if 0 <= hold_y <= margin + bar_h:
                painter.setPen(QPen(QColor(FG), 1.5))
                painter.drawLine(margin, int(hold_y), margin + bar_w, int(hold_y))

        painter.setPen(QColor(FG_DIM))
        font = painter.font()
        font.setPointSize(7)
        painter.setFont(font)
        painter.drawText(QRectF(0, margin + bar_h + 2, w, 12), Qt.AlignmentFlag.AlignCenter, self._label)
