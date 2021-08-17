# -*- coding: utf-8 -*-
'''
TermPix
Author: Hu, Ying-Hao (hyinghao@hotmail.com)
Version: 0.1
Last modification date: 2021-08-16

Copyright 2021 Hu, Ying-Hao

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

'''

import math
import numpy as np
import os
import sys
import urllib.request

from PIL import Image
from io import BytesIO

class TermPix:
    def __init__(self):
        tsize = os.get_terminal_size()
        
        self.screenWidth = tsize.columns
        self.screenHeight = tsize.lines * 2
        self.whRatio = float(self.screenWidth) / float(self.screenHeight)
        
        # https://notes.burke.libbey.me/ansi-escape-codes/
        self.colorMode = [38, 48] # foreground color, background color
        self.CSI = '\x1b[' # Control Sequence Introducer
        self.SGR = 'm' # Select Graphics Rendition
        
        self.block = "▄"
    
    def draw(self, imFilename):
        
        if imFilename.lower().startswith("http"):
            data =  urllib.request.urlopen(imFilename).read()
            b = BytesIO()
            b.write(data)
            im = Image.open(b).convert("RGB")
        else:
            im = Image.open(imFilename).convert("RGB")
        imWidth, imHeight = im.size
        imWhRatio = float(imWidth) / float(imHeight)
        if imWhRatio >self.whRatio:
            im = im.resize([self.screenWidth, int(self.screenWidth / imWhRatio)], Image.ANTIALIAS)
        else:
            im = im.resize([int(self.screenHeight * imWhRatio), self.screenHeight], Image.ANTIALIAS)
        
        txWidth, txHeight = im.size
        data = np.array(im)
        textMat = np.zeros([txWidth, int(math.ceil(float(txHeight)/2.))*2]).tolist()
        
        for x in range(txWidth):
            textMat[x][-1] = self.CSI + '38;2;255;255;255' + self.SGR
        
        for y in range(txHeight):
            for x in range(txWidth):
                textMat[x][y] = (self.CSI + '%d;2;%d;%d;%d'+ self.SGR) %(
                    self.colorMode[y % 2], 
                    data[y,x,0], data[y,x,1], data[y,x,2] # RGB
                )
            if y % 2 == 0:
                line = ""
                for x in range(txWidth):
                    line += "".join([
                        textMat[x][y-1],
                        textMat[x][y],
                        self.block,
                        self.CSI + '0' + self.SGR])
                print(line)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        t = TermPix()
        t.draw(sys.argv[1])
    else:
        print("Usage: python3.6 termpix.py <image_filename>")

