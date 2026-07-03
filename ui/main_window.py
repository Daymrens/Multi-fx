from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QSlider, QFileDialog, QMessageBox, QFrame
)
from pathlib import Path
import numpy as np

from .theme import *
from .chain_view import ChainView
from .effect_panel import EffectPanel

from dsp.chain import EffectChain, get_effect_names
from dsp import EffectChain
from audio_engine import AudioEngine
from preset_manager import save_preset, load_preset, list_presets, init_factory_presets


class _MiniMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._peak = 0.0
        self.setFixedSize(4, 28)

    def set_peak(self, p):
        self._peak = p
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(METER_BG))
        painter.drawRoundedRect(0, 0, w, h, 1, 1)
        if self._peak > 0:
            db = max(-60, 20 * np.log10(max(self._peak, 1e-10)))
            ratio = max(0, min(1, (db + 60) / 60))
            fill_h = max(1, int(ratio * h))
            c = METER_LOW if ratio < 0.6 else METER_MID if ratio < 0.85 else METER_HIGH
            painter.setBrush(QColor(c))
            painter.drawRoundedRect(0, h - fill_h, w, fill_h, 1, 1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Multi-FX')
        self.setMinimumSize(680, 380)
        self.resize(680, 400)
        self.setStyleSheet(STYLESHEET)

        self.chain = EffectChain(44100)
        self.engine = AudioEngine(self.chain)
        self._selected_effect = -1

        init_factory_presets()
        self._build_ui()
        self._setup_timers()
        self._load_default_chain()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        header = self._build_header()
        layout.addLayout(header)

        self.chain_view = ChainView()
        self.chain_view._on_select = self._on_effect_selected
        self.chain_view._on_toggle_bypass = self._on_toggle_bypass
        self.chain_view._on_remove = self._on_remove_effect
        self.chain_view._on_ensure_visible = self._ensure_pedal_visible
        layout.addWidget(self.chain_view)

        io_panel = self._build_io_panel()
        layout.addWidget(io_panel)

        self.effect_panel = EffectPanel()
        layout.addWidget(self.effect_panel, 1)

        self.buf_slider.valueChanged.connect(self._on_buffer_changed)
        self.direct_mon.toggled.connect(self._on_direct_monitor_toggled)

        footer = self._build_footer()
        layout.addLayout(footer)

    def _build_header(self):
        h = QHBoxLayout()
        title = QLabel('Multi-FX')
        title.setStyleSheet(f'font-size: 18px; font-weight: 700; color: {ACCENT}; font-family: Righteous, {FONT_FAMILY};')
        h.addWidget(title)

        h.addStretch()

        self.add_combo = QComboBox()
        self.add_combo.setStyleSheet(f'font-size: 11px; min-width: 120px;')
        self.add_combo.addItem('+ Add Effect')
        for name in get_effect_names():
            self.add_combo.addItem(name)
        self.add_combo.currentIndexChanged.connect(self._on_add_effect)
        h.addWidget(self.add_combo)

        self.zoom_combo = QComboBox()
        self.zoom_combo.setStyleSheet(f'font-size: 10px; min-width: 64px;')
        self.zoom_combo.addItems(['100%', '85%', '70%'])
        self.zoom_combo.currentIndexChanged.connect(self._on_zoom_changed)
        h.addWidget(self.zoom_combo)

        self.status_label = QLabel('Stopped')
        self.status_label.setStyleSheet(f'color: {FG_DIM}; font-size: 10px; font-family: {FONT_MONO};')
        h.addWidget(self.status_label)

        return h

    def _build_io_panel(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_DARK};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(10, 6, 10, 6)
        vbox.setSpacing(4)

        row0 = QHBoxLayout()
        row0.setSpacing(8)

        in_lbl = QLabel('IN')
        in_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-weight: 600;')
        row0.addWidget(in_lbl)

        self._in_mm = _MiniMeter()
        row0.addWidget(self._in_mm)

        self.in_dev = QComboBox()
        self.in_dev.setStyleSheet(f'font-size: 10px; min-width: 160px;')
        row0.addWidget(self.in_dev)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f'background: {BORDER_SUBTLE}; max-width: 1px;')
        row0.addWidget(sep)

        out_lbl = QLabel('OUT')
        out_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-weight: 600;')
        row0.addWidget(out_lbl)

        self._out_mm = _MiniMeter()
        row0.addWidget(self._out_mm)

        self.out_dev = QComboBox()
        self.out_dev.setStyleSheet(f'font-size: 10px; min-width: 160px;')
        row0.addWidget(self.out_dev)

        row0.addStretch()
        vbox.addLayout(row0)

        row1 = QHBoxLayout()
        row1.setSpacing(6)

        buf_lbl = QLabel('Buffer')
        buf_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-weight: 600;')
        row1.addWidget(buf_lbl)

        self.buf_slider = QSlider(Qt.Orientation.Horizontal)
        self.buf_slider.setRange(64, 1024)
        self.buf_slider.setValue(128)
        self.buf_slider.setSingleStep(32)
        self.buf_slider.setPageStep(128)
        self.buf_slider.setFixedWidth(120)
        self.buf_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {BORDER_SUBTLE}; height: 4px; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {ACCENT}; width: 12px; height: 12px;
                margin: -4px 0; border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT}; border-radius: 2px;
            }}
        """)
        row1.addWidget(self.buf_slider)

        self._buf_label = QLabel('128 (2.9ms)')
        self._buf_label.setStyleSheet(f'font-size: 10px; color: {FG_MUTED}; font-family: {FONT_MONO};')
        row1.addWidget(self._buf_label)

        self._sr_label = QLabel('44.1kHz')
        self._sr_label.setStyleSheet(f'font-size: 10px; color: {FG_DIM}; font-family: {FONT_MONO};')
        row1.addWidget(self._sr_label)

        row1.addStretch()

        dm_lbl = QLabel('DM')
        dm_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-weight: 600;')
        row1.addWidget(dm_lbl)

        self.direct_mon = QCheckBox()
        self.direct_mon.setStyleSheet(f'font-size: 12px; color: {FG};')
        row1.addWidget(self.direct_mon)

        route_lbl = QLabel('Route')
        route_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-weight: 600;')
        row1.addWidget(route_lbl)

        self.route_combo = QComboBox()
        self.route_combo.addItems(['Direct', 'Loopback', 'Split'])
        self.route_combo.setStyleSheet(f'font-size: 10px; min-width: 80px;')
        row1.addWidget(self.route_combo)

        vbox.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self._clip_label = QLabel('Clip: OFF')
        self._clip_label.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-family: {FONT_MONO};')
        row2.addWidget(self._clip_label)

        self._latency_label = QLabel('2.9ms buf | 12ms rt')
        self._latency_label.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-family: {FONT_MONO};')
        row2.addWidget(self._latency_label)

        row2.addStretch()

        status_lbl = QLabel('Ready')
        status_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM};')
        self._status_io = status_lbl
        row2.addWidget(status_lbl)

        vbox.addLayout(row2)

        self._populate_devices()
        self.in_dev.currentIndexChanged.connect(self._on_device_changed)
        self.out_dev.currentIndexChanged.connect(self._on_device_changed)

        return frame

    def _build_footer(self):
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self.start_btn = QPushButton('Start')
        self.start_btn.setStyleSheet(f'background: {ACCENT}; color: {BG}; font-weight: 700; padding: 8px 20px; border: none; border-radius: 6px;')
        self.start_btn.clicked.connect(self._toggle_audio)
        layout.addWidget(self.start_btn)

        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet(f'font-size: 11px; min-width: 140px;')
        self.preset_combo.addItem('Load Preset...')
        for p in list_presets():
            self.preset_combo.addItem(p['name'], p['path'])
        self.preset_combo.currentIndexChanged.connect(self._on_load_preset)
        layout.addWidget(self.preset_combo)

        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self._on_save_preset)
        layout.addWidget(save_btn)

        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self._on_clear_chain)
        layout.addWidget(clear_btn)

        layout.addStretch()

        return layout

    def _populate_devices(self):
        self.in_dev.clear()
        self.out_dev.clear()
        devices = self.engine.get_devices()
        default_in = None
        default_out = None
        for dev in devices:
            ha = dev['hostapi']
            label = f"[{ha}] {dev['name']}"
            if dev['inputs'] > 0:
                self.in_dev.addItem(label, dev['id'])
                if 'ASIO' in ha or 'FL Studio' in dev['name']:
                    default_in = self.in_dev.count() - 1
            if dev['outputs'] > 0:
                self.out_dev.addItem(label, dev['id'])
                if 'ASIO' in ha or 'FL Studio' in dev['name']:
                    default_out = self.out_dev.count() - 1

        if default_in is not None:
            self.in_dev.setCurrentIndex(default_in)
        if default_out is not None:
            self.out_dev.setCurrentIndex(default_out)

    def _on_device_changed(self):
        if self.engine.is_running:
            self.engine.restart()

    def _on_buffer_changed(self, val):
        self.engine.blocksize = val
        buf_ms = val / self.engine.sample_rate * 1000
        self._buf_label.setText(f'{val} ({buf_ms:.1f}ms)')

    def _on_direct_monitor_toggled(self, checked):
        self.engine.direct_monitor = checked

    def _setup_timers(self):
        self._meter_timer = QTimer(self)
        self._meter_timer.timeout.connect(self._update_meters)
        self._meter_timer.start(40)

    def _load_default_chain(self):
        self.chain = EffectChain(44100)
        self.engine.chain = self.chain
        self.chain.add('Gate')
        self.chain.add('FilterEQ')
        self.chain.add('Compressor')
        self.chain.add('Delay')
        self.chain.add('Limiter')
        self._refresh_chain_view()

    def _refresh_chain_view(self):
        names = [type(e).__name__ for e in self.chain.effects]
        bypasses = [e.bypass for e in self.chain.effects]
        self.chain_view.set_effects(names, bypasses)
        self._rebuild_pedalboard()
        if self.chain.effects and self._selected_effect < 0:
            self._on_effect_selected(0)
        elif self._selected_effect >= len(self.chain.effects):
            self._selected_effect = len(self.chain.effects) - 1
            if self._selected_effect >= 0:
                self._on_effect_selected(self._selected_effect)

    def _rebuild_pedalboard(self):
        self.effect_panel.set_effects(
            self.chain.effects,
            on_param_change=self._on_params_changed,
            on_bypass=self._update_chain_view,
            on_remove=self._on_remove_effect,
            on_add=self._on_add_requested
        )

    def _on_add_requested(self):
        self.add_combo.showPopup()

    def _on_add_effect(self, idx):
        if idx <= 0:
            return
        name = self.add_combo.currentText()
        pos = self._selected_effect + 1 if self._selected_effect >= 0 else None
        effect = self.chain.add(name, pos)
        if effect:
            self._refresh_chain_view()
            self._on_effect_selected(pos if pos is not None else len(self.chain.effects) - 1)
        self.add_combo.setCurrentIndex(0)

    def _on_effect_selected(self, idx):
        if 0 <= idx < len(self.chain.effects):
            self._selected_effect = idx
            self.chain_view.select(idx)

    def _on_toggle_bypass(self, idx):
        if 0 <= idx < len(self.chain.effects):
            e = self.chain.effects[idx]
            e.bypass = not e.bypass
            self._refresh_chain_view()

    def _on_remove_effect(self, idx):
        if 0 <= idx < len(self.chain.effects):
            self.chain.remove(idx)
            self._refresh_chain_view()

    def _on_params_changed(self):
        self.effect_panel.refresh_all()

    def _update_chain_view(self):
        if self._selected_effect >= 0 and self._selected_effect < len(self.chain.effects):
            self.chain_view.select(self._selected_effect)

    def _toggle_audio(self):
        if self.engine.is_running:
            self.engine.stop()
            self.start_btn.setText('Start')
            self.start_btn.setStyleSheet(f'background: {ACCENT}; color: {BG}; font-weight: 700; padding: 8px 20px; border: none; border-radius: 6px;')
            self.status_label.setText('Stopped')
        else:
            try:
                in_idx = self.in_dev.currentData()
                out_idx = self.out_dev.currentData()
                self.engine.input_device = in_idx
                self.engine.output_device = out_idx
                self.engine.start()
                self.start_btn.setText('Stop')
                self.start_btn.setStyleSheet(f'background: {DESTRUCTIVE}; color: {FG}; font-weight: 700; padding: 8px 20px; border: none; border-radius: 6px;')
                self.status_label.setText('Running')
            except Exception as e:
                QMessageBox.critical(self, 'Audio Error', str(e))

    def _update_meters(self):
        if self.engine.is_running:
            self._in_mm.set_peak(self.engine.peak_in)
            self._out_mm.set_peak(self.engine.peak_out)
            rt = self.engine.latency_ms
            buf = self.engine.buffer_ms
            self._latency_label.setText(f'{buf:.1f}ms buf | {rt:.1f}ms rt')
            if self.engine.peak_in > 0.99 or self.engine.peak_out > 0.99:
                self._clip_label.setText('Clip: ON')
                self._clip_label.setStyleSheet(f'font-size: 9px; color: {CLIP}; font-weight: 700; font-family: {FONT_MONO};')
            if max(self.engine.peak_in, self.engine.peak_out) < 0.5:
                self._clip_label.setText('Clip: OFF')
                self._clip_label.setStyleSheet(f'font-size: 9px; color: {FG_DIM}; font-family: {FONT_MONO};')
            self.engine._peak_in = 0.0
            self.engine._peak_out = 0.0

    def _on_load_preset(self, idx):
        if idx <= 0:
            return
        path = self.preset_combo.currentData()
        if path:
            try:
                data = load_preset(path)
                self.chain = EffectChain(44100)
                self.engine.chain = self.chain
                self.chain.from_dict(data.get('chain', []))
                self._selected_effect = -1
                self._refresh_chain_view()
            except Exception as e:
                QMessageBox.warning(self, 'Preset Error', str(e))
        self.preset_combo.setCurrentIndex(0)

    def _on_save_preset(self):
        name, ok = QFileDialog.getSaveFileName(
            self, 'Save Preset', str(Path.home() / 'Desktop'), 'JSON (*.json)'
        )
        if name:
            chain_data = self.chain.to_dict()
            save_preset(Path(name).stem, chain_data)
            self.preset_combo.addItem(Path(name).stem, name)

    def _on_clear_chain(self):
        self.chain = EffectChain(44100)
        self.engine.chain = self.chain
        self._selected_effect = -1
        self._refresh_chain_view()

    def _ensure_pedal_visible(self, idx):
        pw = self.effect_panel.pedal_widgets
        if 0 <= idx < len(pw):
            self.effect_panel.ensureWidgetVisible(pw[idx])

    def _on_zoom_changed(self, idx):
        levels = [1.0, 0.85, 0.70]
        self.effect_panel.set_zoom(levels[idx])

    def closeEvent(self, event):
        self.engine.stop()
        super().closeEvent(event)
