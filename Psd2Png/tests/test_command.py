import unittest

import subprocess
import shutil
import glob
import os
import os.path

from PIL import Image

class TestCommanrline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(os.path.join("dist","Psd2Png.exe")):
            import setup
        cls.command=[os.path.join("dist","Psd2Png.exe"),"--noalert"]

    def setUp(self):
        self.command=[os.path.join("dist","Psd2Png.exe"),"--noalert"]
        for rmPath in glob.glob("tests/testPsd/*"):
            if os.path.isdir(rmPath):
                shutil.rmtree(rmPath)

    def testNotCommand(self):
        proc=subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding="cp932")
        std=proc.communicate()
        self.assertIn("このソフトにpsdファイルをドラッグ&ドロップしてください",std[1])

        
    def test_PsdFileIsNotFound(self):
        self.command.append(os.path.join("tests","testPsd","NotExist.psd"))
        proc=subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding="cp932")
        stderr=proc.communicate()[1]
        self.assertIn("ERROR:PSD2Png:指定されたファイルが見つかりません\n"+os.path.join("tests","testPsd","NotExist.psd"),stderr)

        
    def test_FileIsNotPsd(self):
        self.command.append(os.path.join("tests","testPsd","PngFile.psd"))
        proc=subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding="cp932")
        stderr=proc.communicate()[1]
        self.assertIn("ERROR:PSD2Png:指定されたファイルはpsdではありません\n"+os.path.join("tests","testPsd","PngFile.psd"),stderr)
        
    def testSimpleMultiLayer(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append("--outlist")
        proc=subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding="cp932")
        stdout=proc.communicate()[0].split("\n")
        stdout.remove("")
        self.assertEqual(stdout,[os.path.join("tests","testPsd","SimpleMultiLayer","red"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","blue"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","green"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","alpha")])
        
    def testSimpleOutputPngMultiLayer(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","red.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","green.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png")))

        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","red.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","green.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()

    def testUpdateError(self):
        os.makedirs(os.path.join("tests","testPsd","SimpleMultiLayer"))
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        proc=subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding="cp932")
        stderr=proc.communicate()[1]
        self.assertIn("ERROR:PSD2Png:既にファイルが存在するため、出力を中断しました",stderr)
        
    def testUpdateForce(self):
        os.makedirs(os.path.join("tests","testPsd","SimpleMultiLayer"))
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append("--force")
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","red.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","green.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png")))

        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","red.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","green.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()
        
    def testOutputDir(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append("--outdir="+os.path.join("tests","testPsd","output"))
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output","red.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output","blue.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output","green.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output","alpha.png")))

        im=Image.open(os.path.join("tests","testPsd","output","red.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","output","green.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","output","blue.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","output","alpha.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()
        
    def testOutputPaths(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test1"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test2"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test3"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test4"))
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output_paths","test1.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output_paths","test2.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output_paths","test3.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","output_paths","test4.png")))

        im=Image.open(os.path.join("tests","testPsd","output_paths","test1.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","output_paths","test2.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","output_paths","test3.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","output_paths","test4.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()

    def testOutputPathsTooMany(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test1"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test2"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test3"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test4"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test5"))
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","red.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","green.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png")))

        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","red.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","green.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()

    def testOutputPathsTooLess(self):
        self.command.append(os.path.join("tests","testPsd","SimpleMultiLayer.psd"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test1"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test2"))
        self.command.append(os.path.join("tests","testPsd","output_paths","test3"))
        proc=subprocess.Popen(self.command,shell=True,encoding="cp932")
        proc.wait()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","red.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","green.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png")))

        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","red.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","green.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","blue.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","SimpleMultiLayer","alpha.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()