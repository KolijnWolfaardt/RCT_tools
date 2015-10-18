import struct
import math
import os.path
import argparse

from PIL import Image
import numpy as np

verbose = False

"""
	Basic Reading functions. Auto converts to the correct file type
"""
def readBytes(number):
	dataArray = []

	pos = filepointer.tell()
	dataToCopy = filepointer.read(number)

	#globalRead = globalRead+number

	for a in dataToCopy:
		dataArray.append(struct.unpack("b",a)[0])

	return dataArray

#A small int is a 2 byte signed integer
def readSmallint():
	data1 = readBytes(2)
	return data1[1]<<8 | data1[0]%256

#A word is probably a 2 byte unsigned number
def readWord():
	return readSmallint()% 2**16

# int is a 4 byte signed integer
def readInt():
	data1 = readBytes(4)
	return data1[3]%256<<24 | data1[2]%256<<16 | data1[1]%256<<8 | data1[0]%256

#A long word is probably a 2 byte unsigned number
def readLongword():
	return readInt() % 2**32

def log(message):
	if verbose==True:
		print message

"""
Write a number above a sprite
"""
def writenum(arr,xOffset,yOffset,num):
	#First convert to a decimal representation
	a = "{}".format(num)

	#For each of the digits
	for i in range(len(a)):
		singleCharacter = numberData[int(a[i])]
		for y in range(5):
			for x in range(3):
				if singleCharacter[y][x] == 1:
					arr[yOffset+y,xOffset+x+i*4,:] = np.array([0,0,0])


"""
The numberData is used to display numbers next to the sprites
"""
numberData=[[[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
	[[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
	[[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
	[[1,1,1],[0,0,1],[0,1,1],[0,0,1],[1,1,1]],
	[[1,0,0],[1,0,0],[1,0,1],[1,1,1],[0,0,1]],
	[[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
	[[1,0,0],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
	[[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
	[[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
	[[1,1,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]]]

# 'Global' variables
filepoint 		= None
spriteStart 	= 0
spriteEnd		= 1000
maxImageWidth	= 1000
maxImageHeight  = 1000
filename 		= 'g1.dat'
verbose			= False
customColor1 	= 3
customColor2 	= 4
paletteFile		= "./palettes/Palette_0cb27f"
onlyDoPalette	= False
palette			= "default"

#Add the arguments
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", help="Increase the program verbosity",action="store_true")
parser.add_argument("-f", "--file", help="Set the location of the g1.dat file",action="store")
parser.add_argument("-s", "--sprite-start", help="Set the sprite number at which to start.",type=int)
parser.add_argument("-e", "--sprite-end", help="Set the sprite number at which to end. Outputs everything per default",type=int)
parser.add_argument("--out-width", help="Set the output file width. Defaults to 1000",type=int)
parser.add_argument("--out-height", help="Set the output file height. Defaults to 1000",type=int)
parser.add_argument("-c1", help="Sets colour 1 to replace.",type=int)
parser.add_argument("-c2", help="Sets colour 2 to replace.",type=int)
parser.add_argument("-p", help="Sets the palette to the specified file")
args = parser.parse_args()

if args.verbose:
	verbose = True

if args.file:
	filename = args.file

if not args.sprite_start == None:
	spriteStart = args.sprite_start
	print "Set start to {}".format(spriteStart)

if not args.sprite_end == None:
	spriteEnd = args.sprite_end
	print "Set end to {}".format(spriteEnd)

if args.out_width:
	maxImageWidth = args.out_width

if args.out_height:
	maxImageHeight = args.out_width

if args.c1:
	customColor1 = args.c1

if args.c2:
	customColor1 = args.c2

if args.p:
	paletteFile = args.p
	palette = "custom"

#Check that the file exists
if os.path.isfile(filename):
	filepointer = open(filename,'rb')
	log ("File opened")
else:
	print "Could not find g1.data file. Make sure it is in the current directory, or specify a file with -f"
	quit()

#Read the number of images in the file
nrImages = readInt()
sizeOfImages = readInt()

log("Number of images {}".format(nrImages))
log("Size of images {}".format(sizeOfImages))

#The spriteLookupArray will store details about each sprite, until we read the image detail
spriteLookupArr = []

for n in range(0,nrImages):

	startAddr 	= readLongword()
	width 		= readWord()
	height 		= readWord()
	xOffset		= readSmallint()
	yOffset		= readSmallint()
	flags		= readWord()
	padding		= readWord()

	spriteLookupArr.append([startAddr,width,height,xOffset,yOffset,flags,padding])

#imageDataStartsAt stores the location in the file where the image data starts
imageDataStartsAt = filepointer.tell()

paletteColors = []
#Check if the palettes are there.
if palette=="default":
	if (os.path.isfile("./palettes/Palette_0cb27f")):

		#Palette found, load it
		paletteFile = open("./palettes/Palette_0cb27f")
		lines = paletteFile.readlines()
		for l in lines:
			colors = l.split(',')
			paletteColors.append([int(colors[0]),int(colors[1]),int(colors[2])])
		paletteFile.close()

	else:
		#Force a run with only the palettes
		print "No palette found. Doing a run with only palettes"
		onlyDoPalette = True
		spriteEnd = 29294
else:
	#Load the palette that the user specified
	paletteFile = open("./palettes/Palette_0cb27f")
	lines = paletteFile.readlines()
	for l in lines:
		colors = l.split(',')
		paletteColors.append([int(colors[0]),int(colors[1]),int(colors[2])])
	paletteFile.close()

if not os.path.exists("./output"):
	os.makedirs("./output")

if not os.path.exists("./palettes"):
	os.makedirs("./palettes")

nfoFile = open("output/sprites.nfo","w")

numSprites = spriteEnd-spriteStart


# listOfPages contains a bunch of arrays. Each array represents a new page.
# inside each page array is a list containing the positions for each sprite
#The positions are for the border or number.
listOfPages = []

# First determine the positions that sprites will be placed on the sprite sheet.
# Position sprites on a horizontal grid of 'spriteWidth' width. If the sprite is larger, use
# multiple positions in the grid.
# When the end of the line is reached, see if the line can be added to the current page without exceeding the image size.
# If it cant, go to the next page.
# The positions have an additional small offset to display the sprite numbers.

lineHeight     = 0	#lineheight holds the maximum sprite height of the current line
spriteWidth    = 32	#The grid spacing.

linePosition   = 0 
currentHeight  = 0

currentPagePositions = []
positionsToAddToThePage = []

#Loop through all the sprites, to determine their positions
for i in range(spriteStart,spriteStart+numSprites):

	#Get the sprite details
	spriteData = spriteLookupArr[i]
	startAddr 	= spriteData[0]
	width 		= spriteData[1]
	height 		= spriteData[2]
	xOffset		= spriteData[3]
	yOffset		= spriteData[4]
	flags		= spriteData[5]


	#If the sprite will fit on this line, add it
	if max(linePosition*spriteWidth+width+2,(linePosition+1)*spriteWidth-1) < maxImageWidth:
		#The sprite will fit!
		#Append its position to the currentPagePositions Array
		positionsToAddToThePage.append([linePosition*spriteWidth+2,currentHeight])
		lineHeight = max(lineHeight,height+8)
		linePosition = linePosition + int(math.floor((width+2)/spriteWidth))+1

	else:
		#The sprite does not fit! move it to the next line!
		#First check if we have to move to the next image as well?
		if (currentHeight+lineHeight > maxImageHeight):
			#Add currentPagePositions to the big array, and clear it
			listOfPages.append(currentPagePositions)
			currentPagePositions = []
			currentHeight = 0

			#All the sprites that are yet to be added have wrong heights. change it
			for j in range(0,len(positionsToAddToThePage)):
				positionsToAddToThePage[j][1] = 0

			
		#Add the previous array to i, since it hasn't been added yet
		currentPagePositions = currentPagePositions + positionsToAddToThePage
		currentHeight = currentHeight+lineHeight
		linePosition = 0

		#These positions have just been added. Clear the array
		positionsToAddToThePage = []

		positionsToAddToThePage.append([linePosition*spriteWidth+2,currentHeight])
		lineHeight = height+8
		linePosition = linePosition + int(math.floor((width+2)/spriteWidth))+1



#It is possible that the final array hasn't been appended yet.
currentPagePositions = currentPagePositions + positionsToAddToThePage
listOfPages.append(currentPagePositions)

log("Sprites divided into {} sheets".format(len(listOfPages)))


spriteNumber = 0
totalSprites = 0

for pageNumber in range(0,len(listOfPages)):

	#Get a list of all the positions for sprites
	currentPagePositions = listOfPages[pageNumber]

	#Create a new image to work on
	emptyImage = np.ones((maxImageHeight,maxImageWidth,3),'uint8')*255

	log("Processing page {}, containing {} sprites".format(pageNumber,len(currentPagePositions)))

	for n in range(0,len(currentPagePositions)):

		blockY = (currentPagePositions[n])[1]
		blockX = (currentPagePositions[n])[0]
		imagePosX = blockX+1
		imagePosY = blockY+7
		#print "\timages {} at {} {}".format(n,imagePosX,imagePosY)

		spriteData = spriteLookupArr[n+spriteStart+totalSprites]

		startAddr 	= spriteData[0]
		width 		= spriteData[1]
		height 		= spriteData[2]
		xOffset		= spriteData[3]
		yOffset		= spriteData[4]
		flags		= spriteData[5]
		
		if width== 0 and height==0:
			log("Waring: found empty image at {}".format(n+spriteStart+totalSprites))

		offsetAddress = startAddr+imageDataStartsAt

		#Write pageNumber, sprite number, total sprite number, width, height, xOffset, yOffset, flags
		nfoFile.write("{}, {:4}, {:6}, {:6x}, {}, {}, {}, {}, {}, {}, {}\n".format(pageNumber,n,n+spriteStart+totalSprites,offsetAddress,width,height,xOffset,yOffset,flags,imagePosX,imagePosY))

		writenum(emptyImage,blockX+1,blockY+1,n+spriteStart+totalSprites)
		
		#This is a compressed image
		if (flags == 5 or flags==21) and onlyDoPalette == False: 
			#Go to the address			
			filepointer.seek(offsetAddress)
			firstHeader = readWord()

			#Read the offsets to the individual scan lines
			bogusBytes = readBytes(firstHeader-2)

			#Fill the background with black, so we can see it
			try:
				for x in range(0,width):
					for y in range(0,height):
						emptyImage[imagePosY+y,imagePosX+x,:] = np.array([112,146,190])	
			except  IndexError:
				log("Waring:Oversized sprite detected. Sprite {} is {} {}".format(n+spriteStart+totalSprites,width,height))

			#Loop through height
			y = 0
			#for counter1 in range(0,len(bogusBytes)/2):
			while (y<height):
				firstHeader = readBytes(1)[0]%256
				dataLength = firstHeader%128

				x = readBytes(1)[0]

				imagesData = readBytes(dataLength%256)

				for i in range(0,len(imagesData)):
					position = (imagesData[i])%256

					#Replace customColor1
					if position>= 243 and position<256:
						position = position-243 + customColor1*12+10

					posOffset = position-10

					if posOffset>= 16*12 and posOffset<17*12:
						position = posOffset-16*12+10+customColor2*12

					#print ("Looking up position {}".format(position))
					color = paletteColors[position]
					try:
						emptyImage[imagePosY+y,imagePosX+x+i,:] = np.array([color[2],color[1],color[0]])
					except  IndexError:
						log("Waring:Oversized sprite detected. Sprite {} is {} {}".format(n+spriteStart+totalSprites,width,height))
			

				#If this is false, there will be another scanline for THE SAME LINE
				if (firstHeader>127):
					y = y+1

		#Plain BMP image
		if (flags == 1 or flags==17) and onlyDoPalette == False: 
			filepointer.seek(offsetAddress)

			imagesData = readBytes(height*width)
			for x in range(0,height):
				for y in range(0,width):
					position = (imagesData[x*width+y])%256
					color = paletteColors[position]
					try:
						emptyImage[imagePosY+x,imagePosX+y,:] = np.array([color[2],color[1],color[0]])	
					except  IndexError:
						log("Waring:Oversized sprite detected. Sprite {} is {} {}".format(n+spriteStart+totalSprites,width,height))
						continue
		

		if (flags == 8):
			log("Palette found at {}".format(n+spriteStart+totalSprites))

			#Go to the addres
			filepointer.seek(offsetAddress)

			#Read the data
			paletteArr = np.array(readBytes(width*3),'uint8')

			colorArr = np.zeros((252,1,3),'uint8')
			colorArr[0:width,0,0] = paletteArr[2::3]	#Red
			colorArr[0:width,0,1] = paletteArr[1::3]	#Green
			colorArr[0:width,0,2] = paletteArr[0::3]	#Blue

			#Write it to the file
			g = open("palettes/Palette_{:06x}".format(offsetAddress),'w')

			#Write the required padding
			g.write("0,0,0\n"*10)

			for a in range(width):
				g.write("{},{},{}\n".format(colorArr[a,0,2],colorArr[a,0,1],colorArr[a,0,0])),

			#Write the required padding
			g.write("0,0,0\n"*10)

			g.close()

			colorArr = np.resize(colorArr,(21,12,3))
			img = Image.fromarray(colorArr)
			img.save('palettes/palette_{:06x}.png'.format(offsetAddress))

	#After the for loop
	#Increment the total number ofsprites sofar
	totalSprites = totalSprites + len(currentPagePositions)
		
	# plt.imshow(emptyImage,interpolation="nearest")
	
	#And save the image
	if onlyDoPalette == False:
		img = Image.fromarray(emptyImage)
		img.save('output/sprite_{}.png'.format(pageNumber))

filepointer.close()
nfoFile.close()

if (onlyDoPalette ==True):
	print "Done saving palettes. Run again with the same arguments"