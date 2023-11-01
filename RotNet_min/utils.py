from __future__ import division

import cv2
import os
import keras.backend as K

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


def angle_difference(x, y):
    """
    Calculate minimum difference between two angles.
    """
    return 180 - abs(abs(x - y) - 180)


def angle_error(y_true, y_pred):
    """
    Calculate the mean diference between the true angles
    and the predicted angles. Each angle is represented
    as a binary vector.
    """
    diff = angle_difference(K.argmax(y_true), K.argmax(y_pred))
    return K.mean(K.cast(K.abs(diff), K.floatx()))


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

