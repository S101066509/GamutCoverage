# Triangle Gamut Coverage Calculator

本計算器使用 Python 與 numpy，實作色域三角形的重心座標法（Barycentric coordinate）  
快速計算兩個三角形色域的覆蓋率。  

---

## 功能介紹

- 定義任意三角形色域（以三個頂點 xy 座標）
- 使用**重心座標法**向量化判斷點是否在三角形內
- 批量計算一個色域（如 BT2020）被另一個色域覆蓋的百分比
- 可自訂網格解析度，兼顧速度與精度

---

## 安裝方式

1. 複製本專案或下載檔案至本地資料夾
2. 建議使用虛擬環境（venv/myenv）
3. 安裝 numpy 套件
    ```bash
    pip install numpy
    ```

---

## 使用方法

1. 編輯 `Triangle` 物件，輸入三角形三個頂點的 xy 座標
2. 執行主程式即可得到覆蓋率

### 範例程式

```python
import numpy as np

class Triangle:
    def __init__(self, a, b, c, d, e, f):
        self.ax, self.ay = a, b
        self.bx, self.by = c, d
        self.cx, self.cy = e, f

    # 向量化重心座標法
    def inside_mask(self, X, Y):
        x1, y1 = self.ax, self.ay
        x2, y2 = self.bx, self.by
        x3, y3 = self.cx, self.cy

        denominator = ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
        u = ((y2 - y3)*(X - x3) + (x3 - x2)*(Y - y3)) / denominator
        v = ((y3 - y1)*(X - x3) + (x1 - x3)*(Y - y3)) / denominator
        w = 1 - u - v
        return (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1) & (w >= 0) & (w <= 1)

# 定義三角形
BT2020 = Triangle(0.708,0.292, 0.17,0.797, 0.131,0.046)
test = Triangle(0.6935,0.3063, 0.2919,0.6679, 0.1556,0.0198)

# 設定解析度
O1, O2 = 1000, 1000
xs = np.linspace(0, 1, O1)
ys = np.linspace(0, 1, O2)
X, Y = np.meshgrid(xs, ys)

# 計算覆蓋
bt_mask = BT2020.inside_mask(X, Y)
test_mask = test.inside_mask(X, Y)

bt_total = np.sum(bt_mask)
bt_cover = np.sum(bt_mask & test_mask)

print('CIE 1931 BT2020覆蓋率')
print('%.1f%%' % (bt_cover / bt_total * 100))
