#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 2017

@author: Mark Dammer

Various actuator classes to provide an interface to external hard- and software.
The 'dummy' class can be used for testing and training.
"""

import numpy as np
import cv2
from threading import Thread, Event
from kivy.graphics import Line, Color
from kivy.graphics.instructions import InstructionGroup

import requests
import pyautogui
import liblo

class Dummy:
    def __init__(self, cnf):
        self.name = 'Dummy'
        self.cnf = cnf
        self.x = self.y = self.z = 0
        self.oldx = self.oldy = self.oldz = 0
        self.jx = self.jy = 0
        self.joldx = self.joldy = 0
        self.actuator_thread_run = True
        self.sendrequest = Event()
        if not self.cnf.single_thread:
            self.requestthread = Thread(target=self.request_thread)
            self.requestthread.start()

    def transmit(self, x, y, z, jx, jy):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)
        self.jx = int(jx)
        self.jy = int(jy)
        if self.x != self.oldx or self.y != self.oldy or self.z != self.oldz or self.jx != self.joldx or self.jy != self.joldy:
            if self.cnf.single_thread:
                self.output()
            else:
                self.sendrequest.set()
        self.oldx = self.x
        self.oldy = self.y
        self.oldz = self.z
        self.joldx = self.jx
        self.joldy = self.jy

    def start(self):
        print('start actuator')

    def stop(self):
        print('stop actuator')

    def shutdown(self):
        self.actuator_thread_run = False
        self.stop()
        self.x = self.y = self.z = 0
        self.sendrequest.set()
        if not self.cnf.single_thread:
            self.requestthread.join()

    def video_play(self):
        print('play videofeed')

    def video_stop(self):
        print('stop videofeed')

    def output(self):
        print(self.x, self.y, self.z)

    def request_thread(self):
        while self.actuator_thread_run:
            self.sendrequest.wait()
            self.output()
            self.sendrequest.clear()


class Paint(object):
    __slots__ = ['name', 'cnf', 'x', 'y', 'z', 'oldx', 'oldy', 'oldz', 'video', 'draw_widget',
                 'draw_instructions', 'firstrun', 'actuator_thread_run', 'sendrequest', 'requestthread']

    def __init__(self, cnf):
        self.name = 'Paint'
        self.cnf = cnf
        self.x = self.y = self.z = 0
        self.oldx = self.oldy = self.oldz = 0
        self.video = self.cnf.rootwidget.oimage_wid
        self.video.source = self.cnf.background_source
        self.draw_widget = self.cnf.rootwidget.oimage_wid
        self.draw_instructions = InstructionGroup()
        self.draw_widget.canvas.add(self.draw_instructions)
        self.firstrun = True
        self.actuator_thread_run = True
        self.sendrequest = Event()
        if not self.cnf.single_thread:
            self.requestthread = Thread(target=self.request_thread)
            self.requestthread.start()

    def transmit(self, x, y, z, jx, jy):
        self.x = int(x * self.cnf.out_xscale + self.cnf.out_xcenter)
        self.y = int(y * self.cnf.out_yscale + self.cnf.out_ycenter)
        self.z = z
        if self.cnf.single_thread:
            self.output()
        else:
            self.sendrequest.set()

    def start(self):
        self.cnf.show_z = False
        self.cnf.rootwidget.zindicator_wid.text = ''
        self.cnf.rootwidget.marker_wid.source = 'assets/draw_marker.png'
        self.draw_instructions = InstructionGroup()
        self.draw_widget.canvas.add(self.draw_instructions)

    def stop(self):
        self.draw_widget.canvas.remove(self.draw_instructions)
        self.cnf.rootwidget.marker_wid.source = 'assets/hud_marker.png'
        self.cnf.show_z = True

    def shutdown(self):
        self.actuator_thread_run = False
        self.stop()
        self.sendrequest.set()
        if not self.cnf.single_thread:
            self.requestthread.join()

    def video_play(self):
        self.video.state = 'play'

    def video_stop(self):
        self.video.state = 'stop'

    def output(self):
        if self.firstrun:
            self.oldx = self.x + 1
            self.oldy = self.y + 1
            self.oldz = self.z
            self.firstrun = False
        if self.x != self.oldx or self.y != self.oldy:
            self.draw_instructions.add(Color(self.z / 255, 1, 1, mode='hsv'))
            self.draw_instructions.add(
                Line(points=[self.oldx, self.oldy, self.x, self.y], width=2))
            self.oldx = self.x
            self.oldy = self.y
            self.oldz = self.z

    def request_thread(self):
        while self.actuator_thread_run:
            self.sendrequest.wait()
            self.output()
            self.sendrequest.clear()

class Mouse:
    def __init__(self, cnf):
        self.name = 'Mouse'
        self.cnf = cnf
        self.screenx, self.screeny = pyautogui.size()
        self.x = self.oldx = self.centerx = self.screenx / 2
        self.y = self.oldy = self.centery = self.screeny / 2
        self.xfactor = self.centerx / 1000
        self.yfactor = self.centery / -1000
        pyautogui.moveTo(self.x, self.y, duration=1)
        self.actuator_thread_run = True
        if not self.cnf.single_thread:
            self.requestthread = Thread(target=self.request_thread)
            self.requestthread.start()

    def transmitabs(self, x, y):
        self.x = int(x * self.xfactor + self.centerx)
        self.y = int(y * self.yfactor + self.centery)
        if self.x != self.oldx or self.y != self.oldy:
            pyautogui.moveTo(self.x, self.y)
        self.oldx = self.x
        self.oldy = self.y

    def transmit(self, x, y, z, jx, jy):
        self.x = int(x / 10)
        self.y = int(y / -10)
        if self.x != 0 or self.y != 0:
            if self.cnf.single_thread:
                self.set_pointer()
            else:
                self.sendrequest.set()

    def start(self):
        print('start actuator')

    def stop(self):
        print('stop actuator')

    def shutdown(self):
        self.actuator_thread_run = False
        self.stop()
        self.sendrequest.set()
        if not self.cnf.single_thread:
            self.requestthread.join()

    def video_play(self):
        print('play')

    def video_stop(self):
        print('stop')

    def set_pointer(self):
        pyautogui.moveRel(self.x, self.y)

    def request_thread(self):
        while self.actuator_thread_run:
            self.sendrequest.wait()
            self.set_pointer()
            self.sendrequest.clear()


class OSC:
    def __init__(self, cnf):
        self.name = 'OSC'
        self.cnf = cnf
        self.url = "osc.udp://" + str(self.cnf.actuator_parm)
        self.x = self.y = self.z = 0
        self.oldx = self.oldy = self.oldz = 0
        self.jx = self.jy = 0
        self.joldx = self.joldy = 0
        self.oscclient = liblo.Address(self.url)
        self.video = self.cnf.rootwidget.oimage_wid
        self.video.source = self.cnf.background_source
        if not self.cnf.single_thread:
            self.actuator_thread_run = True
            self.sendrequest = Event()
            self.requestthread = Thread(target=self.request_thread)
            self.requestthread.start()

    def transmit(self, x, y, z, jx, jy):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)
        self.jx = int(jx)
        self.jy = int(jy)
        if self.x != self.oldx or self.y != self.oldy or self.z != self.oldz or self.jx != self.joldx or self.jy != self.joldy:
            if self.cnf.single_thread:
                self.osc_output()
            else:
                self.sendrequest.set()

    def start(self):
        print('start actuator')

    def stop(self):
        self.x = self.y = self.z = 0
        self.sendrequest.set()
        print('stop actuator')

    def shutdown(self):
        self.actuator_thread_run = False
        self.stop()
        if not self.cnf.single_thread:
            self.requestthread.join()

    def video_play(self):
        self.video.state = 'play'

    def video_stop(self):
        self.video.state = 'stop'

    def request_thread(self):
        while self.actuator_thread_run:
            self.sendrequest.wait()
            self.osc_output()
            self.sendrequest.clear()

    def osc_output(self):
        if self.x != self.oldx:
            liblo.send(self.oscclient, "/xaxis", self.x)
            self.oldx = self.x
        if self.y != self.oldy:
            liblo.send(self.oscclient, "/yaxis", self.y)
            self.oldy = self.y
        if self.z != self.oldz:
            liblo.send(self.oscclient, "/zaxis", self.z)
            self.oldz = self.z
        if self.jx != self.joldx:
            liblo.send(self.oscclient, "/joyx", self.jx)
            self.joldx = self.jx
        if self.jy != self.joldy:
            liblo.send(self.oscclient, "/joyy", self.jy)
            self.joldy = self.jy


class STSpilot:
    def __init__(self, cnf):
        self.name = 'STSpilot'
        self.cnf = cnf
        self.session = requests.Session()
        self.x = 0
        self.y = 0
        self.oldx = 0
        self.oldy = 0
        self.video = self.cnf.rootwidget.oimage_wid
        self.reqtimeout = 1.0
        self.sendrequest = Event()
        self.url = 'http://' + self.cnf.actuator_parm
        self.joystick = '/joystick'
        self.videofeed = '/video_feed.mjpg'
        self.actuator_thread_run = True
        self.requestpayload = {'x': '0', 'y': '0'}
        self.video.source = self.url + self.videofeed
        self.video.state = 'stop'
        if not self.cnf.single_thread:
            self.requestthread = Thread(target=self.request_thread)
            self.requestthread.start()

    def video_play(self):
        self.video.state = 'play'

    def video_stop(self):
        self.video.state = 'stop'

    def transmit(self, x, y, z, jx, jy):
        self.x = int(x)
        self.y = int(y)
        if self.x != self.oldx or self.y != self.oldy:
            payload = {'x': str(self.x), 'y': str(self.y)}
            self.send_request(payload)
        self.oldx = self.x
        self.oldy = self.y

    def start(self):
        print('start actuator')

    def stop(self):
        self.send_request({'x': '0', 'y': '0'})

    def shutdown(self):
        self.actuator_thread_run = False
        self.stop()
        if not self.cnf.single_thread:
            self.requestthread.join()

    def send_request(self, payload):
        self.requestpayload = payload
        if self.cnf.single_thread:
            self.http_request()
        else:
            self.sendrequest.set()

    def http_request(self):
        try:
            r = self.session.get(
                self.url + self.joystick, params=self.requestpayload, timeout=self.reqtimeout)
        except:
            print('HTTP Request to ' + self.url + ' timed out')

    def request_thread(self):
        while self.actuator_thread_run:
            self.sendrequest.wait()
            self.http_request()
            self.sendrequest.clear()

