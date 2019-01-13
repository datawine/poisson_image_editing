import cv2
import numpy as np

from poisson import *

if __name__ == '__main__':
#    offset = [-120, 0]
    offset = [140, 150]
    srcimg = cv2.imread("../images/test2_src.png")
    srcmask = cv2.imread("../images/test2_mask.png")
    dstimg = cv2.imread("../images/test2_target.png")
    poissonOperator = Poisson(offset, srcimg, srcmask, dstimg)
    output, naive_output = poissonOperator.process("merge1")
    cv2.imwrite("../res/test2_result.png", output)
    cv2.imwrite("../res/test2_naive_result.png", naive_output)
