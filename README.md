# termpix

Draw images in an ANSI terminal! Requires that your terminal can show ANSI colours, and uses a font that can show the 'bottom half block' character (▄).

Usage: `python3.9 termpix.py <filename|url> [--width <width>] [--height <height>] [--true-color|--true-colour]`

filename or url can be any `image` file readable by the python 'PIL' library or can be any `video` file readable by `imageio`. If you type camera as the filename, you can view your camera video.

It will fill as much of the terminal as possible, while keeping the aspect ratio of the input image. Use --width or --height to override this.

Try this command:
`python3.9 termpix.py https://img.blogs.es/anexom/wp-content/uploads/2020/10/mario-destacada_E.jpg --true-color` . And you will see:

[![asciicast](https://asciinema.org/a/cEW7FK66bmr0wsmRNcMpocx1D.svg)](https://asciinema.org/a/cEW7FK66bmr0wsmRNcMpocx1D)

This library is also extended to play video in terminal (with audio), you can try the `python3.9 termpix.py <mp4_filename>`

[![asciicast](https://asciinema.org/a/yuogBz7sZaSwLmRBN4BGcTv6v.svg)](https://asciinema.org/a/yuogBz7sZaSwLmRBN4BGcTv6v)

This project is much inspired by the following repository: 
https://github.com/hopey-dishwasher/termpix

# Installing
`# if you want to play video, followings are required`

`# apt install portaudio ffmpeg`

`pip3 install -r requirements.txt`

# License
Apache 2.0 license

