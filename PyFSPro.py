#!/usr/bin/env python
from __future__ import division, print_function
import sys
import signal
import time
import argparse

import numpy as np
import cv2
import cv2.cv as cv

# local imports
import config
import videosource as vs
import framestacker as fs
import filters as flt

#scikit-video (scikit-video.org) is used for recording because of OpenCV Linux bug
from skvideo.io import FFmpegWriter as VideoWriter

cnf = config.Settings()

def nothing(par):
    return

def signal_handler(signal, frame):
    sys.exit(0)
    
def gettime():
    timestring = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    return timestring

def set_osd():
    cnf.osd_inp = 'Input: Gain:' + "{:3.2f}".format(imagestack.gain_inp)
    cnf.osd_out = 'Output: Gain:' + "{:3.2f}".format(imagestack.gain_out)
    cnf.osd_col = ('Size: ' + str(cnf.video_width) + 'x' +
               str(cnf.video_height) + ' Color: ')
    cnf.osd_mode = 'Proc:'
    if cnf.stabilizer:
        cnf.osd_inp += ' Stabilizer'
    if cnf.equ_inp == 0:
        cnf.osd_inp += ' Equ:OFF'
    elif cnf.equ_inp == 1:
        cnf.osd_inp += ' Equ:Hist'
    elif cnf.equ_inp == 2:
        cnf.osd_inp += ' Equ:CLAHE'
    if cnf.equ_out == 0:
        cnf.osd_out += ' Equ:OFF'
    elif cnf.equ_out == 1:
        cnf.osd_out += ' Equ:Hist'
    elif cnf.equ_out == 2:
        cnf.osd_out += ' Equ:CLAHE'
    if imagestack.blr_inp:
        cnf.osd_inp += ' Blur:' + str(imagestack.kernel_size)
    if imagestack.blr_out:
        cnf.osd_out += ' Blur:' + str(imagestack.kernel_size)
    if cnf.dnz_inp:
        cnf.osd_inp += ' Dnz:' + str(cnf.dnz_inp_str)
    if cnf.dnz_out:
        cnf.osd_out += ' Dnz:' + str(cnf.dnz_out_str)
    if cnf.flt_inp > 0:
         cnf.osd_inp += ' Flt: ' + str(flt_inp_name) + ' ' +  "{:3.2f}".format(cnf.flt_inp_strength)
    if cnf.flt_out > 0:
         cnf.osd_out += ' Flt: ' + str(flt_out_name) + ' ' +  "{:3.2f}".format(cnf.flt_out_strength)
    if imageinput.loop:
        cnf.osd_inp += ' LOOPING'
    if cnf.pseudoc is False:
        cnf.osd_col += 'Grey'
    else:
        cnf.osd_col += cnf.colormaps[cnf.color_mode] + '(' + str(cnf.color_mode) + ')'
    if cnf.mode_prc == 0:
        cnf.osd_mode += 'OFF'
    elif cnf.mode_prc == 1:
        cnf.osd_mode += 'AVG'
    elif cnf.mode_prc == 2:
        cnf.osd_mode += 'DIFF'
    elif cnf.mode_prc == 3:
        cnf.osd_mode += 'CUMSUM'
    if imagestack.flip_x:
        cnf.osd_mode += ' Flip_X'
    if imagestack.flip_y:
        cnf.osd_mode += ' Flip_Y'
    if cnf.dyn_dark:
        cnf.osd_mode += ' DarkF:AVG'
    else:
        cnf.osd_mode += ' DarkF:Fix'
    cnf.osd_mode += ' Stack:' + str(cnf.numframes)
    if cnf.recordv:
        cnf.osd_recording = 'Rec: Video'
    if cnf.recordi:
        if cnf.recordv:
            cnf.osd_recording += ' + Image Sequence'
        else:
            cnf.osd_recording = 'Rec: Image Sequence'


def show_help():
    print('', file=sys.stderr)
    for h in cnf.helptxt:
        print(h, file=sys.stderr)
    print('', file=sys.stderr)


def draw_pattern():
    if cnf.pattern_size <= 0:
        cnf.pattern_size = 0
    if cnf.pattern_size == 0 and cnf.backgnd:
        cv2.destroyWindow('Schlieren Background')
        cnf.backgnd = False
    tmp_img = np.zeros((cnf.screen_height,cnf.screen_width,3), np.uint8)
    if cnf.pattern_size >= 1:
        if not cnf.backgnd:
            cv2.namedWindow('Schlieren Background', 0)
            cnf.backgnd = True
        if (cnf.pattern_mode == 3):
            for j in range(0,cnf.screen_width,2*cnf.pattern_size):
                cv2.rectangle(tmp_img,(j,0),(j+cnf.pattern_size,cnf.screen_height),(255,255,255),cv.CV_FILLED)
        else:
            for j in range(0,cnf.screen_height,2*cnf.pattern_size):
                if (cnf.pattern_mode == 1):
                    for i in range(0,cnf.screen_width,2*cnf.pattern_size):
                        cv2.rectangle(tmp_img,(i,j),(i+cnf.pattern_size,j+cnf.pattern_size),(255,255,255),cv.CV_FILLED)
                        cv2.rectangle(tmp_img,(i+cnf.pattern_size,j+cnf.pattern_size),(i+2*cnf.pattern_size,j+2*cnf.pattern_size),(255,255,255),cv.CV_FILLED)
                if (cnf.pattern_mode == 2):
                        cv2.rectangle(tmp_img,(0,j),(cnf.screen_width,j+cnf.pattern_size),(255,255,255),cv.CV_FILLED)
        cv2.putText(tmp_img, str(cnf.pattern_size), (12, 41), cv2.FONT_HERSHEY_PLAIN, 2.0, cnf.black, thickness=2, lineType=cv2.CV_AA)
        cv2.putText(tmp_img, str(cnf.pattern_size), (10, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, cnf.red, thickness=2, lineType=cv2.CV_AA)
    return tmp_img



if __name__ == '__main__':

    # register signal handler for a clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # command line parser
    parser = argparse.ArgumentParser(description='Python Frame Sequence Processor')
    parser.add_argument('-is', '--input_source', default=cnf.video_src,
                        help='Input Source, filename or camera index')
    parser.add_argument('-iw', '--input_width', default=cnf.video_width,
                        help='Width of captured frames')
    parser.add_argument('-ih', '--input_height', default=cnf.video_height,
                        help='Height of captured frames')
    parser.add_argument('-ib', '--input_blur', action='store_true',
                        help='Blur Input')
    parser.add_argument('-ie', '--input_equalize', default=cnf.equ_inp,
                        help='Input Equalization Mode')
    parser.add_argument('-if', '--input_filter', default=cnf.flt_inp,
                        help='Set Input Filter')
    parser.add_argument('-ifs', '--input_filter_strength', default='none',
                        help='Set Input Filter Strength')
    parser.add_argument('-ig', '--input_gain', default=cnf.gain_inp, help='Input Gain')
    parser.add_argument('-il', '--loop_input', action='store_true',
                        help='Loop input video')
    parser.add_argument('-im', '--input_mode', default=cnf.mode_in,
                        help='Display Mode Input Window')
    parser.add_argument('-in', '--input_denoise', default='none',
                        help='Input Denoise Strength')
    parser.add_argument('-i', '--image_stabilizer', action='store_true',
                        help='Enable input image stabilizer')
    parser.add_argument('-bs', '--blur_strength', default=cnf.blr_strength,
                        help='Blur Strength (Kernel Size')
    parser.add_argument('-fx', '--flip_x', action='store_true',
                        help='Flip around X axis')
    parser.add_argument('-fy', '--flip_y', action='store_true',
                        help='Flip around Y axis')
    parser.add_argument('-k', '--keyboard_shortcuts', action='store_true',
                        help='Show Keyboard Shortcuts')
    parser.add_argument('-ob', '--output_blur', action='store_true',
                        help='Blur Output')
    parser.add_argument('-oc', '--color_mode', default=cnf.color_mode,
                        help='Output Pseudocolor mode (1-11)')
    parser.add_argument('-oe', '--output_equalize', default=cnf.equ_out,
                        help='Output Equalization Mode')
    parser.add_argument('-of', '--output_filter', default=cnf.flt_out,
                        help='Set Output Filter')
    parser.add_argument('-ofs', '--output_filter_strength', default='none',
                        help='Set Output Filter Strength')
    parser.add_argument('-og', '--output_gain', default=cnf.gain_out, help='Output Gain')
    parser.add_argument('-on', '--output_denoise', default='none',
                        help='Output Denoise Strength')   
    parser.add_argument('-om', '--output_mode', default=cnf.mode_out,
                        help='Display Mode Output Window')
    parser.add_argument('-ov', '--output_video', default='none',
                        help='Save output as video (Path or Prefix).')
    parser.add_argument('-oi', '--output_images', default='none',
                        help='Save output as image sequence (Path or Prefix).')
    parser.add_argument('-pm', '--processing_mode', default=cnf.mode_prc,
                        help='Set Processing Mode')
    parser.add_argument('-ps', '--pattern_size', default=cnf.pattern_size,
                        help='Schlieren Background Pattern Size')
    parser.add_argument('-pt', '--pattern_type', default='none',
                        help='Schlieren Background Pattern (1-3)')
    parser.add_argument('-pz', '--stack_size', default=cnf.numframes,
                        help='Image Stacking (No. of frames to stack)')
    parser.add_argument('-ww', '--window_width', default=cnf.window_width,
                        help='Width of displayed Windows')
    parser.add_argument('-wh', '--window_height', default=cnf.window_height,
                        help='Height of displayed Windows')
    args = parser.parse_args()

    # process command line arguments
    if args.input_denoise != 'none':
        cnf.dnz_inp = True
        cnf.dnz_inp_str = float(args.input_denoise)
    if args.output_denoise != 'none':
        cnf.dnz_out = True
        cnf.dnz_out_str = float(args.output_denoise)
    cnf.equ_inp = int(args.input_equalize)
    cnf.equ_out = int(args.output_equalize)
    cnf.mode_out = int(args.output_mode)
    cnf.mode_in = int(args.input_mode)
    cnf.mode_prc = int(args.processing_mode)
    cnf.gain_inp = float(args.input_gain)
    cnf.gain_out = float(args.output_gain)
    cnf.blr_inp = args.input_blur
    cnf.blr_out = args.output_blur
    cnf.blr_strength = int(args.blur_strength)
    cnf.flt_inp = int(args.input_filter)
    cnf.flt_out = int(args.output_filter)
    cnf.loop = args.loop_input
    cnf.stabilizer = args.image_stabilizer
    cnf.flip_x = args.flip_x
    cnf.flip_y = args.flip_y
    if cnf.equ_inp >= 3:
        cnf.equ_inp = 2
    elif cnf.equ_inp <= -1:
        cnf.equ_inp = 0
    if cnf.equ_out >= 3:
        cnf.equ_out = 2
    elif cnf.equ_out <= -1:
        cnf.equ_out = 0
    if cnf.mode_prc >= 4:
        cnf.mode_prc = 3
    elif cnf.mode_prc <= -1:
        cnf.mode_prc = 0
    if cnf.mode_in >= 3:
        cnf.mode_in = 2
    elif cnf.mode_in <= -1:
        cnf.mode_in = 0
    if cnf.mode_out >= 3:
        cnf.mode_out = 2
    elif cnf.mode_out <= -1:
        cnf.mode_out = 0
    if int(args.stack_size) > 0:
        cnf.numframes = int(args.stack_size)
    if int(args.color_mode) <= 11 and int(args.color_mode) >= 0:
        cnf.color_mode = int(args.color_mode)
        cnf.pseudoc = True
    if str(args.input_source).isdigit():
        cnf.video_src = int(args.input_source)
    else:
        cnf.video_src = args.input_source
    if args.keyboard_shortcuts:
        show_help()
        sys.exit(0)
    if args.pattern_type != 'none':
        cnf.pattern_mode = int(args.pattern_type)
        if int(args.pattern_size) > 0:
            cnf.pattern_size = int(args.pattern_size)
        else:
            cnf.pattern_size = 4
        cnf.pattern = draw_pattern()
        cv2.imshow('Schlieren Background', cnf.pattern)
    if int(args.pattern_size) > 0:
        cnf.pattern_size = int(args.pattern_size)
        cnf.pattern = draw_pattern()
        cv2.imshow('Schlieren Background', cnf.pattern)
    if args.output_video != 'none':
        cnf.recordv = True
        cnf.video_dst = args.output_video
    if args.output_images != 'none':
        cnf.recordi = True
        cnf.image_dst = args.output_images
    cnf.window_width = int(args.window_width)
    cnf.window_height = int(args.window_height)

    # initialize video input
    imageinput = vs.FrameInput(cnf.video_src, args.input_width, args.input_height)
    imageinput.loop = cnf.loop
    cnf.video_width = imageinput.frame_width
    cnf.video_height = imageinput.frame_height

    # we wait to make sure whoever started this program has released RETURN
    time.sleep(1)
    nokey = cv2.waitKey(5)  # get value for "no key pressed"

    # load filter kernels
    kernels = flt.Kernels()
    numkernels = kernels.get_numkernels()
    flt_inp_name, cnf.inp_kernel, cnf.flt_inp_strength = kernels.get_kernel(cnf.flt_inp)
    flt_out_name, cnf.out_kernel, cnf.flt_out_strength = kernels.get_kernel(cnf.flt_out)
    if args.input_filter_strength != 'none':
        cnf.flt_inp_strength = float(args.input_filter_strength)
    if args.output_filter_strength != 'none':
        cnf.flt_out_strength = float(args.output_filter_strength)
    flt_inp_kernel = cnf.inp_kernel * cnf.flt_inp_strength
    flt_out_kernel = cnf.out_kernel * cnf.flt_out_strength
    
    # prepare stack
    imagestack = fs.FrameStack(cnf.numframes, cnf.video_width, cnf.video_height)
    imagestack.gain_inp = cnf.gain_inp
    imagestack.gain_out = cnf.gain_out
    imagestack.blr_inp = cnf.blr_inp
    imagestack.blr_out = cnf.blr_out
    imagestack.setKernel(cnf.blr_strength)
    imagestack.flip_x = cnf.flip_x
    imagestack.flip_y = cnf.flip_y

    # create windows and GUI
    cv2.namedWindow('Processed Output', 0)
    cv2.namedWindow('Input', 0)
    cv2.resizeWindow('Input', cnf.window_width, cnf.window_height)
    cv2.resizeWindow('Processed Output', cnf.window_width, cnf.window_height)
    cv2.moveWindow('Input', cnf.window_x, cnf.window_y)
    cv2.moveWindow('Processed Output', cnf.window_x + cnf.window_width +
                   cnf.window_space, cnf.window_y)
    set_osd()

    # create a CLAHE object (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))

    # prepare on screen vector display
    center_x = int(cnf.video_width / 2)
    center_y = int(cnf.video_height / 2)
    center = (center_x, center_y)
    vec_zoom_2 = cnf.vec_zoom / 2
    background = np.full((cnf.video_height, cnf.video_width, 3),
                         imagestack.default_value, np.uint8)
    
    # keep image aspect ratio of video input
    image_height = int(cnf.video_height / cnf.video_width * cnf.window_width)
    
    # prepare image stabilizer
    inp = imageinput.grab_frame()
    inp_old = inp.copy()
    inp_raw = inp.copy()

    # main video processing loop
    while True:
        inp = imageinput.grab_frame()
        if cnf.dnz_inp:
            cv2.fastNlMeansDenoising(inp, inp, cnf.dnz_inp_str, 7, 21)
        if cnf.equ_inp == 1:
            inp = cv2.equalizeHist(inp)
        elif cnf.equ_inp == 2:
            inp = clahe.apply(inp)
        elif cnf.flt_inp != 0:
            inp = cv2.filter2D(inp, -1, flt_inp_kernel)
        if cnf.stabilizer:
            back = np.nanmean(inp)
            transform = cv2.estimateRigidTransform(inp_old, inp, False)
            if transform is not None:
                inp = cv2.warpAffine(inp, transform, (cnf.video_width, cnf.video_height), inp_raw, cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP, cv2.BORDER_TRANSPARENT)
        inp_old = inp
        imagestack.addFrame(inp)
        if cnf.mode_prc == 0:
            dsp = imagestack.getINP()
        elif cnf.mode_prc == 1:
            dsp = imagestack.getAVG()
        elif cnf.mode_prc == 2:
            dsp = imagestack.getDIFF()
        elif cnf.mode_prc == 3:
            dsp = imagestack.getCUMSUM()
        if cnf.equ_out == 1:
            dsp = cv2.equalizeHist(dsp)
        elif cnf.equ_out == 2:
            dsp = clahe.apply(dsp)
        if cnf.dnz_out:
            cv2.fastNlMeansDenoising(dsp, dsp, cnf.dnz_out_str, 7, 21)
        elif cnf.flt_out != 0:
            dsp = cv2.filter2D(dsp, -1, flt_out_kernel)

        # create input image
        if cnf.mode_in == 1:
            inp = np.copy(background)
        else:
            inp = cv2.cvtColor(np.uint8(imagestack.inp_frame),
                               cv2.COLOR_GRAY2BGR)
        inp = cv2.resize(inp, (cnf.window_width, image_height))
        if cnf.mode_in <= 1:
            cv2.putText(inp, cnf.osd_inp, (12, 41), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.black, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_inp, (10, 40), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.green, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_out, (12, 71), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.black, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_out, (10, 70), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.green, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_col, (12, 101), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.black, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_col, (10, 100), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.green, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_mode, (12, 131), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.black, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, cnf.osd_mode, (10, 130), cv2.FONT_HERSHEY_PLAIN,
                        cnf.osd_txtsize, cnf.blue, thickness=cnf.osd_txtline,
                        lineType=cv2.CV_AA)
            if cnf.recordv or cnf.recordi:
                cv2.putText(inp, cnf.osd_recording, (12, 161),
                            cv2.FONT_HERSHEY_PLAIN, cnf.osd_txtsize, cnf.black,
                            thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
                cv2.putText(inp, cnf.osd_recording, (10, 160),
                            cv2.FONT_HERSHEY_PLAIN, cnf.osd_txtsize, cnf.red,
                            thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
            if imagestack.filling_stack:
                cv2.putText(inp, "Filling Stack", (12, 191),
                            cv2.FONT_HERSHEY_PLAIN, cnf.osd_txtsize, cnf.black,
                            thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
                cv2.putText(inp, "Filling Stack", (10, 190),
                            cv2.FONT_HERSHEY_PLAIN, cnf.osd_txtsize, cnf.red,
                            thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
        cv2.imshow('Input', inp)

        # create output image
        if cnf.mode_out == 1:
            out = np.copy(background)
        elif cnf.pseudoc:
            out = cv2.applyColorMap(dsp, cnf.color_mode)
        else:
            out = cv2.cvtColor(dsp, cv2.COLOR_GRAY2BGR)
        if cnf.mode_out >= 1:
            x_avg, y_avg = imagestack.getVECTOR(cnf.vec_zoom)
            cv2.line(out, center, (x_avg, y_avg), cnf.green,
                     thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
            cv2.circle(out, (x_avg, y_avg), 20, cnf.red,
                       thickness=cnf.osd_txtline, lineType=cv2.CV_AA)
        cv2.imshow('Processed Output', out)
        
        # record video or image sequence
        if cnf.recordv:
            if cnf.novfile:
                video = VideoWriter(cnf.video_dst + gettime() + '.avi')
                cnf.novfile = False
            video.writeFrame(out)
        if cnf.recordi:
            if cnf.imgindx == 0:
                cnf.image_dst += gettime()
            filename = cnf.image_dst + str(cnf.imgindx).zfill(8) + '.bmp'
            cv2.imwrite(filename, out)
            cnf.imgindx += 1

        # process keyboard input and update OSD
        keyscan = cv2.waitKey(5)
        if keyscan != nokey:
            asckey = 0xFF & keyscan
            if asckey == 97:  # a auto adjust input gain and offset
                imagestack.autoInpGain()
            if asckey == 65:  # A auto adjust output gain and offset
                imagestack.autoOutGain()
            if asckey == 98:  # b blur input
                imagestack.blr_inp = not imagestack.blr_inp
            elif asckey == 66:  # B blur output
                imagestack.blr_out = not imagestack.blr_out
            elif asckey == 99:  # c choose color palette
                cnf.color_mode += 1
                if cnf.color_mode > 11:
                    cnf.pseudoc = False
                    cnf.color_mode = -1
                else:
                    cnf.pseudoc = True
            elif asckey == 100:  # d use current average as dark frame
                cnf.dyn_dark = not cnf.dyn_dark
                imagestack.dyn_dark = cnf.dyn_dark
            elif asckey == 101:  # e Cycle input equalization
                cnf.equ_inp += 1
                if cnf.equ_inp >= 3:
                    cnf.equ_inp = 0
            elif asckey == 69:  # E Cycle output equalization
                cnf.equ_out += 1
                if cnf.equ_out >= 3:
                    cnf.equ_out = 0
            elif asckey == 102:  # f Cycle input filters
                cnf.flt_inp += 1
                if cnf.flt_inp >= numkernels:
                    cnf.flt_inp = 0
                flt_inp_name, cnf.inp_kernel, cnf.flt_inp_strength = kernels.get_kernel(cnf.flt_inp)
                flt_inp_kernel = cnf.inp_kernel * cnf.flt_inp_strength
            elif asckey == 70:  # F Cycle output filters
                cnf.flt_out += 1
                if cnf.flt_out >= numkernels:
                    cnf.flt_out = 0
                flt_out_name, cnf.out_kernel, cnf.flt_out_strength = kernels.get_kernel(cnf.flt_out)
                flt_out_kernel = cnf.out_kernel * cnf.flt_out_strength
            elif asckey == 104:  # h show help
                show_help()
            elif asckey == 105: # i toggle image stabilizer
                cnf.stabilizer = not cnf.stabilizer
            elif asckey == 108: # l toggle input video loop mode
                imageinput.loop = not imageinput.loop
            elif asckey == 109:  # m input mode
                cnf.mode_in += 1
                if cnf.mode_in >= 3:
                    cnf.mode_in = 0
            elif asckey == 77:  # M output mode
                cnf.mode_out += 1
                if cnf.mode_out >= 3:
                    cnf.mode_out = 0
            elif asckey == 110:  # n denoise input
                cnf.dnz_inp = not cnf.dnz_inp
            elif asckey == 78:  # N denoise output
                cnf.dnz_out = not cnf.dnz_out
            elif asckey == 112:  # p processing mode
                cnf.mode_prc += 1
                if cnf.mode_prc >= 4:
                    cnf.mode_prc = 0
            elif asckey == 113:  # q terminates program
                sys.exit(0)
            elif asckey == 114:  # r reset cumulative summing
                imagestack.resetCUMSUM()
            elif asckey == 82:  # R reset gain and offset
                imagestack.gain_inp = cnf.gain_inp
                imagestack.gain_out = cnf.gain_out
                imagestack.offset_inp = 0
                imagestack.offset_out = 0
            elif asckey == 115: # s save settings
                cnf.write_config(cnf.cfgfilename)
            elif asckey == 83: # S load settings
                cnf.read_config(cnf.cfgfilename)
            elif asckey == 118: # v toggle video recording
                cnf.recordv = not cnf.recordv
            elif asckey == 86: # V toggle image sequence recording
                cnf.recordi = not cnf.recordi
            elif asckey == 63:  # ? cycle schlieren pattern type
                cnf.pattern_mode += 1
                if cnf.pattern_mode > 3:
                    cnf.pattern_mode = 1
                if cnf.pattern_size == 0:
                    cnf.pattern_size = 4
                cnf.pattern = draw_pattern()
            elif asckey == 62: # > increase schlieren pattern size
                cnf.pattern_size += 1
                cnf.pattern = draw_pattern()
            elif asckey == 60: # < decrease schlieren pattern size
                cnf.pattern_size -= 1
                cnf.pattern = draw_pattern()
            elif asckey == 120:  # x flip around X axis
                imagestack.flip_x = not imagestack.flip_x
            elif asckey == 121:  # y flip around Y axis
                imagestack.flip_y = not imagestack.flip_y
            elif asckey == 93:  # ] increase input gain
                imagestack.gain_inp += cnf.gain_increment
            elif asckey == 91:  # [ decrease input gain
                imagestack.gain_inp -= cnf.gain_increment
            elif asckey == 125:  # } increase output gain
                imagestack.gain_out += cnf.gain_increment
            elif asckey == 123:  # { decrease output gain
                imagestack.gain_out -= cnf.gain_increment
            elif asckey == 43:  # + increase input filter strength
                cnf.flt_inp_strength += cnf.flt_strength_increment
                flt_inp_kernel = cnf.inp_kernel * cnf.flt_inp_strength
            elif asckey == 45:  # - decrease input filter strength
                cnf.flt_inp_strength -= cnf.flt_strength_increment
                flt_inp_kernel = cnf.inp_kernel * cnf.flt_inp_strength
            elif asckey == 61:  # = increase output filter strength
                cnf.flt_out_strength += cnf.flt_strength_increment
                flt_out_kernel = cnf.out_kernel * cnf.flt_out_strength
            elif asckey == 95:  # _ decrease output filter strength
                cnf.flt_out_strength -= cnf.flt_strength_increment
                flt_out_kernel = cnf.out_kernel * cnf.flt_out_strength
            elif asckey == 32:  # SPACE create screenshot
                filename = cnf.output_path + 'Screenshot-' + gettime() + '.bmp'
                cv2.imwrite(filename, out)
            elif asckey >= 49 and asckey <= 57:  # no of frames to stack
                cnf.numframes = asckey - 48
                imagestack.initStack(cnf.numframes)
            if cnf.backgnd:
                cv2.imshow('Schlieren Background', cnf.pattern)
            set_osd()
    sys.exit(0)
