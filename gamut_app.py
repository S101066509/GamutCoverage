import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QGridLayout, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

# 引入核心計算模組與配置
from cal import Triangle, calculate_coverage
from config import DARK_STYLE, D65_WHITE

def load_cie_data(filepath):
    """
    從 CSV 檔案讀取 CIE XYZ 數據並轉換為 xy 座標。
    """
    locus_x = []
    locus_y = []
    wavelengths = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 4: continue
                try:
                    w = float(row[0])
                    X = float(row[1])
                    Y = float(row[2])
                    Z = float(row[3])
                    total = X + Y + Z
                    if total > 0:
                        locus_x.append(X / total)
                        locus_y.append(Y / total)
                        wavelengths.append(w)
                except ValueError:
                    continue
        # 封閉光譜軌跡（連接首尾形成封閉圖形）
        if locus_x:
            locus_x.append(locus_x[0])
            locus_y.append(locus_y[0])
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {filepath}")
    return np.array(locus_x), np.array(locus_y), np.array(wavelengths)

# 全域載入 CIE 光譜數據
SPECTRAL_LOCUS_X, SPECTRAL_LOCUS_Y, WAVELENGTHS = load_cie_data('CIE_xyz_1931_2deg.csv')

# 常見色域標準預設值
STANDARDS = {
    "BT.709 / sRGB": [(0.640, 0.330), (0.300, 0.600), (0.150, 0.060)],
    "DCI-P3": [(0.680, 0.320), (0.265, 0.690), (0.150, 0.060)],
    "BT.2020": [(0.708, 0.292), (0.170, 0.797), (0.131, 0.046)],
    "NTSC (CIE 1953)": [(0.670, 0.330), (0.210, 0.710), (0.140, 0.080)],
    "Adobe RGB": [(0.640, 0.330), (0.210, 0.710), (0.150, 0.060)],
}

class GamutApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("專業色域覆蓋率分析工具")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(DARK_STYLE)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(main_widget)

        # 左側控制面板
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel, 1)

        # --- 標準色域選擇 ---
        std_group = QGroupBox("參考標準設定")
        std_layout = QVBoxLayout(std_group)
        self.std_combo = QComboBox()
        self.std_combo.addItems(STANDARDS.keys())
        self.std_combo.currentIndexChanged.connect(self.on_std_changed)
        std_layout.addWidget(QLabel("選擇基準色域 (Reference):"))
        std_layout.addWidget(self.std_combo)
        left_panel.addWidget(std_group)

        # --- 參考座標顯示 (唯讀) ---
        ref_group = QGroupBox("參考標準基色座標")
        ref_grid = QGridLayout(ref_group)
        self.ref_inputs = {}
        for i, color in enumerate(['Red', 'Green', 'Blue']):
            ref_grid.addWidget(QLabel(f"{color} x:"), i, 0)
            self.ref_inputs[f'{color}_x'] = QLineEdit()
            self.ref_inputs[f'{color}_x'].setReadOnly(True)
            ref_grid.addWidget(self.ref_inputs[f'{color}_x'], i, 1)
            ref_grid.addWidget(QLabel(f"y:"), i, 2)
            self.ref_inputs[f'{color}_y'] = QLineEdit()
            self.ref_inputs[f'{color}_y'].setReadOnly(True)
            ref_grid.addWidget(self.ref_inputs[f'{color}_y'], i, 3)
        left_panel.addWidget(ref_group)

        # --- 測試色域輸入 (自定義) ---
        test_group = QGroupBox("測試/實測基色座標")
        test_grid = QGridLayout(test_group)
        self.test_inputs = {}
        # 預設使用 BT.2020 座標作為起點
        init_vals = [0.708, 0.292, 0.170, 0.797, 0.131, 0.046]
        for i, color in enumerate(['Red', 'Green', 'Blue']):
            test_grid.addWidget(QLabel(f"{color} x:"), i, 0)
            self.test_inputs[f'{color}_x'] = QLineEdit(str(init_vals[i*2]))
            test_grid.addWidget(self.test_inputs[f'{color}_x'], i, 1)
            test_grid.addWidget(QLabel(f"y:"), i, 2)
            self.test_inputs[f'{color}_y'] = QLineEdit(str(init_vals[i*2+1]))
            test_grid.addWidget(self.test_inputs[f'{color}_y'], i, 3)
        
        self.apply_btn = QPushButton("執行運算並更新圖表")
        self.apply_btn.setFixedHeight(45)
        self.apply_btn.clicked.connect(self.calculate)
        test_grid.addWidget(self.apply_btn, 3, 0, 1, 4)
        left_panel.addWidget(test_group)

        # --- 數據結果 ---
        res_group = QGroupBox("分析統計")
        res_layout = QVBoxLayout(res_group)
        self.result_label = QLabel("覆蓋率: -%")
        self.result_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #00ff88; margin: 10px 0;")
        self.result_label.setAlignment(Qt.AlignCenter)
        res_layout.addWidget(self.result_label)
        left_panel.addWidget(res_group)
        left_panel.addStretch()

        # 右側繪圖區域
        plt.style.use('dark_background')
        self.figure, self.ax = plt.subplots(figsize=(8, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color:transparent;")
        main_layout.addWidget(self.canvas, 3)

        self.on_std_changed(0)
        self.calculate()

    def on_std_changed(self, index):
        """當下拉選單切換時，更新參考座標。"""
        std_name = self.std_combo.currentText()
        coords = STANDARDS[std_name]
        for i, color in enumerate(['Red', 'Green', 'Blue']):
            self.ref_inputs[f'{color}_x'].setText(str(coords[i][0]))
            self.ref_inputs[f'{color}_y'].setText(str(coords[i][1]))
        self.calculate()

    def calculate(self):
        """讀取 GUI 輸入，調用核心模組運算並繪圖。"""
        try:
            ref_pts = [ (float(self.ref_inputs[f'{c}_x'].text()), float(self.ref_inputs[f'{c}_y'].text())) for c in ['Red', 'Green', 'Blue'] ]
            test_pts = [ (float(self.test_inputs[f'{c}_x'].text()), float(self.test_inputs[f'{c}_y'].text())) for c in ['Red', 'Green', 'Blue'] ]
            
            # 使用靈活的 *args 建立 Triangle 物件
            ref_tri = Triangle(*ref_pts)
            test_tri = Triangle(*test_pts)

            # 調用 cal.py 中的模組化函數計算覆蓋率
            coverage = calculate_coverage(ref_tri, test_tri, resolution=500)
            self.result_label.setText(f"覆蓋率: {coverage:.2f}%")

            self.update_plot(ref_pts, test_pts)
        except ValueError:
            self.result_label.setText("輸入錯誤！")

    def update_plot(self, ref_pts, test_pts):
        """重新繪製 CIE 1931 色度圖與色域三角形。"""
        self.ax.clear()
        
        # 繪製 CIE 1931 背景光譜軌跡
        if len(SPECTRAL_LOCUS_X) > 0:
            self.ax.plot(SPECTRAL_LOCUS_X, SPECTRAL_LOCUS_Y, color='#ffffff', alpha=0.4, linewidth=1.5, label='CIE 1931 光譜軌跡')
            self.ax.fill(SPECTRAL_LOCUS_X, SPECTRAL_LOCUS_Y, color='#ffffff', alpha=0.04)

        # 標註 D65 白點
        self.ax.scatter(D65_WHITE[0], D65_WHITE[1], color='white', marker='+', s=100, linewidth=1, label='D65 白點', zorder=5)

        # 繪製參考標準三角形
        rx, ry = zip(*(ref_pts + [ref_pts[0]]))
        self.ax.plot(rx, ry, color='#ff3e3e', linestyle='--', linewidth=1.5, label='參考標準色域')
        self.ax.fill(rx, ry, color='#ff3e3e', alpha=0.1)

        # 繪製實測/測試色域三角形
        tx, ty = zip(*(test_pts + [test_pts[0]]))
        self.ax.plot(tx, ty, color='#00d1ff', linestyle='-', linewidth=2.5, label='實測/來源色域')
        self.ax.fill(tx, ty, color='#00d1ff', alpha=0.2)

        # 加入頂點標示
        for p in ref_pts: self.ax.scatter(*p, color='#ff3e3e', s=40, edgecolors='white', zorder=10)
        for p in test_pts: self.ax.scatter(*p, color='#00d1ff', s=50, edgecolors='white', zorder=10)

        # 設定座標軸樣式
        self.ax.set_xlim(-0.05, 0.85)
        self.ax.set_ylim(-0.05, 0.95)
        self.ax.set_xlabel('CIE x', color='#aaaaaa', fontweight='bold')
        self.ax.set_ylabel('CIE y', color='#aaaaaa', fontweight='bold')
        self.ax.tick_params(colors='#777777')
        self.ax.grid(True, linestyle=':', alpha=0.15)
        
        self.ax.legend(facecolor='#1e1e1e', edgecolor='#333333', fontsize=9, loc='upper right')
        self.ax.set_title("色域覆蓋率分析可視化", color='white', pad=25, fontdict={'fontsize': 16, 'fontweight': 'bold'})
        
        # 在光譜軌跡上標註特定波長位置
        if len(WAVELENGTHS) > 0:
            for wl, color in [(460, '#aaaaff'), (520, '#aaffaa'), (700, '#ffaaaa')]:
                idx = np.abs(WAVELENGTHS - wl).argmin()
                self.ax.text(SPECTRAL_LOCUS_X[idx], SPECTRAL_LOCUS_Y[idx], f' {wl}nm', color=color, fontsize=8)

        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamutApp()
    window.show()
    sys.exit(app.exec())
