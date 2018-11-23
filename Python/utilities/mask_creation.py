#lets create the basic template
# sources
# https://stackoverflow.com/questions/37624509/whats-the-most-efficient-way-to-select-a-non-rectangular-roi-of-an-image-in-ope 
import numpy as np
import cv2
from matplotlib import pyplot as plt
import os
import json


def show_image_wait(img, title='Original', subplot=111):
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.imshow(title, img)
        return

        
grayMask = colourMask = None

filename= 'C:\\Users\\ninadk\\Downloads\\GardenPhotos\\backup\\Birds\\2018-11-12_0400.jpg'

colorImage = cv2.imread(filename)
assert(colorImage is not None), "Unable to load " + filename
show_image_wait(colorImage, "colorImage")
gray_image = cv2.cvtColor(colorImage, cv2.COLOR_BGR2GRAY)
show_image_wait(gray_image, "gray_image")

# height and width is fixed for the image that we are capturing. 
# It is same for all the images
height, width = colorImage.shape[:2]
print("height = {0}, width = {1}".format(str(height), str(width)))

#create mask to stub out areas that we don't want to include. 
myROI = [[0, 1000], [1750, 1000], [2592, 1350], [2592, 0], [0, 0]] 

#colour mask
colourMask = colorImage[0:height, 0:width]
#colourMask[:] = (255, 255,255) # change everything to white


# Gray mask
grayMask = gray_image[0:height, 0:width]
#grayMask[:] = 255 # change everything to white

#create the masks
cv2.fillPoly(grayMask, [np.array(myROI)],0)
show_image_wait(grayMask, "grayMask")
cv2.fillPoly(colourMask, [np.array(myROI)],(0,0,0))
show_image_wait(colourMask, "colourMask")


k = cv2.waitKey(0) & 0xff   # 0 means wait indefinitely. 
if k == 27:
        print("Exit")
cv2.destroyAllWindows()

outFileName= filename + 'mask_file.txt'

with open(outFileName, 'w') as filehandle:  
        #filehandle.writelines("%s\n" % itemRI for itemRI in myROI)
        json.dump(myROI, filehandle)

places = []

# open file and read the content in a list
with open(outFileName, 'r') as filehandle:  
        #places = [current_place.rstrip() for current_place in filehandle.readlines()]
        places = json.load(filehandle)

for pl in places:
        print(pl)

