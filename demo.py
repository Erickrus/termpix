# -*- coding: utf-8 -*-
'''
TermPix
Author: Hu, Ying-Hao (hyinghao@hotmail.com)
Version: 0.3
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
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

def make_heart_shape():
    t=np.arange(0,2*np.pi,0.1)
    x=16*np.sin(t)**3
    y=13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)
    return x, y

if __name__ == "__main__":

    x, y = make_heart_shape()
    plt.plot(x,y,color="red")

    plt.axis('off')
    b = BytesIO()
    plt.savefig(b)
    im = Image.open(b)

    print(TermPix().draw_tx_im(im, true_color=True))


