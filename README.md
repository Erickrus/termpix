# termpix

Draw images in an ANSI terminal! Requires that your terminal can show ANSI colours, and uses a font that can show the 'bottom half block' character (▄).

Usage: `python3.6 termpix.py <filename|url> [--width <width>] [--height <height>] [--true-color|--true-colour]`

filename or url can be any `image` file readable by the python 'PIL' library. 

It will fill as much of the terminal as possible, while keeping the aspect ratio of the input image. Use --width or --height to override this.

Try this command:
`python3.6 termpix.py https://img.blogs.es/anexom/wp-content/uploads/2020/10/mario-destacada_E.jpg --true-color` . And you will see:

![Demo](https://github.com/Erickrus/termpix/blob/main/demo.png)

This library is also extended to play video in terminal, you can try the `python3.6 video-demo.py <mp4_filename>`

[![asciicast](https://asciinema.org/a/yuogBz7sZaSwLmRBN4BGcTv6v.svg)](https://asciinema.org/a/yuogBz7sZaSwLmRBN4BGcTv6v)

This project is much inspired by the following repository: 
https://github.com/hopey-dishwasher/termpix

# Installing
`pip3 install -r requirements.txt
`

# License
Apache 2.0 license

