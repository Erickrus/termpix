#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
TermPix
Author: Hu, Ying-Hao (hyinghao@hotmail.com)
Version: 0.5
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
__author__ = "Hu, Ying-Hao<hyinghao@hotmail.com>"
__copyright__ = "Copyright 2021 Hu, Ying-Hao"
__license__ = "the Apache License, Version 2.0"
__version__ = "0.5.2"

import argparse
import datetime
import math
import numpy as np
import os
import urllib.request
import tempfile
import termios
import threading
import time
import sys

from ctypes import *

from PIL import Image
from io import BytesIO

try:
    import pyheif
except:
    pass

class AudioThread(threading.Thread):
    def __init__(self, audio_filename):
        threading.Thread.__init__(self)
        self.audio_filename = audio_filename
        self.is_terminated = False

    def run(self):
        '''# this make the sound not sync with video
        if sys.platform.lower() == "linux":
            # From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
            # $ grep -rn snd_lib_error_handler_t
            # include/error.h:59:typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *fmt, ...) /* __attribute__ ((format (printf, 5, 6))) */;
            # Define our error handler type
            ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
            def py_error_handler(filename, line, function, err, fmt):
                pass
            c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

            asound = cdll.LoadLibrary('libasound.so.2')
            # Set error handler
            asound.snd_lib_error_set_handler(None)
        '''

        import pyaudio
        import wave
        wave_file = wave.open(self.audio_filename, 'rb')
        p = pyaudio.PyAudio()
        chunk_size = 1024

        stream = p.open(
            format=p.get_format_from_width(wave_file.getsampwidth()),
            channels=wave_file.getnchannels(),
            rate=wave_file.getframerate(),
            output=True
        )
        data = wave_file.readframes(chunk_size)
        while data != b'' and not self.is_terminated:
            try:
                stream.write(data)
            except:
                pass
            data = wave_file.readframes(chunk_size)
        stream.stop_stream()
        stream.close()
        p.terminate()
        os.system("rm %s" % self.audio_filename)

class Terminal:
    def __init__(self):
        self.csi = '\x1b[' # Control Sequence Introducer
        self.sgr = 'm' # Select Graphics Rendition

    def getkey(self):
        fd = sys.stdin.fileno()
        o = termios.tcgetattr(fd)
        n = termios.tcgetattr(fd)
        n[3] = n[3] & ~termios.ICANON & ~termios.ECHO
        n[6][termios.VMIN] = 1
        n[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, n)
        c = None
        try:
            c = os.read(fd, 1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, o)
        return c.decode('utf-8')

    def is_tty(self):
        res = False
        try:
            res = type(os.environ["SSH_TTY"]) == str
        except:
            pass
        return res

    def gotoxy(self, x, y):
        print("%s%d;%df" % (self.csi, x, y), end='')

    def clear_screen(self):
        print("%s2J" % self.csi, end='')

    def show_cursor(self):
        print("%s?25h" % self.csi, end='')

    def hide_cursor(self):
        print("%s?25l" % self.csi, end='')

class TermPix:

    def __init__(self):

        self.heif_supported = True
        try:
            import pyheif
        except:
            self.heif_supported = False

        self.term = Terminal()
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

    def draw_tx_im(self, im_filename, width=0, height=0, true_color=False, show_grid=False, cinema_mode=False):
        self.screen_width, self.screen_height, self.wh_ratio = self._update_terminal_info(show_grid)

        # matches PIL ImageFile class
        if str(type(im_filename)).find('PIL') >= 0 and str(type(im_filename)).find('Image') >= 0:
            im = im_filename.convert('RGB')
        else:
            if im_filename.lower().startswith("http"):
                try:
                    data =  urllib.request.urlopen(im_filename).read()
                    b = BytesIO()
                    b.write(data)
                    im = Image.open(b).convert("RGB")
                except:
                    print("failed to load url: %s" % im_filename)
                    sys.exit(1)
            else:
                if im_filename.lower().endswith("heic") and self.heif_supported:
                    im = pyheif.read(im_filename)
                    im = Image.frombytes(mode = im.mode, size=im.size, data = im.data).convert("RGB")
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

        if cinema_mode:
            show_grid = False
            lines = self.cinema(im, lines, true_color)

        if show_grid:
            for i in range(len(lines)):
                lines[i] = ("%2d" % (i*2))+lines[i]
            line  = "  "
            for i in range(tx_width//2):
                line += "%-2d" % (i*2)
            lines.append(line)

        return "\n".join(lines)

    def cinema(self, im, lines, true_color):
        # use text approach to center the image
        # in the mean time, fill the rest screen with black_block
        c = [0, 0, 0]
        if not true_color:
            c = [self._find_color_index(np.array(c))]

        black_block = "".join([
            self._set_tx_pixel(c, self.color_mode[0]),
            self._set_tx_pixel(c, self.color_mode[1]),
            self.block,
            self.csi + '0' + self.sgr
        ])
        black_block_len = len(black_block)

        # horizontal padding
        horiz_padding_size = self.screen_width // 2 - im.size[0] // 2
        horiz_line = ""
        for i in range(horiz_padding_size):
            horiz_line += black_block
        for i in range(len(lines)):
            lines[i] = horiz_line + lines[i] + horiz_line[:-black_block_len]

        # vertical padding
        vert_line = ""
        for i in range(self.screen_width):
            vert_line += black_block
        vert_line_size = self.screen_height//4 - len(lines) // 2
        for _ in range(vert_line_size):
            lines.insert(0, vert_line)

        for _ in range(self.screen_height//2 - len(lines)):
                lines.append(vert_line)
        return lines


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


    def video_wrapper(self, mp4_filename, func, true_color, mirror):
        self.term.hide_cursor()
        self.term.clear_screen()
        self.term.gotoxy(1, 1)
        audio_thread = AudioThread(mp4_filename)
        try:
            # this probably work in linux system
            if sys.platform.lower() == "linux" and not self.term.is_tty():
                os.system("jack_control stop > /dev/null")
                os.system("pulseaudio --kill")
                os.system("jack_control start > /dev/null")
                os.system("pulseaudio --start")
                #time.sleep(0.05)
            func(mp4_filename, audio_thread, true_color, mirror) # play_video
        except KeyboardInterrupt:
            audio_thread.is_terminated = True
            #audio_thread.join()
            #pass

        self.term.show_cursor()
        self.term.clear_screen()
        self.term.gotoxy(1, 1)

    def play_video(self, mp4_filename, true_color=True, mirror=False):
        self.video_wrapper(mp4_filename, self._play_video, true_color, mirror)

    def _play_video(self, mp4_filename, audio_thread, true_color, mirror):
        import imageio
        support_audio = True
        timestamp = int(datetime.datetime.now().timestamp())
        ext = os.path.splitext(mp4_filename)[-1]

        temp_dir = tempfile.gettempdir()
        proposed_video_filename = "%s/tp_%s%s" % (temp_dir, timestamp, ext.lower())
        proposed_audio_filename = "%s/tp_%s%s" % (temp_dir, timestamp, '.wav')

        if mp4_filename.lower() == 'camera':
            if self.term.is_tty():
                raise Exception("start camera via tty is not allowed")
            v_in = imageio.get_reader('<video0>')
            support_audio = False
        elif mp4_filename.lower().startswith("http"):
            data =  urllib.request.urlopen(mp4_filename).read()
            with open(proposed_video_filename, "wb") as f:
                f.write(data)
            os.system("ffmpeg -y -v quiet -i %s %s" % (proposed_video_filename, proposed_audio_filename))
            os.system("rm %s" % proposed_video_filename)
            v_in = imageio.get_reader(BytesIO(data), 'ffmpeg')
            support_audio = True
        else:
            v_in = imageio.get_reader(mp4_filename, 'ffmpeg')
            os.system("ffmpeg -y -v quiet -i %s %s" % (mp4_filename, proposed_audio_filename))
            support_audio = True

        # audio part goes here
        if support_audio and not self.term.is_tty(): # you wont get audio from ssh client
            audio_thread.audio_filename = proposed_audio_filename
            audio_thread.start()

        fps = v_in.get_meta_data()['fps']

        play_start_time = datetime.datetime.now()
        frame_duration = 1. / float(fps)

        sec = datetime.timedelta(seconds=1.)
        for i, im in enumerate(v_in):
            current_time = datetime.datetime.now()
            if (current_time - play_start_time)/sec <= float(i+1) * frame_duration:
                im = Image.fromarray(im)
                if mp4_filename.lower() == 'camera' and mirror:
                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                curr_tx_im = self.draw_tx_im(im, true_color=true_color, cinema_mode=True)
                print(curr_tx_im)
                self.term.gotoxy(1,1)
            # else:
                # current_time is left behind, skip the drawing

            current_time = datetime.datetime.now()
            sleep_time = frame_duration - (current_time - play_start_time)/sec + float(i) * frame_duration
            if sleep_time > 0.:
                time.sleep(sleep_time)
        v_in.close()


def main():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        usage='python3.6 termpix.py <filename|url> [--width <width>] [--height <height>] [--true-color|--true-colour]'
    )
    parser.add_argument("filename", type=str)
    parser.add_argument("--true-color", "--true-colour", action='store_true')
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--height", type=int, default=0)
    parser.add_argument("--show-grid", action='store_true')
    parser.add_argument("--mirror", action='store_true') # only used in the camera mode
    # parser.add_argument("--cinema_mode", "-c")
    parser.add_argument("--output", "-o", type=str, nargs=1)

    args = vars(parser.parse_args())
    if (args["filename"].lower().endswith("mp4") or
        args["filename"].lower().endswith("mov") or
        args["filename"].lower() == "camera"):
        TermPix().play_video(
            args["filename"],
            true_color = args["true_color"],
            mirror = args["mirror"]
        )
    else:
        tx_im = TermPix().draw_tx_im(
            args["filename"],
            width = args["width"],
            height = args["height"],
            true_color = args["true_color"],
            show_grid= args["show_grid"]
        )
        if args["output"] != None:
            with open(args["output"][0], "w") as f:
                f.write(tx_im)
        else:
            print(tx_im)

if __name__ == "__main__":
    main()
