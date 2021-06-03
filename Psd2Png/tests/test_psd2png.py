import unittest

import shutil
import glob
import os
import os.path
import logging

from PIL import Image

from Psd2Png import Psd2Png

class TestPsd2PngBase(unittest.TestCase):
    #テスト実行の都度、過去に生成したフォルダを削除します。
    def setUp(self):
        self.logger = logging.getLogger("TEST")
        for rmPath in glob.glob("tests/testPsd/*"):
            if os.path.isdir(rmPath):
                shutil.rmtree(rmPath)

class TestInputError(TestPsd2PngBase):
    def test_PsdFileIsNotFound(self):
        with self.assertLogs("TEST",level=logging.ERROR) as cm:
            with self.assertRaises(FileNotFoundError):
                Psd2Png(os.path.join("tests","testPsd","NotExist.psd"),self.logger)
        self.assertIn("ERROR:TEST:指定されたファイルが見つかりません",str(cm))
            
    def test_FileIsNotPsd(self):
        with self.assertLogs("TEST",level=logging.ERROR) as cm:
            with self.assertRaises(OSError):
                Psd2Png(os.path.join("tests","testPsd","PngFile.psd"),self.logger)
        self.assertIn("ERROR:TEST:指定されたファイルはpsdではありません",str(cm))

class TestMakeOutputPaths(TestPsd2PngBase):
    def testSimpleMultiLayer(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","SimpleMultiLayer.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","SimpleMultiLayer","red"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","blue"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","green"),
                                          os.path.join("tests","testPsd","SimpleMultiLayer","alpha")])
        
    def testLayerNamecp932(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNamecp932.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","LayerNamecp932","あ")])
        
    def testLayerNameUtf8(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNameUtf8.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","LayerNameUtf8","あ")])

    def testLayerNameIsNone(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNameIsNone.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","LayerNameIsNone","LayerNameIsNone")])
        
    def testLayerNameIsDuplication(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNameDuplication.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","LayerNameDuplication","test__"),
                                          os.path.join("tests","testPsd","LayerNameDuplication","test"),
                                          os.path.join("tests","testPsd","LayerNameDuplication","test_"),
                                          os.path.join("tests","testPsd","LayerNameDuplication","test___")])
        
    def testBadLayerName(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","BadLayerName.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","BadLayerName","test"),
                                          os.path.join("tests","testPsd","BadLayerName","test2"),
                                          os.path.join("tests","testPsd","BadLayerName","test3"),
                                          os.path.join("tests","testPsd","BadLayerName","test4"),
                                          os.path.join("tests","testPsd","BadLayerName","test5"),
                                          os.path.join("tests","testPsd","BadLayerName","test6"),
                                          os.path.join("tests","testPsd","BadLayerName","test7"),
                                          os.path.join("tests","testPsd","BadLayerName","layer0"),
                                          os.path.join("tests","testPsd","BadLayerName","layer1")])
    def testGroup(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","Group.psd"),self.logger)
        p2p.SetOutputPaths()
        self.assertEqual(p2p.outputPaths,[os.path.join("tests","testPsd","Group","layer0","NoneGroupName"),
                                          os.path.join("tests","testPsd","Group","BadGroupName","badlayer"),
                                          os.path.join("tests","testPsd","Group","日本語グループ","日本語レイヤー"),
                                          os.path.join("tests","testPsd","Group","NoGroup"),
                                          os.path.join("tests","testPsd","Group","SimpleGroup","Layer1"),
                                          os.path.join("tests","testPsd","Group","SimpleGroup","NestedGroup","NestedLayer")])

class TestOutputPng(TestPsd2PngBase):
    def testSimpleMultiLayer(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","SimpleMultiLayer.psd"),self.logger)
        p2p.OutputPng()
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
        
    def testGroup(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","Group.psd"),self.logger)
        p2p.OutputPng()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","layer0","NoneGroupName.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","BadGroupName","badlayer.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","日本語グループ","日本語レイヤー.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","NoGroup.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","SimpleGroup","Layer1.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","Group","SimpleGroup","NestedGroup","NestedLayer.png")))
        
    def testLayerNameIsNone(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNameIsNone.psd"),self.logger)
        p2p.OutputPng()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","LayerNameIsNone","LayerNameIsNone.png")))
        im=Image.open(os.path.join("tests","testPsd","LayerNameIsNone","LayerNameIsNone.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0))
        im.close()

    def testLayerOffset(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","offset.psd"),self.logger)
        p2p.OutputPng()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","offset","bgi.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","offset","offset.png")))
        im=Image.open(os.path.join("tests","testPsd","offset","offset.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        self.assertEqual(im.getpixel((0,1)),(0,0,0,0))
        self.assertEqual(im.getpixel((0,2)),(0,0,0,0))
        self.assertEqual(im.getpixel((1,0)),(0,0,0,0))
        self.assertEqual(im.getpixel((1,1)),(0,0,255,255))
        self.assertEqual(im.getpixel((1,2)),(0,0,0,0))
        self.assertEqual(im.getpixel((2,0)),(0,0,0,0))
        self.assertEqual(im.getpixel((2,1)),(0,0,0,0))
        self.assertEqual(im.getpixel((2,2)),(0,0,0,0))
        im.close()
        im=Image.open(os.path.join("tests","testPsd","offset","bgi.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        self.assertEqual(im.getpixel((0,1)),(255,0,0,255))
        self.assertEqual(im.getpixel((0,2)),(255,0,0,255))
        self.assertEqual(im.getpixel((1,0)),(255,0,0,255))
        self.assertEqual(im.getpixel((1,1)),(255,0,0,255))
        self.assertEqual(im.getpixel((1,2)),(255,0,0,255))
        self.assertEqual(im.getpixel((2,0)),(255,0,0,255))
        self.assertEqual(im.getpixel((2,1)),(255,0,0,255))
        self.assertEqual(im.getpixel((2,2)),(255,0,0,255))
        im.close()
        
    def testSimpleMultiLayerOutputPathsOverride(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","SimpleMultiLayer.psd"),self.logger)
        p2p.outputPaths=[os.path.join("tests","testPsd","override","test1"),
                         os.path.join("tests","testPsd","override","test2"),
                         os.path.join("tests","testPsd","override","test3"),
                         os.path.join("tests","testPsd","override","test4")]
        p2p.OutputPng()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","override","test1.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","override","test2.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","override","test3.png")))
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","override","test4.png")))

        im=Image.open(os.path.join("tests","testPsd","override","test1.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0,255))
        im=Image.open(os.path.join("tests","testPsd","override","test2.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,255,255))
        im=Image.open(os.path.join("tests","testPsd","override","test3.png"))
        self.assertEqual(im.getpixel((0,0)),(0,255,0,255))
        im=Image.open(os.path.join("tests","testPsd","override","test4.png"))
        self.assertEqual(im.getpixel((0,0)),(0,0,0,0))
        im.close()
        
    def testLayerNameIsNoneOutputPathsOverride(self):
        p2p=Psd2Png(os.path.join("tests","testPsd","LayerNameIsNone.psd"),self.logger)
        p2p.outputPaths=[os.path.join("tests","testPsd","override","test1")]
        p2p.OutputPng()
        self.assertTrue(os.path.isfile(os.path.join("tests","testPsd","override","test1.png")))
        im=Image.open(os.path.join("tests","testPsd","override","test1.png"))
        self.assertEqual(im.getpixel((0,0)),(255,0,0))
        im.close()