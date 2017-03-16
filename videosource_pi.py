#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:28:47 2017

@author: Mark Dammer

FrameInput class to grab frames of given size from camera or file.
"""

from __future__ import division, print_function
import sys
import time
import cv2
import picamera
import picamera.array

class FrameInput():
    def __init__(self, video_src, input_width, input_height):
        self.loop = False
        self.video_src = video_src
        self.input_width = int(input_width)
        self.input_height = int(input_height)
        self.cam = picamera.PiCamera()
        if self.input_width > 0 and self.input_height > 0:
            self.cam.resolution = (self.input_width, self.input_height)
        # let camera warm up
        self.cam.start_preview()
        time.sleep(2)
        self.frame_width = self.input_width
        self.frame_height = self.input_height

    def grab_frame(self):
        with picamera.array.PiRGBArray(self.cam) as self.stream:
            self.cam.capture(self.stream, format='bgr', use_video_port=True)
            # At this point the image is available as stream.array
            self.video_frame = self.stream.array
        self.gray_frame = cv2.cvtColor(self.video_frame, cv2.COLOR_BGR2GRAY)
        return self.gray_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)
