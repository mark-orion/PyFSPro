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
import videosource as vs
import framestacker as fs

#scikit-video (scikit-video.org) is used for recording because of OpenCV Linux bug
from skvideo.io import FFmpegWriter as VideoWriter

# default values
numframes = 255  # No. of frames in stack
color_mode = -1  # Greyscale output
video_src = 0  # Default camera
video_width = 1024
video_height = 768
window_x = 100  # Position of first window on screen
window_y = 100
window_space = 50  # Space between windows
window_width = 1024 # Default window size
window_height = 768

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
flip_x = False
flip_y = False
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
        'lower/UPPER case = apply to input/output pipeline',
        'a/A  Auto adjust offset and gain',
        'b/B  Blur',
        'c    Cycle through Color Palette',
        'd    Toggle Dark Frame mode (Rolling Average / Fixed)',
        'e/E  Cycle through Equalizer modes (OFF, HIST, CLAHE)',
        'h    Show this help text',
        'i    Toggle image sequence recording',
        'l    Toggle input video loop mode',
        'm    Input Mode (BOTH, STATUS, IMAGE)',
        'M    Output Mode (IMAGE, VECTOR, BOTH)',
        'n/N  Denoise',
        'p    Processing Mode (OFF, AVG, DIFF, CUMSUM)',
        'q    Terminate Program',
        'r    Reset Cumulative Summing',
        'R    Reset Gains and Offsets',
        's    Enable / change Schlieren pattern',
        'S    Toggle input image stabilizer',
        'v    Toggle video recording',
        '>    Increase Schlieren pattern size',
        '<    Decrease Schlieren pattern size',
        'x    Flip image around X axis',
        'y    Flip image around Y axis',
        '[/]  Decrease / Increase Input Gain',
        '{/}  Decrease / Increase Output Gain',
        'SPACE create Screenshot',
        '1-9  Set No. of frames in Stack',
        ]


def nothing(par):
    return

def signal_handler(signal, frame):
    sys.exit(0)
    
def gettime():
    timestring = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    return timestring

def set_osd():
    global osd_inp
    global osd_out
    global osd_col
    global osd_mode
    global osd_recording
    osd_inp = 'Input: Gain:' + "{:3.2f}".format(imagestack.gain_inp)
    osd_out = 'Output: Gain:' + "{:3.2f}".format(imagestack.gain_out)
    osd_col = ('Size: ' + str(video_width) + 'x' +
               str(video_height) + ' Color: ')
    osd_mode = 'Proc:'
    if stabilizer:
        osd_inp += ' Stabilizer'
    if equ_inp == 0:
        osd_inp += ' Equ:OFF'
    elif equ_inp == 1:
        osd_inp += ' Equ:Hist'
    elif equ_inp == 2:
        osd_inp += ' Equ:CLAHE'
    if equ_out == 0:
        osd_out += ' Equ:OFF'
    elif equ_out == 1:
        osd_out += ' Equ:Hist'
    elif equ_out == 2:
        osd_out += ' Equ:CLAHE'
    if imagestack.blr_inp:
        osd_inp += ' Blur:' + str(imagestack.kernel_size)
    if imagestack.blr_out:
        osd_out += ' Blur:' + str(imagestack.kernel_size)
    if dnz_inp:
        osd_inp += ' Dnz:' + str(dnz_inp_str)
    if dnz_out:
        osd_out += ' Dnz:' + str(dnz_out_str)
    if imageinput.loop:
        osd_inp += ' LOOPING'
    if pseudoc is False:
        osd_col += 'Grey'
    else:
        osd_col += colormaps[color_mode] + '(' + str(color_mode) + ')'
    if mode_prc == 0:
        osd_mode += 'OFF'
    elif mode_prc == 1:
        osd_mode += 'AVG'
    elif mode_prc == 2:
        osd_mode += 'DIFF'
    elif mode_prc == 3:
        osd_mode += 'CUMSUM'
    if imagestack.flip_x:
        osd_mode += ' Flip_X'
    if imagestack.flip_y:
        osd_mode += ' Flip_Y'
    if dyn_dark:
        osd_mode += ' DarkF:AVG'
    else:
        osd_mode += ' DarkF:Fix'
    osd_mode += ' Stack:' + str(numframes)
    if recordv:
        osd_recording = 'Rec: Video'
    if recordi:
        if recordv:
            osd_recording += ' + Image Sequence'
        else:
            osd_recording = 'Rec: Image Sequence'


def show_help():
    print('', file=sys.stderr)
    for h in helptxt:
        print(h, file=sys.stderr)
    print('', file=sys.stderr)


def draw_pattern():
    global backgnd
    global pattern_size
    if pattern_size <= 0:
        pattern_size = 0
    if pattern_size == 0 and backgnd:
        cv2.destroyWindow('Schlieren Background')
        backgnd = False
    tmp_img = np.zeros((screen_height,screen_width,3), np.uint8)
    if pattern_size >= 1:
        if not backgnd:
            cv2.namedWindow('Schlieren Background', 0)
            backgnd = True
        if (pattern_mode == 3):
            for j in range(0,screen_width,2*pattern_size):
                cv2.rectangle(tmp_img,(j,0),(j+pattern_size,screen_height),(255,255,255),cv.CV_FILLED)
        else:
            for j in range(0,screen_height,2*pattern_size):
                if (pattern_mode == 1):
                    for i in range(0,screen_width,2*pattern_size):
                        cv2.rectangle(tmp_img,(i,j),(i+pattern_size,j+pattern_size),(255,255,255),cv.CV_FILLED)
                        cv2.rectangle(tmp_img,(i+pattern_size,j+pattern_size),(i+2*pattern_size,j+2*pattern_size),(255,255,255),cv.CV_FILLED)
                if (pattern_mode == 2):
                        cv2.rectangle(tmp_img,(0,j),(screen_width,j+pattern_size),(255,255,255),cv.CV_FILLED)
        cv2.putText(tmp_img, str(pattern_size), (12, 41), cv2.FONT_HERSHEY_PLAIN, 2.0, black, thickness=2, lineType=cv2.CV_AA)
        cv2.putText(tmp_img, str(pattern_size), (10, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, red, thickness=2, lineType=cv2.CV_AA)
    return tmp_img



if __name__ == '__main__':

    # register signal handler for a clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # command line parser
    parser = argparse.ArgumentParser(description='Python Schlieren Imager')
    parser.add_argument('-bi', '--blur_input', action='store_true',
                        help='Blur Input')
    parser.add_argument('-bo', '--blur_output', action='store_true',
                        help='Blur Output')
    parser.add_argument('-bs', '--blur_strength', default=blr_strength,
                        help='Blur Strength (Kernel Size')
    parser.add_argument('-c', '--color_mode', default=color_mode,
                        help='Pseudocolor mode (1-11)')
    parser.add_argument('-di', '--denoise_input', default='none',
                        help='Input Denoise Strength')
    parser.add_argument('-do', '--denoise_output', default='none',
                        help='Output Denoise Strength')
    parser.add_argument('-ei', '--equalize_input', default=equ_inp,
                        help='Input Equalization Mode')
    parser.add_argument('-eo', '--equalize_output', default=equ_out,
                        help='Output Equalization Mode')
    parser.add_argument('-fx', '--flip_x', action='store_true',
                        help='Flip around X axis')
    parser.add_argument('-fy', '--flip_y', action='store_true',
                        help='Flip around Y axis')
    parser.add_argument('-gi', '--gain_input', default=gain_inp, help='Input Gain')
    parser.add_argument('-go', '--gain_output', default=gain_out, help='Output Gain')
    parser.add_argument('-i', '--input_source', default=video_src,
                        help='Input Source, filename or camera index')
    parser.add_argument('-iw', '--input_width', default=video_width,
                        help='Width of captured frames')
    parser.add_argument('-ih', '--input_height', default=video_height,
                        help='Height of captured frames')
    parser.add_argument('-is', '--image_stabilizer', action='store_true',
                        help='Enable input image stabilizer')
    parser.add_argument('-k', '--keyboard_shortcuts', action='store_true',
                        help='Show Keyboard Shortcuts')
    parser.add_argument('-l', '--loop_input', action='store_true',
                        help='Loop input video')
    parser.add_argument('-mi', '--input_mode', default=mode_in,
                        help='Input Mode')
    parser.add_argument('-mp', '--processing_mode', default=mode_prc,
                        help='Processing Mode')
    parser.add_argument('-mo', '--output_mode', default=mode_out,
                        help='Output Mode')
    parser.add_argument('-ov', '--output_video', default='none',
                        help='Save output as video (Path or Prefix).')
    parser.add_argument('-oi', '--output_images', default='none',
                        help='Save output as image sequence (Path or Prefix).')
    parser.add_argument('-pm', '--pattern_mode', default='none',
                        help='Schlieren Background Pattern (1-3)')
    parser.add_argument('-ps', '--pattern_size', default=pattern_size,
                        help='Schlieren Background Pattern Size')
    parser.add_argument('-s', '--stack', default=numframes,
                        help='Image Stacking (No. of frames to stack)')
    parser.add_argument('-ww', '--window_width', default=window_width,
                        help='Width of displayed Windows')
    parser.add_argument('-wh', '--window_height', default=window_height,
                        help='Height of displayed Windows')
    args = parser.parse_args()

    # process command line arguments
    if args.denoise_input != 'none':
        dnz_inp = True
        dnz_inp_str = float(args.denoise_input)
    if args.denoise_output != 'none':
        dnz_out = True
        dnz_out_str = float(args.denoise_output)
    equ_inp = int(args.equalize_input)
    equ_out = int(args.equalize_output)
    mode_out = int(args.output_mode)
    mode_in = int(args.input_mode)
    mode_prc = int(args.processing_mode)
    gain_inp = float(args.gain_input)
    gain_out = float(args.gain_output)
    blr_inp = args.blur_input
    blr_out = args.blur_output
    blr_strength = int(args.blur_strength)
    loop = args.loop_input
    stabilizer = args.image_stabilizer
    flip_x = args.flip_x
    flip_y = args.flip_y
    if equ_inp >= 3:
        equ_inp = 2
    elif equ_inp <= -1:
        equ_inp = 0
    if equ_out >= 3:
        equ_out = 2
    elif equ_out <= -1:
        equ_out = 0
    if mode_prc >= 4:
        mode_prc = 3
    elif mode_prc <= -1:
        mode_prc = 0
    if mode_in >= 3:
        mode_in = 2
    elif mode_in <= -1:
        mode_in = 0
    if mode_out >= 3:
        mode_out = 2
    elif mode_out <= -1:
        mode_out = 0
    if int(args.stack) > 0:
        numframes = int(args.stack)
    if int(args.color_mode) <= 11 and int(args.color_mode) >= 0:
        color_mode = int(args.color_mode)
        pseudoc = True
    if str(args.input_source).isdigit():
        video_src = int(args.input_source)
    else:
        video_src = args.input_source
    if args.keyboard_shortcuts:
        show_help()
    if args.pattern_mode != 'none':
        pattern_mode = int(args.pattern_mode)
        if int(args.pattern_size) > 0:
            pattern_size = int(args.pattern_size)
        else:
            pattern_size = 4
        pattern = draw_pattern()
        cv2.imshow('Schlieren Background', pattern)
    if int(args.pattern_size) > 0:
        pattern_size = int(args.pattern_size)
        pattern = draw_pattern()
        cv2.imshow('Schlieren Background', pattern)
    if args.output_video != 'none':
        recordv = True
        video_dst = args.output_video
    if args.output_images != 'none':
        recordi = True
        image_dst = args.output_images
    window_width = int(args.window_width)
    window_height = int(args.window_height)

    # initialize video input
    imageinput = vs.FrameInput(video_src, args.input_width, args.input_height)
    imageinput.loop = loop
    video_width = imageinput.frame_width
    video_height = imageinput.frame_height

    # we wait to make sure whoever started this program has released RETURN
    time.sleep(1)
    nokey = cv2.waitKey(5)  # get value for "no key pressed"

    # prepare stack
    imagestack = fs.FrameStack(numframes, video_width, video_height)
    imagestack.gain_inp = gain_inp
    imagestack.gain_out = gain_out
    imagestack.blr_inp = blr_inp
    imagestack.blr_out = blr_out
    imagestack.setKernel(blr_strength)
    imagestack.flip_x = flip_x
    imagestack.flip_y = flip_y

    # create windows and GUI
    cv2.namedWindow('Processed Output', 0)
    cv2.namedWindow('Input', 0)
    cv2.resizeWindow('Input', window_width, window_height)
    cv2.resizeWindow('Processed Output', window_width, window_height)
    cv2.moveWindow('Input', window_x, window_y)
    cv2.moveWindow('Processed Output', window_x + window_width +
                   window_space, window_y)
    set_osd()

    # create a CLAHE object (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))

    # prepare on screen vector display
    center_x = int(video_width / 2)
    center_y = int(video_height / 2)
    center = (center_x, center_y)
    vec_zoom_2 = vec_zoom / 2
    background = np.full((video_height, video_width, 3),
                         imagestack.default_value, np.uint8)
    
    # keep image aspect ratio of video input
    image_height = int(video_height / video_width * window_width)
    inp = imageinput.grab_frame()
    inp_old = inp.copy()

    # main video processing loop
    while True:
        inp_raw = imageinput.grab_frame()
        if stabilizer:
            transform = cv2.estimateRigidTransform(inp_old, inp_raw, False)
            if transform is not None:
                inp = cv2.warpAffine(inp_raw, transform, (video_width, video_height), inp_old, cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP)
            else:
                inp = inp_raw
        else:
            inp = inp_raw
        inp_old = inp.copy()
        if dnz_inp:
            cv2.fastNlMeansDenoising(inp, inp, dnz_inp_str, 7, 21)
        if equ_inp == 1:
            inp = cv2.equalizeHist(inp)
        elif equ_inp == 2:
            inp = clahe.apply(inp)
        imagestack.addFrame(inp)
        if mode_prc == 0:
            dsp = imagestack.getINP()
        elif mode_prc == 1:
            dsp = imagestack.getAVG()
        elif mode_prc == 2:
            dsp = imagestack.getDIFF()
        elif mode_prc == 3:
            dsp = imagestack.getCUMSUM()
        if equ_out == 1:
            dsp = cv2.equalizeHist(dsp)
        elif equ_out == 2:
            dsp = clahe.apply(dsp)
        if dnz_out:
            cv2.fastNlMeansDenoising(dsp, dsp, dnz_out_str, 7, 21)

        # create input image
        if mode_in == 1:
            inp = np.copy(background)
        else:
            inp = cv2.cvtColor(np.uint8(imagestack.inp_frame),
                               cv2.COLOR_GRAY2BGR)
        inp = cv2.resize(inp, (window_width, image_height))
        if mode_in <= 1:
            cv2.putText(inp, osd_inp, (12, 41), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, black, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_inp, (10, 40), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, green, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_out, (12, 71), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, black, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_out, (10, 70), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, green, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_col, (12, 101), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, black, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_col, (10, 100), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, green, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_mode, (12, 131), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, black, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            cv2.putText(inp, osd_mode, (10, 130), cv2.FONT_HERSHEY_PLAIN,
                        osd_txtsize, blue, thickness=osd_txtline,
                        lineType=cv2.CV_AA)
            if recordv or recordi:
                cv2.putText(inp, osd_recording, (12, 161),
                            cv2.FONT_HERSHEY_PLAIN, osd_txtsize, black,
                            thickness=osd_txtline, lineType=cv2.CV_AA)
                cv2.putText(inp, osd_recording, (10, 160),
                            cv2.FONT_HERSHEY_PLAIN, osd_txtsize, red,
                            thickness=osd_txtline, lineType=cv2.CV_AA)
            if imagestack.filling_stack:
                cv2.putText(inp, "Filling Stack", (12, 191),
                            cv2.FONT_HERSHEY_PLAIN, osd_txtsize, black,
                            thickness=osd_txtline, lineType=cv2.CV_AA)
                cv2.putText(inp, "Filling Stack", (10, 190),
                            cv2.FONT_HERSHEY_PLAIN, osd_txtsize, red,
                            thickness=osd_txtline, lineType=cv2.CV_AA)
        cv2.imshow('Input', inp)

        # create output image
        if mode_out == 1:
            out = np.copy(background)
        elif pseudoc:
            out = cv2.applyColorMap(dsp, color_mode)
        else:
            out = cv2.cvtColor(dsp, cv2.COLOR_GRAY2BGR)
        if mode_out >= 1:
            x_avg, y_avg = imagestack.getVECTOR(vec_zoom)
            cv2.line(out, center, (x_avg, y_avg), green,
                     thickness=osd_txtline, lineType=cv2.CV_AA)
            cv2.circle(out, (x_avg, y_avg), 20, red,
                       thickness=osd_txtline, lineType=cv2.CV_AA)
        cv2.imshow('Processed Output', out)
        
        # record video or image sequence
        if recordv:
            if novfile:
                video = VideoWriter(video_dst + gettime() + '.avi')
                novfile = False
            video.writeFrame(out)
        if recordi:
            if imgindx == 0:
                image_dst += gettime()
            filename = image_dst + str(imgindx).zfill(8) + '.bmp'
            cv2.imwrite(filename, out)
            imgindx += 1

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
                color_mode += 1
                if color_mode > 11:
                    pseudoc = False
                    color_mode = -1
                else:
                    pseudoc = True
            elif asckey == 100:  # d use current average as dark frame
                dyn_dark = not dyn_dark
                imagestack.dyn_dark = dyn_dark
            elif asckey == 101:  # e toggle input equalization
                equ_inp += 1
                if equ_inp >= 3:
                    equ_inp = 0
            elif asckey == 69:  # E toggle output equalization
                equ_out += 1
                if equ_out >= 3:
                    equ_out = 0
            elif asckey == 104:  # h show help
                show_help()
            elif asckey == 105: # i toggle image sequence recording
                recordi = not recordi
            elif asckey == 108: # l toggle input video loop mode
                imageinput.loop = not imageinput.loop
            elif asckey == 109:  # m input mode
                mode_in += 1
                if mode_in >= 3:
                    mode_in = 0
            elif asckey == 77:  # M output mode
                mode_out += 1
                if mode_out >= 3:
                    mode_out = 0
            elif asckey == 110:  # n denoise input
                dnz_inp = not dnz_inp
            elif asckey == 78:  # N denoise output
                dnz_out = not dnz_out
            elif asckey == 112:  # p processing mode
                mode_prc += 1
                if mode_prc >= 4:
                    mode_prc = 0
            elif asckey == 113:  # q terminates program
                sys.exit(0)
            elif asckey == 114:  # r reset cumulative summing
                imagestack.resetCUMSUM()
            elif asckey == 82:  # R reset gain and offset
                imagestack.gain_inp = gain_inp
                imagestack.gain_out = gain_inp
                imagestack.offset_inp = 0
                imagestack.offset_out = 0
            elif asckey == 115:  # s schlieren pattern
                pattern_mode += 1
                if pattern_mode > 3:
                    pattern_mode = 1
                if pattern_size == 0:
                    pattern_size = 4
                pattern = draw_pattern()
            elif asckey == 83: # S toggle image stabilizer
                stabilizer = not stabilizer
            elif asckey == 118: # v toggle video recording
                recordv = not recordv
            elif asckey == 62: # > increase schlieren pattern size
                pattern_size += 1
                pattern = draw_pattern()
            elif asckey == 60: # < decrease schlieren pattern size
                pattern_size -= 1
                pattern = draw_pattern()
            elif asckey == 120:  # x flip around X axis
                imagestack.flip_x = not imagestack.flip_x
            elif asckey == 121:  # y flip around Y axis
                imagestack.flip_y = not imagestack.flip_y
            elif asckey == 93:  # ] increase input gain
                imagestack.gain_inp += gain_increment
            elif asckey == 91:  # [ decrease input gain
                imagestack.gain_inp -= gain_increment
            elif asckey == 125:  # } increase output gain
                imagestack.gain_out += gain_increment
            elif asckey == 123:  # { decrease output gain
                imagestack.gain_out -= gain_increment
            elif asckey == 32:  # SPACE create screenshot
                filename = output_path + 'Screenshot-' + gettime() + '.bmp'
                cv2.imwrite(filename, out)
            elif asckey >= 49 and asckey <= 57:  # no of frames to stack
                numframes = asckey - 48
                imagestack.initStack(numframes)
            if backgnd:
                cv2.imshow('Schlieren Background', pattern)
            set_osd()
    sys.exit(0)
