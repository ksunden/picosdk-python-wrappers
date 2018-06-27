#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PS6000 BLOCK MODE EXAMPLE
# This example opens a 2000 driver device, sets up two channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps2000 import ps2000 as ps
import matplotlib.pyplot as plt

def adc2mV(bufferADC, range, maxADC):
    """ 
        adc2mc(
                c_short_Array           buffer
                int                     range
                c_int32                  maxADC
                )
               
        Takes a buffer of raw adc count values and converts it into milivolts 
    """

    channelInputRanges = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    vRange = channelInputRanges[range]
    bufferV = [(x * vRange) / maxADC.value for x in bufferADC]

    return bufferV

# Create status ready for use
status = {}

# Open 2000 series PicoScope
# Returns handle to chandle for use in future API functions
status["openUnit"] = ps.ps2000_open_unit()

# Create chandle for use
chandle = ctypes.c_int16(status["openUnit"])

# Set up channel A
# handle = chandle
# channel = PS2000_CHANNEL_A = 0
# enabled = 1
# coupling type = PS2000_DC = 1
# range = PS2000_2V = 7
# analogue offset = 0 V
chARange = 7
status["setChA"] = ps.ps2000_set_channel(chandle, 0, 1, 1, chARange)

# Set up channel B
# handle = chandle
# channel = PS2000_CHANNEL_B = 1
# enabled = 1
# coupling type = PS2000_DC = 1
# range = PS2000_2V = 7
# analogue offset = 0 V
chBRange = 7
status["setChB"] = ps.ps2000_set_channel(chandle, 1, 1, 1, chBRange)

# Set up single trigger
# handle = chandle
# source = PS2000_CHANNEL_A = 0
# threshold = 1024 ADC counts
# direction = PS2000_RISING = 2
# delay = 0 s
# auto Trigger = 1000 ms
status["trigger"] = ps.ps2000_set_trigger(chandle, 0, 64, 2, 0, 1000)

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 2500
postTriggerSamples = 2500
maxSamples = preTriggerSamples + postTriggerSamples

# Get timebase information
# handle = chandle
# timebase = 8 = timebase
# no_of_samples = maxSamples
# pointer to time_interval = ctypes.byref(timeInterval)
# pointer to time_units = ctypes.byref(timeUnits)
# oversample = 1 = oversample
# pointer to max_samples = ctypes.byref(maxSamplesReturn)
timebase = 8
timeInterval = ctypes.c_int32()
timeUnits = ctypes.c_int32()
oversample = ctypes.c_int16(1)
maxSamplesReturn = ctypes.c_int32()
status["getTimebase"] = ps.ps2000_get_timebase(chandle, timebase, maxSamples, ctypes.byref(timeInterval), ctypes.byref(timeUnits), oversample, ctypes.byref(maxSamplesReturn))

# Run block capture
# handle = chandle
# no_of_samples = maxSamples
# timebase = timebase
# oversample = oversample
# pointer to time_indisposed_ms = ctypes.byref(timeIndisposedms)
timeIndisposedms = ctypes.c_int32()
status["runBlock"] = ps.ps2000_run_block(chandle, maxSamples, timebase, oversample, ctypes.byref(timeIndisposedms))

# Check for data collection to finish using ps5000aIsReady
ready = ctypes.c_int16(0)
check = ctypes.c_int16(0)
while ready.value == check.value:
    status["isReady"] = ps.ps2000_ready(chandle)
    ready = ctypes.c_int16(status["isReady"])

# Create buffers ready for data
bufferA = (ctypes.c_int16 * maxSamples)()
bufferB = (ctypes.c_int16 * maxSamples)()

# Get data from scope
# handle = chandle
# pointer to buffer_a = ctypes.byref(bufferA)
# pointer to buffer_b = ctypes.byref(bufferB)
# poiner to overflow = ctypes.byref(oversample)
# no_of_values = cmaxSamples
cmaxSamples = ctypes.c_int32(maxSamples)
status["getValues"] = ps.ps2000_get_values(chandle, ctypes.byref(bufferA), ctypes.byref(bufferB), None, None, ctypes.byref(oversample), cmaxSamples)

# find maximum ADC count value
maxADC = ctypes.c_int16(32767)

# convert ADC counts data to mV
adc2mVChA =  adc2mV(bufferA, chARange, maxADC)
adc2mVChB =  adc2mV(bufferB, chBRange, maxADC)

# Create time data
time = np.linspace(0, (cmaxSamples.value) * timeInterval.value, cmaxSamples.value)

# plot data from channel A and B
plt.plot(time, adc2mVChA[:])
plt.plot(time, adc2mVChB[:])
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
plt.show()

# Stop the scope
# handle = chandle
status["stop"] = ps.ps2000_stop(chandle)

# display status returns
print(status)

# Close unitDisconnect the scope
# handle = chandle
ps.ps2000_close_unit(chandle)