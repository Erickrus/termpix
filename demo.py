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

x = np.linspace(0., np.pi*2.)
y = np.log(x)
y2 = np.sin(x)
y3 = np.cos(x)
plt.plot(x, y)
plt.plot(x, y2)
plt.plot(x, y3)

plt.axis('off')
b = BytesIO()
plt.savefig(b)
im = Image.open(b)

print(TermPix().draw_tx_im(im))


