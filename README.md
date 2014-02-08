watch wilmaa with coop (wwwc)
=============================

wwwc is a script to watch wilmaa TV with a player (of your choice).
There is no need for a webbrowser or a flashplayer.

limitation
----------

__NOTE__
_THIS MOST LIKELY WORKS ONLY FROM SWITZERLAND, SINCE THE IPTV SERVICE
FROM WILMAA.COM IS ONLY AVAILABLE TO SWISS IP ADDRESSES._


see: http://github.com/DerCoop/wwwc    
Copyright: DerCoop 2014



requirements
------------

__deprecated since 0.1.1__
This script is based on the following binary programs:

     o wget


Installation
------------

Simply run the setup.py script to install wwwc.

> ./setup.py install


Usage
-----

type
> watch_wilma --help

to get a short summary of the commandline options

__NOTE__
Use the _config.ini_ file! At the moment not all options were parsed (do not use different http and https proxy settings!)


If no channel is choosen via commandline, an interactive dialog show you all available channels!

wwwc will save the stream in up to two files at your configured tmp folder. 
The next file is automatically selected if filesize of the current file exceeded.
The filenames are "0" and "1"

For watching the stream, it is possible to create a playlist with this two files and set the loop option!


Feel free to watch wilmaa with coop ;)

Have Fun!
