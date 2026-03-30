# --- 介面樣式表 ---
DARK_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
}
QGroupBox {
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 8px;
    margin-top: 15px;
    font-weight: bold;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLabel {
    color: #dddddd;
}
QLineEdit {
    background-color: #3b3b3b;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 2px 5px;
}
QLineEdit[readOnly="true"] {
    background-color: #2d2d2d;
    color: #aaaaaa;
}
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
QComboBox {
    background-color: #3b3b3b;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px;
}
"""

# D65 標準白點座標
D65_WHITE = (0.3127, 0.3290)
