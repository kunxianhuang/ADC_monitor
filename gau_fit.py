#!/usr/bin/env python3
""" Fitting of voltage value of 16 ADCs by Gaussian function

Kunxian Huang 2024-02-22
"""

import numpy as np
import math 
from scipy.optimize import minimize, least_squares, curve_fit

def gauss_fn(x,mu,sigma,A):
    
    fn = A*np.exp(-1*(x-mu)**2/(2*sigma**2))/(sigma*math.sqrt(2*math.pi))
    return fn



def gau_fit(x_array,voltagesub_array,relgain_array):
    assert voltagesub_array.shape==relgain_array.shape
    assert voltagesub_array.shape==x_array.shape
    vol_calgain = np.divide(voltagesub_array,relgain_array)
    #guess initial value
    mu0 = np.dot(x_array,vol_calgain)/x_array.shape[0]
    sigma0 = 5.0 # beam size 
    A0 = np.max(vol_calgain)
    p0 = np.array([mu0,sigma0,A0])
    popt, pcov = curve_fit(gauss_fn,x_array,vol_calgain,p0=p0)
    mu = popt[0]
    sigma = popt[1]
    A = popt[2]
    fit_array = gauss_fn(x_array, *popt)
    return mu,sigma,A,fit_array
