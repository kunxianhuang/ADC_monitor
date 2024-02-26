#!/usr/bin/env python3
""" Fitting of voltage value of 16 ADCs by Gaussian function

Kunxian Huang 2023-02-22
"""

import numpy as np
import math 
from scipy.optimize import minimize, least_squares, curve_fit

def gauss_fn(x,mu,sigma):
    mu,sigma = para
    fn = np.exp(-1*(x-mu)**2/(2*sigma**2))/(sigma*math.sqrt(2*math.pi))
    return fn



def gau_fit(x_array,voltage_array,pedestal_array):
    assert voltage_array.shape==pedestal_array.shape
    vol_substract = np.subtract(voltage_array,pedestal_array)
    assert vol_substract.shape==x_array.shape
    popt, pcov = curve_fit(gauss_fn,x_array,vol_substract)
    mu = popt[0]
    sigma = popt[1]
    fit_array = gauss_fn(x_array, *popt)
    return mu,sigma,fit_array
