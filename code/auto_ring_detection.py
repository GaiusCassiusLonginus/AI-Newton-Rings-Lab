import cv2
import numpy as np
from tkinter import Tk, filedialog, simpledialog
import sys
import os
# ---------------------- 十字中心检测 ----------------------
def detect_cross_center(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
    if lines is None:
        print("未检测到十字叉丝")
        return None
    horizontal_lines = []
    vertical_lines = []
    for line in lines:
        rho, theta = line[0]
        if abs(theta) < np.pi / 4 or abs(theta - np.pi) < np.pi / 4:
            horizontal_lines.append((rho, theta))
        elif abs(theta - np.pi / 2) < np.pi / 4:
            vertical_lines.append((rho, theta))
    if not horizontal_lines or not vertical_lines:
        print("未检测到完整的十字叉丝")
        return None
    h, w = image.shape[:2]
    img_center = (w // 2, h // 2)
    def line_distance(rho, theta):
        return abs(rho - (img_center[0] * np.cos(theta) + img_center[1] * np.sin(theta)))
    horizontal_lines.sort(key=lambda x: line_distance(x[0], x[1]))
    vertical_lines.sort(key=lambda x: line_distance(x[0], x[1]))
    h_rho, h_theta = horizontal_lines[0]
    v_rho, v_theta = vertical_lines[0]
    A = np.array([[np.cos(h_theta), np.sin(h_theta)],
                  [np.cos(v_theta), np.sin(v_theta)]])
    B = np.array([h_rho, v_rho])
    try:
        center = np.linalg.solve(A, B)
        return (int(round(center[0])), int(round(center[1])))
    except np.linalg.LinAlgError:
        print("无法计算十字叉丝交点")
        return None
# ---------------------- 工具函数：从曲线中找极值与半高宽边界 ----------------------
def find_extrema_indices(y):
    """基于一阶差分的极值（峰/谷）检测"""
    dy = np.diff(y)
    maxima, minima = [], []
    for i in range(1, len(dy)):
        if dy[i - 1] > 0 and dy[i] <= 0:
            maxima.append(i)
        if dy[i - 1] < 0 and dy[i] >= 0:
            minima.append(i)
    return maxima, minima
def half_height_radius(y, a, b, y_min, y_max):
    """
    在区间 [a, b] (a<b) 上，用线性插值求 y == y_half 的半高宽交点半径。
    y_half = y_min + 0.5*(y_max - y_min)
    要求 y[a] 和 y[b] 分别在 y_half 的两侧。
    """
    y_half = y_min + 0.5 * (y_max - y_min)
    for i in range(a, b):
        y1, y2 = y[i], y[i + 1]
        if (y1 - y_half) * (y2 - y_half) <= 0 and y1 != y2:
            r = i + (y_half - y1) / (y2 - y1)
            return float(r)
    return (a + b) / 2.0
# ---------------------- 暗环检测：输出每个环的内/外径 ----------------------
def detect_dark_rings(image, center, px_to_mm=None, save_prefix=None):
    if center is None:
        return
    result = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    max_radius = min(center[0], w - center[0], center[1], h - center[1])
    if max_radius < 20:
        print("有效检测范围过小，无法检测暗环")
        return
    # 1) 径向平均灰度（1px步长，360采样）+ 轻微高斯平滑
    radial_gray = []
    for r in range(0, max_radius, 1):
        total = 0.0
        cnt = 0
        for ang in np.linspace(0, 2 * np.pi, 360, endpoint=False):
            x = int(center[0] + r * np.cos(ang))
            y = int(center[1] + r * np.sin(ang))
            if 0 <= x < w and 0 <= y < h:
                total += gray[y, x]
                cnt += 1
        radial_gray.append(total / cnt if cnt else 255.0)
    radial_gray = np.array(radial_gray, dtype=np.float32)
    if len(radial_gray) >= 7:
        radial_gray = cv2.GaussianBlur(radial_gray.reshape(-1, 1), (7, 1), 0).ravel()
    # 2) 极值（峰/谷）检测
    maxima, minima = find_extrema_indices(radial_gray)
    # 最小间隔（像素）与最小“对比度”过滤，避免噪声
    min_gap = 3
    contrast_min = 2.0  # 相邻峰-谷的最小灰度差（越大越严格）
    ring_list = []  # [(r_in, r_out), ...]
    last_r_out = -1e9
    for m in minima:
        # 最近的左峰 l 与右峰 r
        l_candidates = [p for p in maxima if p < m]
        r_candidates = [p for p in maxima if p > m]
        if not l_candidates or not r_candidates:
            continue
        l = l_candidates[-1]
        r = r_candidates[0]
        # 基础过滤：峰-谷对比度
        if (radial_gray[l] - radial_gray[m] < contrast_min) or (radial_gray[r] - radial_gray[m] < contrast_min):
            continue
        # 间隔过滤
        if ring_list and (m - (last_r_out)) < min_gap:
            continue
        # 3) 计算内/外半径（半高度阈值处）
        r_in = half_height_radius(radial_gray, l, m, y_min=radial_gray[m], y_max=radial_gray[l])
        r_out = half_height_radius(radial_gray, m, r, y_min=radial_gray[m], y_max=radial_gray[r])
        if r_in < 1 or r_out <= r_in:
            continue
        ring_list.append((r_in, r_out))
        last_r_out = r_out
    # 保底：若没检出任何环，尝试中心附近构造一个
    if not ring_list and len(radial_gray) > 16:
        m = int(np.argmin(radial_gray[5:16])) + 5
        l = max(1, m - 5)
        r = min(len(radial_gray) - 2, m + 5)
        r_in = half_height_radius(radial_gray, l, m, y_min=radial_gray[m], y_max=radial_gray[l])
        r_out = half_height_radius(radial_gray, m, r, y_min=radial_gray[m], y_max=radial_gray[r])
        if r_out > r_in:
            ring_list.append((r_in, r_out))
    if not ring_list:
        print("未检测到有效暗环（内/外边界）")
        return
    # 4) 叠加标注图：画内/外边界；二值图：填充环带
    annotated = result.copy()
    rings_binary = np.full((h, w), 255, dtype=np.uint8)  # 白底
    table_rows = []  # [(idx, d_in_px, d_out_px, d_in_mm?, d_out_mm?)]
    for idx, (r_in, r_out) in enumerate(ring_list, start=1):
        rin_i = int(round(r_in))
        rout_i = int(round(r_out))
        # 叠加标注（内边界：蓝；外边界：绿）
        cv2.circle(annotated, center, rin_i, (255, 0, 0), 2)
        cv2.circle(annotated, center, rout_i, (0, 255, 0), 2)
        cv2.putText(annotated, f"{idx}", (center[0] + rout_i + 5, center[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)
        # 二值：填充环带为黑
        cv2.circle(rings_binary, center, rout_i, 0, thickness=-1)
        cv2.circle(rings_binary, center, rin_i, 255, thickness=-1)
        # 尺寸统计
        d_in_px = 2.0 * r_in
        d_out_px = 2.0 * r_out
        if px_to_mm is not None:
            d_in_mm = d_in_px * px_to_mm
            d_out_mm = d_out_px * px_to_mm
            table_rows.append((idx, d_in_px, d_out_px, d_in_mm, d_out_mm))
            print(f"暗环 #{idx}: r_in={r_in:.2f}px, r_out={r_out:.2f}px | "
                  f"d_in={d_in_px:.2f}px({d_in_mm:.4f}mm), d_out={d_out_px:.2f}px({d_out_mm:.4f}mm)")
        else:
            table_rows.append((idx, d_in_px, d_out_px, None, None))
            print(f"暗环 #{idx}: r_in={r_in:.2f}px, r_out={r_out:.2f}px | "
                  f"d_in={d_in_px:.2f}px, d_out={d_out_px:.2f}px")
    # 十字中心标记
    cv2.circle(annotated, center, 5, (0, 0, 255), -1)
    cv2.line(annotated, (center[0] - 15, center[1]), (center[0] + 15, center[1]), (0, 0, 255), 2)
    cv2.line(annotated, (center[0], center[1] - 15), (center[0], center[1] + 15), (0, 0, 255), 2)
    # 5) 右侧表格（自适应是否显示 mm 列）
    if table_rows:
        margin = 18
        col_w = [85, 150, 150]  # 序号, 内径(px), 外径(px)
        header = ["环序号", "内径(px)", "外径(px)"]
        font_scale_head = 0.9
        font_scale_cell = 0.8
        if px_to_mm is not None:
            col_w += [160, 160]
            header += ["内径(mm)", "外径(mm)"]
        row_h = 30
        header_h = 36
        table_w = sum(col_w) + margin
        table_h = header_h + len(table_rows) * row_h + margin
        table_x = max(margin, w - table_w - margin)
        table_y = margin
        # 背景与边框
        cv2.rectangle(annotated, (table_x, table_y), (table_x + table_w, table_y + table_h), (255, 255, 255), -1)
        cv2.rectangle(annotated, (table_x, table_y), (table_x + table_w, table_y + table_h), (0, 0, 0), 2)
        # 表头
        x = table_x + margin
        for i, head in enumerate(header):
            cv2.putText(annotated, head, (x, table_y + header_h - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale_head, (0, 0, 0), 2)
            x += col_w[i]
        cv2.line(annotated, (table_x + 5, table_y + header_h), (table_x + table_w - 5, table_y + header_h), (0, 0, 0), 2)
        # 行
        for r_i, row in enumerate(table_rows):
            y = table_y + header_h + (r_i + 1) * row_h
            x = table_x + margin
            idx, d_in_px, d_out_px, d_in_mm, d_out_mm = row
            cells = [f"{idx}", f"{d_in_px:.1f}", f"{d_out_px:.1f}"]
            if px_to_mm is not None:
                cells += [f"{d_in_mm:.4f}", f"{d_out_mm:.4f}"]
            for ci, text in enumerate(cells):
                cv2.putText(annotated, text, (x, y - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale_cell, (0, 0, 0), 2)
                x += col_w[ci]
            if r_i < len(table_rows) - 1:
                cv2.line(annotated, (table_x + 5, y + 4), (table_x + table_w - 5, y + 4), (0, 0, 0), 1)
    # 保存与显示
    if save_prefix is not None:
        out1 = f"{save_prefix}_annotated.png"
        out2 = f"{save_prefix}_rings_binary.png"
        cv2.imwrite(out1, annotated)
        #cv2.imwrite(out2, rings_binary)
        print(f"已保存：{out1}")
        #print(f"已保存：{out2}")
    cv2.namedWindow("牛顿环检测结果（内/外边界）", cv2.WINDOW_NORMAL)
    cv2.imshow("牛顿环检测结果（内/外边界）", annotated)
    cv2.namedWindow("黑环提取（二值，黑=环带）", cv2.WINDOW_NORMAL)
    cv2.imshow("黑环提取（二值，黑=环带）", rings_binary)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# ---------------------- 主流程（带文件选择 + 物理标定） ----------------------
def detect_newton_rings():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择牛顿环图像",
        filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp")]
    )
    if not file_path:
        print("未选择图像文件")
        return
    try:
        image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"图像读取失败：{e}")
        return
    if image is None:
        print("图像读取失败！请检查文件路径是否正确。")
        return
    center = detect_cross_center(image)
    if not center:
        print("十字中心检测失败")
        return
    print(f"十字中心坐标：{center}")
    # ==================== 关键修改点：输入每毫米对应的像素数（px/mm） ====================
    px_per_mm = simpledialog.askfloat(
        "物理标定",
        "请输入每毫米对应的像素数 (px/mm)。\n留空或取消则仅计算像素尺寸。",
        minvalue=1e-6  # 允许极小值，避免输入0
    )
    if px_per_mm is not None and px_per_mm > 0:
        px_to_mm = 1 / px_per_mm  # 核心换算：1像素 = 1/(px_per_mm) 毫米
        print(f"物理标定：1mm = {px_per_mm:.2f} px → 1px = {px_to_mm:.6f} mm")
    else:
        px_to_mm = None
        print("未进行物理标定，将仅显示像素尺寸。")
    save_prefix = os.path.splitext(file_path)[0]
    detect_dark_rings(image, center, px_to_mm=px_to_mm, save_prefix=save_prefix)
if __name__ == "__main__":
    detect_newton_rings()