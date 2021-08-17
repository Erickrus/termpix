Draw images in an ANSI terminal! Requires that your terminal can show ANSI colours, and uses a font that can show the 'bottom half block' character (▄).

Usage: `python3.6 termpix.py <filename|url>`

filename can be any `image` file readable by the python 'PIL' library. 

It will fill as much of the terminal as possible, while keping the aspect ratio of the input image. 

Try this command:
`python3.6 termpix.py https://img.blogs.es/anexom/wp-content/uploads/2020/10/mario-destacada_E.jpg` . And you will see:

![](https://github.com/Erickrus/termpix/blob/main/demo.png)

It is much inspired by this repository: 
https://github.com/hopey-dishwasher/termpix
