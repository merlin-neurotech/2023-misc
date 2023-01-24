#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:05:33 2023

@author: alossius
"""

from neurol import streams
from neurol.connect_device import get_lsl_EEG_inlets
from neurol.BCI import generic_BCI, automl_BCI
from neurol import BCI_tools
from neurol.models import classification_tools
from sys import exit
from phue import Bridge #HUE
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from AlphaLight_V2.AlphaVisualizer import AlphaPlot

# Function to set the color of the light
def setColor(x, y): 
    for light in lights: light.xy = [x/10, y/10]
    
# Function to set the starting conditions of the game
def setDefault(): 
    setColor(1, 10) # set color to green
    global state, ys, xs
    state = 0 # initialize state to 0
    ys = []
    xs = []
    print("Light default set")
    
def changeLight2(input_):
    global diff, state, ys, xs

    if diff == 0: step = 0.1
    elif diff == 1: step = 0.2
    else: step = 0.5
    
    if abs(state) >= 10:
        setColor(10, 1)
        print("GAME OVER")
        exit()

    if (input_ == 'Non-concentrated'):
        print(input_)
        state = state - step
    else:
        print(input_)
        state = state + step
    
    x = abs(state)
    setColor(x, 10)
    
    ys.append(state)
    xs.append(len(ys))
    
    plt.figure()
    plt.plot(xs, ys)
    plt.show()

# def animate(i):
#     ax1.clear()
#     ax1.plot(xs, ys)

#-------------------------------------------

b = Bridge('192.168.0.187')  
b.connect()
lights = b.get_light_objects()
    
setDefault()

# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)

# ani = animation.FuncAnimation(fig, animate, interval=1000)
# plt.show()

#-------------------------------------------
# region define BCI behaviour

# we defined a calibrator which returns the 65th percentile of alpha wave
# power over the 'AF7' and 'AF8' channels of a muse headset after recording for 10 seconds
# and using epochs of 1 second seperated by 0.25 seconds.
clb = lambda stream:  BCI_tools.band_power_calibrator(stream, ['AF7', 'AF8'], 'muse', bands=['alpha_low', 'alpha_high'],
                                                        percentile=9, recording_length=10, epoch_len=1, inter_window_interval=0.25)


# define a transformer that corresponds to the choices we made with the calibrator
gen_tfrm = lambda buffer, clb_info: BCI_tools.band_power_transformer(buffer, clb_info, ['AF7', 'AF8'], 'muse',
                                                                    bands=['alpha_low', 'alpha_high'], epoch_len=1)

# Again, we define a classifier that matches the choices we made
# we use a function definition instead of a lambda expression since we want to do slightly more with


def clf(clf_input, clb_info):

    # use threshold_clf to get a binary classification
    binary_label = classification_tools.threshold_clf(
        clf_input, clb_info, clf_consolidator='all')

    # decode the binary_label into something more inteligible for printing
    label = classification_tools.decode_prediction(
        binary_label, {True: 'Concentrated', False: 'Non-concentrated'})

    return label
# endregion
#-------------------------------------------

# GET EEG STREAM
# gets first inlet, assuming only one EEG streaming device is connected
inlet = get_lsl_EEG_inlets()[0]

# we ask the stream object to manage a buffer of 1024 samples from the inlet
stream = streams.lsl_stream(inlet, buffer_length=1024)


# DEFINE GENERIC BCI
alpha_light_generic = generic_BCI(
    clf, transformer=gen_tfrm, action=changeLight2, calibrator=clb)


# DEFINE AUTO_ML BCI parameters
ml_epoch_len = 50
ml_recording_length = 10
ml_n_states = 2
ml_transformer = lambda x: x[:,1] # takes the first two channels

from sklearn import svm
ml_model = svm.SVC()
alpha_light_automl = automl_BCI(ml_model, ml_epoch_len, ml_n_states, ml_transformer, action=print)


usrChoice = int(input("Choose your BCI.\n1) Generic BCI\n2) AutoML BCI\n"))
diff = int(input("\nChoose your game difficultly.\n0 = Easy\n1 = Medium\n2 = Hard\n"))

# RUN BCI
try:
    # inlet -> calibrate -> transform -> classify -> action
    if usrChoice == 1:
    # CALIBRATE GENERIC BCI
        alpha_light_generic.calibrate(stream)
        alpha_light_generic.run(stream)
        AlphaPlot(state)
    elif usrChoice == 2:
        alpha_light_automl.build_model(stream, ml_recording_length)
        alpha_light_automl.run(stream)
except KeyboardInterrupt:
    print('\n\nBCI Ended')


""" Todo:
- Calculated threshold value per individual - check out BCI workshop
- incorporate the blink classifier - Where can we find the blink classifier?
- pip installable the extra tools (from AI team)
- clean and document (requirements.txt)"""


# add pynput to requirements# insa
