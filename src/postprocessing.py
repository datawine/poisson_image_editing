def genRes(img, patch, tl):
    _img = img.copy()
    for i in range(patch.shape[0]):
        for j in range(patch.shape[1]):
            for k in range(patch.shape[2]):
                _img[i + tl[0], j + tl[1], k] = patch[i, j, k]
    return _img

def genNaiveRes(img, patch, mask, tl):
    _img = img.copy()
    for i in range(patch.shape[0]):
        for j in range(patch.shape[1]):
            for k in range(patch.shape[2]):
                if mask[i, j, k] != 0:
                    _img[i + tl[0], j + tl[1], k] = patch[i, j, k]
    return _img