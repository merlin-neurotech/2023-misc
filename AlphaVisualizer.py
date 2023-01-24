#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 21:29:02 2023

@author: alossius
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import random


def AlphaPlot(state):

    app = QtGui.QApplication([])
    
    # Create a plot widget
    plot = pg.plot()
    
    # Create a curve to be plotted
    curve = plot.plot(y=state)
    
    # Create a function to update the plot with new data
    def update():
        global curve, plot
        y = random.random()
        x = curve.xData[-1] + 1 if curve.xData else 0
        curve.setData(np.append(curve.xData, x))
        curve.setData(np.append(curve.yData, y))
        plot.enableAutoRange('xy', False)
        plot.setXRange(x-50, x)
    
    # Set a timer to update the plot every 100ms
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)
    
    # Show the plot
    plot.show()
    app.exec_()
