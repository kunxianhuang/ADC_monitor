#!/usr/bin/env python3
"""File for test loop and the  interrupt to the process
"""
import os,sys
import logging
import multiprocessing
import time
import signal
from time import perf_counter,sleep,strftime,localtime

def loop_test(adcFile):
    p = multiprocessing.current_process()
    try:
        signal.signal(signal.SIGINT,handler)  
        print("[PID:{}] acquiring resources".format(p.pid))
        while(True):       
            print(adcFile)    
            #working...
            time.sleep(1.5)

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("[PID:{}] releasing resources".format(p.pid))

def handler(signal, frame):
    print("handler!!!")
    sys.exit(10)
