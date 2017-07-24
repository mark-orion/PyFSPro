#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:00:42 2017

@author: Mark Dammer
"""

import os.path
import time
from kivy.config import ConfigParser

class Settings:
    def __init__(self):
        self.Config = ConfigParser()
        self.Config.add_section('Input')
        self.Config.add_section('Processor')
        self.Config.add_section('Output')

        # default values
        self.cfgfilename = 'default.conf'
        self.helpfile = 'doc/PyFSPro_dataflow.jpg'
        self.numframes = 255  # No. of frames in stack
        self.color_mode = -1  # Greyscale output
        self.input_channel = 0  # Greyscale input
        self.video_src = 0  # Default camera
        self.video_width = 1024
        self.video_height = 768
        self.show_inp = True
        self.show_out = True
        self.show_vec = False
        self.show_help = False
        self.stack_status = False

        # timing settings for processing and display threads
        self.proc_thread_run = True
        self.proc_frames = True
        self.proc_fps = 1.0 / 30.0
        self.output_fps = 1.0 / 25.0

        # settings for video and image sequence recording
        self.recordi = False
        self.recordv = False
        self.novfile = True
        self.imgindx = 0
        self.output_path = './output/'
        self.image_dst = self.output_path
        self.video_dst = self.output_path

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
        #self.mode_in = 0
        self.mode_prc = 0
        #self.mode_out = 0
        self.pseudoc = False
        self.dyn_dark = True
        self.gain_inp = 1.0
        self.gain_out = 1.0
        self.offset_inp = 0
        self.offset_out = 0
        self.vec_zoom = 0.1
        self.loop = False
        self.stb_inp = False
        self.stb_out = False
        self.osd_txtline = 2
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.blue = (255, 0, 0)
        self.black = (0, 0, 0)
        self.colormaps = [
                'AUTUMN', 'BONE', 'JET', 'WINTER',
                'RAINBOW', 'OCEAN', 'SUMMER', 'SPRING',
                'COOL', 'HSV', 'PINK', 'HOT'
                ]
        self.set_defaults()

    def gettime(self):
        self.timestring = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        return self.timestring

    def set_defaults(self):
        # Section 'Input'
        self.Config.setdefault('Input','video_src', self.video_src)
        self.Config.setdefault('Input','video_width', self.video_width)
        self.Config.setdefault('Input','video_height', self.video_height)
        self.Config.setdefault('Input','loop', self.loop)
        self.Config.setdefault('Input','flip_x', self.flip_x)
        self.Config.setdefault('Input','flip_y', self.flip_y)
        self.Config.setdefault('Input','blr_inp', self.blr_inp)
        self.Config.setdefault('Input','equ_inp', self.equ_inp)
        self.Config.setdefault('Input','dnz_inp', self.dnz_inp)
        self.Config.setdefault('Input','dnz_inp_str', self.dnz_inp_str)
        self.Config.setdefault('Input','flt_inp', self.flt_inp)
        self.Config.setdefault('Input','flt_inp_strength', self.flt_inp_strength)
        #self.Config.setdefault('Input','mode_in', self.mode_in)
        self.Config.setdefault('Input','gain_inp', self.gain_inp)
        self.Config.setdefault('Input','offset_inp', self.offset_inp)
        self.Config.setdefault('Input','stb_inp', self.stb_inp)

        # Section 'Processor'
        self.Config.setdefault('Processor','mode_prc', self.mode_prc)
        self.Config.setdefault('Processor','dyn_dark', self.dyn_dark)
        self.Config.setdefault('Processor','blr_strength', self.blr_strength)
        self.Config.setdefault('Processor','numframes', self.numframes)

        # Section 'Output'
        self.Config.setdefault('Output','video_dst', self.video_dst)
        self.Config.setdefault('Output','image_dst', self.image_dst)
        self.Config.setdefault('Output','recordv', self.recordv)
        self.Config.setdefault('Output','recordi', self.recordi)
        self.Config.setdefault('Output','blr_out', self.blr_out)
        self.Config.setdefault('Output','equ_out', self.equ_out)
        self.Config.setdefault('Output','dnz_out', self.dnz_out)
        self.Config.setdefault('Output','dnz_out_str', self.dnz_out_str)
        self.Config.setdefault('Output','flt_out', self.flt_out)
        self.Config.setdefault('Output','flt_out_strength', self.flt_out_strength)
        #self.Config.setdefault('Output','mode_out', self.mode_out)
        self.Config.setdefault('Output','gain_out', self.gain_out)
        self.Config.setdefault('Output','offset_out', self.offset_out)
        self.Config.setdefault('Output','color_mode', self.color_mode)
        self.Config.setdefault('Output','pseudoc', self.pseudoc)
        self.Config.setdefault('Output','vec_zoom', self.vec_zoom)
        self.Config.setdefault('Output','stb_out', self.stb_out)

    def write_config(self, filename):
        if filename is None:
            filename = self.cfgfilename
        self.cfgfile = open(filename,'w')

        # Section 'Input'
        self.Config.set('Input','video_src', self.video_src)
        self.Config.set('Input','video_width', self.video_width)
        self.Config.set('Input','video_height', self.video_height)
        self.Config.set('Input','loop', self.loop)
        self.Config.set('Input','flip_x', self.flip_x)
        self.Config.set('Input','flip_y', self.flip_y)
        self.Config.set('Input','blr_inp', self.blr_inp)
        self.Config.set('Input','equ_inp', self.equ_inp)
        self.Config.set('Input','dnz_inp', self.dnz_inp)
        self.Config.set('Input','dnz_inp_str', self.dnz_inp_str)
        self.Config.set('Input','flt_inp', self.flt_inp)
        self.Config.set('Input','flt_inp_strength', self.flt_inp_strength)
        #self.Config.set('Input','mode_in', self.mode_in)
        self.Config.set('Input','gain_inp', self.gain_inp)
        self.Config.set('Input','offset_inp', self.offset_inp)
        self.Config.set('Input','stb_inp', self.stb_inp)

        # Section 'Processor'
        self.Config.set('Processor','mode_prc', self.mode_prc)
        self.Config.set('Processor','dyn_dark', self.dyn_dark)
        self.Config.set('Processor','blr_strength', self.blr_strength)
        self.Config.set('Processor','numframes', self.numframes)

        # Section 'Output'
        self.Config.set('Output','video_dst', self.video_dst)
        self.Config.set('Output','image_dst', self.image_dst)
        self.Config.set('Output','recordv', self.recordv)
        self.Config.set('Output','recordi', self.recordi)
        self.Config.set('Output','blr_out', self.blr_out)
        self.Config.set('Output','equ_out', self.equ_out)
        self.Config.set('Output','dnz_out', self.dnz_out)
        self.Config.set('Output','dnz_out_str', self.dnz_out_str)
        self.Config.set('Output','flt_out', self.flt_out)
        self.Config.set('Output','flt_out_strength', self.flt_out_strength)
        #self.Config.set('Output','mode_out', self.mode_out)
        self.Config.set('Output','gain_out', self.gain_out)
        self.Config.set('Output','offset_out', self.offset_out)
        self.Config.set('Output','color_mode', self.color_mode)
        self.Config.set('Output','pseudoc', self.pseudoc)
        self.Config.set('Output','vec_zoom', self.vec_zoom)
        self.Config.set('Output','stb_out', self.stb_out)

        self.Config.write(self.cfgfile)
        self.cfgfile.close()

    def read_config(self, filename):
        if os.path.isfile(filename):
            self.Config.read(filename)
            self.video_src = self.Config.get('Input','video_src')
            self.video_width = int(self.Config.get('Input','video_width'))
            self.video_height = int(self.Config.get('Input','video_height'))
            self.loop = self.Config.getboolean('Input','loop')
            self.flip_x = self.Config.getboolean('Input','flip_x')
            self.flip_y = self.Config.getboolean('Input','flip_y')
            self.blr_inp = self.Config.getboolean('Input','blr_inp')
            self.equ_inp = int(self.Config.get('Input','equ_inp'))
            self.dnz_inp = self.Config.getboolean('Input','dnz_inp')
            self.dnz_inp_str = float(self.Config.get('Input','dnz_inp_str'))
            self.flt_inp = int(self.Config.get('Input','flt_inp'))
            self.flt_inp_strength = float(self.Config.get('Input','flt_inp_strength'))
            self.gain_inp = float(self.Config.get('Input','gain_inp'))
            self.offset_inp = float(self.Config.get('Input','offset_inp'))
            self.stb_inp = self.Config.getboolean('Input','stb_inp')
            self.mode_prc = int(self.Config.get('Processor','mode_prc'))
            self.dyn_dark = self.Config.getboolean('Processor','dyn_dark')
            self.blr_strength = int(self.Config.get('Processor','blr_strength'))
            self.numframes = int(self.Config.get('Processor','numframes'))
            self.video_dst = self.Config.get('Output','video_dst')
            self.image_dst = self.Config.get('Output','image_dst')
            self.recordv = self.Config.getboolean('Output','recordv')
            self.recordi = self.Config.getboolean('Output','recordi')
            self.blr_out = self.Config.getboolean('Output','blr_out')
            self.equ_out = int(self.Config.get('Output','equ_out'))
            self.dnz_out = self.Config.getboolean('Output','dnz_out')
            self.dnz_out_str = float(self.Config.get('Output','dnz_out_str'))
            self.flt_out = int(self.Config.get('Output','flt_out'))
            self.flt_out_strength = float(self.Config.get('Output','flt_out_strength'))
            self.gain_out = float(self.Config.get('Output','gain_out'))
            self.offset_out = float(self.Config.get('Output','offset_out'))
            self.color_mode = int(self.Config.get('Output','color_mode'))
            self.pseudoc = self.Config.getboolean('Output','pseudoc')
            self.vec_zoom = float(self.Config.get('Output','vec_zoom'))
            self.stb_out = self.Config.getboolean('Output','stb_out')
        else:
            print('File ' + str(filename) + ' does not exist.')
