
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
    print("Microscope fatigue test: generating crosscorrelation template")
    with load_microscope("microscope_settings.npz") as ms:
        print("Checking for lens shading support...", end="")
        assert picamera_supports_lens_shading(), "You need the updated picamera module with lens shading!"
        print("present.")

        camera = ms.camera
        stage = ms.stage

        camera.resolution=(1640,1232)

        print("Starting camera preview with resolution 640x480")
        camera.start_preview(resolution=(640,480))
        
        print("Acquiring an RGB image...")
        image = ms.rgb_image().astype(np.float32)
        print("  got an image with shape {}, dtype {}".format(image.shape, image.dtype))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print("  converted to shape {}, dtype {}".format(image.shape, image.dtype))
        mean = np.mean(image)
        print("Mean value of image: {}".format(mean))
        w, h = image.shape
        template = (image - mean)[w//2-100:w//2+100, h//2-100:h//2+100]
        np.savez("template.npz", template=template)
        plt.figure()
        plt.imshow(template)
        plt.suptitle("Template image")

        for i in [0.1, ]:
            image = ms.rgb_image().astype(np.float32)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("Testing with another image: shape {}, dtype {}".format(image.shape, image.dtype))

        
            frame = image
            pos, corr = find_template(template, frame - np.mean(frame), return_corr = True, fraction = i)
        
            plt.figure()
            plt.imshow(corr.astype(np.float))
            plt.savefig("test_correlation_fraction_{}.jpg".format(i), bbox_inches='tight', dpi=180)
    plt.show()
