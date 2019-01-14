import cv2
from preprocessing import *

img = cv2.imread("../images/test5_src.jpg")

'''
print img.shape
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if 20 < i and i < 160 and 20 < j and j < 180:
            img[i, j] = [255, 255, 255]
cv2.imwrite("../images/test3_mask2.jpg", img)
'''
'''
print img.shape
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if 58 < j and j < 111 and 81 < i and i < 136:
            img[i, j] = [255, 255, 255]
        else:
            img[i, j] = [0, 0, 0]
cv2.imwrite("../images/test5_mask.jpg", img)
'''
print 4 ** 0.5
#cv2.imshow("image", img)
#cv2.waitKey(0)