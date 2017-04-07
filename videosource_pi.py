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
import threading
import cv2
import picamera
import picamera.array

class FrameInput():
    def __init__(self, video_src, input_width, input_height):
        self.loop = False
        self.video_src = video_src
        self.input_width = int(input_width)
        self.input_height = int(input_height)
        self.frame_width = self.input_width
        self.frame_height = self.input_height
        self.thread = None
        self.video_frame = None
        self.exit_thread = False
        if self.thread is None:
            # start background frame thread
            self.thread = threading.Thread(target=self.framegrabber_thread)
            self.thread.start()

            # wait until frames start to be available
            while self.video_frame is None:
                time.sleep(0)
        
    def framegrabber_thread(self):
        with picamera.PiCamera() as self.cam:
            # camera setup
            if self.input_width > 0 and self.input_height > 0:
                self.cam.resolution = (self.input_width, self.input_height)
            # let camera warm up
            self.cam.start_preview()
            time.sleep(2)
            self.stream = picamera.array.PiRGBArray(self.cam)
            for foo in self.cam.capture_continuous(self.stream, 'bgr',
                                                 use_video_port=True):
                # store frame
                self.stream.seek(0)
                #self.video_frame = self.stream.read()
                self.video_frame = self.stream.array
                # reset stream for next frame
                self.stream.seek(0)
                self.stream.truncate()
                if self.exit_thread:
                    break

    def grab_frame(self):
        return self.video_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)
