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
