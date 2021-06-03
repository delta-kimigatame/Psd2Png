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

    def __init__(self,psdPath,logger=None,outputDir=""):
        if logger is None:
            self.__logger=logging.getLogger("PSD2Png")
        else:
            self.__logger=logger
        self.__layerCount=0
        self.__layers=[]
        self.__outputPaths=[]
        self.__IsInputPathAsFile(psdPath)
        self.__CheckFileFormat(psdPath)
        self.__CheckOutputDir(psdPath,outputDir)
        self.__CheckLength()

    @property
    def outputPaths(self):
        return self.__outputPaths

    def __IsInputPathAsFile(self,psdPath):
        if not os.path.isfile(psdPath):
            self.__logger.error ("指定されたファイルが見つかりません\n"+psdPath)
            raise FileNotFoundError("指定されたファイルが見つかりません\n"+psdPath)
        self.__logger.debug ("OK:"+psdPath)

    def __CheckFileFormat(self,psdPath):
        self.__logger.debug ("ファイルがpsdか確認")
        try:
            self.__psd=PSDImage.open(psdPath,encoding="cp932")
        except:
            self.__logger.error ("指定されたファイルはpsdではありません\n"+psdPath)
            raise OSError(400,"指定されたファイルはpsdではありません",psdPath)
        self.__logger.debug ("ファイルがpsdか確認OK")

    def __CheckOutputDir(self,psdPath,outputDir):
        self.__logger.debug ("保存先フォルダ確認")
        if outputDir=="":
            outputDir=psdPath.split(".")[0]
            self.__logger.info("outputDirが指定されていないため、"+outputDir+"としました")
        self.__outputDir=outputDir


    def __CheckLength(self):
        self.__logger.debug ("レイヤー数の取得")
        if (len(list(self.__psd.descendants()))==0):
            return

        for layer in list(self.__psd.descendants()):
            if layer.is_group():
                continue
            self.__layers.append(layer)
        self.__logger.debug ("取得OK:"+str(len(self.__layers)))


    def OutputPng(self):
        self.__logger.debug ("pngファイルの書き出し")
        self.__logger.debug ("出力リストの確認")
        if len(self.__layers)==0 and len(self.__outputPaths)!=1:
            self.SetOutputPaths()
            self.__outputPaths.append(os.path.join(self.__outputDir,os.path.split(self.__outputDir)[1]))
        elif len(self.__layers)!=len(self.__outputPaths):
            self.__logger.info ("レイヤー数と出力リストが一致しないため再取得します。")
            self.SetOutputPaths()

        self.__MakeOutputDir()
        if len(self.__layers)==0:
            outputImage=self.__psd.composite()
            try:
                outputImage.save(self.__outputPaths[0]+".png")
                self.__logger.info(self.__outputPaths[0]+".pngに保存しました")
            except:
                self.__logger.error(self.__outputPaths[0]+".png)の保存に失敗しました")
            return

        for layer,output in zip(self.__layers,self.__outputPaths):
            outputImage=self.__ApplyLayerOffset(layer)
            outputDir=os.path.split(output)[0]
            if not os.path.isdir(outputDir):
                self.__logger.debug (outputDir+"が存在しないため生成")
                try:
                    os.makedirs(outputDir)
                except:
                    self.__logger.error("フォルダの生成に失敗しました:"+outputDir)
            try:
                outputImage.save(output+".png")
                self.__logger.info("レイヤー名："+layer.name+"を"+output+".pngに保存しました")
            except:
                self.__logger.error("レイヤー名："+layer.name+"("+output+".png)の保存に失敗しました")

    def SetOutputPaths(self):
        self.__logger.debug ("レイヤー名の抽出")
        if len(self.__layers)==0:
            self.__outputPaths.append(os.path.join(self.__outputDir,os.path.split(self.__outputDir)[1]))
            return

        for layer in self.__layers:
            parentDirs=self.__GetParentDirs(layer)
            outputFileName=self.__LayerNameSanitize(layer)
            self.__SetOutputPath(parentDirs,outputFileName)
        self.__logger.debug ("レイヤー名の抽出OK")

    def __GetParentDirs(self,layer):
        self.__logger.debug (layer.name+"のレイヤーグループ確認")
        parentDirs=[]
        parent=layer.parent
        while "layers.Group" in str(type(parent)):
            parentDirs.append(self.__LayerNameSanitize(parent))
            parent=parent.parent
        self.__logger.debug (layer.name+"のレイヤーグループ取得完了"+str(parentDirs))
        return parentDirs

    def __LayerNameSanitize(self,layer):
        self.__logger.debug (layer.name+"のうち、ファイル名に使えない文字の除去")
        newName=re.sub(self.__layerNameSanitizeReg,"",layer.name).replace("\\","")
        if newName=="":
            newName=self.__defaultLayerName+str(self.__layerCount)
            self.__layerCount+=1
            self.__logger.debug (layer.name+"が0文字になったため、"+newName+"としました")
        return newName

    def __SetOutputPath(self,parentDirs,outputFileName):
        tempPath=os.path.join(self.__outputDir,*parentDirs,outputFileName)
        while tempPath in self.__outputPaths:
            tempPath+=self.__paddingChar
        self.__logger.debug ("書き出しファイル名リストに"+outputFileName+"を"+tempPath+"としてセット")
        self.__outputPaths.append(tempPath)

    def __ApplyLayerOffset(self,layer):
        image=layer.topil()
        bgi=Image.new("RGBA",[self.__psd.width,self.__psd.height],(0,0,0,0))
        bgi.paste(image,layer.offset)
        return bgi

    def __MakeOutputDir(self):
        if os.path.isdir(self.__outputDir):
            self.__logger.debug(self.__outputDir +"はすでに存在します")
            updateAlert=messagebox.askquestion("上書きの確認",self.__outputDir +"はすでに存在しますが、上書きしますか?")
            if updateAlert=="yes":
                self.__logger.debug("既存のファイル削除")
                shutil.rmtree(self.__outputDir)
                self.__logger.debug ("既存のファイル削除OK")
            else:
                self.__logger.debug("ファイルの上書きがキャンセルされました")
                raise FileExistsError("ファイルの上書きがキャンセルされました")
        self.__logger.debug ("出力フォルダの生成")
        os.makedirs(self.__outputDir)
        self.__logger.debug ("出力フォルダの生成OK")


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug ("ファイルパス確認")
    if(len(sys.argv) <=1):
        messagebox.showerror("ファイルをドラッグ&ドロップしてください","このソフトにpsdファイルをドラッグ&ドロップしてください")
    else:
        psdPath=sys.argv[1]
        P2P=Psd2Png(psdPath)
        P2P.OutputPng()
