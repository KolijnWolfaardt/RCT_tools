import struct
import math
import os.path
import argparse

from PIL import Image

"""
This script takes some sprites from an already exported spritesheet and creates
an animated gif from them.

Before this script is usefull, you need to export the sprites you want with the 
correct colors changed, and you need to know the indexes of the sprites.

This script just assembles the sprites into an animated gif, it has no knowledge
of what order to put them in, or what the timing was in the original game.
A lot of post-processing might be required.
"""


def parse_sprite_pattern(pattern):
    parts = pattern.split(',')

    sprite_pattern = []

    # Two options: this can be number or a range. If its a range it will 
    # contain 1 or two semicolons
    for part in parts:

        if ':' in part:
            ranges = part.split(":")
            if len(ranges) == 2:
                start = int(ranges[0])
                stop = int(ranges[1])
                sprite_pattern += list(range(start,stop))

            elif len(ranges) == 3:
                start = int(ranges[0])
                stop = int(ranges[1])
                step = int(ranges[2])
                sprite_pattern += list(range(start,stop, step))

            else:
                print(f"Could not parse this part of the sprite pattern: {part}")

        else:
            sprite_pattern.append(int(part))
    return sprite_pattern

def generate_sprite(sprite_directory, output_file, sprite_pattern):

    # This stores the actual images when they are loaded
    sprites = [None] * len(sprite_pattern)

    # This dict maintains the details of all the sprites we need, but only a single
    # copy for every sprite - we might insert the same one in multiple locations
    sprite_details = {}

    for i, value in enumerate(sprite_pattern):
        if value not in sprite_details:
            sprite_details[value] = {"indexes": []}
        sprite_details[value]['indexes'].append(i)

    with open(f"{sprite_directory}/sprites.nfo") as f:
        
        for line in f.readlines():
            parts = line.split(',')
            # All the positions are ints, except [3], which is a hex value
            # This was probably a bad idea, but stuck with it for now.
            info = [int(a) for a in parts[0:3]] + [int (parts[3],base=16)] + [int(a) for a in parts[4::]]

            # Check if info[2] (the index) is required
            if info[2] in sprite_details:
                sprite_details[info[2] ]["details"] = info

    # We don't want to open the images multiple times, so create a lookup of all the spritesheets to load
    required_spritesheets =  {}
    for key, value in sprite_details.items():

        if value["details"][0] not in required_spritesheets:
            required_spritesheets[value["details"][0]] = []
        
        required_spritesheets[value["details"][0]].append(key)

    # Find the Maximum X and Y sizes required. Each sprite has a size and a x and y offset. 
    max_x_left = 0
    max_x_right = 0
    max_y_top = 0
    max_y_bottom = 0
    for key, sprite in sprite_details.items():
        width = sprite["details"][4]
        height = sprite["details"][5]
        sprite_x_offset = sprite["details"][6]
        sprite_y_offset = sprite["details"][7]

        max_x_left = max(max_x_left, -sprite_x_offset)
        max_x_right = max(max_x_right, width + sprite_x_offset)

        max_y_top = max(max_y_top, -sprite_y_offset)
        max_y_bottom = max(max_y_bottom, height + sprite_y_offset)

    gif_size_x = max_x_left + max_x_right
    gif_size_y = max_y_top + max_y_bottom

    for sheet_num, sprites_on_this_sheet in required_spritesheets.items():
        print(f"Opening spritesheet: output/sprite_{sheet_num}.png")
        print(f"Need to get {len(sprites_on_this_sheet)} sprites from here.")

        with Image.open(f"{sprite_directory}/sprite_{sheet_num}.png") as im:
            for sprite_index in sprites_on_this_sheet:
                
                sprite = Image.new("RGBA", (gif_size_x, gif_size_y), (255, 0, 0, 0))

                # This gets a box around the image in the spritesheet, it does not do anythin with the image centre.
                width = sprite_details[sprite_index]["details"][4]
                height = sprite_details[sprite_index]["details"][5]
                x_offset_sprite = max_x_left + sprite_details[sprite_index]["details"][6]
                y_offset_sprite = max_y_top + sprite_details[sprite_index]["details"][7]

                x_offset = sprite_details[sprite_index]["details"][9]
                y_offset = sprite_details[sprite_index]["details"][10]

                extracted_sprite = im.crop(box=(x_offset, y_offset,x_offset+width, y_offset+height))
                sprite.paste(extracted_sprite, (x_offset_sprite, y_offset_sprite), mask=extracted_sprite)

                # Now put this sprite in every position required by the original indexes
                for i in sprite_details[sprite_index]["indexes"]:
                    sprites[i] = sprite

    sprites[0].save(output_file, save_all = True, append_images = sprites[1:], optimize = True, duration = 100, disposal=2, loop=True,transparency=0)

#Add the arguments
parser = argparse.ArgumentParser()

parser.add_argument("-d", help="Sets the directory of the generated sprites. Defaults to ./output/",type=int)
parser.add_argument("-o", help="Sets the output gif. Defaults to ./animation.gif",type=str)
parser.add_argument("pattern", help="Sets the sprite pattern", type=str)
args = parser.parse_args()

directory = "./output/"
output = "./animation.gif"


if args.d:
    directory = args.d
if args.o:
    output = args.o

sprite_pattern = parse_sprite_pattern(args.pattern)

generate_sprite(directory, output, sprite_pattern)

# Mechanic, facing SE, answering radio:
# python exportSprites.py -f g1.dat
# python exportSprites.py -s 11441 -e 11879 -a -c2 10 -f g1.dat
# python animate_sprite.py "11442:11464:4, 11442:11464:4, 11514:11594:4, 11594:11513:-4"


# python exportSprites.py -f g1.dat
# python exportSprites.py -s 5000 -e 6000 -a -c2 10 -f g1.dat
# python animate_sprite.py "5298:5313,5313:5298:-1" -o sick_icon.gif
# python animate_sprite.py "5375:5390" -o cash_graph.gif

# This one has some transparency issue
# python animate_sprite.py "5424:5441, 5423" -o marketing_ico.gif


# Guy Walking, Bottom Right
# python exportSprites.py -s 6200 -e 6800 -a -c2 4 -f g1.dat
# python animate_sprite.py "6411:6431:4" -o guy_walking.gif

# Handyman
# python exportSprites.py -s 11300 -e 11400 -a -c2 10 -f g1.dat
# python animate_sprite.py "11303:11323:4,11324,11301:11321:4,11324" -o handyman_mowing.gif