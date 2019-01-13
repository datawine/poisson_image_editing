import cv2
import numpy as np
import scipy.fftpack
import scipy.ndimage
from scipy.sparse.linalg import spsolve
from scipy.sparse import csc_matrix

def DST(x):
    return scipy.fftpack.dst(x, type=1, axis=0) / 2.0

def IDST(X):
    x = np.real(scipy.fftpack.idst(X, type=1, axis=0))
    return x / (X.shape[0] + 1.0)

def genGradient(im):
    rows, cols = im.shape
    dx = np.zeros((rows, cols), dtype=np.float32)
    dy = np.zeros((rows, cols), dtype=np.float32)
    for i in range(rows - 1):
        for j in range(cols - 1):
            dx[i, j] = im[i, j + 1] - im[i, j]
            dy[i, j] = im[i + 1, j] - im[i, j]
    return dx, dy

def genLaplacian(dx, dy):
    rows, cols = dx.shape
    lapx = np.zeros((rows, cols), dtype=np.float32)
    lapy = np.zeros((rows, cols), dtype=np.float32)
    for i in range(1, rows):
        for j in range(1, cols):
            lapx[i, j] = dx[i, j] - dx[i, j - 1]
            lapy[i, j] = dy[i, j] - dy[i - 1, j]
    return lapx + lapy

def solvePoisson(lap, img):
    img = img.astype('float32')
    rows, cols = img.shape
    img[1:-1, 1:-1] = 0

    L_bp = np.zeros_like(lap)
    L_bp[1:-1, 1:-1] = -4 * img[1:-1, 1:-1] \
                      + img[1:-1, 2:] + img[1:-1, 0:-2] \
                      + img[2:, 1:-1] + img[0:-2, 1:-1]
    L = (lap - L_bp)[1:-1, 1:-1]
    L_dst = DST(DST(L).T).T

    [xx, yy] = np.meshgrid(np.arange(1,cols-1), np.arange(1,rows-1))
    D = (2 * np.cos(np.pi * xx/(cols - 1)) - 2) + (2 * np.cos(np.pi * yy/(rows - 1)) - 2)
    L_dst = L_dst / D

    img_interior = IDST(IDST(L_dst).T).T 
    img = img.copy()
    img[1:-1, 1:-1] = img_interior

    return img    
