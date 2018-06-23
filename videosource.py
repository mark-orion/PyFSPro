#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:28:47 2017

@author: Mark Dammer

FrameInput class to grab frames of given size from camera or file.
"""

from __future__ import division, print_function
import sys
import threading
import time
import cv2

try:
    import picamera
    import picamera.array
    raspi = True
except:
    raspi = False

'''
class FrameInputPi(object):
    __slots__ = ['raspi', 'input_width', 'input_height', 'thread',
                 'video_frame', 'exit_thread', 'cam', 'stream', 'foo',
                 'frame_width', 'frame_height', 'loop']

    def __init__(self, video_src, input_width, input_height, cnf):
        if raspi is False:
            print('Picamera not found, exiting.')
            sys.exit(0)
        self.cam = picamera.PiCamera()
        self.input_width = int(input_width)
        self.input_height = int(input_height)
        self.frame_width = self.input_width
        self.frame_height = self.input_height
        self.thread = None
        self.loop = False
        self.video_frame = None
        self.exit_thread = False
        if self.input_width > 0 and self.input_height > 0:
            self.cam.resolution = (self.input_width, self.input_height)
        self.stream = picamera.array.PiRGBArray(self.cam)

    def grab_frame(self):
        self.cam.capture(self.stream, 'bgr', use_video_port=True)
        self.video_frame = self.stream.array
        return self.video_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)

'''

class FrameInputPi(object):
    __slots__ = ['raspi', 'input_width', 'input_height', 'thread',
                 'video_frame', 'exit_thread', 'cam', 'stream', 'foo',
                 'frame_width', 'frame_height', 'loop', 'cnf']

    def __init__(self, video_src, input_width, input_height, cnf):
        if raspi is False:
            print('Picamera not found, exiting.')
            sys.exit(0)
        self.input_width = int(input_width)
        self.input_height = int(input_height)
        self.frame_width = self.input_width
        self.frame_height = self.input_height
        self.thread = None
        self.loop = False
        self.video_frame = None
        self.exit_thread = False
        self.cnf = cnf
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
            self.cam.stop_preview()
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
                if not self.cnf.proc_thread_run:
                    break

    def grab_frame(self):
        return self.video_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)


class FrameInput(object):
    __slots__ = ['cnf', 'video_frame', 'exit_thread', 'loop', 'video_src', 'input_width',
                 'input_height', 'cam', 'frame_width', 'frame_height', 'ret', 'old_frame',
                 'img', 'prop_width', 'prop_height', 'prop_pos']

    def __init__(self, video_src, input_width, input_height, cnf):
        self.cnf = cnf
        self.video_frame = None
        self.exit_thread = False  # needed for compatibility with videosource_pi.py
        self.loop = False
        self.video_src = video_src
        self.input_width = input_width
        self.input_height = input_height
        self.cam = cv2.VideoCapture(self.video_src)
        if self.input_width > 0 and self.input_height > 0:
            self.cam.set(self.cnf.cap_prop_frame_width,
                         float(self.input_width))
            self.cam.set(self.cnf.cap_prop_frame_height,
                         float(self.input_height))
        if self.cam is None or not self.cam.isOpened():
            print("Warning: unable to open video source:" +
                  str(self.video_src), file=sys.stderr)
        self.frame_width = int(self.cam.get(self.cnf.cap_prop_frame_width))
        self.frame_height = int(self.cam.get(self.cnf.cap_prop_frame_height))
        self.ret, self.img = self.cam.read()
        if self.ret is False:
            self.error_handler()

    def grab_frame(self):
        self.old_frame = self.video_frame
        self.ret, self.video_frame = self.cam.read()
        while self.ret is False:
            if self.loop:
                self.cam.set(self.cnf.cap_prop_pos_frames, 0)
                self.ret, self.video_frame = self.cam.read()
            else:
                self.cnf.rootwidget.playmode_wid.text = '||'
                self.ret = True
                self.video_frame = self.old_frame
        return self.video_frame

    def error_handler(self):
        print("No more frames or capture device down - exiting.",
              file=sys.stderr)
        sys.exit(0)
