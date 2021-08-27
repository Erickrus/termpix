from termpix import TermPix
from PIL import Image

import imageio
import numpy as np
import sys
import time
"""
apt install sox ffmpeg
pip3 install imageio imageio-ffmpeg
"""
def main(mp4_filename):
    t = TermPix()

    v_in = imageio.get_reader(mp4_filename, 'ffmpeg')
    fps = v_in.get_meta_data()['fps']

    for i, im in enumerate(v_in):
        im = Image.fromarray(im)
        print(t.draw_tx_im(im, true_color=True))
        t.gotoxy(1,1)
        time.sleep(1. / float(fps))
    v_in.close()
    t.clear_screen()

if __name__ == "__main__":
    main(sys.argv[1])
