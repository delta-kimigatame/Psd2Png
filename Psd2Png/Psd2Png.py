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
    __layerNameSanitizeReg=re.compile('[\\/:*?"<>|]+')
    __defaultLayerName="layer"
    __paddingChar="_"

    def __init__(self,psdPath,outputDir=""):
        self.__layerCount=0
        self.__layers=[]
        self.__outputPaths=[]
        self.__IsInputPathAsFile(psdPath)
        self.__CheckFileFormat(psdPath)
        self.__CheckOutputDir(psdPath,outputDir)
        self.__CheckLength()


    def __IsInputPathAsFile(self,psdPath):
        if not os.path.isfile(psdPath):
            logging.error ("指定されたファイルが見つかりません\n"+psdPath)
            raise FileNotFoundError("指定されたファイルが見つかりません\n"+psdPath)
        logging.debug ("OK:"+psdPath)

    def __CheckFileFormat(self,psdPath):
        logging.debug ("ファイルがpsdか確認")
        try:
            self.__psd=PSDImage.open(psdPath,encoding="cp932")
        except:
            logging.error ("指定されたファイルはpsdではありません\n"+psdPath)
            raise OSError(400,"指定されたファイルはpsdではありません",psdPath)
        logging.debug ("ファイルがpsdか確認OK")

    def __CheckOutputDir(self,psdPath,outputDir):
        logging.debug ("保存先フォルダ確認")
        if outputDir=="":
            outputDir=psdPath.split(".")[0]
            logging.info("outputDirが指定されていないため、"+outputDir+"としました")

        if os.path.isdir(outputDir):
            logging.debug(outputDir +"はすでに存在します")
            updateAlert=messagebox.askquestion("上書きの確認",outputDir +"はすでに存在しますが、上書きしますか?")
            if updateAlert=="yes":
                logging.debug("既存のファイル削除")
                shutil.rmtree(outputDir)
                logging.debug ("既存のファイル削除OK")
            else:
                logging.debug("ファイルの上書きがキャンセルされました")
                raise FileExistsError("ファイルの上書きがキャンセルされました")
        logging.debug ("出力フォルダの生成")
        os.makedirs(outputDir)
        self.__outputDir=outputDir
        logging.debug ("出力フォルダの生成OK")

    def __CheckLength(self):
        logging.debug ("レイヤー数の取得")
        for layer in list(self.__psd.descendants()):
            if layer.is_group():
                continue
            self.__layers.append(layer)
        logging.debug ("取得OK:"+str(len(self.__layers)))


    def OutputPng(self):
        logging.debug ("pngファイルの書き出し")
        logging.debug ("出力リストの確認")
        if len(self.__layers)!=len(self.__outputPaths):
            logging.info ("レイヤー数と出力リストが一致しないため再取得します。")
            self.SetOutputPaths()
        for layer,output in zip(self.__layers,self.__outputPaths):
            outputImage=self.__ApplyLayerOffset(layer)
            outputDir=os.path.split(output)[0]
            if not os.path.isdir(outputDir):
                logging.debug (outputDir+"が存在しないため生成")
                try:
                    os.makedirs(outputDir)
                except:
                    logging.error("フォルダの生成に失敗しました:"+outputDir)
            try:
                outputImage.save(output+".png")
                logging.info("レイヤー名："+layer.name+"を"+output+".pngに保存しました")
            except:
                logging.error("レイヤー名："+layer.name+"("+output+".png)の保存に失敗しました")

    def SetOutputPaths(self):
        logging.debug ("レイヤー名の抽出")
        for layer in self.__layers:
            parentDirs=self.__GetParentDirs(layer)
            outputFileName=self.__LayerNameSanitize(layer)
            self.__SetOutputPath(parentDirs,outputFileName)
        logging.debug ("レイヤー名の抽出OK")

    def __GetParentDirs(self,layer):
        logging.debug (layer.name+"のレイヤーグループ確認")
        parentDirs=[]
        parent=layer.parent
        while "layers.Group" in str(type(parent)):
            parentDirs.append(self.__LayerNameSanitize(parent))
            parent=parent.parent
        logging.debug (layer.name+"のレイヤーグループ取得完了"+str(parentDirs))
        return parentDirs

    def __LayerNameSanitize(self,layer):
        logging.debug (layer.name+"のうち、ファイル名に使えない文字の除去")
        newName=re.sub(self.__layerNameSanitizeReg,"",layer.name)
        if newName=="":
            newName=self.__defaultLayerName+str(self.__layerCount)
            self.__layerCount+=1
            logging.debug (layer.name+"が0文字になったため、"+newName+"としました")
        return newName

    def __SetOutputPath(self,parentDirs,outputFileName):
        tempPath=os.path.join(self.__outputDir,*parentDirs,outputFileName)
        while tempPath in self.__outputPaths:
            tempPath+=self.__paddingChar
        logging.debug ("書き出しファイル名リストに"+outputFileName+"を"+tempPath+"としてセット")
        self.__outputPaths.append(tempPath)

    def __ApplyLayerOffset(self,layer):
        image=layer.topil()
        bgi=Image.new("RGBA",[self.__psd.width,self.__psd.height],(0,0,0,0))
        bgi.paste(image,layer.offset)
        return bgi

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug ("ファイルパス確認")
    if(len(sys.argv) <=1):
        messagebox.showerror("ファイルをドラッグ&ドロップしてください","このソフトにpsdファイルをドラッグ&ドロップしてください")
    else:
        psdPath=sys.argv[1]
        P2P=Psd2Png(psdPath)
        P2P.OutputPng()
