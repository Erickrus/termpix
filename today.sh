#!/bin/sh
ZH_FILENAME=~/Pictures/BING_`date +"%Y%m%d"`_ZH.txt
EN_FILENAME=~/Pictures/BING_`date +"%Y%m%d"`_EN.txt

if [ ! -f $ZH_FILENAME ]; then
termpix https://cn.bing.com/`curl -s "https://cn.bing.com/?ensearch=1" | tr -s ">" "\n" | grep background-image | grep jpg | head -n 1 | cut -d \( -f 2 | cut -d \) -f 1` --true-color -o $ZH_FILENAME
fi

if [ ! -f $EN_FILENAME ]; then
termpix https://cn.bing.com/`curl -s cn.bing.com | tr -s ">" "\n" | grep background-image | tr -s "<" "\n" | grep jpg | cut -d \( -f 2 | cut -d \) -f 1` --true-color -o $EN_FILENAME
fi

