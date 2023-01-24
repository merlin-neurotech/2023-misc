# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:24:37 2022

@author: jackg
"""

#import neurol
from neurol import BCI
# import ble2lsl as bl
# help(bl.ble2lsl.Streamer)
# help(bl.devices)
from plot import plot, plot_fft, plot_spectrogram

#%%
''' CONNECT TO MUSE'''
from neurol.connect_device import connect_muse
connect_muse()


#%%
'''Creating a BCI to track if we are relaxed or not'''
from neurol import BCI_tools
from neurol.models import classification_tools
from neurol.connect_device import get_lsl_EEG_inlets
from neurol import streams


'''Creates a Calibrator'''
my_clb = lambda stream : BCI_tools.band_power_calibrator(stream, ['AF7', 'AF8'], 'muse', bands=['alpha_low', 'alpha_high'], 
                                        percentile=65, recording_length=10, epoch_len=1, inter_window_interval=0.25)
# we defined a calibrator which returns the 65th percentile of alpha wave 
#power over the 'AF7' and 'AF8' channels of a muse headset after recording for 10 seconds 
# and using epochs of 1 second seperated by 0.25 seconds.

'''Creates a Transformer'''
my_tfrm = lambda buffer, clb_info: BCI_tools.band_power_transformer(buffer, clb_info, ['AF7', 'AF8'], 'muse',
                                                    bands=['alpha_low', 'alpha_high'], epoch_len=1)
# define a transformer that corresponds to the choices we made with the calibrator|

'''Creates a Classifier'''
# Again, we define a classifier that matches the choices we made
# we use a function definition instead of a lambda expression since we want to do slightly more with 
def my_clf(clf_input, clb_info):
    
    # use threshold_clf to get a binary classification
    binary_label = classification_tools.threshold_clf(clf_input, clb_info, clf_consolidator='all')
    
    # decode the binary_label into something more inteligible for printing
    label = classification_tools.decode_prediction(binary_label, {True: 'Relaxed', False: 'Concentrated'})
    
    return label

'''DEFINE THE BCI'''
my_bci = BCI.generic_BCI(my_clf, transformer=my_tfrm, action=print, calibrator=my_clb)

inlet = get_lsl_EEG_inlets()[0] # gets first inlet, assuming only one EEG streaming device is connected

# we ask the stream object to manage a buffer of 1024 samples from the inlet
stream = streams.lsl_stream(inlet, buffer_length=1024)

my_bci.calibrate(stream)

print(my_bci.calibration_info)

#%% Plotting Data Stream

'''
Plot the stream, uncomment 1 at time.
'''
try: 
    plot(stream)                    # voltage against time
    #plot_spectrogram(stream)        # frequency spectrogram
    #plot_fft(stream)                # fft 
except KeyboardInterrupt:
    stream.close()
    
    print('\n')
    print('QUIT BCI')

#%% Running BCI

'''Run the BCI'''
try:
    my_bci.run(stream)
except KeyboardInterrupt:

    stream.close()
    
    print('\n')
    print('QUIT BCI')




















