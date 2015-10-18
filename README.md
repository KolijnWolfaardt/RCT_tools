# RCT_tools
Some tools for working with RollerCoaster Tycoon 2's files. Most of these require the original game.


### exportSprites.py ###
This script output sprites from the g1.dat file. It has options to set which sprites to export, and which color palettes to use. For more info run it with the -h flag.

```
python exportSprites.py -h
```

The script requires [numpy](http://www.numpy.org/) and [PIL](http://www.pythonware.com/products/pil/). Details about the script are [here](zeroFortySeven.com/2015/10/Extracting-RCT-Sprites.html)