#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 16:47:03 2017

@author: Mark Dammer

You can add your on convolution kernels to the "self.kernels" list.
Basic structure: ['Name', default_filter_strength, [kernel]]
"""
import numpy as np

class Kernels:
    def __init__(self):
        self.kernels = [
                ['sharpen1', 1,[[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]],
                ['sharpen2', 1,[[1,1,1], [1,-7,1], [1,1,1]]],
                ['sharpen3', 0.125,[[-1,-1,-1,-1,-1],
                             [-1,2,2,2,-1],
                             [-1,2,8,2,-1],
                             [-1,2,2,2,-1],
                             [-1,-1,-1,-1,-1]]]
                ]
                
    def get_kernel(self, index):
        self.name = self.kernels[index - 1][0]
        self.kernel = self.kernels[index - 1][2]
        self.strength = self.kernels[index - 1][1]
        return self.name, np.array(self.kernel), self.strength
    
    def get_numkernels(self):
        return len(self.kernels) + 1