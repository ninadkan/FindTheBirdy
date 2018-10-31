#lets create the basic template
# sources
# https://stackoverflow.com/questions/37624509/whats-the-most-efficient-way-to-select-a-non-rectangular-roi-of-an-image-in-ope 
import numpy as np
import cv2
from matplotlib import pyplot as plt
import os


IMGFOLDER = 'C:\\Users\\ninadk\\Downloads\\GardenPhotos\\backup\\'

def show_image(img, title='Original', subplot=111):
        from matplotlib import pyplot as plt
        plt.subplot(subplot),plt.imshow(img),plt.title(title) 
        plt.show()
        return

def show_image_wait(img, title='Original', subplot=111):
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.imshow(title, img)
        k = cv2.waitKey(0) & 0xff   # 0 means wait indefinitely. 
        if k == 27:
            return
        
EXTENSION = ".jpg"

FILE_LIST = []
for file in os.listdir(IMGFOLDER):
    if os.path.isfile(os.path.join(IMGFOLDER,file)) and '2018-04-16_04' in file:
        if (file.endswith(EXTENSION)):
            FILE_LIST.append(file)

print ("length of FILELIST = {0}".format(str(len(FILE_LIST))))

#select the ROI using the first image
filename= IMGFOLDER+ FILE_LIST[0]
imgFirst = cv2.imread(filename,0) # using gray
assert(imgFirst is not None), "Unable to load " + filename
# height and width is fixed for the image that we are capturing
# height = 1944, width = 2592, size = 5038848
height, width = imgFirst.shape[:2]
# channels = imgFirst.shape[2]
print( "filename = {0}, height = {1}, width = {2}, size = {3}".format(filename, str(height),str(width), imgFirst.size))

mask = imgFirst[0:height, 0:width]
mask[:] = 255 # change everything to white
myROI = [   (0,990), 
            (250, 930),
            (600,950),
            (950,900),
            (1720,850),
            (1780,845),
            (2100,850),
            (width, 1000),
            (width, 0),
            (0, 0)
            ]  # (x, y)
cv2.fillPoly(mask, [np.array(myROI)],0) # now change the relevant things to black
#h,w = mask.shape[:2]
#print("poly shape = height = {0}, width = {1}".format(str(h), str(w)))
#show_image_wait(mask, "1")
# show_image_wait(mask_changed, "2")
# show_image(mask)
# mask_inv = cv2.bitwise_not(mask_changed)
# show_image_wait(mask_inv, "3")
# show_image(mask_inv)

img2 = cv2.bitwise_and(imgFirst, mask_changed)
show_image_wait(img2, "4")
#show_image_wait(imgFirst)

