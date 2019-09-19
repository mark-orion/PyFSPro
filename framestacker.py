#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:23:37 2017

@author: Mark Dammer

This is the FrameStack class that does all the magic.

"""
from __future__ import division, print_function
import numpy as np


class FrameStack(object):
    __slots__ = ['dyn_dark', 'filling_stack', 'flip_x', 'flip_y', 'blr_inp', 'blr_out',
                 'max_value', 'default_value', 'min_value', 'index', 'gain_inp', 'gain_out',
                 'offset_inp', 'offset_out', 'stacksize', 'stackrange', 'width', 'height',
                 'center_x', 'center_y', 'kernel_size', 'cumz',
                 'ulimit', 'llimit', 'pixelvalue', 'kernel_value', 'raw_inp', 'frame', 'tmp_frame',
                 'inp_frame', 'sum_frames', 'frame_stack', 'avg', 'sqd', 'sum_sqd', 'sqd_stack',
                 'dark_frame', 'var', 'sd', 'z', 'cumsum', 'left', 'right', 'upper', 'lower', 'full_avg', 'left_avg',
                 'left_diff', 'right_diff', 'upper_diff', 'lower_diff','left_sd', 'right_sd', 'upper_sd', 'lower_sd',
                 'right_avg', 'left_cumz', 'right_cumz', 'upper_cumz', 'lower_cumz',
                 'upper_avg', 'lower_avg', 'x_avg', 'y_avg', 'raw_out', 'float_out', 'r', 'c',
                 'max_inp', 'min_inp', 'max_out', 'min_out', 'kernel', 'i', 'proc_out',
                 'initframe', 'prefilter', 'trfilter', 'trpre', 'trflt']

    def __init__(self, stacksize, stackrange, width, height):
        self.width = int(width)
        self.height = int(height)
        self.center_x = int(self.width / 2)
        self.center_y = int(self.height / 2)
        self.dyn_dark = True
        self.filling_stack = True
        self.flip_x = False
        self.flip_y = False
        self.blr_inp = False
        self.blr_out = False
        self.left = []
        self.right = []
        self.upper = []
        self.lower = []
        self.left_diff = []
        self.right_diff = []
        self.upper_diff = []
        self.lower_diff = []
        self.full_avg = 0
        self.left_avg = 0
        self.right_avg = 0
        self.upper_avg = 0
        self.lower_avg = 0
        self.left_cumz = 0
        self.right_cumz = 0
        self.upper_cumz = 0
        self.lower_cumz = 0
        self.left_sd = 0
        self.right_sd = 0
        self.upper_sd = 0
        self.lower_sd = 0
        self.max_value = 255
        self.default_value = 127.5
        self.min_value = 0
        self.index = 0
        self.gain_inp = 1.0
        self.gain_out = 1.0
        self.offset_inp = 0.0
        self.offset_out = 0.0
        self.stacksize = stacksize
        self.stackrange = stackrange
        self.kernel_size = 7
        self.kernel = []
        self.setKernel(self.kernel_size)
        self.initframe = self.uniFrame(0)
        self.initStack(self.stackrange)
        self.resetCUMSUM()

    def uniFrame(self, pixelvalue):
        return np.full((self.height, self.width), pixelvalue, np.float32)

    def setKernel(self, kernel_size):
        self.kernel_size = kernel_size
        self.kernel_value = float(1 / kernel_size)
        self.kernel = [self.kernel_value for self.i in range(self.kernel_size)]

    def addFrame(self, frame):
        return self.addFloatFrame(np.float32(frame))

    def addFloatFrame(self, frame):
        self.raw_inp = frame
        self.tmp_frame = np.copy(self.raw_inp)
        if self.flip_x:
            self.tmp_frame = np.flipud(self.tmp_frame)
        if self.flip_y:
            self.tmp_frame = np.fliplr(self.tmp_frame)
        self.frame = np.clip(
            np.absolute(self.tmp_frame + self.offset_inp) * self.gain_inp, 0, 255)
        if self.blr_inp:
            for self.r in range(self.height):
                self.frame[self.r, :] = np.convolve(
                    self.frame[self.r, :], self.kernel, 'same')
            for self.c in range(self.width):
                self.frame[:, self.c] = np.convolve(
                    self.frame[:, self.c], self.kernel, 'same')
        self.inp_frame = np.copy(self.frame)
        self.sum_frames -= (self.frame_stack[self.index] - self.frame)
        self.frame_stack[self.index] = self.frame
        self.avg = self.sum_frames / self.stackrange
        if self.dyn_dark == 1:
            self.dark_frame = self.avg
        self.sqd = np.square(self.frame - self.avg)
        self.sum_sqd -= (self.sqd_stack[self.index] - self.sqd)
        self.sqd_stack[self.index] = self.sqd
        self.var = self.sum_sqd / self.stackrange
        self.sd = np.sqrt(self.var)
        self.z = (self.frame - self.avg) / self.sd
        if self.index >= self.stackrange - 1:
            self.index = 0
            self.filling_stack = False
        else:
            self.index += 1
        return self.filling_stack

    def getINP(self):
        return self.postProcess(self.inp_frame)

    def getAVG(self):
        return self.postProcess(self.avg)

    def getVAR(self):
        return self.postProcess(self.var)

    def getSD(self):
        return self.postProcess(np.sqrt(self.var))

    def getDIFF(self):
        return self.postProcess(np.absolute(self.inp_frame - self.dark_frame))

    def getCUMSUM(self):
        self.cumsum += (self.inp_frame - self.dark_frame)
        return self.postProcess(np.absolute(self.cumsum))

    def getCUMZ(self):
        self.cumz += self.z
        return self.postProcess(self.cumz)

    def setVECROI(self, img):
        self.left = img[0:self.height,0:self.center_x]
        self.right = img[0:self.height,self.center_x:self.width]
        self.upper = img[0:self.center_y,0:self.width]
        self.lower = img[self.center_y:self.height,0:self.width]
        return

    def getVectorCUMZ(self, img):
        self.setVECROI(img)
        self.full_avg = np.nanmean(img)
        self.left_avg = np.nanmean(self.left)
        self.right_avg = np.nanmean(self.right)
        self.upper_avg = np.nanmean(self.upper)
        self.lower_avg = np.nanmean(self.lower)
        self.left_diff = self.left - self.left_avg
        self.left_sd = np.sqrt(np.sum(np.square(self.left_diff)) / self.left.size)
        self.left_cumz += np.sum(self.left_diff / self.left_sd)
        self.right_diff = self.right - self.right_avg
        self.right_sd = np.sqrt(np.sum(np.square(self.right_diff)) / self.right.size)
        self.right_cumz += np.sum(self.right_diff / self.right_sd)
        self.upper_diff = self.upper - self.upper_avg
        self.upper_sd = np.sqrt(np.sum(np.square(self.upper_diff)) / self.upper.size)
        self.upper_cumz += np.sum(self.upper_diff / self.upper_sd)
        self.lower_diff = self.lower - self.lower_avg
        self.lower_sd = np.sqrt(np.sum(np.square(self.lower_diff)) / self.lower.size)
        self.lower_cumz += np.sum(self.lower_diff / self.lower_sd)
        self.x_avg = self.right_cumz - self.left_cumz
        self.y_avg = self.upper_cumz - self.lower_cumz
        return self.full_avg, self.x_avg, self.y_avg

    def getVectorAVG(self, img):
        self.setVECROI(img)
        self.full_avg = np.nanmean(img)
        self.left_avg = np.nanmean(self.left)
        self.right_avg = np.nanmean(self.right)
        self.upper_avg = np.nanmean(self.upper)
        self.lower_avg = np.nanmean(self.lower)
        self.x_avg = self.right_avg - self.left_avg
        self.y_avg = self.upper_avg - self.lower_avg
        return self.full_avg, self.x_avg, self.y_avg

    def getTRFILTER(self, img):
        self.prefilter = self.trfilter
        self.trfilter = img
        self.trpre = np.nanmean(abs(self.prefilter))
        self.trflt = np.nanmean(abs(self.trfilter))
        return self.trpre, self.trflt

    def resetCUMSUM(self):
        self.cumsum[:] = self.uniFrame(self.default_value)
        self.cumz[:] = self.uniFrame(self.default_value)

    def loadDark(self, frame):
        self.dark_frame = np.float32(frame)

    def postProcess(self, raw_out):
        self.raw_out = raw_out
        self.float_out = (self.raw_out + self.offset_out) * self.gain_out
        self.proc_out = np.clip(self.float_out, self.min_value, self.max_value)
        if self.blr_out:
            for self.r in range(self.height):
                self.proc_out[self.r, :] = np.convolve(
                    self.proc_out[self.r, :], self.kernel, 'same')
            for self.c in range(self.width):
                self.proc_out[:, self.c] = np.convolve(
                    self.proc_out[:, self.c], self.kernel, 'same')
        return np.uint8(self.proc_out)

    def autoInpGain(self):
        self.max_inp = np.nanmax(self.raw_inp)
        self.min_inp = np.nanmin(self.raw_inp)
        gain_inp = 255.0 / abs(self.max_inp - self.min_inp)
        offset_inp = -self.min_inp
        return gain_inp, offset_inp

    def autoOutGain(self):
        self.max_out = np.nanmax(self.raw_out)
        self.min_out = np.nanmin(self.raw_out)
        gain_out = 255.0 / abs(self.max_out - self.min_out)
        offset_out = -self.min_out
        return gain_out, offset_out

    def resetStack(self):
        for self.i in range(self.stackrange):
            self.frame_stack[self.i] = self.initframe
            self.sqd_stack[self.i] = self.initframe
        self.frame[:] = self.initframe
        self.inp_frame[:] = self.initframe
        self.raw_inp[:] = self.initframe
        self.raw_out[:] = self.initframe
        self.sum_frames[:] = self.initframe
        self.sum_sqd[:] = self.initframe
        self.z[:] = self.initframe
        self.prefilter[:] = self.initframe
        self.trfilter[:] = self.initframe
        self.index = 0
        self.resetCUMSUM()
        self.filling_stack = True

    def initStack(self, stackrange):
        self.stackrange = stackrange
        if self.stackrange > self.stacksize:
            self.stackrange = self.stacksize
        if self.stackrange < 1:
            self.stackrange = 1
        self.dark_frame = np.copy(self.initframe)
        self.frame = np.copy(self.initframe)
        self.inp_frame = np.copy(self.initframe)
        self.raw_inp = np.copy(self.initframe)
        self.raw_out = np.copy(self.initframe)
        self.sum_frames = np.copy(self.initframe)
        self.sum_sqd = np.copy(self.initframe)
        self.z = np.copy(self.initframe)
        self.cumz = np.copy(self.initframe)
        self.cumsum = np.copy(self.initframe)
        self.prefilter = np.copy(self.initframe)
        self.trfilter = np.copy(self.initframe)
        self.frame_stack = []
        self.sqd_stack = []
        for self.i in range(self.stackrange):
            self.frame_stack.append(np.copy(self.initframe))
            self.sqd_stack.append(np.copy(self.initframe))
        self.index = 0
        self.filling_stack = True
