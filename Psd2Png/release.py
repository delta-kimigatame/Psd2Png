import shutil
import os
import os.path
import datetime

VERSION=1
RELEASE_DIR="release"
files=os.listdir(RELEASE_DIR)
max=0
for filename in files:
    temp=filename.split("_")
    if int(temp[1])==VERSION and int(temp[2])>max:
        max=int(temp[2])
releasename="_".join(["Psd2Png",str(VERSION),str(max+1),datetime.datetime.today().strftime("%Y%m%d")])


shutil.make_archive(os.path.join(RELEASE_DIR,releasename),"zip",base_dir="dist")