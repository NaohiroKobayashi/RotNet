import cv2
import os
from PIL import Image
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinter import BOTH, BOTTOM, CENTER, DISABLED, E, END, GROOVE, LEFT, N, NW, RIGHT, S, TOP, W, X, Y, Frame, Label, ttk
from tkinterdnd2 import *
from tkinter import scrolledtext
from CTkListbox import *
from PIL import Image, ImageTk
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
from utils import angle_error, display_examples_justangle

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
def filedialog_clicked(textbox):
    fTyp = [("", "*")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    iFilePaths = filedialog.askopenfilenames(filetype = [("Image file", " .png .jpg "), ("PNG", ".png"), ("JPEG", ".jpg") ], initialdir = iFile)
    for file in iFilePaths:
        textbox.insert('end', file)
        textbox.insert('end', '\n')


# フォルダ指定
def dirdialog_clicked(var):
    iDir = os.path.abspath(os.path.dirname(__file__))
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    var.set(iDirPath)

#dnd
def droped(event):
    files = event.data  
    # 文字列をrawに変換
    filename_new = repr(files)[1:-1]
    # ＼と{}を修正
    files_new = filename_new.replace('\\\\', '/').replace('{', '').replace('}', '')
    files_str = str(files_new)
    files_str = files_str.replace(' ', '\n')
    droparea1.insert('end', files_str)

def action():
    global angle_dict
    # area1からパスを取得
    image_files = droparea1.get("1.0", "end-1c")
    image_files = image_files.split()
    image_num = len(image_files)

    # 角度予測
    angle = display_examples_justangle(
    model, 
    image_files,
    num_images=image_num,
    size=(224, 224),
    crop_center=True,
    crop_largest_rect=True,
    preprocess_func=preprocess_input,
    )

    # 角度の辞書を作成
    angle_dict = dict(zip(image_files, angle))

    # 補正対象をリストボックスに挿入
    for k in angle_dict.keys():
        if(angle_dict[k] > 0):
            listbox.insert(END, k)

def resize_image(image, width, height):
    aspect = image.width / image.height
    # 余白用画像
    canvas = Image.new(image.mode, (width, height), (255, 255, 255))

    # 16:9より横長のとき
    if(aspect > 1.78):
        re_image = image.resize((width, int(image.height*(width/image.width))))
        y = int((height - re_image.height) / 2)
        canvas.paste(re_image, (0, y))
    # 16:9より縦長のとき
    else:
        re_image = image.resize((int(image.width*(height/image.height)), height))
        x = int((width - re_image.width) / 2)
        canvas.paste(re_image, (x, 0))
    return canvas

def show_image(canvas, image_path):
    global angle_dict
    # 画像を読み込み
    image=Image.open(image_path)

    # 元画像表示
    re_image = resize_image(image, 640, 360)
    photo = ImageTk.PhotoImage(re_image,)
    # 画像を設定
    canvas_top.itemconfig(image_item_top, image=photo)
    # 参照を保持
    canvas_top.image = photo  

    # 補正のための角度を取得
    angle = angle_dict[image_path]
    if(angle == 1):
        rotate_image = image.rotate(270, expand=True)
    elif(angle == 2):
        rotate_image = image.rotate(180, expand=True)
    else:
        rotate_image = image.rotate(90, expand=True)
    
    re_rotate_image = resize_image(rotate_image, 640, 360)
    rotate_photo = ImageTk.PhotoImage(re_rotate_image,)
    # 画像を設定
    canvas_bottom.itemconfig(image_item_bottom, image=rotate_photo)
    # 参照を保持
    canvas_bottom.image = rotate_photo  

def show_value(file_path):
    show_image(canvas_bottom, file_path)
    print(file_path)

def all_save():
    global angle_dict
    for filepath in angle_dict:
        # 画像を読み込み
        image=Image.open(filepath)
        # 補正のための角度を取得
        angle = angle_dict[filepath]
        if(angle == 1):
            rotate_image = image.rotate(270, expand=True)
        elif(angle == 2):
            rotate_image = image.rotate(180, expand=True)
        else:
            rotate_image = image.rotate(90, expand=True)

        rotate_image.save(filepath)

model_location = 'G:/VScode/RotNet/models/rotnet_street_view_resnet50_keras2_compailed.hdf5'
model = load_model(model_location, custom_objects={'angle_error': angle_error})

#Tkinter
ctk.set_appearance_mode('light')  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

#メインウィンドウ
root = TkinterDnD.Tk()
root.geometry("1200x800")

# frames
frame_left = ctk.CTkFrame(root)
frame_left.pack(side=LEFT, anchor=W, padx=(10, 0), pady=10, expand=True, fill='both')

frame_right = ctk.CTkFrame(root)
frame_right.pack(side=LEFT, anchor=W, padx=(10,0), pady=10, expand=True, fill='both')

'''
# frame_left内部
'''
# button
buttons = ctk.CTkFrame(frame_left)
buttons.pack(side=TOP, pady=(10, 0))
# 参照ボタン
dialog_button = ctk.CTkButton(buttons, text="参照", command=lambda:filedialog_clicked(droparea1), width=10)
dialog_button.pack(side=LEFT, padx=5, )
# 実行ボタン
action_button = ctk.CTkButton(buttons, text='実行', command=action, width=10)
action_button.pack(side=LEFT, padx=5)

#pdf参照ラベル
label1 = ctk.CTkLabel(frame_left, text="補正するファイル")
label1.pack(side=TOP,  padx=10, pady=3,)
var1 = ctk.StringVar()
# pdfドロップvar
var1.set('参照ボタンまたはドラッグアンドドロップ')

# pdfドロップ
droparea1 = scrolledtext.ScrolledText(frame_left, padx=10, pady=10)
droparea1.drop_target_register(DND_FILES)
files = droparea1.dnd_bind('<<Drop>>', droped)
droparea1.pack(side=TOP,  padx=5, pady=10, expand=True, fill='both')

#補正対象ラベル
label2 = ctk.CTkLabel(frame_left, text="補正対象")
label2.pack(side=TOP,  padx=5, pady=5)
var2 = ctk.StringVar()
# 補正対象のリストボックス
listbox = CTkListbox(frame_left, command=show_value, text_color='black', )
listbox.pack(side=TOP, padx=10, pady=10, expand=True, fill='both')

'''
# frame_right内部
'''
# 選択画像表示用キャンバス
canvas_top = ctk.CTkCanvas(frame_right, width=640,height=360, bd=0, highlightthickness=0, relief='ridge')
canvas_top.pack(side=TOP,  padx=5, pady=10)
# 画像を表示するためのキャンバスアイテム
image_item_top = canvas_top.create_image(0, 0, anchor=tk.NW)

# 補正画像表示用キャンバス
canvas_bottom = ctk.CTkCanvas(frame_right, width=640,height=360, bd=0, highlightthickness=0, relief='ridge')
canvas_bottom.pack(side=TOP,  padx=5, pady=10)
# 画像を表示するためのキャンバスアイテム
image_item_bottom = canvas_bottom.create_image(0, 0, anchor=tk.NW)

# button
buttons_right = ctk.CTkFrame(frame_right)
buttons_right.pack(side=TOP, pady=(10, 0))

# 保存ボタン
save_button = ctk.CTkButton(buttons_right, text="すべて補正して保存", command=all_save, width=10)
save_button.pack(side=LEFT, padx=5, )
# リスト化ボタン
# tolist_button = ctk.CTkButton(buttons_right, text='リスト化', command=tolist, width=10)
# tolist_button.pack(side=LEFT, padx=5)


root.mainloop()
