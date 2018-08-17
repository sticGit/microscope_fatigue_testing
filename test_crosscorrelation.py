
from __future__ import print_function
import io
import sys
import os
import time
import argparse
import numpy as np
import picamera
from builtins import input
from readchar import readchar, readkey
from openflexure_stage import OpenFlexureStage
from openflexure_microscope import load_microscope
from openflexure_microscope.microscope import picamera_supports_lens_shading
import scipy
from scipy import ndimage
import matplotlib.pyplot as plt
from contextlib import contextmanager, closing
import data_file
import cv2
from camera_stuff import find_template
#import h5py
import threading
import queue

if __name__ == "__main__":

    with load_microscope("microscope_settings.npz") as ms:

        assert picamera_supports_lens_shading(), "You need the updated picamera module with lens shading!"

        camera = ms.camera
        stage = ms.stage

        camera.resolution=(1640,1232)

        camera.start_preview(resolution=(640,480))
        
        image = ms.rgb_image().astype(np.float32)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean = np.mean(image)
        w, h = image.shape
        template = (image - mean)[w//2-100:w//2+100, h//2-100:h//2+100]
        np.savez("template.npz", template=template)
        plt.figure()
        plt.imshow(template)

        for i in [0.1, ]:
            image = ms.rgb_image().astype(np.float32)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        
            frame = image
            pos, corr = find_template(template, frame - np.mean(frame), return_corr = True, fraction = i)
        
            plt.figure()
            plt.imshow(corr.astype(np.float))
            plt.savefig("test_correlation_fraction_{}.jpg".format(i), bbox_inches='tight', dpi=180)
    plt.show()
