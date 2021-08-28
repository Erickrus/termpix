# -*- coding: utf-8 -*-
'''
TermPix
Author: Hu, Ying-Hao (hyinghao@hotmail.com)
Version: 0.4
Last modification date: 2021-08-21

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

import argparse
import math
import numpy as np
import os
import urllib.request

from PIL import Image
from io import BytesIO

class TermPix:
    
    def __init__(self):
        self.screen_width, self.screen_height, self.wh_ratio = self._update_terminal_info()
        
        # https://notes.burke.libbey.me/ansi-escape-codes/
        self.color_mode = [48, 38] # background color, foreground color
        self.csi = '\x1b[' # Control Sequence Introducer
        self.sgr = 'm' # Select Graphics Rendition
        
        self.block = "▄"
        
        self.ansi_colors = [
        [ 0x00, 0x00, 0x00 ],[ 0x80, 0x00, 0x00 ],[ 0x00, 0x80, 0x00 ],[ 0x80, 0x80, 0x00 ],[ 0x00, 0x00, 0x80 ],
        [ 0x80, 0x00, 0x80 ],[ 0x00, 0x80, 0x80 ],[ 0xc0, 0xc0, 0xc0 ],[ 0x80, 0x80, 0x80 ],[ 0xff, 0x00, 0x00 ],
        [ 0x00, 0xff, 0x00 ],[ 0xff, 0xff, 0x00 ],[ 0x00, 0x00, 0xff ],[ 0xff, 0x00, 0xff ],[ 0x00, 0xff, 0xff ],
        [ 0xff, 0xff, 0xff ]]
        
        color_list = [ 
            0x00, 0x08, 0x12, 0x1c, 0x26, 0x30, 0x3a, 0x44,
            0x4e, 0x58, 0x5f, 0x60, 0x66, 0x76, 0x80, 0x87,
            0x8a, 0x94, 0x9e, 0xa8, 0xaf, 0xb2, 0xbc, 0xc0,
            0xc6, 0xd0, 0xd7, 0xda, 0xe4, 0xee, 0xff
        ]
        
        color_comb_1 = [
            0, 10, 15, 20, 26, 30
        ]
        color_comb_2 = [
            1, 2, 3, 4, 5, 6, 7, 8, 
            9, 11, 12, 13, 14, 16, 17, 
            18, 19, 21, 22, 24, 25, 27, 
            28, 29
        ]
        for i in range(len(color_comb_1)):
            for j in range(len(color_comb_1)):
                for k in range(len(color_comb_1)):
                    self.ansi_colors.append([
                        color_list[color_comb_1[i]],
                        color_list[color_comb_1[j]],
                        color_list[color_comb_1[k]]
                    ])
        for i in range(len(color_comb_2)):
            self.ansi_colors.append([
                color_list[color_comb_2[i]],
                color_list[color_comb_2[i]],
                color_list[color_comb_2[i]]
            ])
            
        self.ansi_colors = np.array(self.ansi_colors, dtype=np.int32)
        
        self.default_background_color = [255, 255, 255]
        self.default_background_colors = {
            True: self.default_background_color,
            False: [self._find_color_index(np.array(self.default_background_color))]
        }
        
    def gotoxy(self, x, y):
        print("%s%d;%df" % (self.csi, x, y), end='')

    def clear_screen(self):
        print("%s2J" % self.csi, end='')

    def show_cursor(self):
        print("%s?25h" % self.csi, end='')

    def hide_cursor(self):
        print("%s?25l" % self.csi, end='')


    def _update_terminal_info(self, show_grid=False):
        tsize = os.get_terminal_size()
        
        show_screen_offset = 0
        if show_grid:
            show_screen_offset = 1
        screen_width = tsize.columns - show_screen_offset * 2
        screen_height = (tsize.lines - 1 - show_screen_offset) * 2 # keep the last prompt line
        whRatio = float(screen_width) / float(screen_height)
        
        return screen_width, screen_height, whRatio
        
    def _override_tx_image_size(self, width, height):
        screen_width, screen_height = self.screen_width, self.screen_height
        overrided = False
        if (width != 0 and 
            height != 0 and
            width <= self.screen_width and 
            height <= self.screen_height
        ):
            screen_width, screen_height = width, height
            overrided = True
        return screen_width, screen_height, overrided
    
    def _set_tx_pixel(self, pixel, color_mode):
        if type(pixel) == type(int):
            pixel = np.array([pixel])
        else:   
            pixel = np.array(pixel)
        
        if pixel.size > 1:
            return (self.csi + '%d;2;%d;%d;%d'+ self.sgr) % (
                color_mode, 
                int(pixel[0]), 
                int(pixel[1]), 
                int(pixel[2])
            )
        else:
            return (self.csi + "%d;5;%d" + self.sgr) % (
                color_mode,
                int(pixel)
            )
    
    def draw_tx_im(self, im_filename, width=0, height=0, true_color=False, show_grid=False):
        self.screen_width, self.screen_height, self.wh_ratio = self._update_terminal_info(show_grid)
       
        # matches PIL ImageFile class
        if str(type(im_filename)).find('PIL') >= 0 and str(type(im_filename)).find('Image') >= 0:
            im = im_filename.convert('RGB')
        else:
            if im_filename.lower().startswith("http"):
                data =  urllib.request.urlopen(im_filename).read()
                b = BytesIO()
                b.write(data)
                im = Image.open(b).convert("RGB")
            else:
                im = Image.open(im_filename).convert("RGB")
        
        im_width, im_height = im.size
        im_wh_ratio = float(im_width) / float(im_height)
        
        screen_width, screen_height, overrided = self._override_tx_image_size(width, height)
        
        if overrided:
            im = im.resize([width, height], Image.ANTIALIAS)
        else:
            if im_wh_ratio > self.wh_ratio:
                im = im.resize([screen_width, int(screen_width / im_wh_ratio)], Image.ANTIALIAS)
            else:
                im = im.resize([int(screen_height * im_wh_ratio), screen_height], Image.ANTIALIAS)
        
        tx_width, tx_height = im.size
        data = np.array(im)
        text_mat = np.zeros([tx_width, int(math.ceil(float(tx_height)/2.))*2]).tolist()
        
        lines = []
        if not true_color:
            data = np.apply_along_axis(self._find_color_index, 2, data)
        
        for x in range(tx_width):
            text_mat[x][-1] = self._set_tx_pixel(
                self.default_background_colors[true_color], 
                self.color_mode[1] # foreground
            )
                
        line = ""
        for y in range(tx_height):
            for x in range(tx_width):
                text_mat[x][y] = self._set_tx_pixel(
                    data[y,x], 
                    self.color_mode[y % 2]
                )
                 
            if y % 2 == 1:
                line = ""
                for x in range(tx_width):
                    line += text_mat[x][y]+ \
                        text_mat[x][y-1]+ \
                        self.block+ \
                        self.csi + '0' + self.sgr
                lines.append(line)
                
        if show_grid:
            for i in range(len(lines)):
                lines[i] = ("%2d" % (i*2))+lines[i]
            line  = "  "
            for i in range(tx_width//2):
                line += "%-2d" % (i*2)
            lines.append(line)
            
        return "\n".join(lines)
    
    # this function is rewritten in python with numpy
    # referenced
    # https://github.com/hopey-dishwasher/termpix/blob/c22d061fde753fe847b40b8ccdc3ad4515d2f47d/src/lib.rs#L57
    def _find_color_index(self, pixel, start_index=0):
        return np.argmin(
            np.sum(
                (np.square(
                    self.ansi_colors[start_index:,] - 
                    np.repeat(
                        np.expand_dims(pixel, 0), 256-start_index, axis = 0
                    ).astype(np.int32)
                )).astype(np.int32), 
                axis = -1
            )
        ) + start_index
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        allow_abbrev=False, 
        usage='python3.6 termpix.py <filename|url> [--width <width>] [--height <height>] [--true-color|--true-colour]'
    )
    parser.add_argument("filename", type=str)
    parser.add_argument("--true-color", "--true-colour", action='store_true')
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--height", type=int, default=0)
    parser.add_argument("--show-grid", action='store_true')
    
    args = vars(parser.parse_args())
    tx_im = TermPix().draw_tx_im(
        args["filename"], 
        width = args["width"],
        height = args["height"],
        true_color = args["true_color"],
        show_grid= args["show_grid"]
    )
    print(tx_im)
    
