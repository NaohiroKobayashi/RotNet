import cv2
import os
import ftplib
from PIL import Image
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import BOTH, BOTTOM, CENTER, DISABLED, E, END, GROOVE, LEFT, N, NW, RIGHT, S, TOP, W, X, Frame, Label, ttk
from tkinterdnd2 import *


def imread(path):
    tmp_dir = os.getcwd()
    # 1. 対象ファイルがあるディレクトリに移動
    if len(path.split("/")) > 1:
        file_dir = "/".join(path.split("/")[:-1])
        os.chdir(file_dir)
    # 2. 対象ファイルの名前を変更
    tmp_name = "tmp_name"
    os.rename(path.split("/")[-1], tmp_name)
    # 3. 対象ファイルを読み取る
    img = cv2.imread(tmp_name)
    # 4. 対象ファイルの名前を戻す
    os.rename(tmp_name, path.split("/")[-1])
    # カレントディレクトリをもとに戻す
    os.chdir(tmp_dir)
    return img

def imwrite(path, img):
    tmp_dir = os.getcwd()
    # 1. 保存するディレクトリに移動
    if len(path.split("/")) > 1:
        file_dir = "/".join(path.split("/")[:-1])
        os.chdir(file_dir)
    # 2. 対象ファイルを保存
    tmp_name = "tmp_name.jpg"
    cv2.imwrite(tmp_name, img)
    # 3. 対象ファイルの名前を戻す
    if os.path.exists(path.split("/")[-1]):  # ファイルが既にあれば削除
        os.remove(path.split("/")[-1])
    os.rename(tmp_name, path.split("/")[-1])
    # カレントディレクトリをもとに戻す
    os.chdir(tmp_dir)

#UI用関数

#ファイル指定
def filedialog_clicked(var):
    fTyp = [("", "*")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    var.set(iFilePath)


# フォルダ指定
def dirdialog_clicked(var):
    iDir = os.path.abspath(os.path.dirname(__file__))
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    var.set(iDirPath)

#dnd
def droped(event):
    print(event.data)
    var1.set(event.data)

def button_function():
    print("button pressed")

def action():
    original_path = droparea1.get()
    resize_dir = os.path.dirname(original_path)
    resize_path = resize_dir +'/'+ str(os.path.splitext(os.path.basename(original_path))[0] + '_resize.jpg')
    print('resizepath:' + resize_path)
    pdf_path = frame2_entry.get()


#Tkinter
ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

#メインウィンドウ
root = TkinterDnD.Tk()
root.geometry("1200x800")

#frame1
frame1 = ctk.CTkFrame(root)
frame1.pack(side=LEFT, anchor=W, padx=(10, 0), pady=10)

#pdf参照ラベル
label1 = ctk.CTkLabel(frame1, text="補正するファイル:")
label1.pack(side=TOP,  padx=10, pady=10)
var1 = ctk.StringVar()

# pdf参照ボタン
IFileButton_pdf = ctk.CTkButton(frame1, text="参照", command=lambda:filedialog_clicked(var1), width=10)
IFileButton_pdf.pack(side=TOP, padx=5, pady=10)

# pdfドロップ
droparea1 = ctk.CTkScrollableFrame(frame1,  width=450)
droparea1.drop_target_register(DND_FILES)
droparea1.dnd_bind('<<Drop>>', droped)
droparea1.pack(side=TOP,  padx=5, pady=10, expand=True)

# pdfドロップvar
var1.set('参照ボタンまたはドラッグアンドドロップ')

#frame2
frame2 = ctk.CTkFrame(root)
frame2.pack(side=LEFT, anchor=W, padx=(10,0), pady=10)

#pdf参照
label2 = ctk.CTkLabel(frame2, text="補正結果")
label2.pack(side=LEFT,  padx=5, pady=10)
var2 = ctk.StringVar()


#frame2エントリー
frame2_entry = ctk.CTkEntry(frame2, textvariable=var2, width=450)
frame2_entry.pack(side=LEFT, padx=5, pady=10)


#frame4
frame4 = ctk.CTkFrame(root)
frame4.pack(side=TOP, anchor=W, padx=(10,0), pady=10)
action_button = ctk.CTkButton(frame4, text='実行', command=action, width=10)
action_button.pack(side=TOP)

root.mainloop()
