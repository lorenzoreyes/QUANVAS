#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 02:45:47 2021

@author: lorenzo
"""

#load libraries
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
# symbols = [stock, market]
# start date for historical prices
symbols = ['AAPL', '^GSPC']
data = yf.download(symbols, period="100d")['Adj Close']
# Convert historical stock prices to daily percent change
price_change = data.pct_change()
# Deletes row one containing the NaN
df = price_change.drop(price_change.index[0])
# Create arrays for x and y variables in the regression model
# Set up the model and define the type of regression
x = np.array(df['AAPL']).reshape((-1,1))
y = np.array(df['^GSPC'])
model = LinearRegression().fit(x, y)
print('Beta = ', model.coef_)