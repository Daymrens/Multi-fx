BG = '#0F0F23'
BG_MUTED = '#1A1A35'
BG_CARD = '#27273B'
BG_DARK = '#0A0A1A'
FG = '#F8FAFC'
FG_MUTED = '#94A3B8'
FG_DIM = '#64748B'
ACCENT = '#22C55E'
ACCENT_GLOW = 'rgba(34, 197, 94, 0.3)'
SECONDARY = '#4338CA'
BORDER = '#312E81'
BORDER_SUBTLE = '#1E1B4B'
DESTRUCTIVE = '#EF4444'
WARNING = '#F59E0B'
ACTIVE_BG = 'rgba(34, 197, 94, 0.15)'
KNOB_BG = '#1E1B4B'
KNOB_ACTIVE = '#22C55E'
KNOB_TRACK = '#312E81'
METER_BG = '#0A0A1A'
METER_LOW = '#22C55E'
METER_MID = '#F59E0B'
METER_HIGH = '#EF4444'

FONT_FAMILY = 'Poppins, Segoe UI, sans-serif'
FONT_MONO = 'JetBrains Mono, Consolas, monospace'

GRID = 8

class Spacing:
    XS = GRID // 2
    SM = GRID
    MD = GRID * 2
    LG = GRID * 3
    XL = GRID * 4

KNOB_DIAMETER = GRID * 6
CELL_W = GRID * 12
CELL_H = GRID * 12

PEDAL_SKINS = {
    'Gate': {
        'shell': '#5B7B6B',
        'shell_border': '#3D5246',
        'panel_style': 'framed',
        'accent': '#4CAF50',
        'led_active': '#4CAF50',
        'led_dim': '#1B3B1B',
    },
    'FilterEQ': {
        'shell': '#4A6B8A',
        'shell_border': '#334A60',
        'panel_style': 'framed',
        'accent': '#42A5F5',
        'led_active': '#42A5F5',
        'led_dim': '#1A3050',
    },
    'Compressor': {
        'shell': '#C47A3A',
        'shell_border': '#8A5528',
        'panel_style': 'framed',
        'accent': '#FFA726',
        'led_active': '#FFA726',
        'led_dim': '#4A2A10',
    },
    'Distortion': {
        'shell': '#8A3A3A',
        'shell_border': '#5C2626',
        'panel_style': 'flush',
        'accent': '#EF5350',
        'led_active': '#EF5350',
        'led_dim': '#3A1010',
    },
    'Modulation': {
        'shell': '#6A4A8A',
        'shell_border': '#48305E',
        'panel_style': 'framed',
        'accent': '#AB47BC',
        'led_active': '#AB47BC',
        'led_dim': '#2A1040',
    },
    'Delay': {
        'shell': '#3A7A7A',
        'shell_border': '#265050',
        'panel_style': 'flush',
        'accent': '#26C6DA',
        'led_active': '#26C6DA',
        'led_dim': '#103040',
    },
    'Reverb': {
        'shell': '#8A5A6A',
        'shell_border': '#5E3A48',
        'panel_style': 'framed',
        'accent': '#EC407A',
        'led_active': '#EC407A',
        'led_dim': '#3A1020',
    },
    'Limiter': {
        'shell': '#9A6A3A',
        'shell_border': '#6A4828',
        'panel_style': 'flush',
        'accent': '#FF7043',
        'led_active': '#FF7043',
        'led_dim': '#4A2010',
    },
}

PANEL_BG = '#1E1E24'
PANEL_BORDER = '#3A3A44'
PANEL_FRAME = '#4A4A54'
FOOTSWITCH_BG = '#D4D0C8'
FOOTSWITCH_BASE = '#8A8678'
FOOTSWITCH_SHADOW = '#5A5850'
KNOB_BODY = '#2A2A32'
KNOB_SHADOW = '#0A0A0E'
KNOB_INDICATOR = '#E8E8F0'
READOUT_BG = '#0A0A0E'
READOUT_BORDER = '#3A3A44'
CLIP = '#FF1744'
ARROW_FADED = '#3A3A50'

STYLESHEET = f"""
QMainWindow {{
    background-color: {BG};
    color: {FG};
    font-family: {FONT_FAMILY};
}}
QWidget {{
    background-color: transparent;
    color: {FG};
    font-family: {FONT_FAMILY};
}}
QLabel {{
    color: {FG};
    font-size: 11px;
}}
QLabel[heading="true"] {{
    font-size: 14px;
    font-weight: 600;
    color: {FG};
}}
QLabel[small="true"] {{
    font-size: 10px;
    color: {FG_MUTED};
}}
QPushButton {{
    background-color: {BG_CARD};
    color: {FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {SECONDARY};
    border-color: {SECONDARY};
}}
QPushButton:pressed {{
    background-color: {ACTIVE_BG};
}}
QPushButton[accent="true"] {{
    background-color: {ACCENT};
    color: {BG};
    border: none;
    font-weight: 600;
}}
QPushButton[accent="true"]:hover {{
    background-color: #16A34A;
}}
QPushButton[danger="true"] {{
    color: {DESTRUCTIVE};
    border-color: {DESTRUCTIVE};
}}
QPushButton[danger="true"]:hover {{
    background-color: rgba(239, 68, 68, 0.15);
}}
QComboBox {{
    background-color: {BG_CARD};
    color: {FG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    min-height: 24px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {FG};
    border: 1px solid {BORDER};
    selection-background-color: {SECONDARY};
}}
QScrollBar:vertical {{
    background: {BG};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BG_CARD};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BORDER};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QFrame {{
    border: none;
}}
"""
