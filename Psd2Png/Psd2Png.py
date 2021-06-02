import sys
import shutil
import os
import os.path
import re
import logging
from tkinter import messagebox
from PIL import Image
from psd_tools import PSDImage


class Psd2Png:
    __layerNameSanitizeReg=re.compile('[\\/:*?"<>|]+')
    __defaultLayerName="layer"
    __paddingChar="_"

    def __init__(self,psdPath,outputDir=""):
        self.__layerCount=0
        self.__outputPaths=[]
        self.__IsInputPathAsFile(psdPath)
        self.__CheckFileFormat(psdPath)
        self.__CheckOutputDir(psdPath,outputDir)


    def __IsInputPathAsFile(self,psdPath):
        if not os.path.isfile(psdPath):
            logging.error ("指定されたファイルが見つかりません\n"+psdPath)
            raise FileNotFoundError("指定されたファイルが見つかりません\n"+psdPath)
        logging.info ("OK:"+psdPath)

    def __CheckFileFormat(self,psdPath):
        logging.info ("ファイルがpsdか確認")
        try:
            self.__psd=PSDImage.open(psdPath)
        except:
            logging.error ("指定されたファイルはpsdではありません\n"+psdPath)
            raise OSError(400,"指定されたファイルはpsdではありません",psdPath)
        logging.info ("OK")

    def __CheckOutputDir(self,psdPath,outputDir):
        logging.info ("保存先フォルダ確認")
        if outputDir=="":
            outputDir=psdPath.split(".")[0]
            logging.debug("outputDirが指定されていないため、"+outputDir+"としました")

        if os.path.isdir(outputDir):
            logging.info(outputDir +"はすでに存在します")
            updateAlert=messagebox.askquestion("上書きの確認",outputDir +"はすでに存在しますが、上書きしますか?")
            if updateAlert=="yes":
                logging.info("既存のファイル削除")
                shutil.rmtree(outputDir)
                logging.info ("OK")
            else:
                logging.info("ファイルの上書きがキャンセルされました")
                raise FileExistsError("ファイルの上書きがキャンセルされました")
        logging.info ("出力フォルダの生成")
        os.makedirs(outputDir)
        self.__outputDir=outputDir
        logging.info ("OK")

    def OutputPng(self):
        self.SetOutputPaths()
        print(self.__outputPaths)
        for layer in list(self.__psd.descendants()):
            if layer.is_group():
                continue
            #applylayeroffset
            #save

    def SetOutputPaths(self):
        for layer in list(self.__psd.descendants()):
            if layer.is_group():
                continue
            parentDirs=self.__GetParentDirs(layer)
            outputFileName=self.__LayerNameSanitize(layer)
            self.__SetOutputPath(parentDirs,outputFileName)


    def __GetParentDirs(self,layer):
        parentDirs=[]
        parent=layer.parent
        while "layers.Group" in str(type(parent)):
            parentDirs.append(self.__LayerNameSanitize(parent))
            parent=parent.parent
        return parentDirs

    def __LayerNameSanitize(self,layer):
        newName=re.sub(self.__layerNameSanitizeReg,"",layer.name)
        if newName=="":
            newName=self.__defaultLayerNasme+str(self.__layerCount)
            self.__layerCount+=1
        return newName

    def __SetOutputPath(self,parentDirs,outputFileName):
        tempPath=os.path.join(newDirPath,*parentDirs,outputFileName)
        while tempPath in self.__outputPaths:
            tempPath+=self.__paddingChar
        self.__outputPaths.append(tempPath)

def main():
    print ("ファイルがpsdか確認")
    try:
        psd=PSDImage.open(psdPath)
    except:
        messagebox.showerror("フォーマットエラー","指定したファイルはpsdではありません")
        return
    print ("OK")

    
    print ("保存先フォルダ確認")
    makeDirName=psdFileName.split(".")[0]
    newDirPath=os.path.join(psdDirPath,makeDirName)
    if os.path.isdir(newDirPath):
        updateAlert=messagebox.askquestion("上書きの確認",makeDirName +"はすでに存在しますが、上書きしますか?")
        if updateAlert=="yes":
            shutil.rmtree(newDirPath)
        else:
            return
    os.mkdir(newDirPath)
    
    print ("OK")
    badFileNameReg=re.compile('[\\/:*?"<>|]+')
    count=0
    for layer in list(psd.descendants()):
        if not layer.is_group():
            parentDirs=[]
            newFile=re.sub(badFileNameReg,"",layer.name)
            parent=layer.parent
            while "layers.Group" in str(type(parent)):
                parentDirs.append(parent.name)
                parent=parent.parent
            print (parentDirs)
            if len(parentDirs)!=0 and not os.path.isdir(os.path.join(newDirPath,*parentDirs)):
                os.makedirs(os.path.join(newDirPath,*parentDirs))

            if newFile=="":
                newFile="layer"+str(count)
            image=layer.topil()
            bg=Image.new("RGBA",[psd.width,psd.height],(0,0,0,0))
            bg.paste(image,layer.offset)

            if os.path.isfile(os.path.join(newDirPath,*parentDirs,newFile+".png")):
                tempFile=newFile+"_"+str(count)
                while os.path.isfile(os.path.join(newDirPath,*parentDirs,tempFile+".png")):
                    tempFile+="_"
                newFile=tempFile
            try:
                bg.save(os.path.join(newDirPath,*parentDirs,newFile+".png"))
                print("レイヤー名："+layer.name+"を"+os.path.join(newDirPath,*parentDirs,newFile+".png")+"に保存しました")
            except:
                print("レイヤー名："+layer.name+"の保存に失敗しました")
            count+=1


if __name__=="__main__":
    #main()
    logging.basicConfig(level=logging.INFO)
    logging.info ("ファイルパス確認")
    if(len(sys.argv) <=1):
        messagebox.showerror("ファイルをドラッグ&ドロップしてください","このソフトにpsdファイルをドラッグ&ドロップしてください")
    else:
        psdPath=sys.argv[1]
        P2P=Psd2Png(psdPath)
        P2P.OutputPng()
