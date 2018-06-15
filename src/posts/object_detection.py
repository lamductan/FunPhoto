import sys
from ctypes import *
import math
import random
import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches
from PIL import Image
import argparse

sys.path.append("/home/lamductan/python/darknet/python")
import darknet as dn

def load_net(cfgPath, weightsPath):
    net = dn.load_net(cfgPath.encode("ascii"), weightsPath.encode("ascii"), 0)
    return net

def load_meta(metaPath):
    meta = dn.load_meta(metaPath.encode("ascii"))
    return meta

def detect(net, meta, imgPath, output):
    r = dn.detect(net, meta, imgPath.encode("ascii"))
    plt.axis('off')
    im2 = np.array(Image.open(imgPath), dtype=np.uint8)
    fig,ax = plt.subplots(1)
    ax.axis('off')
    ax.imshow(im2)
    cmap = get_cmap(len(r))
    for k in range(len(r)):
        w = r[k][2][2]
        h = r[k][2][3]
        x = r[k][2][0] - w/2
        y = r[k][2][1] - h/2
        color = np.random.rand(4,1)
        rect = patches.Rectangle((x,y), w, h, linewidth=1, edgecolor=cmap(k), facecolor='none')
        ax.text(x, y, str(r[k][0])[2:-1], color='white', bbox={'facecolor':'black'})
        ax.add_patch(rect)
    ax.plot()
    fig.savefig(output)
   
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def main(imgPath="/home/lamductan/python/darknet/python/kim-so-hyun.jpg", \
         cfgPath="/home/lamductan/python/darknet/cfg/yolov3.cfg", \
         weightsPath="/home/lamductan/python/darknet/weights/yolov3.weights", 
         metaPath="/home/lamductan/python/darknet/cfg/coco.data", \
         output='/home/lamductan/FIT/ML/results/image.jpg'):
    
    net = dn.load_net(cfgPath.encode("ascii"), weightsPath.encode("ascii"), 0)
    meta = dn.load_meta(metaPath.encode("ascii"))
    detect(net, meta, imgPath, output)

if __name__ == "__main__":
    main()
