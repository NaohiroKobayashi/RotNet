# 画像回転自動補正アプリ with RotNet

このリポジトリにはRotNetを用いた画像の回転を自動で補正するアプリを含んでいます。
RotNetは画像の正しい位置からの回転角度を予測する深層学習モデルです。

## 必要なパッケージ
このアプリケーションは、主にkerasとcustomTKinterを用いて作成しています。
必要なパッケージは以下のコマンドでインストールできます。: `pip install -r requirements.txt`

## 利用方法
- 学習済みモデルを[ここから](https://drive.google.com/file/d/1wIc2q0tSDaDAdHhMym5hpSQixCFacJ5o/view?usp=sharing)ダウンロードします。
- main.pyと同じ場所に配置するか、main.py2227行目のパスを書き換えてください。

## 操作方法
![ダミー画像](https://github.com/NaohiroKobayashi/RotNet/assets/72367261/85e0c440-1a25-472f-adb2-431df7b7b503)
操作方法はシンプルです。
- 参照もしくはドラッグアンドドロップで補正したい画像を選び、実行ボタンを押します。
- 実行後、左下のボックスに表示させる画像パスがNNによって検出された回転している画像です。画像パスをクリックで元画像と補正後画像を確認できます。
- 検出された画像を確認後、[すべて補正して保存]ボタンで一括で補正し保存することもできます。

## 機械学習について
- この深層学習モデルは[RotNet](https://github.com/d4nst/RotNet)を参考に学習を行っています。
- 学習データにはGoogleStreetViewデータセット+lsw顔画像データセットを用いています。
    - つまり、屋外風景と人間の顔画像には高い補正精度を発揮しますが、屋内画像や食べ物、印刷物などには現在のところほとんど無力です。
