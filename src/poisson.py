import cv2
import numpy as np
import scipy.fftpack
import scipy.ndimage
from scipy.sparse.linalg import spsolve
from scipy.sparse import csc_matrix
import time

from myMathFunc import *
from preprocessing import *
from postprocessing import *

class Poisson():
    def __init__(self, offset, srcimg, srcmask, dstimg):
        self.offset = offset
        self.srcimg = srcimg
        self.srcmask = srcmask
        self.dstimg = dstimg
        self.tl, self.br = getRect(self.srcmask)
        self.topimg = self.srcimg[self.tl[0]:self.br[0], self.tl[1]:self.br[1], :]
        self.msk = self.srcmask[self.tl[0]:self.br[0], self.tl[1]:self.br[1], :]

        if self.dstimg:
            self._tl, self._br = genDstRect(self.tl, self.br, self.offset)
            self.groundimg = self.dstimg[self._tl[0]:self._br[0], self._tl[1]:self._br[1], :]

    def process(self, proc_type):
        if proc_type == "merge1":
            self.patch = self.imageFusion()
        elif proc_type == "merge2":
            self.patch = self.imageFusion2()
        elif proc_type == "merge3":
            self.patch = self.imageFusion3()

        res = genRes(self.dstimg, self.patch, self._tl)
        naiveres = genNaiveRes(self.dstimg, self.topimg, self.msk, self._tl)
        return res, naiveres

    def single_pic_process(self, proc_type):
        if proc_type == "flatten":
            self.patch = self.imageFusion4()
        elif proc_type == "illu":
            self.patch = self.imageFusion5()
        res = genRes(self.srcimg, self.patch, self.tl)
        return res

    def imageFusion(self):
        rows, cols, dims = self.topimg.shape

        im1 = self.topimg.copy().astype('float32')
        im2 = self.groundimg.copy().astype('float32')
        im_res = np.zeros((rows, cols, dims), dtype=np.float32)

        for dim in range(dims):
            [dx1, dy1] = genGradient(im1[:, :, dim])
            [dx2, dy2] = genGradient(im2[:, :, dim])

            dx, dy = dx2.copy(), dy2.copy()
            for i in range(rows):
                for j in range(cols):
                    if self.msk[i, j, dim] != 0:
                        dx[i, j], dy[i, j] = dx1[i, j], dy1[i, j]

            lap = genLaplacian(dx, dy)
            im_res[:, :, dim] = np.clip(solvePoisson(lap, im2[:, :, dim]), 0, 255)
        return im_res.astype('uint8')

    def imageFusion2(self):
        rows, cols, dims = self.topimg.shape

        im1 = self.topimg.copy().astype('float32')
        im2 = self.groundimg.copy().astype('float32')
        im_res = np.zeros((rows, cols, dims), dtype=np.float32)

        for dim in range(dims):
            [dx1, dy1] = genGradient(im1[:, :, dim])
            [dx2, dy2] = genGradient(im2[:, :, dim])
            dx, dy = dx2.copy(), dy2.copy()

            A = np.zeros((rows * cols, rows * cols), dtype=np.float32)
            b = np.zeros((rows * cols, ), dtype=np.float32)
            r = 0
            for i in range(rows):
                for j in range(cols):
                    if self.msk[i, j, dim] != 0:
                        dx[i, j], dy[i, j] = dx1[i, j], dy1[i, j]
                        A[r, i * cols + j] = -4
                        if i > 0:
                            A[r, (i - 1) * cols + j] = 1
                        if i < rows - 1:
                            A[r, (i + 1) * cols + j] = 1
                        if j > 0:
                            A[r, i * cols + j - 1] = 1
                        if j < cols - 1:
                            A[r, i * cols + j + 1] = 1
                        b[r] = dx[i, j] - dx[i, j - 1] + dy[i, j] - dy[i - 1, j]
                    else:
                        A[r, i * cols + j] = 1
                        b[r] = self.groundimg[i, j, dim]
                    r = r + 1
            x = spsolve(A, b)
            im_res[:, :, dim] = np.clip(x.reshape(rows, cols), 0, 255)

        return im_res.astype('uint8')

    def imageFusion3(self):
        rows, cols, dims = self.topimg.shape

        im1 = self.topimg.copy().astype('float32')
        im2 = self.groundimg.copy().astype('float32')
        im_res = np.zeros((rows, cols, dims), dtype=np.float32)

        for dim in range(dims):
            [dx1, dy1] = genGradient(im1[:, :, dim])
            [dx2, dy2] = genGradient(im2[:, :, dim])

            dx, dy = dx2.copy(), dy2.copy()
            for i in range(rows):
                for j in range(cols):
                    if self.msk[i, j, dim] != 0:
                        if abs(dx[i, j]) + abs(dy[i, j]) < abs(dx1[i, j]) + abs(dy1[i, j]):
                            dx[i, j], dy[i, j] = dx1[i, j], dy1[i, j]

            lap = genLaplacian(dx, dy)
            im_res[:, :, dim] = np.clip(solvePoisson(lap, im2[:, :, dim]), 0, 255)
        return im_res.astype('uint8')
    
    def imageFusion4(self):
        rows, cols, dims = self.topimg.shape

        im1 = self.topimg.copy().astype('float32')
        im_res = np.zeros((rows, cols, dims), dtype=np.float32)
        edge_map = genEdgeMap(self.topimg)

        for dim in range(dims):
            [dx, dy] = genGradient(im1[:, :, dim])

            for i in range(rows):
                for j in range(cols):
                    if self.msk[i, j, dim] != 0:
                        dx[i, j] = dx[i, j] * edge_map[i, j]
                        dy[i, j] = dy[i, j] * edge_map[i, j]

            lap = genLaplacian(dx, dy)
            im_res[:, :, dim] = np.clip(solvePoisson(lap, im1[:, :, dim]), 0, 255)
        return im_res.astype('uint8')

    def imageFusion5(self):
        rows, cols, dims = self.topimg.shape

        im1 = self.topimg.copy().astype('float32')
        im_res = np.zeros((rows, cols, dims), dtype=np.float32)
        edge_map = genEdgeMap(self.topimg)

        for dim in range(dims):
            [dx, dy] = genGradient(im1[:, :, dim])
            d_sum, d_avg = 0, 0
            for i in range(rows):
                for j in range(cols):
                    d_sum = d_sum + dx[i, j] + dy[i, j]
            d_avg = abs(d_sum * 0.2 / rows / cols)

            for i in range(rows):
                for j in range(cols):
                    if self.msk[i, j, dim] != 0:
                        if dx[i, j] != 0:
                            dx[i, j] = dx[i, j] * (abs(dx[i, j]) ** -0.2) * (d_avg ** 0.2)
                        if dy[i, j] != 0:
                            dy[i, j] = dy[i, j] * (abs(dy[i, j]) ** -0.2) * (d_avg ** 0.2)

            lap = genLaplacian(dx, dy)
            im_res[:, :, dim] = np.clip(solvePoisson(lap, im1[:, :, dim]), 0, 255)
        return im_res.astype('uint8')