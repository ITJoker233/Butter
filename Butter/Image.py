import cv2 as cv

class Image:
    
    def __init__(self,imgpath):
        self.imgpath = imgpath
        self.image = cv.imread(self.imgpath)
        
    def read(self,imgpath,**kw):
        self.image = cv.imread(imgpath,**kw)
        return self.image
    
    def show(self,**kw):
        cv.imshow(self.image,**kw)    
    
    def save(self,filename,**kw):
        cv.imwrite(filename=filename,img=self.image,**kw)

    def binarization(self):
        pass

    def gaussianBlur(self):
        pass

    def commic(self):
        pass