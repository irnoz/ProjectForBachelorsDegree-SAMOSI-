import numpy as np
import cv2 as cv
import math
import keras
import keras.models


class Imgproc:
    def __init__(self, img):
        self.img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)[:img.shape[0] - 3]
        self.procimg = None

    def getimg(self):
        return self.img.copy()

    def __readyforstraighten(self):
        self.procimg = self.img[self.img.shape[0] // 15 * 14:].copy()
        imgh, imgw = self.procimg.shape
        self.procimg = cv.Sobel(src=self.procimg, ddepth=cv.CV_64F, dx=0, dy=1, ksize=1)
        for i in range(imgh):
            for j in range(imgw):
                if (self.procimg[i][j] >= 20):
                    self.procimg[i][j] = 250
                else:
                    self.procimg[i][j] = 0
        self.procimg = cv.dilate(self.procimg, (5, 5), iterations=5)

    def straightenimg(self):
        self.__readyforstraighten()
        h, w = self.procimg.shape
        w = w // 2
        h = h - 1
        while (self.procimg[h][w] < 250):
            h -= 1

        lh = rh = h
        lw = rw = w
        while (True):
            if (self.procimg[lh][lw - 1] == 250):
                lw -= 1
                continue
            if (self.procimg[lh - 1][lw - 1] == 250):
                lw -= 1
                lh -= 1
                continue
            if (self.procimg[lh + 1][lw - 1] == 250):
                lw -= 1
                lh += 1
                continue
            break
        while (True):
            if (self.procimg[rh][rw + 1] == 250):
                rw += 1
                continue
            if (self.procimg[rh - 1][rw + 1] == 250):
                rw += 1
                rh -= 1
                continue
            if (self.procimg[rh + 1][rw + 1] == 250):
                rw += 1
                rh += 1
                continue
            break
        centerh, centerw = self.img.shape[0] / 2, self.img.shape[1] / 2
        sigma = math.atan((lh - rh) / (lw - rw)) * 180 / math.pi
        self.img = cv.warpAffine(self.img,
                                 cv.getRotationMatrix2D((centerh, centerw),
                                                        sigma,
                                                        1),
                                 (1250, 1750), borderMode=cv.BORDER_CONSTANT, borderValue=255)

    def procimgforcords(self):
        self.__readyforstraighten()
        imgh, imgw = self.img.shape
        self.straightenimg()
        self.procimg = cv.resize(self.img[imgh // 6:imgh // 18 * 11, imgw - 305:imgw - 5],
                                 (0, 0), fx=2 / 3, fy=2 / 3, interpolation=cv.INTER_AREA)

    def horizontify(self, img):
        # horizontifys img itself
        h, w = img.shape

        for i in range(h):
            sum = 0
            for j in range(w):
                sum += img[i][j]
            for j in range(w):
                img[i][j] = sum / w

    def blacken(self, img, threshold=100):
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if (img[i][j] < threshold):
                    img[i][j] = 0
                else:
                    img[i][j] = 255

    def gethbounds(self):
        nimg = self.procimg[:, :50].copy()
        self.horizontify(nimg)
        self.blacken(nimg, 140)
        hnimg = nimg.copy()
        nimg = cv.blur(nimg, (5, 5))
        self.blacken(nimg, 105)
        nimg = cv.blur(nimg, (5, 5))
        self.blacken(nimg, 52)
        x, y = nimg.shape

        starth = 0
        endh = nimg.shape[0] - 1
        # 28 can be changed for anything else, while its <50
        while (nimg[starth][28] == 255):
            starth += 1
        h1 = starth - 10
        while (hnimg[h1][28] == 255):
            h1 -= 1

        while (nimg[endh][28] == 255):
            endh -= 1
        h2 = endh + 10
        while (hnimg[h2][28] == 255):
            h2 += 1

        return h1, h2

    def vertify(self, img):
        # img itself is changed
        h, w = img.shape

        for i in range(w):
            sum = 0
            for j in range(h):
                sum += img[j][i]
            for j in range(h):
                img[j][i] = sum // h

    def horizontify(self, img):
        h, w = img.shape
        for i in range(h):
            sum = 0
            for j in range(w):
                sum += img[i][j]
            for j in range(w):
                img[i][j] = sum / w

    def whitenimg(self, img, bckground=0, threshold=100):
        # img itself is changed
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if (img[i][j] > threshold):
                    img[i][j] = 255
                else:
                    img[i][j] = bckground

    def getwbounds(self, hstart):
        nimg = self.procimg[hstart:100]
        nimg = cv.Sobel(src=nimg, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
        self.whitenimg(nimg, 0, 80)
        self.vertify(nimg)
        self.whitenimg(nimg, 0, 80)

        wstart = 0
        while (nimg[11][wstart] != 255):
            wstart += 1
        wend = nimg.shape[1] - 1
        while (nimg[11][wend] != 255):
            wend -= 1

        if (wstart < 2):
            wstart = 0
        else:
            wstart -= 2
        return wstart, wend

    def procfornumbers(self):
        self.procimgforcords()
        hstart, hend = self.gethbounds()
        wstart, wend = self.getwbounds(hstart)

        himg = self.procimg[hstart:hend, :10].copy()
        self.horizontify(himg)
        self.blacken(himg, 200)

        h = 0
        he = 0
        hlist = []
        hend -= hstart
        i = 0
        while (h != hend):
            while (himg[h][0] == 0 and h < hend - 1):
                h += 1
            if (h == hend - 1):
                break
            hs = h
            while (himg[h][0] == 255 and h < hend - 1):
                h += 1
            he = h
            if (he - hs >= 40):
                continue
            i += 1
            hlist.append(self.procimg[hstart + hs:hstart + he, wstart:wend].copy())

        return hlist, i

    def tomnist(self, img):
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if (img[i][j] <= 200):
                    img[i][j] = 0
                else:
                    img[i][j] = 255
        return img

    def modelinputs(self):
        imglist, num = self.procfornumbers()
        formodel = []
        for img in imglist:
            w = img.shape[1] // 4
            img1 = np.resize(self.tomnist(cv.resize(img[:, :w].copy(), (28, 28))), (28, 28, 1)).astype('float32') / 255
            img2 = np.resize(self.tomnist(cv.resize(img[:, w:2 * w].copy(), (28, 28))), (28, 28, 1)).astype('float32') / 255
            img3 = np.resize(self.tomnist(cv.resize(img[:, 2 * w:3 * w].copy(), (28, 28))), (28, 28, 1)).astype(
                'float32') / 255
            img4 = np.resize(self.tomnist(cv.resize(img[:, 3 * w:].copy(), (28, 28))), (28, 28, 1)).astype('float32') / 255
            formodel.append([img1, img2, img3, img4])
        formodel = np.array(formodel)
        return formodel, num


def predict(img, modelfile):
    model = keras.models.load_model(modelfile)
    imgprocobj = Imgproc(img)
    # cv.imshow("",imgprocobj.getimg())
    # cv.waitKey(0)
    fm, k = imgprocobj.modelinputs()
    returnlist = []
    for t in range(k):
        predictions = model.predict(fm[t])
        xs = ""
        for pred in predictions:
            cnt = 0
            for i in range(10):
                if pred[i] < 0.9:
                    cnt += 1
            if cnt == 10:
                x = 0
            else:
                x = np.argmax(pred)
            xs = xs + str(x)
        returnlist.append((xs, t))

    return returnlist

# image = cv.imread("/Users/noza/PycharmProjects/pythonProjectForBach/res/290978592_410423371050212_1989803757001338259_n.jpg")
# print(type(image))
# obj = Imgproc(image)
# list = predict(image, "/Users/noza/PycharmProjects/pythonProjectForBach/model")
# print(list)