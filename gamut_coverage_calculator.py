import numpy as np

class Triangle:
    def __init__(self, a, b, c, d, e, f):
        self.ax, self.ay = a, b
        self.bx, self.by = c, d
        self.cx, self.cy = e, f

    # 向量化的重心座標法，判斷哪些點在三角形內
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

# 算出 BT2020 覆蓋點
bt_mask = BT2020.inside_mask(X, Y)
test_mask = test.inside_mask(X, Y)

# 覆蓋率計算
bt_total = np.sum(bt_mask)
bt_cover = np.sum(bt_mask & test_mask)

print('CIE 1931 BT2020覆蓋率')
print('%.1f%%' % (bt_cover / bt_total * 100))
