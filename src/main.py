import cv2
import numpy as np

from poisson import *

if __name__ == '__main__':
#    offset = [-120, 0]
#    offset = [140, 150]
    offset = [150, 150]
    srcimg = cv2.imread("../images/test5_src.jpg")
    srcmask = cv2.imread("../images/test5_mask.jpg")
#    dstimg = cv2.imread("../images/test3_target.jpg")
    dstimg = None
    poissonOperator = Poisson(offset, srcimg, srcmask, dstimg)
#    output, naive_output = poissonOperator.process("merge3")
    output = poissonOperator.single_pic_process("illu")
    cv2.imwrite("../res/test5_illu_result.jpg", output)
#    cv2.imwrite("../res/test3_naive_result.jpg", naive_output)
