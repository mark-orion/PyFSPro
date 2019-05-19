#!/usr/bin/env python
from __future__ import division, print_function
import sys
import os
import time
import argparse
import signal
import gc

import numpy as np
import cv2

from threading import Thread, Event

# scikit-video (scikit-video.org) is used for recording because of OpenCV
# Linux bug
try:
    from skvideo.io import FFmpegWriter as VideoWriter

    skvdetected = True
except:
    skvdetected = False

# disable Kivy command line args and chatter on STDOUT
os.environ["KIVY_NO_ARGS"] = "1"
#os.environ["KIVY_NO_CONSOLELOG"] = "1"

# kivy imports
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
#from kivy.properties import NumericProperty
from kivy.animation import Animation

# local imports
import config

# choose between generic and Raspberry Pi camera support
import videosource as vs
# import videosource_pi as vs

import actuators as acts
import framestacker as fs
import filters as flt


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
    iequ_wid = ObjectProperty()
    oequ_wid = ObjectProperty()
    iflt_wid = ObjectProperty()
    oflt_wid = ObjectProperty()
    proc_wid = ObjectProperty()
    dark_wid = ObjectProperty()
    stack_wid = ObjectProperty()
    reset_wid = ObjectProperty()
    stackdisplay_wid = ObjectProperty()
    dout_wid = ObjectProperty()
    inifile_wid = ObjectProperty()
    actuator_wid = ObjectProperty()
    recorder_wid = ObjectProperty()
    override_wid = ObjectProperty()
    colors_wid = ObjectProperty()
    flipx_wid = ObjectProperty()
    flipy_wid = ObjectProperty()
    ichan_wid = ObjectProperty()
    indicator_wid = ObjectProperty()
    zindicator_wid = ObjectProperty()
    indzoom_wid = ObjectProperty()
    indzoomvalue_wid = ObjectProperty()
    indzoombox_wid = ObjectProperty()
    ihist_wid = ObjectProperty()
    ohist_wid = ObjectProperty()
    marker_wid = ObjectProperty()
    istab_wid = ObjectProperty()
    ostab_wid = ObjectProperty()
    trf_wid = ObjectProperty()
    playmode_wid = ObjectProperty()
    vectype_wid = ObjectProperty()


class PyFSPro(App):
    title = 'Python Frame Sequence Processor'

    def on_stop(self):
        self.cnf.proc_thread_run = False
        self.cnf.act.shutdown()
        if not self.cnf.single_thread:
            self.cnf.procthread.join()
        sys.exit(0)

    # signal handler for a clean and happy ending
    def signal_handler(self, signal, frame):
        self.on_stop()

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
        if self.cnf.dyn_dark == 3:
            self.cnf.imagestack.loadDark(np.full((self.cnf.video_height, self.cnf.video_width), self.cnf.imagestack.default_value, np.uint8))
        if self.cnf.dyn_dark == 4:
            self.cnf.imagestack.loadDark(np.full((self.cnf.video_height, self.cnf.video_width), 0, np.uint8))
        self.cnf.flt_inp_kernel = self.cnf.inp_kernel * self.cnf.flt_inp_strength
        self.cnf.flt_out_kernel = self.cnf.out_kernel * self.cnf.flt_out_strength
        self.imageinput.loop = self.cnf.loop
        if (self.cnf.imagestack.stackrange != self.cnf.numframes):
            self.cnf.imagestack.initStack(self.cnf.numframes)
        gc.collect()

    def osd_callback(self, instance, value):
        if value == 'normal':
            # Hide the control panels by moving them out of the window
            self.ibar_out.start(self.cnf.rootwidget.ipan_wid)
            self.obar_out.start(self.cnf.rootwidget.opan_wid)
            self.outb_large.start(self.cnf.rootwidget.outb_wid)
            self.inpb_large.start(self.cnf.rootwidget.inpb_wid)
            self.bpan_out.start(self.cnf.rootwidget.bpan_wid)
            self.tpan_out.start(self.cnf.rootwidget.tpan_wid)
        else:
            # Get the control panels back in place
            self.ibar_in.start(self.cnf.rootwidget.ipan_wid)
            self.obar_in.start(self.cnf.rootwidget.opan_wid)
            self.outb_small.start(self.cnf.rootwidget.outb_wid)
            self.inpb_small.start(self.cnf.rootwidget.inpb_wid)
            self.bpan_in.start(self.cnf.rootwidget.bpan_wid)
            self.tpan_in.start(self.cnf.rootwidget.tpan_wid)

    def vec_callback(self, instance, value):
        if value == 'normal':
            self.cnf.show_vec = False
            self.cnf.rootwidget.indicator_wid.pos_hint = {'top': 3}
        else:
            self.cnf.show_vec = True

    def inp_callback(self, instance, value):
        if value == 'normal':
            self.cnf.show_inp = False
            self.showiimage = self.cnf.background
            self.cnf.rootwidget.iimage_wid.texture = self.img2tex(
                self.cnf.background)
            self.cnf.rootwidget.iimage_wid.pos_hint = {'top': 3}
        else:
            self.cnf.show_inp = True
            self.cnf.rootwidget.iimage_wid.pos_hint = {'top': 0.9}

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

    def istab_callback(self, instance, value):
        if value == 'down':
            self.cnf.stb_inp = True
        else:
            self.cnf.stb_inp = False

    def out_callback(self, instance, value):
        if value == 'down':
            self.cnf.act.video_stop()
            self.cnf.show_out = True
        else:
            self.cnf.show_out = False
            self.cnf.act.video_play()

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

    def ostab_callback(self, instance, value):
        if value == 'down':
            self.cnf.stb_out = True
        else:
            self.cnf.stb_out = False

    def oimage_size_callback(self, instance, size):
        xsize, ysize = size
        self.cnf.out_xcenter = xsize / 2
        self.cnf.out_ycenter = ysize / 2
        self.cnf.out_xscale = xsize / 200
        self.cnf.out_yscale = ysize / 200

    def stack_callback(self, instance, value):
        self.cnf.numframes = int(value)
        self.apply_settings()

    def proc_callback(self, instance, value):
        if value == 'AVG':
            self.cnf.mode_prc = 1
        elif value == 'DIFF':
            self.cnf.mode_prc = 2
        elif value == 'CUM-Z':
            self.cnf.mode_prc = 3
        else:
            self.cnf.mode_prc = 0
        self.apply_settings()

    def dark_callback(self, instance, value):
        if value == 'DynDark':
            self.cnf.dyn_dark = 1
        elif value == 'Static':
            self.cnf.dyn_dark = 2
        elif value == 'Grey':
            self.cnf.dyn_dark = 3
        elif value == 'Dark-OFF':
            self.cnf.dyn_dark = 4
        else:
            self.cnf.rootwidget.dark_wid.text = 'Dark-OFF'
        self.apply_settings()

    def reset_callback(self, instance):
        if self.cnf.mode_prc == 3:
            self.cnf.imagestack.resetCUMSUM()
        else:
            self.cnf.rootwidget.igain_wid.value = 1
            self.cnf.rootwidget.ogain_wid.value = 1
            self.cnf.rootwidget.ioffset_wid.value = 0
            self.cnf.rootwidget.ooffset_wid.value = 0

    def inifile_callback(self, instance):
        filename = self.cnf.output_dir + 'Settings-' + self.cnf.gettime() + '.conf'
        self.cnf.write_config(filename, self.cnf.rootwidget)

    def dout_callback(self, instance, value):
        if value == 'down':
            self.cnf.dout_active = True
        else:
            self.cnf.dout_active = False

    def recorder_callback(self, instance, value):
        if value == 'Sequence':
            self.cnf.imgindx = 0
            self.cnf.image_dst = self.cnf.output_dir + self.cnf.gettime()
            self.cnf.recordi = True
        elif value == 'Video' and skvdetected:
            self.cnf.recordi = False
            self.cnf.video = VideoWriter(
                self.cnf.output_dir + self.cnf.gettime() + '.avi')
            self.cnf.recordv = True
        else:
            self.cnf.recordi = False
            self.cnf.recordv = False

    def override_callback(self, instance, value):
        if value == 'down':
            self.cnf.override_active = False
        else:
            self.cnf.override_active = True

    def colors_callback(self, instance, value):
        self.cnf.pseudoc = True
        if value == 'AUTUMN':
            self.cnf.color_mode = 0
        elif value == 'BONE':
            self.cnf.color_mode = 1
        elif value == 'JET':
            self.cnf.color_mode = 2
        elif value == 'WINTER':
            self.cnf.color_mode = 3
        elif value == 'RAINBOW':
            self.cnf.color_mode = 4
        elif value == 'OCEAN':
            self.cnf.color_mode = 5
        elif value == 'SUMMER':
            self.cnf.color_mode = 6
        elif value == 'SPRING':
            self.cnf.color_mode = 7
        elif value == 'COOL':
            self.cnf.color_mode = 8
        elif value == 'HSV':
            self.cnf.color_mode = 9
        elif value == 'PINK':
            self.cnf.color_mode = 10
        elif value == 'HOT':
            self.cnf.color_mode = 11
        else:
            self.cnf.pseudoc = False
            self.cnf.color_mode = 12

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
        elif value == 'RND':
            self.cnf.input_channel = 10
        elif value == 'RNDX':
            self.cnf.input_channel = 11
        else:
            self.cnf.input_channel = 0

    def ihist_callback(self, instance, value):
        if value == 'down':
            self.cnf.show_ihist = True
        else:
            self.cnf.show_ihist = False

    def ohist_callback(self, instance, value):
        if value == 'down':
            self.cnf.show_ohist = True
        else:
            self.cnf.show_ohist = False

    def trf_callback(self, instance, value):
        if value == 'Rise':
            self.cnf.trslope = 0
            self.cnf.trfilter = True
            self.cnf.rootwidget.indzoom_wid.value = self.cnf.trtrigger * 100
        elif value == 'Fall':
            self.cnf.trslope = 1
            self.cnf.trfilter = True
            self.cnf.rootwidget.indzoom_wid.value = self.cnf.trtrigger * 100
        else:
            self.cnf.trfilter = False

    def playmode_callback(self, instance, value):
        if value == '>':
            self.cnf.loop = True
            self.cnf.run = True
        elif value == '>||':
            self.cnf.loop = False
            self.cnf.run = True
        elif value == '||':
            self.cnf.loop = False
            self.cnf.run = False
        self.imageinput.loop = self.cnf.loop

    def vectype_callback(self, instance, value):
        if value == 'Datamode\nAVG':
            self.cnf.vectype = 1
        elif value == 'Datamode\nCUM-Z':
            self.cnf.vectype = 2
        else:
            self.cnf.rootwidget.vectype_wid.text = 'Datamode\nAVG'

    def img2tex(self, img):
        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        tex = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        tex.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return tex

    def process_vector(self, x, y, z):
        self.cnf.vecx = x
        self.cnf.vecy = y
        self.cnf.vecz = z
        outx = 0.0
        outy = 0.0
        outz = 0.0
        if self.cnf.dout_active:
            outx = self.cnf.indzoom * self.cnf.vecx
            outy = self.cnf.indzoom * self.cnf.vecy
            outz = self.cnf.vecz
        if self.cnf.override_active:
            outx += self.cnf.joyx
            outy += self.cnf.joyy
        outx = np.clip(outx - self.cnf.vecxcenter, -100, 100)
        outy = np.clip(outy - self.cnf.vecycenter, -100, 100)
        if self.cnf.actuator:
            self.cnf.act.transmit(
                outx, outy, outz, self.cnf.joyx, self.cnf.joyy)
        if self.cnf.show_vec:
            indx = np.clip(outx / 200 + 0.45, -0.05, 0.95)
            indy = np.clip(outy / 200 + 0.45, -0.05, 0.95)
            ind_pos = {}
            ind_pos['x'] = float(indx)
            ind_pos['y'] = float(indy)
            self.cnf.rootwidget.indicator_wid.pos_hint = ind_pos
            if self.cnf.show_z:
                self.cnf.rootwidget.zindicator_wid.text = str(int(outz))
            if self.cnf.log and not self.cnf.trfilter:
                logstring = str(time.time()) + ',' + time.strftime("%Y%m%d%H%M%S") + ',' + str(outx) + ',' + str(
                    outy) + ',' + str(outz) + ',' + str(self.cnf.joyx) + ',' + str(self.cnf.joyy) + '\n'
                if self.cnf.logfile == 'STDOUT':
                    sys.stdout.write(logstring)
                else:
                    self.cnf.loghandle.write(logstring)

    def image_histogram(self, inputimage, plotimage, color):
        height, width, chans = plotimage.shape
        xscale = width / 255
        counter = 0
        img_hist = cv2.calcHist([inputimage], [0], None, [256], [0, 255])
        cv2.normalize(img_hist, img_hist, 0, height, cv2.NORM_MINMAX)
        for b in img_hist:
            cv2.rectangle(plotimage, (int(counter), height), (int(
                counter + xscale), int(height - b[0])), color, thickness=-1)
            counter += xscale
        return plotimage

    def indzoom_callback(self, instance, value):
        if self.cnf.trfilter:
            self.cnf.trtrigger = float(value / 100)
        else:
            self.cnf.indzoom = float(value)

    def on_joy_axis(self, win, stickid, axisid, value):
        if axisid == self.cnf.joyxaxis:
            self.cnf.joyx = value * 100 / self.cnf.joymaxx
        if axisid == self.cnf.joyyaxis:
            self.cnf.joyy = value * -100 / self.cnf.joymaxy

    def on_joy_hat(self, win, stickid, hatid, value):
        if hatid == self.cnf.joyhat:
            x, y = value
            self.cnf.indzoominc = float(2 * y)

    def on_joy_button_down(self, win, stickid, buttonid):
        # 1 toggle data output
        if buttonid == 0:
            if self.cnf.rootwidget.dout_wid.state == "down":
                self.cnf.rootwidget.dout_wid.state = "normal"
            else:
                self.cnf.rootwidget.dout_wid.state = "down"
        # 2 reset vectoroutput
        elif buttonid == 1:
            self.zerooutput_callback(True)
        # 3 toggle manual override
        elif buttonid == 2:
            if self.cnf.rootwidget.override_wid.state == "down":
                self.cnf.rootwidget.override_wid.state = "normal"
            else:
                self.cnf.rootwidget.override_wid.state = "down"
        # 4 toggle actuator
        elif buttonid == 3:
            if self.cnf.rootwidget.actuator_wid.state == "down":
                self.cnf.rootwidget.actuator_wid.state = "normal"
            else:
                self.cnf.rootwidget.actuator_wid.state = "down"

    def zerooutput_callback(self, instance):
        self.cnf.vecxcenter = self.cnf.indzoom * self.cnf.vecx
        self.cnf.vecycenter = self.cnf.indzoom * self.cnf.vecy
        if self.cnf.override_active:
            self.cnf.vecxoffset = self.cnf.joyx
            self.cnf.vecyoffset = self.cnf.joyy
        self.cnf.vecxcenter -= self.cnf.vecxoffset
        self.cnf.vecycenter -= self.cnf.vecyoffset

    def actuator_callback(self, instance, value):
        if value == 'down':
            self.cnf.actuator = True
            self.cnf.act.start()
        else:
            self.cnf.actuator = False
            self.cnf.act.stop()

    def apply_args(self):
        if self.args.config_file is not None:
            self.cnf.cfgfilename = self.args.config_file
            self.cnf.read_parms(self.cnf.cfgfilename)
        if self.args.input_source is not None:
            self.cnf.video_src = self.args.input_source
        if self.args.frames_second is not None:
            self.cnf.proc_fps = 1.0 / float(self.args.frames_second)
        if self.args.actuator_class is not None:
            self.cnf.actuator_class = self.args.actuator_class
        if self.args.actuator_parm is not None:
            self.cnf.actuator_parm = self.args.actuator_parm
        if self.args.single_thread:
            self.cnf.single_thread = True
            self.title = self.title + ' - SINGLE THREADED'
        if self.args.input_width is not None:
            self.cnf.video_width = self.args.input_width
        if self.args.input_height is not None:
            self.cnf.video_height = self.args.input_height
        if self.args.input_fourcc is not None:
            self.cnf.prop_fourcc = self.args.input_fourcc
        if self.args.output_dir is not None:
            self.cnf.output_dir = self.args.output_dir
        if self.args.log is not None:
            self.cnf.logfile = self.args.log
            self.cnf.log = True
            if self.args.log == 'STDOUT':
                self.cnf.loghandle = sys.stdout
            else:
                self.cnf.loghandle = open(self.cnf.logfile, 'a')
        if str(self.cnf.video_src).isdigit():
            self.cnf.video_src = int(self.cnf.video_src)
        elif self.cnf.video_src == 'PICAMERA':
            self.cnf.raspicam = True
        if self.args.background_source is not None:
            self.cnf.background_source = self.args.background_source
        if str(self.args.blur_strength).isdigit():
            self.cnf.blr_strength = int(self.args.blur_strength)
        if str(self.args.trf_trigger).isdigit():
            self.cnf.trtrigger = float(self.args.trf_trigger)

    def apply_ui_args(self):
        if self.args.config_file is not None:
            self.cnf.read_ui_parms(self.cnf.cfgfilename, self.cnf.rootwidget)
        if self.args.input_denoise:
            self.cnf.rootwidget.idnz_wid.state = 'down'
        if self.args.output_denoise:
            self.cnf.rootwidget.odnz_wid.state = 'down'
        if self.args.input_equalize is not None:
            self.cnf.rootwidget.iequ_wid.text = self.args.input_equalize
        if self.args.output_equalize is not None:
            self.cnf.rootwidget.oequ_wid.text = self.args.output_equalize
        if self.args.processing_mode is not None:
            self.cnf.rootwidget.proc_wid.text = self.args.processing_mode
        if self.args.input_gain is not None:
            self.cnf.rootwidget.igain_wid.value = float(self.args.input_gain)
        if self.args.output_gain is not None:
            self.cnf.rootwidget.ogain_wid.value = float(self.args.output_gain)
        if self.args.input_blur:
            self.cnf.rootwidget.iblur_wid.state = 'down'
        if self.args.output_blur:
            self.cnf.rootwidget.oblur_wid.state = 'down'
        if self.args.input_filter is not None:
            self.cnf.rootwidget.iflt_wid.text = self.args.input_filter
        if self.args.output_filter is not None:
            self.cnf.rootwidget.oflt_wid.text = self.args.output_filter
        if self.args.flip_x:
            self.cnf.rootwidget.flipx_wid.state = 'down'
        if self.args.flip_y:
            self.cnf.rootwidget.flipy_wid.state = 'down'
        if self.args.input_stabilizer:
            self.cnf.rootwidget.istab_wid.state = 'down'
        if self.args.output_stabilizer:
            self.cnf.rootwidget.ostab_wid.state = 'down'
        if self.args.stack_size is not None:
            self.cnf.rootwidget.stack_wid.value = int(self.args.stack_size)
        if self.args.color_mode is not None:
            self.cnf.rootwidget.colors_wid.text = self.args.color_mode
        if self.args.output_recording is not None:
            if self.args.output_recording == 'SEQ':
                self.cnf.rootwidget.recorder_wid.text = 'Sequence'
            if self.args.output_recording == 'VID':
                self.cnf.rootwidget.recorder_wid.text = 'Video'
        if self.args.input_channel is not None:
            self.cnf.rootwidget.ichan_wid.text = self.args.input_channel
        if self.args.vector_zoom is not None:
            self.cnf.rootwidget.indzoom_wid.value = float(
                self.args.vector_zoom)
        if self.args.processing_state is not None:
            if self.args.processing_state == 'PLAY':
                self.cnf.rootwidget.playmode_wid.text = '>||'
            elif self.args.processing_state == 'LOOP':
                self.cnf.rootwidget.playmode_wid.text = '>'
            elif self.args.processing_state == 'PAUSE':
                self.cnf.rootwidget.playmode_wid.text = '||'
        if self.args.hide_input:
            self.cnf.rootwidget.inp_wid.state = 'normal'
        if self.args.hide_output:
            self.cnf.rootwidget.out_wid.state = 'normal'
        if self.args.trf_mode is not None:
            self.cnf.rootwidget.tfl_wid.text = self.args.tfl_mode
        if self.args.darkframe_mode is not None:
            self.cnf.rootwidget.dark_wid.text = self.args.darkframe_mode
        if self.args.vector_mode is not None:
            self.cnf.rootwidget.vectype_wid.text = 'Datamode\n' + self.args.vector_mode

    def create_output(self):
        self.cnf.oimage = self.dsp.copy()
        # create output image
        if self.cnf.pseudoc:
            self.cnf.out = cv2.applyColorMap(self.cnf.oimage, self.cnf.color_mode)
        else:
            self.cnf.out = cv2.cvtColor(self.cnf.oimage, cv2.COLOR_GRAY2BGR)

        # get output vector
        if self.cnf.vectype == 1:
            self.cnf.full_avg, self.cnf.x_avg, self.cnf.y_avg = self.cnf.imagestack.getVectorAVG(self.cnf.imagestack.float_out)
        else:
            self.cnf.full_avg, self.cnf.x_avg, self.cnf.y_avg = self.cnf.imagestack.getVectorCUMZ(self.cnf.imagestack.float_out)

        # record image sequence or video
        if self.cnf.recordi:
            self.cnf.output_file = self.cnf.image_dst + \
                                   str(self.cnf.imgindx).zfill(8) + '.bmp'
            cv2.imwrite(self.cnf.output_fileself.cnf.out)
            self.cnf.imgindx += 1
        elif self.cnf.recordv:
            self.cnf.video.writeFrame(self.cnf.out)

    def generate_xormasks(self):
        one = np.uint8(1)
        self.cnf.xormask1 = np.zeros((self.cnf.video_height, self.cnf.video_width), np.uint8)
        for v in range(0, self.cnf.video_width, 2):
            for h in range(0, self.cnf.video_height, 2):
                self.cnf.xormask1[h, v] = one
                self.cnf.xormask1[h + 1, v + 1] = one
        self.cnf.xormask2 = np.bitwise_xor(self.cnf.xormask1, 1)

    def build(self):
        signal.signal(signal.SIGINT, self.signal_handler)
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
        self.inpb_small = Animation(pos_hint={'x': 0.1, 'top': 0.9})
        self.bpan_in = Animation(pos_hint={'top': 0.1})
        self.bpan_out = Animation(pos_hint={'top': 0})
        self.tpan_in = Animation(pos_hint={'top': 1})
        self.tpan_out = Animation(pos_hint={'top': 1.1})

        # create Kivy UI
        self.cnf.rootwidget = MyScreen()
        self.namelist = ['FLT-OFF']
        for k in range(1, self.cnf.numkernels):
            self.namelist.append(self.cnf.kernels.get_kernel(k)[0])
        if not skvdetected:
            self.cnf.rootwidget.recorder_wid.values = ['Rec-OFF', 'Sequence']
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
        self.cnf.rootwidget.iequ_wid.bind(text=self.iequ_callback)
        self.cnf.rootwidget.oequ_wid.bind(text=self.oequ_callback)
        self.cnf.rootwidget.iflt_wid.bind(text=self.iflt_callback)
        self.cnf.rootwidget.oflt_wid.bind(text=self.oflt_callback)
        self.cnf.rootwidget.stack_wid.bind(value=self.stack_callback)
        self.cnf.rootwidget.proc_wid.bind(text=self.proc_callback)
        self.cnf.rootwidget.dark_wid.bind(text=self.dark_callback)
        self.cnf.rootwidget.reset_wid.bind(on_release=self.reset_callback)
        self.cnf.rootwidget.dout_wid.bind(state=self.dout_callback)
        self.cnf.rootwidget.zero_wid.bind(on_release=self.zerooutput_callback)
        self.cnf.rootwidget.ichan_wid.bind(text=self.ichan_callback)
        self.cnf.rootwidget.indzoom_wid.bind(value=self.indzoom_callback)
        self.cnf.rootwidget.trf_wid.bind(text=self.trf_callback)
        self.cnf.rootwidget.playmode_wid.bind(text=self.playmode_callback)
        self.cnf.rootwidget.inifile_wid.bind(
            on_release=self.inifile_callback)
        self.cnf.rootwidget.recorder_wid.bind(text=self.recorder_callback)
        self.cnf.rootwidget.actuator_wid.bind(
            state=self.actuator_callback)
        self.cnf.rootwidget.override_wid.bind(state=self.override_callback)
        self.cnf.rootwidget.colors_wid.bind(text=self.colors_callback)
        self.cnf.rootwidget.flipx_wid.bind(state=self.flipx_callback)
        self.cnf.rootwidget.flipy_wid.bind(state=self.flipy_callback)
        self.cnf.rootwidget.ihist_wid.bind(state=self.ihist_callback)
        self.cnf.rootwidget.ohist_wid.bind(state=self.ohist_callback)
        self.cnf.rootwidget.istab_wid.bind(state=self.istab_callback)
        self.cnf.rootwidget.ostab_wid.bind(state=self.ostab_callback)
        self.cnf.rootwidget.oimage_wid.bind(size=self.oimage_size_callback)
        self.cnf.rootwidget.vectype_wid.bind(text=self.vectype_callback)
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_hat=self.on_joy_hat)
        Window.bind(on_joy_button_down=self.on_joy_button_down)

        # command line parser
        parser = argparse.ArgumentParser(
            description='Python Frame Sequence Processor', add_help=True)
        parser.add_argument('-ac', '--actuator_class',
                            help='Load actuator class from actuators.py: (Defaults to Paint)')
        parser.add_argument('-ap', '--actuator_parm',
                            help='Parameter (IP etc.) for actuator')
        parser.add_argument('-bg', '--background_source',
                            help='Background image or video')
        parser.add_argument('-bs', '--blur_strength',
                            help='Blur Strength (Kernel Size')
        parser.add_argument('-c', '--config_file',
                            help='Load Configuration from file')
        parser.add_argument('-dm', '--darkframe_mode',
                            help='Darkframe processing mode: Dark-OFF, DynDark, Static, Grey')
        parser.add_argument('-fx', '--flip_x', action='store_true',
                            help='Flip around X axis')
        parser.add_argument('-fy', '--flip_y', action='store_true',
                            help='Flip around Y axis')
        parser.add_argument('-fps', '--frames_second',
                            help='Set processing frame rate')
        parser.add_argument('-hi', '--hide_input', action='store_true',
                            help='Hide input image')
        parser.add_argument('-ho', '--hide_output', action='store_true',
                            help='Hide output image')
        parser.add_argument('-ic', '--input_channel',
                            help='Input Channel: BW, R, G, B, H, S, V, Y, Cr, Cb, RND, RNDX')
        parser.add_argument('-is', '--input_source',
                            help='Input Source: Filename, camera index or PICAMERA')
        parser.add_argument('-iw', '--input_width',
                            help='Width of captured frames')
        parser.add_argument('-ih', '--input_height',
                            help='Height of captured frames')
        parser.add_argument('-i4', '--input_fourcc',
                            help='fourcc string for input camera codec. Default YUYV')
        parser.add_argument('-ib', '--input_blur', action='store_true',
                            help='Blur Input')
        parser.add_argument('-ie', '--input_equalize',
                            help='Input Equalization Mode')
        parser.add_argument('-if', '--input_filter', help='Set Input Filter')
        parser.add_argument('-ifs', '--input_filter_strength',
                            help='Set Input Filter Strength')
        parser.add_argument('-ig', '--input_gain', help='Input Gain')
        parser.add_argument('-ii', '--input_stabilizer', action='store_true',
                            help='Enable input image stabilizer')
        parser.add_argument('-in', '--input_denoise', action='store_true',
                            help='Input Denoise')
        parser.add_argument('-l', '--log',
                            help='Log to Filename or STDOUT')
        parser.add_argument('-ob', '--output_blur', action='store_true',
                            help='Blur Output')
        parser.add_argument('-oc', '--color_mode', help='Output Color Mode')
        parser.add_argument('-od', '--output_dir',
                            help='Directory to save videos, images and logfiles.')
        parser.add_argument('-oe', '--output_equalize',
                            help='Output Equalization Mode')
        parser.add_argument('-of', '--output_filter', help='Set Output Filter')
        parser.add_argument('-ofs', '--output_filter_strength',
                            help='Set Output Filter Strength')
        parser.add_argument('-og', '--output_gain', help='Output Gain')
        parser.add_argument('-oi', '--output_stabilizer', action='store_true',
                            help='Enable output image stabilizer')
        parser.add_argument('-on', '--output_denoise', action='store_true',
                            help='Output Denoise')
        parser.add_argument('-or', '--output_recording',
                            help='Record output: SEQ, VID')
        parser.add_argument('-ps', '--processing_state',
                            help='Processing State: PLAY, LOOP, PAUSE')
        parser.add_argument('-pm', '--processing_mode',
                            help='Set Processing Mode: AVG, DIFF, CUM-Z')
        parser.add_argument('-pz', '--stack_size',
                            help='Image Stacking (No. of frames to stack)')
        parser.add_argument('-st', '--single_thread', action='store_true',
                            help='Run appication as single thread')
        parser.add_argument('-tfm', '--trf_mode',
                            help='Set Transient Filter Mode: Rise, Fall')
        parser.add_argument('-tft', '--trf_trigger',
                            help='Set Transient Filter Triggerlevel')
        parser.add_argument('-vm', '--vector_mode',
                            help='Set Vector Display / Data Mode: AVG, CUM-Z')
        parser.add_argument('-vz', '--vector_zoom',
                            help='Set Vector Display / Output Zoom')

        self.args = parser.parse_args(sys.argv[1:])
        self.apply_args()

        # initialize video input
        if self.cnf.raspicam:
            self.imageinput = vs.FrameInputPi(
                self.cnf.video_src, self.cnf.video_width, self.cnf.video_height, self.cnf)
        else:
            self.imageinput = vs.FrameInput(
                self.cnf.video_src, self.cnf.video_width, self.cnf.video_height, self.cnf)
        self.cnf.video_width = self.imageinput.frame_width
        self.cnf.video_height = self.imageinput.frame_height

        # prepare stack
        self.cnf.imagestack = fs.FrameStack(
            self.cnf.max_stacksize, self.cnf.numframes, self.cnf.video_width, self.cnf.video_height)

        # apply loaded settings to stack
        self.apply_settings()

        # create a CLAHE object (Contrast Limited Adaptive Histogram
        # Equalization)
        self.clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))

        # prepre background image
        self.cnf.background = np.full((self.cnf.video_height, self.cnf.video_width, 3),
                                  self.cnf.imagestack.default_value, np.uint8)
        self.generate_xormasks()

        # prepare first frame
        self.inp = self.imageinput.grab_frame()
        self.cnf.out = self.inp.copy()
        self.cnf.disp_image = self.inp.copy()
        self.inp = cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY)
        self.cnf.oimage = self.inp.copy()
        self.inp_old = self.inp.copy()
        self.inp_raw = self.inp.copy()
        self.dsp_old = self.inp.copy()
        self.dsp_raw = self.inp.copy()

        # load actuator
        self.oimage_size_callback(None, self.cnf.rootwidget.oimage_wid.size)
        try:
            class_ = getattr(acts, self.cnf.actuator_class)
            self.cnf.act = class_(self.cnf)
        except:
            self.cnf.actuator_class = 'Paint'
            class_ = getattr(acts, self.cnf.actuator_class)
            self.cnf.act = class_(self.cnf)

        # update UI and settings
        self.apply_ui_args()

        # run worker threads or loop
        self.apply_ui_args()
        if self.cnf.single_thread:
            Clock.schedule_interval(self.single_thread, self.cnf.output_fps)
        else:
            Clock.schedule_interval(self.update_output, self.cnf.output_fps)
            self.cnf.procthread = Thread(target=self.process_thread)
            self.cnf.procthread.start()
        return self.cnf.rootwidget

    def single_thread(self, dt):
        self.process_frame()
        self.update_output(True)

    def update_output(self, dt):
        if self.cnf.run:
            if self.cnf.show_out:
                if self.cnf.show_ihist:
                    tmpimg = self.image_histogram(
                        self.cnf.imagestack.inp_frame, self.cnf.out, self.cnf.red)
                else:
                    tmpimg = self.cnf.out
                if self.cnf.show_ohist:
                    self.cnf.disp_image = self.image_histogram(
                        self.cnf.oimage, tmpimg, self.cnf.green)
                else:
                    self.cnf.disp_image = tmpimg
                self.cnf.rootwidget.oimage_wid.texture = self.img2tex(self.cnf.disp_image)
            if self.cnf.show_inp:
                self.showiimage = cv2.cvtColor(np.uint8(self.cnf.imagestack.inp_frame),
                                               cv2.COLOR_GRAY2BGR)
                self.cnf.rootwidget.iimage_wid.texture = self.img2tex(
                    self.showiimage)
            if self.cnf.stack_status:
                self.cnf.rootwidget.stackdisplay_wid.color = (1, 0, 0, 1)
            else:
                self.cnf.rootwidget.stackdisplay_wid.color = (0, 1, 0, 1)
            self.process_vector(
                self.cnf.x_avg, self.cnf.y_avg, self.cnf.full_avg)
            if self.cnf.indzoominc != 0 and not self.cnf.trfilter:
                zoom = self.cnf.rootwidget.indzoom_wid.value
                zoom = np.clip(zoom + self.cnf.indzoominc, 1, 4000)
                self.cnf.rootwidget.indzoom_wid.value = float(zoom)

    def process_thread(self):
        while self.cnf.proc_thread_run:
            self.process_frame()
            time.sleep(self.cnf.proc_fps)

    # main video processing function
    def process_frame(self):
        if self.cnf.run:
            self.inp = self.imageinput.grab_frame()
            if self.cnf.input_channel == 0:
                self.inp = cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY)
            elif self.cnf.input_channel == 1:
                b, g, self.inp = cv2.split(self.inp)
            elif self.cnf.input_channel == 2:
                b, self.inp, r = cv2.split(self.inp)
            elif self.cnf.input_channel == 3:
                self.inp, g, r = cv2.split(self.inp)
            elif self.cnf.input_channel == 4:
                self.inp, s, v = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
            elif self.cnf.input_channel == 5:
                h, self.inp, v = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
            elif self.cnf.input_channel == 6:
                h, s, self.inp = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2HSV))
            elif self.cnf.input_channel == 7:
                self.inp, cr, cb = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
            elif self.cnf.input_channel == 8:
                y, self.inp, cb = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
            elif self.cnf.input_channel == 9:
                y, cr, self.inp = cv2.split(
                    cv2.cvtColor(self.inp, cv2.COLOR_BGR2YCR_CB))
            elif self.cnf.input_channel == 10:
                self.inp = np.bitwise_and(cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY), 1) * 255
            elif self.cnf.input_channel == 11:
                self.inp = np.bitwise_and(cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY), 1)
                if self.cnf.xorvalue:
                    self.cnf.xorvalue = False
                    self.inp = np.bitwise_xor(self.inp, self.cnf.xormask2) * 255
                else:
                    self.cnf.xorvalue = True
                    self.inp = np.bitwise_xor(self.inp, self.cnf.xormask1) * 255
            if self.cnf.equ_inp == 1:
                self.inp = cv2.equalizeHist(self.inp)
            elif self.cnf.equ_inp == 2:
                self.inp = self.clahe.apply(self.inp)
            if self.cnf.dnz_inp:
                cv2.fastNlMeansDenoising(
                    self.inp, self.inp, self.cnf.dnz_inp_str, 7, 21)
            if self.cnf.flt_inp != 0:
                self.inp = cv2.filter2D(self.inp, -1, self.cnf.flt_inp_kernel)
            if self.cnf.stb_inp:
                self.transform = cv2.estimateRigidTransform(
                    self.inp_old, self.inp, False)
                if self.transform is not None:
                    self.inp = cv2.warpAffine(self.inp, self.transform, (self.cnf.video_width, self.cnf.video_height),
                                              self.inp_raw, cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                                              cv2.BORDER_TRANSPARENT)
            self.inp_old = self.inp
            self.cnf.iimage = self.inp.copy()
            self.cnf.stack_status = self.cnf.imagestack.addFrame(self.inp)
            if self.cnf.mode_prc == 0:
                self.dsp = self.cnf.imagestack.getINP()
            elif self.cnf.mode_prc == 1:
                self.dsp = self.cnf.imagestack.getAVG()
            elif self.cnf.mode_prc == 2:
                self.dsp = self.cnf.imagestack.getDIFF()
            elif self.cnf.mode_prc == 3:
                self.dsp = self.cnf.imagestack.getCUMSUM()
            if self.cnf.equ_out == 1:
                self.dsp = cv2.equalizeHist(self.dsp)
            elif self.cnf.equ_out == 2:
                self.dsp = self.clahe.apply(self.dsp)
            if self.cnf.dnz_out:
                cv2.fastNlMeansDenoising(
                    self.dsp, self.dsp, self.cnf.dnz_out_str, 7, 21)
            if self.cnf.flt_out != 0:
                self.dsp = cv2.filter2D(self.dsp, -1, self.cnf.flt_out_kernel)
            if self.cnf.stb_out:
                self.transform = cv2.estimateRigidTransform(
                    self.dsp_old, self.dsp, False)
                if self.transform is not None:
                    self.dsp = cv2.warpAffine(self.dsp, self.transform, (self.cnf.video_width, self.cnf.video_height),
                                              self.dsp_raw, cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                                              cv2.BORDER_TRANSPARENT)

            # transient filter
            if self.cnf.trfilter:
                self.cnf.trpre, self.cnf.trflt = self.cnf.imagestack.getTRFILTER(self.cnf.imagestack.float_out)
                self.cnf.trpref = abs(self.cnf.trpre - self.cnf.trflt)
                if self.cnf.log:
                    logstring = str(time.time()) + ',' + time.strftime("%Y%m%d%H%M%S") + ',' + str(self.cnf.trflt) + ',' + str(self.cnf.trpref) + '\n'
                    self.cnf.loghandle.write(logstring)
                if self.cnf.trslope == 1:
                    if self.cnf.trpref <= self.cnf.trtrigger:
                        self.create_output()
                elif self.cnf.trpref >= self.cnf.trtrigger:
                    self.create_output()
            else:
                self.create_output()

            self.dsp_old = self.dsp


if __name__ == '__main__':
    PyFSPro().run()
