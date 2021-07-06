import cv2 as cv
import numpy as np

class Image:
    
    def __init__(self,imgpath=None,image=None):
        self.imgpath = imgpath
        if self.imgpath is None and image is not None:
            self.image = image
        elif self.imgpath is not None and image is None:
            self.image = cv.imread(self.imgpath)
        elif self.imgpath is not None and image is not None:
            self.image = image
        else:
            raise('Image Class init error!')
            
    def read(self,imgpath,**kw):
        self.image = cv.imread(imgpath,**kw)
        return self.image
    
    def show(self,winname,image=None):
        if image is not None:
            self.image = image
        cv.imshow(winname,self.image)
        cv.waitKey(0)    
    
    def save(self,filename,**kw):
        cv.imwrite(filename=filename,img=self.image,**kw)

    def binarization(self,thresh=127,maxval=255,type_=cv.THRESH_BINARY):
        g_image=cv.cvtColor(self.image,cv.COLOR_BGR2GRAY)
        ret,binary=cv.threshold(g_image,thresh,maxval,type_)
        return binary
    
    def gaussianBlur(self,ksize=(11,11),sigmaX=0,sigmaY=0):
        blur_image = cv.GaussianBlur(self.image,ksize=ksize,sigmaX=sigmaX,sigmaY=sigmaY)
        return blur_image
    
    def commic(self):
        g_image = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        blur_image = cv.medianBlur(g_image,3)
        edge_image = cv.adaptiveThreshold(blur_image,
                        255,
                        cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv.THRESH_BINARY,
                        blockSize=7,
                        C=3)
        edge_image = cv.cvtColor(edge_image, cv.COLOR_GRAY2BGR)
        return edge_image
    
    def findLargestContour(self,binary_image=None,image=None,color=(0,255,0),tickness=2):
        if binary_image is None and image is not None:
            self.image = image
            gray = cv.cvtColor(self.image,cv.COLOR_BGR2GRAY)
            ret, binary_image = cv.threshold(gray,127,255,cv.THRESH_BINARY)
        if binary_image is None:
            raise('binary_image is None!')
        contours, hierarchy = cv.findContours(binary_image,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
        length = len(contours)
        maxArea = -1
        if length > 0:
            for i in range(length):
                temp = contours[i]
                area = cv.contourArea(temp)
                if area > maxArea:
                    maxArea = area
                    ci = i
            largest_contour = contours[ci]
        return cv.drawContours(image=self.image,contours=largest_contour,contourIdx=-1,color=color,thickness=tickness)
    
    def detectHands(self,image=None,lower=None,upper=None,color=(0,255,0),tickness=2):
        if image is not None:
            self.image = image
        img = self.image.copy()
        if lower is None:
            lower = np.array([0,139,60],np.uint8)
        if upper is None:
            upper = np.array([255,180,127],np.uint8)
        ycrcb = cv.cvtColor(img, cv.COLOR_BGR2YCR_CB)
        mask = cv.inRange(ycrcb,lower,upper)
        #skin = cv.bitwise_and(ycrcb, ycrcb, mask=mask)
        _,binary = cv.threshold(mask,127,255,0)
        return self.findLargestContour(binary_image=binary,color=color,tickness=tickness)

class Video:
    def __init__(self,camera_index=0):
        self.camera = cv.VideoCapture(camera_index)
    
    def captureCamera(self):
        ret, frame =  self.camera.read()
        self.camera.release()
        return frame
    
class Audio:
    def __init__(self):
        pass