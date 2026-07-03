from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFileDialog, QMessageBox, QFrame, QSplitter
)
from pathlib import Path

from .theme import *
from .chain_view import ChainView
from .effect_panel import EffectPanel
from .meter import Meter
from dsp.chain import EffectChain, get_effect_names
from dsp import EffectChain
from audio_engine import AudioEngine
from preset_manager import save_preset, load_preset, list_presets, init_factory_presets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Multi-FX')
        self.setMinimumSize(900, 500)
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
        layout.addWidget(self.chain_view)

        self.effect_panel = EffectPanel()
        self.effect_panel._on_param_change = self._on_params_changed
        self.effect_panel._on_bypass = self._update_chain_view
        layout.addWidget(self.effect_panel, 1)

        meters = self._build_meters()
        layout.addLayout(meters)

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

        self.status_label = QLabel('Stopped')
        self.status_label.setStyleSheet(f'color: {FG_DIM}; font-size: 10px; font-family: {FONT_MONO};')
        h.addWidget(self.status_label)

        return h

    def _build_meters(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.in_meter = Meter('IN')
        self.out_meter = Meter('OUT')

        meter_frame = QFrame()
        meter_frame.setStyleSheet(f'background: {BG_DARK}; border: 1px solid {BORDER}; border-radius: 6px;')
        m_layout = QHBoxLayout(meter_frame)
        m_layout.setContentsMargins(8, 4, 8, 4)
        m_layout.addWidget(QLabel('IN'))
        m_layout.addWidget(self.in_meter)
        m_layout.addWidget(QLabel('OUT'))
        m_layout.addWidget(self.out_meter)

        layout.addWidget(meter_frame)
        layout.addStretch()

        # Device selection
        dev_frame = QFrame()
        dev_frame.setStyleSheet(f'background: {BG_DARK}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px;')
        d_layout = QVBoxLayout(dev_frame)
        d_layout.setContentsMargins(8, 4, 8, 4)
        d_layout.setSpacing(2)

        in_lbl = QLabel('Input')
        in_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM};')
        self.in_dev = QComboBox()
        self.in_dev.setStyleSheet(f'font-size: 10px; min-width: 160px;')
        d_layout.addWidget(in_lbl)
        d_layout.addWidget(self.in_dev)

        out_lbl = QLabel('Output')
        out_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM};')
        self.out_dev = QComboBox()
        self.out_dev.setStyleSheet(f'font-size: 10px; min-width: 160px;')
        d_layout.addWidget(out_lbl)
        d_layout.addWidget(self.out_dev)

        self._populate_devices()
        self.in_dev.currentIndexChanged.connect(self._on_device_changed)
        self.out_dev.currentIndexChanged.connect(self._on_device_changed)

        layout.addWidget(dev_frame)

        # Routing
        route_frame = QFrame()
        route_frame.setStyleSheet(f'background: {BG_DARK}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px;')
        r_layout = QVBoxLayout(route_frame)
        r_layout.setContentsMargins(8, 4, 8, 4)
        r_layout.setSpacing(2)

        route_lbl = QLabel('Routing')
        route_lbl.setStyleSheet(f'font-size: 9px; color: {FG_DIM};')
        self.route_combo = QComboBox()
        self.route_combo.addItems(['Direct', 'Loopback', 'Split'])
        self.route_combo.setStyleSheet(f'font-size: 10px;')
        r_layout.addWidget(route_lbl)
        r_layout.addWidget(self.route_combo)

        layout.addWidget(route_frame)

        return layout

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

        self.latency_label = QLabel('2.9ms')
        self.latency_label.setStyleSheet(f'color: {FG_DIM}; font-size: 10px; font-family: {FONT_MONO};')
        layout.addWidget(self.latency_label)

        return layout

    def _populate_devices(self):
        self.in_dev.clear()
        self.out_dev.clear()
        devices = self.engine.get_devices()
        default_in = None
        default_out = None
        for dev in devices:
            label = f"{dev['id']}: {dev['name']}"
            if dev['inputs'] > 0:
                self.in_dev.addItem(label, dev['id'])
                if 'ASIO' in dev['name'] or 'FL Studio' in dev['name']:
                    default_in = self.in_dev.count() - 1
            if dev['outputs'] > 0:
                self.out_dev.addItem(label, dev['id'])
                if 'ASIO' in dev['name'] or 'FL Studio' in dev['name']:
                    default_out = self.out_dev.count() - 1

        if default_in is not None:
            self.in_dev.setCurrentIndex(default_in)
        if default_out is not None:
            self.out_dev.setCurrentIndex(default_out)

    def _on_device_changed(self):
        if self.engine.is_running:
            self._toggle_audio()

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
        if self.chain.effects and self._selected_effect < 0:
            self._on_effect_selected(0)
        elif self._selected_effect >= len(self.chain.effects):
            self._selected_effect = len(self.chain.effects) - 1
            if self._selected_effect >= 0:
                self._on_effect_selected(self._selected_effect)
            else:
                self.effect_panel.set_effect(None, -1)

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
            self.effect_panel.set_effect(self.chain.effects[idx], idx)

    def _on_toggle_bypass(self, idx):
        if 0 <= idx < len(self.chain.effects):
            e = self.chain.effects[idx]
            e.bypass = not e.bypass
            self._refresh_chain_view()
            if idx == self._selected_effect:
                self.effect_panel.set_effect(e, idx)

    def _on_remove_effect(self, idx):
        if 0 <= idx < len(self.chain.effects):
            self.chain.remove(idx)
            self._refresh_chain_view()

    def _on_params_changed(self):
        self._update_chain_view()

    def _update_chain_view(self):
        if self._selected_effect >= 0 and self._selected_effect < len(self.chain.effects):
            self.chain_view.select(self._selected_effect)
            self.effect_panel.refresh_from_effect()

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
            self.in_meter.set_peak(self.engine.peak_in)
            self.out_meter.set_peak(self.engine.peak_out)
            self.latency_label.setText(f'{self.engine.latency_ms:.1f}ms')
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

    def closeEvent(self, event):
        self.engine.stop()
        super().closeEvent(event)
