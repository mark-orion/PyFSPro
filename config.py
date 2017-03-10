#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:00:42 2017

@author: Mark Dammer
"""

# default values
numframes = 255  # No. of frames in stack
color_mode = -1  # Greyscale output
video_src = 0  # Default camera
video_width = 1024
video_height = 768
window_x = 100  # Position of first window on screen
window_y = 100
window_space = 50  # Space between windows
window_width = 800 # Default window size
window_height = 600

# default values for pattern generator
screen_width = 1920
screen_height = 1080
pattern_size = 0
pattern_mode = 2
backgnd = False

# settings for video and image sequence recording
recordi = False
recordv = False
novfile = True
imgindx = 0
output_path = './output/'
image_dst = output_path
video_dst = output_path

# switches for image filters and tools
blr_inp = False
blr_out = False
blr_strength = 7
equ_inp = 0
equ_out = 0
dnz_inp = False
dnz_out = False
dnz_inp_str = 33
dnz_out_str = 33
flt_inp = 0
flt_out = 0
flt_inp_strength = 0
flt_out_strength = 0
flt_strength_increment = 0.1
flip_x = False
flip_y = False
inp_kernel = None
out_kernel = None
mode_in = 0
mode_prc = 0
mode_out = 0
pseudoc = False
dyn_dark = True
gain_inp = 1.0
gain_out = 1.0
gain_increment = 0.2
vec_zoom = 0.1
loop = False
stabilizer = False

# presets for text in OSD
green = (0, 255, 0)
red = (0, 0, 255)
blue = (255, 0, 0)
black = (0, 0, 0)
osd_inp = 'Input:'
osd_out = 'Output:'
osd_col = 'Color: '
osd_mode = 'Proc: '
osd_recording = ''
osd_txtsize = 1.5
osd_txtline = 2
colormaps = [
        'AUTUMN', 'BONE', 'JET', 'WINTER',
        'RAINBOW', 'OCEAN', 'SUMMER', 'SPRING',
        'COOL', 'HSV', 'PINK', 'HOT'
        ]

# help text array
helptxt = [
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

