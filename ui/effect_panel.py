from PyQt6.QtCore import Qt, QRectF, QPointF, QSize, QEvent, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QGridLayout, QVBoxLayout, QComboBox, QCheckBox, QPushButton

import math

from .theme import *
from .knob import Knob


class PedalWidget(QWidget):
    SHELL_W = CELL_W * 2 + Spacing.LG * 2

    def __init__(self, effect, skin, on_param_change=None, on_bypass_toggle=None, on_remove_request=None):
        super().__init__()
        self._effect = effect
        self._skin = skin
        self._on_param_change = on_param_change
        self._on_bypass_toggle = on_bypass_toggle
        self._on_remove_request = on_remove_request
        self._knobs = {}
        self._footswitch_rect = QRectF()
        self._footswitch_pressed = False

        self.setFixedWidth(self.SHELL_W)
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(Spacing.SM + 2)
        layout.setVerticalSpacing(2)
        layout.setContentsMargins(Spacing.LG - 4, Spacing.MD, Spacing.LG - 4, Spacing.MD)

        param_info = self._effect.params()

        for idx, (key, info) in enumerate(param_info.items()):
            row = idx // 2
            col = idx % 2

            if 'options' in info:
                w = self._build_selector(key, info)
            elif isinstance(info.get('default'), bool):
                w = self._build_checkbox(key, info)
            else:
                w = self._build_knob(key, info)

            layout.addWidget(w, row, col, Qt.AlignmentFlag.AlignCenter)

        if len(param_info) % 2 == 1:
            layout.setColumnStretch(1, 1)

    def _build_knob(self, key, info):
        default = info.get('default', 0)
        min_v = info.get('min', 0)
        max_v = info.get('max', 100)
        label = info.get('label', key)
        unit = info.get('unit', '')
        show_readout = info.get('show_readout', True)
        range_dots = info.get('range_dots', False)

        knob = Knob(label=label, vmin=min_v, vmax=max_v, default=default,
                     unit=unit, show_readout=show_readout, range_dots=range_dots)
        knob.set_value(getattr(self._effect, key, default))
        knob.value_changed.connect(lambda v, k=key: self._param_changed(k, v))
        self._knobs[key] = knob
        return knob

    def _build_selector(self, key, info):
        options = info.get('options', [])
        current = getattr(self._effect, key, options[0] if options else '')

        combo = QComboBox()
        combo.setStyleSheet(f"""
            QComboBox {{
                background: {PANEL_BG}; color: {FG}; border: 1px solid {PANEL_BORDER};
                border-radius: 4px; padding: 2px 6px; font-size: 9px; min-width: 70px;
            }}
            QComboBox::drop-down {{ border: none; width: 14px; }}
            QComboBox QAbstractItemView {{
                background: {PANEL_BG}; color: {FG}; border: 1px solid {PANEL_BORDER};
                selection-background-color: {PANEL_FRAME};
            }}
        """)
        for opt in options:
            combo.addItem(str(opt), opt)
        idx = combo.findData(current)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.currentIndexChanged.connect(lambda i, k=key, cb=combo: self._selector_changed(k, cb))
        self._knobs[key] = combo
        return combo

    def _build_checkbox(self, key, info):
        current = getattr(self._effect, key, False)
        cb = QCheckBox(info.get('label', key))
        cb.setChecked(current)
        cb.setStyleSheet(f'color: {FG_MUTED}; font-size: 9px;')
        cb.toggled.connect(lambda v, k=key: self._param_changed(k, v))
        self._knobs[key] = cb
        return cb

    def _param_changed(self, key, value):
        if self._effect and hasattr(self._effect, key):
            setattr(self._effect, key, value)
            self._effect.update()
            if self._on_param_change:
                self._on_param_change()

    def _selector_changed(self, key, combo):
        value = combo.currentData()
        self._param_changed(key, value)

    def refresh(self):
        if self._effect and hasattr(self._effect, 'params'):
            for key in self._effect.params():
                if key in self._knobs:
                    w = self._knobs[key]
                    v = getattr(self._effect, key)
                    if isinstance(w, Knob):
                        w.set_value(v)
                    elif isinstance(w, QComboBox):
                        idx = w.findData(v)
                        if idx >= 0:
                            w.setCurrentIndex(idx)
                    elif isinstance(w, QCheckBox):
                        w.setChecked(v)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        sk = self._skin
        corner = Spacing.SM + 4

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), corner, corner)

        shadow = QPainterPath()
        shadow.addRoundedRect(QRectF(3, 3, w, h), corner, corner)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawPath(shadow)

        painter.setPen(QPen(QColor(sk['shell_border']), 2))
        painter.setBrush(QColor(sk['shell']))
        painter.drawPath(path)

        highlight = QPainterPath()
        highlight.moveTo(corner, 0)
        highlight.arcTo(QRectF(0, 0, corner * 2, corner * 2), 180, -90)
        highlight.lineTo(w - corner, 0)
        painter.setPen(QPen(QColor(sk['shell']).lighter(140), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(highlight)

        screw_r = 3
        for sx, sy in [(screw_r * 2 + 2, screw_r * 2 + 2),
                       (w - screw_r * 2 - 2, screw_r * 2 + 2),
                       (screw_r * 2 + 2, h - screw_r * 2 - 2),
                       (w - screw_r * 2 - 2, h - screw_r * 2 - 2)]:
            painter.setPen(QPen(QColor('#3A3A3A'), 1))
            painter.setBrush(QColor('#2A2A2A'))
            painter.drawEllipse(QPointF(sx, sy), screw_r, screw_r)
            painter.setPen(QPen(QColor('#5A5A5A'), 1))
            painter.drawLine(QPointF(sx - 2, sy), QPointF(sx + 2, sy))
            painter.drawLine(QPointF(sx, sy - 2), QPointF(sx, sy + 2))

        panel_margin = Spacing.LG
        panel_top = GRID * 4 + 2
        panel_bottom = GRID * 8 + 4
        panel_rect = QRectF(panel_margin, panel_top, w - panel_margin * 2, h - panel_top - panel_bottom)
        panel_path = QPainterPath()
        panel_path.addRoundedRect(panel_rect, Spacing.SM, Spacing.SM)

        if sk['panel_style'] == 'framed':
            bevel_light = QPainterPath()
            bevel_light.addRoundedRect(panel_rect.adjusted(0, 0, -1, -1), Spacing.SM, Spacing.SM)
            painter.setPen(QPen(QColor(PANEL_FRAME).lighter(150), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(bevel_light)
            bevel_dark = QPainterPath()
            bevel_dark.addRoundedRect(panel_rect.adjusted(1, 1, 0, 0), Spacing.SM, Spacing.SM)
            painter.setPen(QPen(QColor(PANEL_BORDER).darker(120), 1))
            painter.drawPath(bevel_dark)
        else:
            painter.setPen(QPen(QColor(PANEL_BORDER), 1))

        painter.setBrush(QColor(PANEL_BG))
        painter.drawPath(panel_path)

        led_r = 5
        led_cx = w / 2
        led_cy = panel_top + panel_rect.height() + Spacing.SM
        led_color = sk['led_active'] if not self._effect.bypass else sk['led_dim']
        if not self._effect.bypass:
            glow = QRadialGradient(led_cx, led_cy, led_r * 3)
            glow.setColorAt(0, QColor(led_color))
            glow.setColorAt(1, QColor(led_color).darker(200))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(led_cx, led_cy), led_r * 3, led_r * 3)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(led_color))
        painter.drawEllipse(QPointF(led_cx, led_cy), led_r, led_r)

        painter.setPen(QPen(QColor(FOOTSWITCH_SHADOW), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(led_cx, led_cy), led_r + 1, led_r + 1)

        name_y = led_cy + led_r + Spacing.SM + 2
        name_font = QFont(FONT_FAMILY, 10, QFont.Weight.Bold)
        name_font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 110)
        painter.setFont(name_font)
        painter.setPen(QColor(sk['accent']))
        name_rect = QRectF(Spacing.SM, name_y, w - Spacing.MD, Spacing.SM + 4)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, type(self._effect).__name__.upper())

        fs_cy = h - GRID * 4 - 4
        fs_cx = w / 2
        fs_r = 22
        self._footswitch_rect = QRectF(fs_cx - fs_r, fs_cy - fs_r, fs_r * 2, fs_r * 2)

        base_r = fs_r + 6
        n_sides = 6
        base_path = QPainterPath()
        for i in range(n_sides):
            a = math.radians(-90 + i * 360 / n_sides)
            px = fs_cx + base_r * math.cos(a)
            py = fs_cy + base_r * math.sin(a)
            if i == 0:
                base_path.moveTo(px, py)
            else:
                base_path.lineTo(px, py)
        base_path.closeSubpath()
        painter.setPen(QPen(QColor(FOOTSWITCH_BASE), 1))
        painter.setBrush(QColor(FOOTSWITCH_BASE))
        painter.drawPath(base_path)

        fs_off = 2 if self._footswitch_pressed else 0
        fs_grad = QRadialGradient(fs_cx - 4, fs_cy - 4 + fs_off, fs_r)
        fs_grad.setColorAt(0, QColor('#F0ECE4'))
        fs_grad.setColorAt(1, QColor(FOOTSWITCH_BG))
        painter.setPen(QPen(QColor(FOOTSWITCH_SHADOW), 1))
        painter.setBrush(fs_grad)
        painter.drawEllipse(QPointF(fs_cx, fs_cy + fs_off), fs_r, fs_r)

        remove_r = 8
        remove_x = w - Spacing.SM - 2
        remove_y = Spacing.SM + 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 120))
        painter.drawEllipse(QPointF(remove_x, remove_y), remove_r, remove_r)
        painter.setPen(QPen(QColor(FG_MUTED), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QPointF(remove_x - 3, remove_y - 3), QPointF(remove_x + 3, remove_y + 3))
        painter.drawLine(QPointF(remove_x + 3, remove_y - 3), QPointF(remove_x - 3, remove_y + 3))

        if self._effect.bypass:
            overlay = QPainterPath()
            overlay.addRoundedRect(QRectF(0, 0, w, h), corner, corner)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.drawPath(overlay)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            remove_r = 8
            remove_x = self.width() - Spacing.SM - 2
            remove_y = Spacing.SM + 2
            if (pos.x() - remove_x) ** 2 + (pos.y() - remove_y) ** 2 <= remove_r ** 2:
                if self._on_remove_request:
                    self._on_remove_request()
                return
            if self._footswitch_rect.contains(pos):
                self._footswitch_pressed = True
                self.update()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._footswitch_pressed:
            self._footswitch_pressed = False
            if self._effect:
                self._effect.bypass = not self._effect.bypass
                self.update()
                if self._on_bypass_toggle:
                    self._on_bypass_toggle()
            return
        super().mouseReleaseEvent(event)

    def minimumSizeHint(self):
        param_info = self._effect.params() if hasattr(self._effect, 'params') else {}
        knob_count = sum(1 for v in param_info.values() if 'options' not in v and not isinstance(v.get('default'), bool))
        rows = max(1, (knob_count + 1) // 2)
        h = (Spacing.MD + Spacing.LG * 2 + rows * CELL_H
             + 32 + 24 + 96 + Spacing.MD)
        return QSize(self.SHELL_W, h)

    def sizeHint(self):
        return self.minimumSizeHint()


class _EdgeFade(QWidget):
    def __init__(self, scroll_area):
        super().__init__(scroll_area.viewport())
        self._show_left = False
        self._show_right = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.raise_()

    def show_edges(self, left, right):
        self._show_left = left
        self._show_right = right
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        fade_w = 20
        bg = QColor(BG)
        painter.setPen(Qt.PenStyle.NoPen)
        if self._show_left:
            grad = QLinearGradient(0, 0, fade_w, 0)
            grad.setColorAt(0, bg)
            grad.setColorAt(1, QColor(bg.red(), bg.green(), bg.blue(), 0))
            painter.setBrush(grad)
            painter.drawRect(0, 0, fade_w, h)
        if self._show_right:
            grad = QLinearGradient(w - fade_w, 0, w, 0)
            grad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0))
            grad.setColorAt(1, bg)
            painter.setBrush(grad)
            painter.drawRect(w - fade_w, 0, fade_w, h)


class EffectPanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._container = QWidget()
        self._layout = QHBoxLayout(self._container)
        self._layout.setContentsMargins(Spacing.MD, 0, Spacing.MD, 0)
        self._layout.setSpacing(Spacing.SM)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(self._container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background: {BG}; height: 6px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {BG_CARD}; border-radius: 3px; min-width: 20px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)

        self._on_param_change = None
        self._on_bypass = None
        self._on_remove = None
        self._on_add = None
        self._pedal_widgets = []
        self._edge_fade = _EdgeFade(self)
        self.horizontalScrollBar().valueChanged.connect(self._update_fade)
        self.horizontalScrollBar().rangeChanged.connect(self._update_fade)
        self.viewport().installEventFilter(self)

    def set_effects(self, effects, on_param_change=None, on_bypass=None, on_remove=None, on_add=None):
        self._on_param_change = on_param_change
        self._on_bypass = on_bypass
        self._on_remove = on_remove
        self._on_add = on_add

        while self._layout.count():
            w = self._layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self._pedal_widgets = []

        for idx, effect in enumerate(effects):
            name = type(effect).__name__
            skin = PEDAL_SKINS.get(name, list(PEDAL_SKINS.values())[0])
            pedal = PedalWidget(
                effect, skin,
                on_param_change=on_param_change,
                on_bypass_toggle=on_bypass,
                on_remove_request=lambda i=idx: self._on_remove_effect(i)
            )
            self._pedal_widgets.append(pedal)
            self._layout.addWidget(pedal)

        add_btn = QPushButton('+')
        add_btn.setFixedSize(60, 180)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD}; color: {FG_MUTED};
                border: 2px dashed {BORDER_SUBTLE}; border-radius: 12px;
                font-size: 28px; font-weight: 300;
            }}
            QPushButton:hover {{
                background: {ACTIVE_BG}; color: {ACCENT};
                border-color: {ACCENT};
            }}
        """)
        add_btn.clicked.connect(lambda: self._on_add and self._on_add())
        self._layout.addWidget(add_btn)
        self._update_fade()

    def _on_remove_effect(self, idx):
        if self._on_remove:
            self._on_remove(idx)

    def refresh_all(self):
        for i in range(self._layout.count()):
            w = self._layout.itemAt(i).widget()
            if isinstance(w, PedalWidget):
                w.refresh()

    @property
    def pedal_widgets(self):
        return self._pedal_widgets

    def set_zoom(self, level):
        for pedal in self._pedal_widgets:
            pedal.setFixedWidth(int(PedalWidget.SHELL_W * level))
        self._layout.invalidate()

    def _update_fade(self):
        sb = self.horizontalScrollBar()
        self._edge_fade.show_edges(sb.value() > sb.minimum(), sb.value() < sb.maximum())

    def wheelEvent(self, event):
        sb = self.horizontalScrollBar()
        delta = event.angleDelta().y()
        if delta != 0:
            step = sb.singleStep() or 120
            sb.setValue(sb.value() - delta // 8 * step // 4)
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._edge_fade.setGeometry(self.viewport().rect())

    def eventFilter(self, obj, event):
        if obj == self.viewport() and event.type() == QEvent.Type.Resize:
            self._edge_fade.setGeometry(self.viewport().rect())
            self._update_fade()
        return super().eventFilter(obj, event)
