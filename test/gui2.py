import cv2
import os
from PIL import Image
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import BOTH, BOTTOM, CENTER, DISABLED, E, END, GROOVE, LEFT, N, NW, RIGHT, S, TOP, W, X, Y, Frame, Label, ttk
from tkinterdnd2 import *
from tkinter import scrolledtext
from CTkListbox import *
from PIL import Image, ImageTk
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
from utils import angle_error
import numpy as np

def resize_for_predict(image, target_size):
    height = image.shape[0]
    width = image.shape[1]
    
    # 縦長
    if height >= width:
        dst = cv2.resize(image, None, fx=target_size/width, fy=target_size/width)
        padding = int((dst.shape[0] - target_size)/2)
        resized_image = dst[padding:target_size+padding, 0:target_size]
    # 横長
    else:
        dst = cv2.resize(image, None, fx=target_size/height, fy=target_size/height)
        padding = int((dst.shape[1] - target_size)/2)
        resized_image = dst[0:target_size, padding:target_size+padding]

    return resized_image

def display_examples_justangle(model, input, num_images=5, size=None, crop_center=False,
                     crop_largest_rect=False, preprocess_func=None, save_path=None):
    """
    Given a model that predicts the rotation angle of an image,
    and a NumPy array of images or a list of image paths, display
    the specified number of example images in three columns:
    Original, Rotated and Corrected.
    """

    if isinstance(input, (np.ndarray)):
        images = input
        N, h, w = images.shape[:3]
        if not size:
            size = (h, w)
        indexes = np.random.choice(N, num_images)
        images = images[indexes, ...]
    else:
        images = []
        filenames = input
        N = len(filenames)
        # indexes = np.random.choice(N, num_images)
        for i in range(N):
            image = imread(filenames[i])
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images.append(image)
        images = np.asarray(images)

    x = []

    for i, image in enumerate(images):
        
        height, width = image.shape[:2]
        if width < height:
            height = width
        else:
            width = height

        resized_image = resize_for_predict(image, 224)

        x.append(resized_image)

    x = np.asarray(x, dtype='float32')

    if x.ndim == 3:
        x = np.expand_dims(x, axis=3)

    if preprocess_func:
        x = preprocess_func(x)

    y_pred = []
    for i, item1 in enumerate(x):
        item = item1[np.newaxis, :, :, :,]
        y_pred_tmp = np.argmax(model.predict(item), axis=1)
        y_pred.append(y_pred_tmp[0])
        prog_bar.configure(value=0.2 + ((i+1)/len(x)))
        prog_bar.update()

    y_pred=np.array(y_pred)
    y_pred[(y_pred>315) | (y_pred<=45)] = 0
    y_pred[(y_pred>45) & (y_pred<=135)] = 1
    y_pred[(y_pred>135) & (y_pred<=225)] = 2
    y_pred[(y_pred>225) & (y_pred<=315)] = 3

    return y_pred

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
    global count_drop
    fTyp = [("", "*")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    iFilePaths = filedialog.askopenfilenames(filetype = [("Image file", " .png .jpg "), ("PNG", ".png"), ("JPEG", ".jpg") ], initialdir = iFile)
    droparea1.configure(state='normal')
    if(count_drop == 0):
        droparea1.delete('1.0', END)
    for file in iFilePaths:
        textbox.insert('end', file)
        textbox.insert('end', '\n')
    droparea1.configure(state='disabled')
    count_drop += 1


# フォルダ指定
def dirdialog_clicked(var):
    iDir = os.path.abspath(os.path.dirname(__file__))
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    var.set(iDirPath)

#dnd
def droped(event):
    global count_drop
    files = event.data  
    # 文字列をrawに変換
    filename_new = repr(files)[1:-1]
    # ＼と{}を修正
    files_new = filename_new.replace('\\\\', '/').replace('{', '').replace('}', '')
    files_str = str(files_new)
    files_str = files_str.replace(' ', '\n')
    # 起動して最初のドロップなら、初期文字を消して挿入
    droparea1.configure(state='normal')
    if(count_drop == 0):
        droparea1.delete('1.0', END)    
    droparea1.insert('end', files_str)
    droparea1.configure(state='disabled')
    count_drop += 1

def action():
    global angle_dict, count_listbox
    prog_bar.configure(value=0.1)
    prog_bar.update()
    # area1からパスを取得
    image_files = droparea1.get("1.0", "end-1c")
    image_files = image_files.split()
    image_num = len(image_files)
    prog_bar.configure(value=0.2)
    prog_bar.update()
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

    # 起動して最初なら初期表示を削除
    if(count_listbox == 0):
        listbox.delete(0, END)
    # 補正対象をリストボックスに挿入
    for k in angle_dict.keys():
        if(angle_dict[k] > 0):
            listbox.insert(END, k)
    count_listbox += 1

def clear():
    droparea1.configure(state='normal')
    droparea1.delete('1.0', END)
    droparea1.configure(state='disabled')
    listbox.delete(0, END)

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
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# 初期表示消去用変数
count_drop = 0
count_listbox = 0

#メインウィンドウ
root = TkinterDnD.Tk()
root.geometry("1200x900")

# frames
frame_bottom = ctk.CTkFrame(root)
frame_bottom.pack(side=BOTTOM, anchor=W, padx=10, pady=10, expand=False, fill=X)

frame_buttons = ctk.CTkFrame(root)
frame_buttons.pack(side=LEFT, anchor=W, padx=(10, 0), pady=10, expand=True, fill='both')

frame_left = ctk.CTkFrame(root, width=100)
frame_left.pack(side=LEFT, anchor=W, padx=(10, 0), pady=10, expand=True, fill='both')

frame_right = ctk.CTkFrame(root)
frame_right.pack(side=LEFT, anchor=W, padx=(10,0), pady=10, expand=True, fill='both')



'''
# frame_left内部
'''
# button
buttons = ctk.CTkFrame(frame_buttons)
buttons.pack(side=LEFT, pady=(10, 0),)
# 参照ボタン
dialog_button = ctk.CTkButton(buttons, text="参照", command=lambda:filedialog_clicked(droparea1), width=10)
dialog_button.pack(side=TOP, padx=5, pady = 20,)
# 実行ボタン
action_button = ctk.CTkButton(buttons, text='実行', command=action, width=10)
action_button.pack(side=TOP, padx=5, pady = 20)# クリアボタン
action_button = ctk.CTkButton(buttons, text='クリア', command=clear, width=10)
action_button.pack(side=TOP, padx=5, pady = 20)
# pdfドロップ
droparea1 = scrolledtext.ScrolledText(frame_left, padx=10, pady=10, width=50, height=8)
droparea1.config(font=('', '15'))
droparea1.drop_target_register(DND_FILES)
files = droparea1.dnd_bind('<<Drop>>', droped)
droparea1.pack(side=TOP,  padx=5, pady=10, expand=True, fill='both')
droparea1.insert(END, '参照ボタンまたはドラッグアンドドロップ', )
droparea1.configure(state='disabled')

var2 = ctk.StringVar()
# 補正対象のリストボックス
listbox = CTkListbox(frame_left, command=show_value, text_color='black')
listbox.pack(side=TOP, padx=10, pady=10, expand=True, fill='both')
# listbox.config(bg='#232D3F')
# listbox.config(font=('meyrio', '15'))
listbox.insert(END, '実行を押して回転を検出')

frame_left.propagate(False)

'''
# frame_right内部
'''
# button
buttons_right = ctk.CTkFrame(frame_right)
buttons_right.pack(side=TOP, pady=(10, 0))

# 選択画像表示用キャンバス
canvas_top = ctk.CTkCanvas(frame_right, width=640,height=360, bd=0, highlightthickness=0, relief='ridge')
canvas_top.pack(side=TOP,  padx=5, pady=10, expand=True)
# 画像を表示するためのキャンバスアイテム
image_item_top = canvas_top.create_image(0, 0, anchor=tk.NW)
# canvas_top.config(bg='#232D3F')

# 補正画像表示用キャンバス
canvas_bottom = ctk.CTkCanvas(frame_right, width=640,height=360, bd=0, highlightthickness=0, relief='ridge')
canvas_bottom.pack(side=TOP,  padx=5, pady=10, expand=True)
# 画像を表示するためのキャンバスアイテム
image_item_bottom = canvas_bottom.create_image(0, 0, anchor=tk.NW)

# 保存ボタン
save_button = ctk.CTkButton(buttons_right, text="すべて補正して保存", command=all_save, width=10)
save_button.pack(side=LEFT, padx=5, )
# リスト化ボタン
# tolist_button = ctk.CTkButton(buttons_right, text='リスト化', command=tolist, width=10)
# tolist_button.pack(side=LEFT, padx=5)

'''
# frame_bottom内部
'''
style=ttk.Style()
style.theme_use()
style.configure("Horizontal.TProgressbar")
prog_bar = ttk.Progressbar(frame_bottom, maximum=1, style="Horizontal.TProgressbar")
style.theme_use("classic")
prog_bar.pack(side=LEFT, expand=True, fill=X)

root.mainloop()
