#!/usr/bin/env python3
"""File for reading ADC by the class ADS79XX in pipyadc package

ADS79XX AD-converter cycling through sixteen input channels.

Hardware: ADS79XX interfaced to the Raspberry Pi 4
 
Kunxian Huang 2023-10-25


"""
import os,sys
import logging
import multiprocessing
import time
import signal
from time import perf_counter,sleep,strftime,localtime

PiPyADC_PATH = u'/Users/bean/work/pyana/PiPyADC'
if PiPyADC_PATH not in sys.path:
    sys.path = [PiPyADC_PATH] + sys.path

from pipyadc import ADS79XX
from pipyadc.ADS79XX_definitions import *
from pipyadc import ADS79XX_default_config

logging.basicConfig(level=logging.DEBUG)

def raw_to_voltage(raw_channel,v_per_digit):
    #count_mask = 0b0000111111110000 # 8-bit mask
    count_mask = 0b0000111111111111 # 12-bit mask
    #print("reply message is {}".format(raw_channel))
    adc_ch = raw_channel>>12 #D15-D12 ADC channel number
    adc_count = raw_channel&count_mask # D0-D11 ADC count 
    voltage = v_per_digit*adc_count

    return adc_ch,voltage

def loop_infinite_measurements(ads,adcFilename):
    # Arbitrary length tuple of input channel pair values to scan sequentially
    CH_SEQUENCE = 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15

    p = multiprocessing.current_process()

    # sample rate 50 Hz , 0.02 sec -latency (0.01 sec)
    sleep_duration = 1.0/50.0 - 0.01
    adcFile = open(adcFilename,"w+",encoding="utf-8")
    try:
        signal.signal(signal.SIGINT,loop_handler)  
        print("[PID:{}] acquiring resources".format(p.pid))
        while(True):
                start = perf_counter()  
            # Returns list of integers, one result for each configured channel
            raw_channels = ads.read_sequence(CH_SEQUENCE)
            record_time = strftime('%c', localtime())
            ch_l =[]
            voltage_l=[]
            for raw_channel in raw_channels:
                ch, voltage = raw_to_voltage(raw_channel,ads.v_per_digit)
                ch_l.append(ch)
                voltage_l.append(voltage)

            end = perf_counter()
            exe_time = (end-start)
            print("execute {}-times time {}\n".format(i,exe_time))
            #print("epoch {} channel {} execute time {}\n".format(epoch,chs,exe_time))
            for ch,voltage in zip(ch_l,voltage_l):
                adcFile.write("CH:{:0>2d}\tVoltage:{:.4f}V\t\tTime:{%s}\n".format(ch,voltage,record_time))

        

            time.sleep(sleep_duration) # 50 Hz

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("[PID:{}] releasing resources".format(p.pid))
        


def loop_oneminute_measurements(ads,adcFile):
    # Arbitrary length tuple of input channel pair values to scan sequentially
    CH_SEQUENCE = 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    # sample rate 50 Hz for recording 1 min data 
    counts = 1.0 * 60.0* 50.0
    i=0
    while i <counts:

        start = perf_counter()
        # Returns list of integers, one result for each configured channel
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        record_time = strftime('%c', localtime())
        ch_l =[]
        voltage_l=[]
        for raw_channel in raw_channels:
            ch, voltage = raw_to_voltage(raw_channel,ads.v_per_digit)
            ch_l.append(ch)
            voltage_l.append(voltage)

        end = perf_counter()
        exe_time = (end-start)
        print("execute {}-times time {}\n".format(i,exe_time))
        #print("epoch {} channel {} execute time {}\n".format(epoch,chs,exe_time))
        for ch,voltage in zip(ch_l,voltage_l):
            adcFile.write("CH:{}\t Voltage:{}V\t Time:{}\n".format(ch,voltage,record_time))

        

        time.sleep(1.0/50.0) # 50 Hz
        i+=1



def testrun():
    adcfile= open("./adc_files.txt","w+",encoding="utf-8")
    try:
        
        # Use this to have ADS79XX automatically close the SPI device and
        # pigpio resources at exit:
        with ADS79XX(ADS79XX_default_config) as ads:
            # Get and process data
            loop_oneminute_measurements(ads,adcfile)

    except KeyboardInterrupt:
        print("\nUser Exit.\n")


def loop_test(adcFile):
    p = multiprocessing.current_process()
    try:
        signal.signal(signal.SIGINT,loop_handler)  
        print("[PID:{}] acquiring resources".format(p.pid))
        while(True):       
            print(adcFile)    
            #working...
            time.sleep(1.5)

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("[PID:{}] releasing resources".format(p.pid))

def loop_handler(signal, frame):
    print("handler!!!")
    sys.exit(10)