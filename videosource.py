#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:28:47 2017

@author: Mark Dammer

FrameInput class to grab frames of given size from camera or file.
"""

from __future__ import division, print_function
import sys
import cv2
import cv2.cv as cv

class FrameInput():
    def __init__(self, video_src, input_width, input_height):
        self.video_src = video_src
        self.input_width = input_width
        self.input_height = input_height
        self.cam = cv2.VideoCapture(self.video_src)
        if self.input_width > 0 and self.input_height > 0:
            self.cam.set(cv.CV_CAP_PROP_FRAME_WIDTH,
                         float(self.input_width))
            self.cam.set(cv.CV_CAP_PROP_FRAME_HEIGHT,
                         float(self.input_height))
        if self.cam is None or not self.cam.isOpened():
            print("Warning: unable to open video source:" +
                  str(self.video_src), file = sys.stderr)
        self.frame_width = int(self.cam.get(cv.CV_CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cam.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
        self.ret, self.img = self.cam.read()
        if self.ret is False:
            self.error_handler()

    def grab_frame(self):
        self.ret, self.video_frame = self.cam.read()
        if self.ret is False:
            self.error_handler()
        self.gray_frame = cv2.cvtColor(self.video_frame, cv2.COLOR_BGR2GRAY)
        return self.gray_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)
