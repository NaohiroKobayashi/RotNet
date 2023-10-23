import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ppm *.pgm")])
    if file_path:
        image = Image.open(file_path)
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_item, image=photo)
        canvas.image = photo  # 参照を保持してガベージコレクションを防ぎます

# ウィンドウを作成
root = tk.Tk()
root.title("画像ビューア")

# Canvasを作成
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

# 画像を表示するためのキャンバスアイテム
image_item = canvas.create_image(0, 0, anchor=tk.NW)

# 画像を開くボタン
open_button = tk.Button(root, text="画像を選択", command=open_image)
open_button.pack()

# ウィンドウを表示
root.mainloop()
