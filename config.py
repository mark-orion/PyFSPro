#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:00:42 2017

@author: Mark Dammer
"""

import ConfigParser

class Settings:
    def __init__(self):
        self.Config = ConfigParser.ConfigParser()
        self.Config.add_section('Input')
        self.Config.add_section('Processor')
        self.Config.add_section('Output')
        self.Config.add_section('Display')
        self.Config.add_section('Pattern_Generator')
        self.Config.add_section('Misc')
        # default values
        self.cfgfilename = 'default.conf'
        self.numframes = 255  # No. of frames in stack
        self.color_mode = -1  # Greyscale output
        self.video_src = 0  # Default camera
        self.video_width = 1024
        self.video_height = 768
        self.window_x = 100  # Position of first window on screen
        self.window_y = 100
        self.window_space = 50  # Space between windows
        self.window_width = 800 # Default window size
        self.window_height = 600
        
        # default values for pattern generator
        self.screen_width = 1920
        self.screen_height = 1080
        self.pattern_size = 0
        self.pattern_mode = 2
        self.backgnd = False
        
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
        self.flt_strength_increment = 0.1
        self.flip_x = False
        self.flip_y = False
        self.inp_kernel = None
        self.out_kernel = None
        self.mode_in = 0
        self.mode_prc = 0
        self.mode_out = 0
        self.pseudoc = False
        self.dyn_dark = True
        self.gain_inp = 1.0
        self.gain_out = 1.0
        self.gain_increment = 0.2
        self.vec_zoom = 0.1
        self.loop = False
        self.stabilizer = False
        
        # presets for text in OSD
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.blue = (255, 0, 0)
        self.black = (0, 0, 0)
        self.osd_inp = 'Input:'
        self.osd_out = 'Output:'
        self.osd_col = 'Color: '
        self.osd_mode = 'Proc: '
        self.osd_recording = ''
        self.osd_txtsize = 1.5
        self.osd_txtline = 2
        self.colormaps = [
                'AUTUMN', 'BONE', 'JET', 'WINTER',
                'RAINBOW', 'OCEAN', 'SUMMER', 'SPRING',
                'COOL', 'HSV', 'PINK', 'HOT'
                ]
        
        # help text array
        self.helptxt = [
                'KEYBOARD SHORTCUTS',
                'lower/UPPER case = apply to input/OUTPUT processing chain.',
                'a/A  Auto adjust offset and gain',
                'b/B  Blur',
                'c    Cycle Color Palette',
                'd    Toggle Dark Frame mode (Rolling Average / Fixed)',
                'e/E  Cycle Equalizer modes (OFF, HIST, CLAHE)',
                'f/F  Cycle Filters defined in filters.py',
                'h    Show this help text',
                'i    Toggle image stabilizer',
                'l    Toggle input video loop mode',
                'm    Cycle Input Mode (BOTH, STATUS, IMAGE)',
                'M    Cycle Output Mode (IMAGE, VECTOR, BOTH)',
                'n/N  Denoise',
                'p    Cycle Processing Mode (OFF, AVG, DIFF, CUMSUM)',
                'q    Terminate Program',
                'r    Reset Cumulative Summing',
                'R    Reset Gains and Offsets',
                's    ',
                'S    ',
                'v    Toggle video recording',
                'V    Toggle image sequence recording',
                '?    Cycle Schlieren pattern types',
                '>    Increase Schlieren pattern size',
                '<    Decrease Schlieren pattern size',
                'x    Flip image around X axis',
                'y    Flip image around Y axis',
                '[/]  Decrease / Increase Input Gain',
                '{/}  Decrease / Increase Output Gain',
                '-/+  Decrease / Increase Input Filter Strength',
                '_/=  Decrease / Increase Output Filter Strength',
                'SPACE create Screenshot',
                '1-9  Set No. of frames in Stack',
                ]

    def write_config(self, filename):
        if filename is None:
            filename = self.cfgfilename
        self.cfgfile = open(filename,'w')
        #self.Config.add_section('Input')
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
        self.Config.set('Input','mode_in', self.mode_in)
        self.Config.set('Input','gain_inp', self.gain_inp)
        #self.Config.add_section('Processor')
        self.Config.set('Processor','mode_prc', self.mode_prc)
        self.Config.set('Processor','dyn_dark', self.dyn_dark)
        self.Config.set('Processor','blr_strength', self.blr_strength)
        self.Config.set('Processor','numframes', self.numframes)
        #self.Config.add_section('Output')
        self.Config.set('Output','video_dst', self.video_dst)
        self.Config.set('Output','image_dst', self.image_dst)
        self.Config.set('Output','recordv', self.recordv)
        self.Config.set('Output','recordi', self.recordi)
        self.Config.set('Output','blr_out', self.blr_inp)
        self.Config.set('Output','equ_out', self.equ_inp)
        self.Config.set('Output','dnz_out', self.dnz_inp)
        self.Config.set('Output','dnz_out_str', self.dnz_inp_str)
        self.Config.set('Output','flt_out', self.flt_inp)
        self.Config.set('Output','flt_out_strength', self.flt_inp_strength)
        self.Config.set('Output','mode_out', self.mode_in)
        self.Config.set('Output','gain_out', self.gain_inp)
        self.Config.set('Output','color_mode', self.color_mode)
        self.Config.set('Output','pseudoc', self.pseudoc)
        self.Config.set('Output','vec_zoom', self.vec_zoom)
        #self.Config.add_section('Display')
        self.Config.set('Display','window_x', self.window_x)
        self.Config.set('Display','window_y', self.window_y)
        self.Config.set('Display','window_width', self.window_width)
        self.Config.set('Display','window_height', self.window_height)
        self.Config.set('Display','window_space', self.window_space)
        #self.Config.add_section('Pattern_Generator')
        self.Config.set('Pattern_Generator','screen_width', self.screen_width)
        self.Config.set('Pattern_Generator','screen_height', self.screen_height)
        self.Config.set('Pattern_Generator','pattern_mode', self.pattern_mode)
        self.Config.set('Pattern_Generator','pattern_size', self.pattern_size)
        self.Config.set('Pattern_Generator','backgnd', self.backgnd)
        #self.Config.add_section('Misc')
        self.Config.set('Misc','flt_strength_increment', self.flt_strength_increment)
        self.Config.set('Misc','gain_increment', self.gain_increment)
        self.Config.write(self.cfgfile)
        self.cfgfile.close()
        
    def read_config(self, filename):
        self.Config.read(filename)
        self.video_src = self.Config.get('Input','video_src')
        self.video_width = self.Config.get('Input','video_width')
        self.video_height = self.Config.get('Input','video_height')
        self.loop = self.Config.get('Input','loop')
        self.flip_x = self.Config.get('Input','flip_x')
        self.flip_y = self.Config.get('Input','flip_y')
        self.blr_inp = self.Config.get('Input','blr_inp')
        self.equ_inp = self.Config.get('Input','equ_inp')
        self.dnz_inp = self.Config.get('Input','dnz_inp')
        self.dnz_inp_str = self.Config.get('Input','dnz_inp_str')
        self.flt_inp = self.Config.get('Input','flt_inp')
        self.flt_inp_strength = self.Config.get('Input','flt_inp_strength')
        self.mode_in = self.Config.get('Input','mode_in')
        self.gain_inp = self.Config.get('Input','gain_inp')
        self.mode_prc = self.Config.get('Processor','mode_prc')
        self.dyn_dark = self.Config.get('Processor','dyn_dark')
        self.blr_strength = self.Config.get('Processor','blr_strength')
        self.numframes = self.Config.get('Processor','numframes')
        self.video_dst = self.Config.get('Output','video_dst')
        self.image_dst = self.Config.get('Output','image_dst')
        self.recordv = self.Config.get('Output','recordv')
        self.recordi = self.Config.get('Output','recordi')
        self.blr_out = self.Config.get('Output','blr_out')
        self.equ_out = self.Config.get('Output','equ_out')
        self.dnz_out = self.Config.get('Output','dnz_out')
        self.dnz_out_str = self.Config.get('Output','dnz_out_str')
        self.flt_out = self.Config.get('Output','flt_out')
        self.flt_out_strength = self.Config.get('Output','flt_out_strength')
        self.mode_out = self.Config.get('Output','mode_out')
        self.gain_out = self.Config.get('Output','gain_out')
        self.color_mode = self.Config.get('Output','color_mode')
        self.pseudoc = self.Config.get('Output','pseudoc')
        self.vec_zoom = self.Config.get('Output','vec_zoom')
        self.window_x = self.Config.get('Display','window_x')
        self.window_y = self.Config.get('Display','window_y')
        self.window_width = self.Config.get('Display','window_width')
        self.window_height = self.Config.get('Display','window_height')
        self.window_space = self.Config.get('Display','window_space')
        self.screen_width = self.Config.get('Pattern_Generator','screen_width')
        self.screen_height = self.Config.get('Pattern_Generator','screen_height')
        self.pattern_mode = self.Config.get('Pattern_Generator','pattern_mode')
        self.pattern_size = self.Config.get('Pattern_Generator','pattern_size')
        self.backgnd = self.Config.get('Pattern_Generator','backgnd')
        self.flt_strength_increment = self.Config.get('Misc','flt_strength_increment')
        self.gain_increment = self.Config.get('Misc','gain_increment')