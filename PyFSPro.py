#!/usr/bin/env python
from __future__ import division, print_function
import sys
import time
import argparse

import numpy as np
import cv2
import cv2.cv as cv

from threading import Thread, Event

# kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.animation import Animation

# local imports
import config

# choose between generic and Raspberry Pi camera support
import videosource as vs
#import videosource_pi as vs

import framestacker as fs
import filters as flt

# scikit-video (scikit-video.org) is used for recording because of OpenCV
# Linux bug
try:
    from skvideo.io import FFmpegWriter as VideoWriter
    skvdetected = True
except:
    skvdetected = False


class MyScreen(BoxLayout):
    iimage_wid = ObjectProperty()
    oimage_wid = ObjectProperty()
    select_wid = ObjectProperty()
    osd_wid = ObjectProperty()
    vec_wid = ObjectProperty()
    ipan_wid = ObjectProperty()
    opan_wid = ObjectProperty()
    mid_wid = ObjectProperty()
    inp_wid = ObjectProperty()
    out_wid = ObjectProperty()
    inpb_wid = ObjectProperty()
    outb_wid = ObjectProperty()
    bpan_wid = ObjectProperty()
    tpan_wid = ObjectProperty()
    iauto_wid = ObjectProperty()
    igain_wid = ObjectProperty()
    ioffset_wid = ObjectProperty()
    oauto_wid = ObjectProperty()
    ogain_wid = ObjectProperty()
    ooffset_wid = ObjectProperty()
    iblur_wid = ObjectProperty()
    idnz_wid = ObjectProperty()
    oblur_wid = ObjectProperty()
    odnz_wid = ObjectProperty()
    istab_wid = ObjectProperty()
    ostab_wid = ObjectProperty()
    iequ_wid = ObjectProperty()
    oequ_wid = ObjectProperty()
    iflt_wid = ObjectProperty()
    oflt_wid = ObjectProperty()
    proc_wid = ObjectProperty()
    dark_wid = ObjectProperty()
    stack_wid = ObjectProperty()
    reset_wid = ObjectProperty()
    stackdisplay_wid = ObjectProperty()
    play_wid = ObjectProperty()
    loop_wid = ObjectProperty()
    screenshot_wid = ObjectProperty()
    video_wid = ObjectProperty()
    imagesequence_wid = ObjectProperty()
    help_wid = ObjectProperty()
    helpbox_wid = ObjectProperty()
    colors_wid = ObjectProperty()
    flipx_wid = ObjectProperty()
    flipy_wid = ObjectProperty()
    ichan_wid = ObjectProperty()

class PyFSProApp(App):

    def on_stop(self):
        # signal all threads to stop
        self.cnf.proc_thread_run = False
        self.cnf.procthread.join()

    def apply_settings(self):
        self.cnf.imagestack.blr_inp = self.cnf.blr_inp
        self.cnf.imagestack.blr_out = self.cnf.blr_out
        self.cnf.imagestack.flip_x = self.cnf.flip_x
        self.cnf.imagestack.flip_y = self.cnf.flip_y
        self.cnf.imagestack.gain_inp = self.cnf.gain_inp
        self.cnf.imagestack.gain_out = self.cnf.gain_out
        self.cnf.imagestack.offset_inp = self.cnf.offset_inp
        self.cnf.imagestack.offset_out = self.cnf.offset_out
        self.cnf.imagestack.setKernel(self.cnf.blr_strength)
        self.cnf.imagestack.dyn_dark = self.cnf.dyn_dark
        self.cnf.flt_inp_kernel = self.cnf.inp_kernel * self.cnf.flt_inp_strength
        self.cnf.flt_out_kernel = self.cnf.out_kernel * self.cnf.flt_out_strength
        self.imageinput.loop = self.cnf.loop
        if (self.cnf.imagestack.stackrange != self.cnf.numframes):
            self.cnf.imagestack.initStack(self.cnf.numframes)

    def update_controls(self, values):
        if values.input_denoise:
            self.cnf.rootwidget.idnz_wid.state = 'down'
        if values.output_denoise:
            self.cnf.rootwidget.odnz_wid.state = 'down'
        if values.input_equalize != self.cnf.rootwidget.iequ_wid.text:
            self.cnf.rootwidget.iequ_wid.text = values.input_equalize
        if values.output_equalize != self.cnf.rootwidget.oequ_wid.text:
            self.cnf.rootwidget.oequ_wid.text = values.output_equalize
        if values.processing_mode != self.cnf.rootwidget.proc_wid.text:
            self.cnf.rootwidget.proc_wid.text = values.processing_mode
        if float(values.input_gain) != float(self.cnf.rootwidget.igain_wid.value):
            self.cnf.rootwidget.igain_wid.value = float(values.input_gain)
        if float(values.output_gain) != float(self.cnf.rootwidget.ogain_wid.value):
            self.cnf.rootwidget.ogain_wid.value = float(values.output_gain)
        if values.input_blur:
            self.cnf.rootwidget.iblur_wid.state = 'down'
        if values.output_blur:
            self.cnf.rootwidget.oblur_wid.state = 'down'
        if values.input_filter != self.cnf.rootwidget.iflt_wid.text:
            self.cnf.rootwidget.iflt_wid.text = values.input_filter
        if values.output_filter != self.cnf.rootwidget.oflt_wid.text:
            self.cnf.rootwidget.oflt_wid.text = values.output_filter
        if values.loop_input:
            self.cnf.rootwidget.loop_wid.state = 'down'
        if values.input_stabilizer:
            self.cnf.rootwidget.istab_wid.state = 'down'
        if values.output_stabilizer:
            self.cnf.rootwidget.ostab_wid.state = 'down'
        if values.flip_x:
            self.cnf.rootwidget.flipx_wid.state = 'down'
        if values.flip_y:
            self.cnf.rootwidget.flipy_wid.state = 'down'
        if int(values.stack_size) != int(self.cnf.rootwidget.stack_wid.value):
            self.cnf.rootwidget.stack_wid.value = int(values.stack_size)
        if values.color_mode != self.cnf.rootwidget.colors_wid.text:
            self.cnf.rootwidget.colors_wid.text = values.color_mode
        if values.output_video != 'none' and skvdetected:
            self.cnf.video_dst = values.output_video
            self.cnf.rootwidget.video_wid.state = 'down'
        if values.output_images != 'none':
            self.cnf.image_dst = values.output_images
            self.cnf.rootwidget.imagesequence_wid.state = 'down'
        if values.input_channel != self.cnf.rootwidget.ichan_wid.text:
            self.cnf.rootwidget.ichan_wid.text = values.input_channel

    def osd_callback(self, instance, value):
        if value == 'normal':
            # Hide the control panels by moving them out of the window
            self.ibar_out.start(self.cnf.rootwidget.ipan_wid)
            self.obar_out.start(self.cnf.rootwidget.opan_wid)
            self.outb_large.start(self.cnf.rootwidget.outb_wid)
            self.inpb_large.start(self.cnf.rootwidget.inpb_wid)
            self.bpan_out.start(self.cnf.rootwidget.bpan_wid)
            self.tpan_out.start(self.cnf.rootwidget.tpan_wid)
            self.cnf.rootwidget.helpbox_wid.size_hint_y = 1
        else:
            # Get the control panels back in place
            self.ibar_in.start(self.cnf.rootwidget.ipan_wid)
            self.obar_in.start(self.cnf.rootwidget.opan_wid)
            self.outb_small.start(self.cnf.rootwidget.outb_wid)
            self.inpb_small.start(self.cnf.rootwidget.inpb_wid)
            self.bpan_in.start(self.cnf.rootwidget.bpan_wid)
            self.tpan_in.start(self.cnf.rootwidget.tpan_wid)
            self.cnf.rootwidget.helpbox_wid.size_hint_y = 0.9

    def vec_callback(self, instance, value):
        if value == 'normal':
            self.cnf.show_vec = False
        else:
            self.cnf.show_vec = True

    def inp_callback(self, instance, value):
        if value == 'normal':
            self.cnf.show_inp = False
            self.showiimage = self.background
            self.cnf.rootwidget.iimage_wid.texture = self.img2tex(
                self.background)
            self.cnf.rootwidget.iimage_wid.pos_hint = {'top': 3}
        else:
            self.cnf.show_inp = True
            self.cnf.rootwidget.iimage_wid.pos_hint = {'top': 1}

    def istab_callback(self, instance, value):
        if value == 'down':
            self.cnf.stb_inp = True
        else:
            self.cnf.stb_inp = False

    def iauto_callback(self, instance):
        gain, offset = self.cnf.imagestack.autoInpGain()
        self.cnf.rootwidget.igain_wid.value = float(gain)
        self.cnf.rootwidget.ioffset_wid.value = float(offset)

    def igain_callback(self, instance, value):
        self.cnf.gain_inp = value
        self.apply_settings()

    def ioffset_callback(self, instance, value):
        self.cnf.offset_inp = value
        self.apply_settings()

    def iblur_callback(self, instance, value):
        if value == 'down':
            self.cnf.blr_inp = True
        else:
            self.cnf.blr_inp = False
        self.apply_settings()

    def idnz_callback(self, instance, value):
        if value == 'down':
            self.cnf.dnz_inp = True
        else:
            self.cnf.dnz_inp = False

    def iequ_callback(self, instance, value):
        if value == 'HIST':
            self.cnf.equ_inp = 1
        elif value == 'CLAHE':
            self.cnf.equ_inp = 2
        else:
            self.cnf.equ_inp = 0

    def iflt_callback(self, instance, value):
        self.cnf.flt_inp = 0
        for k in range(1, self.cnf.numkernels):
            if self.cnf.kernels.get_kernel(k)[0] == value:
                self.cnf.flt_inp = k
                self.cnf.flt_inp_name, self.cnf.inp_kernel, self.cnf.flt_inp_strength = self.cnf.kernels.get_kernel(
                    self.cnf.flt_inp)
                self.apply_settings()

    def out_callback(self, instance, value):
        if value == 'normal':
            self.cnf.show_out = False
            self.showoimage = self.background
        else:
            self.cnf.show_out = True

    def ostab_callback(self, instance, value):
        if value == 'down':
            self.cnf.stb_out = True
        else:
            self.cnf.stb_out = False

    def oauto_callback(self, instance):
        gain, offset = self.cnf.imagestack.autoOutGain()
        self.cnf.rootwidget.ogain_wid.value = float(gain)
        self.cnf.rootwidget.ooffset_wid.value = float(offset)

    def ogain_callback(self, instance, value):
        self.cnf.gain_out = value
        self.apply_settings()

    def ooffset_callback(self, instance, value):
        self.cnf.offset_out = value
        self.apply_settings()

    def oblur_callback(self, instance, value):
        if value == 'down':
            self.cnf.blr_out = True
        else:
            self.cnf.blr_out = False
        self.apply_settings()

    def odnz_callback(self, instance, value):
        if value == 'down':
            self.cnf.dnz_out = True
        else:
            self.cnf.dnz_out = False

    def oequ_callback(self, instance, value):
        if value == 'HIST':
            self.cnf.equ_out = 1
        elif value == 'CLAHE':
            self.cnf.equ_out = 2
        else:
            self.cnf.equ_out = 0

    def oflt_callback(self, instance, value):
        self.cnf.flt_out = 0
        for k in range(1, self.cnf.numkernels):
            if self.cnf.kernels.get_kernel(k)[0] == value:
                self.cnf.flt_out = k
                self.cnf.flt_out_name, self.cnf.out_kernel, self.cnf.flt_out_strength = self.cnf.kernels.get_kernel(
                    self.cnf.flt_out)
                self.apply_settings()

    def stack_callback(self, instance, value):
        self.cnf.numframes = int(value)
        self.apply_settings()

    def proc_callback(self, instance, value):
        if value == 'AVG':
            self.cnf.mode_prc = 1
        elif value == 'DIFF':
            self.cnf.mode_prc = 2
        elif value == 'CUMSUM':
            self.cnf.mode_prc = 3
        else:
            self.cnf.mode_prc = 0
        self.apply_settings()

    def dark_callback(self, instance, value):
        if value == 'down':
            self.cnf.dyn_dark = True
        else:
            self.cnf.dyn_dark = False
        self.apply_settings()

    def reset_callback(self, instance):
        if self.cnf.mode_prc == 3:
            self.cnf.imagestack.resetCUMSUM()
        else:
            self.cnf.rootwidget.igain_wid.value = 1
            self.cnf.rootwidget.ogain_wid.value = 1
            self.cnf.rootwidget.ioffset_wid.value = 0
            self.cnf.rootwidget.ooffset_wid.value = 0

    def screenshot_callback(self, instance):
        self.cnf.filename = self.cnf.output_path + \
            'Screenshot-' + self.cnf.gettime() + '.bmp'
        cv2.imwrite(self.cnf.filename, self.cnf.out)

    def play_callback(self, instance, value):
        if value == 'down':
            self.cnf.proc_frames = True
        else:
            self.cnf.proc_frames = False

    def loop_callback(self, instance, value):
        if value == 'down':
            self.cnf.loop = True
        else:
            self.cnf.loop = False
        self.imageinput.loop = self.cnf.loop

    def video_callback(self, instance, value):
        if value == 'down':
            self.cnf.video = VideoWriter(
                self.cnf.video_dst + self.cnf.gettime() + '.avi')
            self.cnf.recordv = True
        else:
            self.cnf.recordv = False

    def imagesequence_callback(self, instance, value):
        if value == 'down':
            self.cnf.recordi = True
        else:
            self.cnf.recordi = False

    def help_callback(self, instance, value):
        if value == 'down':
            self.help_in.start(self.cnf.rootwidget.helpbox_wid)
        else:
            self.help_out.start(self.cnf.rootwidget.helpbox_wid)

    def colors_callback(self, instance):
        self.cnf.color_mode += 1
        if self.cnf.color_mode > 11:
            self.cnf.pseudoc = False
            self.cnf.color_mode = -1
            self.cnf.rootwidget.colors_wid.text = 'GREY'
        else:
            self.cnf.pseudoc = True
            self.cnf.rootwidget.colors_wid.text = self.cnf.colormaps[self.cnf.color_mode]

    def flipx_callback(self, instance, value):
        if value == 'down':
            self.cnf.flip_x = True
        else:
            self.cnf.flip_x = False
        self.apply_settings()

    def flipy_callback(self, instance, value):
        if value == 'down':
            self.cnf.flip_y = True
        else:
            self.cnf.flip_y = False
        self.apply_settings()

    def ichan_callback(self, instance, value):
        if value == 'R':
            self.cnf.input_channel = 1
        elif value == 'G':
            self.cnf.input_channel = 2
        elif value == 'B':
            self.cnf.input_channel = 3
        elif value == 'H':
            self.cnf.input_channel = 4
        elif value == 'S':
            self.cnf.input_channel = 5
        elif value == 'V':
            self.cnf.input_channel = 6
        elif value == 'Y':
            self.cnf.input_channel = 7
        elif value == 'Cr':
            self.cnf.input_channel = 8
        elif value == 'Cb':
            self.cnf.input_channel = 9
        else:
            self.cnf.input_channel = 0


    def img2tex(self, img):
        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        tex = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        tex.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return tex

    def build(self):
        self.cnf = config.Settings()

        # load filter kernels
        self.cnf.kernels = flt.Kernels()
        self.cnf.numkernels = self.cnf.kernels.get_numkernels()
        self.cnf.flt_inp_name, self.cnf.inp_kernel, self.cnf.flt_inp_strength = self.cnf.kernels.get_kernel(
            self.cnf.flt_inp)
        self.cnf.flt_out_name, self.cnf.out_kernel, self.cnf.flt_out_strength = self.cnf.kernels.get_kernel(
            self.cnf.flt_out)

        # Kivy stuff
        # define widget animations
        self.ibar_in = Animation(pos_hint={'right': 0.1})
        self.ibar_out = Animation(pos_hint={'right': 0})
        self.obar_in = Animation(pos_hint={'right': 1})
        self.obar_out = Animation(pos_hint={'right': 1.1})
        self.outb_large = Animation(pos_hint={'x': 0, 'top': 1}, size_hint_x=1)
        self.outb_small = Animation(
            pos_hint={'x': 0.1, 'top': 1}, size_hint_x=0.8)
        self.inpb_large = Animation(pos_hint={'x': 0, 'top': 1})
        self.inpb_small = Animation(pos_hint={'x': 0.1, 'top': 1})
        self.bpan_in = Animation(pos_hint={'top': 0.1})
        self.bpan_out = Animation(pos_hint={'top': 0})
        self.tpan_in = Animation(pos_hint={'top': 1})
        self.tpan_out = Animation(pos_hint={'top': 1.1})
        self.help_out = Animation(pos_hint={'top': 2.2})
        self.help_in = Animation(pos_hint={'top': 1})

        # create Kivy UI
        self.cnf.rootwidget = MyScreen()
        self.namelist = ['FLT-OFF']
        for k in range(1, self.cnf.numkernels):
            self.namelist.append(self.cnf.kernels.get_kernel(k)[0])
        self.cnf.rootwidget.iflt_wid.values = self.namelist
        self.cnf.rootwidget.oflt_wid.values = self.namelist
        self.cnf.rootwidget.osd_wid.bind(state=self.osd_callback)
        self.cnf.rootwidget.vec_wid.bind(state=self.vec_callback)
        self.cnf.rootwidget.inp_wid.bind(state=self.inp_callback)
        self.cnf.rootwidget.out_wid.bind(state=self.out_callback)
        self.cnf.rootwidget.iauto_wid.bind(on_release=self.iauto_callback)
        self.cnf.rootwidget.igain_wid.bind(value=self.igain_callback)
        self.cnf.rootwidget.ioffset_wid.bind(value=self.ioffset_callback)
        self.cnf.rootwidget.oauto_wid.bind(on_release=self.oauto_callback)
        self.cnf.rootwidget.ogain_wid.bind(value=self.ogain_callback)
        self.cnf.rootwidget.ooffset_wid.bind(value=self.ooffset_callback)
        self.cnf.rootwidget.iblur_wid.bind(state=self.iblur_callback)
        self.cnf.rootwidget.idnz_wid.bind(state=self.idnz_callback)
        self.cnf.rootwidget.oblur_wid.bind(state=self.oblur_callback)
        self.cnf.rootwidget.odnz_wid.bind(state=self.odnz_callback)
        self.cnf.rootwidget.istab_wid.bind(state=self.istab_callback)
        self.cnf.rootwidget.ostab_wid.bind(state=self.ostab_callback)
        self.cnf.rootwidget.iequ_wid.bind(text=self.iequ_callback)
        self.cnf.rootwidget.oequ_wid.bind(text=self.oequ_callback)
        self.cnf.rootwidget.iflt_wid.bind(text=self.iflt_callback)
        self.cnf.rootwidget.oflt_wid.bind(text=self.oflt_callback)
        self.cnf.rootwidget.stack_wid.bind(value=self.stack_callback)
        self.cnf.rootwidget.proc_wid.bind(text=self.proc_callback)
        self.cnf.rootwidget.dark_wid.bind(state=self.dark_callback)
        self.cnf.rootwidget.reset_wid.bind(on_release=self.reset_callback)
        self.cnf.rootwidget.play_wid.bind(state=self.play_callback)
        self.cnf.rootwidget.loop_wid.bind(state=self.loop_callback)
        self.cnf.rootwidget.ichan_wid.bind(text=self.ichan_callback)
        self.cnf.rootwidget.screenshot_wid.bind(
            on_release=self.screenshot_callback)
        if skvdetected:
            self.cnf.rootwidget.video_wid.bind(state=self.video_callback)
        else:
            self.cnf.rootwidget.video_wid.disabled = True
        self.cnf.rootwidget.imagesequence_wid.bind(
            state=self.imagesequence_callback)
        self.cnf.rootwidget.help_wid.bind(state=self.help_callback)
        self.cnf.rootwidget.colors_wid.bind(on_release=self.colors_callback)
        self.cnf.rootwidget.flipx_wid.bind(state=self.flipx_callback)
        self.cnf.rootwidget.flipy_wid.bind(state=self.flipy_callback)

        # command line parser
        parser = argparse.ArgumentParser(
            description='Python Frame Sequence Processor', add_help=True)
        parser.add_argument('-c', '--config_file', default='none',
                            help='Load Configuration from file')
        parser.add_argument('-ic', '--input_channel', default=self.cnf.rootwidget.ichan_wid.text,
                            help='Input Channel: BW, R, G, B, H, S, V, Y, Cr, Cb')
        parser.add_argument('-is', '--input_source', default=self.cnf.video_src,
                            help='Input Source, filename or camera index')
        parser.add_argument('-iw', '--input_width', default=self.cnf.video_width,
                            help='Width of captured frames')
        parser.add_argument('-ih', '--input_height', default=self.cnf.video_height,
                            help='Height of captured frames')
        parser.add_argument('-ib', '--input_blur', action='store_true',
                            help='Blur Input')
        parser.add_argument('-ie', '--input_equalize', default=self.cnf.rootwidget.iequ_wid.text,
                            help='Input Equalization Mode')
        parser.add_argument('-if', '--input_filter', default=self.cnf.rootwidget.iflt_wid.text,
                            help='Set Input Filter')
        parser.add_argument('-ifs', '--input_filter_strength', default='none',
                            help='Set Input Filter Strength')
        parser.add_argument('-ig', '--input_gain', default=self.cnf.rootwidget.igain_wid.value,
                            help='Input Gain')
        parser.add_argument('-il', '--loop_input', action='store_true',
                            help='Loop input video')
        parser.add_argument('-in', '--input_denoise', action='store_true',
                            help='Input Denoise')
        parser.add_argument('-ii', '--input_stabilizer', action='store_true',
                            help='Enable input image stabilizer')
        parser.add_argument('-bs', '--blur_strength', default=self.cnf.blr_strength,
                            help='Blur Strength (Kernel Size')
        parser.add_argument('-fx', '--flip_x', action='store_true',
                            help='Flip around X axis')
        parser.add_argument('-fy', '--flip_y', action='store_true',
                            help='Flip around Y axis')
        parser.add_argument('-ob', '--output_blur', action='store_true',
                            help='Blur Output')
        parser.add_argument('-oc', '--color_mode', default=self.cnf.rootwidget.colors_wid.text,
                            help='Output Color Mode')
        parser.add_argument('-oe', '--output_equalize', default=self.cnf.rootwidget.oequ_wid.text,
                            help='Output Equalization Mode')
        parser.add_argument('-of', '--output_filter', default=self.cnf.rootwidget.oflt_wid.text,
                            help='Set Output Filter')
        parser.add_argument('-ofs', '--output_filter_strength', default='none',
                            help='Set Output Filter Strength')
        parser.add_argument('-og', '--output_gain',
                            default=self.cnf.rootwidget.ogain_wid.value, help='Output Gain')
        parser.add_argument('-oi', '--output_stabilizer', action='store_true',
                            help='Enable output image stabilizer')
        parser.add_argument('-on', '--output_denoise',  action='store_true',
                            help='Output Denoise')
        parser.add_argument('-ov', '--output_video', default='none',
                            help='Save output as video (Path or Prefix).')
        parser.add_argument('-os', '--output_images', default='none',
                            help='Save output as image sequence (Path or Prefix).')
        parser.add_argument('-pm', '--processing_mode', default=self.cnf.rootwidget.proc_wid.text,
                            help='Set Processing Mode: AVG, DIFF, CUMSUM')
        parser.add_argument('-pz', '--stack_size', default=self.cnf.rootwidget.stack_wid.value,
                            help='Image Stacking (No. of frames to stack)')

        self.args = parser.parse_args(sys.argv[2:])
        if str(self.args.input_source).isdigit():
            self.cnf.video_src = int(self.args.input_source)
        else:
            self.cnf.video_src = self.args.input_source

        # initialize video input
        self.cnf.video_width = self.args.input_width
        self.cnf.video_height = self.args.input_height
        self.imageinput = vs.FrameInput(
            self.cnf.video_src, self.cnf.video_width, self.cnf.video_height)
        self.imageinput.loop = self.cnf.loop
        self.cnf.video_width = self.imageinput.frame_width
        self.cnf.video_height = self.imageinput.frame_height

        # prepare stack
        self.cnf.imagestack = fs.FrameStack(
            self.cnf.numframes, self.cnf.video_width, self.cnf.video_height)

        # apply loaded settings to stack
        self.apply_settings()
        # load command line arguments and update UI and settings
        self.update_controls(self.args)

        # create a CLAHE object (Contrast Limited Adaptive Histogram
        # Equalization)
        self.clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))

        # prepare on screen vector display
        self.center_x = int(self.cnf.video_width / 2)
        self.center_y = int(self.cnf.video_height / 2)
        self.center = (self.center_x, self.center_y)
        self.vec_zoom_2 = self.cnf.vec_zoom / 2
        self.background = np.full((self.cnf.video_height, self.cnf.video_width, 3),
                                  self.cnf.imagestack.default_value, np.uint8)

        # prepare image stabilizer
        self.inp = self.imageinput.grab_frame()
        self.inp = cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY)
        self.inp_old = self.inp.copy()
        self.inp_raw = self.inp.copy()
        self.dsp_old = self.inp.copy()
        self.dsp_raw = self.inp.copy()

        Clock.schedule_interval(self.update_output, self.cnf.output_fps)
        self.cnf.procthread = Thread(target=self.process_thread)
        self.cnf.procthread.start()
        return self.cnf.rootwidget

    def update_output(self, dt):
        #self.process_frame()
        self.cnf.rootwidget.oimage_wid.texture = self.img2tex(self.showoimage)
        if self.cnf.show_inp == True:
            self.showiimage = cv2.cvtColor(np.uint8(self.cnf.imagestack.inp_frame),
                                           cv2.COLOR_GRAY2BGR)
            self.cnf.rootwidget.iimage_wid.texture = self.img2tex(
                self.showiimage)
        if self.cnf.stack_status:
            self.cnf.rootwidget.stackdisplay_wid.color = (1, 0, 0, 1)
        else:
            self.cnf.rootwidget.stackdisplay_wid.color = (0, 1, 0, 1)

    def process_thread(self):
        while self.cnf.proc_thread_run:
            if self.cnf.proc_frames:
                self.process_frame()
            time.sleep(self.cnf.proc_fps)

    # main video processing function
    def process_frame(self):
        self.inp = self.imageinput.grab_frame()
        if self.cnf.input_channel == 0:
            self.inp = cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY)
        elif self.cnf.input_channel == 1:
            b,g,self.inp = cv2.split(self.inp)
        elif self.cnf.input_channel == 2:
            b,self.inp,r = cv2.split(self.inp)
        elif self.cnf.input_channel == 3:
            self.inp,g,r = cv2.split(self.inp)
        elif self.cnf.input_channel == 4:
            self.inp,s,v = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
        elif self.cnf.input_channel == 5:
            h,self.inp,v = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
        elif self.cnf.input_channel == 6:
            h,s,self.inp = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
        elif self.cnf.input_channel == 7:
            self.inp,cr,cb = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
        elif self.cnf.input_channel == 8:
            y,self.inp,cb = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
        elif self.cnf.input_channel == 9:
            y,cr,self.inp = cv2.split(cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
        if self.cnf.dnz_inp:
            cv2.fastNlMeansDenoising(
                self.inp, self.inp, self.cnf.dnz_inp_str, 7, 21)
        if self.cnf.equ_inp == 1:
            self.inp = cv2.equalizeHist(self.inp)
        elif self.cnf.equ_inp == 2:
            self.inp = self.clahe.apply(self.inp)
        elif self.cnf.flt_inp != 0:
            self.inp = cv2.filter2D(self.inp, -1, self.cnf.flt_inp_kernel)
        if self.cnf.stb_inp:
            self.transform = cv2.estimateRigidTransform(
                self.inp_old, self.inp, False)
            if self.transform is not None:
                self.inp = cv2.warpAffine(self.inp, self.transform, (self.cnf.video_width, self.cnf.video_height),
                                          self.inp_raw, cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, cv2.BORDER_TRANSPARENT)
        self.inp_old = self.inp
        self.cnf.stack_status = self.cnf.imagestack.addFrame(self.inp)
        if self.cnf.mode_prc == 0:
            self.dsp = self.cnf.imagestack.getINP()
        elif self.cnf.mode_prc == 1:
            self.dsp = self.cnf.imagestack.getAVG()
        elif self.cnf.mode_prc == 2:
            self.dsp = self.cnf.imagestack.getDIFF()
        elif self.cnf.mode_prc == 3:
            self.dsp = self.cnf.imagestack.getCUMSUM()
        if self.cnf.stb_out:
            self.transform = cv2.estimateRigidTransform(
                self.dsp_old, self.dsp, False)
            if self.transform is not None:
                self.dsp = cv2.warpAffine(self.dsp, self.transform, (self.cnf.video_width, self.cnf.video_height),
                                          self.dsp_raw, cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, cv2.BORDER_TRANSPARENT)
        self.dsp_old = self.dsp
        if self.cnf.equ_out == 1:
            self.dsp = cv2.equalizeHist(self.dsp)
        elif self.cnf.equ_out == 2:
            self.dsp = self.clahe.apply(self.dsp)
        if self.cnf.dnz_out:
            cv2.fastNlMeansDenoising(
                self.dsp, self.dsp, self.cnf.dnz_out_str, 7, 21)
        elif self.cnf.flt_out != 0:
            self.dsp = cv2.filter2D(self.dsp, -1, self.cnf.flt_out_kernel)

        # create output image
        if self.cnf.pseudoc:
            self.cnf.out = cv2.applyColorMap(self.dsp, self.cnf.color_mode)
        else:
            self.cnf.out = cv2.cvtColor(self.dsp, cv2.COLOR_GRAY2BGR)
        if self.cnf.show_out == True:
            self.showoimage = self.cnf.out
        if self.cnf.show_vec:
            if self.cnf.show_out == False:
                self.showoimage = self.background.copy()
            self.full_avg, self.x_avg, self.y_avg = self.cnf.imagestack.getVECTOR(
                self.cnf.vec_zoom)
            self.x_avg = int(self.x_avg)
            self.y_avg = int(self.y_avg)
            cv2.line(self.showoimage, self.center, (self.x_avg, self.y_avg), self.cnf.green,
                     thickness=self.cnf.osd_txtline, lineType=cv2.CV_AA)
            cv2.circle(self.showoimage, (self.x_avg, self.y_avg), 20, self.cnf.red,
                       thickness=self.cnf.osd_txtline, lineType=cv2.CV_AA)

        # record video or image sequence
        if self.cnf.recordv:
            self.cnf.video.writeFrame(self.cnf.out)
        if self.cnf.recordi:
            if self.cnf.imgindx == 0:
                self.cnf.image_dst += self.cnf.gettime()
            self.cnf.filename = self.cnf.image_dst + \
                str(self.cnf.imgindx).zfill(8) + '.bmp'
            cv2.imwrite(self.cnf.filename, self.cnf.out)
            self.cnf.imgindx += 1


if __name__ == '__main__':
    PyFSProApp().run()
