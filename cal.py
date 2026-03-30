import numpy as np

class Triangle:
    """
    用於表示 2D 空間中的三角形，通常用於定義色域邊界。
    """
    def __init__(self, *para):
        """
        初始化三角形。支援以下方式傳入：
        - Triangle(ax, ay, bx, by, cx, cy)
        - Triangle((ax, ay), (bx, by), (cx, cy))
        """
        if len(para) == 6:
            self.ax, self.ay, self.bx, self.by, self.cx, self.cy = para
        elif len(para) == 3:
            (self.ax, self.ay), (self.bx, self.by), (self.cx, self.cy) = para
        else:
            raise ValueError("三角形需要 6 個獨立座標或 3 組座標對。")

    def inside_mask(self, X, Y):
        """
        使用向量化的重心座標法判定哪些點 (X, Y) 落在三角形內。
        
        參數:
            X, Y: 代表網格座標的 numpy 陣列。
            
        回傳:
            布林 numpy 遮罩，True 表示該點在三角形內。
        """
        x1, y1 = self.ax, self.ay
        x2, y2 = self.bx, self.by
        x3, y3 = self.cx, self.cy

        denominator = ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
        if denominator == 0:
            return np.zeros_like(X, dtype=bool)
            
        u = ((y2 - y3)*(X - x3) + (x3 - x2)*(Y - y3)) / denominator
        v = ((y3 - y1)*(X - x3) + (x1 - x3)*(Y - y3)) / denominator
        w = 1 - u - v
        return (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1) & (w >= 0) & (w <= 1)

def calculate_coverage(reference_tri, test_tri, resolution=500):
    """
    計算測試色域覆蓋參考色域的百分比。
    
    參數:
        reference_tri: 參考色域的 Triangle 物件。
        test_tri: 測試色域的 Triangle 物件。
        resolution: 計算用的網格解析度。
        
    回傳:
        float: 覆蓋率百分比 (0-100)。
    """
    xs = np.linspace(0, 1, resolution)
    ys = np.linspace(0, 1, resolution)
    X, Y = np.meshgrid(xs, ys)

    ref_mask = reference_tri.inside_mask(X, Y)
    test_mask = test_tri.inside_mask(X, Y)

    ref_total = np.sum(ref_mask)
    if ref_total == 0:
        return 0.0
        
    overlap = np.sum(ref_mask & test_mask)
    return (overlap / ref_total) * 100.0