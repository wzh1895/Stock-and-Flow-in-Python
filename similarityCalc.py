"""
Calculating similarity between two dynamic behaviors (time sequences) using DTW (dynamic time warping)
"""
# from fastdtw import fastdtw

from dtw import dtw
import numpy as np
import pandas as pd

filename = 'dec_decreasing.csv'
data = pd.read_csv(filename)
t_series_temperature = data["Temperature"].tolist()

x = np.array(t_series_temperature).reshape(-1,1)
test1 = np.array([100,90,80,70,60,50,40,30,20]).reshape(-1,1)
test2 = np.array([20,30,40,50,60,70,80,90,100]).reshape(-1,1)


dist1, cost1, acc1, path1 = dtw(x, test1, dist=lambda x, test1: np.linalg.norm(x - test1, ord=1))
dist2, cost2, acc2, path2 = dtw(x, test2, dist=lambda x, test2: np.linalg.norm(x - test2, ord=1))

print('Minimum distance found for test1:', dist1)
print('Minimum distance found for test2:', dist2)
