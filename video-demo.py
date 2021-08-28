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
from termpix import TermPix
from PIL import Image
from io import BytesIO

import datetime
import imageio
import numpy as np
import os
import pyaudio
import sys
import time
import urllib.request
import wave

import threading


class AudioThread(threading.Thread):
    def __init__(self, audio_filename):
        threading.Thread.__init__(self)
        self.audio_filename = audio_filename
        self.is_terminated = False

    def run(self):
        CHUNK = 1024
        wave_file = wave.open(self.audio_filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wave_file.getsampwidth()),
            channels=wave_file.getnchannels(),
            rate=wave_file.getframerate(),
            output=True
        )
        data = wave_file.readframes(CHUNK)
        while data != b'' and not self.is_terminated :
            stream.write(data)
            data = wave_file.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        os.system("rm %s" % self.audio_filename)

'''
apt install sox ffmpeg 
apt install portaudio
pip3 install imageio imageio-ffmpeg pyaudio
'''

def wrapper(mp4_filename, func):
    t = TermPix()
    t.hide_cursor()
    t.clear_screen()
    t.gotoxy(1,1)
    audio_thread = AudioThread(mp4_filename)
    try:
        func(t, mp4_filename, audio_thread) # play_video
    except KeyboardInterrupt:
        audio_thread.is_terminated = True
        audio_thread.join()
        pass
    t.show_cursor()
    t.clear_screen()
    t.gotoxy(1,1)

def play_video(t, mp4_filename, audio_thread):

    support_audio = True
    timestamp = int(datetime.datetime.now().timestamp())
    ext = os.path.splitext(mp4_filename)[-1]
    try:
        os.mkdir("tmp")
    except:
        pass
    proposed_video_filename = "tmp/tp_%s%s" % (timestamp, ext.lower())
    proposed_audio_filename = "tmp/tp_%s%s" % (timestamp, '.wav')

    if mp4_filename.lower() == 'camera':
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
    if support_audio:
        print("support audio")
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
            print(t.draw_tx_im(im, true_color=True))
            t.gotoxy(1,1)
        # else: 
            # current_time is left behind, skip the drawing
        
        current_time = datetime.datetime.now()
        sleep_time = frame_duration - (current_time - play_start_time)/sec + float(i) * frame_duration
        if sleep_time > 0.:
            time.sleep(sleep_time)
    v_in.close()

def main(mp4_filename):
    wrapper(mp4_filename, play_video)

if __name__ == "__main__":
    main(sys.argv[1])

