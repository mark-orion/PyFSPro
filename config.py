#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:00:42 2017

@author: Mark Dammer
"""

import os.path
import time
from kivy.config import ConfigParser
import numpy as np


class Settings(object):
    __slots__ = ['cfgfilename', 'background_source', 'max_stacksize', 'color_mode', 'input_channel',
                 'video_src', 'video_width', 'video_height', 'show_inp', 'show_out', 'show_vec',
                 'show_z', 'show_help', 'stack_status', 'single_thread', 'show_ihist', 'show_ohist',
                 'out', 'loop', 'run', 'x_avg', 'y_avg', 'full_avg', 'indzoom', 'indzoominc',
                 'log', 'logfile', 'loghandle', 'vecx', 'vecy', 'vecoldx', 'vecoldy', 'vecxcenter',
                 'vecycenter', 'vecxoffset', 'vecyoffset', 'out_xcenter', 'out_xscale',
                 'out_ycenter', 'out_yscale', 'actuator', 'actuator_parm', 'dout_active',
                 'override_active', 'joyx', 'joyy', 'joyxaxis', 'joyyaxis', 'joyaaxis',
                 'joybaxis', 'joyhat', 'joyoldx', 'joyoldy', 'joymaxx', 'joymaxy', 'proc_thread_run',
                 'proc_fps', 'output_fps', 'recordi', 'recordv', 'imgindx', 'video', 'output_dir',
                 'image_dst', 'blr_inp', 'blr_out', 'blr_strength', 'equ_inp', 'equ_out',
                 'dnz_inp', 'dnz_out', 'dnz_inp_str', 'dnz_out_str', 'flt_inp', 'flt_out',
                 'flt_inp_strength', 'flt_out_strength', 'flt_inp_kernel', 'flt_out_kernel',
                 'trfilter', 'trslope', 'trtrigger', 'trpre', 'trflt', 'trpref', 'output_file',
                 'inp_kernel', 'out_kernel', 'flip_x', 'flip_y', 'mode_prc', 'pseudoc', 'dyn_dark',
                 'gain_inp', 'gain_out', 'offset_inp', 'offset_out', 'stb_inp', 'stb_out',
                 'vec_zoom', 'green', 'red', 'blue', 'black', 'Config', 'kernels', 'numkernels',
                 'flt_inp_name', 'flt_out_name', 'rootwidget', 'imagestack', 'disp_image', 'oimage',
                 'iimage', 'act', 'vecz', 'procthread', 'numframes', 'raspicam', 'timestring',
                 'cap_prop_frame_width', 'cap_prop_frame_height', 'cap_prop_pos_frames', 'prop_fourcc', 'xorvalue']

    def __init__(self):
        self.Config = ConfigParser()
        self.Config.add_section('Input')
        self.Config.add_section('Processor')
        self.Config.add_section('Output')

        # default values
        self.cfgfilename = 'default.conf'
        self.background_source = 'assets/background.png'
        self.max_stacksize = 255  # Max. No. of frames in stack
        self.numframes = 128
        self.color_mode = -1  # Greyscale output
        self.input_channel = 0  # Greyscale input
        self.video_src = 0  # Default camera
        self.video_width = 1024
        self.video_height = 768
        self.show_inp = True
        self.show_out = True
        self.show_vec = False
        self.show_z = True
        self.show_help = False
        self.stack_status = False
        self.single_thread = False
        self.show_ihist = False
        self.show_ohist = False
        self.out = None
        self.loop = True
        self.run = True
        self.raspicam = False
        self.xorvalue = np.uint8(0)

        # opencv properties
        self.cap_prop_frame_width = 3
        self.cap_prop_frame_height = 4
        self.cap_prop_pos_frames = 1
        self.prop_fourcc = 'YUYV'

        # variables for vector display and actuators
        self.x_avg = 0
        self.y_avg = 0
        self.full_avg = 0
        self.indzoom = 1
        self.indzoominc = 0
        self.log = False
        self.logfile = 'none'
        self.loghandle = None
        self.vecx = 0
        self.vecy = 0
        self.vecoldx = 0
        self.vecoldy = 0
        self.vecxcenter = 0
        self.vecycenter = 0
        self.vecxoffset = 0
        self.vecyoffset = 0
        self.out_xcenter = 0
        self.out_ycenter = 0
        self.out_xscale = 0
        self.out_yscale = 0
        self.actuator = False
        self.actuator_parm = '127.0.0.1:9003'
        self.dout_active = False
        self.override_active = False

        # joystick Configuration
        self.joyx = 0
        self.joyy = 0
        self.joyxaxis = 2
        self.joyyaxis = 3
        self.joyaaxis = 0
        self.joybaxis = 1
        self.joyhat = 0
        self.joyoldx = 0
        self.joyoldy = 0
        self.joymaxx = 32768
        self.joymaxy = 32768

        # timing settings for processing and display threads
        self.proc_thread_run = True
        self.proc_fps = 1.0 / 30.0
        self.output_fps = 1.0 / 25.0

        # settings for transient filter
        self.trfilter = False
        self.trslope = 1
        self.trtrigger = 1
        self.trpre = 0
        self.trflt = 0
        self.trpref = 0

        # settings for video and image sequence recording
        self.recordi = False
        self.recordv = False
        self.imgindx = 0
        self.video = None
        self.output_file = None
        self.output_dir = './output/'
        self.image_dst = self.output_dir

        # switches for image filters and tools
        self.blr_inp = False
        self.blr_out = False
        self.blr_strength = 7
        self.equ_inp = 0
        self.equ_out = 0
        self.dnz_inp = False
        self.dnz_out = False
        self.dnz_inp_str = 33
        self.dnz_out_str = 33
        self.flt_inp = 0
        self.flt_out = 0
        self.flt_inp_strength = 0
        self.flt_out_strength = 0
        self.flt_inp_kernel = None
        self.flt_out_kernel = None
        self.flip_x = False
        self.flip_y = False
        self.inp_kernel = None
        self.out_kernel = None
        self.mode_prc = 0
        self.pseudoc = False
        self.dyn_dark = True
        self.gain_inp = 1.0
        self.gain_out = 1.0
        self.offset_inp = 0
        self.offset_out = 0
        self.stb_inp = False
        self.stb_out = False
        self.vec_zoom = 0.1
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.blue = (255, 0, 0)
        self.black = (0, 0, 0)
        # self.set_defaults()

    def gettime(self):
        self.timestring = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        return self.timestring

    def write_config(self, filename, widget):
        if filename is None:
            filename = self.cfgfilename

        # Section 'Input'
        self.Config.set('Input', 'play_mode', widget.playmode_wid.text)
        self.Config.set('Input', 'video_src', self.video_src)
        self.Config.set('Input', 'video_width', self.video_width)
        self.Config.set('Input', 'video_height', self.video_height)
        self.Config.set('Input', 'video_codec', self.prop_fourcc)
        self.Config.set('Input', 'input', widget.inp_wid.state)
        self.Config.set('Input', 'flip_x', widget.flipx_wid.state)
        self.Config.set('Input', 'flip_y', widget.flipy_wid.state)
        self.Config.set('Input', 'blr_inp', widget.iblur_wid.state)
        self.Config.set('Input', 'equ_inp', widget.iequ_wid.text)
        self.Config.set('Input', 'dnz_inp', widget.idnz_wid.state)
        self.Config.set('Input', 'dnz_inp_str', self.dnz_inp_str)
        self.Config.set('Input', 'flt_inp', widget.iflt_wid.text)
        self.Config.set('Input', 'flt_inp_strength', self.flt_inp_strength)
        self.Config.set('Input', 'stb_inp', widget.istab_wid.state)
        self.Config.set('Input', 'gain_inp', widget.igain_wid.value)
        self.Config.set('Input', 'offset_inp', widget.ioffset_wid.value)
        self.Config.set('Input', 'color_channel', widget.ichan_wid.text)

        # Section 'Processor'
        self.Config.set('Processor', 'mode_prc', widget.proc_wid.text)
        self.Config.set('Processor', 'dyn_dark', widget.dark_wid.state)
        self.Config.set('Processor', 'blr_strength', self.blr_strength)
        self.Config.set('Processor', 'stack_size', widget.stack_wid.value)
        self.Config.set('Processor', 'ind_zoom', widget.indzoom_wid.value)
        self.Config.set('Processor', 'dout', widget.dout_wid.state)
        self.Config.set('Processor', 'actuator', widget.actuator_wid.state)
        self.Config.set('Processor', 'override', widget.override_wid.state)

        # Section 'Output'
        self.Config.set('Output', 'output', widget.out_wid.state)
        self.Config.set('Output', 'output_dir', self.output_dir)
        self.Config.set('Output', 'recorder', widget.recorder_wid.text)
        self.Config.set('Output', 'blr_out', widget.oblur_wid.state)
        self.Config.set('Output', 'equ_out', widget.oequ_wid.text)
        self.Config.set('Output', 'dnz_out', widget.odnz_wid.state)
        self.Config.set('Output', 'dnz_out_str', self.dnz_out_str)
        self.Config.set('Output', 'flt_out', widget.oflt_wid.text)
        self.Config.set('Output', 'flt_out_strength', self.flt_out_strength)
        self.Config.set('Output', 'stb_out', widget.ostab_wid.state)
        self.Config.set('Output', 'gain_out', widget.ogain_wid.value)
        self.Config.set('Output', 'offset_out', widget.ooffset_wid.value)
        self.Config.set('Output', 'color_mode', widget.colors_wid.text)
        self.Config.set('Output', 'background_source', self.background_source)
        self.Config.set('Output', 'osd', widget.osd_wid.state)
        self.Config.set('Output', 'hud', widget.vec_wid.state)
        self.Config.set('Output', 'trf_mode', widget.trf_wid.text)
        self.Config.set('Output', 'trf_trig', self.trtrigger)
        self.Config.read(filename)
        self.Config.write()

    def read_parms(self, filename):
        if os.path.isfile(filename):
            self.Config.read(filename)
            # Section 'Input'
            self.video_src = self.Config.get('Input', 'video_src')
            self.video_width = int(self.Config.get('Input', 'video_width'))
            self.video_height = int(self.Config.get('Input', 'video_height'))
            self.prop_fourcc = self.Config.get('Input', 'video_codec')
            self.dnz_inp_str = float(self.Config.get('Input', 'dnz_inp_str'))
            self.flt_inp_strength = float(
                self.Config.get('Input', 'flt_inp_strength'))
            # Section 'Processor'
            self.blr_strength = int(
                self.Config.get('Processor', 'blr_strength'))
            # Section 'Output'
            self.output_dir = self.Config.get('Output', 'output_dir')
            self.dnz_out_str = float(self.Config.get('Output', 'dnz_out_str'))
            self.flt_out_strength = float(
                self.Config.get('Output', 'flt_out_strength'))
            self.background_source = self.Config.get(
                'Output', 'background_source')
            self.trtrigger = self.Config.get('Output', 'trf_trig')
        else:
            print('File ' + str(filename) + ' does not exist.')

    def read_ui_parms(self, filename, widget):
        if os.path.isfile(filename):
            self.Config.read(filename)
            # Section 'Input'
            widget.playmode_wid.text = self.Config.get('Input', 'play_mode')
            widget.inp_wid.state = self.Config.get('Input', 'input')
            widget.flipx_wid.state = self.Config.get('Input', 'flip_x')
            widget.flipy_wid.state = self.Config.get('Input', 'flip_y')
            widget.iblur_wid.state = self.Config.get('Input', 'blr_inp')
            widget.iequ_wid.text = self.Config.get('Input', 'equ_inp')
            widget.idnz_wid.state = self.Config.get('Input', 'dnz_inp')
            widget.iflt_wid.text = self.Config.get('Input', 'flt_inp')
            widget.istab_wid.state = self.Config.get('Input', 'stb_inp')
            widget.igain_wid.value = float(
                self.Config.get('Input', 'gain_inp'))
            widget.ioffset_wid.value = float(
                self.Config.get('Input', 'offset_inp'))
            widget.ichan_wid.text = self.Config.get('Input', 'color_channel')
            # Section 'Processor'
            widget.proc_wid.text = self.Config.get('Processor', 'mode_prc')
            widget.dark_wid.state = self.Config.get('Processor', 'dyn_dark')
            widget.stack_wid.value = int(
                self.Config.get('Processor', 'stack_size'))
            widget.indzoom_wid.value = float(
                self.Config.get('Processor', 'ind_zoom'))
            widget.dout_wid.state = self.Config.get('Processor', 'dout')
            widget.actuator_wid.state = self.Config.get(
                'Processor', 'actuator')
            widget.override_wid.state = self.Config.get(
                'Processor', 'override')
            # Section 'Output'
            widget.out_wid.state = self.Config.get('Output', 'output')
            widget.recorder_wid.text = self.Config.get('Output', 'recorder')
            widget.oblur_wid.state = self.Config.get('Output', 'blr_out')
            widget.oequ_wid.text = self.Config.get('Output', 'equ_out')
            widget.odnz_wid.state = self.Config.get('Output', 'dnz_out')
            widget.oflt_wid.text = self.Config.get('Output', 'flt_out')
            widget.ostab_wid.state = self.Config.get('Output', 'stb_out')
            widget.ogain_wid.value = float(
                self.Config.get('Output', 'gain_out'))
            widget.ooffset_wid.value = float(
                self.Config.get('Output', 'offset_out'))
            widget.colors_wid.text = self.Config.get('Output', 'color_mode')
            widget.osd_wid.state = self.Config.get('Output', 'osd')
            widget.vec_wid.state = self.Config.get('Output', 'hud')
            widget.trf_wid.text = self.Config.get('Output', 'trf')

        else:
            print('File ' + str(filename) + ' does not exist.')
