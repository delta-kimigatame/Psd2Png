import sys
import shutil
import os
import os.path
import re
from tkinter import messagebox
from PIL import Image
from psd_tools import PSDImage

def main():
    print ("ファイルパス確認")
    if(len(sys.argv) <=1):
        messagebox.showerror("ファイルをドラッグ&ドロップしてください","このソフトにpsdファイルをドラッグ&ドロップしてください")
        return
    psdPath=sys.argv[1]
    psdDirPath,psdFileName=os.path.split(psdPath)
    if not os.path.isfile(psdPath):
        messagebox.showerror("ファイルが見つかりません","指定されたファイルが見つかりません")
        return
    
    print ("OK")
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
            try:
                image.save(os.path.join(newDirPath,*parentDirs,newFile+".png"))
                print("レイヤー名："+layer.name+"を"+os.path.join(newDirPath,*parentDirs,newFile+".png")+"に保存しました")
            except:
                print("レイヤー名："+layer.name+"の保存に失敗しました")
            count+=1




if __name__=="__main__":
    main()
