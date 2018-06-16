import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys

from django.conf import settings
sys.path.append(settings.DARKNET_DIR)
import darknet as dn

def maskPerson(img, rects):
    img2 = img.copy()        
    mask = np.zeros((len(rects), img.shape[0], img.shape[1]), dtype = np.uint8)

    bgdmodel = np.zeros((1,65),np.float64)
    fgdmodel = np.zeros((1,65),np.float64)

    mask3 = np.zeros(img.shape[:2], dtype = np.uint8)
    for i in range(len(rects)):
        cv2.grabCut(img2,mask[i],rects[i],bgdmodel,fgdmodel,1,cv2.GC_INIT_WITH_RECT)
        mask3 = np.add(mask3,mask[i])
    mask2 = np.where((mask3==1) + (mask3==3))
    return mask2

def pastePerson(src, mask, background):
    newImg = background.copy()        
    m = np.zeros((src.shape), dtype=np.uint8)
    transform = int(src.shape[1]/2) if src.shape[1]*2 == background.shape[1] else 0
    for pos in zip(mask[0], mask[1]):
        newImg[pos[0],pos[1] + transform] = src[pos]
    return newImg

def detectPerson(imgPath, net, meta):
    r = dn.detect(net, meta, imgPath.encode("ascii"))
    rects = []
    for k in range(len(r)):
        if str(r[k][0])[2:-1] == "person":
            w = int(r[k][2][2])
            h = int(r[k][2][3])
            x = int(r[k][2][0] - w/2)
            y = int(r[k][2][1] - h/2)
            rects.append(tuple([x,y,w,h]))
    return rects

def loadNet(cfgPath, weightsPath, metaPath):
    net = dn.load_net(cfgPath.encode("ascii"), weightsPath.encode("ascii"), 0)
    meta = dn.load_meta(metaPath.encode("ascii"))
    return net, meta

def changeBackground(srcPath, backgroundPath, net, meta, output):
    rects = detectPerson(srcPath, net, meta)
    src = cv2.imread(srcPath)
    background = cv2.imread(backgroundPath)
    scaleW = 1
    if background.shape[1] < 1.5*src.shape[1]:
        scaleW = 2
    background_resize = cv2.resize(background, (scaleW*src.shape[1],src.shape[0]))
    mask = maskPerson(src, rects)
    changeBackgroundImg = pastePerson(src, mask, background_resize)
    cv2.imwrite(output, changeBackgroundImg)
