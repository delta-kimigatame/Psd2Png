import sys
import shutil
import os
import os.path
import re
import logging
from tkinter import messagebox
from PIL import Image
from psd_tools import PSDImage

#debug用
#import tests.MakeTestData
class Psd2Png:
    __layerNameSanitizeReg = re.compile('[\\/:*?"<>|]+')
    __defaultLayerName = "layer"
    __paddingChar = "_"
    __updateAlert = False
    __forceOveride = True

    def __init__(self,psdPath,logger=None,outputDir=""):
        if logger is None:
            self.__logger = logging.getLogger("PSD2Png")
        else:
            self.__logger = logger
        self.__layerCount = 0
        self.__layers = []
        self.__outputPaths = []
        self.__IsInputPathAsFile(psdPath)
        self.__CheckFileFormat(psdPath)
        self.__CheckOutputDir(psdPath,outputDir)
        self.__CheckLength()

    @property
    def outputPaths(self):
        return self.__outputPaths

    @outputPaths.setter
    def outputPaths(self,values):
        if type(values) == list:
            self.__outputPaths = values
            
    @property
    def updateAlert(self):
        return self.__updateAlert

    @updateAlert.setter
    def updateAlert(self,value):
        self.__updateAlert = bool(value)

    @property
    def forceOveride(self):
        return self.__forceOveride

    @forceOveride.setter
    def forceOveride(self,value):
        self.__forceOveride = bool(value)

    def __IsInputPathAsFile(self,psdPath):
        if not os.path.isfile(psdPath):
            self.__logger.error("指定されたファイルが見つかりません\n" + psdPath)
            raise FileNotFoundError("指定されたファイルが見つかりません\n" + psdPath)
        self.__logger.debug("OK:" + psdPath)

    def __CheckFileFormat(self,psdPath):
        self.__logger.debug("ファイルがpsdか確認")
        try:
            self.__psd = PSDImage.open(psdPath,encoding="cp932")
        except:
            self.__logger.error("指定されたファイルはpsdではありません\n" + psdPath)
            raise OSError(400,"指定されたファイルはpsdではありません",psdPath)
        self.__logger.debug("ファイルがpsdか確認OK")

    def __CheckOutputDir(self,psdPath,outputDir):
        self.__logger.debug("保存先フォルダ確認")
        if outputDir == "":
            outputDir = psdPath.split(".")[0]
            self.__logger.info("outputDirが指定されていないため、" + outputDir + "としました")
        self.__outputDir = outputDir


    def __CheckLength(self):
        self.__logger.debug("レイヤー数の取得")
        if (len(list(self.__psd.descendants())) == 0):
            return

        for layer in list(self.__psd.descendants()):
            if layer.is_group():
                continue
            self.__layers.append(layer)
        self.__logger.debug("取得OK:" + str(len(self.__layers)))


    def OutputPng(self):
        self.__logger.debug("pngファイルの書き出し")
        self.__logger.debug("出力リストの確認")
        if len(self.__layers) == 0 and len(self.__outputPaths) != 1:
            self.SetOutputPaths()
            self.__outputPaths.append(os.path.join(self.__outputDir,os.path.split(self.__outputDir)[1]))
        elif len(self.__layers) != 0 and len(self.__layers) != len(self.__outputPaths):
            self.__logger.info("レイヤー数と出力リストが一致しないため再取得します。")
            self.__outputPaths=[]
            self.SetOutputPaths()

        self.__MakeOutputDir(self.__outputDir)
        if len(self.__layers) == 0:
            outputImage = self.__psd.composite()
            self.__MakeOutputDir(os.path.split(self.__outputPaths[0])[0],True)
            try:
                outputImage.save(self.__outputPaths[0] + ".png")
                self.__logger.info(self.__outputPaths[0] + ".pngに保存しました")
            except:
                self.__logger.error(self.__outputPaths[0] + ".png)の保存に失敗しました")
            return

        for layer,output in zip(self.__layers,self.__outputPaths):
            outputImage = self.__ApplyLayerOffset(layer)
            self.__MakeOutputDir(os.path.split(output)[0],True)
            try:
                outputImage.save(output + ".png")
                self.__logger.info("レイヤー名：" + layer.name + "を" + output + ".pngに保存しました")
            except:
                self.__logger.error("レイヤー名：" + layer.name + "(" + output + ".png)の保存に失敗しました")

    def SetOutputPaths(self):
        self.__logger.debug("レイヤー名の抽出")
        if len(self.__layers) == 0:
            self.__outputPaths.append(os.path.join(self.__outputDir,os.path.split(self.__outputDir)[1]))
            return

        for layer in self.__layers:
            parentDirs = self.__GetParentDirs(layer)
            outputFileName = self.__LayerNameSanitize(layer)
            self.__SetOutputPath(parentDirs,outputFileName)
        self.__logger.debug("レイヤー名の抽出OK")

    def __GetParentDirs(self,layer):
        self.__logger.debug(layer.name + "のレイヤーグループ確認")
        parentDirs = []
        parent = layer.parent
        while "layers.Group" in str(type(parent)):
            parentDirs = [self.__LayerNameSanitize(parent)] + parentDirs
            parent = parent.parent
        self.__logger.debug(layer.name + "のレイヤーグループ取得完了" + str(parentDirs))
        return parentDirs

    def __LayerNameSanitize(self,layer):
        self.__logger.debug(layer.name + "のうち、ファイル名に使えない文字の除去")
        newName = re.sub(self.__layerNameSanitizeReg,"",layer.name).replace("\\","")
        if newName == "":
            newName = self.__defaultLayerName + str(self.__layerCount)
            self.__layerCount+=1
            self.__logger.debug(layer.name + "が0文字になったため、" + newName + "としました")
        return newName

    def __SetOutputPath(self,parentDirs,outputFileName):
        tempPath = os.path.join(self.__outputDir,*parentDirs,outputFileName)
        while tempPath in self.__outputPaths:
            tempPath+=self.__paddingChar
        self.__logger.debug("書き出しファイル名リストに" + outputFileName + "を" + tempPath + "としてセット")
        self.__outputPaths.append(tempPath)

    def __ApplyLayerOffset(self,layer):
        image = layer.topil()
        bgi = Image.new("RGBA",[self.__psd.width,self.__psd.height],(0,0,0,0))
        bgi.paste(image,layer.offset)
        return bgi

    def __MakeOutputDir(self,output,marge=False):
        if os.path.isdir(output) and not marge:
            self.__logger.debug(output + "はすでに存在します")
            if self.__forceOveride:
                self.__RemoveDir(output)
            elif self.__updateAlert:
                updateAlert = self.ShowUpdateAlert(output)
                if updateAlert == "yes":
                    self.__RemoveDir(output)
                else:
                    self.__logger.error("ファイルの上書きがキャンセルされました")
                    raise FileExistsError("ファイルの上書きがキャンセルされました")
            else:
                self.__logger.error("既にファイルが存在するため、出力を中断しました")
                raise FileExistsError("既にファイルが存在するため、出力を中断しました")
        elif not os.path.isdir(output):
            self.__logger.debug("出力フォルダの生成")
            os.makedirs(output)
            self.__logger.debug("出力フォルダの生成OK")

    def ShowUpdateAlert(self,output):
        return messagebox.askquestion("上書きの確認",output + "はすでに存在しますが、上書きしますか?")

    def __RemoveDir(self,dir):
        try:
            self.__logger.debug("既存のファイル削除")
            shutil.rmtree(dir)
            self.__logger.debug("既存のファイル削除OK")
        except PermissionError:
            self.__logger.error(dir + "はほかのプロセスで使用中のため、削除できませんでした")
            raise PermissionError(dir + "はほかのプロセスで使用中のため、削除できませんでした")




if __name__ == "__main__":

    argv = sys.argv
    
    if "--help" in argv:
        print("Usage: Psd2Png PSD_PATH [--force] [---noalert] [--outlist] [--outdir=OUTPUT_DIR] [--logfile=LOG_PATH] [PNG_PATHS]...")
        print("""
指定したPSDファイルを、レイヤー名毎のpngファイルとして保存します。

PSD_PATH:
  レイヤー毎に分割したいpsdファイルのパスを入力してください。
  レイヤー名の文字コードは、utf-8かshift-jis(cp932)のみ対応しています。

--force:
  pngファイルを保存するフォルダが既に存在する場合、確認せず削除します。

--noalert:
  pngファイルを保存するフォルダが既に存在する場合、上書きせず処理を中断します。
  別のプロセスから本ソフトを呼び出すような場合に有用です。

--outlist:
  作成予定のpngファイルパスの一覧を標準出力に返します。

--outdir=OUTPUT_DIR:
  pngファイルを保存するフォルダを指定します。
  このオプションを使用しない場合、元のpsdファイルと同じ名前のフォルダに出力されます。

--logfile=LOG_PATH:
　実行ログを出力するファイルを指定します。
　このオプションを使用しない場合、実行ログはエラー出力に表示されます。

[PNG_PATHS]...:
  pngファイルをレイヤー名以外で保存する場合に使用します。
  --outlistオプションでレイヤー名の一覧を取得 → GUIで保存先の名前を編集 → このオプションを付けて出力 のような使い方を想定しています。
        """)
        sys.exit()
        
    if "--force" in argv:
        force = True
        argv.remove("--force")
    else:
        force = False

    if "--noalert" in argv:
        alert = False
        argv.remove("--noalert")
    else:
        alert = True

    if "--outlist" in argv:
        outlist = True
        argv.remove("--outlist")
    else:
        outlist = False
        
    tempList = [x for x in argv if str(x).startswith("--logfile=")]
    if tempList != []:
        logging.basicConfig(filename=tempList[0].replace("--logfile=","",1), filemode='w',level=logging.DEBUG)
        for temp in tempList:
            argv.remove(temp)
    else:
        logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("PSD2Png")


    tempList = [x for x in argv if str(x).startswith("--outdir=")]
    if tempList == []:
        outdir = ""
    else:
        outdir = tempList[0].replace("--outdir=","",1)
        for temp in tempList:
            argv.remove(temp)
            

    outputPaths=[]
    for path in argv[2:]:
        temp=path.replace("\r","").replace("\n","").replace("/","\\").split("\\")
        outputPaths.append(os.path.abspath(os.path.join(*temp)))

    logger.debug("ファイルパス確認")
    if(len(argv) <= 1):
        if alert:
            messagebox.showerror("ファイルをドラッグ&ドロップしてください","このソフトにpsdファイルをドラッグ&ドロップしてください")
        logger.error("このソフトにpsdファイルをドラッグ&ドロップしてください")
    else:
        psdPath = argv[1]
        P2P = Psd2Png(psdPath,logger=logger,outputDir=outdir)
        P2P.updateAlert = alert
        P2P.forceOveride = force
        P2P.outputPaths = outputPaths
        if outlist:
            P2P.SetOutputPaths()
            for output in P2P.outputPaths:
                print(output)
        else:
            P2P.OutputPng()
