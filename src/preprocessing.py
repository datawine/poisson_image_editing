import cv2
import numpy as np

# get the rectangle that contains the mask aera
# of the top image
# tl means top left
# br means bottom right
def getRect(img):
    tl = [1000000, 1000000]
    br = [-1, -1]
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 0] != 0:
                if tl[0] > i - 2:
                    tl[0] = max(0, i - 2)
                if tl[1] > j - 2:
                    tl[1] = max(0, j - 2)
                if br[0] < i + 2:
                    br[0] = min(img.shape[0], i + 2)
                if br[1] < j + 2:
                    br[1] = min(img.shape[1], j + 2)
    return tl, br

# add the offset to the top left and bottom right
# to get the tl and br of the ground image
def genDstRect(tl, br, offset):
    _tl = [0, 0]
    _br = [0, 0]
    _tl[0] = tl[0] + offset[0]
    _tl[1] = tl[1] + offset[1]
    _br[0] = br[0] + offset[0]
    _br[1] = br[1] + offset[1]
    return _tl, _br

def genEdgeMap(img):
    raw_edge = cv2.Canny(img, 100, 200)
    edge_map = np.zeros(raw_edge.shape)
    for i in range(edge_map.shape[0]):
        for j in range(edge_map.shape[1]):
            if raw_edge[i][j] != 0:
                for delta_i in range(-2, 2):
                    for delta_j in range(-2, 2):
                        new_i = min(max(0, i + delta_i), edge_map.shape[0] - 1)
                        new_j = min(max(0, j + delta_j), edge_map.shape[1] - 1)
                        edge_map[new_i][new_j] = 1
    return edge_map