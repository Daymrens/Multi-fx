from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QScrollArea, QCheckBox
import math

from .theme import *
from .knob import Knob


class EffectPanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._effect = None
        self._param_widgets = {}
        self._on_param_change = None
        self._on_bypass = None

        self.setWidgetResizable(True)
        self.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                background: {BG_DARK};
            }}
        """)

        self._container = QWidget()
        self._container.setStyleSheet(f'background: {BG_DARK};')
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(6)
        self.setWidget(self._container)

        self._show_empty()

    def _show_empty(self):
        for i in reversed(range(self._layout.count())):
            w = self._layout.itemAt(i).widget()
            if w:
                self._layout.removeWidget(w)
                w.deleteLater()
        lbl = QLabel('Select an effect to edit')
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f'color: {FG_DIM}; font-size: 12px; padding: 40px;')
        self._layout.addWidget(lbl)

    def set_effect(self, effect, index):
        self._effect = effect
        self._param_widgets = {}

        for i in reversed(range(self._layout.count())):
            w = self._layout.itemAt(i).widget()
            if w:
                self._layout.removeWidget(w)
                w.deleteLater()

        if effect is None:
            self._show_empty()
            return

        name = type(effect).__name__

        header = QHBoxLayout()
        title = QLabel(name)
        title.setStyleSheet(f'font-size: 15px; font-weight: 700; color: {FG}; font-family: Righteous, {FONT_FAMILY};')
        header.addWidget(title)

        bypass_cb = QCheckBox('Bypass')
        bypass_cb.setChecked(effect.bypass)
        bypass_cb.setStyleSheet(f'color: {FG_MUTED}; font-size: 11px;')
        bypass_cb.toggled.connect(lambda v: self._on_bypass_toggle(v))
        header.addStretch()
        header.addWidget(bypass_cb)
        self._layout.addLayout(header)

        if hasattr(effect, 'params'):
            param_info = effect.params()
            rows = []
            current_row = []
            for key, info in param_info.items():
                if 'options' in info:
                    w = self._build_dropdown(key, info, effect)
                elif isinstance(info.get('default'), bool):
                    w = self._build_checkbox(key, info, effect)
                else:
                    w = self._build_knob(key, info, effect)

                current_row.append(w)
                if len(current_row) >= 3:
                    rows.append(current_row)
                    current_row = []

            if current_row:
                rows.append(current_row)

            for row_widgets in rows:
                row = QHBoxLayout()
                row.setSpacing(8)
                for w in row_widgets:
                    row.addWidget(w)
                row.addStretch()
                self._layout.addLayout(row)

        self._layout.addStretch()

    def _build_knob(self, key, info, effect):
        default = info.get('default', 0)
        min_v = info.get('min', 0)
        max_v = info.get('max', 100)
        label = info.get('label', key)
        unit = info.get('unit', '')
        current = getattr(effect, key, default)

        knob = Knob(label=label, min_val=min_v, max_val=max_v, default=default, unit=unit)
        knob.set_value(current)
        knob.value_changed.connect(lambda v, k=key: self._param_changed(k, v))
        self._param_widgets[key] = knob
        return knob

    def _build_dropdown(self, key, info, effect):
        options = info.get('options', [])
        default = info.get('default', options[0] if options else '')
        current = getattr(effect, key, default)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        lbl = QLabel(info.get('label', key))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f'font-size: 10px; color: {FG_MUTED};')

        combo = QComboBox()
        for opt in options:
            display = str(opt)
            combo.addItem(display, opt)
        idx = combo.findData(current)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.currentIndexChanged.connect(lambda i, k=key, cb=combo: self._combo_changed(k, cb))
        container.setFixedWidth(80)
        layout.addWidget(lbl)
        layout.addWidget(combo)
        self._param_widgets[key] = combo
        return container

    def _build_checkbox(self, key, info, effect):
        current = getattr(effect, key, False)
        cb = QCheckBox(info.get('label', key))
        cb.setChecked(current)
        cb.setStyleSheet(f'color: {FG}; font-size: 11px;')
        cb.toggled.connect(lambda v, k=key: self._param_changed(k, v))
        self._param_widgets[key] = cb
        return cb

    def _param_changed(self, key, value):
        if self._effect and hasattr(self._effect, key):
            setattr(self._effect, key, value)
            self._effect.update()
            if self._on_param_change:
                self._on_param_change()

    def _combo_changed(self, key, combo):
        value = combo.currentData()
        self._param_changed(key, value)

    def _on_bypass_toggle(self, v):
        if self._effect:
            self._effect.bypass = v
            if self._on_bypass:
                self._on_bypass()

    def refresh_from_effect(self):
        if self._effect and hasattr(self._effect, 'params'):
            for key in self._effect.params():
                if key in self._param_widgets:
                    w = self._param_widgets[key]
                    v = getattr(self._effect, key)
                    if isinstance(w, Knob):
                        w.set_value(v)
                    elif isinstance(w, QComboBox):
                        idx = w.findData(v)
                        if idx >= 0:
                            w.setCurrentIndex(idx)
                    elif isinstance(w, QCheckBox):
                        w.setChecked(v)
