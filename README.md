# Psd2Png
## 概要
Psdファイルをレイヤー毎のpngに分割出力するソフトです。

## 動作環境
Python 3.8  
Pullow 7.1.2  
psd-tools 1.9.15  

バイナリはwindows版のみです。  
開発環境は日本語windows10 64bitですが、おそらくOS固有の動作は使用していないため、おそらく他の環境でも動作します(未検証)

## 使い方
psd2png.exeに任意のpsdファイルをD&Dしてください。

## 詳細な使い方
```
Psd2Png PSD_PATH [--force] [---noalert] [--outlist] [--outdir=OUTPUT_DIR] [--logfile=LOG_PATH] [PNG_PATHS]...
```
詳細は、`Psd2Png --help`でも確認できます。
### `PSD_PATH`
  レイヤー毎に分割したいpsdファイルのパスを入力してください。  
  レイヤー名の文字コードは、utf-8かshift-jis(cp932)のみ対応しています。  

### `--force`
  pngファイルを保存するフォルダが既に存在する場合、確認せず削除します。

### `--noalert`
  pngファイルを保存するフォルダが既に存在する場合、上書きせず処理を中断します。  
  別のプロセスから本ソフトを呼び出すような場合に有用です。  

### `--outlis`
  作成予定のpngファイルパスの一覧を標準出力に返します。  

### `--outdir=OUTPUT_DIR`
  pngファイルを保存するフォルダを指定します。  
  このオプションを使用しない場合、元のpsdファイルと同じ名前のフォルダに出力されます。  

### `--logfile=LOG_PATH`
　実行ログを出力するファイルを指定します。  
　このオプションを使用しない場合、実行ログはエラー出力に表示されます。  

### `[PNG_PATHS]...`
  pngファイルをレイヤー名以外で保存する場合に使用します。  
  --outlistオプションでレイヤー名の一覧を取得 → GUIで保存先の名前を編集 → このオプションを付けて出力 のような使い方を想定しています。
  
## ライセンス
MIT

## クレジット
Copyright (c) 2001 Python Software Foundation; All Rights Reserved
