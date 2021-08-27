from termpix import TermPix
from PIL import Image

import datetime
import imageio
import numpy as np
import sys
import time
"""
apt install sox ffmpeg
pip3 install imageio imageio-ffmpeg
"""
def wrapper(mp4_filename, func):
    t = TermPix()
    t.hide_cursor()
    t.clear_screen()
    t.gotoxy(1,1)
    try:
        func(t, mp4_filename)
    except KeyboardInterrupt:
        pass
    t.show_cursor()
    t.clear_screen()

def play_video(t, mp4_filename):
    # v_in = imageio.get_reader('<video0>')
    v_in = imageio.get_reader(mp4_filename, 'ffmpeg')
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

