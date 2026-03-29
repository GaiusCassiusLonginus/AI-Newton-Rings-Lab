import tkinter as tk
original_image = None
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math
# 全局变量
image_path = None
canvas = None
canvas_container = None
display_image = None
scale_factor = 1.0
points = []
def select_image():
    global image_path, canvas, canvas_container, original_image, display_image, scale_factor, points
    image_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if image_path:
        original_image = Image.open(image_path)
        display_image = original_image.copy()
        display_image.thumbnail((800, 800))

        scale_factor = original_image.width / display_image.width

        photo = ImageTk.PhotoImage(display_image)

        # 清除旧 canvas 容器
        if canvas_container:
            canvas_container.destroy()
        canvas_container = tk.Frame(root)
        canvas_container.pack()
        canvas_width, canvas_height = display_image.width, display_image.height
        canvas = tk.Canvas(canvas_container, width=canvas_width, height=canvas_height)
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo
        canvas.bind("<Button-1>", on_canvas_click)
        points.clear()
def reset_program():
    global canvas, canvas_container, image_path, original_image, display_image, scale_factor, points
    points.clear()
    if canvas_container:
        canvas_container.destroy()
        canvas_container = None
    canvas = None
    image_path = None
    original_image = None
    display_image = None
    scale_factor = 1.0
def on_canvas_click(event):
    x, y = event.x, event.y
    original_x = int(x * scale_factor)
    original_y = int(y * scale_factor)
    points.append((original_x, original_y))
    # 显示红色长十字准心（可选虚线 dash）
    canvas.create_line(0, y, canvas.winfo_width(), y, fill="red", dash=(4, 2))
    canvas.create_line(x, 0, x, canvas.winfo_height(), fill="red", dash=(4, 2))
    # 中心红点
    canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")
    if mode.get() == "circle" and len(points) == 3:
        calculate_and_draw_circle()
    elif mode.get() == "distance" and len(points) == 2:
        calculate_distance()
def calculate_and_draw_circle():
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    temp = x2**2 + y2**2
    bc = (x1**2 + y1**2 - temp) / 2
    cd = (temp - x3**2 - y3**2) / 2
    det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)
    if abs(det) < 1e-6:
        messagebox.showerror("错误", "三点共线，无法拟合圆。")
        points.clear()
        return
    cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
    cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
    r = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
    diameter = 2 * r
    answer = messagebox.askyesno("结果", f"拟合圆的像素直径为: {diameter:.2f}\n是否在图上绘制此圆？")
    if answer:
        draw_x = cx / scale_factor
        draw_y = cy / scale_factor
        draw_r = r / scale_factor
        canvas.create_oval(
            draw_x - draw_r, draw_y - draw_r,
            draw_x + draw_r, draw_y + draw_r,
            outline="blue", width=2
        )
    points.clear()
def calculate_distance():
    (x1, y1), (x2, y2) = points
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    messagebox.showinfo("像素距离", f"两点之间的像素距离为: {distance:.2f}")
    canvas.create_line(
        x1 / scale_factor, y1 / scale_factor,
        x2 / scale_factor, y2 / scale_factor,
        fill="green", width=2
    )
    points.clear()
# 主界面
root = tk.Tk()
root.title("图像测量工具")
mode = tk.StringVar(value="circle")  # 模式变量，必须在 root 创建后
# 控件区
control_frame = tk.Frame(root)
control_frame.pack(pady=10)
tk.Button(control_frame, text="选择图片", command=select_image).grid(row=0, column=0, padx=5)
tk.Button(control_frame, text="重新开始", command=reset_program).grid(row=0, column=1, padx=5)
tk.Label(control_frame, text="选择模式：").grid(row=0, column=2, padx=5)
tk.Radiobutton(control_frame, text="三点拟合圆", variable=mode, value="circle").grid(row=0, column=3)
tk.Radiobutton(control_frame, text="两点测距", variable=mode, value="distance").grid(row=0, column=4)
root.mainloop()