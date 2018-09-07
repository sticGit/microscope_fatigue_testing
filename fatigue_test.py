
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
from scipy import ndimage, signal
import matplotlib.pyplot as plt
from contextlib import contextmanager, closing
import data_file
import cv2
from camera_stuff import find_template
#import h5py
import threading
import queue

if __name__ == "__main__":

    with load_microscope("microscope_settings.npz", dummy_stage = False) as ms, \
         closing(data_file.Datafile(filename = "fatigue_tests.hdf5")) as df:
        
        assert picamera_supports_lens_shading(), "You need the updated picamera module with lens shading!"

        camera = ms.camera
        stage = ms.stage

        step_size = 1000
        n_steps = 3
        backlash = 0

        camera.resolution=(1640,1232)
        stage.backlash = backlash

        data_group = df.new_group("fatigue_test")

        camera.start_preview(resolution=(640,480))

        #stage.move_rel([-backlash, -backlash, -backlash])
        #stage.move_rel([backlash, backlash, backlash])

        frame = ms.rgb_image().astype(np.float32).mean(axis=2)
        #mean = np.mean(image)
        #templ8 = (image - mean)[100:-100, 100:-100]
        template = np.load("template.npz")['template']

        d, corr = find_template(template, frame, return_corr = True, fraction=0.15)        

        initial_stage_position = stage.position

        try:
            while True:
                for d in [1, -1]:
                    data_stage = np.zeros((n_steps + 1, 3))
                    data_cam = np.zeros((n_steps + 1, 2))
                    for i in range(n_steps+1):
                        if i>0:
                            stage.move_rel([d*step_size, 0, 0])
                        data_stage[i, 0:] = stage.position
                        frame = ms.rgb_image().astype(np.float32).mean(axis=2)
                        data_cam[i, 0:], corr = find_template(template, frame, return_corr = True, fraction=0.15)
                    df.add_data(data_stage, data_group, "data_stage_{}".format("out" if d==1 else "back"))
                    df.add_data(data_cam, data_group, "data_cam_{}".format("out" if d==1 else "back"))
        except KeyboardInterrupt:
            print("Got a keyboard interrupt, stopping...")

        stage.move_abs(initial_stage_position)
        camera.stop_preview()
        print("Done")
